@echo off
echo ==============================================
echo    Lancement de MaroTrade Intelligence
echo ==============================================

echo [1/2] Lancement du Backend (API FastAPI)...
start cmd /k "python -m pip install -r requirements.txt && title MaroTrade Backend && python api.py"

echo [2/2] Lancement du Frontend (Next.js)...
start cmd /k "cd marotrade-frontend && npm install && title MaroTrade Frontend && npm run dev"

echo.
echo Les serveurs vont demarrer dans deux nouvelles fenetres.
echo - Le backend sera accessible sur : http://localhost:8000
echo - Le frontend sera accessible sur : http://localhost:3000
echo.
pause
