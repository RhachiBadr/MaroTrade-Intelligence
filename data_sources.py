"""
data_sources.py — Couche de données du moteur de scoring C03
Gère toutes les sources externes avec fallback sur données réalistes intégrées.
"""

import requests
import pandas as pd
import numpy as np


# ═══════════════════════════════════════════════════════════════
# BASE DE CONNAISSANCES STATIQUE
# Données réalistes encodées (utilisées si les APIs sont indisponibles)
# ═══════════════════════════════════════════════════════════════

# Accords commerciaux Maroc — taux de droits préférentiels (%)
ACCORDS_MAROC = {
    # Union Européenne — Accord d'association
    "FRA": {"accord": "Accord d'association UE",        "droits": 0.0,  "type": "ALE"},
    "DEU": {"accord": "Accord d'association UE",        "droits": 0.0,  "type": "ALE"},
    "ESP": {"accord": "Accord d'association UE",        "droits": 0.0,  "type": "ALE"},
    "ITA": {"accord": "Accord d'association UE",        "droits": 0.0,  "type": "ALE"},
    "NLD": {"accord": "Accord d'association UE",        "droits": 0.0,  "type": "ALE"},
    "BEL": {"accord": "Accord d'association UE",        "droits": 0.0,  "type": "ALE"},
    "GBR": {"accord": "Accord bilatéral post-Brexit",   "droits": 2.5,  "type": "PREF"},
    # Amérique du Nord
    "USA": {"accord": "Accord de libre-échange",        "droits": 0.0,  "type": "ALE"},
    "CAN": {"accord": "Aucun accord préférentiel",      "droits": 6.5,  "type": "NPF"},
    # Pays arabes — GAFTA
    "SAU": {"accord": "Zone arabe libre-échange GAFTA", "droits": 0.0,  "type": "ALE"},
    "ARE": {"accord": "Zone arabe libre-échange GAFTA", "droits": 0.0,  "type": "ALE"},
    "EGY": {"accord": "Zone arabe libre-échange GAFTA", "droits": 0.0,  "type": "ALE"},
    "QAT": {"accord": "Zone arabe libre-échange GAFTA", "droits": 0.0,  "type": "ALE"},
    "KWT": {"accord": "Zone arabe libre-échange GAFTA", "droits": 0.0,  "type": "ALE"},
    # Afrique — Zone de libre-échange continentale africaine (ZLECAf)
    "SEN": {"accord": "ZLECAf (en cours)",              "droits": 3.0,  "type": "PREF"},
    "CIV": {"accord": "ZLECAf (en cours)",              "droits": 3.0,  "type": "PREF"},
    "NGA": {"accord": "ZLECAf (en cours)",              "droits": 5.0,  "type": "PREF"},
    # Asie — pas d'accord
    "JPN": {"accord": "Aucun accord préférentiel",      "droits": 3.2,  "type": "NPF"},
    "CHN": {"accord": "Aucun accord préférentiel",      "droits": 7.5,  "type": "NPF"},
    "KOR": {"accord": "Aucun accord préférentiel",      "droits": 8.0,  "type": "NPF"},
    "SGP": {"accord": "Aucun accord préférentiel",      "droits": 0.0,  "type": "NPF"},  # Singapore = 0% MFN
}

