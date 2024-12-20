import json
import datetime
import psycopg2
from psycopg2 import sql
from datetime import datetime


import requests



def get_city_coordinates(city_name, country_code, api_key):
    """Get the latitude and longitude of a city."""
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name},{country_code}&limit=1&appid={api_key}"
    response = requests.get(geo_url)
    if response.status_code == 200:
        data = response.json()
        if data:
            print("Succes")
            return data[0]['lat'], data[0]['lon']
        else:
            print(f"No data found for {city_name}")
            return None
            
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None




