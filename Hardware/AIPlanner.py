# -*- coding: utf-8 -*-


import os
import time
import shutil
import psycopg2
import threading

from datetime import datetime
from MQTTInterface import MQTTSubscriber
from MQTTInterface import MQTTPublisher
import valueThresholds


MAX_RANGE_MOTION_DETECTED = 10            # 5 minutes
OPENING_HOUR = datetime.strptime('08:00:00', '%H:%M:%S')
CLOSING_HOUR = datetime.strptime('20:00:00', '%H:%M:%S')

DOMAIN_FILE_PATH = "Hardware/PDDL_Files/Domain.pddl"
PROBLEM_FILE_PATH = "Hardware/PDDL_Files/ProblemFile_SR_1.pddl"
PLAN_RESULT_PATH = "Hardware/PDDL_Files/Plan.txt"


class AIPlannerInterface:
    def __init__(self, room):
        self.sensorValues = { 'Humidity_Sensor': 0,
                              'Motion_Sensor': 0,
                              'Light_Sensor': 0,
                              'Outside_Sensor': 0,
                              'Sound_Sensor': 0,
                              'Temperature_Sensor': 0 }
        self.actuatorValues = { 'Blinds': 0,
                                'Lights': 0,
                                'AC': 0,
                                'Heater': 0 }
        
        self.replannedSinceMotionToggle = False
        self.time_lastMotionDetected = datetime.now().strftime("%H:%M:%S")
        self.room = room
        
        
        sub = MQTTSubscriber(room, '+', '+')
        sub.client.on_message = self.on_message
        
        self.sub = threading.Thread(target=sub.run)
        self.sub.start()
        
        
    
    def on_message(self, client, userdata, msg):
       # print(msg.payload.decode())
        res = eval(msg.payload.decode())
        
        if 'Sensor' in res['Device']:
            self.sensorValues[res['Device']] = res['Value']
        else:
            self.actuatorValues[res['Device']] = res['Value']
            
        if res['Device'] == 'Motion_Sensor' and res['Value'] == 1:
            self.time_lastMotionDetected = res['TimeStamp']
            self.replannedSinceMotionToggle = False
    
    
    def createAIProblemFile(self, inits, goals):
        dirname = os.path.dirname(__file__)
        
        src = dirname + f'\PDDL_Files\ProblemFile_{self.room}_Temp.pddl'
        dst = dirname + f'\PDDL_Files\ProblemFile_{self.room}.pddl'
        
        path = shutil.copy2(src,dst)
        
        text_init = "(:init\n"
        for init in inits:
            text_init += ('\t' + init + '\n')
        text_init += ')\n\n'
        
        text_goal = "(:goal (and\n"
        for goal in goals:
            text_goal += ('\t' + goal + '\n')
        text_goal += ') )\n)'
        
        with open(path, "a") as myfile:
            myfile.write(text_init)
            myfile.write(text_goal)

            
    def _getHumidityInit(self):
        if float(self.sensorValues['Humidity_Sensor']) < valueThresholds.hum_lower:
            return f'(hum_isGood {self.room})'
        elif float(self.sensorValues['Humidity_Sensor']) < valueThresholds.temp_upper:
            return f'(hum_isMid {self.room})'
        else:
            return f'(hum_isBad {self.room})'
        
    def _getTempInit(self):
        if float(self.sensorValues['Temperature_Sensor']) < valueThresholds.temp_lower:
            return f'(temp_isCold {self.room})'
        elif float(self.sensorValues['Temperature_Sensor']) < valueThresholds.temp_upper:
            return f'(temp_isGood {self.room})'
        else:
            return f'(temp_isHot {self.room})'
        
    def _getInsideLightInit(self):
        if int(self.sensorValues['Light_Sensor']) > valueThresholds.inside_isLight:
            return f'(inside_isLight {self.room})'
        else:
            return ''
        
    def _getOutsideLightInit(self):
        if int(self.sensorValues['Outside_Sensor']) == valueThresholds.outside_isDark:
            return f'(outside_isDark {self.room})'
        elif int(self.sensorValues['Outside_Sensor']) == valueThresholds.outside_isVerySunny:
            return f'(outside_isVerySunny {self.room})'
        else:
            return ''
            
    def _getMotionInit(self):
        if int(self.sensorValues['Motion_Sensor']) == 1:
            return f'(motion_detected {self.room})'
        else:
            return ''
        
    def _getActuatorInit(self):
        if self.room == 'SR_1': roomNr = '1'
        elif self.room == 'SR_2': roomNr = '2'
        
        
        inits = []
        if int(self.actuatorValues['Blinds']) == 1:
            inits.append(f'(blinds_down b{roomNr} {self.room})')
        if int(self.actuatorValues['Lights']) == 1:
           inits.append(f'(lighting_on l{roomNr} {self.room})')
        if int(self.actuatorValues['AC']) == 1:
            inits.append(f'(airConditioning_on ac{roomNr} {self.room})')
        if int(self.actuatorValues['Heater']) == 1:
            inits.append(f'(heater_on h{roomNr} {self.room})')
            
        return inits
        
        
    def getAIPlannerInits(self):
        result = []
        result.append(self._getHumidityInit())
        result.append(self._getTempInit())
        result.append(self._getInsideLightInit())
        result.append(self._getOutsideLightInit())
        result.append(self._getMotionInit())
        
        result.extend(self._getActuatorInit())
        
        return result
    
    def getAIPlannerGoals(self, inits):
        goals = []
        if self.room == 'SR_1': roomNr = '1'
        elif self.room == 'SR_2': roomNr = '2'
        
        if f'(hum_isGood {self.room})' in inits and f'(temp_isGood {self.room})' in inits: goals.append(f'(saveEnergy_acs {self.room})')
        elif f'(hum_isGood {self.room})' not in inits: goals.append(f'(hum_isGood {self.room})')
        elif f'(temp_isGood {self.room})' not in inits: goals.append(f'(temp_isGood {self.room})')
        elif f'(temp_isGood {self.room})' in inits: goals.append(f'(saveEnergy_heater {self.room})')
        
        if f'(motion_detected {self.room})' in inits: goals.append(f'(inside_isLight {self.room})')
        elif f'(motion_detected {self.room})' not in inits and f'(inside_isLight {self.room})' in inits: goals.append(f'(saveEnergy_lights {self.room})')
        
        return goals
            
    def startPlanning(self):
        inits = self.getAIPlannerInits()
        goals = self.getAIPlannerGoals(inits)
        
        self.createAIProblemFile(inits, goals)
        
    
    def setActuators(plan):
        steps = plan.split(')')
        
        for step in steps:
            step.replace('(' ,'')
            elements = step.split(' ')
            
            if 'heater' in elements[0]:
                pass
            elif 'ac' in elements[0]:
                pass
            elif 'blinds' in elements[0]:
                pass
            elif 'lights' in elements[0]:
                pass
        
        
        
