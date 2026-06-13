"""
scoring_engine.py — Moteur de scoring MaroTrade Intelligence v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Améliorations v2.0 :
  ✦ 7 dimensions (vs 6) — ajout "Tendance & Demande" (Google Trends + ITC prix)
  ✦ Export Readiness Pre-check — avertissements certifications manquantes
  ✦ Simulateur de rentabilité intégré (marge nette estimée par marché)
  ✦ Poids adaptatifs selon le type de produit (terroir / artisanat / agroalimentaire)
  ✦ Textes SHAP en langage naturel multilingue (FR/EN/AR)
  ✦ Bonus contextuel : MRE + accord commercial → booster combiné
  ✦ Alerte risque de paiement intégrée dans les résultats
  ✦ Score de confiance par pays (qualité des données disponibles)
  ✦ Logging structuré remplace les print
  ✦ Pipeline asynchrone optionnel pour batch analysis
"""

import numpy as np
import pandas as pd
import logging
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import warnings
warnings.filterwarnings("ignore")

import joblib
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
import shap

from data_sources import (
    get_trade_data, get_accord_score,
    get_diaspora, get_logistique, get_trends, get_market_context,
    ACCORDS_MAROC, PAYS_NOM, fetch_itc_price, _WB_FALLBACK,
)
from external_api_manager import api_manager
from dynamic_growth import enrich_with_growth, interpret_growth, growth_label

logger = logging.getLogger("marotrade.scoring")


ROOT_DIR = Path(__file__).resolve().parents[2]
V6_MODEL_PATH = ROOT_DIR / "artifacts" / "market_ranking_model_v6.joblib"
V6_RESULTS_PATH = ROOT_DIR / "artifacts" / "benchmark_phase1_v6_results.json"


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION DU MOTEUR
# ═══════════════════════════════════════════════════════════════

# Poids des 7 dimensions — configuration par défaut (terroir/artisanat premium)
WEIGHTS_DEFAULT = {
    "marche":    0.26,   # Taille + croissance
    "accord":    0.22,   # Accord commercial
    "business":  0.16,   # Facilité des affaires
    "stabilite": 0.11,   # Stabilité & risque pays
    "diaspora":  0.10,   # Réseau MRE
    "logistique":0.09,   # Logistique & transport
    "tendance":  0.06,   # Google Trends + ITC prix (NOUVEAU)
}

# Profils de poids par type de produit
WEIGHTS_PROFILES = {
    "terroir_premium": {  # Huile d'argan, safran, dattes premium
        "marche": 0.22, "accord": 0.20, "business": 0.14,
        "stabilite": 0.10, "diaspora": 0.15, "logistique": 0.09, "tendance": 0.10,
    },
    "artisanat": {  # Tapis, zellige, poterie
        "marche": 0.24, "accord": 0.20, "business": 0.15,
        "stabilite": 0.10, "diaspora": 0.14, "logistique": 0.10, "tendance": 0.07,
    },
    "agroalimentaire": {  # Sardines, conserves, épices bulk
        "marche": 0.30, "accord": 0.25, "business": 0.17,
        "stabilite": 0.12, "diaspora": 0.06, "logistique": 0.07, "tendance": 0.03,
    },
    "default": WEIGHTS_DEFAULT,
}

# Mapping HS → profil produit
_HS_PROFILES: Dict[str, str] = {
    "151590":   "terroir_premium",   # Huile d'argan
    "09102010": "terroir_premium",   # Safran
    "080410":   "terroir_premium",   # Dattes premium
    "570110":   "artisanat",         # Tapis berbère
    "691010":   "artisanat",         # Zellige
    "160413":   "agroalimentaire",   # Sardines
    "090920":   "agroalimentaire",   # Cumin/épices bulk
}

# Ratio ensemble
ENSEMBLE_RATIO = {"weighted": 0.60, "xgboost": 0.40}

# Seuils pour les catégories de score
SCORE_THRESHOLDS = {
    "excellent": 80,
    "bon":       65,
    "moyen":     50,
    "faible":    35,
}

# Noms des features pour explications
FEATURE_LABELS = {
    "vol_norm":         "Volume du marché",
    "growth_norm":      "Croissance des imports",
    "prix_norm":        "Prix pratiqué (USD/kg)",
    "accord_norm":      "Qualité de l'accord commercial",
    "droits_norm":      "Niveau des droits de douane",
    "ease_biz_norm":    "Facilité à faire des affaires",
    "rule_law_norm":    "État de droit",
    "stability_norm":   "Stabilité politique",
    "risk_norm":        "Risque pays global",
    "diaspora_norm":    "Taille diaspora MRE",
    "transferts_norm":  "Transferts financiers MRE",
    "distance_norm":    "Proximité géographique",
    "lpi_norm":         "Performance logistique",
    "cout_norm":        "Coût du transport",
    "tendance_norm":    "Tendance demande consommateur",
}


# ═══════════════════════════════════════════════════════════════
# STRUCTURES DE DONNÉES
# ═══════════════════════════════════════════════════════════════

@dataclass
class DimensionScore:
    """Score d'une dimension avec détail et interprétation."""
    nom: str
    score: float
    poids: float
    contribution: float
    detail: dict
    interpretation: str
    emoji: str = ""

@dataclass
class RentabiliteEstimee:
    """Simulation de rentabilité export pour un marché."""
    marche: str
    prix_fob_usd_kg: float
    cout_production_usd_kg: float
    cout_fret_usd_kg: float
    droits_douane_pct: float
    marge_brute_pct: float
    marge_nette_pct: float
    point_mort_volume_kg: int
    note: str

@dataclass
class MarketResult:
    """Résultat complet pour un marché d'export."""
    rank: int
    country_code: str
    country_name: str
    score_final: float
    score_weighted: float
    score_xgboost: float
    score_label: str               # "Excellent" / "Bon" / "Moyen" / "Faible"
    confidence: float              # 0–100 : qualité des données disponibles
    dimensions: List[DimensionScore]
    shap_values: dict
    top_atouts: List[str]
    top_risques: List[str]
    accord_info: dict
    logistique_info: dict
    trends_info: dict
    rentabilite: Optional[RentabiliteEstimee]
    certifications_requises: List[str]
    payment_alerte: str            # Alerte sur le mode de paiement recommandé
    shap_narrative: str            # Explication narrative du score en langage naturel
    score_ml_v6: Optional[float] = None
    scoring_method: str = "legacy_weighted_xgboost"
    v6_features_used: List[str] = field(default_factory=list)
    v6_explanation: str = ""
    v6_strengths: List[str] = field(default_factory=list)
    v6_risks: List[str] = field(default_factory=list)
    v6_feature_snapshot: dict = field(default_factory=dict)
    data_freshness: dict = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
# MOTEUR PRINCIPAL
# ═══════════════════════════════════════════════════════════════