# Indicateurs World Bank — Ease of Doing Business & Governance (score 0–100)
WORLD_BANK_SCORES = {
    "FRA": {"ease_business": 76.8, "political_stability": 55.2, "rule_of_law": 86.0, "regulatory_quality": 87.3},
    "DEU": {"ease_business": 79.7, "political_stability": 68.1, "rule_of_law": 91.5, "regulatory_quality": 92.0},
    "ESP": {"ease_business": 77.9, "political_stability": 52.3, "rule_of_law": 79.6, "regulatory_quality": 80.1},
    "ITA": {"ease_business": 72.9, "political_stability": 50.1, "rule_of_law": 71.3, "regulatory_quality": 74.2},
    "NLD": {"ease_business": 82.4, "political_stability": 72.3, "rule_of_law": 95.2, "regulatory_quality": 95.6},
    "BEL": {"ease_business": 75.0, "political_stability": 53.8, "rule_of_law": 87.0, "regulatory_quality": 86.4},
    "GBR": {"ease_business": 83.5, "political_stability": 54.3, "rule_of_law": 92.3, "regulatory_quality": 94.1},
    "USA": {"ease_business": 84.0, "political_stability": 48.6, "rule_of_law": 90.1, "regulatory_quality": 89.9},
    "CAN": {"ease_business": 79.6, "political_stability": 80.2, "rule_of_law": 93.8, "regulatory_quality": 94.5},
    "SAU": {"ease_business": 71.6, "political_stability": 32.5, "rule_of_law": 55.2, "regulatory_quality": 57.0},
    "ARE": {"ease_business": 80.9, "political_stability": 56.1, "rule_of_law": 68.3, "regulatory_quality": 73.5},
    "EGY": {"ease_business": 60.1, "political_stability": 22.1, "rule_of_law": 39.4, "regulatory_quality": 41.2},
    "QAT": {"ease_business": 68.4, "political_stability": 65.3, "rule_of_law": 62.1, "regulatory_quality": 64.0},
    "JPN": {"ease_business": 78.0, "political_stability": 80.5, "rule_of_law": 89.4, "regulatory_quality": 88.7},
    "CHN": {"ease_business": 77.9, "political_stability": 28.3, "rule_of_law": 44.7, "regulatory_quality": 45.8},
    "KOR": {"ease_business": 84.0, "political_stability": 52.9, "rule_of_law": 83.0, "regulatory_quality": 82.4},
    "SGP": {"ease_business": 89.0, "political_stability": 89.2, "rule_of_law": 95.5, "regulatory_quality": 97.0},
    "SEN": {"ease_business": 59.3, "political_stability": 48.6, "rule_of_law": 52.1, "regulatory_quality": 50.3},
    "CIV": {"ease_business": 60.0, "political_stability": 32.1, "rule_of_law": 35.4, "regulatory_quality": 40.0},
    "NGA": {"ease_business": 56.9, "political_stability": 8.2,  "rule_of_law": 18.3, "regulatory_quality": 22.4},
    "KWT": {"ease_business": 67.9, "political_stability": 45.6, "rule_of_law": 58.2, "regulatory_quality": 54.3},
}

# Diaspora marocaine (MRE) — estimation population et transferts (M USD/an)
DIASPORA_MRE = {
    "FRA": {"population": 1_200_000, "transferts_musd": 2_100},
    "ESP": {"population":   750_000, "transferts_musd":   950},
    "ITA": {"population":   250_000, "transferts_musd":   380},
    "BEL": {"population":   200_000, "transferts_musd":   290},
    "NLD": {"population":   150_000, "transferts_musd":   210},
    "DEU": {"population":   120_000, "transferts_musd":   180},
    "GBR": {"population":    60_000, "transferts_musd":    95},
    "USA": {"population":   100_000, "transferts_musd":   420},
    "CAN": {"population":    80_000, "transferts_musd":   310},
    "SAU": {"population":    50_000, "transferts_musd":   180},
    "ARE": {"population":    45_000, "transferts_musd":   165},
    "QAT": {"population":    12_000, "transferts_musd":    55},
    "JPN": {"population":     2_000, "transferts_musd":     8},
    "CHN": {"population":     1_500, "transferts_musd":     5},
    "KOR": {"population":       800, "transferts_musd":     3},
}

