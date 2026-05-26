"""
download_all_sources.py — Téléchargement toutes sources de données
MaroTrade Intelligence — Dataset complet pour benchmark ML

Sources :
    1. UN Comtrade    — Volumes export/import par produit et pays
    2. World Bank     — Indicateurs gouvernance + économie
    3. FDA openFDA    — Alertes sanitaires USA
    4. RASFF          — Alertes sanitaires UE
    5. Google Trends  — Tendance demande consommateur
    6. OCDE           — Risque pays (statique)
"""

import requests
import json
import time
import pandas as pd
from pathlib import Path
from datetime import datetime

# ── Configuration ────────────────────────────────────────────
DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

COMTRADE_KEY = "b363a3d6c9a84b8cbfa82e11904fcaa0"

# Pays cibles (code ISO3 → code numérique UN)
COUNTRIES = {
    "FRA": {"un": "251",  "wb": "FRA", "name": "France"},
    "DEU": {"un": "276",  "wb": "DEU", "name": "Allemagne"},
    "USA": {"un": "842",  "wb": "USA", "name": "États-Unis"},
    "ESP": {"un": "724",  "wb": "ESP", "name": "Espagne"},
    "ITA": {"un": "380",  "wb": "ITA", "name": "Italie"},
    "NLD": {"un": "528",  "wb": "NLD", "name": "Pays-Bas"},
    "BEL": {"un": "056",  "wb": "BEL", "name": "Belgique"},
    "GBR": {"un": "826",  "wb": "GBR", "name": "Royaume-Uni"},
    "CAN": {"un": "124",  "wb": "CAN", "name": "Canada"},
    "JPN": {"un": "392",  "wb": "JPN", "name": "Japon"},
    "SAU": {"un": "682",  "wb": "SAU", "name": "Arabie Saoudite"},
    "ARE": {"un": "784",  "wb": "ARE", "name": "Émirats Arabes"},
    "QAT": {"un": "634",  "wb": "QAT", "name": "Qatar"},
    "KWT": {"un": "414",  "wb": "KWT", "name": "Koweït"},
    "CHN": {"un": "156",  "wb": "CHN", "name": "Chine"},
    "KOR": {"un": "410",  "wb": "KOR", "name": "Corée du Sud"},
    "SGP": {"un": "702",  "wb": "SGP", "name": "Singapour"},
    "AUS": {"un": "036",  "wb": "AUS", "name": "Australie"},
    "NOR": {"un": "578",  "wb": "NOR", "name": "Norvège"},
    "CHE": {"un": "756",  "wb": "CHE", "name": "Suisse"},
}

YEARS = list(range(2015, 2024))

# Indicateurs World Bank
WB_INDICATORS = {
    "IC.BUS.EASE.XQ": "ease_business",
    "RL.EST":          "rule_of_law",
    "RQ.EST":          "reg_quality",
    "PV.EST":          "political_stability",
    "GE.EST":          "govt_effectiveness",
    "NY.GDP.PCAP.CD":  "gdp_per_capita",
    "NE.IMP.GNFS.ZS":  "imports_pct_gdp",
    "TG.VAL.TOTL.GD.ZS": "trade_pct_gdp",
}

# Produits pour Google Trends
TREND_KEYWORDS = {
    "151590":   ["argan oil", "huile argan"],
    "09102010": ["saffron", "safran"],
    "160413":   ["moroccan sardines", "sardines"],
    "080410":   ["medjool dates", "dattes maroc"],
    "090920":   ["cumin", "cumin morocco"],
    "570110":   ["berber carpet", "tapis berbere"],
    "691010":   ["zellige", "moroccan tiles"],
    "150910":   ["moroccan olive oil", "huile olive maroc"],
    "070200":   ["moroccan tomatoes", "tomates maroc"],
    "080521":   ["moroccan citrus", "clementines maroc"],
}


# ════════════════════════════════════════════════════════════
# SOURCE 1 — WORLD BANK
# ════════════════════════════════════════════════════════════

