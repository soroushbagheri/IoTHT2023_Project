# Imports for MQTT
import time
import datetime
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import subprocess
import random

# Using decimal to round the value for lux :)
from decimal import Decimal

# Imports for sensor
import board
import busio

# Uncomment the correct sensor 
import adafruit_vcnl4010 	# Proximity sensor

min_threshold = 2410
# Initialize I2C bus and sensor.
i2c = busio.I2C(board.SCL, board.SDA)

# Uncomment your current sensor :)
sensor_pro = adafruit_vcnl4010.VCNL4010(i2c)	# Proximity

# Set MQTT broker and topic
broker = "test.mosquitto.org" # Broker 

pub_topic = "iotproject/asmoccupancy" # asm -scensmanagement  send messages to this topic


############### MQTT section ##################

# when connecting to mqtt do this;
def on_connect(client, userdata, flags, rc):
	if rc==0:
		print("Connection established. Code: "+str(rc))
	else:
		print("Connection failed. Code: " + str(rc))
		
def on_publish(client, userdata, mid):
    print("Published: " + str(mid))
	
def on_disconnect(client, userdata, rc):
	if rc != 0:
		print ("Unexpected disonnection. Code: ", str(rc))
	else:
		print("Disconnected. Code: " + str(rc))
	
def on_log(client, userdata, level, buf):	# Message is in buf
    print("MQTT Log: " + str(buf))

	
############### Sensor section ##################		
def get_proximity():
    proximity = sensor_pro.proximity # The higher the value, object closer to sensor
    # Adjust this threshold based on your sensor and setup
    if proximity > min_threshold:
        subprocess.run(["tdtool", "--on", "4"])
        occupancy_status ="Light Turned On"
        print(occupancy_status)
        print('Proximity: {0}'.format(proximity))
        return [proximity,occupancy_status]
    else:
        subprocess.run(["tdtool", "--off", "4"])
		occupancy_status ="Light Turned Off"
        print(occupancy_status)
        print('Proximity: {0}'.format(proximity))
        return [proximity,occupancy_status]

# Connect functions for MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_log = on_log

# Connect to MQTT 
print("Attempting to connect to broker " + broker)
client.connect(broker)	# Broker address, port and keepalive (maximum period in seconds allowed between communications with the broker)
client.loop_start()


# Loop that publishes message
while True:
	data_to_send = str(get_proximity())
	client.publish(pub_topic, str(data_to_send))
	time.sleep(2.0)	# Set delay