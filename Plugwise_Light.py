import paho.mqtt.client as mqtt
import random

from plugwise import *
import plugwise.util


stick = Stick("/dev/ttyUSB0")  # Adjust the path to your Stick device
circle = Circle("000D6F0005A9062F", stick)  # MAC address of Circle+

print("Current electricity consumption in W: %.2f" % (circle.get_power_usage(),))

def plugwise_light(payload):
    if payload == "on":
        circle.switch_on()
    elif payload == "off":
        circle.switch_off()

class MQTTSubscriber:
    def __init__(self):
        self.broker = '192.168.188.40'
        self.port = 1883
        self.topic = "library/SR_1/Plugwise/Light"
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
            plugwise_light(msg.payload.decode())
    
        self.client.subscribe(self.topic)
        self.client.on_message = on_message    
    
    def run(self):
        self.subscribe()
        self.client.loop_forever()
        
sub = MQTTSubscriber()
sub.run()

# def on_connect(client, userdata, flags, rc):
#     client.subscribe("library/SR_1/Plugwise/Light")


# def on_message(client, userdata, message):
#     print(f"MQTT: {message.topic} {message.payload.decode()}")
#     plugwise_light(message.payload.decode())

# #MQTT client setup
# #API Version 5.0
# client = mqtt.Client(callback_api_version=5)
# client.on_connect = on_connect
# client.on_message = on_message
# client.connect("192.168.188.40", 1883, 60)  # Replace with your MQTT broker address
# client.loop_start()