# -*- coding: utf-8 -*-



import random
import time
from paho.mqtt import client as mqtt_client



BROKER_IP = '192.168.188.40'
PORT = 1883



class MQTTPublisher:
    def __init__(self):
        self.broker = BROKER_IP
        self.port = PORT
        
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
        
        
    def publish(self, room, deviceType, device, value):
        if deviceType == 'Plugwise':
            msg = value
        else:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            msg = str({f'Device': device, 'Value': value, 'TimeStamp': current_time})
            
        topic = f"library/{room}/{deviceType}/{device}"
        
        result = self.client.publish(topic, msg)
    
    
    def run(self, room, deviceType, device, value):
        self.client.loop_start()
        self.publish(room, deviceType, device, value)
        self.client.loop_stop()
        


class MQTTSubscriber:
    def __init__(self, room, deviceType, device):
        self.broker = BROKER_IP
        self.port = PORT
        
        self.room = room
        self.deviceType = deviceType
        self.device = device
        
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
        topic = f"library/{self.room}/{self.deviceType}/{self.device}"
    
        self.client.subscribe(topic)
    
    
    def run(self):
        self.subscribe()
        self.client.loop_forever()
        
   
        
   
def on_message(client, userdata, msg):
    print(msg.payload.decode())
    
sub = MQTTSubscriber()
sub.client.on_message = on_message
sub.run('SR_1', '+', '+')