# Logistique — distance km depuis Casablanca + Logistics Performance Index World Bank (0–5)
LOGISTIQUE = {
    "FRA": {"distance_km": 2_100,  "lpi": 3.84, "cout_conteneur_usd": 1_200},
    "ESP": {"distance_km":   700,  "lpi": 3.83, "cout_conteneur_usd":   800},
    "ITA": {"distance_km": 2_400,  "lpi": 3.76, "cout_conteneur_usd": 1_300},
    "NLD": {"distance_km": 2_800,  "lpi": 4.02, "cout_conteneur_usd": 1_400},
    "BEL": {"distance_km": 2_600,  "lpi": 3.95, "cout_conteneur_usd": 1_350},
    "DEU": {"distance_km": 3_100,  "lpi": 4.20, "cout_conteneur_usd": 1_500},
    "GBR": {"distance_km": 2_500,  "lpi": 3.99, "cout_conteneur_usd": 1_450},
    "USA": {"distance_km": 7_500,  "lpi": 3.89, "cout_conteneur_usd": 2_800},
    "CAN": {"distance_km": 8_200,  "lpi": 3.73, "cout_conteneur_usd": 3_100},
    "SAU": {"distance_km": 6_500,  "lpi": 3.16, "cout_conteneur_usd": 2_200},
    "ARE": {"distance_km": 6_800,  "lpi": 3.92, "cout_conteneur_usd": 2_400},
    "EGY": {"distance_km": 3_500,  "lpi": 2.82, "cout_conteneur_usd": 1_600},
    "QAT": {"distance_km": 6_900,  "lpi": 3.32, "cout_conteneur_usd": 2_500},
    "JPN": {"distance_km":14_000,  "lpi": 4.03, "cout_conteneur_usd": 4_500},
    "CHN": {"distance_km":12_000,  "lpi": 3.61, "cout_conteneur_usd": 4_000},
    "KOR": {"distance_km":12_500,  "lpi": 3.59, "cout_conteneur_usd": 4_200},
    "SGP": {"distance_km":12_800,  "lpi": 4.00, "cout_conteneur_usd": 4_100},
    "SEN": {"distance_km": 2_800,  "lpi": 2.51, "cout_conteneur_usd": 1_800},
    "CIV": {"distance_km": 4_200,  "lpi": 2.58, "cout_conteneur_usd": 2_100},
    "NGA": {"distance_km": 5_400,  "lpi": 2.53, "cout_conteneur_usd": 2_600},
    "KWT": {"distance_km": 6_600,  "lpi": 3.04, "cout_conteneur_usd": 2_300},
}

