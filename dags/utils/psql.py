import json
import datetime
import psycopg2
from psycopg2 import DatabaseError
from psycopg2 import sql
from datetime import datetime


# Fonction pour créer la table
CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS {} (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    temperature FLOAT,
    weather_description VARCHAR(255),
    pressure INTEGER,
    humidity INTEGER,
    timestamp TIMESTAMP,
    UNIQUE (city, timestamp)
);
"""


def create_table(connection, table_name):
    with connection.cursor() as cursor:
        cursor.execute(CREATE_TABLE_QUERY.format(table_name))
    connection.commit()


def insert_data(connection, data, table_name):
    INSERT_QUERY = f"""
    INSERT INTO {table_name} (city, temperature, weather_description, pressure, humidity, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    try:
        # Transformation du timestamp en datetime
        datetime.strptime(data["timestamp"], '%Y-%m-%d %H:%M:%S')
        # Exécution de la requête
        with connection.cursor() as cursor:
            cursor.execute(
                INSERT_QUERY,
                (
                    data["city"],
                    data["temperature"],
                    data["weather_description"],
                    data["pressure"],
                    data["humidity"],
                    data["timestamp"]  # Déjà converti en datetime
                )
            )
        connection.commit()

    except DatabaseError as db_err:
        # Annuler les changements en cas d'erreur
        connection.rollback()
        raise RuntimeError(f"Erreur lors de l'insertion des données dans la base de données : {db_err}") from db_err

    except KeyError as key_err:
        raise ValueError(f"Données manquantes ou mal formatées : {key_err}") from key_err

    except Exception as e:
        raise RuntimeError(f"Une erreur inattendue s'est produite : {e}") from e


# Fonction pour insérer les données
def insert_data_2(connection, data, table_name):
    INSERT_QUERY = f"""
    INSERT INTO {table_name} (city, temperature, weather_description, pressure, humidity, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (city, timestamp)
    DO UPDATE SET
        temperature = EXCLUDED.temperature,
        weather_description = EXCLUDED.weather_description,
        pressure = EXCLUDED.pressure,
        humidity = EXCLUDED.humidity;
    """
    try:
        # Validation de la clé timestamp
        data["timestamp"] = datetime.strptime(data["timestamp"], '%Y-%m-%d %H:%M:%S')

        # Validation des autres champs
        required_keys = ["city", "temperature", "weather_description", "pressure", "humidity", "timestamp"]
        for key in required_keys:
            if key not in data:
                raise KeyError(f"Clé manquante dans les données : {key}")

        # Exécution de la requête
        with connection.cursor() as cursor:
            cursor.execute(
                INSERT_QUERY,
                (
                    data["city"],
                    data["temperature"],
                    data["weather_description"],
                    data["pressure"],
                    data["humidity"],
                    data["timestamp"]
                )
            )
        connection.commit()

    except DatabaseError as db_err:
        connection.rollback()
        raise RuntimeError(f"Erreur lors de l'insertion/mise à jour dans la base : {db_err}") from db_err

    except KeyError as key_err:
        raise ValueError(f"Données manquantes ou mal formatées : {key_err}") from key_err

    except ValueError as val_err:
        raise RuntimeError(f"Erreur de validation des données : {val_err}") from val_err

    except Exception as e:
        raise RuntimeError(f"Une erreur inattendue s'est produite : {e}") from e