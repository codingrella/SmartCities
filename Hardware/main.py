# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 11:44:35 2025

@author: Vivienne Beck
"""

import grovepi

# import Sensors.LightSensor as LightSensor
# import Sensors.PIR as PIR
# import Sensors.SoundSensor as SoundSensor
# import Sensors.Button as Button
# import Actuators.LCD as LCD


ports = {
        'LightSensor': 1,
        'SoundSensor': 2,
        'PIR': 0,
        'Button': 8
        }


if __name__ == "__main__":
    while True:
        lightLevel = grovepi.analogRead(ports['LightSensor'])
        print("LIGHT LEVEL:\t" + lightLevel)
        noiseLevel = grovepi.analogRead(ports['SoundSensor'])
        print("NOISE LEVEL:\t" + noiseLevel)
        motionLevel = grovepi.analogRead(ports['PIR'])
        print("MOTION LEVEL:\t" + motionLevel)
        sitting = grovepi.analogRead(ports['Button'])
        print("OCCUPIED:\t" + sitting)
        
       # text = LCD.getNoiseLevelText(noiseLevel)
       # LCD.writeData(text)
