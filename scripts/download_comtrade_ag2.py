"""
scripts/download_comtrade_ag2.py
================================
Télécharge TOUS les exports du Maroc depuis UN Comtrade
- Niveau : AG2 (codes HS 2 chiffres)
- Années : 2015 → 2025
- Partenaires : TOUS les pays disponibles
- Flux : Exports uniquement (flowCode = X)

Produit : data/raw/comtrade_ag2_full.csv
"""

import requests
import pandas as pd
import time
import json
from pathlib import Path
from datetime import datetime

# ── Configuration ────────────────────────────────────────────
API_KEY  = "b363a3d6c9a84b8cbfa82e11904fcaa0"
BASE_URL = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

REPORTER = "504"           # Maroc
YEARS    = list(range(2015, 2026))   # 2015 → 2025
AGG_LVL  = "AG2"          # Codes HS 2 chiffres

# Pause entre requêtes (respecter rate limit)
SLEEP_BETWEEN = 2.0        # secondes
SLEEP_RATELIMIT = 65.0     # secondes si 429


# ════════════════════════════════════════════════════════════
# ÉTAPE 0 — Récupérer tous les codes AG2 disponibles
# ════════════════════════════════════════════════════════════

def get_ag2_codes():
    """
    Récupère la liste des codes HS AG2 exportés par le Maroc.
    Basé sur les données 2022 (année référence).
    """
    cache_file = DATA_DIR / "ag2_codes.json"
    if cache_file.exists():
        with open(cache_file) as f:
            codes = json.load(f)
        print(f"✅ Codes AG2 chargés depuis cache : {len(codes)} codes")
        return codes

    print("Récupération des codes AG2 depuis UN Comtrade...")
    try:
        r = requests.get(
            BASE_URL,
            params={
                "reporterCode": REPORTER,
                "period":       "2022",
                "flowCode":     "X",
                "includeDesc":  "True",
                "aggLevel":     AGG_LVL,
            },
            headers={"Ocp-Apim-Subscription-Key": API_KEY},
            timeout=60,
        )
        r.raise_for_status()
        rows = r.json().get("data", [])

        codes = {}
        for row in rows:
            code = str(row.get("cmdCode", "")).strip()
            desc = row.get("cmdDesc", "")
            val  = row.get("primaryValue", 0) or 0
            if code and len(code) <= 2:
                codes[code] = {"desc": desc, "value_2022": val}

        # Trier par valeur décroissante
        codes = dict(sorted(codes.items(),
                            key=lambda x: x[1]["value_2022"],
                            reverse=True))

        with open(cache_file, "w") as f:
            json.dump(codes, f, ensure_ascii=False, indent=2)

        print(f"✅ {len(codes)} codes AG2 trouvés")
        for i, (code, info) in enumerate(list(codes.items())[:10]):
            print(f"   {i+1:2}. HS{code:3} — {info['desc'][:50]:50} "
                  f"{info['value_2022']:>15,.0f} USD")

        return codes

    except Exception as e:
        print(f"❌ Erreur : {e}")
        return {}


# ════════════════════════════════════════════════════════════
# ÉTAPE 1 — Télécharger pour chaque code AG2 × année
# ════════════════════════════════════════════════════════════

def fetch_one(hs_code: str, year: int, retry: int = 3) -> list:
    """
    Télécharge les données UN Comtrade pour un code AG2 et une année.
    Retourne la liste de tous les partenaires avec leurs valeurs.
    """
    for attempt in range(retry):
        try:
            r = requests.get(
                BASE_URL,
                params={
                    "reporterCode": REPORTER,
                    "cmdCode":      hs_code,
                    "period":       str(year),
                    "flowCode":     "X",
                    "includeDesc":  "True",
                    "aggLevel":     AGG_LVL,
                },
                headers={"Ocp-Apim-Subscription-Key": API_KEY},
                timeout=45,
            )

            if r.status_code == 429:
                print(f"      ⏳ Rate limit — attente {SLEEP_RATELIMIT}s")
                time.sleep(SLEEP_RATELIMIT)
                continue

            if r.status_code == 404:
                return []

            r.raise_for_status()
            return r.json().get("data", [])

        except requests.Timeout:
            print(f"      ⏰ Timeout HS{hs_code}/{year} (essai {attempt+1})")
            time.sleep(5)
        except Exception as e:
            print(f"      ⚠️  Erreur HS{hs_code}/{year} : {e}")
            time.sleep(3)

    return []


