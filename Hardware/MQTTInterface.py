# -*- coding: utf-8 -*-



import random
import time
from paho.mqtt import client as mqtt_client





class __MQTTPublisher:
    def __init__(self, room, deviceType, topic):
        self.deviceType = deviceType
        self.deviceName = topic
        self.broker = '192.168.188.40'
        self.port = 1883
        self.topic = f"library/{room}/{deviceType}/{topic}"
        
        self.client_id = f'publish-{random.randint(0, 1000)}'
        # self.username = 'emqx'
        # self.password = 'public'
        
        self.client = self.connect_mqtt()
        
        
    def connect_mqtt(self):
        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, self.client_id)
        # client.username_pw_set(self.username, self.password)
        client.connect(self.broker, self.port)
        return client
    
            
    def disconnect(self):
        self.client.disconnect()
        
        
    def publish(self, value):
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)

        msg = str({f'{self.deviceType}': self.deviceName, 'Value': value, 'TimeStamp': current_time})
        result = self.client.publish(self.topic, msg)
    
    
    def run(self, value):
        self.client.loop_start()
        self.publish(value)
        self.client.loop_stop()
        


class MQTTSubscriber:
    def __init__(self, room, deviceType, topic):
        self.broker = '192.168.188.40'
        self.port = 1883
        self.topic = self.topic = f"library/{room}/{deviceType}/{topic}"
        self.client_id = f'subscribe-{random.randint(0, 100)}'
        # self.username = 'emqx'
        # self.password = 'public'
        
        self.client = self.connect_mqtt()
        
        
    def connect_mqtt(self):
    
        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, self.client_id)
        # client.username_pw_set(self.username, self.password)
        # client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client
    
    
    def subscribe(self):
        def on_message(client, userdata, msg):
            print(msg.payload.decode())
    
        self.client.subscribe(self.topic)
        self.client.on_message = on_message
    
    
    def run(self):
        self.subscribe()
        self.client.loop_forever()
        
