"""
Si occupa di dialogare con octoprint
"""

import requests
import json
from config import Config
import subprocess
import time
import logging
import http.client as http_client
from threading import Timer
http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


class OctoprintApi():
    """
    Classe di interfaccia con le api di octoprint
    """

    def __init__(self, debug: bool = True):
        CONFIG = Config('config.ini')
        self.apikey = CONFIG['OCTOPRINT']['api_key']
        self.nozzle_temperature = CONFIG['PRINTER']['nozzle_temperature']
        self.bed_temperature = CONFIG['PRINTER']['bed_temperature']
        self.base_url = "http://localhost/api/"
        self.power_off_command = CONFIG['PRINTER']['poweroff_script']
        self.power_on_command = CONFIG['PRINTER']['poweron_script']
        self.last_heart_beat = None
        self.debug = debug
        self.connected = self.is_connected()

    def homexy(self) -> None:
        self.__postCommand({'command': 'G28'})

    def disable_stepper(self) -> None:
        self.__postCommand({'command': 'M18'})

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
        self.__postCommand({'commands': ['G91', 'G1 X10 F6000', 'G90']})

    def left(self) -> None:
        self.__postCommand({'commands': ['G91', 'G1 X-10 F6000', 'G90']})

    def backward(self) -> None:
        self.__postCommand({'commands': ['G91', 'G1 Y10 F6000', 'G90']})

    def forward(self) -> None:
        self.__postCommand({'commands': ['G91', 'G1 Y-10 F6000', 'G90']})

    def up(self) -> None:
        self.__postCommand({'commands': ['G91', 'G1 Z10 F200', 'G90']})

    def down(self) -> None:
        self.__postCommand({'commands': ['G91', 'G1 Z-10 F200', 'G90']})

    def homez(self) -> None:
        self.__postCommand({'commands': ['G91', 'G28 Z0', 'G90']})

    def extrude(self) -> None:
        self.__postCommand({'commands': ['G91', 'G1 E50 F300', 'G90']})

    def retract(self) -> None:
        self.__postCommand({'commands': ['G91', 'G1 E-50 F300', 'G90']})

    def preheat_nozzle(self) -> None:
        self.__postCommand({'command': 'M104 S'+self.nozzle_temperature})

    def preheat_bed(self) -> None:
        self.__postCommand({'command': 'M140 S'+self.bed_temperature})

    def is_busy(self) -> bool:
        url = self.__build_printer_url(None, 'exclude=temperature,sd')
        responseData = self.__get(url)
        if responseData is None:
            if self.debug:
                print('Non connesso')
            print('Busy: False')
            return False
        busy = responseData["state"]["flags"]["printing"] or responseData["state"][
            "flags"]["pausing"] or responseData["state"]["flags"]["finishing"]
        if self.debug:
            print('Busy: %s' % str(busy))
        return busy

    def is_connected(self) -> bool:
        url = self.__build_url(self.base_url + 'connection')
        response = requests.get(url, headers={'X-Api-Key': self.apikey})
        self.last_heart_beat = time.time()
        is_connected = False
        if response is not None:
            responseText = str(response.text)
            responseData = json.loads(responseText)
            is_connected = responseData['current']['state'] != "Closed"

        if self.debug:
            print("Connected: " + str(is_connected))

        return is_connected

    def connect(self) -> None:
        url = self.__build_url(self.base_url + 'connection')
        jsonData = {
            "command": "connect",
            "port": "/dev/ttyACM0",
            "baudrate": 115200
        }
        requests.post(url, json=jsonData, headers={
            'X-Api-Key': self.apikey})

    def __get(self, url: str = None) -> json:
        if self.debug:
            print('Url richiesto: %s' % url)
        if self.is_connected() == False:
            self.connect()
        if self.is_connected() == True:
            response = requests.get(url, headers={'X-Api-Key': self.apikey})
            responseData = str(response.text)
            return json.loads(responseData)
        else:
            print("WARNING - NOT CONNECTED")
            return None

    def __postCommand(self, jsonData=None) -> None:
        if self.is_connected() == False:
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
                    print('Stampante impegnata in altra operazione')

    def __build_url(self, base: str, command: str = None, additional_params: str = None) -> str:
        url = base
        if command is not None:
            url += '/' + command
        if additional_params is not None:
            url += '?' + additional_params
        return url

    def __build_printer_url(self, command: str = None, additional_params: str = None) -> str:
        return self.__build_url(self.base_url + 'printer', command, additional_params)
