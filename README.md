# idntty

## Raspberry Pi Vehicle Access Control System

## Overview
This project is a Raspberry Pi-based vehicle access control system using two-factor authentication (2FA) with GSM technology. It's designed to manage and control access to vehicles, enhancing security by requiring authentication before access is granted. The system uses RFID and SMS authentication, integrated with a GSM module for communication.

## Features
- **2FA Security**: Enhances vehicle security by requiring a second form of verification.
- **SMS Communication**: Send and receive SMS for remote control and monitoring.
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
  python 2fa.py
  ```
2. **Sending Commands**: The system will listen for incoming SMS commands to authenticate access.

## Functionality
- **Relay State Change**: Detects changes in the relay state and sends an SMS alert.
- **Send SMS**: Sends an SMS when access is attempted.
- **Recieve SMS**: Listens for incoming SMS messages to authenticate access.

## Author
Jonathan Opperman
