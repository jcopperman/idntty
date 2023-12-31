import RPi.GPIO as GPIO
import time
import logging
import serial
import random
import threading

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
recipient_number = '+27649702432'  # Replace with actual recipient number

# Global variables
isAuthenticated = False
waitingForReply = False
sms_sent_counter = 0
current_pin = ""
serial_lock = threading.Lock()

# Override pins for direct control
override_open_pin = "1111"  # Disarm/Open relay
override_close_pin = "0701"  # Arm/Close relay

def initialize_modem():
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        ser.write(b'AT+CMGF=1\r')
        time.sleep(0.5)
        ser.write(b'AT+CNMI=2,2,0,0,0\r')
        time.sleep(0.5)
        print("Modem initialized.")
        return ser
    except Exception as e:
        print("Failed to initialize modem:", e)
        logging.error(f"Failed to initialize modem: {e}")
        return None

def reset_system():
    global isAuthenticated, waitingForReply, sms_sent_counter, current_pin
    isAuthenticated = False
    waitingForReply = False
    sms_sent_counter = 0
    current_pin = ""
    logging.info("System reset, ready for new access request.")

def generate_pin():
    return str(random.randint(1000, 9999))

def send_sms(message, ser):
    global sms_sent_counter, waitingForReply
    try:
        with serial_lock:
            ser.write(b'AT+CMGF=1\r')
            time.sleep(1)
            ser.write(b'AT+CMGS="' + recipient_number.encode() + b'"\r')
            time.sleep(1)
            ser.write(message.encode() + b"\x1A")
            time.sleep(3)
            logging.info(f"SMS sent: {message}")
            print("SMS sent:", message)
            sms_sent_counter += 1
            waitingForReply = True  # Flag that we are now waiting for a reply
    except Exception as e:
        print("Failed to send SMS:", e)
        logging.error(f"Failed to send SMS: {e}")

def trigger_second_relay(duration=20):
    GPIO.output(relay2_gpio_pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(relay2_gpio_pin, GPIO.LOW)
    logging.info(f"Second relay triggered for {duration} seconds.")
    print(f"Second relay triggered for {duration} seconds.")

def relay_state_changed(channel, ser):
    global current_pin
    current_state = GPIO.input(channel)
    print("Relay State:", "ON" if current_state else "OFF")
    if current_state and not isAuthenticated:
        current_pin = generate_pin()
        send_sms(f'Access to your asset has been requested. Reply with the following 4 digit PIN to authenticate: {current_pin}', ser)

def receive_sms(ser):
    global isAuthenticated, current_pin, waitingForReply
    max_retries = 5  # Maximum number of retries for reading SMS

    while True:
        with serial_lock:
            retry_count = 0
            while retry_count < max_retries and ser.isOpen():
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        print("Line Read:", line)
                        if line.startswith('+CMT:'):
                            sms_content = ser.readline().decode('utf-8').strip()
                            print(f"Incoming SMS Content:\n{sms_content}")
                            
                            # Check for override PINs
                            if sms_content.strip() == override_close_pin:
                                print("Override command received: Closing relay.")
                                trigger_second_relay(20)  # Close relay for 20 seconds
                                reset_system()
                            elif sms_content.strip() == override_open_pin:
                                print("Override command received: Opening relay.")
                                GPIO.output(relay2_gpio_pin, GPIO.LOW)  # Ensure relay is open
                                reset_system()
                            elif current_pin in sms_content:
                                print("Access is authenticated.")
                                isAuthenticated = True
                                trigger_second_relay()
                                time.sleep(20)
                                reset_system()  # Reset the system after successful authentication
                            else:
                                print("Received SMS with unexpected content or incorrect PIN.")
                            break
                        elif line in ['OK', 'ERROR']:
                            continue  # Ignore standard command responses
                        else:
                            print("Received unexpected data.")
                    else:
                        retry_count += 1
                        print(f"Waiting for data... Attempt {retry_count} of {max_retries}")
                        time.sleep(10)
                except Exception as e:
                    print("Error receiving SMS:", e)
                    logging.error(f"Error receiving SMS: {e}")
                    break  # Exit the retry loop on exception
            if retry_count == max_retries:
                print("Max retries reached. Moving to next read attempt.")
        time.sleep(1)  # Check less frequently if not expecting a reply

def main():
    ser = initialize_modem()
    if ser is not None:
        GPIO.add_event_detect(relay_gpio_pin, GPIO.BOTH, lambda channel: relay_state_changed(channel, ser))
        threading.Thread(target=receive_sms, args=(ser,)).start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting program...")
        finally:
            GPIO.cleanup()
            if ser and ser.isOpen():
                ser.close()

if __name__ == "__main__":
    main()
