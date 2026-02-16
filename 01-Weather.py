import requests
import os
import json

def get_coordinates():
    with open('coordinates.json', 'r', encoding='utf-8') as f:
        return json.load(f)

coordinates = get_coordinates()  

base_url = 'https://api.openweathermap.org/data/2.5/forecast'
api_key = '36f115b32bd1f55fc152ca1d6beacb1d'

all_forecasts = {}

for place_name, lat_lon_keys in coordinates.items():
    lat = lat_lon_keys['lat']
    lon = lat_lon_keys['lon']

    payload = {'lat': lat, 
              'lon': lon, 
              'APPID': api_key,
              'units': 'metric'
              }

    response = requests.get(base_url, params = payload)

    if response.status_code == 200:
        print(f"Forecast for {place_name}:")
        print(response.json())
        all_forecasts[place_name] = response.json()
    else:
        print(f"Error for {place_name}: {response.status_code} - {response.text}")



with open('weather_forecasts.json', 'w') as json_file:
    json.dump(all_forecasts, json_file, indent=2)

print(f"\nCoordinates saved to weather_forecast.json in {os.getcwd()}")