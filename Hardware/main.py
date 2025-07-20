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
                 'Blinds_down': 5 }



def _setHeater(value):
    grovepi.digitalWrite(actuatorPins['Heater'], value)
    
def _setBlinds(value):
    if value == 1:
        grovepi.digitalWrite(actuatorPins['Blinds_down'], 1)
    elif value == 0:
        grovepi.digitalWrite(actuatorPins['Blinds_up'], 1)
        grovepi.digitalWrite(actuatorPins['Blinds_down'], 1)
        
    time.sleep(4)
    grovepi.digitalWrite(actuatorPins['Blinds_up'], 0)
    grovepi.digitalWrite(actuatorPins['Blinds_down'], 0)





if __name__ == "__main__":
    # dbInterface_num = NumericDatabaseInterface()
    lightSensor = AnalogSensorInterface(analogPorts['LightSensor'])
    soundSensor = AnalogSensorInterface(analogPorts['SoundSensor'])
    
    PIR = DigitalSensorInterface(digitalPorts['PIR'])
    # button = DigitalSensorInterface(digitalPorts['Button'])
    
    
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
        # dbInterface_num.updateMotion(movement)
        # print("MOVEMENT:\t" + str(movement))
        
        # sitting = button.getData()
        # print("SITTING:\t" + str(sitting))
        
        lightLevel = lightSensor.getData()
        pub.run('SR_1', 'Sensor', 'Light_Sensor', lightLevel)
        # dbInterface_num.updateLightLevel(lightLevel)
        # print("LIGHT LEVEL:\t" + str(lightLevel))
        
        noiseLevel = soundSensor.getData()
        pub.run('SR_1', 'Sensor', 'Sound_Sensor', noiseLevel)
        # dbInterface_num.updateNoiseLevel(noiseLevel)
        #print("NOISE LEVEL:\t" + str(noiseLevel))
        
        text = getNoiseLevelText(noiseLevel)
        writeDataToLCD(text)
        
        time.sleep(1)
        [temp, humidity] = grovepi.dht(digitalPorts['Temp+Humidity'],0)  
        if math.isnan(temp) == False and math.isnan(humidity) == False:
            pub.run('SR_1', 'Sensor', 'Temperature_Sensor', "%.02f"%temp)
            pub.run('SR_1', 'Sensor', 'Humidity_Sensor', "%.02f"%humidity)
            # dbInterface_num.updateTemperature(temp)
            # dbInterface_num.updateHumidity(humidity)
            # print("temp =  C humidity =%.02f%%"%(temp, humidity))
            
        _setHeater(getActuatorValues.actuatorValues['Heater'])
        _setBlinds(getActuatorValues.actuatorValues['Blinds'])
        
        print('<3', flush=True)
        
