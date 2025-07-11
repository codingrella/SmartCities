# -*- coding: utf-8 -*-



import grovepi
import math

from SensorInterfaces import DigitalSensorInterface
from SensorInterfaces import AnalogSensorInterface
from Actuators.LCD import * 


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
    lightSensor = AnalogSensorInterface(analogPorts['LightSensor'])
    soundSensor = AnalogSensorInterface(analogPorts['SoundSensor'])
    
    PIR = DigitalSensorInterface(digitalPorts['PIR'])
    button = DigitalSensorInterface(digitalPorts['Button'])
    
    while True:
        time.sleep(1)
        movement = PIR.getData()
        print("MOVEMENT:\t" + str(movement))
        sitting = button.getData()
        print("SITTING:\t" + str(sitting))
        
        time.sleep(1)
        lightLevel = lightSensor.getData()
        print("LIGHT LEVEL:\t" + str(lightLevel))
        noiseLevel = soundSensor.getData()
        print("NOISE LEVEL:\t" + str(noiseLevel))
        
        text = getNoiseLevelText(noiseLevel)
        print('', flush=True)
        writeDataToLCD(text)
        
        time.sleep(1)
        [temp,humidity] = grovepi.dht(digitalPorts['Temp+Humidity'],blue)  
        if math.isnan(temp) == False and math.isnan(humidity) == False:
            print("temp = %.02f C humidity =%.02f%%"%(temp, humidity))
        
