#!/usr/bin/python
import serial
import requests
import json
import sys
from config import Config
from octoprint_api import OctoprintApi

CONFIG = Config('config.ini')

api_key = ""

api = OctoprintApi();


def is_busy() -> bool:
    response = requests.get(
        "http://localhost/api/printer?apikey=B713F275B2B74CD5BA92C07F40101649&exclude=temperature,sd")
    responseData = str(response.text)
    state = json.loads(responseData)
    return state["state"]["flags"]["printing"] or state["state"]["flags"]["pausing"] or state["state"]["flags"]["finishing"]


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
