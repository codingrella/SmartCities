# -*- coding: utf-8 -*-


import time
import grovepi
import threading

from MQTTInterface import MQTTSubscriber, MQTTPublisher


class setter(threading.Thread):
    def __init__(self, room):
        self.actuatorToFunc = { 'AC': self._setAC,
                                'Heater': self._setHeater,
                                'Blinds': self._setBlinds,
                                'Light': self._setLights }
        
        self.actuatorPins = { 'AC': 3,
                              'Heater': 6,
                              'Blinds_up': 8,
                              'Blinds_down': 5 }
        
        self._setPinModes()
        
        self.room = room
        self.pub = MQTTPublisher()
        
        
    def startSubscriber(self):
        sub = MQTTSubscriber(self.room, 'Actuator', '#')
        sub.client.on_message = self.on_message
        
        self.sub = threading.Thread(target=sub.run)
        self.sub.start()
        
        
    def _setPinModes(self):
        for key, value in self.actuatorPins.items():
            grovepi.pinMode(value, "INPUT")
            
    def _setAC(self, value):
        if value == 1:
            value = 'ac_on'
        elif value == 0:
            value = 'ac_off'
            
        self.pub.run('SR_1', 'Actuator', 'AC', value)
        
    def _setHeater(self, value):
        grovepi.digitalWrite(self.actuatorPins['Heater'], value)
        
    def _setBlinds(self, value):
        if value == 1:
            grovepi.digitalWrite(self.actuatorPins['Blinds_down'], 1)
        elif value == 0:
            grovepi.digitalWrite(self.actuatorPins['Blinds_up'], 1)
            grovepi.digitalWrite(self.actuatorPins['Blinds_down'], 1)
            
        time.sleep(4)
        grovepi.digitalWrite(self.actuatorPins['Blinds_up'], 0)
        grovepi.digitalWrite(self.actuatorPins['Blinds_down'], 0)
        
    def _setLights(self, value):
        if value == 1:
            value = 'light_on'
        elif value == 0:
            value = 'light_off'
            
        self.pub.run('SR_1', 'Actuator', 'Light', value)
        
    def on_message(self, client, userdata, msg):
        if msg.payload.decode() != 'light_on' and msg.payload.decode() != 'light_off' and msg.payload.decode() != 'ac_on' and msg.payload.decode() != 'ac_off' and msg.payload.decode() != 'up' and msg.payload.decode() != 'down':
            res = eval(msg.payload.decode())
            self.actuatorToFunc[res['Device']](res['Value'])
        
            
