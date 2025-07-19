import paho.mqtt.client as mqtt

from plugwise.stick import Stick
from plugwise import Circle


stick = Stick("/dev/ttyUSB0")  # Adjust the path to your Stick device
circle = Circle(stick, "000D6F0005A9062F")  # MAC address of Circle+

print("Current electricity consumption in W: %.2f" % (circle.get_power_usage(),))

def plugwise_light(payload):
    if payload == "on":
        circle.switch_on()
    elif payload == "off":
        circle.switch_off()

def on_message(client, userdata, message):
    print(f"MQTT: {message.topic } {message.payload.decode()}")
    plugwise_light(message.payload.decode())

client = mqtt.Client()
client.connect("192.168.188.40", 1883, 60)  # Replace with your MQTT broker address
client.subscribe("library/SR_1/Plugwise/Light")
client.on_message = on_message
client.loop_start()