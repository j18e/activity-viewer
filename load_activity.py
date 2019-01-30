#!/usr/bin/env python3

from os import environ
from re import match
from influxdb import InfluxDBClient
from json import dumps

def post_data(client, data, measurement_name):
    body = [{"measurement": measurement_name, "time": m[0],
             "fields": {"value": m[1]}} for m in data]
    client.write_points(body)


browser_history_file = environ["BROWSER_TIMESTAMP_CSV"]
zsh_history_file = environ["ZSH_HISTORY_FILE"]
influxdb_host = environ["INFLUXDB_HOST"]

with open(browser_history_file, 'r') as s:
    browser_timestamps = [(int(l.strip()) * 1000, 1) for l in s.readlines()]
browser_timestamps.sort()

with open(zsh_history_file, 'r') as s:
    zsh_timestamps = [(int(l.split(':')[1].strip()) * 1000000000,
                       l.split(':0;')[1].strip())
                      for l in s.readlines() if match(r'^: \d{10,15}:0;', l)]
zsh_timestamps.sort()

database_name = "activity"
client = InfluxDBClient(host=influxdb_host, database=database_name)
client.create_database(database_name)

post_data(client, zsh_timestamps, "zsh_activity")
post_data(client, browser_timestamps, "browser_activity")

