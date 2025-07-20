# -*- coding: utf-8 -*-



import grovepi
import math

from SensorInterfaces import DigitalSensorInterface
from SensorInterfaces import AnalogSensorInterface
from Actuators.LCD import * 
from setActuator import setter

# from DatabaseConn import NumericDatabaseInterface, AbstractedDatabaseInterface

from MQTTInterface import MQTTPublisher


analogPorts = {
        'LightSensor': 1,
        'SoundSensor': 2
        }

digitalPorts = {
        'PIR': 2,
        'Button': 8,
        'Temp+Humidity': 4
        }


# pub = MQTTPublisher_Sensor('SR_1', 'test')
# pub.run('HELLO')
# pub.disconnect()

if __name__ == "__main__":
    # dbInterface_num = NumericDatabaseInterface()
    lightSensor = AnalogSensorInterface(analogPorts['LightSensor'])
    soundSensor = AnalogSensorInterface(analogPorts['SoundSensor'])
    
    PIR = DigitalSensorInterface(digitalPorts['PIR'])
    # button = DigitalSensorInterface(digitalPorts['Button'])
    
    
    pub = MQTTPublisher()
    setActuators = setter('SR_1')
    setActuators.start()
    
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
            
            
        
        print('<3', flush=True)
        
