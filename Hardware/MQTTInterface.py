# -*- coding: utf-8 -*-

import random
import time
from paho.mqtt import client as mqtt_client


FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60


class MQTTPublisher:
    def __init__(self, room, deviceType, topic):
        self.broker = '192.168.63.237'
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
    
    
    def publish(self, msg):
        result = self.client.publish(self.topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{self.topic}`")
        else:
            print(f"Failed to send message to topic {self.topic}")
            
    def disconnect(self):
        self.client.disconnect()
    
    
    def run(self, value):
        self.client.loop_start()
        self.publish(value)
        self.client.loop_stop()

        


class MQTTPublisher_Sensor(MQTTPublisher):
    def __init__(self, room, topic):
        self.room = room
        self.sensor = topic
        
        super().__init__(room, 'Sensor', topic)
    
    def publish(self, value):
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)

        msg = str({'Sensor': self.sensor, 'Value': value, 'TimeStamp': current_time})
        result = self.client.publish(self.topic, msg)







class MQTTSubscriber:
    def __init__(self, topic):
        self.broker = 'test.mosquitto.org'
        self.port = 1883
        self.topic = f"{topic}"
        self.client_id = f'subscribe-{random.randint(0, 100)}'
        # self.username = 'emqx'
        # self.password = 'public'
        
        self.client = self.connect_mqtt()
        
    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)
    
        client = mqtt_client.Client(self.client_id)
        # client.username_pw_set(self.username, self.password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client
    
    def subscribe(self):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    
        self.client.subscribe(topic)
        self.client.on_message = on_message
    
    
    def run(self):
        self.client = connect_mqtt()
        subscribe(client)
        self.client.loop_forever()
