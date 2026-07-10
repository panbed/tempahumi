import json
import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import requests

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

DB_FILE = 'database.db'
CLIMATE_URL = 'http://192.168.1.179/'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def insert_climate_data():
    try:
        # get temp and humidity from esp32
        response = requests.get(CLIMATE_URL, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        print(json_data)

        temperature = json_data['temperature']
        humidity = json_data['humidity']

        # insert into sqlite database
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO climate (temperature, humidity) VALUES (?, ?)',
                (temperature, humidity)
            )
            conn.commit()
    except requests.exceptions.RequestException as error:
        print(f"something went horribly wrong (the server is probably down): {str(error)}")
        return

# scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    id='sqlite_climate_data_inserter',
    func=insert_climate_data,
    trigger='interval',
    seconds=60
)
scheduler.start()

@app.route('/')
def index():
    conn = get_db_connection()
    climate_info = conn.execute('SELECT * FROM climate LIMIT 10080').fetchall()
    conn.close()
    return render_template('index.html', climate_info=climate_info)

@app.route('/chart')
def chart():
    conn = get_db_connection()
    climate_info = conn.execute('SELECT * FROM climate LIMIT 10080').fetchall()
    json_data = json.dumps([dict(row) for row in climate_info])
    conn.close()
    return render_template('chart.html', climate_info=json_data)

if __name__ == '__main__':
    app.run()