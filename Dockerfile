FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code directement dans /app
COPY . .

# Exposer le port 5000 pour Flask
EXPOSE 5000

# Attendre que la base de données soit prête avant l'initialisation
CMD ["sh", "-c", "python app/init-db.py && python app/main.py"]



# FROM python:3.10-slim

# # Définir le répertoire de travail
# WORKDIR /app

# # Installer les dépendances
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copier tout le code directement dans /app
# COPY . .

# # Exposer le port 5000 pour Flask
# EXPOSE 5000

# # Démarrer l'application avec le bon chemin
# CMD ["python", "app/main.py"]

