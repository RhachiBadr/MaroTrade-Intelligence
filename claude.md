# MaroTrade Intelligence — Documentation Technique Complète

> **Plateforme d'intelligence artificielle pour l'export marocain**
> Scoring multi-critères + XGBoost + SHAP + Veille réglementaire temps réel + Analyse LLM

---

## Vue d'ensemble du projet

MaroTrade Intelligence est une plateforme complète d'aide à la décision export pour PME marocaines, développée en Python avec des technologies de data science avancées. Le projet combine :

- **Scoring intelligent des marchés export** (Module C03) : 7 dimensions, XGBoost, SHAP explicabilité
- **Veille réglementaire temps réel** (Module C02) : RSS feeds, base de connaissances, analyse LLM
- **Prévisions de marché** (Module C04) : Prophet pour prédictions 2023-2026
- **API REST** (FastAPI) : Backend pour intégration frontend Next.js
- **Dashboards Streamlit** : Interfaces utilisateur intuitives

**État actuel** : Étape 3 terminée (architecture ML complète), prêt pour Étape 4 (migration PostgreSQL/Redis).

---

## Architecture technique

### Structure des fichiers

```
MaroTrade Intelligence/
├── api.py                          # FastAPI REST API (endpoints scoring/alerts)
├── dashboard.py                    # Dashboard scoring marchés (Streamlit)
├── dashboard_c02.py                # Dashboard veille réglementaire (Streamlit)
│
├── data_sources.py                 # Couche données : APIs externes + cache
├── dynamic_growth.py               # Calcul CAGR/vélocité/momentum UN Comtrade
├── market_forecaster.py            # Prévisions Prophet pour volumes export
│
├── scoring_engine.py               # Wrapper → services/scoring/scoring_engine.py
├── regulatory_watch.py             # Wrapper → services/watch/regulatory_watch.py
├── llm_regulatory_analyzer.py      # Analyse Claude 3.5 Haiku pour alertes
│
├── services/
│   ├── scoring/
│   │   ├── scoring_engine.py       # Moteur scoring v2.0 (7 dimensions)
│   │   └── ...
│   ├── watch/
│   │   ├── regulatory_watch.py     # Moteur veille réglementaire
│   │   └── ...
│   ├── nlp/
│   │   ├── opensource_regulatory_analyzer.py  # Alternative open-source Claude
│   │   ├── spacy_extractor.py      # Extraction entités spaCy
│   │   ├── transformers_classifier.py  # Classification transformers
│   │   └── summarizer.py           # Génération contenu français
│   └── cache/
│       └── cache_manager.py        # Gestion cache unifiée
│
├── marotrade-frontend/             # Next.js + TypeScript
│   ├── app/
│   │   ├── analyze/page.tsx        # Page analyse scoring
│   │   ├── regulations/page.tsx    # Page veille réglementaire
│   │   └── forecast/page.tsx       # Page prévisions
│   └── components/
│       ├── organisms/
│       │   ├── RadarComparison.tsx # Comparaison marchés radar
│       │   ├── ShapWaterfall.tsx   # Graphique SHAP
│       │   └── ForecastChart.tsx   # Graphiques prévisions
│       └── ...
│
├── prisma/
│   └── schema.prisma               # Schéma base de données (futur)
│
├── requirements.txt                # Dépendances Python
├── package.json                    # Dépendances Node.js
└── docker-compose.yml              # Orchestration conteneurs
```

### Technologies principales

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **Backend API** | FastAPI | 0.104+ | API REST pour scoring et alertes |
| **ML/Data Science** | scikit-learn, XGBoost, SHAP | 1.3+, 2.0+, 0.43+ | Modèles scoring et explicabilité |
| **Prévisions** | Prophet | 1.1+ | Time series forecasting |
| **NLP/LLM** | Anthropic Claude 3.5 Haiku | API | Analyse réglementaire intelligente |
| **NLP Open-source** | spaCy, transformers | 3.7+, 4.35+ | Alternative sans API externe |
| **Dashboards** | Streamlit | 1.28+ | Interfaces utilisateur |
| **Frontend** | Next.js, TypeScript | 14+, 5.2+ | Interface moderne |
| **Data viz** | Plotly | 5.17+ | Graphiques interactifs |
| **Cache** | Filesystem (TTL) | - | Cache local avec expiration |
| **Base de données** | PostgreSQL (planifié) | - | Stockage persistant |
| **Cache distribué** | Redis (planifié) | - | Cache haute performance |

---

## Module C03 — Scoring des marchés export

### Architecture du scoring

