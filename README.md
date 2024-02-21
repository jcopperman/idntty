# idntty

## Raspberry Pi  Access Control System

## Overview
This project is a Raspberry Pi-based access control system using two-factor authentication (2FA) with GSM technology. It's designed to manage and control access to assets, enhancing security by requiring authentication before access is granted. The system uses native mobile authentication, integrated with a GSM module for communication.

## Features
- **2FA Security**: Enhances vehicle security by requiring a second form of verification.
- **GSM Communication**: Send and receive messages over 3G for remote control and monitoring.
- **Relay Control**: Manage access with a relay module connected to the Raspberry Pi.
- **Logging**: Keep track of system access and errors through log files.

## Hardware Requirements
- Raspberry Pi (any model with GPIO pins)
- GSM Module (connected via USB, `/dev/ttyUSB0`)
- Relay Module
- Power supply for Raspberry Pi and GSM module
- Jumper wires and a breadboard for connections

## Software Dependencies
- RPi.GPIO (for Raspberry Pi GPIO control)
- Python Serial (for GSM communication)
- Python Subprocess (for executing shell commands)
- Python Logging (for logging information and errors)
- Mosquitto for MQTT protocol

## Installation & Setup
1. **Hardware Setup**: Connect the GSM module and relay to the Raspberry Pi according to the GPIO configuration.
2. **Software Setup**: Install the required Python packages if not already installed:
   ```bash
   pip install RPi.GPIO pyserial
   ```
3. **Configuration**: The relay_gpio_pin value in the script is currently set to GPIO pin number 26.

## Usage
1. **Running the Script**: Execute the script on the Raspberry Pi via SSH.
  ```bash
  python idntty-control.py
  ```
2. **Sending Commands**: The system will listen for incoming commands to authenticate access via the MQTT broker.

## Functionality
- **Relay State Change**: Relay triggered by Python function based on topic subscription to switch NO/NC.
- **Publich Topic**: Publishes the state or location of the system (ARM/DISARM, GPS Coordinates)
- **Subscribe to Topic**: Listens for incoming messages to authenticate access (ARM/DISARM).

## Author
Jonathan Opperman

## License
Licensed under Apache 2.0 - See License.md
