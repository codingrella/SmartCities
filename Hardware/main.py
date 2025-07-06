# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 11:44:35 2025

@author: Vivienne Beck
"""

import grovepi

from Sensors.LightSensor import * 
from Sensors.PIR import * 
from Sensors.SoundSensor import * 
from Sensors.Button import * 
from Actuators.LCD import * 


ports = {
        'LightSensor': 1,
        'SoundSensor': 2,
        'PIR': 0,
        'Button': 8
        }


if __name__ == "__main__":
    while true:
        lightLevel = LightSensor.getData(ports['LightSensor'])
        print("LIGHT LEVEL:\t" + lightLevel)
        noiseLevel = SoundSensor.getData(ports['SoundSensor'])
        print("LIGHT LEVEL:\t" + noiseLevel)
        motionLevel = PIR.getData(ports['PIR'])
        print("LIGHT LEVEL:\t" + motionLevel)
        sitting = Button.getData(ports['Button'])
        print("LIGHT LEVEL:\t" + sitting)
        
        text = LCD.getNoiseLevelText(noiseLevel)
        LCD.writeData(text)