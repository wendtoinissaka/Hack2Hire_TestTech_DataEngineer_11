import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration API
API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
CITIES = ["Dakar", "Thiès"]

def get_db_connection():
    """
    Établit une connexion à la base de données en utilisant soit l'URI,
    soit les paramètres individuels.
    """
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Utilisation de l'URI de connexion
        return psycopg2.connect(database_url)
    else:
        # Utilisation des paramètres individuels
        return psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'meteo_db'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )

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
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO weather (city, temperature, description, pressure, humidity, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (
            data["city"],
            data["temperature"],
            data["description"],
            data["pressure"],
            data["humidity"],
            data["timestamp"]
        ))
        connection.commit()
        print(f"Données insérées avec succès pour {data['city']}")
    
    except Exception as e:
        print(f"Erreur lors de l'insertion en DB : {e}")
    finally:
        if connection:
            connection.close()

def check_env_variables():
    """Vérifie la présence des variables d'environnement requises."""
    if not os.getenv('OPENWEATHER_API_KEY'):
        print("Erreur: OPENWEATHER_API_KEY est requise")
        return False
        
    # Vérifie si on a soit l'URI, soit les credentials complets
    has_database_url = bool(os.getenv('DATABASE_URL'))
    has_credentials = all([
        os.getenv('DB_USER'),
        os.getenv('DB_PASSWORD')
    ])
    
    if not (has_database_url or has_credentials):
        print("Erreur: Vous devez fournir soit DATABASE_URL, soit (DB_USER et DB_PASSWORD)")
        return False
        
    return True

def main():
    """Fonction principale."""
    if not check_env_variables():
        return

    create_table()
    
    for city in CITIES:
        weather_data = fetch_weather_data(city)
        if weather_data:
            insert_into_db(weather_data)

if __name__ == "__main__":
    main()