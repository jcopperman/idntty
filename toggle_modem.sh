#!/bin/bash
echo "4" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio4/direction
echo "0" > /sys/class/gpio/gpio4/value
sleep 1
echo "1" > /sys/class/gpio/gpio4/value
echo "4" > /sys/class/gpio/unexport