if __name__ == "__main__":
    planner = AIPlannerInterface('SR_1')
    time.sleep(5)
    
    while True:
        time1 = datetime.strptime(planner.time_lastMotionDetected, '%H:%M:%S')
        time2 = datetime.strptime(datetime.now().strftime("%H:%M:%S"), '%H:%M:%S')
        difference = time2 - time1
        
        print(difference)
        
        # if OPENING_HOUR.time() >= datetime.now().time() or datetime.now().time() >= CLOSING_HOUR.time():
        #     print('CLOSED')
        if not planner.replannedSinceMotionToggle and int(difference.total_seconds()) >= MAX_RANGE_MOTION_DETECTED:
            print('REPLANNING')
            planner.startPlanning()
            planner.replannedSinceMotionToggle = True
            os.system(f"./FF/FF-v2.3/ff –o {DOMAIN_FILE_PATH} –f {PROBLEM_FILE_PATH} > {PLAN_RESULT_PATH}")
        elif planner.sensorValues['Outside_Sensor'] == 2:
            planner.startPlanning()
            os.system(f"./FF/FF-v2.3/ff –o {DOMAIN_FILE_PATH} –f {PROBLEM_FILE_PATH} > {PLAN_RESULT_PATH}")
        elif datetime.now().minute == 0 or datetime.now().minute == 30:
            planner.startPlanning
            os.system(f"./FF/FF-v2.3/ff –o {DOMAIN_FILE_PATH} –f {PROBLEM_FILE_PATH} > {PLAN_RESULT_PATH}")
    
        
    
    # inits = AIPlanner.getAIPlannerInits('SR_1')    
    # goals = AIPlanner.getAIPlannerGoals(inits, 'SR_1')
    
    # AIPlanner.createAIProblemFile(inits, goals, 'SR_1')
    
    
    
    
