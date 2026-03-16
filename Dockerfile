# Image Python légère
FROM python:3.11-slim

# Dossier de travail dans le container
WORKDIR /app

# Copier les dépendances en premier (optimise le cache Docker)
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source
COPY . .

# Port utilisé par Streamlit
EXPOSE 8501

# Lancer le dashboard Streamlit
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
