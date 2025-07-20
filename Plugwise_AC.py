import paho.mqtt.client as mqtt
import random

from plugwise import *
import plugwise.util


stick = Stick("/dev/ttyUSB0")  # Adjust the path to your Stick device
circle = Circle("000D6F0004B1E1C4", stick)  # MAC address of Circle

print("Current electricity consumption in W: %.2f" % (circle.get_power_usage(),))

def plugwise_ventilator(payload):
    if payload == 'ac_on':
        circle.switch_on()
    elif payload == 'ac_off':
        circle.switch_off()


class MQTTSubscriber:
    def __init__(self):
        self.broker = '192.168.188.40'
        self.port = 1883
        self.topic = "library/SR_1/Actuator/AC"
        self.client_id = f'subscribe-{random.randint(0, 100)}'
        # self.username = 'emqx'
        # self.password = 'public'
        
        self.client = self.connect_mqtt()
        
    def connect_mqtt(self):
    
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, self.client_id)
        # client.username_pw_set(self.username, self.password)
        # client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client
    
    def subscribe(self):
        def on_message(client, userdata, msg):
            print(f"Received {msg.payload.decode()} from {msg.topic} topic")
            plugwise_ventilator(msg.payload.decode())
    
        self.client.subscribe(self.topic)
        self.client.on_message = on_message
    
    
    def run(self):
        self.subscribe()
        self.client.loop_forever()
        
sub = MQTTSubscriber()
sub.run()