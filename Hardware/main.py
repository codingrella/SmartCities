# -*- coding: utf-8 -*-



import grovepi
import math

from SensorInterfaces import DigitalSensorInterface
from SensorInterfaces import AnalogSensorInterface
from Actuators.LCD import * 

from DatabaseConn import NumericDatabaseInterface, AbstractedDatabaseInterface


analogPorts = {
        'LightSensor': 1,
        'SoundSensor': 2
        }

digitalPorts = {
        'PIR': 2,
        'Button': 8,
        'Temp+Humidity': 4
        }


if __name__ == "__main__":
    dbInterface = NumericDatabaseInterface()
    lightSensor = AnalogSensorInterface(analogPorts['LightSensor'])
    soundSensor = AnalogSensorInterface(analogPorts['SoundSensor'])
    
    PIR = DigitalSensorInterface(digitalPorts['PIR'])
    # button = DigitalSensorInterface(digitalPorts['Button'])
    
    while True:
        time.sleep(1)
        
        movement = PIR.getData()
        dbInterface.updateMotion(movement)
        #print("MOVEMENT:\t" + str(movement))
        
        # sitting = button.getData()
        # print("SITTING:\t" + str(sitting))
        
        lightLevel = lightSensor.getData()
        dbInterface.updateLightLevel(lightLevel)
        # print("LIGHT LEVEL:\t" + str(lightLevel))
        
        noiseLevel = soundSensor.getData()
        dbInterface.updateNoiseLevel(noiseLevel)
        #print("NOISE LEVEL:\t" + str(noiseLevel))
        
        text = getNoiseLevelText(noiseLevel)
        writeDataToLCD(text)
        
        time.sleep(1)
        [temp,humidity] = grovepi.dht(digitalPorts['Temp+Humidity'],0)  
        if math.isnan(temp) == False and math.isnan(humidity) == False:
            dbInterface.updateTemperature(temp)
            dbInterface.updateHumidity(humidity)
            # print("temp = %.02f C humidity =%.02f%%"%(temp, humidity))
            
            
        
        print('', flush=True)
        
