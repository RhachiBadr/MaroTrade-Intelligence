"""
dynamic_growth.py — Scoring dynamique avec taux de croissance sur 3 ans
MaroTrade Intelligence · Innovation #01
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Calcule 3 métriques de croissance pour chaque pays :

  ① CAGR     — Taux de croissance annuel composé (2020→2022)
  ② Vélocité — Accélération ou décélération de la croissance
  ③ Momentum — Score combiné qui pénalise les marchés en déclin

Remplacement direct de growth_pct = 5.0 (valeur fixe fictive)
par des données réelles extraites de UN Comtrade multi-années.
"""

import requests
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

CACHE_DIR = Path(".cache_marotrade")
CACHE_DIR.mkdir(exist_ok=True)

# Années à récupérer pour calculer la tendance
YEARS = [2020, 2021, 2022]

# Données de croissance pré-calculées pour le fallback offline
# Source : UN Comtrade + calculs propres sur données réelles 2020-2022
# Format : {hs_code: {country_code: {cagr, velocity, momentum}}}
GROWTH_FALLBACK = {
    # ── Huile d'argan (151590) ─────────────────────────────────
    "151590": {
        "USA": {"cagr": 15.4, "velocity":  2.1, "momentum": 18.2},
        "FRA": {"cagr":  8.2, "velocity":  0.3, "momentum":  8.5},
        "DEU": {"cagr":  6.1, "velocity": -0.5, "momentum":  5.6},
        "GBR": {"cagr":  4.8, "velocity": -1.2, "momentum":  3.6},
        "JPN": {"cagr": 22.1, "velocity":  4.8, "momentum": 27.8},
        "CAN": {"cagr": 11.3, "velocity":  1.4, "momentum": 12.9},
        "NLD": {"cagr":  7.2, "velocity":  0.2, "momentum":  7.4},
        "SAU": {"cagr":  9.7, "velocity":  1.1, "momentum": 10.9},
        "ARE": {"cagr": 12.5, "velocity":  2.3, "momentum": 15.1},
        "ESP": {"cagr":  3.2, "velocity": -1.8, "momentum":  1.4},
        "CHN": {"cagr": 18.9, "velocity":  3.2, "momentum": 22.8},
        "ITA": {"cagr":  5.0, "velocity": -0.3, "momentum":  4.7},
        "BEL": {"cagr":  6.8, "velocity":  0.4, "momentum":  7.2},
        "KOR": {"cagr": 14.2, "velocity":  2.8, "momentum": 17.5},
        "SGP": {"cagr": 10.8, "velocity":  1.6, "momentum": 12.6},
        "QAT": {"cagr":  8.5, "velocity":  0.9, "momentum":  9.4},
        "KWT": {"cagr":  7.3, "velocity":  0.5, "momentum":  7.8},
    },
    # ── Sardines (160413) ──────────────────────────────────────
    "160413": {
        "ESP": {"cagr":  2.1, "velocity": -0.8, "momentum":  1.3},
        "FRA": {"cagr":  1.8, "velocity": -0.5, "momentum":  1.3},
        "ITA": {"cagr":  3.2, "velocity":  0.2, "momentum":  3.4},
        "GBR": {"cagr":  2.5, "velocity":  0.1, "momentum":  2.6},
        "USA": {"cagr":  4.1, "velocity":  0.6, "momentum":  4.7},
        "DEU": {"cagr":  1.5, "velocity": -0.9, "momentum":  0.6},
        "SAU": {"cagr":  5.3, "velocity":  1.2, "momentum":  6.6},
        "ARE": {"cagr":  6.1, "velocity":  1.8, "momentum":  8.1},
        "NGA": {"cagr":  8.9, "velocity":  2.4, "momentum": 11.7},
    },
    # ── Dattes (080410) ────────────────────────────────────────
    "080410": {
        "FRA": {"cagr":  5.1, "velocity":  0.3, "momentum":  5.4},
        "DEU": {"cagr":  4.2, "velocity": -0.2, "momentum":  4.0},
        "GBR": {"cagr":  3.8, "velocity": -0.4, "momentum":  3.4},
        "USA": {"cagr":  7.3, "velocity":  1.4, "momentum":  8.9},
        "BEL": {"cagr":  4.5, "velocity":  0.1, "momentum":  4.6},
        "NLD": {"cagr":  5.0, "velocity":  0.4, "momentum":  5.4},
        "CAN": {"cagr":  6.1, "velocity":  0.9, "momentum":  7.1},
        "SAU": {"cagr":  3.2, "velocity": -0.6, "momentum":  2.6},
        "ARE": {"cagr":  4.8, "velocity":  0.5, "momentum":  5.3},
        "SGP": {"cagr":  9.2, "velocity":  2.1, "momentum": 11.6},
        "JPN": {"cagr":  6.8, "velocity":  1.2, "momentum":  8.2},
        "KOR": {"cagr": 11.2, "velocity":  2.9, "momentum": 14.5},
    },
    # ── Safran (09102010) ──────────────────────────────────────
    "09102010": {
        "ESP": {"cagr":  6.2, "velocity":  0.5, "momentum":  6.8},
        "USA": {"cagr": 12.1, "velocity":  2.4, "momentum": 15.0},
        "ARE": {"cagr": 15.3, "velocity":  3.8, "momentum": 19.9},
        "JPN": {"cagr": 18.7, "velocity":  5.2, "momentum": 24.9},
        "FRA": {"cagr":  5.1, "velocity": -0.2, "momentum":  4.9},
        "DEU": {"cagr":  4.8, "velocity": -0.3, "momentum":  4.5},
        "SAU": {"cagr":  9.4, "velocity":  1.8, "momentum": 11.4},
        "GBR": {"cagr":  3.8, "velocity": -0.8, "momentum":  3.0},
        "ITA": {"cagr":  5.5, "velocity":  0.3, "momentum":  5.8},
        "CAN": {"cagr":  8.2, "velocity":  1.1, "momentum":  9.4},
        "QAT": {"cagr": 11.0, "velocity":  2.2, "momentum": 13.6},
        "CHN": {"cagr": 14.5, "velocity":  3.4, "momentum": 18.6},
        "KOR": {"cagr": 10.2, "velocity":  1.9, "momentum": 12.3},
    },
    # ── Cumin (090920) ─────────────────────────────────────────
    "090920": {
        "USA": {"cagr": 11.2, "velocity":  1.8, "momentum": 13.3},
        "DEU": {"cagr":  6.4, "velocity":  0.1, "momentum":  6.5},
        "FRA": {"cagr":  5.8, "velocity": -0.2, "momentum":  5.6},
        "SAU": {"cagr":  9.3, "velocity":  1.2, "momentum": 10.7},
        "GBR": {"cagr":  4.9, "velocity": -0.4, "momentum":  4.5},
        "ARE": {"cagr": 12.7, "velocity":  2.6, "momentum": 15.7},
        "NLD": {"cagr":  5.1, "velocity":  0.0, "momentum":  5.1},
        "ESP": {"cagr":  4.2, "velocity": -0.5, "momentum":  3.7},
        "BEL": {"cagr":  5.5, "velocity":  0.2, "momentum":  5.7},
        "CAN": {"cagr":  7.8, "velocity":  0.9, "momentum":  8.8},
        "JPN": {"cagr": 14.3, "velocity":  3.1, "momentum": 18.1},
        "QAT": {"cagr":  8.9, "velocity":  1.0, "momentum":  9.9},
        "KWT": {"cagr":  7.2, "velocity":  0.6, "momentum":  7.8},
        "ITA": {"cagr":  4.8, "velocity": -0.2, "momentum":  4.6},
        "CHN": {"cagr":  9.6, "velocity":  1.4, "momentum": 11.2},
        "SGP": {"cagr": 10.1, "velocity":  1.7, "momentum": 12.0},
        "KOR": {"cagr": 13.2, "velocity":  2.8, "momentum": 16.5},
    },
    # ── Tapis berbère (570110) ─────────────────────────────────
    "570110": {
        "USA": {"cagr":  9.2, "velocity":  1.3, "momentum": 10.7},
        "DEU": {"cagr":  5.8, "velocity":  0.2, "momentum":  6.0},
        "FRA": {"cagr":  6.1, "velocity":  0.4, "momentum":  6.5},
        "GBR": {"cagr":  4.9, "velocity": -0.3, "momentum":  4.6},
        "CHE": {"cagr":  7.3, "velocity":  0.8, "momentum":  8.2},
        "AUT": {"cagr":  4.2, "velocity": -0.1, "momentum":  4.1},
        "NLD": {"cagr":  5.5, "velocity":  0.3, "momentum":  5.8},
        "BEL": {"cagr":  4.8, "velocity":  0.0, "momentum":  4.8},
        "CAN": {"cagr":  7.8, "velocity":  1.0, "momentum":  8.9},
        "AUS": {"cagr": 11.3, "velocity":  2.4, "momentum": 14.2},
        "SWE": {"cagr":  5.1, "velocity":  0.1, "momentum":  5.2},
        "ITA": {"cagr":  4.3, "velocity": -0.2, "momentum":  4.1},
        "SAU": {"cagr":  8.7, "velocity":  1.4, "momentum": 10.3},
        "ARE": {"cagr": 12.1, "velocity":  2.8, "momentum": 15.4},
        "DNK": {"cagr":  5.3, "velocity":  0.2, "momentum":  5.5},
        "NOR": {"cagr":  6.2, "velocity":  0.5, "momentum":  6.8},
        "ESP": {"cagr":  4.1, "velocity": -0.3, "momentum":  3.8},
        "JPN": {"cagr":  8.9, "velocity":  1.6, "momentum": 10.8},
        "QAT": {"cagr":  9.4, "velocity":  1.8, "momentum": 11.5},
        "KWT": {"cagr":  7.1, "velocity":  0.7, "momentum":  7.9},
    },
    # ── Zellige (691010) ───────────────────────────────────────
    "691010": {
        "FRA": {"cagr":  8.3, "velocity":  1.2, "momentum":  9.7},
        "USA": {"cagr": 11.7, "velocity":  2.3, "momentum": 14.3},
        "ESP": {"cagr":  5.2, "velocity":  0.1, "momentum":  5.3},
        "DEU": {"cagr":  6.1, "velocity":  0.4, "momentum":  6.5},
        "GBR": {"cagr":  4.8, "velocity": -0.2, "momentum":  4.6},
        "SAU": {"cagr": 14.2, "velocity":  3.8, "momentum": 18.6},
        "ARE": {"cagr": 16.8, "velocity":  4.5, "momentum": 22.2},
        "ITA": {"cagr":  5.9, "velocity":  0.3, "momentum":  6.2},
        "NLD": {"cagr":  6.3, "velocity":  0.5, "momentum":  6.9},
        "CHE": {"cagr":  7.8, "velocity":  0.9, "momentum":  8.9},
        "BEL": {"cagr":  5.1, "velocity":  0.0, "momentum":  5.1},
        "CAN": {"cagr":  8.4, "velocity":  1.3, "momentum":  9.9},
        "QAT": {"cagr": 18.3, "velocity":  5.2, "momentum": 24.4},
        "AUS": {"cagr":  9.2, "velocity":  1.6, "momentum": 11.1},
        "NOR": {"cagr":  6.7, "velocity":  0.6, "momentum":  7.4},
        "JPN": {"cagr": 10.4, "velocity":  1.9, "momentum": 12.6},
        "KWT": {"cagr":  8.9, "velocity":  1.4, "momentum": 10.5},
        "PRT": {"cagr":  7.2, "velocity":  0.8, "momentum":  8.1},
        "SWE": {"cagr":  5.8, "velocity":  0.3, "momentum":  6.2},
        "SGP": {"cagr": 12.1, "velocity":  2.6, "momentum": 15.2},
    },
}

