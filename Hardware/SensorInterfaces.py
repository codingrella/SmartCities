# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 19:31:16 2025

@author: Vivienne Beck
"""

import grovepi

class DigitalSensorInterface:
    def __init__(self, connector):
        self.port = connector
        grovepi.pinMode(connector, "INPUT")
        
    def getData(self):
        data = grovepi.digitalRead(self.port)
        return data
        
        

class AnalogSensorInterface:
    def __init__(self, connector):
        self.port = connector
        grovepi.pinMode(connector, "INPUT")
        
    def getData(self):
        data = grovepi.analogRead(self.port)
        return data