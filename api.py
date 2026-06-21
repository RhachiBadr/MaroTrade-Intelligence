import hashlib
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Charge explicitement la configuration du projet avant Prisma et les services.
# override=True evite qu'une ancienne DATABASE_URL heritee du terminal soit utilisee.
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

# Import modules from the current backend
from services.cache import CacheService
from services.auth import router as auth_router
from services.auth.repository import auth_repository
from services.auth.security import AuthContext, get_current_auth
from services.i18n import localize_api_message, request_locale

try:
    from services import MarketScoringEngine, RegulatoryWatchEngine
except ImportError:
    try:
        from services.scoring import MarketScoringEngine
        from services.watch import RegulatoryWatchEngine
    except ImportError:
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
app.include_router(auth_router)


@app.exception_handler(HTTPException)
async def localized_http_exception_handler(request: Request, exc: HTTPException):
    """Translate user-facing API errors without changing endpoint behavior."""
    locale = request_locale(request.headers.get("accept-language"))
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": localize_api_message(exc.detail, locale)},
        headers=exc.headers,
    )

# --- Pydantic Models for Input ---

class ScoreRequest(BaseModel):
    hs_code: str
    product_name: str
    top_n: int = 5
    force_refresh: bool = False

class AlertsRequest(BaseModel):
    hs_code: str
    product_name: str
    target_countries: List[str]
    force_refresh: bool = False


def get_alert_value(alert, key, default=None):
    """Read an alert field from either a dictionary or a legacy object."""
    if isinstance(alert, dict):
        return alert.get(key, default)
    return getattr(alert, key, default)


def _alert_text_value(value, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item)
    return str(value)


