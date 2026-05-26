@echo off
REM MaroTrade Intelligence - Démarrage Étape 4
REM Infrastructure PostgreSQL + Redis + Authentification

echo 🚀 MAROTRADE INTELLIGENCE - ÉTAPE 4
echo ======================================
echo Infrastructure Production
echo PostgreSQL + Redis + Authentification
echo ======================================

REM Vérifier si docker.env existe
if not exist "docker.env" (
    echo ❌ Fichier docker.env manquant
    echo 📋 Copiez .env.example vers docker.env et configurez les variables
    pause
    exit /b 1
)

echo ✅ Configuration trouvée

REM Démarrer les services externes
echo 🔄 Démarrage PostgreSQL et Redis...
docker-compose up -d postgres redis

echo ⏳ Attente initialisation services (30s)...
timeout /t 30 /nobreak > nul

REM Vérifier les services
echo 🔍 Vérification services...
docker-compose ps

REM Installer dépendances Python
echo 📦 Installation dépendances Python...
pip install -r requirements.txt

REM Générer client Prisma
echo 🔧 Génération client Prisma...
prisma generate

REM Exécuter vérification pré-migration
echo 🔍 Vérification environnement...
python scripts/check_etape4.py

if %errorlevel% neq 0 (
    echo ❌ Vérification échouée - corrigez les erreurs
    pause
    exit /b 1
)

REM Exécuter migration complète
echo 🗄️ Migration base de données...
python scripts/run_etape4.py

if %errorlevel% neq 0 (
    echo ❌ Migration échouée
    pause
    exit /b 1
)

REM Tests de validation
echo 🧪 Tests de validation...
python scripts/test_etape4.py

if %errorlevel% neq 0 (
    echo ❌ Tests échoués - vérifiez les logs
    pause
    exit /b 1
)

echo.
echo 🎉 ÉTAPE 4 RÉUSSIE !
echo =====================
echo.
echo Services disponibles:
echo 🔗 API FastAPI: http://localhost:8000
echo 🔗 Dashboard: streamlit run dashboard.py
echo 🔗 Frontend: cd marotrade-frontend && npm run dev
echo.
echo Utilisateur admin:
echo 📧 admin@marotrade.ma
echo 🔑 admin123
echo.
echo 📚 Documentation: ETAPE4_README.md
echo.

pause