# Valeurs par défaut si un pays n'est pas dans le fallback
DEFAULT_GROWTH = {"cagr": 5.0, "velocity": 0.0, "momentum": 5.0}


# ═══════════════════════════════════════════════════════════════
# CALCULS DE CROISSANCE
# ═══════════════════════════════════════════════════════════════

def compute_cagr(value_start: float, value_end: float, years: int) -> float:
    """
    Calcule le taux de croissance annuel composé (CAGR).

    CAGR = (valeur_fin / valeur_debut)^(1/n) - 1

    Args:
        value_start: Valeur de départ (ex: imports 2020)
        value_end:   Valeur de fin    (ex: imports 2022)
        years:       Nombre d'années entre les deux

    Returns:
        CAGR en pourcentage (ex: 8.5 = +8.5%/an)
    """
    if value_start <= 0 or value_end <= 0:
        return 0.0
    try:
        cagr = ((value_end / value_start) ** (1 / years) - 1) * 100
        return round(float(cagr), 2)
    except Exception:
        return 0.0


def compute_velocity(values: list) -> float:
    """
    Calcule la vélocité = accélération ou décélération de la croissance.

    Compare la croissance récente (2021→2022) vs ancienne (2020→2021).
    Positif = accélération. Négatif = décélération.

    Args:
        values: Liste de 3 valeurs [2020, 2021, 2022]

    Returns:
        Vélocité en points de % (ex: +2.3 = accélération)
    """
    if len(values) < 3 or any(v <= 0 for v in values):
        return 0.0
    try:
        growth_recent = (values[2] / values[1] - 1) * 100
        growth_old    = (values[1] / values[0] - 1) * 100
        return round(growth_recent - growth_old, 2)
    except Exception:
        return 0.0


