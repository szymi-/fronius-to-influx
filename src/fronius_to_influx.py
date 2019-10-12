# coding: utf-8
import datetime
import json
from time import sleep
from typing import Any, Dict, List, Type

import pytz
from astral import Location
from influxdb import InfluxDBClient
from requests import get
from requests.exceptions import ConnectionError


class WrongFroniusData(Exception):
    pass


class SunIsDown(Exception):
    pass


class DataCollectionError(Exception):
    pass


class FroniusToInflux:
    BACKOFF_INTERVAL = 3
    IGNORE_SUN_DOWN = False

    def __init__(self, client: InfluxDBClient, location: Location, endpoints: List[str], tz: Any) -> None:
        self.client = client
        self.location = location
        self.endpoints = endpoints
        self.tz = tz
        self.data: Dict[Any, Any] = {}

    def get_float_or_zero(self, value: str) -> float:
        internal_data: Dict[Any, Any] = {}
        try:
            internal_data = self.data['Body']['Data']
        except KeyError:
            raise WrongFroniusData('Response structure is not healthy.')
        return float(internal_data.get(value, {}).get('Value', 0))

    def translate_response(self) -> List[Dict]:
        collection = self.data['Head']['RequestArguments']['DataCollection']
        timestamp = self.data['Head']['Timestamp']
        if collection == 'CommonInverterData':
            return [
                {
                    'measurement': 'DeviceStatus',
                    'time': timestamp,
                    'fields': {
                        'ErrorCode': self.data['Body']['Data']['DeviceStatus']['ErrorCode'],
                        'LEDColor': self.data['Body']['Data']['DeviceStatus']['LEDColor'],
                        'LEDState': self.data['Body']['Data']['DeviceStatus']['LEDState'],
                        'MgmtTimerRemainingTime': self.data['Body']['Data']['DeviceStatus']['MgmtTimerRemainingTime'],
                        'StateToReset': self.data['Body']['Data']['DeviceStatus']['StateToReset'],
                        'StatusCode': self.data['Body']['Data']['DeviceStatus']['StatusCode'],
                    }
                },
                {
                    'measurement': collection,
                    'time': timestamp,
                    'fields': {
                        'FAC': self.get_float_or_zero('FAC'),
                        'IAC': self.get_float_or_zero('IAC'),
                        'IDC': self.get_float_or_zero('IDC'),
                        'PAC': self.get_float_or_zero('PAC'),
                        'UAC': self.get_float_or_zero('UAC'),
                        'UDC': self.get_float_or_zero('UDC'),
                        'DAY_ENERGY': self.get_float_or_zero('DAY_ENERGY'),
                        'YEAR_ENERGY': self.get_float_or_zero('YEAR_ENERGY'),
                        'TOTAL_ENERGY': self.get_float_or_zero('TOTAL_ENERGY'),
                    }
                }
            ]
        elif collection == '3PInverterData':
            return [
                {
                    'measurement': collection,
                    'time': timestamp,
                    'fields': {
                        'IAC_L1': self.get_float_or_zero('IAC_L1'),
                        'IAC_L2': self.get_float_or_zero('IAC_L2'),
                        'IAC_L3': self.get_float_or_zero('IAC_L3'),
                        'UAC_L1': self.get_float_or_zero('UAC_L1'),
                        'UAC_L2': self.get_float_or_zero('UAC_L2'),
                        'UAC_L3': self.get_float_or_zero('UAC_L3'),
                    }
                }
            ]
        elif collection == 'MinMaxInverterData':
            return [
                {
                    'measurement': collection,
                    'time': timestamp,
                    'fields': {
                        'DAY_PMAX': self.get_float_or_zero('DAY_PMAX'),
                        'DAY_UACMAX': self.get_float_or_zero('DAY_UACMAX'),
                        'DAY_UDCMAX': self.get_float_or_zero('DAY_UDCMAX'),
                        'YEAR_PMAX': self.get_float_or_zero('YEAR_PMAX'),
                        'YEAR_UACMAX': self.get_float_or_zero('YEAR_UACMAX'),
                        'YEAR_UDCMAX': self.get_float_or_zero('YEAR_UDCMAX'),
                        'TOTAL_PMAX': self.get_float_or_zero('TOTAL_PMAX'),
                        'TOTAL_UACMAX': self.get_float_or_zero('TOTAL_UACMAX'),
                        'TOTAL_UDCMAX': self.get_float_or_zero('TOTAL_UDCMAX'),
                    }
                }
            ]
        else:
            raise DataCollectionError("Unknown data collection type.")


    def sun_is_shining(self) -> None:
        sun = self.location.sun()
        if not self.IGNORE_SUN_DOWN and not sun['sunrise'] < datetime.datetime.now(tz=self.tz) < sun['sunset']:
            raise SunIsDown
        return None

    def run(self) -> None:
        try:
            while True:
                try:
                    self.sun_is_shining()
                    collected_data = []
                    for url in self.endpoints:
                        response = get(url)
                        self.data = response.json()
                        collected_data.extend(self.translate_response())
                        sleep(self.BACKOFF_INTERVAL)
                    self.client.write_points(collected_data)
                    print('Data written')
                    sleep(self.BACKOFF_INTERVAL)
                except SunIsDown:
                    print("Waiting for sunrise")
                    sleep(60)
                    print('Waited 60 seconds for sunrise')
                except ConnectionError:
                    print("Waiting for connection...")
                    sleep(10)
                    print('Waited 10 seconds for connection')
                except KeyError:
                    raise WrongFroniusData('Response structure is not healthy')
                except Exception as e:
                    self.data = {}
                    sleep(10)
                    print("Exception: {}".format(e))

        except KeyboardInterrupt:
            print("Finishing. Goodbye!", end="\r")
