"""
scripts/run_etape4.py — Script principal d'exécution Étape 4
Migration PostgreSQL + Redis + Services mis à jour
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any

def check_environment():
    """Vérifier les variables d'environnement requises."""
    print("🔍 VÉRIFICATION ENVIRONNEMENT")
    print("-" * 30)

    required_vars = {
        "DATABASE_URL": "postgresql://user:password@localhost:5432/marotrade",
        "REDIS_URL": "redis://localhost:6379",
        "ANTHROPIC_API_KEY": "sk-ant-...",
        "JWT_SECRET_KEY": "marotrade-secret-key-change-in-production"
    }

    missing = []
    for var, example in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"❌ {var} : NON DÉFINI (exemple: {example})")
            missing.append(var)
        else:
            print(f"✅ {var} : DÉFINI")

    if missing:
        print(f"\n❌ Variables manquantes: {', '.join(missing)}")
        print("📝 Définissez-les dans docker.env ou variables d'environnement")
        return False

    print("\n✅ Environnement OK")
    return True

def check_dependencies():
    """Vérifier les dépendances Python."""
    print("\n🔍 VÉRIFICATION DÉPENDANCES")
    print("-" * 30)

    required_packages = [
        "prisma", "redis", "bcrypt", "jwt", "slowapi",
        "fastapi", "uvicorn", "streamlit", "plotly"
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)

    if missing:
        print(f"\n❌ Paquets manquants: {', '.join(missing)}")
        print("📦 Installez avec: pip install -r requirements.txt")
        return False

    print("\n✅ Dépendances OK")
    return True

def run_migration():
    """Exécuter la migration de base de données."""
    print("\n🗄️ MIGRATION BASE DE DONNÉES")
    print("-" * 30)

    # Générer le client Prisma
    print("📦 Génération client Prisma...")
    try:
        subprocess.run([sys.executable, "-m", "prisma", "generate"], check=True)
        print("✅ Client Prisma généré")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur génération Prisma: {e}")
        return False

    # Appliquer les migrations Prisma
    print("🔄 Application migrations Prisma...")
    try:
        subprocess.run([sys.executable, "-m", "prisma", "db", "push"], check=True)
        print("✅ Migrations appliquées")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur migrations: {e}")
        return False

    # Migrer les données statiques
    print("📊 Migration données statiques...")
    try:
        subprocess.run([sys.executable, "scripts/migrate_static_data.py"], check=True)
        print("✅ Données statiques migrées")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur migration statique: {e}")
        return False

    # Migrer les données cache
    print("📈 Migration données cache...")
    try:
        subprocess.run([sys.executable, "scripts/migrate_cache_data.py"], check=True)
        print("✅ Données cache migrées")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur migration cache: {e}")
        return False

    print("\n✅ Migration base de données terminée")
    return True

def update_services():
    """Mettre à jour les services pour Étape 4."""
    print("\n🔧 MISE À JOUR SERVICES")
    print("-" * 30)

    try:
        subprocess.run([sys.executable, "scripts/update_services_etape4.py"], check=True)
        print("✅ Services mis à jour")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur mise à jour services: {e}")
        return False

def test_services():
    """Tester les services mis à jour."""
    print("\n🧪 TESTS SERVICES")
    print("-" * 30)

    # Test connexion PostgreSQL
    print("🔗 Test connexion PostgreSQL...")
    try:
        from prisma import Prisma
        db = Prisma()
        import asyncio
        asyncio.run(db.connect())
        asyncio.run(db.disconnect())
        print("✅ PostgreSQL connecté")
    except Exception as e:
        print(f"❌ Erreur PostgreSQL: {e}")
        return False

    # Test connexion Redis
    print("🔗 Test connexion Redis...")
    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL"))
        r.ping()
        print("✅ Redis connecté")
    except Exception as e:
        print(f"❌ Erreur Redis: {e}")
        return False

    # Test import des services
    print("📦 Test imports services...")
    try:
        from services.cache.cache_manager import CacheManager
        from data_sources import CACHE_MANAGER
        print("✅ Services importés")
    except Exception as e:
        print(f"❌ Erreur imports: {e}")
        return False

    print("\n✅ Tests services réussis")
    return True

def create_admin_user():
    """Créer un utilisateur administrateur."""
    print("\n👤 CRÉATION UTILISATEUR ADMIN")
    print("-" * 30)

    try:
        import asyncio
        from prisma import Prisma

        async def create_admin():
            db = Prisma()
            await db.connect()
            try:
                # Vérifier si admin existe
                existing = await db.user.find_first(where={"role": "ADMIN"})
                if existing:
                    print("✅ Utilisateur admin existe déjà")
                    return True

                # Créer admin
                from api import get_password_hash
                hashed_password = get_password_hash("admin123")

                admin = await db.user.create(data={
                    "email": "admin@marotrade.ma",
                    "hashedPassword": hashed_password,
                    "companyName": "MaroTrade Intelligence",
                    "role": "ADMIN",
                    "isActive": True,
                })

                print("✅ Utilisateur admin créé")
                print("📧 Email: admin@marotrade.ma")
                print("🔑 Mot de passe: admin123")
                return True

            finally:
                await db.disconnect()

        asyncio.run(create_admin())
        return True

    except Exception as e:
        print(f"❌ Erreur création admin: {e}")
        return False

def main():
    """Fonction principale d'exécution Étape 4."""
    print("🚀 ÉTAPE 4 — MIGRATION INFRASTRUCTURE")
    print("=" * 50)
    print("PostgreSQL + Redis + Authentification + Services")
    print("=" * 50)

    # Vérifications préalables
    if not check_environment():
        return

    if not check_dependencies():
        return

    # Exécution des étapes
    steps = [
        ("Migration base de données", run_migration),
        ("Mise à jour services", update_services),
        ("Tests services", test_services),
        ("Création admin", create_admin_user),
    ]

    for step_name, step_func in steps:
        print(f"\n▶️ {step_name}...")
        if not step_func():
            print(f"\n❌ ÉCHEC à l'étape: {step_name}")
            return

    print("\n" + "=" * 50)
    print("🎉 ÉTAPE 4 TERMINÉE AVEC SUCCÈS !")
    print("=" * 50)
    print("📋 Prochaines étapes:")
    print("1. Démarrer avec: python api.py")
    print("2. Tester l'API: http://localhost:8000/docs")
    print("3. Lancer dashboard: streamlit run dashboard.py")
    print("4. Passer à l'Étape 5: Production et scaling")

if __name__ == "__main__":
    main()