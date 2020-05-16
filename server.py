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
while True:
    line = serialPort.readline()
    line = line.decode('utf-8').strip()
    if line is not "":
        print(line)
    if line == "POWER":
        if api.isOn():
            api.power_off()
        else:
            api.power_on() 
    if line == "DISABLE_STEPPER":
        api.disable_stepper()
    if line == "LEFT":
        api.left()
    if line == "FORWARD":
        api.forward()        
    if line == "HOME":
        api.homexy()
    if line == "BACKWARD":
        api.backward()        
    if line == "RIGHT":
        api.right()        
    if line == "UP":
        api.up()        
    if line == "HOMEZ":
        api.homez()        
    if line == "DOWN":
        api.down()        
    if line == "EXTRUDE":
        api.extrude()        
    if line == "RETRACT":
        api.retract()        
    if line == "HEATNOZZLE":
        api.heat_nozzle()        
    if line == "HEATPLATE":
        api.heat_bed()        
