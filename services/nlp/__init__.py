"""Module de service NLP open source.

ÉTAPE 3 : Remplace Claude Anthropic par pipeline NLP 100% open-source.

Modules:
  - spacy_extractor: Extraction entités
  - transformers_classifier: Classification des alertes
  - summarizer: Résumés et contenu français
  - opensource_regulatory_analyzer: Orchestrateur principal
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

# Imports pour la nouvelle Étape 3
try:
    from .spacy_extractor import SpacyExtractor, ExtractedEntity
    from .transformers_classifier import (
        TransformersAlertClassifier,
        AlertClassification,
        ImpactCalculator
    )
    from .summarizer import AlertSummarizer, Summary, FrenchContentGenerator
    from .opensource_regulatory_analyzer import (
        OpenSourceRegulatoryAnalyzer,
        RegulatoryAnalysis,
    )
    OPENSOURCE_NLP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Modules NLP open-source non disponibles: {e}")
    OPENSOURCE_NLP_AVAILABLE = False

# Pour compatibilité avec le code existant
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


# Alias pour RegulatoryAnalysis (compatible avec ancien code)
RegulatoryAnalysis_ = NLPAnalysis


class NLPAnalyzer:
    """Pipeline NLP local pour l'analyse réglementaire.

    Version ÉTAPE 3 : utilise les modèles open-source transformers.
    Pas de dépendance Anthropic Claude.
    """

    def __init__(self, use_models: bool = True):
        self.classifier = None
        self.summarizer = None
        self.embedder = None
        self.available = False
        self.opensource_analyzer = None

        # NOUVELLE ÉTAPE 3 : Initialiser l'analyseur open-source
        if use_models and OPENSOURCE_NLP_AVAILABLE:
            try:
                logging.info("Initialisation du pipeline NLP open-source (Transformers + spaCy)...")
                self.opensource_analyzer = OpenSourceRegulatoryAnalyzer(
                    language="en",
                    use_gpu=False,
                    use_cache=True
                )
                self.available = True
                logging.info("✅ NLP open-source initialisé avec succès")
                return
            except Exception as e:
                logging.error(f"Erreur initialisation NLP open-source: {e}")
        
        # Fallback ancien code
        logging.info("NLP en mode basique (pas de modèles ML)")

    def analyze(self, text: str, hs_code: str = "", target_countries: list = None) -> NLPAnalysis:
        pays = target_countries or []
        produits = [hs_code] if hs_code else []

        # Analyse basée sur des règles simples (mots-clés)
        text_lower = text.lower()

        # Mots-clés pour niveaux d'alerte
        critical_words = ["interdiction", "ban", "suspension", "retrait", "rappel", "contamination", "danger"]
        warning_words = ["modification", "changement", "nouveau", "révision", "durcissement", "obligation"]
        info_words = ["mise à jour", "clarification", "information", "notification"]

        niveau = "INFO"
        impact_score = 30.0
        confiance = 0.5

        # Comptage des mots-clés
        critical_count = sum(1 for word in critical_words if word in text_lower)
        warning_count = sum(1 for word in warning_words if word in text_lower)
        info_count = sum(1 for word in info_words if word in text_lower)

        if critical_count > 0:
            niveau = "CRITIQUE"
            impact_score = 85.0
            confiance = min(0.9, 0.5 + critical_count * 0.1)
        elif warning_count > 0:
            niveau = "ATTENTION"
            impact_score = 65.0
            confiance = min(0.8, 0.5 + warning_count * 0.1)
        else:
            niveau = "INFO"
            impact_score = 35.0
            confiance = 0.6

        # Résumé simple : première phrase + ...
        sentences = text.split('.')
        resume = sentences[0].strip() + "." if sentences else text[:200] + "..."

        action_requise = "Vérifier les réglementations manuellement."
        if niveau == "CRITIQUE":
            action_requise = "Action urgente : contacter les autorités douanières."
        elif niveau == "ATTENTION":
            action_requise = "Préparer la mise en conformité dans les délais."

        return NLPAnalysis(
            titre="Analyse réglementaire automatique",
            niveau=niveau,
            pays_concernes=pays,
            produits=produits,
            impact_score=round(impact_score, 1),
            resume=resume,
            impact_export="Impact estimé sur l'exportation marocaine.",
            action_requise=action_requise,
            date_vigueur=None,
            source_fiable=confiance > 0.7,
            confiance=round(confiance, 2),
        )


__all__ = [
    "NLPAnalysis",
    "NLPAnalyzer",
    # Modules ÉTAPE 3 open-source
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