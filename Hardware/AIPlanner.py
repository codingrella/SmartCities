# -*- coding: utf-8 -*-




import os
import time
import shutil
import subprocess
import threading

from datetime import datetime
from MQTTInterface import MQTTSubscriber
from MQTTInterface import MQTTPublisher


MAX_RANGE_MOTION_DETECTED = 10            # 5 minutes
OPENING_HOUR = datetime.strptime('08:00:00', '%H:%M:%S')
CLOSING_HOUR = datetime.strptime('20:00:00', '%H:%M:%S')

DOMAIN_FILE_PATH = r"/PDDL_Files/Domain.pddl"
PROBLEM_FILE_PATH = r"/PDDL_Files/ProblemFile_SR_1.pddl"
PLAN_RESULT_PATH = r"/PDDL_Files/Plan.txt"


class AIPlannerInterface:
    def __init__(self, room):
        self.sensorValues = { 'Humidity_Sensor': 0,
                              'Motion_Sensor': 0,
                              'Light_Sensor': 0,
                              'Outside_Sensor': 0,
                              'Sound_Sensor': 0,
                              'Temperature_Sensor': 0 }
        self.actuatorValues = { 'Blinds': 0,
                                'Lights': 1,
                                'AC': 1,
                                'Heater': 0 }
        
        self.thresholdValues = { 'inside_isLight': 600,
                                 'outside_isDark': 0,
                                 'outside_isVerySunny': 2,
                                 'temp_lower': 21,
                                 'temp_upper': 26,
                                 'hum_lower': 50,
                                 'hum_upper': 60 }
        
        self.actions = { 'turnonac': self._setAC,
                         'turnoffac': self._setAC,
                         'turnonheater': self._setHeater,
                         'turnoffheater': self._setHeater,
                         'turnonlight': self._setLight,
                         'turnofflight': self._setLight,
                         'openblinds': self._setBlinds,
                         'closeblinds': self._setBlinds
            }
        
        self.replannedSinceMotionToggle = False
        self.time_lastMotionDetected = datetime.now().strftime("%H:%M:%S")
        self.room = room
        
        pub = MQTTPublisher()
        
        sub = MQTTSubscriber(room, '+', '+')
        sub.client.on_message = self.on_message
        
        self.sub = threading.Thread(target=sub.run)
        self.sub.start()
        
        
    
    def on_message(self, client, userdata, msg):
       # print(msg.payload.decode())
        res = eval(msg.payload.decode())
        
        if 'Sensor' in res['Device']:
            self.sensorValues[res['Device']] = res['Value']
        elif 'Threshold_Low' in res['Device'] and 'Temp' in res['Device']:
            self.thresholdValues['temp_lower'] = float(res['Value'])
        elif 'Threshold_High' in res['Device'] and 'Temp' in res['Device']:
            self.thresholdValues['temp_upper'] = float(res['Value'])
        elif 'Huminidty_Threshold' != res['Device'] and 'Light' != res['Device']:
            self.actuatorValues[res['Device']] = res['Value']
            
        if res['Device'] == 'Motion_Sensor' and res['Value'] == 1:
            self.time_lastMotionDetected = res['TimeStamp']
            self.replannedSinceMotionToggle = False
    
    
    def createAIProblemFile(self, inits, goals):
        dirname = os.path.dirname(__file__)
        
        src = dirname + f'/PDDL_Files/ProblemFile_{self.room}_Temp.pddl'
        dst = dirname + f'/PDDL_Files/ProblemFile_{self.room}.pddl'
        
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
            
    
    def _setAC(self, value):
        self.actuatorValues['AC'] = value
        self.pub.run(f'{self.room}', 'Actuator', 'AC', value)
        
    def _setHeater(self, value):
        self.actuatorValues['Heater'] = value
        self.pub.run(f'{self.room}', 'Actuator', 'Heater', value)
    
    def _setLight(self, value):
        self.actuatorValues['Lights'] = value
        self.pub.run(f'{self.room}', 'Actuator', 'Lights', value)
    
    def _setBlinds(self, value):
        self.actuatorValues['Blinds'] = value
        self.pub.run(f'{self.room}', 'Actuator', 'Blinds', value)
        
       
    def _getHumidityInit(self):
        if float(self.sensorValues['Humidity_Sensor']) < self.thresholdValues['hum_lower']:
            return f'(hum_isGood {self.room})'
        elif float(self.sensorValues['Humidity_Sensor']) < self.thresholdValues['temp_upper']:
            return f'(hum_isMid {self.room})'
        else:
            return f'(hum_isBad {self.room})'
        
    def _getTempInit(self):
        if float(self.sensorValues['Temperature_Sensor']) < self.thresholdValues['temp_lower']:
            return f'(temp_isCold {self.room})'
        elif float(self.sensorValues['Temperature_Sensor']) < self.thresholdValues['temp_upper']:
            return f'(temp_isGood {self.room})'
        else:
            return f'(temp_isHot {self.room})'
        
    def _getInsideLightInit(self):
        if int(self.sensorValues['Light_Sensor']) > self.thresholdValues['inside_isLight']:
            return f'(inside_isLight {self.room})'
        else:
            return ''
        
    def _getOutsideLightInit(self):
        if int(self.sensorValues['Outside_Sensor']) == self.thresholdValues['outside_isDark']:
            return f'(outside_isDark {self.room})'
        elif int(self.sensorValues['Outside_Sensor']) == self.thresholdValues['outside_isVerySunny']:
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
        
        
    def getPlan(self):
        planSteps = []
        
        dirname = os.path.dirname(__file__)
        path = dirname + PLAN_RESULT_PATH
        
        with open(path, encoding='utf-8') as file:
            my_data = file.read()
            
        if 'ff: found legal plan as follows' in my_data:
            idx1 = my_data.find('step')
            idx2 = my_data.find('time spent:', idx1 + len('step'))
            
            if idx1 != -1 and idx2 != -1:
                combinedSteps = my_data[idx1 + len('step'):idx2]
                combinedSteps = combinedSteps.split('\n')
                
                for step in combinedSteps:
                    action = step.split(':')[1]
                    action = " ".join(action.split()).split(' ')
                    planSteps.append(action)
        return planSteps
                    
    
    def executePlan(self, plan):
        print(plan)
        steps = plan.split(')')
        
        for step in steps:
            step.replace('(' ,'')
            elements = step.split(' ')
            
            if 'on' in elements[0] or 'open' in elements[0]:
                self.actions[elements[0]](1)
            elif 'off' in elements[0] or 'close' in elements[0]:
                self.actions[elements[0]](0)
                
        print(steps)
            
        
        