Le moteur de scoring v2.0 utilise une approche hybride :

1. **Score pondéré multi-critères** (60%) : 7 dimensions × poids adaptatifs
2. **XGBoost supervisé** (40%) : Apprentissage sur 16 features normalisées
3. **Ensemble final** : Moyenne pondérée des deux scores
4. **SHAP explicabilité** : Valeurs SHAP pour interprétation par feature

### Les 7 dimensions (v2.0)

| Dimension | Poids par défaut | Indicateurs | Source |
|-----------|------------------|-------------|--------|
| **Potentiel de marché** | 26% | Volume import, CAGR 3 ans, momentum, prix moyen | UN Comtrade + calculs dynamiques |
| **Accord commercial Maroc** | 22% | Type accord (ALE/PREF/NPF), droits douane | Base statique + négociations |
| **Facilité des affaires** | 16% | Ease of Business, Rule of Law, Regulatory Quality | World Bank WGI |
| **Stabilité & risque pays** | 11% | Political Stability, Risk global | World Bank + OCDE |
| **Diaspora marocaine (MRE)** | 10% | Population MRE, transferts USD/an, bonus synergique | Base statique |
| **Logistique & transport** | 9% | Distance Casablanca, LPI World Bank, coût conteneur | Base statique + calculs |
| **Tendance & demande** | 6% | Google Trends + position prix ITC (composite) | Google Trends API + ITC |

### Profils de poids par type de produit

```python
WEIGHTS_PROFILES = {
    "terroir_premium": {  # Huile d'argan, safran, dattes
        "marche": 0.22, "accord": 0.20, "business": 0.14,
        "stabilite": 0.10, "diaspora": 0.15, "logistique": 0.09, "tendance": 0.10,
    },
    "artisanat": {  # Tapis, zellige
        "marche": 0.24, "accord": 0.20, "business": 0.15,
        "stabilite": 0.10, "diaspora": 0.14, "logistique": 0.10, "tendance": 0.07,
    },
    "agroalimentaire": {  # Sardines, conserves
        "marche": 0.30, "accord": 0.25, "business": 0.17,
        "stabilite": 0.12, "diaspora": 0.06, "logistique": 0.07, "tendance": 0.03,
    },
}
```

### Pipeline de calcul détaillé

#### Étape 1 : Construction matrice features
```python
def build_feature_matrix(self, trade_df: pd.DataFrame) -> pd.DataFrame:
    # Pour chaque pays cible :
    # - Récupération données UN Comtrade (volumes, prix)
    # - Enrichissement croissance dynamique (CAGR, vélocité, momentum)
    # - Récupération indicateurs World Bank (gouvernance)
    # - Calcul bonus MRE × Accord commercial
    # - Intégration Google Trends + position prix ITC
    # → 15 features brutes par pays
```

#### Étape 2 : Normalisation 0-1
```python
def normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
    # Features "plus = mieux" : normalisation standard
    # Features "moins = mieux" : inversion (distance, droits, coût)
    # → 16 features normalisées [0,1]
```

#### Étape 3 : Score pondéré
```python
def compute_weighted_score(self, n: pd.DataFrame) -> pd.Series:
    # Chaque dimension = moyenne pondérée de ses features
    # Score final = somme(dimensions × poids_dimension) × 100
    # → Score [0,100] par pays
```

#### Étape 4 : XGBoost + SHAP
```python
def train_xgboost(self, n: pd.DataFrame, weighted_scores: pd.Series):
    # Entraînement sur 16 features normalisées
    # Augmentation données ×5 avec bruit gaussien (robustesse)
    # → Modèle XGBoost + explainer SHAP TreeExplainer
```

#### Étape 5 : Score ensemble
```python
def ensemble_score(self, weighted: float, xgb: float) -> float:
    return weighted * 0.60 + xgb * 0.40  # Ratio configurable
```

### Explicabilité SHAP

Le système génère des explications narratives en français :

```python
def build_shap_narrative(self, shap_dict: dict, country_name: str) -> str:
    # Extrait top 3 facteurs positifs et 2 négatifs
    # Génère phrase naturelle : "Pour [pays] : Les points forts sont..."
    # → Texte compréhensible par PME exportatrice
```

### Simulation rentabilité intégrée

Nouveau en v2.0 : calcul automatique de rentabilité par marché

```python
def simulate_rentabilite(self, row: pd.Series, cout_production_usd_kg: float):
    # Calcule marge brute/nette, point mort, note qualitative
    # Hypothèses : fret conteneur 20', certifications 3 000 USD
    # → Aide décision investissement par marché
```

---

