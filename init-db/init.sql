-- Création de la table weather
CREATE TABLE IF NOT EXISTS weather (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    temperature DECIMAL NOT NULL,
    description VARCHAR(200) NOT NULL,
    pressure INTEGER NOT NULL,
    humidity INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

-- Création d'un index sur la ville et le timestamp
CREATE INDEX idx_weather_city_timestamp ON weather(city, timestamp);

-- Droits d'accès
GRANT ALL PRIVILEGES ON TABLE weather TO elcapo;
GRANT USAGE, SELECT ON SEQUENCE weather_id_seq TO elcapo;