# ==========================================
# 1. ÉTAPE DE BUILD (Builder Stage)
# ==========================================
FROM python:3.11-slim AS builder

# Empêcher Python de bufferiser les outputs (pratique pour les logs Docker)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Installation des dépendances système nécessaires à la compilation (ex: pour compiler des packages C)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Créer un environnement virtuel pour y installer les paquets (isole les binaires et réduit la taille)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier UNIQUEMENT le fichier de dépendances pour utiliser le système de cache des "layers" Docker
COPY requirements.txt .

# Installation sécurisée et déterministe (sans cache pour réduire le poids temporaire)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# 2. ÉTAPE D'EXÉCUTION (Runtime Stage)
# ==========================================
FROM python:3.11-slim

# Configuration des variables d'environnement restrictives
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Création d'un utilisateur non-root pour réduire la surface d'attaque
# L'UID/GID 10001 est arbitraire pour éviter d'entrer en conflit avec le système hôte
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

WORKDIR /app

# Récupérer l'environnement virtuel pré-compilé depuis l'étape précédente "builder"
COPY --from=builder /opt/venv /opt/venv

# Copier le code local avec les privilèges exclusifs pour le nouvel utilisateur (chown)
COPY --chown=appuser:appgroup . .

# Basculer de "root" vers notre utilisateur sécurisé
USER appuser

# Documenter le port exposé
EXPOSE 8501

# Healthcheck : Surveille si Streamlit répond, sans avoir besoin d'installer cURL
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# Lancer l'application
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
