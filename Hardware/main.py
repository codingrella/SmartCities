# -*- coding: utf-8 -*-



import grovepi
import math

from SensorInterfaces import DigitalSensorInterface
from SensorInterfaces import AnalogSensorInterface
from Actuators.LCD import * 

# from DatabaseConn import NumericDatabaseInterface, AbstractedDatabaseInterface

from MQTTInterface import MQTTPublisher_Sensor as pub_Sensor


analogPorts = {
        'LightSensor': 1,
        'SoundSensor': 2
        }

digitalPorts = {
        'PIR': 2,
        'Button': 8,
        'Temp+Humidity': 4
        }


# pub = MQTTPublisher_Sensor('SR_1', 'test')
# pub.run('HELLO')
# pub.disconnect()

if __name__ == "__main__":
    # dbInterface_num = NumericDatabaseInterface()
    lightSensor = AnalogSensorInterface(analogPorts['LightSensor'])
    soundSensor = AnalogSensorInterface(analogPorts['SoundSensor'])
    
    PIR = DigitalSensorInterface(digitalPorts['PIR'])
    # button = DigitalSensorInterface(digitalPorts['Button'])
    
    
    pub_LightSensor_01 = pub_Sensor('SR_1', 'Light_Sensor')
    pub_SoundSensor_01 = pub_Sensor('SR_1', 'Sound_Sensor')
    pub_MotionSensor_01 = pub_Sensor('SR_1', 'Motion_Sensor')
    pub_TempSensor_01 = pub_Sensor('SR_1', 'Temperature_Sensor')
    pub_HumiditySensor_01 = pub_Sensor('SR_1', 'Humidity_Sensor')
    
    while True:
        time.sleep(1)
        
        movement = PIR.getData()
        pub_MotionSensor_01.run(movement)
        # dbInterface_num.updateMotion(movement)
        # print("MOVEMENT:\t" + str(movement))
        
        # sitting = button.getData()
        # print("SITTING:\t" + str(sitting))
        
        lightLevel = lightSensor.getData()
        pub_LightSensor_01.run(lightLevel)
        # dbInterface_num.updateLightLevel(lightLevel)
        # print("LIGHT LEVEL:\t" + str(lightLevel))
        
        noiseLevel = soundSensor.getData()
        pub_SoundSensor_01.run(noiseLevel)
        # dbInterface_num.updateNoiseLevel(noiseLevel)
        #print("NOISE LEVEL:\t" + str(noiseLevel))
        
        text = getNoiseLevelText(noiseLevel)
        writeDataToLCD(text)
        
        time.sleep(1)
        [temp, humidity] = grovepi.dht(digitalPorts['Temp+Humidity'],0)  
        if math.isnan(temp) == False and math.isnan(humidity) == False:
            pub_TempSensor_01.run("%.02f"%temp)
            pub_HumiditySensor_01.run("%.02f"%humidity)
            # dbInterface_num.updateTemperature(temp)
            # dbInterface_num.updateHumidity(humidity)
            # print("temp =  C humidity =%.02f%%"%(temp, humidity))
            
            
        
        print('', flush=True)
        
