# MQTT Client Configuration for AWS IoT

## Introduction

This document provides step-by-step instructions to configure the MQTT client for communicating with AWS IoT using Mosquitto.

## Prerequisites

- Mosquitto client installed on your system.
- AWS IoT Thing created with certificates and keys generated.
- Certificates and keys moved to `/etc/mosquitto/certs/` directory.

## Configuration File Setup

### Step 1: Create the Configuration File

Create a configuration file named `mosquitto_pub.conf` in the `/etc/mosquitto/conf.d/` directory or another directory of your choice. You can do this using a text editor of your choice. For example:

```bash
sudo nano /etc/mosquitto/conf.d/mosquitto_pub.conf
```

### Step 2: Configuration Parameters

Add the following configurations to the file. Replace placeholders with your actual file paths and AWS IoT endpoint:

```bash
connection awsiot
address your-endpoint.iot.your-region.amazonaws.com:8883
cafile /etc/mosquitto/certs/root-CA.crt
certfile /etc/mosquitto/certs/device-certificate.pem.crt
keyfile /etc/mosquitto/certs/device-private.pem.key
tls_version tlsv1.2
```

- `your-endpoint.iot.your-region.amazonaws.com` is your AWS IoT endpoint.
- `/etc/mosquitto/certs/root-CA.crt` is the path to the Amazon root CA certificate.
- `/etc/mosquitto/certs/device-certificate.pem.crt` is the path to your device's certificate.
- `/etc/mosquitto/certs/device-private.pem.key` is the path to your device's private key.