# Données commerciales de démonstration par code HS (volumes imports mondiaux réalistes)
DEMO_TRADE_DATA = {
    "151590": [  # Huile d'argan et huiles végétales similaires
        {"country_code": "USA", "country_name": "États-Unis",     "value_usd": 24_200_000, "weight_kg": 780_000, "growth_pct": 15.4, "price_usd_kg": 31.0},
        {"country_code": "FRA", "country_name": "France",          "value_usd": 18_500_000, "weight_kg": 620_000, "growth_pct":  8.2, "price_usd_kg": 29.8},
        {"country_code": "DEU", "country_name": "Allemagne",       "value_usd": 11_300_000, "weight_kg": 370_000, "growth_pct":  6.1, "price_usd_kg": 30.5},
        {"country_code": "GBR", "country_name": "Royaume-Uni",     "value_usd":  9_800_000, "weight_kg": 310_000, "growth_pct":  4.8, "price_usd_kg": 31.6},
        {"country_code": "JPN", "country_name": "Japon",           "value_usd":  7_600_000, "weight_kg": 190_000, "growth_pct": 22.1, "price_usd_kg": 40.0},
        {"country_code": "CAN", "country_name": "Canada",          "value_usd":  6_400_000, "weight_kg": 210_000, "growth_pct": 11.3, "price_usd_kg": 30.5},
        {"country_code": "NLD", "country_name": "Pays-Bas",        "value_usd":  5_900_000, "weight_kg": 195_000, "growth_pct":  7.2, "price_usd_kg": 30.3},
        {"country_code": "SAU", "country_name": "Arabie Saoudite", "value_usd":  5_200_000, "weight_kg": 180_000, "growth_pct":  9.7, "price_usd_kg": 28.9},
        {"country_code": "ARE", "country_name": "Émirats Arabes",  "value_usd":  4_800_000, "weight_kg": 155_000, "growth_pct": 12.5, "price_usd_kg": 31.0},
        {"country_code": "ESP", "country_name": "Espagne",         "value_usd":  4_100_000, "weight_kg": 145_000, "growth_pct":  3.2, "price_usd_kg": 28.3},
        {"country_code": "CHN", "country_name": "Chine",           "value_usd":  3_900_000, "weight_kg": 130_000, "growth_pct": 18.9, "price_usd_kg": 30.0},
        {"country_code": "ITA", "country_name": "Italie",          "value_usd":  3_700_000, "weight_kg": 125_000, "growth_pct":  5.0, "price_usd_kg": 29.6},
        {"country_code": "BEL", "country_name": "Belgique",        "value_usd":  2_800_000, "weight_kg":  95_000, "growth_pct":  6.8, "price_usd_kg": 29.5},
        {"country_code": "KOR", "country_name": "Corée du Sud",    "value_usd":  2_600_000, "weight_kg":  80_000, "growth_pct": 14.2, "price_usd_kg": 32.5},
        {"country_code": "SGP", "country_name": "Singapour",       "value_usd":  1_900_000, "weight_kg":  58_000, "growth_pct": 10.8, "price_usd_kg": 32.8},
        {"country_code": "QAT", "country_name": "Qatar",           "value_usd":  1_700_000, "weight_kg":  57_000, "growth_pct":  8.5, "price_usd_kg": 29.8},
        {"country_code": "KWT", "country_name": "Koweït",          "value_usd":  1_400_000, "weight_kg":  48_000, "growth_pct":  7.3, "price_usd_kg": 29.2},
        {"country_code": "SEN", "country_name": "Sénégal",         "value_usd":    800_000, "weight_kg":  30_000, "growth_pct": 12.0, "price_usd_kg": 26.7},
        {"country_code": "CIV", "country_name": "Côte d'Ivoire",   "value_usd":    600_000, "weight_kg":  23_000, "growth_pct":  9.0, "price_usd_kg": 26.1},
        {"country_code": "NGA", "country_name": "Nigeria",         "value_usd":    400_000, "weight_kg":  16_000, "growth_pct":  6.5, "price_usd_kg": 25.0},
    ],
    "160413": [  # Sardines en conserve
        {"country_code": "ESP", "country_name": "Espagne",         "value_usd": 85_000_000, "weight_kg": 42_000_000, "growth_pct":  2.1, "price_usd_kg": 2.02},
        {"country_code": "FRA", "country_name": "France",          "value_usd": 62_000_000, "weight_kg": 30_000_000, "growth_pct":  1.8, "price_usd_kg": 2.07},
        {"country_code": "ITA", "country_name": "Italie",          "value_usd": 35_000_000, "weight_kg": 17_000_000, "growth_pct":  3.2, "price_usd_kg": 2.06},
        {"country_code": "GBR", "country_name": "Royaume-Uni",     "value_usd": 28_000_000, "weight_kg": 14_000_000, "growth_pct":  2.5, "price_usd_kg": 2.00},
        {"country_code": "USA", "country_name": "États-Unis",      "value_usd": 22_000_000, "weight_kg": 10_500_000, "growth_pct":  4.1, "price_usd_kg": 2.10},
        {"country_code": "DEU", "country_name": "Allemagne",       "value_usd": 18_000_000, "weight_kg":  9_000_000, "growth_pct":  1.5, "price_usd_kg": 2.00},
        {"country_code": "SAU", "country_name": "Arabie Saoudite", "value_usd": 12_000_000, "weight_kg":  6_000_000, "growth_pct":  5.3, "price_usd_kg": 2.00},
        {"country_code": "ARE", "country_name": "Émirats Arabes",  "value_usd":  9_500_000, "weight_kg":  4_700_000, "growth_pct":  6.1, "price_usd_kg": 2.02},
        {"country_code": "CAN", "country_name": "Canada",          "value_usd":  7_200_000, "weight_kg":  3_500_000, "growth_pct":  2.8, "price_usd_kg": 2.06},
        {"country_code": "NGA", "country_name": "Nigeria",         "value_usd":  6_800_000, "weight_kg":  3_400_000, "growth_pct":  8.9, "price_usd_kg": 2.00},
        {"country_code": "SEN", "country_name": "Sénégal",         "value_usd":  4_200_000, "weight_kg":  2_100_000, "growth_pct":  7.5, "price_usd_kg": 2.00},
        {"country_code": "CIV", "country_name": "Côte d'Ivoire",   "value_usd":  3_900_000, "weight_kg":  1_950_000, "growth_pct":  6.8, "price_usd_kg": 2.00},
        {"country_code": "EGY", "country_name": "Égypte",          "value_usd":  3_500_000, "weight_kg":  1_750_000, "growth_pct":  4.2, "price_usd_kg": 2.00},
        {"country_code": "JPN", "country_name": "Japon",           "value_usd":  3_200_000, "weight_kg":  1_500_000, "growth_pct":  3.1, "price_usd_kg": 2.13},
        {"country_code": "CHN", "country_name": "Chine",           "value_usd":  2_800_000, "weight_kg":  1_400_000, "growth_pct":  5.5, "price_usd_kg": 2.00},
    ],
    "080410": [  # Dattes fraîches
        {"country_code": "FRA", "country_name": "France",          "value_usd": 42_000_000, "weight_kg": 18_000_000, "growth_pct":  5.1, "price_usd_kg": 2.33},
        {"country_code": "DEU", "country_name": "Allemagne",       "value_usd": 31_000_000, "weight_kg": 13_000_000, "growth_pct":  4.2, "price_usd_kg": 2.38},
        {"country_code": "GBR", "country_name": "Royaume-Uni",     "value_usd": 22_000_000, "weight_kg":  9_200_000, "growth_pct":  3.8, "price_usd_kg": 2.39},
        {"country_code": "USA", "country_name": "États-Unis",      "value_usd": 19_000_000, "weight_kg":  7_800_000, "growth_pct":  7.3, "price_usd_kg": 2.44},
        {"country_code": "BEL", "country_name": "Belgique",        "value_usd": 14_000_000, "weight_kg":  5_900_000, "growth_pct":  4.5, "price_usd_kg": 2.37},
        {"country_code": "NLD", "country_name": "Pays-Bas",        "value_usd": 12_000_000, "weight_kg":  5_000_000, "growth_pct":  5.0, "price_usd_kg": 2.40},
        {"country_code": "CAN", "country_name": "Canada",          "value_usd":  9_500_000, "weight_kg":  3_900_000, "growth_pct":  6.1, "price_usd_kg": 2.44},
        {"country_code": "SAU", "country_name": "Arabie Saoudite", "value_usd":  8_200_000, "weight_kg":  3_500_000, "growth_pct":  3.2, "price_usd_kg": 2.34},
        {"country_code": "ARE", "country_name": "Émirats Arabes",  "value_usd":  6_800_000, "weight_kg":  2_900_000, "growth_pct":  4.8, "price_usd_kg": 2.34},
        {"country_code": "SGP", "country_name": "Singapour",       "value_usd":  3_100_000, "weight_kg":  1_200_000, "growth_pct":  9.2, "price_usd_kg": 2.58},
        {"country_code": "JPN", "country_name": "Japon",           "value_usd":  2_800_000, "weight_kg":  1_050_000, "growth_pct":  6.8, "price_usd_kg": 2.67},
        {"country_code": "AUS", "country_name": "Australie",       "value_usd":  2_400_000, "weight_kg":    980_000, "growth_pct":  7.5, "price_usd_kg": 2.45},
        {"country_code": "KOR", "country_name": "Corée du Sud",    "value_usd":  1_900_000, "weight_kg":    750_000, "growth_pct": 11.2, "price_usd_kg": 2.53},
    ],
}

