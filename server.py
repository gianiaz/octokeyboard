#!/usr/bin/python
import serial
import requests
import json
import sys
from config import Config
from octoprint_api import OctoprintApi
import os

CONFIG = Config(os.path.dirname(__file__) + '/config.ini')
api_key = ""
api = OctoprintApi()
serialPort = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.5)

try:
    while True:
        cmd = serialPort.readline()
        cmd = cmd.decode('utf-8').strip()
        if cmd is not "":
            print(cmd)
        if cmd == "POWER":
            if api.isOn():
                api.power_off()
            else:
                api.power_on()
        if cmd == "DISABLE_STEPPER":
            api.disable_stepper()
        if cmd == "LEFT":
            api.left()
        if cmd == "FORWARD":
            api.forward()
        if cmd == "HOME":
            api.homexy()
        if cmd == "BACKWARD":
            api.backward()
        if cmd == "RIGHT":
            api.right()
        if cmd == "UP":
            api.up()
        if cmd == "HOMEZ":
            api.homez()
        if cmd == "DOWN":
            api.down()
        if cmd == "EXTRUDE":
            api.extrude()
        if cmd == "RETRACT":
            api.retract()
        if cmd == "HEATNOZZLE":
            api.heat_nozzle()
        if cmd == "HEATPLATE":
            api.heat_bed()
except KeyboardInterrupt:
    print('Good bye :-)')
    sys.exit(0)
