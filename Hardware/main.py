# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 11:44:35 2025

@author: Vivienne Beck
"""

import grovepi


sound_sensor = 5


grovepi.pinMode(sound_sensor, "OUTPUT")

while True:
    sound_level = grovepi.digitalRead(sound_sensor)
    print(sound_level)
    print('-----')
    sound_level = grovepi.analogRead(sound_sensor)
    print(sound_level)
    print('=====')
