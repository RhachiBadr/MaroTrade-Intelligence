"""
scripts/migrate_cache_data.py — Migration des données cache vers PostgreSQL
Étape 4 : Migration base de données
"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma import Prisma
from services.cache.cache_manager import CacheManager

async def migrate_comtrade_data(db: Prisma, cache_dir: str):
    """Migrer les données UN Comtrade depuis le cache."""
    print("🔄 Migration des données UN Comtrade...")

    pattern = os.path.join(cache_dir, "comtrade_*.json")
    files = glob.glob(pattern)

    migrated_count = 0
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extraire les métadonnées du nom de fichier
            filename = os.path.basename(file_path)
            parts = filename.replace('comtrade_', '').replace('.json', '').split('_')
            if len(parts) >= 3:
                country_code = parts[0]
                hs_code = parts[1]
                year = int(parts[2])

                # Migrer chaque entrée
                for entry in data.get("data", []):
                    trade_entry = {
                        "productHsCode": hs_code,
                        "countryIsoCode": country_code,
                        "year": year,
                        "valueUsd": entry.get("value_usd", 0),
                        "weightKg": entry.get("weight_kg", 0),
                        "priceUsdKg": entry.get("price_usd_kg", 0),
                        "source": "UN_COMTRADE_API",
                    }
                    await db.trade_data.upsert(
                        where={
                            "productHsCode_countryIsoCode_year": {
                                "productHsCode": hs_code,
                                "countryIsoCode": country_code,
                                "year": year
                            }
                        },
                        data={
                            "create": trade_entry,
                            "update": trade_entry
                        }
                    )
                    migrated_count += 1

        except Exception as e:
            print(f"⚠️ Erreur migration {file_path}: {e}")
            continue

    print(f"✅ {migrated_count} entrées UN Comtrade migrées")

async def migrate_growth_data(db: Prisma, cache_dir: str):
    """Migrer les données de croissance calculées."""
    print("🔄 Migration des données de croissance...")

    pattern = os.path.join(cache_dir, "growth_*.json")
    files = glob.glob(pattern)

    migrated_count = 0
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extraire les métadonnées
            filename = os.path.basename(file_path)
            parts = filename.replace('growth_', '').replace('.json', '').split('_')
            if len(parts) >= 2:
                country_code = parts[0]
                hs_code = parts[1]

                growth_entry = {
                    "productHsCode": hs_code,
                    "countryIsoCode": country_code,
                    "cagr3Years": data.get("cagr_3_years", 0),
                    "velocity": data.get("velocity", 0),
                    "momentum": data.get("momentum", 0),
                    "trendDirection": data.get("trend_direction", "stable"),
                    "lastUpdated": datetime.now(),
                }

                await db.growth_indicator.upsert(
                    where={
                        "productHsCode_countryIsoCode": {
                            "productHsCode": hs_code,
                            "countryIsoCode": country_code
                        }
                    },
                    data={
                        "create": growth_entry,
                        "update": growth_entry
                    }
                )
                migrated_count += 1

        except Exception as e:
            print(f"⚠️ Erreur migration {file_path}: {e}")
            continue

    print(f"✅ {migrated_count} indicateurs de croissance migrés")

async def migrate_forecast_data(db: Prisma, cache_dir: str):
    """Migrer les données de prévisions Prophet."""
    print("🔄 Migration des données de prévisions...")

    pattern = os.path.join(cache_dir, "forecast_*.json")
    files = glob.glob(pattern)

    migrated_count = 0
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extraire les métadonnées
            filename = os.path.basename(file_path)
            parts = filename.replace('forecast_', '').replace('.json', '').split('_')
            if len(parts) >= 2:
                country_code = parts[0]
                hs_code = parts[1]

                # Créer l'entrée de prévision
                forecast_entry = {
                    "productHsCode": hs_code,
                    "countryIsoCode": country_code,
                    "modelType": "PROPHET",
                    "forecastHorizon": 36,  # 3 ans
                    "forecastData": json.dumps(data.get("forecast", {})),
                    "cagrPredicted": data.get("cagr_predicted", 0),
                    "confidenceLevel": data.get("confidence", 0.8),
                    "lastUpdated": datetime.now(),
                    "isActive": True,
                }

                await db.forecast.upsert(
                    where={
                        "productHsCode_countryIsoCode": {
                            "productHsCode": hs_code,
                            "countryIsoCode": country_code
                        }
                    },
                    data={
                        "create": forecast_entry,
                        "update": forecast_entry
                    }
                )
                migrated_count += 1

        except Exception as e:
            print(f"⚠️ Erreur migration {file_path}: {e}")
            continue

    print(f"✅ {migrated_count} prévisions migrées")

async def migrate_llm_analyses(db: Prisma, cache_dir: str):
    """Migrer les analyses LLM depuis le cache."""
    print("🔄 Migration des analyses LLM...")

    pattern = os.path.join(cache_dir, "llm_*.json")
    files = glob.glob(pattern)

    migrated_count = 0
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Créer l'entrée d'analyse LLM
            llm_entry = {
                "externalId": f"llm_{os.path.basename(file_path)}",
                "content": data.get("content", ""),
                "analysisType": data.get("type", "REGULATORY"),
                "modelUsed": data.get("model", "claude-3-haiku-20240307"),
                "confidenceScore": data.get("confidence", 0.8),
                "tokensUsed": data.get("tokens", 0),
                "costUsd": data.get("cost", 0.0),
                "responseTimeMs": data.get("response_time", 0),
                "createdAt": datetime.now(),
                "isActive": True,
            }

            await db.llm_analysis.create(data=llm_entry)
            migrated_count += 1

        except Exception as e:
            print(f"⚠️ Erreur migration {file_path}: {e}")
            continue

    print(f"✅ {migrated_count} analyses LLM migrées")

async def migrate_rss_alerts(db: Prisma, cache_dir: str):
    """Migrer les alertes RSS depuis le cache."""
    print("🔄 Migration des alertes RSS...")

    pattern = os.path.join(cache_dir, "rss_*.json")
    files = glob.glob(pattern)

    migrated_count = 0
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Migrer chaque alerte
            for alert in data.get("alerts", []):
                alert_entry = {
                    "externalId": alert.get("id", f"rss_{migrated_count}"),
                    "titre": alert.get("title", ""),
                    "titreFr": alert.get("title_fr", ""),
                    "niveau": alert.get("level", "INFO"),
                    "source": alert.get("source", "RSS"),
                    "sourceUrl": alert.get("url", ""),
                    "produitsHs": alert.get("hs_codes", []),
                    "produitsNoms": alert.get("products", []),
                    "resumeFr": alert.get("summary", ""),
                    "impactExport": alert.get("impact", 20),
                    "actionRequise": alert.get("action", ""),
                    "datePublication": datetime.fromisoformat(alert["date"]) if "date" in alert else None,
                    "impactScore": alert.get("impact_score", 20),
                    "sourceFilable": True,
                    "llmConfiance": alert.get("llm_confidence"),
                    "llmEnhanced": alert.get("llm_enhanced", False),
                    "isActive": True,
                }

                await db.regulatory_alert.upsert(
                    where={"externalId": alert_entry["externalId"]},
                    data={
                        "create": alert_entry,
                        "update": alert_entry
                    }
                )
                migrated_count += 1

        except Exception as e:
            print(f"⚠️ Erreur migration {file_path}: {e}")
            continue

    print(f"✅ {migrated_count} alertes RSS migrées")

async def main():
    """Fonction principale de migration des données cache."""
    print("🚀 DÉBUT MIGRATION ÉTAPE 4 — Données cache")
    print("=" * 50)

    # Vérifier la connexion DB
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL non définie")
        return

    # Déterminer le répertoire cache
    cache_dir = os.getenv("CACHE_DIR", ".cache_marotrade")
    if not os.path.exists(cache_dir):
        print(f"⚠️ Répertoire cache {cache_dir} n'existe pas")
        return

    print(f"📍 Connexion à : {db_url[:50]}...")
    print(f"📁 Cache source : {cache_dir}")

    db = Prisma()
    await db.connect()

    try:
        # Migration des données cache
        await migrate_comtrade_data(db, cache_dir)
        await migrate_growth_data(db, cache_dir)
        await migrate_forecast_data(db, cache_dir)
        await migrate_llm_analyses(db, cache_dir)
        await migrate_rss_alerts(db, cache_dir)

        print("=" * 50)
        print("✅ MIGRATION CACHE TERMINÉE AVEC SUCCÈS")
        print("📊 Données cache migrées vers PostgreSQL")

    except Exception as e:
        print(f"❌ ERREUR lors de la migration: {e}")
        raise
    finally:
        await db.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())