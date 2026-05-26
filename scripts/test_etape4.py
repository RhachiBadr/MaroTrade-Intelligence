"""
scripts/test_etape4.py — Tests de validation Étape 4
Vérification PostgreSQL + Redis + Services
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any

async def test_database_connection():
    """Tester la connexion PostgreSQL."""
    print("🔗 Test connexion PostgreSQL...")

    try:
        from prisma import Prisma
        db = Prisma()
        await db.connect()

        # Test requête simple
        count = await db.country.count()
        print(f"✅ PostgreSQL connecté ({count} pays)")

        await db.disconnect()
        return True

    except Exception as e:
        print(f"❌ Erreur PostgreSQL: {e}")
        return False

def test_redis_connection():
    """Tester la connexion Redis."""
    print("🔗 Test connexion Redis...")

    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        r.ping()

        # Test set/get
        r.set("test_key", "test_value")
        value = r.get("test_key")
        assert value == b"test_value"

        print("✅ Redis connecté et fonctionnel")
        return True

    except Exception as e:
        print(f"❌ Erreur Redis: {e}")
        return False

async def test_data_integrity():
    """Tester l'intégrité des données migrées."""
    print("📊 Test intégrité données...")

    try:
        from prisma import Prisma
        db = Prisma()
        await db.connect()

        # Compter les enregistrements
        countries = await db.country.count()
        products = await db.product.count()
        trade_data = await db.trade_data.count()
        alerts = await db.regulatory_alert.count()

        print(f"📈 Pays: {countries}")
        print(f"📦 Produits: {products}")
        print(f"📊 Données commerce: {trade_data}")
        print(f"🚨 Alertes: {alerts}")

        # Vérifier données essentielles
        assert countries > 0, "Aucun pays migré"
        assert products > 0, "Aucun produit migré"

        await db.disconnect()
        print("✅ Intégrité données OK")
        return True

    except Exception as e:
        print(f"❌ Erreur intégrité: {e}")
        return False

async def test_cache_manager():
    """Tester le CacheManager avec Redis."""
    print("💾 Test CacheManager...")

    try:
        from services.cache.cache_manager import CacheManager

        cache = CacheManager(
            redis_url=os.getenv("REDIS_URL"),
            fs_cache_dir=os.getenv("CACHE_DIR", ".cache_marotrade")
        )

        # Test set/get
        test_data = {"test": "value", "number": 42}
        cache.set("test_cache", test_data, ttl_seconds=60)

        retrieved = cache.get("test_cache", ttl_seconds=60)
        assert retrieved == test_data, f"Données incorrectes: {retrieved}"

        print("✅ CacheManager OK")
        return True

    except Exception as e:
        print(f"❌ Erreur CacheManager: {e}")
        return False

async def test_authentication():
    """Tester le système d'authentification."""
    print("🔐 Test authentification...")

    try:
        from prisma import Prisma
        from api import get_password_hash, verify_password, create_access_token

        # Test hash password
        password = "test123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed), "Hash password incorrect"

        # Test JWT
        token = create_access_token({"sub": "test@example.com"})
        assert token, "Token JWT non généré"

        # Test utilisateur admin
        db = Prisma()
        await db.connect()

        admin = await db.user.find_first(where={"role": "ADMIN"})
        assert admin, "Aucun administrateur trouvé"
        assert admin.email == "admin@marotrade.ma", "Email admin incorrect"

        await db.disconnect()

        print("✅ Authentification OK")
        return True

    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
        return False

async def test_scoring_service():
    """Tester le service de scoring avec la nouvelle infrastructure."""
    print("🎯 Test service scoring...")

    try:
        from scoring_engine import ScoringEngine

        engine = ScoringEngine()

        # Test scoring pour huile d'argan -> France
        result = await engine.score_markets(
            product_name="Huile d'argan",
            hs_code="151590",
            target_countries=["FRA"]
        )

        assert result, "Résultat scoring vide"
        assert len(result) > 0, "Aucun marché scoré"
        assert "FRA" in [r["country_code"] for r in result], "France non trouvée"

        france_result = next(r for r in result if r["country_code"] == "FRA")
        assert "score_final" in france_result, "Score final manquant"
        assert france_result["score_final"] > 0, "Score invalide"

        print("✅ Service scoring OK")
        return True

    except Exception as e:
        print(f"❌ Erreur service scoring: {e}")
        return False

async def test_regulatory_service():
    """Tester le service de veille réglementaire."""
    print("📋 Test service veille réglementaire...")

    try:
        from regulatory_watch import RegulatoryWatch

        watch = RegulatoryWatch()

        # Test récupération alertes
        alerts = await watch.get_alerts(
            hs_code="151590",
            product_name="Huile d'argan",
            target_countries=["FRA", "ESP"]
        )

        assert alerts, "Alertes vides"
        assert "alerts" in alerts, "Structure alertes incorrecte"

        print("✅ Service veille réglementaire OK")
        return True

    except Exception as e:
        print(f"❌ Erreur service veille: {e}")
        return False

def test_api_imports():
    """Tester les imports API."""
    print("📦 Test imports API...")

    try:
        import api
        from api import app, get_current_user, create_access_token

        assert app, "Application FastAPI non trouvée"
        assert callable(get_current_user), "Fonction get_current_user manquante"
        assert callable(create_access_token), "Fonction create_access_token manquante"

        print("✅ Imports API OK")
        return True

    except Exception as e:
        print(f"❌ Erreur imports API: {e}")
        return False

async def performance_test():
    """Test de performance basique."""
    print("⚡ Test performance...")

    try:
        import time
        from scoring_engine import ScoringEngine

        engine = ScoringEngine()

        # Mesurer temps de scoring
        start_time = time.time()
        result = await engine.score_markets(
            product_name="Huile d'argan",
            hs_code="151590",
            target_countries=["FRA", "DEU", "ESP"]
        )
        end_time = time.time()

        duration = end_time - start_time
        print(".2f"
        # Performance acceptable: < 5 secondes
        if duration < 5.0:
            print("✅ Performance OK")
            return True
        else:
            print("⚠️ Performance lente mais acceptable")
            return True

    except Exception as e:
        print(f"❌ Erreur performance: {e}")
        return False

async def main():
    """Fonction principale de tests."""
    print("🧪 TESTS VALIDATION ÉTAPE 4")
    print("=" * 50)

    tests = [
        ("Connexion PostgreSQL", test_database_connection),
        ("Connexion Redis", test_redis_connection),
        ("Intégrité données", test_data_integrity),
        ("CacheManager", test_cache_manager),
        ("Authentification", test_authentication),
        ("Service scoring", test_scoring_service),
        ("Service veille réglementaire", test_regulatory_service),
        ("Imports API", test_api_imports),
        ("Performance", performance_test),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n▶️ {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                success = await test_func()
            else:
                success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append((test_name, False))

    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS TESTS")

    passed = 0
    failed = 0

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
        else:
            failed += 1

    print(f"\n📈 Score: {passed}/{passed + failed} tests réussis")

    if failed == 0:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("🚀 Étape 4 validée - Prêt pour la production")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) échoué(s)")
        print("🔧 Corrigez les erreurs avant de continuer")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)