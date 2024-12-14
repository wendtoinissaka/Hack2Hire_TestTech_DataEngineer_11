from flask import Flask, render_template, jsonify
import os
from datetime import datetime
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Chargement des variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration
API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
CITIES = ["Dakar", "Thiès"]
DATABASE_URL = os.getenv('DATABASE_URL')
# DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://elcapo:elcapo@db/meteo_db')

def create_table():
    """Crée la table weather si elle n'existe pas."""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100) NOT NULL,
            temperature DECIMAL NOT NULL,
            description VARCHAR(200) NOT NULL,
            pressure INTEGER NOT NULL,
            humidity INTEGER NOT NULL,
            timestamp TIMESTAMP NOT NULL
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'weather' créée ou déjà existante")
    except Exception as e:
        print(f"Erreur lors de la création de la table: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

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
    """Récupère et stocke les données météo."""
    print(f"Fetching weather data at {datetime.now()}")
    for city in CITIES:
        data = fetch_weather_data(city)
        if data:
            insert_into_db(data)

# Initialiser le scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_store_weather, trigger="interval", hours=1)  # Exécuter toutes les  heures
# scheduler.add_job(func=fetch_and_store_weather, trigger="interval", minutes=1)  # Exécuter tous les minutes
scheduler.start()

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

@app.route('/api/weather/history/ten')
def get_all_weather_history_ten():
    """Endpoint API pour obtenir les 10 dernières historiques météo de toutes les villes."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT city, temperature, description, pressure, humidity, timestamp
                FROM weather
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            results = cur.fetchall()
            return jsonify([dict(row) for row in results])



if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=5000)
