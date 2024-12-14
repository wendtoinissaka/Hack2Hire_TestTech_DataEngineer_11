import os
from datetime import datetime
import requests
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
CITIES = ["Dakar", "Thiès"]
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://elcapo:elcapo@db/meteo_db')


def get_db_connection():
    """Établit une connexion à la base de données."""
    return psycopg2.connect(DATABASE_URL)


def create_weather_table():
    """Crée la table weather si elle n'existe pas."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS weather (
        id SERIAL PRIMARY KEY,
        city VARCHAR(100) NOT NULL,
        temperature FLOAT NOT NULL,
        description VARCHAR(255),
        pressure INT,
        humidity INT,
        timestamp TIMESTAMP
    );
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(create_table_query)
            conn.commit()
    print("Table 'weather' vérifiée/créée avec succès.")


def fetch_weather_data(city):
    """Récupère les données météo pour une ville."""
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "timestamp": datetime.now()
        }
    except requests.exceptions.RequestException as e:
        print(f"Erreur en récupérant les données pour {city}: {e}")
        return None


def insert_initial_data():
    """Insère les données météo initiales dans la base de données."""
    create_weather_table()  # Créer la table avant d'insérer les données
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for city in CITIES:
                data = fetch_weather_data(city)
                if data:
                    insert_query = """
                    INSERT INTO weather (city, temperature, description, pressure, humidity, timestamp)
                    VALUES (%(city)s, %(temperature)s, %(description)s, %(pressure)s, %(humidity)s, %(timestamp)s);
                    """
                    cur.execute(insert_query, data)
                    conn.commit()
    print("Données initiales insérées avec succès.")


if __name__ == "__main__":
    insert_initial_data()