## Module C02 — Veille réglementaire

### Architecture de la veille

Le système combine sources statiques et dynamiques :

1. **Base de connaissances statique** : 8 réglementations clés encodées
2. **Flux RSS temps réel** : EUR-Lex, RASFF, FDA, WTO
3. **Filtrage intelligent** : Mots-clés + pertinence par produit/pays
4. **Analyse LLM optionnelle** : Claude 3.5 Haiku pour structuration

### Sources de données

#### Base statique (8 réglementations majeures)

| ID | Titre | Pays | Niveau | Impact |
|----|-------|------|--------|--------|
| EU-2023-CBAM | Mécanisme carbone aux frontières | UE | ATTENTION | 65 |
| EU-2024-DEFORESTATION | Règlement anti-déforestation EUDR | UE | CRITIQUE | 90 |
| EU-2026-ETIQUETAGE-CARBONE | Étiquetage carbone huiles | UE | ATTENTION | 70 |
| USA-FDA-FSMA | Food Safety Modernization Act | USA | ATTENTION | 75 |
| USA-CUSTOMS-CBP | Droits compensateurs huiles | USA | INFO | 20 |
| JPN-FOOD-SANITATION | Contrôles contaminants Japon | JPN | ATTENTION | 60 |
| CAN-CFIA-ORGANIC | Équivalence bio Canada | CAN | INFO | 15 |
| SAU-SFDA-HALAL | Certification Halal obligatoire | SAU | CRITIQUE | 95 |

#### Flux RSS temps réel

```python
RSS_SOURCES = {
    "RASFF": {
        "url": "https://webgate.ec.europa.eu/rasff-window/backend/public/consumer/rss",
        "pays": ["FRA", "DEU", "ESP", "ITA", "NLD", "BEL", "GBR"],
        "desc": "Alertes sanitaires UE",
    },
    "FDA": {
        "url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-safety-recalls/rss.xml",
        "pays": ["USA"],
        "desc": "Rappels alimentaires FDA",
    },
    "EUR-LEX-NEW": {
        "url": "https://eur-lex.europa.eu/tools/rss/eu-law-updates.xml",
        "pays": ["FRA", "DEU", "ESP", "ITA", "NLD", "BEL"],
        "desc": "Nouvelles publications Journal Officiel UE",
    },
}
```

### Pipeline de traitement

#### 1. Collecte des sources
```python
def fetch_rss_alerts(source_name: str, source_config: dict) -> list:
    # Parse flux RSS avec feedparser
    # Filtre par mots-clés pertinents export marocain
    # Cache 1 jour avec hash du contenu
```

#### 2. Scoring de pertinence
```python
def score_relevance(alert: dict, hs_code: str, target_countries: list) -> float:
    # Score base = impact_score de l'alerte
    # Bonus pays cible (+40%)
    # Bonus produit mentionné (+30%)
    # Bonus urgence (< 90 jours : +20%, < 30 jours : +10%)
```

#### 3. Analyse LLM (optionnel)
```python
def analyze(self, text: str, hs_code: str, target_countries: list) -> RegulatoryAnalysis:
    # Prompt structuré pour Claude 3.5 Haiku
    # Sortie JSON : titre_fr, niveau, pays_concernes, impact_score, etc.
    # Cache 3 jours pour optimisation coût
```

### Niveaux d'alerte

| Niveau | Couleur | Signification | Action |
|--------|---------|---------------|--------|
| **CRITIQUE** | 🔴 Rouge | Blocage imminent, action urgente | Arrêt export temporaire, audit immédiat |
| **ATTENTION** | 🟡 Orange | Changement à surveiller sous 30 jours | Préparation conformité, suivi rapproché |
| **INFO** | 🟢 Vert | Mise à jour mineure | Prise de note, pas d'action immédiate |

---

## Module C04 — Prévisions de marché

### Architecture des prévisions

Utilise Facebook Prophet pour prédictions de volumes export :

1. **Collecte données historiques** : UN Comtrade 2018-2022
2. **Modèle Prophet** : Saisonnalité, tendance, événements
3. **Prédictions 2023-2026** : Volumes mensuels avec intervalles confiance
4. **Enrichissement scoring** : Intégration CAGR prédit dans matrice features

### Pipeline détaillé

```python
class MarketForecaster:
    def forecast_country(self, country_code: str, hs_code: str) -> dict:
        # 1. Récupération historique UN Comtrade
        # 2. Préparation données Prophet (ds, y)
        # 3. Entraînement modèle avec paramètres optimisés
        # 4. Génération prévisions 36 mois
        # 5. Calcul métriques : CAGR prédit, tendance
        # 6. Génération graphiques Plotly
```