# Ajouter un fallback générique
_DEFAULT_TRADE = [
    {"country_code": "FRA", "country_name": "France",          "value_usd": 15_000_000, "weight_kg": 5_000_000, "growth_pct": 5.0, "price_usd_kg": 3.0},
    {"country_code": "USA", "country_name": "États-Unis",      "value_usd": 20_000_000, "weight_kg": 6_500_000, "growth_pct": 7.5, "price_usd_kg": 3.1},
    {"country_code": "DEU", "country_name": "Allemagne",       "value_usd": 10_000_000, "weight_kg": 3_300_000, "growth_pct": 4.0, "price_usd_kg": 3.0},
    {"country_code": "GBR", "country_name": "Royaume-Uni",     "value_usd":  8_500_000, "weight_kg": 2_800_000, "growth_pct": 3.5, "price_usd_kg": 3.0},
    {"country_code": "ESP", "country_name": "Espagne",         "value_usd":  6_000_000, "weight_kg": 2_100_000, "growth_pct": 3.0, "price_usd_kg": 2.9},
    {"country_code": "SAU", "country_name": "Arabie Saoudite", "value_usd":  5_000_000, "weight_kg": 1_750_000, "growth_pct": 6.0, "price_usd_kg": 2.9},
    {"country_code": "ARE", "country_name": "Émirats Arabes",  "value_usd":  4_500_000, "weight_kg": 1_500_000, "growth_pct": 7.0, "price_usd_kg": 3.0},
    {"country_code": "NLD", "country_name": "Pays-Bas",        "value_usd":  4_000_000, "weight_kg": 1_300_000, "growth_pct": 4.5, "price_usd_kg": 3.1},
    {"country_code": "ITA", "country_name": "Italie",          "value_usd":  3_800_000, "weight_kg": 1_300_000, "growth_pct": 3.8, "price_usd_kg": 2.9},
    {"country_code": "JPN", "country_name": "Japon",           "value_usd":  3_500_000, "weight_kg": 1_100_000, "growth_pct": 9.0, "price_usd_kg": 3.2},
    {"country_code": "CAN", "country_name": "Canada",          "value_usd":  3_200_000, "weight_kg": 1_050_000, "growth_pct": 5.5, "price_usd_kg": 3.0},
    {"country_code": "CHN", "country_name": "Chine",           "value_usd":  3_000_000, "weight_kg": 1_000_000, "growth_pct":10.0, "price_usd_kg": 3.0},
    {"country_code": "BEL", "country_name": "Belgique",        "value_usd":  2_500_000, "weight_kg":   820_000, "growth_pct": 4.2, "price_usd_kg": 3.0},
    {"country_code": "KOR", "country_name": "Corée du Sud",    "value_usd":  2_200_000, "weight_kg":   700_000, "growth_pct": 8.5, "price_usd_kg": 3.1},
    {"country_code": "SGP", "country_name": "Singapour",       "value_usd":  1_800_000, "weight_kg":   580_000, "growth_pct": 7.2, "price_usd_kg": 3.1},
    {"country_code": "QAT", "country_name": "Qatar",           "value_usd":  1_500_000, "weight_kg":   500_000, "growth_pct": 5.8, "price_usd_kg": 3.0},
    {"country_code": "SEN", "country_name": "Sénégal",         "value_usd":    900_000, "weight_kg":   320_000, "growth_pct": 8.0, "price_usd_kg": 2.8},
    {"country_code": "CIV", "country_name": "Côte d'Ivoire",   "value_usd":    700_000, "weight_kg":   260_000, "growth_pct": 6.5, "price_usd_kg": 2.7},
    {"country_code": "NGA", "country_name": "Nigeria",         "value_usd":    500_000, "weight_kg":   190_000, "growth_pct": 5.0, "price_usd_kg": 2.6},
    {"country_code": "KWT", "country_name": "Koweït",          "value_usd":    450_000, "weight_kg":   160_000, "growth_pct": 4.8, "price_usd_kg": 2.8},
]


