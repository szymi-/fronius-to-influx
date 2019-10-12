from flask import Flask, request
import random
import json
import datetime
import pytz

app = Flask(__name__)

with open('samples/CommonInverterData.json', 'r') as f:
    common_inverter_data = [json.loads(r) for r in f.readlines()]

with open('samples/3PInverterData.json', 'r') as f:
    threep_inverter_data = [json.loads(r) for r in f.readlines()]

with open('samples/MinMaxInverterData.json', 'r') as f:
    min_max_inverter_data = [json.loads(r) for r in f.readlines()]


@app.route('/CommonInverterData.json')
def common_inverter_data_endpoint() -> str:
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Warsaw')).isoformat('T')
    json_response = random.choice(common_inverter_data)
    json_response['Head']['Timestamp'] = now
    return json_response


@app.route('/3PInverterData.json')
def threep_inverter_data_endpoint() -> str:
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Warsaw')).isoformat('T')
    json_response = random.choice(threep_inverter_data)
    json_response['Head']['Timestamp'] = now
    return json_response


@app.route('/MinMaxInverterData.json')
def min_max_inverter_data_endpoint() -> str:
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Warsaw')).isoformat('T')
    json_response = random.choice(min_max_inverter_data)
    json_response['Head']['Timestamp'] = now
    return json_response