def download_worldbank():
    """Télécharge tous les indicateurs World Bank pour tous les pays."""
    print("\n" + "─" * 50)
    print("  SOURCE 1 — World Bank API")
    print("─" * 50)

    results = {}

    for iso3, country in COUNTRIES.items():
        wb_code = country["wb"]
        results[iso3] = {"name": country["name"]}

        for indicator, field in WB_INDICATORS.items():
            try:
                r = requests.get(
                    f"https://api.worldbank.org/v2/country/{wb_code}/indicator/{indicator}",
                    params={"format": "json", "per_page": 10, "mrv": 5},
                    timeout=15,
                )
                data = r.json()
                if len(data) > 1 and data[1]:
                    # Prendre la valeur la plus récente non nulle
                    for entry in data[1]:
                        if entry.get("value") is not None:
                            results[iso3][field] = entry["value"]
                            results[iso3][f"{field}_year"] = entry["date"]
                            break
                time.sleep(0.3)
            except Exception as e:
                print(f"  ⚠️  {iso3}/{indicator}: {e}")

        print(f"  ✅ {country['name']} — {len(results[iso3])} indicateurs")

    # Sauvegarder
    path = DATA_DIR / "worldbank_indicators.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Convertir en CSV
    df = pd.DataFrame(results).T
    df.index.name = "iso3"
    df.to_csv(DATA_DIR / "worldbank_indicators.csv")

    print(f"\n  💾 Sauvegardé : {path}")
    print(f"  📊 {len(results)} pays × {len(WB_INDICATORS)} indicateurs")
    return results


# ════════════════════════════════════════════════════════════
# SOURCE 2 — FDA openFDA
# ════════════════════════════════════════════════════════════

def download_fda():
    """Télécharge les alertes FDA pour les produits marocains."""
    print("\n" + "─" * 50)
    print("  SOURCE 2 — FDA openFDA")
    print("─" * 50)

    all_alerts = []
    keywords   = [
        "morocco", "moroccan", "argan", "sardine",
        "dates", "saffron", "olive oil", "cumin",
        "fish", "seafood", "spice"
    ]

    for kw in keywords:
        try:
            r = requests.get(
                "https://api.fda.gov/food/enforcement.json",
                params={
                    "search": f'reason_for_recall:"{kw}"',
                    "limit":  100,
                },
                timeout=15,
            )
            if r.status_code == 200:
                results = r.json().get("results", [])
                for item in results:
                    all_alerts.append({
                        "source":            "FDA",
                        "keyword":           kw,
                        "date":              item.get("recall_initiation_date", ""),
                        "product":           item.get("product_description", "")[:200],
                        "reason":            item.get("reason_for_recall", "")[:300],
                        "classification":    item.get("classification", ""),
                        "status":            item.get("status", ""),
                        "country":           "USA",
                        "recalling_firm":    item.get("recalling_firm", ""),
                    })
                print(f"  ✅ '{kw}' — {len(results)} alertes")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ⚠️  {kw}: {e}")

    # Dédupliquer
    seen    = set()
    unique  = []
    for a in all_alerts:
        key = a["product"][:50] + a["date"]
        if key not in seen:
            seen.add(key)
            unique.append(a)

    path = DATA_DIR / "fda_alerts.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    pd.DataFrame(unique).to_csv(DATA_DIR / "fda_alerts.csv", index=False)

    print(f"\n  💾 Sauvegardé : {path}")
    print(f"  📊 {len(unique)} alertes uniques")
    return unique


# ════════════════════════════════════════════════════════════
# SOURCE 3 — RASFF (EUR-Lex RSS alternatif)
# ════════════════════════════════════════════════════════════

