# -*- coding: utf-8 -*-



import random
import time
from paho.mqtt import client as mqtt_client


FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60


class __MQTTPublisher:
    def __init__(self, room, deviceType, topic):
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


class MQTTPublisher_Sensor(__MQTTPublisher):
    def __init__(self, room, topic):
        self.room = room
        self.sensor = topic
        
        super().__init__(self.room, 'Sensor', self.sensor)
    
    def publish(self, value):
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)

        msg = str({'Sensor': self.sensor, 'Value': value, 'TimeStamp': current_time})
        result = self.client.publish(self.topic, msg)


class MQTTPublisher_Actuator(__MQTTPublisher):
    def __init__(self, room, topic):
        self.room = room
        self.actuator = topic
        
        super().__init__(self.room, 'Actuator', self.actuator)
    
    def publish(self, value):
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)

        msg = str({'Sensor': self.sensor, 'Value': value, 'TimeStamp': current_time})
        result = self.client.publish(self.topic, msg)



class MQTTSubscriber:
    def _init_(self, room, deviceType, device):
        # self.broker = BROKER_IP
        # self.port = PORT
        
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
        
      
        
class MQTTSubscriber_Sensor(MQTTSubscriber):
    def __init__(self, room, topic):
        self.room = room
        self.sensor = topic
        
        super().__init__(self.room, 'Sensor', self.sensor)
    
    def subscribe(self):
        # def on_message(client, userdata, msg):
        #     print(msg.payload.decode())
    
        self.client.subscribe(self.topic)
        # self.client.on_message = on_message
        
        
        
class MQTTSubscriber_Actuator(MQTTSubscriber):
    def __init__(self, room, topic):
        self.room = room
        self.actuator = topic
        
        super().__init__(self.room, 'Actuator', self.actuator)
    
    def subscribe(self):
        def on_message(client, userdata, msg):
            print(msg.payload.decode())
    
        self.client.subscribe(self.topic)
        self.client.on_message = on_message
        
