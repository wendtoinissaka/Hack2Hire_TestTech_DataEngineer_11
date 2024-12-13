from flask import Flask, render_template, jsonify
import os
import requests
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import threading
import time

# Chargement des variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration
API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
CITIES = ["Dakar", "Thiès"]
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Établit une connexion à la base de données."""
    return psycopg2.connect(DATABASE_URL)

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

def insert_into_db(data):
    """Insère les données météo dans la base de données."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            insert_query = """
            INSERT INTO weather (city, temperature, description, pressure, humidity, timestamp)
            VALUES (%(city)s, %(temperature)s, %(description)s, %(pressure)s, %(humidity)s, %(timestamp)s);
            """
            cur.execute(insert_query, data)
            conn.commit()

def fetch_and_store_weather():
    """Fonction pour récupérer et stocker les données météo périodiquement."""
    while True:
        for city in CITIES:
            data = fetch_weather_data(city)
            if data:
                insert_into_db(data)
        time.sleep(1800)  # Attendre 30 minutes avant la prochaine mise à jour

@app.route('/')
def index():
    """Page d'accueil."""
    return render_template('index.html')

@app.route('/api/weather/current')
def get_current_weather():
    """Endpoint API pour obtenir les dernières données météo."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT ON (city)
                    city, temperature, description, pressure, humidity, timestamp
                FROM weather
                ORDER BY city, timestamp DESC
            """)
            results = cur.fetchall()
            return jsonify([dict(row) for row in results])

@app.route('/api/weather/history/<city>')
def get_weather_history(city):
    """Endpoint API pour obtenir l'historique météo d'une ville."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT city, temperature, description, pressure, humidity, timestamp
                FROM weather
                WHERE city = %s
                ORDER BY timestamp DESC
                LIMIT 24
            """, (city,))
            results = cur.fetchall()
            return jsonify([dict(row) for row in results])

@app.route('/api/weather/history/all')
def get_all_weather_history():
    """Endpoint API pour obtenir l'historique météo de toutes les villes."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT city, temperature, description, pressure, humidity, timestamp
                FROM weather
                ORDER BY timestamp DESC
            """)
            results = cur.fetchall()
            return jsonify([dict(row) for row in results])


if __name__ == '__main__':
    # Démarrer le thread de collecte des données en arrière-plan
    weather_thread = threading.Thread(target=fetch_and_store_weather, daemon=True)
    weather_thread.start()
    
    # Démarrer l'application Flask
    app.run(host='0.0.0.0', port=5000)