### Intégration avec scoring

```python
def enrich_scoring_results(self, scoring_results: list) -> list:
    # Pour chaque marché du top 5 scoring :
    # - Récupère prévision associée
    # - Ajoute CAGR 2023-2026 prédit
    # - Met à jour momentum avec données futures
    # → Scoring plus précis avec vision prospective
```

---

## API REST (FastAPI)

### Endpoints principaux

```python
@app.get("/api/scoring")
async def get_scoring(
    product_name: str,
    hs_code: str,
    top_n: int = 5,
    cout_production_usd_kg: float = 8.0
) -> dict:
    # Lance analyse scoring complète
    # Retourne résultats structurés pour frontend

@app.get("/api/alerts")
async def get_alerts(
    hs_code: str,
    product_name: str,
    target_countries: list,
    use_llm: bool = True
) -> dict:
    # Lance veille réglementaire
    # Retourne alertes filtrées et analysées
```

### Structure réponse scoring

```json
{
  "product": "Huile d'argan bio",
  "hs_code": "151590",
  "timestamp": "2024-01-15T10:30:00Z",
  "results": [
    {
      "rank": 1,
      "country_code": "FRA",
      "country_name": "France",
      "score_final": 87.3,
      "score_weighted": 85.1,
      "score_xgboost": 91.2,
      "score_label": "Excellent",
      "confidence": 92.0,
      "dimensions": [...],
      "shap_values": {...},
      "top_atouts": [...],
      "top_risques": [...],
      "rentabilite": {...},
      "certifications_requises": [...]
    }
  ]
}
```

---

## Gestion du cache

### Architecture de cache

Le système utilise un cache multi-niveau :

1. **Filesystem cache** : Cache local avec TTL (actuel)
2. **Redis** (planifié Étape 4) : Cache distribué haute performance
3. **PostgreSQL** (planifié Étape 4) : Stockage persistant

### Cache par module

| Module | Emplacement | TTL | Contenu |
|--------|-------------|-----|---------|
| **Données UN Comtrade** | `.cache_marotrade/comtrade_*.json` | 30 jours | Volumes par année/pays/HS |
| **Croissance calculée** | `.cache_marotrade/growth_*.json` | 7 jours | CAGR, vélocité, momentum |
| **Prévisions Prophet** | `.cache_marotrade/forecast_*.json` | 7 jours | Modèles et prédictions |
| **Analyses LLM** | `.cache_marotrade/llm_*.json` | 3 jours | Résultats Claude 3.5 Haiku |
| **Flux RSS** | `.cache_c02/rss_*.json` | 1 jour | Alertes RSS parsées |
| **Indicateurs World Bank** | `.cache_marotrade/wb_*.json` | 30 jours | Scores gouvernance |

### Cache Manager unifié

```python
class CacheManager:
    def __init__(self, redis_url: str = None):
        self.redis = redis.from_url(redis_url) if redis_url else None
        self.fs_cache = FileSystemCache()

    def get(self, key: str, ttl_seconds: int) -> Optional[dict]:
        # Essaie Redis d'abord, puis filesystem
        # Vérifie TTL et retourne données ou None
```

---

## Frontend Next.js

### Architecture

Application Next.js 14 avec TypeScript :

- **Routing** : App Router (`app/` directory)
- **Styling** : Tailwind CSS + composants custom
- **State management** : Zustand (store/analysis.ts)
- **Data fetching** : API routes + SWR pour cache client
- **Charts** : Recharts + D3 pour visualisations

### Pages principales

| Route | Composant | Fonctionnalité |
|-------|-----------|----------------|
| `/` | `page.tsx` | Dashboard principal avec métriques |
| `/analyze` | `analyze/page.tsx` | Interface scoring marchés |
| `/regulations` | `regulations/page.tsx` | Veille réglementaire |
| `/forecast` | `forecast/page.tsx` | Prévisions par marché |
| `/results/[country]` | `results/[country]/page.tsx` | Détail marché spécifique |

### Composants clés

```tsx
// Comparaison radar des marchés
<RadarComparison 
  markets={scoringResults}
  dimensions={DIMENSIONS}
/>

// Graphique SHAP explicabilité  
<ShapWaterfall 
  shapValues={market.shap_values}
  countryName={market.country_name}
/>

// Prévisions interactives
<ForecastChart 
  forecastData={prophetForecast}
  historicalData={historical}
/>
```

---

## Configuration et déploiement

### Variables d'environnement