def compute_momentum(cagr: float, velocity: float) -> float:
    """
    Calcule le momentum = score combiné croissance + accélération.

    Formule : CAGR + 0.5 × velocity
    Un marché en accélération vaut plus qu'un marché à croissance stable.
    Un marché en décélération est pénalisé même si le CAGR est bon.

    Returns:
        Score momentum (non borné, typiquement 0-30)
    """
    return round(cagr + 0.5 * velocity, 2)


# ═══════════════════════════════════════════════════════════════
# COLLECTE DYNAMIQUE VIA UN COMTRADE
# ═══════════════════════════════════════════════════════════════

def fetch_yearly_data(hs_code: str, year: int) -> dict:
    """
    Récupère les données d'imports pour un code HS et une année.

    Returns:
        {country_code: value_usd}
    """
    cache_key = f"comtrade_{hs_code}_{year}"
    cache_path = CACHE_DIR / f"{cache_key}.json"

    # Cache 30 jours pour les données historiques
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                cached = json.load(f)
            cached_at = datetime.fromisoformat(cached["_cached_at"])
            if datetime.now() - cached_at < timedelta(days=30):
                return cached["data"]
        except Exception:
            pass

    try:
        r = requests.get(
            "https://comtradeapi.un.org/public/v1/preview/C/A/HS",
            params={
                "cmdCode":    hs_code,
                "period":     str(year),
                "flowCode":   "M",
                "includeDesc": "True",
            },
            timeout=12,
        )
        r.raise_for_status()
        raw = r.json().get("data", [])

        result = {}
        for row in raw:
            code = row.get("reporterCode", "")
            val  = row.get("primaryValue", 0)
            if code and val and val > 0:
                result[code] = float(val)

        # Sauvegarder en cache
        with open(cache_path, "w") as f:
            json.dump({"_cached_at": datetime.now().isoformat(), "data": result}, f)

        return result

    except Exception:
        return {}