if __name__ == "__main__":
    planner = AIPlannerInterface('SR_1')
    time.sleep(5)
    
    resultPlanPath = os.path.dirname(__file__) + PLAN_RESULT_PATH
    print(resultPlanPath)
    
    while True:
        time1 = datetime.strptime(planner.time_lastMotionDetected, '%H:%M:%S')
        time2 = datetime.strptime(datetime.now().strftime("%H:%M:%S"), '%H:%M:%S')
        difference = time2 - time1
        
        # if OPENING_HOUR.time() >= datetime.now().time() or datetime.now().time() >= CLOSING_HOUR.time():
        #     print('CLOSED')
        if not planner.replannedSinceMotionToggle and int(difference.total_seconds()) >= MAX_RANGE_MOTION_DETECTED:
            print('REPLANNING')
            planner.startPlanning()
            time.sleep(5)
            planner.replannedSinceMotionToggle = True
            # os.system(f"./../FF/FF-v2.3/ff –o PDDL_Files/Domain.pddl –f PDDL_Files/ProblemFile_SR_1.pddl > PDDL_Files/Plan.txt")
            # os.system(f"./../FF/FF-v2.3/ff –o /home/pi/SmartCities/Hardware/PDDL_Files/Domain.pddl –f /home/pi/SmartCities/Hardware/PDDL_Files/ProblemFile_SR_1.pddl")
    
            result = subprocess.check_output(["./runPlan.sh"])
            print(result)
            time.sleep(5)
            # plan = planner.getPlan()
            # planner.executePlan(plan)
        elif planner.sensorValues['Outside_Sensor'] == 2:
            planner.startPlanning()
            time.sleep(5)
            os.system(f"./../FF/FF-v2.3/ff –o /home/pi/SmartCities/Hardware/PDDL_Files/Domain.pddl –f /home/pi/SmartCities/Hardware/PDDL_Files/ProblemFile_SR_1.pddl")
            time.sleep(5)
            plan = planner.getPlan()
            planner.executePlan(plan)
        elif datetime.now().minute == 0 or datetime.now().minute == 30:
            planner.startPlanning()
            time.sleep(5)
            os.system(f"./../FF/FF-v2.3/ff –o /home/pi/SmartCities/Hardware/PDDL_Files/Domain.pddl –f /home/pi/SmartCities/Hardware/PDDL_Files/ProblemFile_SR_1.pddl")
            time.sleep(5)
            plan = planner.getPlan()
            planner.executePlan(plan)
    
        
    
    # inits = AIPlanner.getAIPlannerInits('SR_1')    
    # goals = AIPlanner.getAIPlannerGoals(inits, 'SR_1')
    
    # AIPlanner.createAIProblemFile(inits, goals, 'SR_1')
