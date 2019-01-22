#!/usr/bin/env python3

from os import environ
from requests import post
from re import match

def write_data(payload):
    path = "/write?db=activity"
    resp = post(influxdb_server + path, data=payload)
    resp.raise_for_status()

def compile_timestamps(timestamps, db_name):
    count = 0
    payload = ""
    for ts in timestamps:
        payload += "{} value=1 {}\n".format(db_name, str(ts))
        count+=1
        if count > 99:
            write_data(payload)
            payload = ""
            count = 0

browser_history_file = environ["BROWSER_TIMESTAMP_CSV"]
zsh_history_file = environ["ZSH_HISTORY_FILE"]
influxdb_server = environ["INFLUXDB_SERVER"]

with open(browser_history_file, 'r') as s:
    browser_timestamps = [int(l.strip()) * 1000 for l in s.readlines()]
browser_timestamps.sort()

with open(zsh_history_file, 'r') as s:
    zsh_timestamps = [int(l.split(':')[1].strip()) * 1000000000
                      for l in s.readlines() if match(r'^: \d{10,15}:0;', l)]
zsh_timestamps.sort()

resp = post(influxdb_server + "/query", params={"q": "CREATE DATABASE activity"})
resp.raise_for_status()

compile_timestamps(browser_timestamps, "browser_activity")
compile_timestamps(zsh_timestamps, "zsh_activity")