class MarketScoringEngine:
    """
    Moteur de scoring des marchés export pour PME marocaines.
    Architecture : Score pondéré (60%) + XGBoost (40%) + SHAP explicabilité.
    v2.0 : 7 dimensions, simulation rentabilité, Google Trends, poids adaptatifs.
    """

    def __init__(self):
        self.scaler        = MinMaxScaler()
        self.xgb_model     = None
        self.explainer     = None
        self._is_trained   = False
        self._weights      = WEIGHTS_DEFAULT
        self._hs_code      = ""
        self._product_name = ""
        self.v6_model_bundle = None
        self.v6_model = None
        self.v6_preprocessor = None
        self.v6_features: List[str] = []
        self.v6_target = ""
        self.v6_available = False
        self._last_v6_feature_matrix: Optional[pd.DataFrame] = None
        self.wb_indicators = pd.DataFrame()
        self.ocde_risk = pd.DataFrame()
        self._load_v6_model()
        self._load_v6_reference_data()

    def _load_v6_model(self) -> None:
        """Load the offline benchmark v6 model if the artifact is available."""
        if not V6_MODEL_PATH.exists():
            logger.warning("V6 market ranking model not found, using legacy scoring only: %s", V6_MODEL_PATH)
            return

        try:
            self.v6_model_bundle = joblib.load(V6_MODEL_PATH)
            self.v6_model = self.v6_model_bundle.get("model")
            self.v6_preprocessor = self.v6_model_bundle.get("preprocessor")
            self.v6_features = list(self.v6_model_bundle.get("features", []))
            self.v6_target = str(self.v6_model_bundle.get("target", "market_attractiveness_target"))
            self.v6_available = self.v6_model is not None and bool(self.v6_features)
            if self.v6_available:
                logger.info("Loaded v6 market ranking model: %s", V6_MODEL_PATH)
            else:
                logger.warning("V6 model artifact is incomplete, using legacy scoring only")
        except Exception as exc:
            logger.exception("Failed to load v6 market ranking model: %s", exc)
            self.v6_available = False

    def _load_v6_reference_data(self) -> None:
        """Load compact benchmark reference tables used by v6 features."""
        data_dir = ROOT_DIR / "data" / "raw"
        wb_path = data_dir / "worldbank_indicators.csv"
        ocde_path = data_dir / "ocde_risk.csv"

        try:
            if wb_path.exists():
                wb = pd.read_csv(wb_path)
                code_col = "iso3" if "iso3" in wb.columns else "Unnamed: 0"
                wb["country_code"] = wb[code_col].astype(str)
                self.wb_indicators = wb.rename(columns={
                    "gdp_per_capita": "wb_gdp_per_capita",
                    "imports_pct_gdp": "wb_imports_pct_gdp",
                    "trade_pct_gdp": "wb_trade_pct_gdp",
                })
        except Exception as exc:
            logger.warning("Could not load World Bank reference data for v6 scoring: %s", exc)
            self.wb_indicators = pd.DataFrame()

        try:
            if ocde_path.exists():
                ocde = pd.read_csv(ocde_path)
                code_col = "iso3" if "iso3" in ocde.columns else "Unnamed: 0"
                ocde["country_code"] = ocde[code_col].astype(str)
                if "ocde_risk_score" not in ocde.columns:
                    if "category" in ocde.columns:
                        ocde["ocde_risk_score"] = ocde["category"]
                    elif "score" in ocde.columns:
                        ocde["ocde_risk_score"] = (100 - ocde["score"]) / 20
                self.ocde_risk = ocde[["country_code", "ocde_risk_score"]].drop_duplicates("country_code")
        except Exception as exc:
            logger.warning("Could not load OCDE reference data for v6 scoring: %s", exc)
            self.ocde_risk = pd.DataFrame()

    def _lookup_wb_indicator(self, country_code: str, column: str, default: float = 0.0) -> float:
        if self.wb_indicators.empty or column not in self.wb_indicators.columns:
            return default
        row = self.wb_indicators[self.wb_indicators["country_code"] == country_code]
        if row.empty:
            return default
        value = pd.to_numeric(row.iloc[0].get(column), errors="coerce")
        return float(default if pd.isna(value) else value)

    def _lookup_ocde_risk(self, country_code: str, fallback: float = 3.0) -> float:
        if self.ocde_risk.empty:
            return fallback
        row = self.ocde_risk[self.ocde_risk["country_code"] == country_code]
        if row.empty:
            return fallback
        value = pd.to_numeric(row.iloc[0].get("ocde_risk_score"), errors="coerce")
        return float(fallback if pd.isna(value) else value)

    def _get_wb_scores_fast(self, country_code: str) -> dict:
        """Return local World Bank governance fallback without blocking API scoring."""
        return _WB_FALLBACK.get(country_code, {
            "ease_business": 55.0,
            "political_stability": 40.0,
            "rule_of_law": 50.0,
            "regulatory_quality": 50.0,
        })

    def build_v6_feature_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build the 17 benchmark v6 features from the runtime market matrix.
        Missing historical lags are approximated from current value and growth.
        """
        features_df = pd.DataFrame(index=df.index)
        total_value = float(df["value_usd"].sum()) if "value_usd" in df else 0.0
        growth = pd.to_numeric(df.get("growth_pct", 0.0), errors="coerce").fillna(0.0) / 100.0
        value = pd.to_numeric(df.get("value_usd", 0.0), errors="coerce").fillna(0.0).clip(lower=0.0)
        price = pd.to_numeric(df.get("price_usd_kg", 0.0), errors="coerce").fillna(0.0).clip(lower=0.0)

        safe_growth = growth.replace(-1.0, np.nan)
        lag1 = (value / (1.0 + safe_growth)).replace([np.inf, -np.inf], np.nan).fillna(value)
        lag2 = (lag1 / (1.0 + safe_growth)).replace([np.inf, -np.inf], np.nan).fillna(lag1)
        lag3 = (lag2 / (1.0 + safe_growth)).replace([np.inf, -np.inf], np.nan).fillna(lag2)
        ma3 = pd.concat([lag1, lag2, lag3], axis=1).mean(axis=1)
        std3 = pd.concat([lag1, lag2, lag3], axis=1).std(axis=1).fillna(0.0)

        features_df["log_value_usd"] = np.log1p(value)
        features_df["log_lag1"] = np.log1p(lag1.clip(lower=0.0))
        features_df["log_ma3"] = np.log1p(ma3.clip(lower=0.0))
        features_df["std3"] = std3
        features_df["growth_lag1"] = growth * 100.0
        features_df["log_return_lag1"] = np.log1p(growth.clip(lower=-0.95)) * 100.0
        features_df["price_usd_kg"] = price
        features_df["market_share"] = value / total_value if total_value > 0 else 0.0
        features_df["cagr_3y"] = ((value / lag3.replace(0, np.nan)) ** (1 / 3) - 1).replace([np.inf, -np.inf], np.nan).fillna(0.0)

        accord_scores, droits = [], []
        wb_gdp, wb_imports, wb_available = [], [], []
        ocde_scores, distances, trend_scores = [], [], []

        for _, row in df.iterrows():
            code = str(row.get("country_code", ""))
            accord = get_accord_score(code)
            logist = get_logistique(code)
            trends = get_trends(code, self._hs_code)

            accord_type = accord.get("type", "")
            accord_scores.append(100.0 if accord_type == "ALE" else 50.0 if accord_type == "PREF" else 0.0)
            droits.append(float(accord.get("droits", 15.0) or 0.0))

            gdp = self._lookup_wb_indicator(code, "wb_gdp_per_capita", default=0.0)
            imports = self._lookup_wb_indicator(code, "wb_imports_pct_gdp", default=0.0)
            wb_gdp.append(gdp)
            wb_imports.append(imports)
            wb_available.append(1 if gdp > 0 or imports > 0 else 0)

            ocde_scores.append(self._lookup_ocde_risk(code, fallback=float(logist.get("risk_category", 3) or 3)))
            distances.append(float(logist.get("distance_km", row.get("distance_km", 5000)) or 5000))
            trend_scores.append(float(trends.get("trend_score", row.get("tendance", 50)) or 50))

        features_df["accord_score"] = accord_scores
        features_df["droits"] = droits
        features_df["wb_gdp_per_capita"] = wb_gdp
        features_df["wb_imports_pct_gdp"] = wb_imports
        features_df["wb_available"] = wb_available
        features_df["ocde_risk_score"] = ocde_scores
        features_df["distance_km"] = distances
        features_df["trend_score"] = trend_scores

        for feature in self.v6_features:
            if feature not in features_df.columns:
                features_df[feature] = 0.0

        return features_df[self.v6_features].replace([np.inf, -np.inf], np.nan)

    def predict_v6_scores(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """Predict normalized market attractiveness scores with the v6 model."""
        if not self.v6_available:
            return None
        try:
            X = self.build_v6_feature_matrix(df)
            self._last_v6_feature_matrix = X.copy()
            X_model = self.v6_preprocessor.transform(X) if self.v6_preprocessor is not None else X
            raw_scores = np.asarray(self.v6_model.predict(X_model), dtype=float)
            if len(raw_scores) == 0:
                return None
            min_score = float(np.nanmin(raw_scores))
            max_score = float(np.nanmax(raw_scores))
            if np.isclose(max_score, min_score):
                return np.full_like(raw_scores, 50.0, dtype=float)
            return (raw_scores - min_score) / (max_score - min_score) * 100.0
        except Exception as exc:
            logger.exception("V6 market ranking inference failed, using legacy scoring: %s", exc)
            self._last_v6_feature_matrix = None
            return None

    def calibrate_v6_scores_for_pme(self, scores: np.ndarray, v6_features: pd.DataFrame) -> np.ndarray:
        """
        Apply a conservative business calibration for Moroccan SMEs.
        The model remains the primary ranker, then the score is adjusted for
        actionable export readiness: market size, risk, distance, tariffs, and data quality.
        """
        if v6_features is None or v6_features.empty:
            return scores

        calibrated = []
        for score, (_, row) in zip(scores, v6_features.iterrows()):
            value = float(row.get("log_value_usd", 0.0) or 0.0)
            import_value = np.expm1(value)
            distance = float(row.get("distance_km", 5000.0) or 5000.0)
            droits = float(row.get("droits", 8.0) or 0.0)
            ocde = float(row.get("ocde_risk_score", 3.0) or 3.0)
            trend = float(row.get("trend_score", 50.0) or 50.0)
            wb_available = float(row.get("wb_available", 0.0) or 0.0)
            accord = float(row.get("accord_score", 0.0) or 0.0)
            growth = float(row.get("growth_lag1", 0.0) or 0.0)

            business_factor = 1.0

            if import_value < 2_000_000:
                business_factor -= 0.22
            elif import_value < 5_000_000:
                business_factor -= 0.10
            elif import_value >= 15_000_000:
                business_factor += 0.06

            if ocde >= 5:
                business_factor -= 0.22
            elif ocde >= 3:
                business_factor -= 0.08
            elif ocde <= 1:
                business_factor += 0.04

            if distance > 7_000:
                business_factor -= 0.12
            elif distance > 4_500:
                business_factor -= 0.06
            elif distance <= 2_500:
                business_factor += 0.04

            if droits > 8:
                business_factor -= 0.12
            elif droits > 0:
                business_factor -= 0.04
            elif accord >= 100:
                business_factor += 0.04

            if trend < 40:
                business_factor -= 0.06
            elif trend >= 65:
                business_factor += 0.03

            if growth >= 8:
                business_factor += 0.03
            elif growth < 0:
                business_factor -= 0.06

            if wb_available <= 0:
                business_factor -= 0.07

            calibrated.append(float(score) * max(0.55, min(1.15, business_factor)))

        calibrated = np.asarray(calibrated, dtype=float)
        max_score = float(np.nanmax(calibrated)) if len(calibrated) else 0.0
        if max_score > 0:
            calibrated = calibrated / max_score * 100.0
        return calibrated

    def build_v6_explanation(self, row: pd.Series, v6_row: pd.Series, score: float) -> dict:
        """Build business-readable explanations aligned with the v6 ranking features."""
        value_usd = float(row.get("value_usd", 0.0) or 0.0)
        growth = float(v6_row.get("growth_lag1", row.get("growth_pct", 0.0)) or 0.0)
        market_share = float(v6_row.get("market_share", 0.0) or 0.0) * 100.0
        cagr = float(v6_row.get("cagr_3y", 0.0) or 0.0) * 100.0
        price = float(v6_row.get("price_usd_kg", row.get("price_usd_kg", 0.0)) or 0.0)
        accord_score = float(v6_row.get("accord_score", 0.0) or 0.0)
        droits = float(v6_row.get("droits", 0.0) or 0.0)
        ocde = float(v6_row.get("ocde_risk_score", row.get("risk_category", 3.0)) or 3.0)
        distance = float(v6_row.get("distance_km", row.get("distance_km", 0.0)) or 0.0)
        trend = float(v6_row.get("trend_score", row.get("tendance", 50.0)) or 50.0)
        gdp = float(v6_row.get("wb_gdp_per_capita", 0.0) or 0.0)
        imports_gdp = float(v6_row.get("wb_imports_pct_gdp", 0.0) or 0.0)
        wb_available = int(float(v6_row.get("wb_available", 0.0) or 0.0))

        strengths = []
        risks = []

        if value_usd >= 5_000_000:
            strengths.append(f"Demande import significative ({value_usd / 1_000_000:.1f}M USD).")
        elif value_usd < 1_000_000:
            risks.append(f"Marché encore limité en volume ({value_usd / 1_000_000:.1f}M USD).")

        if growth >= 8:
            strengths.append(f"Dynamique récente favorable (+{growth:.1f}% estimée).")
        elif growth < 0:
            risks.append(f"Dynamique récente négative ({growth:.1f}%).")

        if cagr >= 5:
            strengths.append(f"Tendance 3 ans positive (CAGR {cagr:.1f}%).")
        elif cagr < -3:
            risks.append(f"Tendance 3 ans en recul (CAGR {cagr:.1f}%).")

        if accord_score >= 100 or droits <= 0:
            strengths.append("Accord commercial favorable avec droits de douane nuls.")
        elif droits > 10:
            risks.append(f"Droits de douane élevés ({droits:.1f}%).")
        elif droits > 0:
            risks.append(f"Droits de douane à intégrer dans la marge ({droits:.1f}%).")

        if ocde <= 2:
            strengths.append(f"Risque pays faible selon le profil OCDE ({ocde:.0f}).")
        elif ocde >= 5:
            risks.append(f"Risque pays élevé selon le profil OCDE ({ocde:.0f}).")

        if distance and distance <= 2_500:
            strengths.append(f"Proximité logistique favorable ({distance:,.0f} km).")
        elif distance >= 5_000:
            risks.append(f"Distance logistique importante ({distance:,.0f} km).")

        if trend >= 65:
            strengths.append(f"Signal de demande digitale positif ({trend:.0f}/100).")
        elif trend < 40:
            risks.append(f"Signal de demande digitale faible ({trend:.0f}/100).")

        if gdp >= 30_000 or imports_gdp >= 35:
            strengths.append("Contexte macroéconomique favorable pour l'importation.")
        if not wb_available:
            risks.append("Certaines données macro récentes sont manquantes, score calculé avec fallback.")

        if price > 0:
            strengths.append(f"Prix observé exploitable pour positionner l'offre ({price:.2f} USD/kg).")

        strengths = strengths[:4]
        risks = risks[:3]

        if not strengths:
            strengths.append("Le modèle v6 détecte une combinaison favorable de signaux commerciaux.")
        if not risks:
            risks.append("Aucun frein majeur détecté par les indicateurs v6, à valider commercialement.")

        country = row.get("country_name", row.get("country_code", "ce marché"))
        explanation = (
            f"{country} obtient un score v6 de {score:.1f}/100. "
            f"Le classement est basé sur la demande import, la dynamique historique, "
            f"les accords/droits, le risque pays, la distance, les signaux de tendance "
            f"et les indicateurs macro disponibles."
        )

        snapshot = {
            "import_value_usd": round(value_usd, 2),
            "growth_lag1_pct": round(growth, 2),
            "market_share_pct": round(market_share, 3),
            "cagr_3y_pct": round(cagr, 2),
            "price_usd_kg": round(price, 3),
            "accord_score": round(accord_score, 1),
            "droits_pct": round(droits, 2),
            "ocde_risk_score": round(ocde, 1),
            "distance_km": round(distance, 0),
            "trend_score": round(trend, 1),
            "wb_gdp_per_capita": round(gdp, 2),
            "wb_imports_pct_gdp": round(imports_gdp, 2),
            "wb_available": bool(wb_available),
        }

        return {
            "explanation": explanation,
            "strengths": strengths,
            "risks": risks,
            "feature_snapshot": snapshot,
            "data_freshness": {
                "trade_data": "données locales ou cache récent",
                "worldbank": "référence locale récente",
                "ocde_risk": "référence locale récente",
                "trend": "signal calculé ou mis en cache",
            },
        }

    def _get_weights(self, hs_code: str) -> dict:
        """Retourne les poids adaptés au type de produit."""
        profile = _HS_PROFILES.get(hs_code, "default")
        return WEIGHTS_PROFILES.get(profile, WEIGHTS_DEFAULT)

    # ───────────────────────────────────────
    # ÉTAPE 1 — Construction de la matrice
    # ───────────────────────────────────────

    def build_feature_matrix(self, trade_df: pd.DataFrame) -> pd.DataFrame:
        """
        Construit la matrice enrichie de 15 features pour chaque pays.
        v2.0 : ajout Google Trends + ITC prix comme feature "tendance".
        """
        rows = []
        for _, row in trade_df.iterrows():
            code = row["country_code"]

            accord   = get_accord_score(code)
            wb       = self._get_wb_scores_fast(code)
            diaspora = get_diaspora(code)
            logist   = get_logistique(code)
            trends   = get_trends(code, self._hs_code)
            itc      = fetch_itc_price(self._hs_code)

            # Score de tendance combiné : Google Trends + position prix vs référence ITC
            trend_score = trends.get("trend_score", 50)
            price_per_kg = row.get("price_usd_kg", 0)
            world_avg_price = itc.get("world_avg", price_per_kg + 1)
            price_position = min(price_per_kg / world_avg_price, 2.0) if world_avg_price > 0 else 1.0

            # Score tendance composite : 70% Google Trends + 30% position prix
            tendance_composite = trend_score * 0.70 + (price_position * 50) * 0.30

            # Bonus MRE × Accord : marché avec forte diaspora ET bon accord = multiplicateur
            diaspora_accord_bonus = (
                min(diaspora["population"] / 1_000_000, 1.0) *
                (1.0 if accord["type"] == "ALE" else 0.5)
            ) * 20  # 0–20 points bonus

            rows.append({
                "country_code":    code,
                "country_name":    row["country_name"],
                # D1 — Marché
                "value_usd":       row["value_usd"],
                "growth_pct":      row.get("growth_pct", 5.0),
                "velocity":        row.get("velocity", 0.0),
                "momentum":        row.get("momentum", row.get("growth_pct", 5.0)),
                "price_usd_kg":    row.get("price_usd_kg", row["value_usd"] / max(row["weight_kg"], 1)),
                # D2 — Accord commercial
                "droits":          accord["droits"],
                "accord_type":     1.0 if accord["type"] == "ALE" else (0.5 if accord["type"] == "PREF" else 0.0),
                "accord_label":    accord["accord"],
                "accord_zone":     accord.get("zone", "OTHER"),
                # D3 — Facilité des affaires
                "ease_business":   wb["ease_business"],
                "rule_of_law":     wb["rule_of_law"],
                "regulatory_qual": wb["regulatory_quality"],
                # D4 — Stabilité politique
                "political_stab":  wb["political_stability"],
                "risk_global":     (wb["political_stability"] + wb["rule_of_law"]) / 2,
                # D5 — Diaspora MRE
                "diaspora_pop":    diaspora["population"],
                "transferts_musd": diaspora["transferts_musd"],
                "diaspora_bonus":  diaspora_accord_bonus,
                # D6 — Logistique
                "distance_km":     logist["distance_km"],
                "lpi":             logist["lpi"],
                "cout_conteneur":  logist["cout_conteneur_usd"],
                "transit_days":    logist["transit_days"],
                # D7 — Tendance & demande (NOUVEAU)
                "tendance":        tendance_composite,
                "trend_direction": trends.get("trend_direction", "stable"),
                "price_position":  price_position,
                # Méta
                "risk_category":   logist["risk_category"],
                "payment_instr":   logist.get("payment_instrument", ""),
            })

        return pd.DataFrame(rows)

    # ───────────────────────────────────────
    # ÉTAPE 2 — Normalisation
    # ───────────────────────────────────────

    def normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalise les features entre 0 et 1.
        Les features "moins = mieux" sont inversées.
        """
        n = df.copy()

        def norm(series):
            mn, mx = series.min(), series.max()
            if mx == mn:
                return pd.Series(np.ones(len(series)), index=series.index)
            return (series - mn) / (mx - mn)

        def norm_inv(series):
            return 1.0 - norm(series)

        # D1 — Marché
        n["vol_norm"]    = norm(df["value_usd"])
        momentum_col = df["momentum"] if df["momentum"].std() > 0 else df["growth_pct"]
        n["growth_norm"] = norm(momentum_col)
        n["prix_norm"]   = norm(df["price_usd_kg"])

        # D2 — Accord
        n["accord_norm"] = df["accord_type"]
        n["droits_norm"] = norm_inv(df["droits"])

        # D3 — Business (déjà sur 0–100 → ramener sur 0–1)
        n["ease_biz_norm"] = df["ease_business"] / 100.0
        n["rule_law_norm"] = df["rule_of_law"] / 100.0
        n["reg_qual_norm"] = df["regulatory_qual"] / 100.0

        # D4 — Stabilité
        n["stability_norm"] = df["political_stab"] / 100.0
        n["risk_norm"]      = df["risk_global"] / 100.0

        # D5 — Diaspora (avec bonus MRE×Accord)
        n["diaspora_norm"]   = norm(df["diaspora_pop"] + df["diaspora_bonus"] * 50_000)
        n["transferts_norm"] = norm(df["transferts_musd"])

        # D6 — Logistique
        n["distance_norm"] = norm_inv(df["distance_km"])
        n["lpi_norm"]      = (df["lpi"] - 1.0) / 4.0          # LPI 1–5 → 0–1
        n["cout_norm"]     = norm_inv(df["cout_conteneur"])

        # D7 — Tendance (NOUVEAU) : déjà sur 0–100
        n["tendance_norm"] = df["tendance"] / 100.0

        return n

    # ───────────────────────────────────────
    # ÉTAPE 3 — Score pondéré multi-critères
    # ───────────────────────────────────────

    def compute_weighted_score(self, n: pd.DataFrame) -> pd.Series:
        """
        Calcule le score pondéré 0–100 avec 7 dimensions.
        Chaque dimension = moyenne pondérée de ses features.
        """
        w = self._weights

        dim_marche    = (n["vol_norm"] * 0.45 + n["growth_norm"] * 0.35 + n["prix_norm"] * 0.20)
        dim_accord    = (n["accord_norm"] * 0.60 + n["droits_norm"] * 0.40)
        dim_business  = (n["ease_biz_norm"] * 0.40 + n["rule_law_norm"] * 0.35 + n["reg_qual_norm"] * 0.25)
        dim_stabilite = (n["stability_norm"] * 0.55 + n["risk_norm"] * 0.45)
        dim_diaspora  = (n["diaspora_norm"] * 0.55 + n["transferts_norm"] * 0.45)
        dim_logistique= (n["distance_norm"] * 0.40 + n["lpi_norm"] * 0.35 + n["cout_norm"] * 0.25)
        dim_tendance  = n["tendance_norm"]  # Feature unique

        score = (
            dim_marche     * w["marche"]    +
            dim_accord     * w["accord"]    +
            dim_business   * w["business"]  +
            dim_stabilite  * w["stabilite"] +
            dim_diaspora   * w["diaspora"]  +
            dim_logistique * w["logistique"]+
            dim_tendance   * w["tendance"]
        )

        return score * 100.0

    # ───────────────────────────────────────
    # ÉTAPE 4 — XGBoost + SHAP
    # ───────────────────────────────────────

    FEATURE_COLS = [
        "vol_norm", "growth_norm", "prix_norm",
        "accord_norm", "droits_norm",
        "ease_biz_norm", "rule_law_norm", "reg_qual_norm",
        "stability_norm", "risk_norm",
        "diaspora_norm", "transferts_norm",
        "distance_norm", "lpi_norm", "cout_norm",
        "tendance_norm",  # NOUVEAU
    ]

    def train_xgboost(self, n: pd.DataFrame, weighted_scores: pd.Series):
        """
        Entraîne XGBoost sur les 16 features normalisées.
        Augmentation 5× avec bruit gaussien pour robustesse.
        """
        X = n[self.FEATURE_COLS].values
        y = weighted_scores.values / 100.0

        np.random.seed(42)
        X_aug = np.vstack(
            [X + np.random.normal(0, 0.025, X.shape) for _ in range(5)] + [X]
        )
        y_aug = np.tile(y, 6)
        X_aug = np.clip(X_aug, 0.0, 1.0)

        self.xgb_model = XGBRegressor(
            n_estimators=250,
            max_depth=4,
            learning_rate=0.04,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=2,
            gamma=0.1,
            reg_alpha=0.05,
            random_state=42,
            verbosity=0,
        )
        self.xgb_model.fit(X_aug, y_aug)
        self.explainer = shap.TreeExplainer(self.xgb_model)
        self._is_trained = True

    def predict_xgboost(self, n: pd.DataFrame) -> np.ndarray:
        X = n[self.FEATURE_COLS].values
        return self.xgb_model.predict(X) * 100.0

    def get_shap_values(self, n: pd.DataFrame) -> np.ndarray:
        X = n[self.FEATURE_COLS].values
        return self.explainer.shap_values(X)

    # ───────────────────────────────────────
    # ÉTAPE 5 — Score ensemble final
    # ───────────────────────────────────────

    def ensemble_score(self, weighted: float, xgb: float) -> float:
        return weighted * ENSEMBLE_RATIO["weighted"] + xgb * ENSEMBLE_RATIO["xgboost"]

    # ───────────────────────────────────────
    # SCORE LABEL & CONFIANCE
    # ───────────────────────────────────────

    def _score_label(self, score: float) -> str:
        if score >= SCORE_THRESHOLDS["excellent"]:
            return "Excellent"
        elif score >= SCORE_THRESHOLDS["bon"]:
            return "Bon"
        elif score >= SCORE_THRESHOLDS["moyen"]:
            return "Moyen"
        else:
            return "Faible"

    def _compute_confidence(self, row: pd.Series) -> float:
        """
        Score de confiance 0–100 basé sur la qualité des données.
        Pénalise les pays avec données statiques uniquement.
        """
        score = 60.0  # Base
        if row.get("value_usd", 0) > 1_000_000:
            score += 15  # Données commerciales substantielles
        if row.get("lpi", 0) > 3.0:
            score += 10  # Données logistiques fiables
        if row.get("diaspora_pop", 0) > 0:
            score += 10  # Données diaspora disponibles
        if row.get("tendance", 50) != 50:
            score += 5   # Données Google Trends réelles
        return min(score, 100.0)

    # ───────────────────────────────────────
    # CONSTRUCTION DES SCORES PAR DIMENSION
    # ───────────────────────────────────────

    def build_dimension_scores(self, row: pd.Series, n_row: pd.Series) -> List[DimensionScore]:
        """Construit les 7 DimensionScore avec détails et interprétations."""
        w = self._weights
        dims = []

        # D1 — Marché
        score_marche = (
            n_row["vol_norm"] * 0.45 +
            n_row["growth_norm"] * 0.35 +
            n_row["prix_norm"] * 0.20
        ) * 100
        dims.append(DimensionScore(
            nom="Potentiel de marché", emoji="📊",
            score=round(score_marche, 1), poids=w["marche"],
            contribution=round(score_marche * w["marche"], 1),
            detail={
                "Volume importé (2022)": f"{row['value_usd']/1e6:.1f}M USD/an",
                "CAGR 3 ans":            f"+{row['growth_pct']:.1f}%/an",
                "Momentum marché":       f"{row.get('momentum', row['growth_pct']):.1f} — {growth_label(row.get('momentum', row['growth_pct']))}",
                "Prix pratiqué":         f"{row['price_usd_kg']:.2f} USD/kg",
                "Vélocité":              f"{row.get('velocity', 0):+.1f} pts",
            },
            interpretation=self._interpret_marche(row, n_row),
        ))

        # D2 — Accord commercial
        score_accord = (n_row["accord_norm"] * 0.60 + n_row["droits_norm"] * 0.40) * 100
        dims.append(DimensionScore(
            nom="Accord commercial", emoji="🤝",
            score=round(score_accord, 1), poids=w["accord"],
            contribution=round(score_accord * w["accord"], 1),
            detail={
                "Accord":           row["accord_label"],
                "Droits de douane": f"{row['droits']:.1f}%",
                "Type":             row["accord_type"] and ["NPF", "PREF", "ALE"][int(row["accord_type"] * 2)] or "NPF",
                "Zone":             row.get("accord_zone", ""),
            },
            interpretation=self._interpret_accord(row),
        ))

        # D3 — Facilité des affaires
        score_biz = (
            n_row["ease_biz_norm"] * 0.40 +
            n_row["rule_law_norm"] * 0.35 +
            n_row["reg_qual_norm"] * 0.25
        ) * 100
        dims.append(DimensionScore(
            nom="Facilité des affaires", emoji="🏢",
            score=round(score_biz, 1), poids=w["business"],
            contribution=round(score_biz * w["business"], 1),
            detail={
                "Ease of Business (WB)":  f"{row['ease_business']:.1f}/100",
                "État de droit":          f"{row['rule_of_law']:.1f}/100",
                "Qualité réglementaire":  f"{row['regulatory_qual']:.1f}/100",
            },
            interpretation=self._interpret_business(row),
        ))

        # D4 — Stabilité & risque pays
        score_stab = (n_row["stability_norm"] * 0.55 + n_row["risk_norm"] * 0.45) * 100
        dims.append(DimensionScore(
            nom="Stabilité & risque pays", emoji="🛡️",
            score=round(score_stab, 1), poids=w["stabilite"],
            contribution=round(score_stab * w["stabilite"], 1),
            detail={
                "Stabilité politique": f"{row['political_stab']:.1f}/100",
                "Risque global":       f"{row['risk_global']:.1f}/100",
                "Catégorie OCDE":      f"Catégorie {int(row.get('risk_category', 4))}",
            },
            interpretation=self._interpret_stabilite(row),
        ))

        # D5 — Diaspora MRE
        score_dias = (n_row["diaspora_norm"] * 0.55 + n_row["transferts_norm"] * 0.45) * 100
        dims.append(DimensionScore(
            nom="Diaspora marocaine (MRE)", emoji="🌍",
            score=round(score_dias, 1), poids=w["diaspora"],
            contribution=round(score_dias * w["diaspora"], 1),
            detail={
                "Population MRE":    f"{int(row['diaspora_pop']):,} personnes",
                "Transferts annuels": f"{row['transferts_musd']:.0f}M USD/an",
                "Bonus MRE×Accord":  f"+{row.get('diaspora_bonus', 0):.1f} pts",
            },
            interpretation=self._interpret_diaspora(row),
        ))

        # D6 — Logistique & transport
        score_log = (
            n_row["distance_norm"] * 0.40 +
            n_row["lpi_norm"] * 0.35 +
            n_row["cout_norm"] * 0.25
        ) * 100
        dims.append(DimensionScore(
            nom="Logistique & transport", emoji="🚢",
            score=round(score_log, 1), poids=w["logistique"],
            contribution=round(score_log * w["logistique"], 1),
            detail={
                "Distance Casablanca": f"{int(row['distance_km']):,} km",
                "LPI World Bank 2023": f"{row['lpi']:.2f}/5",
                "Coût conteneur 20'":  f"{int(row['cout_conteneur']):,} USD",
                "Transit estimé":      f"{int(row.get('transit_days', 14))} jours",
            },
            interpretation=self._interpret_logistique(row),
        ))

        # D7 — Tendance & demande (NOUVEAU)
        score_tendance = n_row["tendance_norm"] * 100
        dims.append(DimensionScore(
            nom="Tendance & demande", emoji="📈",
            score=round(score_tendance, 1), poids=w["tendance"],
            contribution=round(score_tendance * w["tendance"], 1),
            detail={
                "Score Google Trends": f"{row['tendance']:.0f}/100",
                "Direction tendance":  row.get("trend_direction", "stable").capitalize(),
                "Position prix/moy.":  f"{row.get('price_position', 1.0):.2f}× prix mondial",
            },
            interpretation=self._interpret_tendance(row),
        ))

        return dims

    # ───────────────────────────────────────
    # TEXTES D'INTERPRÉTATION
    # ───────────────────────────────────────

    def _interpret_marche(self, row, n_row):
        vol = row["value_usd"]
        if n_row["vol_norm"] > 0.7:
            taille = f"Grand marché ({vol/1e6:.1f}M USD/an)"
        elif n_row["vol_norm"] > 0.3:
            taille = f"Marché moyen ({vol/1e6:.1f}M USD/an)"
        else:
            taille = f"Marché de niche ({vol/1e6:.1f}M USD/an)"
        cagr = row.get("growth_pct", 5.0)
        vel  = row.get("velocity", 0.0)
        mom  = row.get("momentum", cagr)
        return f"{taille}. {interpret_growth(cagr, vel, mom)}"

    def _interpret_accord(self, row):
        label = row.get("accord_label", "")
        droits = row.get("droits", 8.0)
        if droits == 0:
            return f"{label} — Entrée en franchise totale, avantage compétitif direct vs concurrents hors accord."
        elif droits < 5:
            return f"{label} — Droits préférentiels {droits:.1f}%, reste favorable face aux concurrents."
        else:
            return f"Droits NPF {droits:.1f}% — Surveiller la compétition pays à accord préférentiel."

    def _interpret_business(self, row):
        eb = row.get("ease_business", 50)
        if eb > 82:
            return "Environnement exceptionnel : procédures rapides, contrats respectés, recouvrement efficace."
        elif eb > 70:
            return "Bon environnement des affaires, quelques formalités à anticiper."
        elif eb > 58:
            return "Environnement modéré, certaines complexités administratives à gérer."
        else:
            return "Environnement difficile, accompagnement local recommandé (agent, distributeur)."

    def _interpret_stabilite(self, row):
        ps = row.get("political_stab", 40)
        cat = row.get("risk_category", 4)
        instrument = row.get("payment_instr", "")
        if cat <= 1:
            return f"Pays très stable (cat. OCDE {cat}) — paiements sécurisés, risque d'impayé minimal."
        elif cat <= 2:
            return f"Stabilité satisfaisante (cat. OCDE {cat}) — {instrument}."
        elif cat <= 4:
            return f"Risque modéré à moyen (cat. OCDE {cat}) — {instrument}."
        else:
            return f"Risque élevé (cat. OCDE {cat}) — {instrument}. Assurance SMAEX fortement recommandée."

    def _interpret_diaspora(self, row):
        pop = row.get("diaspora_pop", 0)
        tr  = row.get("transferts_musd", 0)
        bonus = row.get("diaspora_bonus", 0)
        if pop > 800_000:
            base = f"Très forte communauté MRE ({pop:,} personnes, {tr}M USD/an). Réseau commercial naturel direct."
        elif pop > 100_000:
            base = f"Communauté MRE significative ({pop:,}). Potentiel de prescription et distribution."
        elif pop > 10_000:
            base = f"Présence MRE ({pop:,}). Impact modéré sur les ventes."
        else:
            base = "Peu ou pas de diaspora marocaine dans ce pays."
        if bonus > 10:
            base += f" Bonus synergique MRE+Accord : +{bonus:.0f} pts."
        return base

    def _interpret_logistique(self, row):
        km   = row.get("distance_km", 10_000)
        lpi  = row.get("lpi", 2.5)
        cout = row.get("cout_conteneur", 3_000)
        days = row.get("transit_days", 14)
        if km < 2_000 and lpi > 3.8:
            return f"Excellente accessibilité ({km:,} km, LPI {lpi:.1f}/5). Transit ~{days}j, coût {cout:,} USD."
        elif km < 5_000:
            return f"Bonne accessibilité ({km:,} km). Transit ~{days}j, conteneur {cout:,} USD."
        else:
            return f"Distance importante ({km:,} km). Prévoir ~{days}j de transit et {cout:,} USD de fret."

    def _interpret_tendance(self, row):
        score  = row.get("tendance", 50)
        direc  = row.get("trend_direction", "stable")
        pos    = row.get("price_position", 1.0)
        if score >= 70 and direc == "en hausse":
            base = "Demande consommateur en forte croissance — timing favorable pour entrer sur ce marché."
        elif score >= 50:
            base = f"Intérêt consommateur stable à {score:.0f}/100."
        else:
            base = "Demande en retrait — marché plus difficile à pénétrer actuellement."
        if pos > 1.3:
            base += f" Vos prix ({pos:.1f}× la moyenne mondiale) reflètent un positionnement premium."
        elif pos < 0.8:
            base += " Prix compétitifs vs marché mondial — avantage sur volume."
        return base

    # ───────────────────────────────────────
    # SHAP NARRATIVE
    # ───────────────────────────────────────

    def build_shap_dict(self, shap_vals: np.ndarray, idx: int) -> dict:
        """Valeurs SHAP triées par importance absolue."""
        vals = shap_vals[idx]
        result = {}
        for i, col in enumerate(self.FEATURE_COLS):
            label = FEATURE_LABELS.get(col, col)
            result[label] = round(float(vals[i]) * 100, 2)
        return dict(sorted(result.items(), key=lambda x: abs(x[1]), reverse=True))

    def build_shap_narrative(self, shap_dict: dict, country_name: str) -> str:
        """
        Génère une explication narrative du score en langage naturel.
        Traduit les valeurs SHAP en phrase compréhensible par une PME.
        """
        positives = [(k, v) for k, v in shap_dict.items() if v > 0.5][:3]
        negatives = [(k, v) for k, v in shap_dict.items() if v < -0.5][:2]

        parts = [f"Pour {country_name} :"]

        if positives:
            pos_str = ", ".join([f"{k.lower()} (+{v:.1f} pts)" for k, v in positives])
            parts.append(f"Les points forts sont {pos_str}.")

        if negatives:
            neg_str = " et ".join([f"{k.lower()} ({v:.1f} pts)" for k, v in negatives])
            parts.append(f"Les freins principaux sont {neg_str}.")

        return " ".join(parts)

    # ───────────────────────────────────────
    # SIMULATION DE RENTABILITÉ
    # ───────────────────────────────────────

    def simulate_rentabilite(
        self,
        row: pd.Series,
        cout_production_usd_kg: float = 8.0,
        volume_conteneur_kg: int = 18_000,
    ) -> RentabiliteEstimee:
        """
        Estime la rentabilité export pour un marché donné.
        Hypothèses : coût de production fourni, conteneur 20' = 18 000 kg standard.
        """
        prix_fob   = row.get("price_usd_kg", 10.0)
        cout_fret  = row.get("cout_conteneur", 2_000) / max(volume_conteneur_kg, 1)
        droits_pct = row.get("droits", 5.0) / 100.0
        droits_usd = prix_fob * droits_pct

        cout_total   = cout_production_usd_kg + cout_fret + droits_usd
        marge_brute  = (prix_fob - cout_production_usd_kg) / prix_fob * 100 if prix_fob > 0 else 0
        marge_nette  = (prix_fob - cout_total) / prix_fob * 100 if prix_fob > 0 else 0

        # Point mort : volume minimum pour couvrir les coûts fixes (fret + certif = ~3 000 USD)
        frais_fixes    = row.get("cout_conteneur", 2_000) + 1_000  # Fret + certifications
        marge_unit_usd = max(prix_fob - cout_production_usd_kg - droits_usd, 0.01)
        point_mort_kg  = int(frais_fixes / marge_unit_usd)

        if marge_nette > 25:
            note = "Rentabilité excellente — marché très attractif financièrement."
        elif marge_nette > 10:
            note = "Rentabilité satisfaisante — marché viable."
        elif marge_nette > 0:
            note = "Marge faible — optimiser packaging et volume pour rentabiliser."
        else:
            note = "Attention : marge négative aux hypothèses actuelles. Revoir positionnement prix."

        return RentabiliteEstimee(
            marche               = row.get("country_name", ""),
            prix_fob_usd_kg      = round(prix_fob, 2),
            cout_production_usd_kg = round(cout_production_usd_kg, 2),
            cout_fret_usd_kg     = round(cout_fret, 3),
            droits_douane_pct    = row.get("droits", 0.0),
            marge_brute_pct      = round(marge_brute, 1),
            marge_nette_pct      = round(marge_nette, 1),
            point_mort_volume_kg = point_mort_kg,
            note                 = note,
        )

    # ───────────────────────────────────────
    # ATOUTS & RISQUES
    # ───────────────────────────────────────

    def extract_atouts_risques(self, dims: List[DimensionScore], shap_dict: dict) -> tuple:
        """Extrait les 3 meilleurs atouts et principaux risques depuis les dimensions."""
        atouts  = []
        risques = []

        for d in dims:
            if d.score >= 70 and len(atouts) < 3:
                atouts.append(f"{d.emoji} {d.nom} ({d.score:.0f}/100) — {d.interpretation}")
            elif d.score < 45:
                risques.append(f"⚠ {d.nom} ({d.score:.0f}/100) — {d.interpretation}")

        # Compléter avec SHAP si moins de 3 atouts
        for label, val in shap_dict.items():
            if val > 1.0 and len(atouts) < 3:
                if not any(label.lower() in a.lower() for a in atouts):
                    atouts.append(f"✓ {label} contribue fortement au score")
            if val < -1.0 and len(risques) < 2:
                if not any(label.lower() in r.lower() for r in risques):
                    risques.append(f"⚠ {label} pèse sur la compétitivité")

        return atouts[:3], risques[:2]

    # ───────────────────────────────────────
    # PIPELINE PRINCIPAL
    # ───────────────────────────────────────

    def run(
        self,
        product_name: str,
        hs_code: str,
        top_n: int = 5,
        cout_production_usd_kg: float = 8.0,
        force_refresh: bool = False,
    ) -> List[MarketResult]:
        """
        Pipeline complet de scoring export.
        Retourne les top_n marchés avec scores, explications et simulation.

        Args:
            product_name: Nom du produit en français
            hs_code: Code HS douanier (6–8 chiffres)
            top_n: Nombre de marchés à retourner (défaut 5)
            cout_production_usd_kg: Coût de production en USD/kg pour simulation rentabilité
        """
        t_start = time.time()
        self._hs_code      = hs_code
        self._product_name = product_name
        self._weights      = self._get_weights(hs_code)

        profile = _HS_PROFILES.get(hs_code, "default")
        logger.info(f"Analyse : {product_name} (HS {hs_code}) — profil poids : {profile}")

        # ① Données commerciales
        logger.info("  Étape 1/6 — Données commerciales...")
        trade_df = get_trade_data(hs_code, force_refresh=force_refresh)

        # ② Enrichissement croissance dynamique
        logger.info("  Étape 2/6 — CAGR dynamique 3 ans...")
        trade_df = enrich_with_growth(trade_df, hs_code, set(ACCORDS_MAROC.keys()), force_refresh=force_refresh)

        # ③ Matrice de features (7 dimensions)
        logger.info("  Étape 3/6 — Construction matrice features...")
        df = self.build_feature_matrix(trade_df)

        # ④ Normalisation
        n = self.normalize_features(df)

        # ⑤ Score pondéré
        logger.info("  Étape 4/6 — Score pondéré multi-critères...")
        weighted_scores = self.compute_weighted_score(n)

        # ⑥ XGBoost + SHAP
        logger.info("  Étape 5/6 — XGBoost + SHAP...")
        self.train_xgboost(n, weighted_scores)
        xgb_scores = self.predict_xgboost(n)
        shap_vals  = self.get_shap_values(n)

        # ⑦ Score ensemble + classement
        logger.info("  Étape 6/6 — Classement final...")
        final_scores = np.array([
            self.ensemble_score(w, x) for w, x in zip(weighted_scores, xgb_scores)
        ])
        if final_scores.max() > 0:
            final_scores = final_scores / final_scores.max() * 100.0

        v6_scores = self.predict_v6_scores(df)
        v6_feature_matrix = self._last_v6_feature_matrix
        scoring_method = "legacy_weighted_xgboost"
        if v6_scores is not None:
            final_scores = self.calibrate_v6_scores_for_pme(v6_scores, v6_feature_matrix)
            scoring_method = "v6_market_attractiveness"
            logger.info("Using v6 market ranking model with SME calibration for final market ranking")
        else:
            logger.info("Using legacy weighted/XGBoost ranking")

        order   = np.argsort(final_scores)[::-1]
        results = []

        for rank, idx in enumerate(order[:top_n], start=1):
            row    = df.iloc[idx]
            n_row  = n.iloc[idx]

            dims       = self.build_dimension_scores(row, n_row)
            shap_dict  = self.build_shap_dict(shap_vals, idx)
            atouts, risques = self.extract_atouts_risques(dims, shap_dict)
            narrative  = self.build_shap_narrative(shap_dict, row["country_name"])
            v6_context = {
                "explanation": "",
                "strengths": [],
                "risks": [],
                "feature_snapshot": {},
                "data_freshness": {},
            }
            if scoring_method == "v6_market_attractiveness" and v6_feature_matrix is not None:
                v6_context = self.build_v6_explanation(row, v6_feature_matrix.iloc[idx], float(final_scores[idx]))
                atouts = v6_context["strengths"]
                risques = v6_context["risks"]
                narrative = v6_context["explanation"]
            confidence = self._compute_confidence(row)
            rentab     = self.simulate_rentabilite(row, cout_production_usd_kg)

            # Certifications requises selon zone
            zone = row.get("accord_zone", "OTHER")
            certif_zone = {"UE": "UE", "EUR": "UE", "AME": "USA", "MENA": "GAFTA"}.get(zone, "UE")
            from data_sources import get_certifications_requises
            certifications = get_certifications_requises(certif_zone, "alimentaire")

            # Alerte paiement
            risk_cat = int(row.get("risk_category", 0))
            payment_instr = row.get("payment_instr", "Virement bancaire standard")
            if risk_cat >= 5:
                payment_alerte = f"🔴 RISQUE ÉLEVÉ — {payment_instr}"
            elif risk_cat >= 3:
                payment_alerte = f"🟡 RISQUE MODÉRÉ — {payment_instr}"
            else:
                payment_alerte = f"🟢 Risque faible — {payment_instr}"

            results.append(MarketResult(
                rank=rank,
                country_code=row["country_code"],
                country_name=row["country_name"],
                score_final=round(float(final_scores[idx]), 1),
                score_weighted=round(float(weighted_scores.iloc[idx]), 1),
                score_xgboost=round(float(xgb_scores[idx]), 1),
                score_label=self._score_label(float(final_scores[idx])),
                confidence=round(confidence, 1),
                dimensions=dims,
                shap_values=shap_dict,
                top_atouts=atouts,
                top_risques=risques,
                accord_info=get_accord_score(row["country_code"]),
                logistique_info=get_logistique(row["country_code"]),
                trends_info={"score": row.get("tendance", 50), "direction": row.get("trend_direction", "stable")},
                rentabilite=rentab,
                certifications_requises=certifications,
                payment_alerte=payment_alerte,
                shap_narrative=narrative,
                score_ml_v6=round(float(final_scores[idx]), 1) if scoring_method == "v6_market_attractiveness" else None,
                scoring_method=scoring_method,
                v6_features_used=list(self.v6_features) if scoring_method == "v6_market_attractiveness" else [],
                v6_explanation=v6_context["explanation"],
                v6_strengths=v6_context["strengths"],
                v6_risks=v6_context["risks"],
                v6_feature_snapshot=v6_context["feature_snapshot"],
                data_freshness=v6_context["data_freshness"],
            ))

        elapsed = time.time() - t_start
        logger.info(f"Analyse terminée en {elapsed:.1f}s — Top {top_n} marchés identifiés.")
        return results

    def run_batch(
        self,
        products: List[Dict],
        top_n: int = 5,
    ) -> Dict[str, List[MarketResult]]:
        """
        Analyse batch pour plusieurs produits.
        products = [{"name": "Huile d'argan", "hs_code": "151590", "cout_kg": 8.0}, ...]
        """
        results = {}
        for p in products:
            logger.info(f"Batch : analyse de {p['name']}...")
            results[p["hs_code"]] = self.run(
                product_name=p["name"],
                hs_code=p["hs_code"],
                top_n=top_n,
                cout_production_usd_kg=p.get("cout_kg", 8.0),
            )
        return results


