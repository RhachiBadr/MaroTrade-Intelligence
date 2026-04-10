# MaroTrade Intelligence — Documentation Projet

> **Outil d'aide à la décision export pour PME marocaines.**
> Combine scoring multi-critères, XGBoost, veille réglementaire temps réel et analyse LLM (Claude 3.5 Haiku).

---

## 1. Vue d'ensemble

MaroTrade Intelligence est une application Streamlit qui aide les PME marocaines à :

1. **Identifier les meilleurs marchés export** pour un produit donné (scoring C03)
2. **Surveiller la réglementation** applicable à leurs exportations (veille C02)
3. **Enrichir les alertes** via Claude 3.5 Haiku pour une analyse sémantique des textes réglementaires

Deux dashboards Streamlit coexistent :

| Fichier | Rôle |
|---|---|
| `dashboard.py` | Dashboard principal — scoring des marchés (module C03) |
| `dashboard_c02.py` | Dashboard veille réglementaire (module C02) + LLM optionnel |

---

## 2. Architecture des fichiers

```
MaroTrade Intelligence/
├── dashboard.py              # Dashboard scoring marché (C03)
├── dashboard_c02.py          # Dashboard veille réglementaire (C02)
│
├── scoring_engine.py         # Moteur de scoring C03
├── data_sources.py           # Données statiques + accès APIs externes
├── dynamic_growth.py         # Calcul CAGR/vélocité/momentum via UN Comtrade
│
├── regulatory_watch.py       # Moteur de veille réglementaire (C02)
├── llm_regulatory_analyzer.py # Analyse LLM des alertes via Claude 3.5 Haiku
│
├── requirements.txt          # Dépendances Python
├── Dockerfile                # Image Docker
├── docker-compose.yml        # Composition Docker
│
├── .cache_marotrade/         # Cache scoring + LLM (TTL : 7–30 jours)
└── .cache_c02/               # Cache veille réglementaire (TTL : 1 jour)
```

---

## 3. Module C03 — Scoring des marchés export

### 3.1 Fonctionnement

`scoring_engine.py` → classe `MarketScoringEngine`

Pipeline en 7 étapes :
1. Chargement des données commerciales (`data_sources.py`)
2. Construction de la matrice de features (6 dimensions × N pays)
3. Normalisation 0–1
4. Score pondéré multi-critères
5. Entraînement + inférence XGBoost (augmentation données × 5 avec bruit)
6. Calcul SHAP pour l'explicabilité
7. Score ensemble final : **60 % pondéré + 40 % XGBoost**

### 3.2 Les 6 dimensions

| Dimension | Poids | Indicateurs |
|---|---|---|
| Potentiel de marché | 28 % | Volume importé, CAGR, prix moyen |
| Accord commercial Maroc | 22 % | Type accord, droits de douane |
| Facilité des affaires | 18 % | World Bank Ease of Business, Rule of Law |
| Stabilité & risque pays | 12 % | Political Stability, Risk global |
| Diaspora marocaine (MRE) | 10 % | Population MRE, transferts USD/an |
| Logistique & transport | 10 % | Distance Casablanca, LPI, coût conteneur |

### 3.3 Données utilisées

**`data_sources.py`** — base statique avec fallback automatique :
- `ACCORDS_MAROC` — droits préférentiels pour 20+ pays (ALE, PREF, NPF)
- `WORLD_BANK_SCORES` — indicateurs gouvernance World Bank
- `DIASPORA_MRE` — population MRE + transferts par pays
- `LOGISTIQUE` — distance Casablanca + LPI + coût conteneur
- `DEMO_TRADE_DATA` — volumes d'imports par code HS (HS 151590, 160413, 080410)

**API externe (avec fallback)** : UN Comtrade pour les volumes réels.

**`dynamic_growth.py`** — CAGR dynamique :
- Récupère 3 années (2020–2022) via UN Comtrade
- Calcule CAGR, vélocité (accélération) et momentum par pays
- Cache 7 jours dans `.cache_marotrade/`
- Fallback sur `GROWTH_FALLBACK` précalculé pour 7 codes HS