def _alert_date_value(value) -> str:
    if value is None:
        return ""
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _alert_number_value(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _alerts_cache_key(req: AlertsRequest) -> str:
    payload = {
        "presentation_version": 3,
        "hs_code": req.hs_code.strip(),
        "product_name": req.product_name.strip().lower(),
        "target_countries": sorted(country.strip().upper() for country in req.target_countries),
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return f"api:alerts:{digest}"


def _redis_health() -> Dict[str, Any]:
    if not cache_service.redis:
        return {"connected": False, "backend": "memory"}
    try:
        cache_service.redis.ping()
        return {"connected": True, "backend": "redis"}
    except Exception as exc:
        return {"connected": False, "backend": "redis", "error": str(exc)}


def _nlp_health() -> Dict[str, Any]:
    nlp_analyzer = getattr(watch_engine, "nlp_analyzer", None) if watch_engine else None
    opensource = getattr(nlp_analyzer, "opensource_analyzer", None) if nlp_analyzer else None
    classifier = getattr(opensource, "classifier", None) if opensource else None

    return {
        "available": bool(nlp_analyzer),
        "lazy": bool(
            watch_engine
            and getattr(watch_engine, "use_nlp", False)
            and not getattr(watch_engine, "_nlp_initialization_attempted", False)
        ),
        "opensource_analyzer": bool(opensource),
        "local_classifier": bool(getattr(classifier, "local_model_available", False)),
        "model_path": str(getattr(classifier, "model_path", "")) if classifier else "",
        "fallback": "zero-shot/rules" if not getattr(classifier, "local_model_available", False) else None,
    }

# --- Global Engine Instances (Load once) ---

scoring_engine = None
watch_engine = None
cache_service = CacheService()
ALERTS_CACHE_TTL_SECONDS = int(os.getenv("ALERTS_CACHE_TTL_SECONDS", "900"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scoring_engine, watch_engine
    if MarketScoringEngine:
        print("Initialisation du MarketScoringEngine...")
        scoring_engine = MarketScoringEngine()
    if RegulatoryWatchEngine:
        print("Initialisation du RegulatoryWatchEngine...")
        watch_engine = RegulatoryWatchEngine(
            use_nlp=os.getenv("WATCH_NLP_ENABLED", "true").lower() == "true",
            lazy_nlp=os.getenv("WATCH_NLP_LAZY_LOAD", "true").lower() == "true",
        )
    await auth_repository.connect()
    if not auth_repository.available:
        print(f"Authentification DB indisponible: {auth_repository.error}")
    yield
    await auth_repository.disconnect()
    print("Arrêt de l'API...")

app.router.lifespan_context = lifespan

# --- API Endpoints ---

@app.post("/api/score")
async def get_score(req: ScoreRequest, auth: AuthContext = Depends(get_current_auth)):
    if not scoring_engine:
        raise HTTPException(status_code=500, detail="Moteur de scoring non chargé.")
    
    # Exécution du scoring v2.0
    try:
        results = scoring_engine.run(
            req.product_name,
            req.hs_code,
            top_n=req.top_n,
            force_refresh=req.force_refresh,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    response_data = []
    
    for r in results:
        # Simplification et conformation à l'interface MarketResult TypeScript
        dims = []
        for d in r.dimensions:
            dims.append({
                "nom": d.nom,
                "score": float(d.score),
                "poids": float(d.poids),
                "contribution": float(d.contribution),
                "detail": {k: str(v) for k, v in d.detail.items()},
                "interpretation": str(d.interpretation)
            })
            
        acc_info = r.accord_info.copy()
        
        response_data.append({
            "rank": int(r.rank),
            "country": {
                "code": r.country_code,
                "name": r.country_name,
                "flag": r.country_code
            },
            "score_final": float(r.score_final),
            "score_weighted": float(r.score_weighted),
            "score_xgboost": float(r.score_xgboost),
            "score_ml_v6": float(r.score_ml_v6) if r.score_ml_v6 is not None else None,
            "scoring_method": str(getattr(r, "scoring_method", "legacy_weighted_xgboost")),
            "v6_features_used": list(getattr(r, "v6_features_used", [])),
            "v6_explanation": str(getattr(r, "v6_explanation", "")),
            "v6_strengths": list(getattr(r, "v6_strengths", [])),
            "v6_risks": list(getattr(r, "v6_risks", [])),
            "v6_feature_snapshot": dict(getattr(r, "v6_feature_snapshot", {})),
            "data_freshness": dict(getattr(r, "data_freshness", {})),
            "dimensions": dims,
            "shap_values": {str(k): float(v) for k, v in r.shap_values.items()},
            "top_atouts": list(r.top_atouts),
            "top_risques": list(r.top_risques),
            "accord_info": acc_info,
            "logistique": {
                "distance_km": float(r.logistique_info.get('distance_km', 0)),
                "lpi": float(r.logistique_info.get('lpi', 0)),
                "cout_conteneur": float(r.logistique_info.get('cout_conteneur_usd', 0))
            }
        })
    await auth_repository.save_workspace_analysis(
        user_id=auth.user_id,
        organization_id=auth.organization_id,
        product_name=req.product_name,
        hs_code=req.hs_code,
        top_n=req.top_n,
        results=response_data,
    )
    return response_data


@app.get("/api/me/analyses")
async def get_my_analyses(limit: int = 30, auth: AuthContext = Depends(get_current_auth)):
    analyses = await auth_repository.list_workspace_analyses(auth.organization_id, take=limit)
    return [
        {
            "id": analysis.id,
            "product_name": analysis.productName,
            "hs_code": analysis.hsCode,
            "top_n": analysis.topN,
            "results": analysis.results,
            "created_at": analysis.createdAt.isoformat(),
        }
        for analysis in analyses
    ]


@app.delete("/api/me/analyses/{analysis_id}", status_code=204)
async def delete_my_analysis(analysis_id: str, auth: AuthContext = Depends(get_current_auth)):
    if not await auth_repository.delete_workspace_analysis(analysis_id, auth.organization_id):
        raise HTTPException(status_code=404, detail="Analyse introuvable dans votre espace PME.")


@app.post("/api/alerts")
def get_alerts(req: AlertsRequest):
    if not watch_engine:
        raise HTTPException(status_code=500, detail="Moteur de veille non chargé.")
        
    cache_key = _alerts_cache_key(req)
    if req.force_refresh:
        cache_service.delete(cache_key)
    else:
        cached_response = cache_service.get(cache_key)
        if cached_response is not None:
            return cached_response

    try:
        alerts = watch_engine.run(req.hs_code, req.product_name, req.target_countries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Échec de la veille réglementaire : {e}")
        
    # Transformation
    response_data = []
    for a in alerts:
        response_data.append({
            "id": _alert_text_value(get_alert_value(a, "id", "")),
            "titre": _alert_text_value(
                get_alert_value(a, "titre_fr") or get_alert_value(a, "titre") or get_alert_value(a, "title", "")
            ),
            "niveau": _alert_text_value(get_alert_value(a, "niveau") or get_alert_value(a, "level", "INFO")),
            "source": _alert_text_value(get_alert_value(a, "source", "")),
            "pays": _alert_text_value(get_alert_value(a, "pays") or get_alert_value(a, "country", "")),
            "pays_nom": _alert_text_value(
                get_alert_value(a, "pays_nom") or get_alert_value(a, "pays") or get_alert_value(a, "country", "")
            ),
            "date": _alert_date_value(get_alert_value(a, "date", "")),
            "resume": _alert_text_value(
                get_alert_value(a, "resume_fr") or get_alert_value(a, "resume") or get_alert_value(a, "summary", "")
            ),
            "action": _alert_text_value(get_alert_value(a, "action") or get_alert_value(a, "action_requise", "")),
            "url": _alert_text_value(get_alert_value(a, "url", "")),
            "score_impact": _alert_number_value(
                get_alert_value(a, "score_impact", get_alert_value(a, "impact_score", 0))
            ),
            "delai_jours": int(_alert_number_value(get_alert_value(a, "delai_jours", 0))),
            "llm_enhanced": bool(
                get_alert_value(
                    a,
                    "llm_enhanced",
                    get_alert_value(a, "llm_analyzed", get_alert_value(a, "nlp_enhanced", False)),
                )
            ),
            "confidence": _alert_number_value(
                get_alert_value(a, "confidence", get_alert_value(a, "confiance", 0))
            ),
            "impact_score": _alert_number_value(
                get_alert_value(a, "impact_score", get_alert_value(a, "score_impact", 0))
            ),
            "entities": get_alert_value(a, "entities", {}) or {},
            "keywords": get_alert_value(a, "keywords", []) or [],
            "reasoning": _alert_text_value(get_alert_value(a, "reasoning", "")),
            "resume_fr": _alert_text_value(
                get_alert_value(a, "resume_fr") or get_alert_value(a, "resume") or get_alert_value(a, "summary", "")
            ),
            "brief_executif": _alert_text_value(
                get_alert_value(a, "brief_executif", get_alert_value(a, "summary", get_alert_value(a, "resume_fr", "")))
            ),
            "nlp_enhanced": bool(get_alert_value(a, "nlp_enhanced", False)),
            "raw_nlp_level": _alert_text_value(get_alert_value(a, "raw_nlp_level", "")),
            "model_nlp_level": _alert_text_value(get_alert_value(a, "model_nlp_level", "")),
            "classification_basis": _alert_text_value(get_alert_value(a, "classification_basis", "")),
            "calibration_reason": _alert_text_value(get_alert_value(a, "calibration_reason", "")),
            "business_explanation": _alert_text_value(get_alert_value(a, "business_explanation", "")),
            "category": _alert_text_value(get_alert_value(a, "category", "")),
            "classification": _alert_text_value(get_alert_value(a, "classification", "")),
            "origin": _alert_text_value(get_alert_value(a, "origin", "")),
            "relevance": _alert_number_value(get_alert_value(a, "relevance", 0)),
            "product_match": bool(get_alert_value(a, "product_match", False)),
        })
        
    cache_service.set(cache_key, response_data, ttl=ALERTS_CACHE_TTL_SECONDS)
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


@app.get("/api/health")
def api_health():
    redis_status = _redis_health()
    nlp_status = _nlp_health()
    scoring_loaded = scoring_engine is not None
    watch_loaded = watch_engine is not None

    degraded = (
        not scoring_loaded
        or not watch_loaded
        or not redis_status.get("connected")
        or not nlp_status.get("local_classifier")
    )

    return {
        "status": "degraded" if degraded else "ok",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "services": {
            "redis": redis_status,
            "scoring_engine": {"loaded": scoring_loaded},
            "regulatory_watch": {"loaded": watch_loaded},
            "nlp": nlp_status,
        },
        "config": {
            "alerts_cache_ttl_seconds": ALERTS_CACHE_TTL_SECONDS,
        },
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
