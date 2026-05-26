"""
scripts/check_etape4.py — Vérification pré-migration Étape 4
Contrôle environnement et dépendances avant migration
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment_variables():
    """Vérifier les variables d'environnement requises."""
    print("🔍 Variables d'environnement...")

    required_vars = {
        "DATABASE_URL": "postgresql://...",
        "REDIS_URL": "redis://...",
        "ANTHROPIC_API_KEY": "sk-ant-...",
        "JWT_SECRET_KEY": "secret-key"
    }

    optional_vars = {
        "CACHE_DIR": ".cache_marotrade",
        "UN_COMTRADE_API_KEY": "api-key",
        "WORLD_BANK_API_KEY": "api-key",
        "GOOGLE_TRENDS_API_KEY": "api-key"
    }

    missing_required = []
    missing_optional = []

    for var, example in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"❌ {var} : MANQUANT (ex: {example})")
            missing_required.append(var)
        else:
            print(f"✅ {var} : OK")

    for var, example in optional_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"⚠️  {var} : MANQUANT (optionnel, ex: {example})")
            missing_optional.append(var)
        else:
            print(f"✅ {var} : OK")

    if missing_required:
        print(f"\n❌ Variables requises manquantes: {len(missing_required)}")
        print("📝 Définissez-les dans docker.env ou export VAR=value")
        return False

    if missing_optional:
        print(f"\n⚠️ Variables optionnelles manquantes: {len(missing_optional)}")
        print("ℹ️ L'application fonctionnera mais avec limitations")

    return True

def check_python_dependencies():
    """Vérifier les dépendances Python."""
    print("\n🔍 Dépendances Python...")

    required_packages = [
        ("prisma", "0.11.0"),
        ("redis", "5.0.0"),
        ("bcrypt", "4.1.0"),
        ("PyJWT", "2.8.0"),
        ("slowapi", "0.1.9"),
        ("fastapi", "0.104.0"),
        ("uvicorn", "0.24.0"),
        ("streamlit", "1.28.0"),
        ("plotly", "5.17.0"),
        ("pandas", "2.1.0"),
        ("scikit-learn", "1.3.0"),
        ("xgboost", "2.0.0"),
        ("shap", "0.43.0"),
        ("prophet", "1.1.0"),
    ]

    missing = []
    for package, min_version in required_packages:
        try:
            module = __import__(package.replace("-", "_"))
            version = getattr(module, "__version__", "unknown")
            print(f"✅ {package} {version}")
        except ImportError:
            print(f"❌ {package} : MANQUANT")
            missing.append(package)

    if missing:
        print(f"\n❌ Paquets manquants: {len(missing)}")
        print("📦 Installez avec: pip install -r requirements.txt")
        return False

    return True

def check_external_services():
    """Vérifier les services externes (PostgreSQL, Redis)."""
    print("\n🔍 Services externes...")

    # Test PostgreSQL
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            from prisma import Prisma
            import asyncio

            async def test_db():
                db = Prisma()
                await db.connect()
                await db.execute_raw("SELECT 1")
                await db.disconnect()
                return True

            result = asyncio.run(test_db())
            if result:
                print("✅ PostgreSQL : CONNECTÉ")
            else:
                print("❌ PostgreSQL : ERREUR CONNEXION")
                return False
        except Exception as e:
            print(f"❌ PostgreSQL : {e}")
            return False
    else:
        print("❌ PostgreSQL : URL non définie")
        return False

    # Test Redis
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            print("✅ Redis : CONNECTÉ")
        except Exception as e:
            print(f"❌ Redis : {e}")
            return False
    else:
        print("❌ Redis : URL non définie")
        return False

    return True

def check_prisma_setup():
    """Vérifier la configuration Prisma."""
    print("\n🔍 Configuration Prisma...")

    schema_path = Path("prisma/schema.prisma")
    if not schema_path.exists():
        print("❌ schema.prisma : FICHIER MANQUANT")
        return False

    print("✅ schema.prisma : PRÉSENT")

    # Vérifier génération client
    try:
        import prisma
        print("✅ Client Prisma : GÉNÉRÉ")
    except ImportError:
        print("❌ Client Prisma : NON GÉNÉRÉ")
        print("📦 Générez avec: prisma generate")
        return False

    return True

def check_cache_directory():
    """Vérifier le répertoire cache."""
    print("\n🔍 Répertoire cache...")

    cache_dir = os.getenv("CACHE_DIR", ".cache_marotrade")
    cache_path = Path(cache_dir)

    if cache_path.exists():
        # Compter fichiers cache
        files = list(cache_path.glob("**/*"))
        print(f"✅ Cache : {len(files)} fichiers")
    else:
        print("⚠️ Cache : RÉPERTOIRE INEXISTANT (sera créé)")
        try:
            cache_path.mkdir(parents=True, exist_ok=True)
            print("✅ Cache : RÉPERTOIRE CRÉÉ")
        except Exception as e:
            print(f"❌ Cache : ERREUR CRÉATION - {e}")
            return False

    return True

def check_api_keys():
    """Vérifier les clés API externes."""
    print("\n🔍 Clés API externes...")

    api_keys = {
        "ANTHROPIC_API_KEY": "Claude 3.5 Haiku (LLM)",
        "UN_COMTRADE_API_KEY": "UN Comtrade (données commerce)",
        "WORLD_BANK_API_KEY": "World Bank (indicateurs)",
        "GOOGLE_TRENDS_API_KEY": "Google Trends (tendance)"
    }

    missing = 0
    for key, description in api_keys.items():
        value = os.getenv(key)
        if value and len(value.strip()) > 10:  # Clé valide
            print(f"✅ {key} : OK ({description})")
        else:
            print(f"⚠️ {key} : MANQUANT ({description})")
            missing += 1

    if missing > 0:
        print(f"\n⚠️ {missing} clé(s) API manquante(s)")
        print("ℹ️ L'application fonctionnera avec des limitations")

    return True  # Non bloquant

def generate_report():
    """Générer un rapport de vérification."""
    print("\n" + "=" * 50)
    print("📋 RAPPORT VÉRIFICATION ÉTAPE 4")
    print("=" * 50)

    checks = [
        ("Variables environnement", check_environment_variables),
        ("Dépendances Python", check_python_dependencies),
        ("Services externes", check_external_services),
        ("Configuration Prisma", check_prisma_setup),
        ("Répertoire cache", check_cache_directory),
        ("Clés API", check_api_keys),
    ]

    results = []
    for check_name, check_func in checks:
        print(f"\n▶️ {check_name}...")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append((check_name, False))

    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")

    print(f"\n📈 Score: {passed}/{total}")

    if passed == total:
        print("\n🎉 ENVIRONNEMENT PRÊT !")
        print("🚀 Lancez la migration: python scripts/run_etape4.py")
        return True
    else:
        print(f"\n⚠️ {total - passed} vérification(s) échouée(s)")
        print("🔧 Corrigez les erreurs avant de continuer")
        return False

def main():
    """Fonction principale de vérification."""
    print("🔍 VÉRIFICATION PRÉ-MIGRATION ÉTAPE 4")
    print("Contrôle environnement et dépendances")
    print("=" * 50)

    success = generate_report()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)