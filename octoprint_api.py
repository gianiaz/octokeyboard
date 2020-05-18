"""
Api module for talking with octoprint
"""

import requests
import json
from config import Config
import subprocess
import time
import urllib3
import logging
import http.client as http_client
from threading import Timer
import os

# http_client.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


class OctoprintApi():
    """
    Main class
    """

    def __init__(self, debug: bool = True):
        CONFIG = Config(os.path.dirname(__file__) + '/config.ini')
        self.apikey = CONFIG['OCTOPRINT']['apikey']
        self.nozzle_temperature = CONFIG['PRINTER']['nozzle_temperature']
        self.bed_temperature = CONFIG['PRINTER']['bed_temperature']
        self.base_url = CONFIG['OCTOPRINT']['host'] + "/api/"
        self.power_off_command = CONFIG['PRINTER']['poweroff_script']
        self.power_on_command = CONFIG['PRINTER']['poweron_script']
        self.stepper_step = CONFIG['PRINTER']['stepper_step']
        self.extrude_lenght = CONFIG['PRINTER']['extrude_lenght']
        self.last_heart_beat = None
        self.debug = debug
        self.conneted = self.is_connected()

    def homexy(self) -> None:
        self.__postCommand({'commands': ['M300 S200 P80', 'G28 XY']})

    def disable_stepper(self) -> None:
        self.__postCommand({'commands': ['M300 S200 P80', 'M18']})

    def power_on(self) -> None:
        if self.is_busy() == False:
            subprocess.call(self.power_on_command)
            r = Timer(8.0, self.connect)
            r.start()

    def power_off(self) -> None:
        if self.is_busy() == False:
            subprocess.call(self.power_off_command)

    def isOn(self) -> bool:
        return self.is_connected()

    def right(self) -> None:
        self.__postCommand(
            {'commands': ['M300 S200 P80', 'G91', 'G1 X%s F6000' % self.stepper_step, 'G90']})

    def left(self) -> None:
        self.__postCommand(
            {'commands': ['M300 S200 P80', 'G91', 'G1 X-%s F6000' % self.stepper_step, 'G90']})

    def backward(self) -> None:
        self.__postCommand(
            {'commands': ['M300 S200 P80', 'G91', 'G1 Y%s F6000' % self.stepper_step, 'G90']})

    def forward(self) -> None:
        self.__postCommand(
            {'commands': ['M300 S200 P80', 'G91', 'G1 Y-%s F6000' % self.stepper_step, 'G90']})

    def up(self) -> None:
        self.__postCommand(
            {'commands': ['M300 S200 P80', 'G91', 'G1 Z%s F200' % self.stepper_step, 'G90']})

    def down(self) -> None:
        self.__postCommand(
            {'commands': ['M300 S200 P80', 'G91', 'G1 Z-%s F200' % self.stepper_step, 'G90']})

    def homez(self) -> None:
        self.__postCommand(
            {'commands': ['M300 S200 P80', 'G91', 'G28 Z0', 'G90']})

    def extrude(self) -> None:
        self.__postCommand(
            {'commands': ['M300 S200 P80', 'G91', 'G1 E%s F300' % self.extrude_lenght, 'G90']})

    def retract(self) -> None:
        self.__postCommand(
            {'commands': ['M300 S200 P80', 'G91', 'G1 E-%s F300' % self.extrude_lenght, 'G90']})

    def heat_nozzle(self) -> None:
        self.__postCommand(
            {'commands': ['M300 S200 P80', 'M104 S'+self.nozzle_temperature]})

    def heat_bed(self) -> None:
        self.__postCommand(
            {'commands': ['M300 S200 P80', 'M140 S'+self.bed_temperature]})

    def is_busy(self) -> bool:
        url = self.__build_printer_url(None, 'exclude=temperature,sd')
        responseData = self.__get(url)
        if responseData is None:
            if self.debug:
                print('Not connected')
            print('Busy: False')
            return False
        busy = responseData["state"]["flags"]["printing"] or responseData["state"][
            "flags"]["pausing"] or responseData["state"]["flags"]["finishing"]
        if self.debug:
            print('Busy: %s' % str(busy))
        return busy

    def is_connected(self) -> bool:
        url = self.__build_url(self.base_url + 'connection')
        try:
            response = requests.get(url, headers={'X-Api-Key': self.apikey})
            self.last_heart_beat = time.time()
            is_connected = False
            if response is not None and response.text is not "":
                responseText = str(response.text)
                responseData = json.loads(responseText)
                is_connected = responseData['current']['state'] != "Closed"

            if self.debug:
                print("Connected: " + str(is_connected))
        except Exception:
            print('Wrong host or webserver non listening..')
            is_connected = False

        return is_connected

    def connect(self) -> None:
        url = self.__build_url(self.base_url + 'connection')
        jsonData = {
            "command": "connect",
            "port": "/dev/ttyACM0",
            "baudrate": 115200
        }
        response = requests.post(url, json=jsonData, headers={
            'X-Api-Key': self.apikey})
        if self.debug:
            print('Connection result: %d ' % response.status_code)

    def __get(self, url: str = None) -> json:
        try:
            if self.debug:
                print('Requested url: %s' % url)
            if self.is_connected() == False:
                self.connect()
            if self.is_connected() == True:
                response = requests.get(
                    url, headers={'X-Api-Key': self.apikey})
                responseData = str(response.text)
                try:
                    return json.loads(responseData)
                except Exception:
                    return None
            else:
                print("WARNING - NOT CONNECTED")
                return None
        except (requests.exceptions.RequestException, urllib3.exceptions.NewConnectionError) as e:
            print("Something gone wrong")

    def __postCommand(self, jsonData=None) -> None:
        if self.is_connected() == False:
            if self.debug is True:
                print('Not connected, trying to connect')
            self.connect()
        if self.is_connected() == True:
            url = self.__build_printer_url('command')

            if self.is_busy() == False:
                response = requests.post(url, json=jsonData, headers={
                    'X-Api-Key': self.apikey})
                if int(response.status_code) >= 400:
                    print(url)
                    print(response.status_code)
                    print(response.text)
            else:
                if self.debug:
                    print('Printer busy doing is job')

    def __build_url(self, base: str, command: str = None, additional_params: str = None) -> str:
        url = base
        if command is not None:
            url += '/' + command
        if additional_params is not None:
            url += '?' + additional_params
        return url

    def __build_printer_url(self, command: str = None, additional_params: str = None) -> str:
        return self.__build_url(self.base_url + 'printer', command, additional_params)