---

## 4. Module C02 — Veille réglementaire

### 4.1 Fonctionnement

`regulatory_watch.py` → classe `RegulatoryWatchEngine`

Sources connectées :
1. **EUR-Lex RSS** — nouvelles publications Journal Officiel UE
2. **RASFF RSS** — alertes sanitaires/alimentaires UE (rappels, rejets)
3. **FDA RSS** — rappels alimentaires USA
4. **Base locale** — réglementations clés encodées en dur (fallback toujours disponible)

La méthode `.run(hs_code, product_name, target_countries)` :
1. Charge la base statique (`REGLEMENTATIONS_BASE`)
2. Récupère les flux RSS en temps réel
3. Filtre par pertinence (mots-clés × code HS × pays cibles)
4. Score chaque alerte (score d'impact + bonus pays + bonus urgence récente)
5. Trie : CRITIQUE → ATTENTION → INFO, puis par score décroissant

### 4.2 Niveaux d'alerte

| Niveau | Couleur | Signification |
|---|---|---|
| `CRITIQUE` | 🔴 Rouge | Blocage imminent, action urgente |
| `ATTENTION` | 🟡 Orange | Changement à surveiller sous 30 jours |
| `INFO` | 🟢 Vert | Mise à jour mineure |

### 4.3 Réglementations encodées en base

Déjà intégrées dans `REGLEMENTATIONS_BASE` :

| ID | Sujet | Pays | Niveau | Score |
|---|---|---|---|---|
| EU-2024-DEFORESTATION | EUDR anti-déforestation | UE | CRITIQUE | 90 |
| SAU-SFDA-HALAL | Certification Halal SFDA | Arabie Saoudite | CRITIQUE | 95 |
| USA-FDA-FSMA | Food Safety Modernization Act | USA | ATTENTION | 75 |
| EU-2026-ETIQUETAGE-CARBONE | Étiquetage empreinte carbone huiles | UE | ATTENTION | 70 |
| EU-2023-CBAM | Mécanisme carbone aux frontières | UE | ATTENTION | 65 |
| JPN-FOOD-SANITATION | Hygiène alimentaire Japon 2024 | Japon | ATTENTION | 60 |
| EU-RASFF-RESIDUS | LMR pesticides révisés | UE | INFO | 55 |
| USA-CUSTOMS-CBP | ALE Maroc-USA, droits 0 % | USA | INFO | 20 |
| CAN-CFIA-ORGANIC | Équivalence bio ONSSA Canada | Canada | INFO | 15 |

---

## 5. Module LLM — Analyse Claude 3.5 Haiku

### 5.1 Fonctionnement

`llm_regulatory_analyzer.py` → classe `LLMRegulatoryAnalyzer`

Quand activé dans `dashboard_c02.py` :
1. Les alertes brutes de `RegulatoryWatchEngine` sont passées à `upgrade_regulatory_watch()`
2. Chaque alerte est analysée par Claude 3.5 Haiku via l'API Anthropic
3. Le LLM retourne un JSON structuré : titre FR, niveau, pays, produits, résumé, action, score
4. Les champs de l'alerte sont remplacés par les données LLM (meilleure qualité)
5. Un **brief exécutif** global est généré pour le dirigeant

### 5.2 Structure de sortie LLM (`RegulatoryAnalysis`)

```python
titre_fr        # Titre reformulé en français clair
niveau          # CRITIQUE / ATTENTION / INFO
pays_concernes  # Codes ISO3 des pays affectés
produits        # Produits ou codes HS concernés
impact_score    # 0–100
resume_fr       # Résumé 2–3 phrases pour PME marocaine
impact_export   # Impact concret sur les exportateurs
action_requise  # Action précise à effectuer
date_vigueur    # Date d'entrée en vigueur (si connue)
confiance       # Score de confiance du LLM (0–1)
```

### 5.3 Optimisations coût

- **Cache 3 jours** dans `.cache_marotrade/llm_*.json` (hash du texte + contexte)
- **Pré-filtre sans LLM** : `_is_relevant()` élimine les alertes clairement hors sujet
- **Modèle économique** : Claude Haiku → ~$0.0000008/token
- Statistiques d'utilisation disponibles via `analyzer.stats`

### 5.4 Configuration

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Ou dans le dashboard via le champ "Clé API Anthropic"
```

---

## 6. Produits et codes HS supportés

| Produit | Code HS | Données complètes |
|---|---|---|
| Huile d'argan | 151590 | Oui (20 pays) |
| Sardines en conserve | 160413 | Oui (15 pays) |
| Dattes fraîches | 080410 | Oui (13 pays) |
| Safran | 09102010 | Croissance (13 pays) |
| Cumin | 090920 | Croissance (17 pays) |
| Tapis berbère | 570110 | Croissance (20 pays) |
| Zellige | 691010 | Croissance (20 pays) |
| Autre (custom) | — | Données génériques |

---

## 7. Accords commerciaux Maroc encodés

| Pays | Accord | Droits | Type |
|---|---|---|---|
| France, Allemagne, Espagne, Italie, Pays-Bas, Belgique | Accord d'association UE | 0 % | ALE |
| États-Unis | Accord de libre-échange | 0 % | ALE |
| Arabie Saoudite, Émirats, Qatar, Koweït, Égypte | GAFTA | 0 % | ALE |
| Royaume-Uni | Accord bilatéral post-Brexit | 2,5 % | PREF |
| Canada | Aucun accord | 6,5 % | NPF |
| Japon | Aucun accord | 3,2 % | NPF |
| Sénégal, Côte d'Ivoire, Nigeria | ZLECAf (en cours) | 3–5 % | PREF |

---

## 8. Lancer l'application

```bash
# Installer les dépendances
pip install -r requirements.txt

# Dashboard scoring marché (C03)
streamlit run dashboard.py

# Dashboard veille réglementaire (C02)
streamlit run dashboard_c02.py

# Avec Docker
docker-compose up
```

### Dépendances principales

```
pandas >= 2.0.0
numpy >= 1.24.0
scikit-learn >= 1.3.0
xgboost >= 2.0.0
shap >= 0.43.0
streamlit >= 1.28.0
plotly >= 5.17.0
requests >= 2.31.0
feedparser          # Pour les flux RSS
anthropic           # Pour Claude 3.5 Haiku (optionnel)
```

> **Note** : `feedparser` et `anthropic` ne sont pas dans `requirements.txt` mais sont nécessaires respectivement pour les flux RSS et le mode LLM. Installer avec : `pip install feedparser anthropic`

---

## 9. Variables d'environnement

| Variable | Rôle | Obligatoire |
|---|---|---|
| `ANTHROPIC_API_KEY` | Clé API pour Claude 3.5 Haiku | Non (mode basique sinon) |

---

## 10. Cache et performances

| Cache | Emplacement | TTL | Contenu |
|---|---|---|---|
| Données RSS | `.cache_c02/rss_*.json` | 1 jour | Flux RSS parsés |
| Données UN Comtrade annuelles | `.cache_marotrade/comtrade_*.json` | 30 jours | Volumes par année |
| Croissance calculée | `.cache_marotrade/growth_*.json` | 7 jours | CAGR, vélocité, momentum |
| Analyses LLM | `.cache_marotrade/llm_*.json` | 3 jours | Résultats Claude Haiku |

---

## 11. Points d'extension courants

- **Ajouter un produit** : étendre `DEMO_TRADE_DATA` dans `data_sources.py` et `GROWTH_FALLBACK` dans `dynamic_growth.py`
- **Ajouter un pays** : étendre `ACCORDS_MAROC`, `WORLD_BANK_SCORES`, `DIASPORA_MRE`, `LOGISTIQUE`
- **Ajouter une réglementation** : ajouter un dict dans `REGLEMENTATIONS_BASE` (regulatory_watch.py)
- **Changer le modèle LLM** : modifier `MODEL = "claude-haiku-4-5"` dans `llm_regulatory_analyzer.py`
