# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 11:44:35 2025

@author: Vivienne Beck
"""

import grovepi

from SensorInterfaces import DigitalSensorInterface
from SensorInterfaces import AnalogSensorInterface


analogPorts = {
        'LightSensor': 1,
        'SoundSensor': 2
        }

digitalPorts = {
        'PIR': 2,
        'Button': 8
        }


if __name__ == "__main__":
    lightSensor = AnalogSensorInterface(analogPorts['LightSensor'])
    soundSensor = AnalogSensorInterface(analogPorts['SoundSensor'])
    
    PIR = DigitalSensorInterface(digitalPorts['PIR'])
    button = DigitalSensorInterface(digitalPorts['Button'])
    
    while True:
        movement = PIR.getData()
        print("MOVEMENT:\t" + str(movement))
        sitting = button.getData()
        print("SITTING:\t" + str(sitting))
        
        lightLevel = lightSensor.getData()
        print("LIGHT LEVEL:\t" + str(lightLevel))
        noiseLevel = soundSensor.getData()
        print("NOISE LEVEL:\t" + str(noiseLevel))
        
        
        
        
        ## min 0 ; max 1023
        # lightLevel = LightSensor.getData(ports['LightSensor'])
        # print("LIGHT LEVEL:\t" + lightLevel)
        
        
        # # test thresholds
        # noiseLevel = SoundSensor.getData(ports['SoundSensor'])
        # print("LIGHT LEVEL:\t" + noiseLevel)
        
        
        
        # motionLevel = PIR.getData(ports['PIR'])
        # print("LIGHT LEVEL:\t" + motionLevel)
        
        # sitting = Button.getData(ports['Button'])
        # print("LIGHT LEVEL:\t" + sitting)
        
        # text = LCD.getNoiseLevelText(noiseLevel)
        # LCD.writeData(text)