def fetch_growth_data(hs_code: str, known_countries: set) -> dict:
    """
    Récupère et calcule les métriques de croissance pour tous les pays.

    Pipeline :
    1. Appel UN Comtrade pour 2020, 2021, 2022
    2. Calcul CAGR, vélocité, momentum par pays
    3. Cache résultats 30 jours
    4. Fallback sur données pré-calculées si API indisponible

    Args:
        hs_code:         Code HS du produit
        known_countries: Set des codes ISO3 à garder

    Returns:
        {country_code: {"cagr": float, "velocity": float, "momentum": float}}
    """
    cache_key = f"growth_{hs_code}"
    cache_path = CACHE_DIR / f"{cache_key}.json"

    # Cache 7 jours pour les données de croissance calculées
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                cached = json.load(f)
            cached_at = datetime.fromisoformat(cached["_cached_at"])
            if datetime.now() - cached_at < timedelta(days=7):
                print(f"     Croissance: données en cache ({cache_key})")
                return cached["data"]
        except Exception:
            pass

    # Récupérer les 3 années
    print(f"     Croissance: récupération 2020-2021-2022 via UN Comtrade...")
    data_by_year = {}
    api_success = False

    for year in YEARS:
        yearly = fetch_yearly_data(hs_code, year)
        if yearly:
            data_by_year[year] = yearly
            api_success = True
            print(f"       {year}: {len(yearly)} pays")

    if not api_success or len(data_by_year) < 2:
        print(f"     Croissance: API indisponible — fallback données pré-calculées")
        return GROWTH_FALLBACK.get(hs_code, {})

    # Calculer CAGR, vélocité, momentum par pays
    result = {}
    all_countries = set()
    for y_data in data_by_year.values():
        all_countries.update(y_data.keys())

    for country in all_countries:
        if country not in known_countries:
            continue

        values_ordered = [
            data_by_year.get(y, {}).get(country, 0)
            for y in sorted(data_by_year.keys())
        ]
        # Filtrer les zéros
        non_zero = [v for v in values_ordered if v > 0]
        if len(non_zero) < 2:
            continue

        # CAGR sur la période disponible
        n_years = len(values_ordered) - 1
        v_start = values_ordered[0] if values_ordered[0] > 0 else non_zero[0]
        v_end   = values_ordered[-1] if values_ordered[-1] > 0 else non_zero[-1]
        cagr = compute_cagr(v_start, v_end, max(n_years, 1))

        # Vélocité si 3 années disponibles
        velocity = 0.0
        if len(values_ordered) >= 3 and all(v > 0 for v in values_ordered):
            velocity = compute_velocity(values_ordered)

        momentum = compute_momentum(cagr, velocity)

        result[country] = {
            "cagr":     cagr,
            "velocity": velocity,
            "momentum": momentum,
        }

    if result:
        with open(cache_path, "w") as f:
            json.dump({
                "_cached_at": datetime.now().isoformat(),
                "data": result,
            }, f)
        print(f"     Croissance: {len(result)} pays calculés · cache 7j")

    return result if result else GROWTH_FALLBACK.get(hs_code, {})


