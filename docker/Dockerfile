# ███████████████████████████████████████████████████████████████
# MaroTrade Intelligence — Dockerfile Multi-stage Optimisé
# ███████████████████████████████████████████████████████████████
# Image Python 3.11 slim pour réduire la taille (~150MB vs 900MB)
# Multi-stage build pour isoler compilation et runtime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1️⃣ STAGE BUILD — Compilation des dépendances
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FROM python:3.11-slim AS builder

LABEL stage=builder

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Installer uniquement les dépendances de build (build-essential, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer un venv isolé pour les paquets compilés
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier requirements et installer (layers en cache Docker)
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2️⃣ STAGE RUNTIME — Image finale optimisée
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FROM python:3.11-slim

LABEL maintainer="MaroTrade <contact@marotrade.ma>" \
      version="2.0" \
      description="Tool for export market analysis - Moroccan SMEs"

# Variables d'environnement Python restrictives
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    TZ=Africa/Casablanca

WORKDIR /app

# Installer runtime dependencies (libpq pour PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Créer utilisateur non-root pour des raisons de sécurité
# UID/GID 10001 + evite les conflits avec le système hôte
RUN groupadd -g 10001 -r appgroup && \
    useradd -u 10001 -r -g appgroup -s /bin/bash -m appuser

# Copier venv compilé depuis builder stage
COPY --from=builder --chown=appuser:appgroup /opt/venv /opt/venv

# Copier le code application
COPY --chown=appuser:appgroup . .

# Basculer vers utilisateur non-root
USER appuser

# Exposer les ports
EXPOSE 8501 8000

# Healthcheck pour supervision Docker
# Test : Streamlit health endpoint (plus robuste que curl)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request, sys; \
try: \
    urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=5); sys.exit(0) \
except: \
    sys.exit(1)" || exit 1

# Commande de démarrage : Streamlit + options optimisées
CMD [\
    "streamlit", "run", \
    "dashboard.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.maxUploadSize=200", \
    "--logger.level=info", \
    "--client.showErrorDetails=false" \
]