# ═══════════════════════════════════════════════════════════════
# AFFICHAGE TERMINAL ENRICHI
# ═══════════════════════════════════════════════════════════════

def print_results(results: List[MarketResult], product_name: str):
    """Affichage terminal complet et lisible."""
    print(f"\n{'═'*65}")
    print(f"  MARCHÉS PRIORITAIRES — {product_name.upper()}")
    print(f"{'═'*65}")

    for r in results:
        bar_main = "█" * int(r.score_final / 5) + "░" * (20 - int(r.score_final / 5))
        print(f"\n  #{r.rank}  {r.country_name:<22} {bar_main} {r.score_final:.1f}/100 [{r.score_label}]")
        print(f"       Confiance données : {r.confidence:.0f}%")
        print(f"       Score pondéré : {r.score_weighted:.1f} | XGBoost : {r.score_xgboost:.1f}")
        print(f"       Accord : {r.accord_info['accord']}")
        print(f"       {r.payment_alerte}")

        print(f"\n       Dimensions :")
        for d in r.dimensions:
            bar_d = "▓" * int(d.score / 10) + "░" * (10 - int(d.score / 10))
            print(f"         {d.emoji} {d.nom:<30} {bar_d} {d.score:.0f}/100")

        print(f"\n       Atouts principaux :")
        for a in r.top_atouts:
            print(f"         {a}")

        if r.top_risques:
            print(f"\n       Risques identifiés :")
            for ri in r.top_risques:
                print(f"         {ri}")

        if r.rentabilite:
            rt = r.rentabilite
            print(f"\n       Simulation rentabilité (coût prod. {rt.cout_production_usd_kg} USD/kg) :")
            print(f"         Prix FOB : {rt.prix_fob_usd_kg} USD/kg")
            print(f"         Droits douane : {rt.droits_douane_pct:.1f}%")
            print(f"         Marge brute : {rt.marge_brute_pct:.1f}% | Nette : {rt.marge_nette_pct:.1f}%")
            print(f"         Point mort : {rt.point_mort_volume_kg:,} kg")
            print(f"         {rt.note}")

        print(f"\n       Certifications requises : {', '.join(r.certifications_requises[:3])}")
        print(f"\n       Explication IA : {r.shap_narrative}")

    print(f"\n{'═'*65}\n")


# ═══════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    engine = MarketScoringEngine()

    # Test simple — huile d'argan avec coût de production estimé
    results = engine.run(
        product_name="Huile d'argan bio",
        hs_code="151590",
        top_n=5,
        cout_production_usd_kg=8.0,
    )
    print_results(results, "Huile d'argan bio")