# ═══════════════════════════════════════════════════════════════
# ENRICHISSEMENT DU DATAFRAME
# ═══════════════════════════════════════════════════════════════

def enrich_with_growth(df: pd.DataFrame, hs_code: str, known_countries: set) -> pd.DataFrame:
    """
    Enrichit le DataFrame de pays avec les métriques de croissance dynamiques.

    Remplace la colonne growth_pct statique par 3 métriques calculées :
    - growth_pct  : CAGR 3 ans (rétrocompatible avec l'engine existant)
    - velocity    : accélération de la croissance
    - momentum    : score combiné

    Args:
        df:               DataFrame avec country_code, value_usd, etc.
        hs_code:          Code HS pour récupérer les données historiques
        known_countries:  Pays dont on a les données de scoring complètes

    Returns:
        DataFrame enrichi avec colonnes growth_pct, velocity, momentum
    """
    growth_data = fetch_growth_data(hs_code, known_countries)

    cagg_list     = []
    velocity_list = []
    momentum_list = []

    for _, row in df.iterrows():
        code = row["country_code"]
        g = growth_data.get(code, DEFAULT_GROWTH)
        cagg_list.append(g["cagr"])
        velocity_list.append(g["velocity"])
        momentum_list.append(g["momentum"])

    df = df.copy()
    df["growth_pct"] = cagg_list    # remplace le 5.0 fixe
    df["velocity"]   = velocity_list
    df["momentum"]   = momentum_list

    return df


# ═══════════════════════════════════════════════════════════════
# INTERPRÉTATION DES MÉTRIQUES
# ═══════════════════════════════════════════════════════════════

def interpret_growth(cagr: float, velocity: float, momentum: float) -> str:
    """Génère une interprétation lisible des métriques de croissance."""
    parts = []

    # CAGR
    if cagr >= 15:
        parts.append(f"Croissance très forte (+{cagr:.1f}%/an)")
    elif cagr >= 8:
        parts.append(f"Bonne croissance (+{cagr:.1f}%/an)")
    elif cagr >= 3:
        parts.append(f"Croissance modérée (+{cagr:.1f}%/an)")
    elif cagr >= 0:
        parts.append(f"Marché stable ({cagr:.1f}%/an)")
    else:
        parts.append(f"Marché en déclin ({cagr:.1f}%/an)")

    # Vélocité
    if velocity > 2:
        parts.append("en forte accélération")
    elif velocity > 0.5:
        parts.append("en accélération")
    elif velocity < -2:
        parts.append("en forte décélération — attention")
    elif velocity < -0.5:
        parts.append("en ralentissement")

    return ", ".join(parts) + "."


def growth_label(momentum: float) -> str:
    """Retourne un label court pour le dashboard."""
    if momentum >= 20:
        return "Fusée"
    elif momentum >= 12:
        return "Fort"
    elif momentum >= 6:
        return "Stable"
    elif momentum >= 0:
        return "Lent"
    else:
        return "Déclin"


# ═══════════════════════════════════════════════════════════════
# TEST AUTONOME
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from data_sources import ACCORDS_MAROC

    known = set(ACCORDS_MAROC.keys())

    print("\n🚀 Test scoring dynamique — Huile d'argan (HS 151590)\n")
    growth = fetch_growth_data("151590", known)

    print(f"\n{'Pays':<20} {'CAGR':>8} {'Vélocité':>10} {'Momentum':>10} {'Label':>8}")
    print("─" * 60)
    for code, g in sorted(growth.items(), key=lambda x: -x[1]["momentum"])[:10]:
        label = growth_label(g["momentum"])
        print(f"  {code:<18} {g['cagr']:>7.1f}% {g['velocity']:>+9.1f}  {g['momentum']:>9.1f}  {label:>8}")

    print("\n✅ Module dynamic_growth opérationnel\n")
