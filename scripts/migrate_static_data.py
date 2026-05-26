"""
scripts/migrate_static_data.py — Migration des données statiques vers PostgreSQL
Étape 4 : Migration base de données
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma import Prisma
from data_sources import (
    ACCORDS_MAROC, PAYS_NOM, WORLD_BANK_SCORES,
    DIASPORA_MRE, LOGISTIQUE, DEMO_TRADE_DATA
)

async def migrate_countries(db: Prisma):
    """Migrer les données pays vers PostgreSQL."""
    print("🔄 Migration des pays...")

    countries_data = []
    for iso_code, accords in ACCORDS_MAROC.items():
        wb = WORLD_BANK_SCORES.get(iso_code, {})
        diaspora = DIASPORA_MRE.get(iso_code, {"population": 0, "transferts_musd": 0})
        logist = LOGISTIQUE.get(iso_code, {
            "distance_km": 5000, "lpi": 2.5, "cout_conteneur_usd": 2500,
            "risk_category": 4, "risk_label": "Risque moyen"
        })

        country_data = {
            "isoCode": iso_code,
            "isoCode2": iso_code[:2].upper(),
            "name": PAYS_NOM.get(iso_code, iso_code),
            "nameAr": None,  # À compléter si nécessaire
            "flag": f"🇫🇷" if iso_code == "FRA" else None,  # Simplifié
            "region": "Europe" if iso_code in ["FRA", "DEU", "ESP", "ITA", "GBR"] else "Autre",

            # Accord commercial
            "accordLabel": accords.get("accord", "Aucun"),
            "accordType": accords.get("type", "NPF").upper(),
            "droitsDouane": accords.get("droits", 8.0),

            # Indicateurs World Bank
            "easeBusiness": wb.get("ease_business", 50.0),
            "politicalStability": wb.get("political_stability", 0.0),
            "ruleOfLaw": wb.get("rule_of_law", 0.0),
            "regulatoryQuality": wb.get("regulatory_quality", 0.0),
            "wbUpdatedAt": datetime.now() if wb else None,

            # Risque pays OCDE
            "ocdeRiskCategory": logist.get("risk_category", 4),
            "ocdeRiskScore": 50.0,  # Valeur par défaut
            "ocdeRiskLabel": logist.get("risk_label", "Risque moyen"),

            # Logistique
            "distanceKm": logist.get("distance_km", 5000),
            "lpi": logist.get("lpi", 2.5),
            "coutConteneur": logist.get("cout_conteneur_usd", 2500),
            "portPrincipal": None,

            # Diaspora MRE
            "diasporaPopulation": diaspora.get("population", 0),
            "diasporaTransferts": diaspora.get("transferts_musd", 0.0),

            "isActive": True,
        }
        countries_data.append(country_data)

    # Insérer en batch
    await db.country.create_many(data=countries_data, skip_duplicates=True)
    print(f"✅ {len(countries_data)} pays migrés")

async def migrate_products(db: Prisma):
    """Migrer les produits vers PostgreSQL."""
    print("🔄 Migration des produits...")

    products_data = []
    hs_codes = set()

    # Collecter tous les HS codes depuis DEMO_TRADE_DATA
    for country_data in DEMO_TRADE_DATA.values():
        for product_data in country_data.values():
            if "hs_code" in product_data:
                hs_codes.add(product_data["hs_code"])

    # Créer les produits
    product_mapping = {
        "151590": {"name": "Huile d'argan", "category": "Agroalimentaire", "sector": "Terroir", "emoji": "🫒"},
        "160413": {"name": "Sardines en conserve", "category": "Agroalimentaire", "sector": "Agroalimentaire", "emoji": "🐟"},
        "080410": {"name": "Dattes fraîches", "category": "Agroalimentaire", "sector": "Terroir", "emoji": "🌴"},
        "09102010": {"name": "Safran", "category": "Agroalimentaire", "sector": "Terroir", "emoji": "🌺"},
        "090920": {"name": "Cumin", "category": "Agroalimentaire", "sector": "Agroalimentaire", "emoji": "🌿"},
        "570110": {"name": "Tapis berbère", "category": "Artisanat", "sector": "Artisanat", "emoji": "🪆"},
        "691010": {"name": "Zellige", "category": "Artisanat", "sector": "Artisanat", "emoji": "🏺"},
    }

    for hs_code in hs_codes:
        hs_code_6 = hs_code[:6] if len(hs_code) >= 6 else hs_code
        product_info = product_mapping.get(hs_code, {
            "name": f"Produit HS {hs_code}",
            "category": "Autre",
            "sector": "Industrie",
            "emoji": "📦"
        })

        product_data = {
            "hsCode": hs_code,
            "hsCode6": hs_code_6,
            "name": product_info["name"],
            "category": product_info["category"],
            "sector": product_info["sector"],
            "emoji": product_info["emoji"],
            "isActive": True,
        }
        products_data.append(product_data)

    await db.product.create_many(data=products_data, skip_duplicates=True)
    print(f"✅ {len(products_data)} produits migrés")

async def migrate_trade_data(db: Prisma):
    """Migrer les données commerciales vers PostgreSQL."""
    print("🔄 Migration des données commerciales...")

    trade_data = []
    for country_code, products in DEMO_TRADE_DATA.items():
        for product_key, product_data in products.items():
            if "hs_code" in product_data and "value_usd" in product_data:
                trade_entry = {
                    "productHsCode": product_data["hs_code"],
                    "countryIsoCode": country_code,
                    "year": 2022,  # Données 2022
                    "valueUsd": product_data["value_usd"],
                    "weightKg": product_data.get("weight_kg", product_data["value_usd"] / 10),  # Estimation
                    "priceUsdKg": product_data.get("price_usd_kg", product_data["value_usd"] / product_data.get("weight_kg", product_data["value_usd"] / 10)),
                    "source": "DEMO_DATA",
                }
                trade_data.append(trade_entry)

    # Insérer par batches de 100
    batch_size = 100
    for i in range(0, len(trade_data), batch_size):
        batch = trade_data[i:i+batch_size]
        await db.trade_data.create_many(data=batch, skip_duplicates=True)

    print(f"✅ {len(trade_data)} entrées de données commerciales migrées")

async def migrate_regulatory_alerts(db: Prisma):
    """Migrer les réglementations de base vers PostgreSQL."""
    print("🔄 Migration des réglementations de base...")

    from services.watch.regulatory_watch import REGLEMENTATIONS_BASE

    alerts_data = []
    for reg in REGLEMENTATIONS_BASE:
        alert_data = {
            "externalId": reg["id"],
            "titre": reg["titre"],
            "titreFr": reg["titre"],
            "niveau": reg["niveau"],
            "source": reg["source"],
            "sourceUrl": reg.get("url", ""),
            "produitsHs": reg.get("produits", []),
            "produitsNoms": [],  # À compléter
            "resumeFr": reg["resume"],
            "impactExport": reg["impact"],
            "actionRequise": reg["action"],
            "dateVigueur": None,
            "datePublication": datetime.strptime(reg["date"], "%Y-%m-%d") if "date" in reg else None,
            "impactScore": reg["score_impact"],
            "sourceFilable": True,
            "llmConfiance": None,
            "llmEnhanced": False,
            "delaiJours": reg.get("delai_jours"),
            "isActive": True,
        }
        alerts_data.append(alert_data)

    await db.regulatory_alert.create_many(data=alerts_data, skip_duplicates=True)
    print(f"✅ {len(alerts_data)} réglementations de base migrées")

async def main():
    """Fonction principale de migration."""
    print("🚀 DÉBUT MIGRATION ÉTAPE 4 — Données statiques")
    print("=" * 50)

    # Vérifier la connexion DB
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL non définie")
        return

    print(f"📍 Connexion à : {db_url[:50]}...")

    db = Prisma()
    await db.connect()

    try:
        # Migration des données
        await migrate_countries(db)
        await migrate_products(db)
        await migrate_trade_data(db)
        await migrate_regulatory_alerts(db)

        print("=" * 50)
        print("✅ MIGRATION TERMINÉE AVEC SUCCÈS")
        print("📊 Base de données prête pour l'Étape 4")

    except Exception as e:
        print(f"❌ ERREUR lors de la migration: {e}")
        raise
    finally:
        await db.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())