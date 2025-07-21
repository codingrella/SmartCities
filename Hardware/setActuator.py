# -*- coding: utf-8 -*-


import time
import threading

from MQTTInterface import MQTTSubscriber


class getter(threading.Thread):
    def __init__(self, room):
        super(getter, self).__init__()
        self.room  = room
        self.actuatorPins = { 'Heater': 6,
                              'Blinds_up': 8,
                              'Blinds_down': 5 }
        
        # AC and Light handled via Plugwise
        self.actuatorValues = { 'Blinds_down': 0,
                                'Blinds_up': 1,
                                'Heater_off': 0,
                                'Heater_on': 1}
        
        
        
    def startSubscriber(self):
        sub = MQTTSubscriber(self.room, 'Actuator', '#')
        sub.client.on_message = self.on_message
        
        self.sub = threading.Thread(target=sub.run)
        self.sub.start()
        print('Subscriber Active')
        
            
        
    def on_message(self, client, userdata, msg):
        if 'Heater' in msg.payload.decode():
            res = eval(msg.payload.decode())
            if res['Value'] == 0:
                self.actuatorValues['Heater_off'] = 1
            elif res['Value'] == 1:
                self.actuatorValues['Heater_on'] = 1
        
        elif 'Blinds' in msg.payload.decode():
            res = eval(msg.payload.decode())
            if res['Value'] == 0:
                self.actuatorValues['Blinds_down'] = 1
            elif res['Value'] == 1:
                self.actuatorValues['Blinds_up'] = 1
        
            
