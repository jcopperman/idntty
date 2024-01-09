#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import subprocess

# MQTT setup - Your local Mosquitto broker
mqtt_broker = "100.85.122.12"
mqtt_port = 1883  # Default MQTT port (no TLS/SSL)
mqtt_topic = "asset/security/state"
mqtt_client_id = "python_client_id"
current_state = None  # Global variable to hold the current state of the relay

# GPIO setup for relay
arming_relay_pin = 23  # GPIO 23 for arming relay
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(arming_relay_pin, GPIO.OUT)  # Set GPIO 23 as an output

def on_log(client, userdata, level, buf):
    print("log: ", buf)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribe with QoS 1
    client.subscribe(mqtt_topic, 1)

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")
    if rc != 0:  # 0 indicates a call to disconnect()
        print("Unexpected disconnection. Reconnecting...")
        client.reconnect()

def on_message(client, userdata, msg):
    global current_state
    new_state = msg.payload.decode()

    if new_state != current_state:
        if new_state == "ARMED":
            GPIO.output(arming_relay_pin, GPIO.LOW)  # Activate relay (ARMED is active low)
            print("System Armed - Relay is ON")
        elif new_state == "DISARMED":
            GPIO.output(arming_relay_pin, GPIO.HIGH)  # Deactivate relay (DISARMED is active high)
            print("System Disarmed - Relay is OFF")

        # Publish the new state back to the broker for the Android app to consume
        client.publish(mqtt_topic, payload=new_state, qos=1, retain=True)  # With QoS 1 and retain flag

        current_state = new_state  # Update the current state

def check_internet():
    try:
        # Attempt to ping a reliable server
        subprocess.check_call(["ping", "-c", "1", "8.8.8.8"])
        return True
    except subprocess.CalledProcessError:
        return False

# Wait for internet connectivity
while not check_internet():
    print("Waiting for internet connectivity...")
    time.sleep(10)  # Wait for 10 seconds before checking again

# Setup MQTT client and callbacks
mqtt_client = mqtt.Client(mqtt_client_id)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

# Connect to the MQTT broker and start the loop
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()  # Starts a background thread handling reconnection and message processing

try:
    # Keep the script running
    while True:
        time.sleep(1)  # Sleeping for 1 second in the loop

except KeyboardInterrupt:
    print("Script interrupted by the user. Cleaning up...")
    GPIO.cleanup()  # Clean up GPIO to ensure a clean exit
    mqtt_client.loop_stop()  # Stop the MQTT loop
    mqtt_client.disconnect()  # Disconnect from the MQTT broker
