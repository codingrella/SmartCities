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
        
        self.actions = { 'TURNONAC': self._setAC,
                         'TURNOFFAC': self._setAC,
                         'TURNONHEATER': self._setHeater,
                         'TURNOFFHEATER': self._setHeater,
                         'TURNONLIGHT': self._setLight,
                         'TURNOFFLIGHT': self._setLight,
                         'OPENBLINDS': self._setBlinds,
                         'CLOSEBLINDS': self._setBlinds
            }
        
        self.room = room
        
        self.motionToggleOne = False
        self.motionToggleZero = False
        self.time_toggleZeroDetected = datetime.now().strftime("%H:%M:%S")
        self.time_toggleOneDetected = datetime.now().strftime("%H:%M:%S")
        
        
        self.pub = MQTTPublisher()
        
        sub = MQTTSubscriber(room, '+', '+')
        sub.client.on_message = self.on_message
        
        self.sub = threading.Thread(target=sub.run)
        self.sub.start()
        
        
    
    def on_message(self, client, userdata, msg):
        # On manual intervention from UI
        if 'on' == msg.payload.decode(): 
            self.actions['TURNONLIGHT'](1)
            return
        elif 'off' == msg.payload.decode():
            self.actions['TURNOFFLIGHT'](0)
            return
        elif 'up' == msg.payload.decode(): 
            self.actions['OPENBLINDS'](1)
            return
        elif 'down' == msg.payload.decode():
            self.actions['CLOSEBLINDS'](0)
            return
       
        # On hardware updates
        res = eval(msg.payload.decode())
        
        time1 = datetime.strptime(self.time_toggleZeroDetected, '%H:%M:%S')
        time2 = datetime.strptime(datetime.now().strftime("%H:%M:%S"), '%H:%M:%S')
        difference = time2 - time1
        
        if res['Device'] == 'Motion_Sensor':
            if self.actuatorValues[res['Device']] == 0 and res['Value'] == 1:
                self.actuatorValues[res['Device']] = 1
                self.time_toggleOneDetected = res['TimeStamp'].strftime("%H:%M:%S")
                self.motionToggleZero = False
                if difference >= MAX_RANGE_MOTION_DETECTED:
                    self.motionToggleOne = True
                print('Motion toggle to 1')
            elif self.actuatorValues[res['Device']] == 1 and res['Value'] == 0:
                self.actuatorValues[res['Device']] = 0
                self.time_toggleZeroDetected = res['TimeStamp'].strftime("%H:%M:%S")
                self.motionToggleZero = True
                self.motionToggleOne = False
                print('Motion toggle to 0')
        
        if 'Sensor' in res['Device']:
            self.sensorValues[res['Device']] = res['Value']
        elif 'Threshold_Low' in res['Device'] and 'Temp' in res['Device']:
            self.thresholdValues['temp_lower'] = float(res['Value'])
        elif 'Threshold_High' in res['Device'] and 'Temp' in res['Device']:
            self.thresholdValues['temp_upper'] = float(res['Value'])
        elif 'Huminidty_Threshold' != res['Device'] and 'Light' != res['Device']:
            self.actuatorValues[res['Device']] = res['Value']
    
    
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
        
        
    def getPlanSteps(self, plannerResponse):
        planSteps = []
        
        if 'ff: found legal plan as follows' in plannerResponse:
            idx1 = plannerResponse.find('\nstep')
            idx2 = plannerResponse.find('\n\ntime spent:', idx1 + len('step'))
            
            if idx1 != -1 and idx2 != -1:
                combinedSteps = plannerResponse[idx1 + len('\nstep'):idx2]
                combinedSteps = combinedSteps.split('\n')
                
                for step in combinedSteps:
                    if ':' in step:
                        action = step.split(':')[1]
                        # remove white noise, but keep spaces between words
                        action = " ".join(action.split())
                        planSteps.append(action)
        return planSteps
                    
    
    def executePlan(self, steps):        
        for step in steps:
            elements = step.split(' ')
            
            if 'ON' in elements[0] or 'OPEN' in elements[0]:
                self.actions[elements[0]](1)
            elif 'OFF' in elements[0] or 'CLOSE' in elements[0]:
                self.actions[elements[0]](0)
                 
        
if __name__ == "__main__":
    planner = AIPlannerInterface('SR_1')
    
    while True:
        time1 = datetime.strptime(planner.time_toggleZeroDetected, '%H:%M:%S')
        time2 = datetime.strptime(datetime.now().strftime("%H:%M:%S"), '%H:%M:%S')
        difference = time2 - time1
        
        # if OPENING_HOUR.time() >= datetime.now().time() or datetime.now().time() >= CLOSING_HOUR.time():
        #     print('CLOSED')
        
        if planner.motionToggleOne or (planner.motionToggleZero and difference >= MAX_RANGE_MOTION_DETECTED): 
            print('REPLANNING')
            planner.startPlanning()
            time.sleep(5)
            planner.motionToggleOne = False
            planner.motionToggleZero = False
            plannerResponse = subprocess.check_output(["./runPlan.sh"]).decode("utf-8")
            time.sleep(5)
            planSteps = planner.getPlanSteps(plannerResponse)
            planner.executePlan(planSteps)
            
        elif planner.sensorValues['Outside_Sensor'] == 2:
            print('REPLANNING')
            planner.startPlanning()
            time.sleep(5)
            plannerResponse = subprocess.check_output(["./runPlan.sh"]).decode("utf-8")
            time.sleep(5)
            planSteps = planner.getPlanSteps(plannerResponse)
            planner.executePlan(planSteps)
            
        elif datetime.now().minute == 0 or datetime.now().minute == 30:
            print('REPLANNING')
            planner.startPlanning()
            time.sleep(5)
            plannerResponse = subprocess.check_output(["./runPlan.sh"]).decode("utf-8")
            time.sleep(5)
            planSteps = planner.getPlanSteps(plannerResponse)
            planner.executePlan(planSteps)
    
        
    
    # inits = AIPlanner.getAIPlannerInits('SR_1')    
    # goals = AIPlanner.getAIPlannerGoals(inits, 'SR_1')
    
    # AIPlanner.createAIProblemFile(inits, goals, 'SR_1')
