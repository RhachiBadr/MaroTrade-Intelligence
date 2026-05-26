"""
download_dataset.py — Téléchargement dataset complet MaroTrade Intelligence
Télécharge les données UN Comtrade pour les top 100 produits marocains
"""

import requests
import json
import time
import pandas as pd
from pathlib import Path
from datetime import datetime

# ── Configuration ────────────────────────────────────────────
API_KEY  = "b363a3d6c9a84b8cbfa82e11904fcaa0"
BASE_URL = "https://comtradeapi.un.org/data/v1/get/C/A/HS"

YEARS = list(range(2015, 2024))  # 2015 → 2023

# Top pays importateurs (codes numériques UN Comtrade)
TARGET_COUNTRIES = {
    "251": "France",
    "276": "Allemagne",
    "842": "États-Unis",
    "724": "Espagne",
    "380": "Italie",
    "528": "Pays-Bas",
    "056": "Belgique",
    "826": "Royaume-Uni",
    "124": "Canada",
    "392": "Japon",
    "682": "Arabie Saoudite",
    "784": "Émirats Arabes",
    "634": "Qatar",
    "414": "Koweït",
    "156": "Chine",
    "410": "Corée du Sud",
    "702": "Singapour",
    "036": "Australie",
    "578": "Norvège",
    "756": "Suisse",
}

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_top_hs_codes(n=100):
    """Retourne les top N codes HS marocains par valeur export."""
    file = DATA_DIR / "maroc_hs_codes.json"
    if not file.exists():
        print("❌ Fichier maroc_hs_codes.json manquant")
        return []

    with open(file) as f:
        codes = json.load(f)

    sorted_codes = sorted(
        codes.items(),
        key=lambda x: x[1]["value"],
        reverse=True
    )
    top = [(code, info) for code, info in sorted_codes[:n]]
    print(f"✅ {len(top)} codes HS sélectionnés")
    return top


def fetch_comtrade(hs_code, year, reporter_code="504"):
    """Récupère les données UN Comtrade pour un code HS et une année."""
    try:
        r = requests.get(
            BASE_URL,
            params={
                "reporterCode": reporter_code,
                "cmdCode":      hs_code,
                "period":       str(year),
                "flowCode":     "X",
                "includeDesc":  "True",
                "motCode":      "0",
            },
            headers={"Ocp-Apim-Subscription-Key": API_KEY},
            timeout=30,
        )

        if r.status_code == 429:
            print(f"    ⏳ Rate limit — attente 60s...")
            time.sleep(60)
            return fetch_comtrade(hs_code, year, reporter_code)

        if r.status_code != 200:
            return []

        return r.json().get("data", [])

    except Exception as e:
        print(f"    ⚠️  Erreur {hs_code}/{year}: {e}")
        return []


def download_all():
    """Télécharge toutes les données et sauvegarde en CSV + JSON."""
    print("\n" + "═" * 60)
    print("  TÉLÉCHARGEMENT DATASET MAROTRADE INTELLIGENCE")
    print("  UN Comtrade API — Exports Maroc 2015–2023")
    print("═" * 60)

    # Top 100 produits
    top_codes = get_top_hs_codes(100)
    if not top_codes:
        return

    all_rows = []
    total    = len(top_codes) * len(YEARS)
    done     = 0
    errors   = 0

    for hs_code, hs_info in top_codes:
        hs_desc = hs_info.get("desc", "")[:60]
        print(f"\n📦 HS {hs_code} — {hs_desc}")

        for year in YEARS:
            done += 1
            rows = fetch_comtrade(hs_code, year)

            # Filtrer sur pays cibles
            filtered = [
                r for r in rows
                if str(r.get("partnerCode", "")).zfill(3) in TARGET_COUNTRIES
            ]

            for row in filtered:
                partner_code = str(row.get("partnerCode", "")).zfill(3)
                all_rows.append({
                    "hs_code":       hs_code,
                    "hs_desc":       hs_desc,
                    "year":          year,
                    "country_code":  partner_code,
                    "country_name":  TARGET_COUNTRIES.get(partner_code, ""),
                    "value_usd":     row.get("primaryValue", 0) or 0,
                    "weight_kg":     row.get("netWgt", 0) or 0,
                    "qty":           row.get("qty", 0) or 0,
                })

            progress = f"{done}/{total}"
            print(f"  {year}: {len(filtered)} pays cibles | total lignes: {len(all_rows)} [{progress}]")

            # Pause pour respecter le rate limit API
            time.sleep(1.5)

        # Sauvegarde intermédiaire tous les 10 produits
        if done % (len(YEARS) * 10) == 0:
            _save(all_rows, suffix="_partial")
            print(f"\n  💾 Sauvegarde intermédiaire : {len(all_rows)} lignes")

    # Sauvegarde finale
    _save(all_rows)
    print(f"\n✅ Téléchargement terminé")
    print(f"   Total lignes     : {len(all_rows)}")
    print(f"   Produits         : {len(top_codes)}")
    print(f"   Pays             : {len(TARGET_COUNTRIES)}")
    print(f"   Années           : {YEARS[0]} → {YEARS[-1]}")
    print(f"   Fichier CSV      : data/raw/marotrade_dataset.csv")
    print(f"   Fichier JSON     : data/raw/marotrade_dataset.json")


def _save(rows, suffix=""):
    """Sauvegarde les données en CSV et JSON."""
    if not rows:
        print("⚠️  Aucune donnée à sauvegarder")
        return

    df = pd.DataFrame(rows)

    # Enrichissement
    df["price_usd_kg"] = df.apply(
        lambda r: r["value_usd"] / r["weight_kg"]
        if r["weight_kg"] > 0 else 0, axis=1
    )

    # Calcul CAGR par produit/pays
    df_sorted = df.sort_values(["hs_code", "country_code", "year"])
    df_sorted["value_lag1"] = df_sorted.groupby(
        ["hs_code", "country_code"]
    )["value_usd"].shift(1)
    df_sorted["growth_yoy"] = (
        (df_sorted["value_usd"] - df_sorted["value_lag1"])
        / df_sorted["value_lag1"].replace(0, float("nan"))
        * 100
    )

    # Sauvegarder
    csv_path  = DATA_DIR / f"marotrade_dataset{suffix}.csv"
    json_path = DATA_DIR / f"marotrade_dataset{suffix}.json"

    df_sorted.to_csv(csv_path, index=False, encoding="utf-8")
    df_sorted.to_json(json_path, orient="records", force_ascii=False, indent=2)

    print(f"  💾 CSV  : {csv_path} ({len(df_sorted)} lignes)")
    print(f"  💾 JSON : {json_path}")

    # Statistiques
    print(f"\n  📊 Aperçu dataset :")
    print(f"     Produits uniques : {df_sorted['hs_code'].nunique()}")
    print(f"     Pays uniques     : {df_sorted['country_name'].nunique()}")
    print(f"     Années           : {df_sorted['year'].min()} → {df_sorted['year'].max()}")
    print(f"     Valeur totale    : {df_sorted['value_usd'].sum():,.0f} USD")


if __name__ == "__main__":
    start = datetime.now()
    download_all()
    duration = (datetime.now() - start).total_seconds() / 60
    print(f"\n⏱️  Durée totale : {duration:.1f} minutes")