def download_rasff():
    """Télécharge les alertes RASFF via l'API officielle."""
    print("\n" + "─" * 50)
    print("  SOURCE 3 — RASFF Alerts")
    print("─" * 50)

    all_alerts = []

    # Essayer plusieurs URLs RASFF
    urls = [
        "https://webgate.ec.europa.eu/rasff-window/backend/public/consumer/rss",
        "https://www.efsa.europa.eu/en/rss/rasff",
    ]

    import feedparser
    for url in urls:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                for entry in feed.entries:
                    all_alerts.append({
                        "source":   "RASFF",
                        "title":    entry.get("title", ""),
                        "summary":  entry.get("summary", "")[:300],
                        "date":     str(entry.get("published", "")),
                        "link":     entry.get("link", ""),
                        "country":  "EU",
                    })
                print(f"  ✅ {url} — {len(feed.entries)} alertes")
                break
        except Exception as e:
            print(f"  ⚠️  {url}: {e}")

    # Compléter avec EUR-Lex
    try:
        r = requests.get(
            "https://eur-lex.europa.eu/tools/rss/eu-law-updates.xml",
            timeout=15
        )
        feed = feedparser.parse(r.content)
        for entry in feed.entries[:50]:
            title = entry.get("title", "").lower()
            if any(kw in title for kw in [
                "food", "import", "regulation", "standard",
                "sanitary", "phytosanitary", "customs"
            ]):
                all_alerts.append({
                    "source":  "EUR-Lex",
                    "title":   entry.get("title", ""),
                    "summary": entry.get("summary", "")[:300],
                    "date":    str(entry.get("published", "")),
                    "link":    entry.get("link", ""),
                    "country": "EU",
                })
        print(f"  ✅ EUR-Lex — {len(feed.entries)} entrées filtrées")
    except Exception as e:
        print(f"  ⚠️  EUR-Lex: {e}")

    path = DATA_DIR / "rasff_alerts.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_alerts, f, ensure_ascii=False, indent=2)

    pd.DataFrame(all_alerts).to_csv(
        DATA_DIR / "rasff_alerts.csv", index=False
    )

    print(f"\n  💾 Sauvegardé : {path}")
    print(f"  📊 {len(all_alerts)} alertes")
    return all_alerts


# ════════════════════════════════════════════════════════════
# SOURCE 4 — GOOGLE TRENDS
# ════════════════════════════════════════════════════════════

def download_google_trends():
    """Télécharge les tendances Google pour les produits marocains."""
    print("\n" + "─" * 50)
    print("  SOURCE 4 — Google Trends")
    print("─" * 50)

    try:
        from pytrends.request import TrendReq
    except ImportError:
        print("  ⚠️  pytrends non installé : pip install pytrends")
        return {}

    pt      = TrendReq(hl="en-US", timeout=(10, 30))
    results = {}

    target_geos = ["FR", "DE", "US", "ES", "GB", "JP", "SA", "AE"]

    for hs_code, keywords in TREND_KEYWORDS.items():
        results[hs_code] = {}
        kw = keywords[0]  # Premier mot-clé

        for geo in target_geos:
            try:
                pt.build_payload(
                    [kw],
                    geo=geo,
                    timeframe="today 5-y"
                )
                df = pt.interest_over_time()
                if not df.empty and kw in df.columns:
                    results[hs_code][geo] = {
                        "mean":    float(df[kw].mean()),
                        "last":    float(df[kw].iloc[-1]),
                        "trend":   float(
                            df[kw].iloc[-4:].mean() -
                            df[kw].iloc[:4].mean()
                        ),
                    }
                time.sleep(2)
            except Exception as e:
                print(f"  ⚠️  {hs_code}/{geo}: {e}")

        vals = [v["mean"] for v in results[hs_code].values() if "mean" in v]
        print(
            f"  ✅ HS {hs_code} — {len(results[hs_code])} pays "
            f"| score moyen: {sum(vals)/len(vals):.1f}" if vals else
            f"  ⚠️  HS {hs_code} — pas de données"
        )

    path = DATA_DIR / "google_trends.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n  💾 Sauvegardé : {path}")
    return results


# ════════════════════════════════════════════════════════════
# SOURCE 5 — OCDE RISQUE PAYS (statique 2024)
# ════════════════════════════════════════════════════════════

def save_ocde_risk():
    """Sauvegarde les données OCDE risque pays 2024."""
    print("\n" + "─" * 50)
    print("  SOURCE 5 — OCDE Risque Pays 2024")
    print("─" * 50)

    ocde = {
        "FRA": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "DEU": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "USA": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "ESP": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "ITA": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "NLD": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "BEL": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "GBR": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "CAN": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "JPN": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "AUS": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "NOR": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "CHE": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "KOR": {"category": 0, "score": 100, "label": "Pays OCDE"},
        "SAU": {"category": 2, "score": 70,  "label": "Risque faible"},
        "ARE": {"category": 2, "score": 70,  "label": "Risque faible"},
        "QAT": {"category": 2, "score": 70,  "label": "Risque faible"},
        "KWT": {"category": 2, "score": 70,  "label": "Risque faible"},
        "CHN": {"category": 2, "score": 65,  "label": "Risque faible"},
        "SGP": {"category": 1, "score": 90,  "label": "Risque très faible"},
    }

    path = DATA_DIR / "ocde_risk.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ocde, f, ensure_ascii=False, indent=2)

    pd.DataFrame(ocde).T.to_csv(DATA_DIR / "ocde_risk.csv")
    print(f"  ✅ {len(ocde)} pays sauvegardés")
    print(f"  💾 {path}")
    return ocde


