import requests
import logging
import json
import psycopg2
from psycopg2 import sql
from .psql import create_table, insert_data, insert_data_2
log = logging.getLogger(__name__)


def fetch_weather_data(lat, lon, api_key, url):
    """Get the weather data for a given latitude and longitude and save it to a JSON file."""
    weather_url = url.format(lat, lon, api_key)
    try:
        response = requests.get(weather_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        log.info(f"Data fetched for : {lon} et {lat} ")
        return data
    except requests.exceptions.RequestException as e:
        # print(f"Failed to fetch weather data: {e}")
        log.error(f"Failed to fetch {lon} et {lat} weather data: {e}  ")
        return None


def get_weather_raw_data(cities, api_key, url, raw_data_file):
    """Get the data for all the cities"""
    output_file = raw_data_file
    try:
        weather_raw_data = []
        for lon_lat in cities:
            featched_data = fetch_weather_data(lon_lat[0], lon_lat[1], api_key, url)
            if featched_data:
                weather_raw_data.append(featched_data)
            else:
                log.warning("Non data featched")

        with open(output_file, "w") as file:
            json.dump(weather_raw_data, file, indent=4)

        log.info(f"Weather data successfully fetched and stored in {output_file}")
    except IOError as io_err:
        log.error(f"Error saving the file: {io_err}")


def load_data_to_postgredb(processed_data_file, table_name, USER, PASSWORD, SERVER, DBNAME):
    input_file = processed_data_file
    db_url = f"""postgresql://{USER}:{PASSWORD}@{SERVER}/{DBNAME}"""
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(db_url)
        log.info("Connexion établie avec succès !")

        # Création de la table
        create_table(conn, table_name)
        log.info(f"Table {table_name} créée ou déjà existante.")

        weather_data = None

        with open(input_file, "r") as file:
            weather_data = json.load(file)

        # Insertion des données
        if table_name == "current_weather":
            for data in weather_data:
                insert_data(conn, data, table_name)
        else:
            for data in weather_data:
                insert_data_2(conn, data, table_name)
        log.info("Données insérées avec succès !")
        if conn:
            conn.close()
            log.info("Connexion fermée.")
    except Exception as e:
        log.info(f"Une erreur s'est produite : {e}")