# ═══════════════════════════════════════════════════════════════
# FONCTIONS D'ACCÈS AUX DONNÉES
# ═══════════════════════════════════════════════════════════════

def get_trade_data(hs_code: str) -> pd.DataFrame:
    """
    Retourne les données commerciales pour un code HS donné.
    Essaie l'API UN Comtrade, fall back sur données intégrées.
    """
    # Tentative API UN Comtrade
    try:
        url = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
        params = {"cmdCode": hs_code, "period": "2022", "flowCode": "M", "includeDesc": "True"}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        raw = r.json().get("data", [])
        if raw:
            df = pd.DataFrame(raw)[["reporterCode", "reporterDesc", "primaryValue", "netWgt"]]
            df.columns = ["country_code", "country_name", "value_usd", "weight_kg"]
            df["growth_pct"] = 5.0  # valeur neutre si pas disponible
            df["price_usd_kg"] = df["value_usd"] / (df["weight_kg"] + 1)
            return df[df["value_usd"] > 0].dropna().reset_index(drop=True)
    except Exception:
        pass

    # Fallback données intégrées
    records = DEMO_TRADE_DATA.get(hs_code, _DEFAULT_TRADE)
    return pd.DataFrame(records)


def get_accord_score(country_code: str) -> dict:
    """Retourne les infos accord commercial Maroc pour un pays."""
    return ACCORDS_MAROC.get(country_code, {
        "accord": "Aucun accord préférentiel", "droits": 8.0, "type": "NPF"
    })


def get_wb_scores(country_code: str) -> dict:
    """Retourne les indicateurs World Bank pour un pays."""
    return WORLD_BANK_SCORES.get(country_code, {
        "ease_business": 55.0, "political_stability": 40.0,
        "rule_of_law": 50.0, "regulatory_quality": 50.0
    })


def get_diaspora(country_code: str) -> dict:
    """Retourne les données diaspora MRE pour un pays."""
    return DIASPORA_MRE.get(country_code, {"population": 0, "transferts_musd": 0})


def get_logistique(country_code: str) -> dict:
    """Retourne les données logistiques pour un pays."""
    return LOGISTIQUE.get(country_code, {
        "distance_km": 10_000, "lpi": 2.5, "cout_conteneur_usd": 3_500
    })
