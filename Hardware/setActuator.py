# -*- coding: utf-8 -*-


import time
import threading

from MQTTInterface import MQTTSubscriber


class getter(threading.Thread):
    def __init__(self, room):
        super(getter, self).__init__()
        self.actuatorPins = { 'Heater': 6,
                              'Blinds_up': 8,
                              'Blinds_down': 5 }
        
        # AC and Light handled via Plugwise
        self.actuatorValues = { 'Blinds': 0,
                                'Light': 1,
                                'AC': 1,
                                'Heater': 0 }
        
        
        
    def startSubscriber(self):
        sub = MQTTSubscriber(self.room, 'Actuator', '#')
        sub.client.on_message = self.on_message
        
        self.sub = threading.Thread(target=sub.run)
        self.sub.start()
        print('Subscriper Active')
        
            
        
    def on_message(self, client, userdata, msg):
        if 'Blinds' in msg.payload.decode() or 'Heater' in msg.payload.decode():
            res = eval(msg.payload.decode())
            self.actuatorValues[res['Device']] = res['Value']
        
            
