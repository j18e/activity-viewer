#!/usr/bin/env python3

from os import environ
from re import match
from influxdb import InfluxDBClient
import sqlite3

def post_data(client, data, measurement_name):
    print(type(data))
    print(len(data))
    body = [{"measurement": measurement_name, "time": m[0],
             "fields": {"value": m[1]}} for m in data]
    client.write_points(body)

def load_browser_history(browser_db_file):
    conn = sqlite3.connect(browser_db_file)
    cur = conn.cursor()
    cur.execute("SELECT id, url FROM moz_places")
    places = {p[0]: p[1] for p in cur.fetchall()}
    cur.execute("SELECT visit_date, place_id FROM moz_historyvisits")
    history = [(e[0] * 1000, places[e[1]]) for e in cur.fetchall()]
    return history

def load_zsh_history(zsh_history_file):
    with open(zsh_history_file, 'r') as s:
        zsh_history = [l for l in s.readlines()]
    zsh_history = [
        (int(l.split(':')[1].strip()) * 1000000000, l.split(':0;')[1].strip())
        for l in zsh_history if match(r'^: \d{10,15}:0;', l)
    ]
    return zsh_history

browser_db_file = environ["BROWSER_DB_FILE"]
zsh_history_file = environ["ZSH_HISTORY_FILE"]
influxdb_host = environ["INFLUXDB_HOST"]

browser_history = load_browser_history(browser_db_file)
zsh_history = load_zsh_history(zsh_history_file)

database_name = "activity"
client = InfluxDBClient(host=influxdb_host, database=database_name)
client.create_database(database_name)

post_data(client, zsh_history, "zsh_activity")
post_data(client, browser_history, "browser_activity")

