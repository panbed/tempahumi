import json
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import populate_weather

# load environment variables from .env
load_dotenv()

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

def get_db_connection() -> sqlite3.Connection:
    db_file = os.getenv("DB_FILE")
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def insert_climate_data() -> None:
    db_file = os.getenv("DB_FILE")
    esp_url = os.getenv("ESP_URL")
    try:
        # get temp and humidity from esp32
        response = requests.get(esp_url, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        print(json_data)

        temperature = json_data['temperature']
        humidity = json_data['humidity']

        # insert into sqlite database
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO climate (temperature, humidity) VALUES (?, ?)',
                (temperature, humidity)
            )
            conn.commit()
    except requests.exceptions.RequestException as error:
        print(f"something went horribly wrong (the server is probably down): {str(error)}")
        return

def insert_historical_weather_data() -> None:
    # create dataframe with temperature data from openmeteo
    df = populate_weather.create_historical_temperature_dataframe()
    # write to sqlite
    populate_weather.write_dataframe_to_sqlite(df)

# scheduler for getting temp/humidity from esp32
esp_scheduler = BackgroundScheduler()
esp_scheduler.add_job(
    id='sqlite_climate_data_inserter',
    func=insert_climate_data,
    trigger='interval',
    seconds=60,
)
esp_scheduler.start()

# another scheduler for like, getting hourly data i guess (using openmeteo)
om_scheduler = BackgroundScheduler()
om_scheduler.add_job(
    id='sqlite_historical_temperature_data_inserter',
    func=insert_historical_weather_data,
    trigger='interval',
    seconds=3550,
    next_run_time=datetime.now()
)
om_scheduler.start()

@app.route('/')
def index():
    conn = get_db_connection()
    climate_info = conn.execute('SELECT * FROM climate ORDER BY timestamp DESC LIMIT 10080').fetchall()
    conn.close()
    return render_template('index.html', climate_info=climate_info)

@app.route('/chart')
def chart():
    conn = get_db_connection()
    climate_info = conn.execute('SELECT * FROM climate ORDER BY timestamp DESC LIMIT 10080').fetchall()
    outside_info = conn.execute('SELECT * FROM outside_weather ORDER BY timestamp DESC LIMIT 10080').fetchall()
    climate_json_data = json.dumps([dict(row) for row in climate_info])
    outside_json_data = json.dumps([dict(row) for row in outside_info])

    conn.close()
    return render_template('chart.html', climate_info=climate_json_data, outside_info=outside_json_data)

def run_app():
    return app

if __name__ == '__main__':
    app.run()