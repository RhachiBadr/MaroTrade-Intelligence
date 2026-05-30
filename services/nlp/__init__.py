"""Services NLP open-source de MaroTrade Intelligence."""

import logging
from dataclasses import dataclass
from typing import List, Optional


logger = logging.getLogger(__name__)

try:
    from .spacy_extractor import ExtractedEntity, SpacyExtractor
    from .transformers_classifier import (
        AlertClassification,
        ImpactCalculator,
        TransformersAlertClassifier,
    )
    from .summarizer import AlertSummarizer, FrenchContentGenerator, Summary
    from .opensource_regulatory_analyzer import OpenSourceRegulatoryAnalyzer, RegulatoryAnalysis

    OPENSOURCE_NLP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Modules NLP open-source non disponibles: {e}")
    OPENSOURCE_NLP_AVAILABLE = False

TRANSFORMERS_AVAILABLE = False


@dataclass
class NLPAnalysis:
    titre: str
    niveau: str
    pays_concernes: List[str]
    produits: List[str]
    impact_score: float
    resume: str
    impact_export: str
    action_requise: str
    date_vigueur: Optional[str]
    source_fiable: bool
    confiance: float


RegulatoryAnalysis_ = NLPAnalysis


class NLPAnalyzer:
    """Facade stable vers OpenSourceRegulatoryAnalyzer avec fallback simple."""

    def __init__(self, use_models: bool = True):
        self.classifier = None
        self.summarizer = None
        self.embedder = None
        self.available = False
        self.use_models = use_models
        self.opensource_analyzer = None

        if use_models and OPENSOURCE_NLP_AVAILABLE:
            try:
                logging.info("NLPAnalyzer using OpenSourceRegulatoryAnalyzer")
                self.opensource_analyzer = OpenSourceRegulatoryAnalyzer(
                    language="en",
                    use_gpu=False,
                    use_cache=True,
                )
                self.available = True
                return
            except Exception as e:
                logging.error(f"NLPAnalyzer fallback triggered because of error: {e}")

        logging.info("NLPAnalyzer using fallback rule-based analyzer")

    def analyze(
        self,
        text: str,
        category: str = "",
        classification: str = "",
        origin: str = "",
        maroc_relevant: Optional[bool] = None,
        hs_code: Optional[str] = None,
        target_countries: list = None,
        context: dict = None,
    ) -> dict:
        """Analyse un texte avec le pipeline open-source ou le fallback.

        Compatible avec l'ancien appel NLPAnalyzer.analyze(text).
        """
        context = context or {}
        hs_code = hs_code or context.get("hs_code", "")
        target_countries = target_countries or context.get("target_countries", [])

        if self.opensource_analyzer is not None:
            try:
                logging.info("NLPAnalyzer using OpenSourceRegulatoryAnalyzer")
                analysis = self.opensource_analyzer.analyze(
                    text=text,
                    category=category,
                    classification=classification,
                    origin=origin,
                    maroc_relevant=maroc_relevant,
                    hs_code=hs_code,
                    target_countries=target_countries,
                )
                return self._analysis_to_dict(analysis)
            except Exception as e:
                logging.error(f"NLPAnalyzer fallback triggered because of error: {e}")

        logging.info("NLPAnalyzer using fallback rule-based analyzer")
        return self._fallback_analyze(
            text=text,
            category=category,
            classification=classification,
            origin=origin,
            maroc_relevant=maroc_relevant,
            hs_code=hs_code,
            target_countries=target_countries,
        )

    def _analysis_to_dict(self, analysis) -> dict:
        """Convertit RegulatoryAnalysis en dictionnaire stable."""
        return {
            "niveau": getattr(analysis, "niveau", "INFO"),
            "level": getattr(analysis, "niveau", "INFO"),
            "confidence": getattr(analysis, "confiance", 0.0),
            "confiance": getattr(analysis, "confiance", 0.0),
            "impact_score": getattr(analysis, "impact_score", 0.0),
            "summary": getattr(analysis, "resume_fr", ""),
            "resume": getattr(analysis, "resume_fr", ""),
            "resume_fr": getattr(analysis, "resume_fr", ""),
            "entities": getattr(analysis, "entities", None) or [],
            "keywords": getattr(analysis, "keywords", None) or [],
            "reasoning": getattr(analysis, "reasoning", ""),
            "category": getattr(analysis, "category", ""),
            "classification": getattr(analysis, "classification", ""),
            "origin": getattr(analysis, "origin", ""),
            "maroc_relevant": getattr(analysis, "maroc_relevant", None),
            "titre": getattr(analysis, "titre_fr", ""),
            "titre_fr": getattr(analysis, "titre_fr", ""),
            "pays_concernes": getattr(analysis, "pays_concernes", []),
            "produits": getattr(analysis, "produits", []),
            "impact_export": getattr(analysis, "impact_export", ""),
            "action_requise": getattr(analysis, "action_requise", ""),
            "date_vigueur": getattr(analysis, "date_vigueur", None),
            "source_fiable": getattr(analysis, "source_fiable", False),
        }

    def _fallback_analyze(
        self,
        text: str,
        category: str = "",
        classification: str = "",
        origin: str = "",
        maroc_relevant: Optional[bool] = None,
        hs_code: str = "",
        target_countries: list = None,
    ) -> dict:
        pays = target_countries or []
        produits = [hs_code] if hs_code else []
        text_lower = text.lower()

        critical_words = ["interdiction", "ban", "suspension", "retrait", "rappel", "contamination", "danger"]
        warning_words = ["modification", "changement", "nouveau", "revision", "durcissement", "obligation"]

        critical_count = sum(1 for word in critical_words if word in text_lower)
        warning_count = sum(1 for word in warning_words if word in text_lower)

        if critical_count > 0:
            niveau = "CRITIQUE"
            impact_score = 85.0
            confidence = min(0.9, 0.5 + critical_count * 0.1)
        elif warning_count > 0:
            niveau = "ATTENTION"
            impact_score = 65.0
            confidence = min(0.8, 0.5 + warning_count * 0.1)
        else:
            niveau = "INFO"
            impact_score = 35.0
            confidence = 0.6

        sentences = text.split(".")
        summary = sentences[0].strip() + "." if sentences and sentences[0].strip() else text[:200] + "..."

        action_requise = "Verifier les reglementations manuellement."
        if niveau == "CRITIQUE":
            action_requise = "Action urgente : contacter les autorites douanieres."
        elif niveau == "ATTENTION":
            action_requise = "Preparer la mise en conformite dans les delais."

        return {
            "niveau": niveau,
            "level": niveau,
            "confidence": round(confidence, 2),
            "confiance": round(confidence, 2),
            "impact_score": round(impact_score, 1),
            "summary": summary,
            "resume": summary,
            "resume_fr": summary,
            "entities": [],
            "keywords": [],
            "reasoning": "Fallback rule-based analyzer.",
            "category": category,
            "classification": classification,
            "origin": origin,
            "maroc_relevant": maroc_relevant,
            "titre": "Analyse reglementaire automatique",
            "titre_fr": "Analyse reglementaire automatique",
            "pays_concernes": pays,
            "produits": produits,
            "impact_export": "Impact estime sur l'exportation marocaine.",
            "action_requise": action_requise,
            "date_vigueur": None,
            "source_fiable": confidence > 0.7,
        }


__all__ = [
    "NLPAnalysis",
    "NLPAnalyzer",
    "SpacyExtractor",
    "ExtractedEntity",
    "TransformersAlertClassifier",
    "AlertClassification",
    "ImpactCalculator",
    "AlertSummarizer",
    "Summary",
    "FrenchContentGenerator",
    "OpenSourceRegulatoryAnalyzer",
    "RegulatoryAnalysis",
]
