# -*- coding: utf-8 -*-



import grovepi
import math

from SensorInterfaces import DigitalSensorInterface
from SensorInterfaces import AnalogSensorInterface
from Actuators.LCD import * 
from setActuator import getter

# from DatabaseConn import NumericDatabaseInterface, AbstractedDatabaseInterface

from MQTTInterface import MQTTPublisher


analogPorts = {
        'LightSensor': 1,
        'SoundSensor': 2 }

digitalPorts = {
        'PIR': 2,
        'Button': 8,
        'Temp+Humidity': 4 }

actuatorPins = { 'Heater': 6,
                 'Blinds_up': 8,
                 'Blinds_down': 3 }



def _setHeater(value):
    grovepi.digitalWrite(actuatorPins['Heater'], value)
    
def _setBlinds(value):
    if value == 1:
        grovepi.digitalWrite(actuatorPins['Blinds_down'], 1)
    elif value == 0:
        grovepi.digitalWrite(actuatorPins['Blinds_up'], 1)
        
    time.sleep(6)
    grovepi.digitalWrite(actuatorPins['Blinds_up'], 0)
    grovepi.digitalWrite(actuatorPins['Blinds_down'], 0)



if __name__ == "__main__":
    lightSensor = AnalogSensorInterface(analogPorts['LightSensor'])
    soundSensor = AnalogSensorInterface(analogPorts['SoundSensor'])
    
    PIR = DigitalSensorInterface(digitalPorts['PIR'])
    
    pub = MQTTPublisher()
    getActuatorValues = getter('SR_1')
    getActuatorValues.start()
    getActuatorValues.startSubscriber()
    
    for key, value in actuatorPins.items():
        grovepi.pinMode(value, "INPUT")
    
    while True:
        time.sleep(1)
        
        movement = PIR.getData()
        pub.run('SR_1', 'Sensor', 'Motion_Sensor', movement)
        
        lightLevel = lightSensor.getData()
        pub.run('SR_1', 'Sensor', 'Light_Sensor', lightLevel)
        
        noiseLevel = soundSensor.getData()
        pub.run('SR_1', 'Sensor', 'Sound_Sensor', noiseLevel)
        
        text = getNoiseLevelText(noiseLevel)
        writeDataToLCD(text)
        
        time.sleep(1)
        [temp, humidity] = grovepi.dht(digitalPorts['Temp+Humidity'],0)  
        if math.isnan(temp) == False and math.isnan(humidity) == False:
            pub.run('SR_1', 'Sensor', 'Temperature_Sensor', "%.02f"%temp)
            pub.run('SR_1', 'Sensor', 'Humidity_Sensor', "%.02f"%humidity)
            
        if getActuatorValues.actuatorValues['Heater_off'] == 1:
            _setHeater(0)
            getActuatorValues.actuatorValues['Heater_off'] = 0
        elif getActuatorValues.actuatorValues['Heater_on'] == 1:
            _setHeater(1)
            getActuatorValues.actuatorValues['Heater_on'] = 0
                
        if getActuatorValues.actuatorValues['Blinds_down'] == 1:
            _setBlinds(1)
            getActuatorValues.actuatorValues['Blinds_down'] = 0
        elif getActuatorValues.actuatorValues['Blinds_up'] == 1:
            _setBlinds(0)
            getActuatorValues.actuatorValues['Blinds_up'] = 0
            
        print('<3', flush=True)
        
