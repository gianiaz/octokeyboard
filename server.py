#!/usr/bin/python
import serial
import requests
import json
import sys
from config import Config

CONFIG = Config('config.ini')

api_key = ""


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
    if line == "HOME":
        data = {'command': 'G28'}
        url = "http://localhost/api/printer/command?apikey=B713F275B2B74CD5BA92C07F40101649"
        response = requests.post(url, json=data)
        print(response.status_code)
