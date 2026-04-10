import os
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import modules from the current backend
try:
    from scoring_engine import MarketScoringEngine
except ImportError:
    print("ATTENTION: scoring_engine.py introuvable ou erreur d'importation (e.g. xgboost manquant).")
    MarketScoringEngine = None

try:
    from regulatory_watch import RegulatoryWatchEngine
except ImportError:
    print("ATTENTION: regulatory_watch.py introuvable ou erreur d'importation.")
    RegulatoryWatchEngine = None

app = FastAPI(
    title="MaroTrade Intelligence API",
    description="Backend API pour le Frontend Next.js MaroTrade Intelligence",
    version="1.0.0"
)

# Configuration CORS pour autoriser Next.js (par défaut sur 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Input ---

class ScoreRequest(BaseModel):
    hs_code: str
    product_name: str
    top_n: int = 5

class AlertsRequest(BaseModel):
    hs_code: str
    product_name: str
    target_countries: List[str]

# --- Global Engine Instances (Load once) ---

scoring_engine = None
watch_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scoring_engine, watch_engine
    if MarketScoringEngine:
        print("Initialisation du MarketScoringEngine...")
        scoring_engine = MarketScoringEngine()
    if RegulatoryWatchEngine:
        print("Initialisation du RegulatoryWatchEngine...")
        watch_engine = RegulatoryWatchEngine()
    yield
    print("Arrêt de l'API...")

app.router.lifespan_context = lifespan

# --- API Endpoints ---

@app.post("/api/score")
def get_score(req: ScoreRequest):
    if not scoring_engine:
        raise HTTPException(status_code=500, detail="Moteur de scoring non chargé.")
    
    # Exécution du scoring
    try:
        results = scoring_engine.score_markets(req.hs_code, req.product_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Transformation en JSON pour le frontend
    # Les datatypes Python customisés (XGBoost, Numpy, etc.) doivent être castés en natifs
    response_data = []
    
    # Limiter aux N meilleurs  (la fonction score_markets trie déjà)
    top_results = results[:req.top_n]
    
    for r in top_results:
        # Simplification et conformation à l'interface MarketResult TypeScript
        dims = []
        for nom, data in r.dimensions.items():
            dims.append({
                "nom": nom,
                "score": float(data['score']),
                "poids": float(data['poids']),
                "contribution": float(data['contribution']),
                "detail": {k: str(v) for k, v in data.get('detail', {}).items()},
                "interpretation": str(data.get('interpretation', ''))
            })
            
        acc_info = r.accord_info.copy()
        
        # Le forecast (C04) n'est pas complètement intégré par défaut dans scoring_engine,
        # mais la structure Data_Sources peut contenir le dynamique.
        # Ici on retransmet juste l'interface de base.
        
        response_data.append({
            "rank": int(r.rank),
            "country": {
                "code": r.country_code,
                "name": r.country_name,
                "flag": r.country_flag
            },
            "score_final": float(r.score_final),
            "score_weighted": float(r.score_weighted),
            "score_xgboost": float(r.score_xgboost),
            "dimensions": dims,
            "shap_values": {str(k): float(v) for k, v in r.shap_values.items()},
            "top_atouts": list(r.top_atouts),
            "top_risques": list(r.top_risques),
            "accord_info": acc_info,
            "logistique": {
                "distance_km": float(r.logistique.get('distance_km', 0)),
                "lpi": float(r.logistique.get('lpi', 0)),
                "cout_conteneur": float(r.logistique.get('cout_conteneur', 0))
            }
        })
        
    return response_data


@app.post("/api/alerts")
def get_alerts(req: AlertsRequest):
    if not watch_engine:
        raise HTTPException(status_code=500, detail="Moteur de veille non chargé.")
        
    try:
        alerts = watch_engine.run(req.hs_code, req.product_name, req.target_countries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Transformation
    response_data = []
    for a in alerts:
        response_data.append({
            "id": a.id,
            "titre": a.titre_fr or a.title,
            "niveau": a.level,
            "source": a.source,
            "pays": a.country,
            "pays_nom": a.country,  # On pourrait faire un mapper
            "date": a.date.isoformat() if hasattr(a.date, 'isoformat') else str(a.date),
            "resume": a.resume_fr or a.summary,
            "action": a.action_requise or "",
            "url": a.url,
            "score_impact": int(a.impact_score),
            "llm_enhanced": getattr(a, 'llm_analyzed', False)
        })
        
    return response_data


@app.get("/api/forecast")
def get_forecast(hs_code: str, country: str):
    # Endpoint provisoire pour forecast (prophet)
    # Dans la doc, on utilise encore Prophet, ce qui pourrait requérir le module 'market_forecaster.py' 
    # Pour l'instant on retourne une erreur polie pour triggler le FALLBACK MOCK du front 
    # (qui a été codé pour intercepter les erreurs 500 et afficher la courbe)
    raise HTTPException(status_code=501, detail="Endpoint Forecast en cours de construction.")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "MaroTrade API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
