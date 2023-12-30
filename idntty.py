import RPi.GPIO as GPIO
import time
import logging
import serial
import random

# Configure the logger
logging.basicConfig(filename='/var/log/sms_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

# Define GPIO pins
relay_gpio_pin = 26  # Relay 1
relay2_gpio_pin = 24  # Relay 2
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Initialize GPIO pins
GPIO.setup(relay_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(relay2_gpio_pin, GPIO.OUT, initial=GPIO.LOW)

# Define the recipient's phone number
recipient_number = '27649702432'  # Replace with the actual recipient's phone number

# Global variables
isAuthenticated = False
sms_sent_counter = 0
current_pin = ""  # Holds the current PIN
waiting_for_reply = False  # Indicates system sent an SMS and is waiting for reply

def initialize_modem():
    # Open the serial port
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

        # Set SMS text mode
        ser.write(b'AT+CMGF=1\r')
        response = ser.readline()
        print("Text Mode Response:", response.strip())

        # Set new SMS message indications
        ser.write(b'AT+CNMI=2,2,0,0,0\r')
        response = ser.readline()
        print("New SMS Indication Response:", response.strip())

        ser.close()
    except Exception as e:
        print("Failed to initialize modem:", e)
        logging.error(f"Failed to initialize modem: {e}")

initialize_modem()

def reset_system():
    """Reset the system variables and states for a new cycle."""
    global isAuthenticated, sms_sent_counter, current_pin, waiting_for_reply
    isAuthenticated = False
    sms_sent_counter = 0
    current_pin = ""  # Reset the current PIN
    waiting_for_reply = False  # No longer waiting for a reply
    logging.info("System reset, ready for new access request.")

def generate_pin():
    """Generate a random 4-digit PIN."""
    return str(random.randint(1000, 9999))

def send_sms(message):
    """Send an SMS with the given message using direct serial writes."""
    global sms_sent_counter, waiting_for_reply
    if not isAuthenticated and sms_sent_counter <= 2:
        try:
            with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as ser:
                ser.write(b'AT+CMGF=1\r')
                time.sleep(1)
                ser.write(b'AT+CMGS="' + recipient_number.encode() + b'"\r')
                time.sleep(1)
                ser.write(message.encode() + b"\x1A")
                time.sleep(1)
                logging.info(f"SMS sent: {message}")
                print("SMS sent:", message)  # Printing the SMS sent for debugging
                sms_sent_counter += 1
                waiting_for_reply = True  # Now waiting for a reply
        except Exception as e:
            print("Failed to send SMS:", e)  # Print error
            logging.error(f"Failed to send SMS: {e}")

def trigger_second_relay():
    """Trigger the second relay."""
    GPIO.output(relay2_gpio_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(relay2_gpio_pin, GPIO.LOW)
    logging.info("Second relay triggered.")
    print("Second relay triggered.")

def relay_state_changed(channel):
    """Handle the relay state change and initiate an SMS message."""
    global current_pin, isAuthenticated, waiting_for_reply
    current_state = GPIO.input(channel)
    print("Relay State:", "ON" if current_state else "OFF")  # Print relay state
    if current_state:  # If the relay is activated
        logging.info("Relay is ON - Detected new access request.")
        current_pin = generate_pin()
        waiting_for_reply = False  # Allow sending a new SMS if relay toggles again
        send_sms(f'Access to your asset has been requested. Reply with the following 4 digit PIN to authenticate: {current_pin}')
    else:
        logging.info("Relay is OFF - Waiting for next activation.")

# Add an event listener for the relay GPIO pin
GPIO.add_event_detect(relay_gpio_pin, GPIO.BOTH, callback=relay_state_changed)

def receive_sms():
    global isAuthenticated, current_pin  # Ensure current_pin is global or passed appropriately

    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            print("Line Read:", line)  # Print the line read for debugging
            if line.startswith("+CMTI:"):
                index = line.split(',')[1]
                ser.write(f'AT+CMGR={index}\r\n'.encode('utf-8'))
                time.sleep(1)
                sms_content = ""
                while True:
                    sms_line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if sms_line.startswith("+CMGR:") or sms_line == "OK":
                        continue
                    if sms_line == "":
                        break
                    sms_content += sms_line + "\n"

                print(f"Incoming SMS:\n{sms_content}")  # Debug: observe the incoming message
                
                if current_pin in sms_content:  # Check if the current PIN is in the SMS
                    print("Access is authenticated.")
                    isAuthenticated = True
                    reset_system()  # Reset counters or perform additional actions as needed
                else:
                    print("Authentication failed or incorrect PIN.")

            time.sleep(1)  # Adjust as needed

    except Exception as e:
        logging.error(f"Error receiving SMS: {e}")
        print("Error receiving SMS:", e)  # Print error

try:
    logging.info("Access Control System is running...")
    while True:
        receive_sms()
        time.sleep(1)

except KeyboardInterrupt:
    logging.info("Exiting program...")

finally:
    GPIO.cleanup()