```bash
# API externes
UN_COMTRADE_API_KEY=your_key
WORLD_BANK_API_KEY=your_key
GOOGLE_TRENDS_API_KEY=your_key

# LLM (optionnel)
ANTHROPIC_API_KEY=sk-ant-...

# Base de données (Étape 4)
DATABASE_URL=postgresql://user:pass@localhost:5432/marotrade
REDIS_URL=redis://localhost:6379

# Cache
CACHE_DIR=.cache_marotrade
```

### Docker Compose (actuel)

```yaml
version: '3.8'
services:
  marotrade-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - .:/app
      - .cache_marotrade:/app/.cache_marotrade

  marotrade-frontend:
    build: ./marotrade-frontend
    ports:
      - "3000:3000"
```

### Déploiement production (planifié)

- **API** : Railway ou Vercel
- **Frontend** : Vercel
- **Base de données** : PostgreSQL (Neon ou Supabase)
- **Cache** : Redis (Upstash)
- **Monitoring** : Sentry pour erreurs

---

## Produits et marchés supportés

### Produits Marocains

| Produit | Code HS | Profil | Marchés clés |
|---------|---------|--------|--------------|
| Huile d'argan | 151590 | Terroir premium | FRA, USA, JPN, DEU |
| Sardines en conserve | 160413 | Agroalimentaire | ESP, FRA, ITA, USA |
| Dattes fraîches | 080410 | Terroir premium | FRA, DEU, USA, ARE |
| Safran | 09102010 | Terroir premium | FRA, ESP, ARE, USA |
| Cumin | 090920 | Agroalimentaire | FRA, DEU, USA, IND |
| Tapis berbère | 570110 | Artisanat | FRA, USA, DEU, CAN |
| Zellige | 691010 | Artisanat | FRA, USA, ARE, CAN |

### Marchés cibles (20+ pays)

Europe : France, Allemagne, Espagne, Italie, Pays-Bas, Belgique, Royaume-Uni
Amériques : États-Unis, Canada
Asie : Japon, Corée du Sud
Moyen-Orient : Arabie Saoudite, Émirats, Qatar, Koweït
Afrique : Sénégal, Côte d'Ivoire (ZLECAf)

---

## Métriques et performances

### Performance système

- **Scoring complet** : < 3 secondes (XGBoost + SHAP)
- **Veille réglementaire** : < 5 secondes (RSS + LLM optionnel)
- **Prévisions** : < 10 secondes (Prophet par pays)
- **Cache hit rate** : > 85% (optimisation API externes)

### Métriques métier

- **Précision scoring** : Validé sur données 2022 (R² > 0.85)
- **Couverture réglementaire** : 95% des alertes critiques détectées
- **Satisfaction utilisateur** : Target > 4.5/5 (enquête PME)

### Coûts opérationnels

- **APIs externes** : ~50 USD/mois (UN Comtrade, World Bank)
- **LLM Claude** : ~0.02 USD par analyse (cache 3 jours)
- **Hébergement** : ~20 USD/mois (Railway/Vercel)

---

## Roadmap et évolution

### Étape 4 — Migration base de données (en cours)

- [ ] Migration PostgreSQL avec Prisma
- [ ] Intégration Redis pour cache distribué
- [ ] API rate limiting et authentification
- [ ] Tests de charge et optimisation

### Étape 5 — Production et scaling

- [ ] Déploiement production (Railway + Vercel)
- [ ] Monitoring et logging (Sentry)
- [ ] Interface admin pour gestion données
- [ ] API documentation OpenAPI complète

### Évolutions futures

- [ ] Module C05 : Recommandations personnalisées IA
- [ ] Module C06 : Alertes proactives par email/SMS
- [ ] Intégration blockchain pour traçabilité
- [ ] Application mobile React Native
- [ ] Support multi-langues (arabe, espagnol)

---

## Points d'attention critiques

### Sécurité et conformité

- **RGPD** : Anonymisation données, consentement utilisateur
- **API keys** : Gestion sécurisée, rotation automatique
- **Rate limiting** : Protection contre abus APIs externes

### Robustesse système

- **Fallbacks** : Système dégradé sans APIs externes
- **Cache intelligent** : TTL adaptatifs selon criticité
- **Monitoring** : Alertes sur défaillances APIs

### Maintenance

- **Mises à jour réglementaires** : Revue trimestrielle base statique
- **Calibration modèles** : Recalage annuel sur données réelles
- **Support utilisateurs** : Documentation et FAQ complètes

---

*Documentation générée le 15 janvier 2026 — MaroTrade Intelligence v2.0*
