import openmeteo_requests
import os
import pandas as pd
import requests_cache
from retry_requests import retry
import sqlite3

# this is (mostly) just the example from open-meteo lol
def create_historical_temperature_dataframe() -> pd.DataFrame:
	# setup openmeteo api client w/ cache and retry when it errors
	cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
	retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
	openmeteo = openmeteo_requests.Client(session = retry_session)

	# weather variables
	url = "https://api.open-meteo.com/v1/forecast"
	lat = os.getenv('LATITUDE')
	long = os.getenv('LONGITUDE')
	params = {
		"latitude": lat,
		"longitude": long,
		"hourly": "temperature_2m",
		"timezone": "auto",
		"past_days": 6,
		"forecast_days": 1,
		"temperature_unit": "fahrenheit",
	}
	print(params)
	responses = openmeteo.weather_api(url, params = params)

	# process location
	response = responses[0]
	print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation: {response.Elevation()} m asl")
	print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
	print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

	# hourly data
	hourly = response.Hourly()
	hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

	hourly_data = {
		"timestamp": pd.date_range(
			start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
			end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
			freq = pd.Timedelta(seconds = hourly.Interval()),
			inclusive = "left"
		).tz_convert(response.Timezone().decode())
	}

	hourly_data["temperature"] = hourly_temperature_2m

	df = pd.DataFrame(data = hourly_data)
	# remove timezone stuff so it matches other table (actually maybe i dont need this (wait maybe i do))
	df['timestamp'] = df['timestamp'].dt.tz_localize(None)
	print("\nHourly data\n", df)

	return df

def write_dataframe_to_sqlite(df) -> None:
	# append dataframe to sqlite database
	db_file = os.getenv('DB_FILE')
	conn = sqlite3.connect(db_file)

	df.to_sql(
		name="temp_weather_data",
		con=conn,
		if_exists="replace",
		index=False
	)

	conn.execute("INSERT OR IGNORE INTO outside_weather (timestamp, temperature) SELECT timestamp, temperature FROM temp_weather_data")
	conn.execute("DROP TABLE temp_weather_data")

	conn.commit()
	conn.close()