# ════════════════════════════════════════════════════════════
# SOURCE 6 — ACCORDS COMMERCIAUX MAROC (statique)
# ════════════════════════════════════════════════════════════

def save_accords():
    """Sauvegarde les accords commerciaux Maroc."""
    print("\n" + "─" * 50)
    print("  SOURCE 6 — Accords Commerciaux Maroc")
    print("─" * 50)

    accords = {
        "FRA": {"accord": "Accord association UE", "droits": 0.0,  "type": "ALE"},
        "DEU": {"accord": "Accord association UE", "droits": 0.0,  "type": "ALE"},
        "USA": {"accord": "Accord libre-échange",  "droits": 0.0,  "type": "ALE"},
        "ESP": {"accord": "Accord association UE", "droits": 0.0,  "type": "ALE"},
        "ITA": {"accord": "Accord association UE", "droits": 0.0,  "type": "ALE"},
        "NLD": {"accord": "Accord association UE", "droits": 0.0,  "type": "ALE"},
        "BEL": {"accord": "Accord association UE", "droits": 0.0,  "type": "ALE"},
        "GBR": {"accord": "Accord préférentiel",   "droits": 2.5,  "type": "PREF"},
        "CAN": {"accord": "NPF standard",          "droits": 5.0,  "type": "NPF"},
        "JPN": {"accord": "NPF standard",          "droits": 5.0,  "type": "NPF"},
        "SAU": {"accord": "Accord GAFTA",          "droits": 0.0,  "type": "ALE"},
        "ARE": {"accord": "Accord GAFTA",          "droits": 0.0,  "type": "ALE"},
        "QAT": {"accord": "Accord GAFTA",          "droits": 0.0,  "type": "ALE"},
        "KWT": {"accord": "Accord GAFTA",          "droits": 0.0,  "type": "ALE"},
        "CHN": {"accord": "NPF standard",          "droits": 8.0,  "type": "NPF"},
        "KOR": {"accord": "NPF standard",          "droits": 5.0,  "type": "NPF"},
        "SGP": {"accord": "NPF standard",          "droits": 0.0,  "type": "NPF"},
        "AUS": {"accord": "NPF standard",          "droits": 5.0,  "type": "NPF"},
        "NOR": {"accord": "Accord AELE",           "droits": 0.0,  "type": "ALE"},
        "CHE": {"accord": "Accord AELE",           "droits": 0.0,  "type": "ALE"},
    }

    path = DATA_DIR / "accords_maroc.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(accords, f, ensure_ascii=False, indent=2)

    pd.DataFrame(accords).T.to_csv(DATA_DIR / "accords_maroc.csv")
    print(f"  ✅ {len(accords)} pays sauvegardés")
    print(f"  💾 {path}")
    return accords


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    start = datetime.now()

    print("\n" + "═" * 60)
    print("  MAROTRADE INTELLIGENCE — TÉLÉCHARGEMENT TOUTES SOURCES")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("═" * 60)

    # Sources statiques (rapides)
    save_ocde_risk()
    save_accords()

    # APIs externes
    download_worldbank()
    download_fda()
    download_rasff()
    download_google_trends()

    duration = (datetime.now() - start).total_seconds() / 60

    print("\n" + "═" * 60)
    print("  ✅ TOUTES LES SOURCES TÉLÉCHARGÉES")
    print(f"  ⏱️  Durée : {duration:.1f} minutes")
    print("\n  Fichiers générés :")
    for f in sorted(DATA_DIR.glob("*.json")):
        size = f.stat().st_size / 1024
        print(f"    {f.name:<40} {size:>8.1f} KB")
    print("═" * 60)