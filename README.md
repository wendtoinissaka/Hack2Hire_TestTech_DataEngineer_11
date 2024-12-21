
# 🌤️ Weather Data Pipeline avec Apache Airflow 🚀


## 📝 Description du Projet


Ce projet est une solution d'automatisation de pipeline de données météorologiques utilisant Apache Airflow pour orchestrer et automatiser la récupération, la transformation (selection des caractéristiques souhaiter) et le chargement (ETL) des données météo des villes de Dakatr et de Saint-Louis. Les données sont récupérées via l'API [OpenWeatherMap](https://openweathermap.org/) 🌍. La version gratuite de l'API permet de d'avoir les données de la [météo courante](https://openweathermap.org/current#one) et d'avoir des previsions météo pour les [5 prochains jours](https://openweathermap.org/forecast5#data). Les données obtenus a la fin du processus sont stockées dans une base de données PostgreSQL gratuite et dsponible sur [Render.com](https://render.com/).

L'objectif final est de créer des dashboards interactifs avec Power BI 📊 pour suivre et analyser l'évolution de la température et d'autres indicateurs météorologiques.


---


## 🚀 Fonctionnalités Principales

🔄 Récupération Automatisée des Données : Utilisation de DAGS (Directed Acyclic Graphs) pour orchestrer l'extraction de données météorologiques en temps réel ou en différé.

🧹 Transformation des Données : Filtrage et extraction des informations clés (nom de la ville, température, description météo, pression, humidité, timestamp).

📤 Chargement dans PostgreSQL : Insertion des données transformées dans une base de données PostgreSQL distante.

📊 Visualisation avec Power BI : Création de tableaux de bord pour suivre et analyser les données météorologiques.

🗂️ Gestion des Fichiers Intermédiaires : Les données brutes et transformées sont enregistrées sous format JSON entre les différentes étapes du pipeline.


---


## ⚙️ Technologies Utilisées

🌀 Orchestration : Apache Airflow

🌍 API Météo : OpenWeatherMap (version gratuite)

🗄️ Base de Données : PostgreSQL (instance gratuite sur Render.com)

📊 Visualisation : Power BI

🗂️ Stockage Intermédiaire : JSON

🐳 Conteneurisation : Docker


---


## 🏗️ Architecture du Pipeline

Notre système est representé par le schéma suivant 

![image](https://github.com/user-attachments/assets/5d37537f-d726-4275-97cb-2242c04db985)






---



## 🔄 Déroulement du Pipeline ETL


1. 🌐 Récupération des Données (Phase 1)

Un DAG Airflow exécute des requêtes vers l'API OpenWeatherMap pour récupérer les données météorologiques.

Les données brutes sont enregistrées au format JSON.

2. 🧪 Transformation des Données (Phase 2)

Un second DAG prend les données JSON et applique des transformations pour extraire uniquement les champs pertinents (nom de la ville, température, description météo, pression, humidité, timestamp).

Ces données sont également enregistrées en JSON avant d'être chargées.

3. 📤 Chargement dans PostgreSQL (Phase 3)

Les données transformées sont lues depuis le fichier json puis sont insérées dans une base de données PostgreSQL distante.

Airflow permet de gerer la connexion et l'insertion des données de manière automatisée.

4. 📊 Visualisation avec Power BI

Les données présentes dans PostgreSQL sont exploitées pour créer des visualisations et dashboards interactifs.

Ci-dessous les differents dashboards réalisés : 



1. Prévision météo pour la région de Dakar :

![image](https://github.com/user-attachments/assets/cf269fc6-5e1f-4267-9993-2cd08bd62024)


2. Prévision météo pour la région de Thiès :

![image](https://github.com/user-attachments/assets/b62e6469-eace-47d2-a7e4-62fa3de29088)




---


# ✅ Pré-requis


- Python 3.10 ou plus

- 🌀 Apache Airflow installé et configuré.
 
- 🐳 Docker installé.

- Accès à l'API OpenWeatherMap (Clé API requise).

- PostgreSQL (hébergé ou local avec accès distant configuré).

- Power BI pour les dashboards.


---


## 🛠️ Installation et Configuration


1. 📥 Clonez le Référentiel

            git clone https://github.com/wendtoinissaka/Hack2Hire_TestTech_DataEngineer_11.git
            cd  Hack2Hire_TestTech_DataEngineer_11


2. 🐳 Lancer avec Docker Compose

Un fichier docker-compose.yml est disponible à la racine du projet. Pour lancer l'application avec Airflow et PostgreSQL :

      docker-compose up -d

Acceder a l'interface

      http://localhost:8080

Les identifiants sont "Airflow" pour le login et "Airflow pour le password.


---


## 🔧 Utilisation

- Déclenchez le DAG pour récupérer les données de l'API.

- Laissez Airflow exécuter les transformations automatiques.

- Consultez la base de données PostgreSQL pour vérifier l'ingestion des données.

- Verifier les logs en cas de problemes

- Créez des dashboards sur Power BI connectés à la base PostgreSQL.


---


## 👤👤 Auteurs


1. **[Wendtoin Issaka OUEDRAOGO](#)**  ------------------>  [CV](cv/cv_issaka.pdf)  

2. **[Mafoya Elie Abissola ADJOBO](#)**  ------------------->  [CV](cv/CV%20Elie%20Adjobo.pdf)


---

## Documentation

Ressource officiel d'[Apache airflow pour l'utilisation avec Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)

Video youtube expliquant l'[installation d'airflow avec Docker](https://www.youtube.com/watch?v=Sva8rDtlWi4)

