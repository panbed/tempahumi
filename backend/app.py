import json
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, date, timedelta
from flask import Flask, render_template
from flask_caching import Cache
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import populate_weather

# load environment variables from .env
load_dotenv()

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

CORS(app) # cors handling so frontend can access the backend

# caching for apis so we hopefully dont have to use our disk too much
cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})

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
    
# get climate data from esp32 for one week prior
@app.route('/climate-info/weekly')
@cache.cached(timeout=60)
def climate_info_weekly() -> str:
    # get current date, and date a week prior (7 days) 
    current_date: date = date.today()
    prior_date: date = current_date - timedelta(days=7)
    sql_date: str = f"'{prior_date.strftime('%Y-%m-%d')}' AND '{current_date.strftime('%Y-%m-%d')}'"

    conn = get_db_connection()
    climate_info: list = conn.execute(f"SELECT * FROM climate WHERE DATE(timestamp) BETWEEN {sql_date} ORDER BY timestamp DESC LIMIT 10080").fetchall()
    conn.close()

    climate_json: str = json.dumps([dict(row) for row in climate_info])
    return climate_json

# get the latest <n> num of rows from the db without looking at dates 
# (for example, if the esp32 was off for a while.. theres gonna be no data if we use /weekly)
@app.route('/climate-info/latest')
@cache.cached(timeout=60)
def climate_info_latest() -> str:
    conn = get_db_connection()
    climate_info: list = conn.execute(f"SELECT * FROM climate ORDER BY timestamp DESC LIMIT 10080").fetchall()
    conn.close()

    climate_json: str = json.dumps([dict(row) for row in climate_info])
    return climate_json

def run_app():
    return app

if __name__ == '__main__':
    app.run()