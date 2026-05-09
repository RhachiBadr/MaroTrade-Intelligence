# Audit et préparation — Étape 1

## 1. Objectif de l’audit
L’objectif est d’analyser l’architecture existante de MaroTrade Intelligence, d’identifier les points de couplage, les dépendances payantes ou critiques, et de préparer la migration vers une solution plus modulée, scalable et open source.

## 2. Composants clés identifiés

### Backend / Moteurs
- `scoring_engine.py`
  - Moteur de scoring hybride XGBoost + scoring pondéré
  - 7 dimensions, SHAP explicatif, features avancées
  - Fort couplage aux sources de données et aux fonctions métier
- `regulatory_watch.py`
  - Moteur de veille réglementaire basé sur RSS et base statique
  - Filtrage par mots-clés et scoring d’impact
- `llm_regulatory_analyzer.py`
  - Analyse LLM via Claude 3.5 Haiku (Anthropic)
  - Cache local et sortie JSON structurée
- `api.py`
  - API FastAPI exposant `/api/score`, `/api/alerts`, `/api/forecast`
  - Charge `MarketScoringEngine` et `RegulatoryWatchEngine`

### Frontend / Interfaces
- `dashboard.py`
  - Dashboard Streamlit pour scoring marché
  - Interface de visualisation et paramètres utilisateur
- `dashboard_c02.py`
  - Dashboard Streamlit pour veille réglementaire
  - Option Claude 3.5 Haiku activable
- `marotrade-frontend/`
  - Frontend Next.js moderne
  - Composants UI atomiques, pages d’analyse, prévisions, réglementations

### Données et cache
- `data_sources.py` : sources statiques + fallback API
- `dynamic_growth.py` : calcul de croissance et features UN Comtrade
- Cache local : `.cache_marotrade/`, `.cache_c02/`

### Déploiement
- `Dockerfile`, `docker-compose.yml`
- Environnement Python/Streamlit + API FastAPI

## 3. Points de force
- Architecture déjà hybride Backend + Frontend
- Utilisation de ML interprétable (XGBoost + SHAP)
- Présence de dashboards existants (Streamlit) et de frontend Next.js
- Base de données structurée possible via Prisma
- Cache local pour réduire les appels externes

## 4. Problèmes et risques identifiés

### Architecture
- Backend monolithique : logique métier, APIs et dashboards mélangés
- Duplication potentielle entre Streamlit et Next.js
- Service LLM payant dépendant de Claude/Anthropic

### Scalabilité
- Cache local non distribué
- Pas de séparation claire des services métier
- Faible préparation pour scaling horizontal

### MLOps / Data Engineering
- Pas de versioning de modèles ou données
- Pas de pipeline ETL automatisé
- Pas de suivi des modèles ou monitoring ML

### Sécurité / Robustesse
- LLM payant nécessite clé API exposée
- Pas de circuit breaker / retry avancé pour API externes
- Potentiel manque de tests et de validation automatisée

## 5. Priorités de préparation

### 5.1. Imposer la modularisation
- Créer une structure par service : `services/scoring/`, `services/watch/`, `services/nlp/`
- Isoler le code métier de l’UI
- Transformer les fonctions de scoring et de veille en modules réutilisables

### 5.2. Supprimer la dépendance payante
- Remplacer le pipeline Claude par un pipeline NLP open source
- Préparer un service `nlp` avec `transformers`, `spaCy`, `sentence-transformers`

### 5.3. Mettre en place une base solide pour MLOps
- Décider d’un outil de versioning : `MLflow` + `DVC`
- Préparer un pipeline ETL avec `Apache Airflow`
- Prévoir un service de modèle et de monitoring

## 6. Recommandations immédiates

1. Conserver les dashboards existants comme preuve de concept.
2. Prioriser l’extraction du backend métier vers des services modulaires.
3. Rédiger une architecture technique cible simple pour la phase 2.
4. Éliminer progressivement Claude/Anthropic en faveur d’un pipeline open source.
5. Valider l’environnement de déploiement (Docker Compose ou Kubernetes selon capacité).

## 7. Résultat attendu de l’étape 1
- Audit complet de l’architecture actuelle
- Liste des composants et de leurs responsabilités
- Évaluation des risques et des dépendances payantes
- Plan de préparation pour la modularisation et MLOps

---

Fichier généré automatiquement pour formaliser l’étape 1.