# ════════════════════════════════════════════════════════════
# ÉTAPE 2 — Pipeline principal
# ════════════════════════════════════════════════════════════

def download_all():
    """
    Télécharge toutes les données et produit un CSV propre.
    """
    print("\n" + "═" * 65)
    print("  TÉLÉCHARGEMENT COMTRADE AG2 — MaroTrade Intelligence")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"  Reporter : Maroc (504) | Niveau : AG2 | Années : {YEARS[0]}–{YEARS[-1]}")
    print("═" * 65)

    # Récupérer les codes AG2
    ag2_codes = get_ag2_codes()
    if not ag2_codes:
        print("❌ Impossible de récupérer les codes AG2")
        return

    total_tasks = len(ag2_codes) * len(YEARS)
    done        = 0
    all_rows    = []

    print(f"\n📦 {len(ag2_codes)} codes AG2 × {len(YEARS)} années = {total_tasks} requêtes\n")

    for hs_code, hs_info in ag2_codes.items():
        hs_desc = hs_info.get("desc", "")[:55]
        print(f"HS{hs_code:3} — {hs_desc}")

        for year in YEARS:
            done += 1
            rows = fetch_one(hs_code, year)

            for row in rows:
                partner_code = str(row.get("partnerCode", "")).strip()
                partner_name = str(row.get("partnerDesc", "")).strip()
                value_usd    = row.get("primaryValue", 0) or 0
                weight_kg    = row.get("netWgt", 0) or 0

                # Exclure les agrégats (monde, etc.)
                if partner_code in ("0", "899", ""):
                    continue

                all_rows.append({
                    "hs_code":      hs_code,
                    "hs_desc":      hs_desc,
                    "year":         year,
                    "partner_code": partner_code,
                    "partner_name": partner_name,
                    "value_usd":    value_usd,
                    "weight_kg":    weight_kg,
                })

            pct = done / total_tasks * 100
            print(f"  {year} : {len(rows):>4} partenaires | "
                  f"total={len(all_rows):>7,} | {pct:.1f}%")

            time.sleep(SLEEP_BETWEEN)

        # Sauvegarde intermédiaire tous les 10 codes
        if len(all_rows) > 0 and done % (len(YEARS) * 10) == 0:
            _save_csv(all_rows, suffix="_partial")
            print(f"\n  💾 Sauvegarde intermédiaire : {len(all_rows):,} lignes\n")

    # Sauvegarde finale
    df = _save_csv(all_rows)

    print("\n" + "═" * 65)
    print("  ✅ TÉLÉCHARGEMENT TERMINÉ")
    print(f"  Lignes totales  : {len(all_rows):,}")
    print(f"  Codes HS AG2    : {df['hs_code'].nunique()}")
    print(f"  Partenaires     : {df['partner_code'].nunique()}")
    print(f"  Années          : {df['year'].min()} → {df['year'].max()}")
    print(f"  Valeur totale   : {df['value_usd'].sum():,.0f} USD")
    print(f"  Fichier         : data/raw/comtrade_ag2_full.csv")
    print("═" * 65)


# ════════════════════════════════════════════════════════════
# ÉTAPE 3 — Sauvegarde CSV propre
# ════════════════════════════════════════════════════════════

def _save_csv(rows: list, suffix: str = "") -> pd.DataFrame:
    """Sauvegarde les données en CSV propre."""
    if not rows:
        print("⚠️  Aucune donnée à sauvegarder")
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Nettoyer
    df["value_usd"]  = pd.to_numeric(df["value_usd"], errors="coerce").fillna(0)
    df["weight_kg"]  = pd.to_numeric(df["weight_kg"], errors="coerce").fillna(0)
    df["year"]       = df["year"].astype(int)
    df["hs_code"]    = df["hs_code"].astype(str).str.zfill(2)

    # Prix moyen USD/kg
    df["price_usd_kg"] = (
        df["value_usd"] / df["weight_kg"].replace(0, float("nan"))
    ).fillna(0)

    # Trier
    df = df.sort_values(["hs_code", "partner_code", "year"]).reset_index(drop=True)

    # Sauvegarder
    path = DATA_DIR / f"comtrade_ag2_full{suffix}.csv"
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"  💾 {path} — {len(df):,} lignes")

    return df


