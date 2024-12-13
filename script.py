import requests
import psycopg2
from datetime import datetime

# Paramètres de l'API OpenWeather
API_KEY = "4527fae7a2d505f971ef18e300c969f7"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Villes à scraper
CITIES = ["Dakar", "Thiès"]

# Fonction pour récupérer les données météo
def fetch_weather_data(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "timestamp": datetime.now()
        }
    else:
        print(f"Erreur en récupérant les données pour {city}: {response.status_code}")
        return None

# Fonction pour insérer les données dans PostgreSQL
def insert_into_db(data):
    try:
        connection = psycopg2.connect(
            dbname="meteo_db",
            user="votre_utilisateur",
            password="votre_mot_de_passe",
            host="db"  # Nom du service PostgreSQL dans Docker
        )
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO weather (city, temperature, description, pressure, humidity, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (
            data["city"], data["temperature"], data["description"],
            data["pressure"], data["humidity"], data["timestamp"]
        ))
        connection.commit()
        print(f"Inséré avec succès : {data}")
    except Exception as e:
        print(f"Erreur lors de l'insertion en DB : {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# Exécution principale
if __name__ == "__main__":
    for city in CITIES:
        weather_data = fetch_weather_data(city)
        if weather_data:
            insert_into_db(weather_data)
