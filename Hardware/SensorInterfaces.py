# -*- coding: utf-8 -*-



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