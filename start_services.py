# start_services.py — Démarrage unifié des services

import asyncio
import logging
import sys
from pathlib import Path

# Configuration
sys.path.insert(0, str(Path(__file__).parent))

from logging_config import setup_logging
from services.cache import CacheService
from external_api_manager import api_manager
from services.scoring import MarketScoringEngine
from services.watch import RegulatoryWatchEngine
from services.nlp import NLPAnalyzer

logger = setup_logging("INFO")

async def test_services():
    """Test rapide de tous les services."""
    print("=== Test des Services MaroTrade ===\n")

    # 1. Cache
    print("1. Test Cache Redis...")
    cache = CacheService()
    cache.set("test", {"message": "hello"}, ttl=60)
    result = cache.get("test")
    print(f"   Cache: {'OK' if result else 'FAIL'}")

    # 2. APIs Externes
    print("\n2. Test APIs Externes...")
    try:
        result = await api_manager.fetch_un_comtrade("151590", "USA", 2022)
        print(f"   UN Comtrade: {'OK' if result else 'FAIL'}")
    except Exception as e:
        print(f"   UN Comtrade: FAIL ({e})")

    # 3. Scoring Engine
    print("\n3. Test Scoring Engine...")
    try:
        engine = MarketScoringEngine()
        results = engine.run("Huile d'argan", "151590", top_n=2)
        print(f"   Scoring: OK ({len(results)} résultats)")
    except Exception as e:
        print(f"   Scoring: FAIL ({e})")

    # 4. Regulatory Watch
    print("\n4. Test Regulatory Watch...")
    try:
        watch = RegulatoryWatchEngine()
        alerts = watch.run("151590", "Huile d'argan", ["USA", "FRA"])
        print(f"   Watch: OK ({len(alerts)} alertes)")
    except Exception as e:
        print(f"   Watch: FAIL ({e})")

    # 5. NLP Analyzer
    print("\n5. Test NLP Analyzer...")
    try:
        analyzer = NLPAnalyzer()
        print(f"   NLP: OK (disponible: {analyzer.available})")
    except Exception as e:
        print(f"   NLP: FAIL ({e})")

    print("\n=== Tests terminés ===")

def main():
    """Point d'entrée principal."""
    logger.info("Démarrage MaroTrade Intelligence v2.0")

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Mode test
        asyncio.run(test_services())
    else:
        # Mode normal - démarrer les serveurs
        print("Mode serveur - À implémenter (FastAPI + Streamlit)")
        logger.info("Services prêts")

if __name__ == "__main__":
    main()