# ════════════════════════════════════════════════════════════
# ÉTAPE 4 — Construction dataset ML avec log-return
# ════════════════════════════════════════════════════════════

def build_ml_dataset():
    """
    Construit le dataset ML final avec :
    - Features lag (lag1, lag2, lag3, ma3, std3)
    - Variable cible : log-return année N+1
    - Split temporel : train/val/test
    """
    print("\n" + "─" * 65)
    print("  CONSTRUCTION DATASET ML")
    print("─" * 65)

    path = DATA_DIR / "comtrade_ag2_full.csv"
    if not path.exists():
        print(f"❌ Fichier manquant : {path}")
        print("   Lance d'abord : python scripts/download_comtrade_ag2.py")
        return

    df = pd.read_csv(path)
    print(f"✅ Données chargées : {len(df):,} lignes")

    # ── Trier ────────────────────────────────────────────────
    df = df.sort_values(["hs_code", "partner_code", "year"])

    # ── Log-return (variable cible) ───────────────────────────
    # Pour chaque (hs_code, partner_code) :
    # target_N = log(value_N+1 / value_N) × 100
    df["value_next"] = df.groupby(
        ["hs_code", "partner_code"]
    )["value_usd"].shift(-1)

    df["log_return"] = (
        (df["value_next"] / df["value_usd"].replace(0, float("nan")))
        .apply(lambda x: None if x is None or x <= 0 else __import__("math").log(x) * 100)
    )

    # ── Lag features ─────────────────────────────────────────
    grp = df.groupby(["hs_code", "partner_code"])["value_usd"]

    df["lag1"]  = grp.shift(1)   # valeur année N-1
    df["lag2"]  = grp.shift(2)   # valeur année N-2
    df["lag3"]  = grp.shift(3)   # valeur année N-3
    df["ma3"]   = (df["lag1"] + df["lag2"] + df["lag3"]) / 3
    df["std3"]  = df[["lag1", "lag2", "lag3"]].std(axis=1)

    # Growth lag1
    df["growth_lag1"] = (
        (df["value_usd"] - df["lag1"]) / df["lag1"].replace(0, float("nan"))
    ) * 100

    # Log-return lag1
    df["log_return_lag1"] = (
        (df["value_usd"] / df["lag1"].replace(0, float("nan")))
        .apply(lambda x: None if x is None or x <= 0 else __import__("math").log(x) * 100)
    )

    # ── Features prix ─────────────────────────────────────────
    df["price_lag1"] = grp.shift(1)  # proxy

    # ── Supprimer lignes sans cible ───────────────────────────
    df_ml = df.dropna(subset=["log_return"]).copy()

    # Filtrer les outliers extrêmes (log-return entre -200% et +200%)
    df_ml = df_ml[
        (df_ml["log_return"] >= -200) &
        (df_ml["log_return"] <= 200)
    ]

    print(f"✅ Après nettoyage : {len(df_ml):,} lignes")
    print(f"   Log-return moyen : {df_ml['log_return'].mean():.2f}%")
    print(f"   Log-return std   : {df_ml['log_return'].std():.2f}%")

    # ── Split temporel ────────────────────────────────────────
    train = df_ml[df_ml["year"] <= 2021]
    val   = df_ml[df_ml["year"].isin([2022, 2023])]
    test  = df_ml[df_ml["year"].isin([2024, 2025])]

    print(f"\n✅ Split temporel :")
    print(f"   Train (2015–2021) : {len(train):,} lignes")
    print(f"   Val   (2022–2023) : {len(val):,} lignes")
    print(f"   Test  (2024–2025) : {len(test):,} lignes")

    # ── Sauvegarder ───────────────────────────────────────────
    df_ml.to_csv(DATA_DIR / "ml_dataset_full.csv",   index=False)
    train.to_csv(DATA_DIR / "ml_train.csv",           index=False)
    val.to_csv(  DATA_DIR / "ml_val.csv",             index=False)
    test.to_csv( DATA_DIR / "ml_test.csv",            index=False)

    print(f"\n✅ Datasets sauvegardés :")
    print(f"   data/raw/ml_dataset_full.csv")
    print(f"   data/raw/ml_train.csv")
    print(f"   data/raw/ml_val.csv")
    print(f"   data/raw/ml_test.csv")

    return df_ml


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--build-only":
        # Construire dataset ML depuis fichier existant
        build_ml_dataset()
    else:
        # Télécharger + construire
        download_all()
        build_ml_dataset()
