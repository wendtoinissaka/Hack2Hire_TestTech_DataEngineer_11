import os
import logging
import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
import json
from datetime import datetime, timedelta
from datetime import datetime
from dotenv import load_dotenv
from utils.commons import get_weather_raw_data, load_data_to_postgredb

log = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

DAKAR_LON_LAT = (14.693425, -17.447938)
THIES_LON_LAT = (14.791461, -16.925605)

API_KEY=os.getenv("API_KEY")
DBNAME=os.getenv("DBNAME")
USER=os.getenv("USER")
PASSWORD=os.getenv("PASSWORD")
SERVER=os.getenv("SERVER")

forecast_weather_url = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}&units=metric"

raw_data_file = "raw_forecast_weather_data.json"
processed_data_file = "processed_forecast_weather_data.json"


def extract_forecast_data_from_file(input_file=raw_data_file, output_file=processed_data_file):
    """Extract the desired weather information from a JSON file and save it to another JSON file."""
    try:
        # Load raw data from JSON file
        with open(input_file, "r") as file:
            weather_data_list = json.load(file)  # Charger toutes les entrées comme une liste

        # Résultat pour toutes les entrées
        results = []

        for weather_data in weather_data_list:
            if weather_data.get("city").get("name") == "Keur Issa Bambara":
                city = "Thies"
            else:
                city = "Dakar"

            for forecast in weather_data.get('list'):
                result = {
                    "city": city,
                    "temperature": forecast.get("main").get('temp'),
                    "weather_description": forecast.get("weather")[0].get('description'),
                    "pressure": forecast.get("main").get("pressure"),
                    "humidity": forecast.get('main').get("humidity"),
                    "timestamp": forecast.get("dt_txt")
                }
                results.append(result)

        # Save processed data to JSON file
        with open(output_file, "w") as file:
            json.dump(results, file, indent=4)

        log.info(f"Processed weather data successfully stored in {output_file}")
        # return result
    except FileNotFoundError:
        log.error(f"Input file {input_file} not found.")
        # return None
    except Exception as e:
        log.error(f"Failed to process weather data: {e}")
        # return None


default_arguments = {
    'owner': 'Elie',
    'email': ['adjoboelie@gmail.com'],
    'start_date': datetime(2024, 12, 13),
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

# Définition du DAG
with DAG(
    dag_id='forecast_weather_data_pipeline',
    default_args=default_arguments,
    description='A DAG to fetch and process weather data',
    schedule_interval='0 */8 * * *',  # Toutes les 2 minutes
    catchup=False,
) as dag:

    get_weather_raw_data = PythonOperator(
        task_id="get_weather_raw_data",
        python_callable=get_weather_raw_data,
        op_kwargs={
            "cities": [DAKAR_LON_LAT, THIES_LON_LAT],
            "api_key": API_KEY,
            "url": forecast_weather_url,
            "raw_data_file": raw_data_file
        }
    )

    extract_data_from_file = PythonOperator(
        task_id="extract_forecast_data_from_file",
        python_callable=extract_forecast_data_from_file
    )

    load_data_to_postgredb = PythonOperator(
        task_id="load_data_to_postgredb",
        python_callable=load_data_to_postgredb,
        op_kwargs = {
            "processed_data_file": processed_data_file,
            "table_name": "forecast_weather",
            "USER": USER,
            "PASSWORD": PASSWORD,
            "SERVER": SERVER,
            "DBNAME": DBNAME
        }
    )

    get_weather_raw_data >> extract_data_from_file >> load_data_to_postgredb

