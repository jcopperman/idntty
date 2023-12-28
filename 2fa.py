import RPi.GPIO as GPIO
import time
import subprocess
import logging
import serial

# Configure the logger
logging.basicConfig(filename='sms_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Define the GPIO pin connected to the relay module control terminal
relay_gpio_pin = 26  # Replace with the actual GPIO pin number

# Set up GPIO mode (BCM or BOARD numbering)
GPIO.setmode(GPIO.BCM)

# Disable GPIO warnings
GPIO.setwarnings(False)

# Initialize the relay control pin as an input with pull-up resistor
GPIO.setup(relay_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define the recipient's phone number
recipient_number = '27649702432'

# Initialize the isAuthenticated flag to True
isAuthenticated = False

# Initialize the SMS sent counter
sms_sent_counter = 0

# Function to send an SMS
def send_sms(message):
    global sms_sent_counter  # Declare the counter as global

    try:
        if not isAuthenticated and sms_sent_counter <= 2:  # Check if isAuthenticated is False and counter is less than or equal to 1
            # Use subprocess to send AT commands via minicom
            cmd = f'echo -e "AT+CMGF=1\rAT+CMGS=\\"{recipient_number}\\"\r{message}\x1A" | sudo minicom -D /dev/ttyUSB0'
            subprocess.call(cmd, shell=True)
            log_message = f"SMS sent to {recipient_number}: {message}, isAuthenticated: {isAuthenticated}"
            logging.info(log_message)
            print(log_message)  # You can still print it if needed
            sms_sent_counter += 1  # Increment the counter
        else:
            print("Waiting for authentication...")
    except Exception as e:
        error_message = f"Error sending SMS: {e}"
        logging.error(error_message)
        print(error_message)

# Function to handle relay state change and send SMS
def relay_state_changed(channel):
    global isAuthenticated  # Declare the flag as global

    if not isAuthenticated:  # Check if isAuthenticated is False
        if GPIO.input(channel):  # If relay is activated (Normally Open)
            print("Relay is ON")
            sms_message = 'Access to your vehicle has been requested. Reply Yes to authenticate.'
            send_sms(sms_message)
            time.sleep(5)  # Add a delay after sending an SMS
        else:  # Relay is deactivated (open)
            print("Relay is OFF")

# Add an event listener for the relay GPIO pin
GPIO.add_event_detect(relay_gpio_pin, GPIO.BOTH, callback=relay_state_changed)

# Function to listen for incoming SMS messages
def receive_sms():
    global isAuthenticated  # Declare the flag as global

    try:
        # Open the serial port (replace '/dev/ttyUSB0' with your modem's device path)
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("+CMTI:"):  # Check for incoming SMS indicator
                # Extract the SMS index
                index = line.split(',')[1]
                # Read the SMS content using AT commands
                ser.write(f'AT+CMGR={index}\r\n'.encode('utf-8'))
                time.sleep(1)
                sms_content = ""
                while True:
                    sms_line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if sms_line.startswith("+CMGR:") or sms_line == "OK":
                        # Ignore header lines and stop when "OK" is received
                        continue
                    if sms_line == "":
                        # Stop when an empty line is encountered
                        break
                    sms_content += sms_line + "\n"
                # Process the incoming SMS content here
                print(f"Incoming SMS:\n{sms_content}")
                # Add your logic to check for "Yes" reply and set the authenticated flag
                if "Yes" in sms_content:
                    # Set the authenticated flag to True
                    print("Access is authenticated.")
                    print("isAuthenticated: True")
                    print("Relay is OFF")
                    isAuthenticated = True  # Update the flag
                    sms_sent_counter = 0  # Reset the counter
                    # Add your code to perform authenticated actions here
                    # For example, activate the relay or perform other tasks.
            time.sleep(1)  # Adjust the polling interval as needed

    except Exception as e:
        error_message = f"Error receiving SMS: {e}"
        logging.error(error_message)
        print(error_message)

try:
    # Keep the script running
    while True:
        # time.sleep(1)  # You can add your own logic here

        # Check for incoming SMS messages and set the 'isAuthenticated' flag
        receive_sms()

except KeyboardInterrupt:
    pass  # No need to clean up here, as cleanup is done later

finally:
    # Clean up GPIO pins when the program is terminated (Ctrl+C)
    GPIO.cleanup()

# Close the serial port
subprocess.call(f'sudo minicom -C', shell=True)
