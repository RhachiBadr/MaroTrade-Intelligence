"""Orchestrateur NLP open-source pour les alertes reglementaires.

Ce module garde la structure compatible avec l'ancien analyseur, tout en
branchant le classifieur RASFF XLM-RoBERTa fine-tune via
TransformersAlertClassifier. spaCy, le summarizer et ImpactCalculator restent
des complements du classifieur principal.
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from services.nlp.spacy_extractor import SpacyExtractor
from services.nlp.summarizer import AlertSummarizer, FrenchContentGenerator
from services.nlp.transformers_classifier import ImpactCalculator, TransformersAlertClassifier


logger = logging.getLogger(__name__)

CACHE_DIR = Path(".cache_marotrade")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL_DAYS = 3

MAROC_CONTEXT = {
    "main_products": ["151590", "160413", "080410", "09102010"],
    "main_markets": ["FRA", "DEU", "USA", "SAU", "ARE"],
    "main_organizations": ["ONSSA", "Douanes marocaines", "ASIDCOM"],
}


@dataclass
class RegulatoryAnalysis:
    """Resultat structure de l'analyse d'une alerte reglementaire."""

    titre_fr: str
    niveau: str
    pays_concernes: list
    produits: list
    impact_score: float
    resume_fr: str
    impact_export: str
    action_requise: str
    date_vigueur: Optional[str]
    source_fiable: bool
    confiance: float
    keywords: Optional[List[str]] = None
    reasoning: str = ""
    entities: Optional[List[Dict]] = None
    category: str = ""
    classification: str = ""
    origin: str = ""
    maroc_relevant: Optional[bool] = None


class OpenSourceRegulatoryAnalyzer:
    """Pipeline local: spaCy + classifieur RASFF fine-tune + resume."""

    def __init__(
        self,
        language: str = "en",
        use_gpu: bool = False,
        use_cache: bool = True,
    ):
        self.language = language
        self.use_gpu = use_gpu
        self.use_cache = use_cache

        print("[NLP] Chargement des modeles open-source...")
        self.extractor = SpacyExtractor(lang=language, use_transformers=False)
        self.classifier = TransformersAlertClassifier(use_gpu=use_gpu)
        self.summarizer = AlertSummarizer(language=language, use_gpu=use_gpu)
        self.impact_calc = ImpactCalculator()

        self._call_count = 0
        self._total_tokens = 0
        self._cache_hits = 0

    def analyze(
        self,
        text: str,
        hs_code: str = "",
        target_countries: List[str] = None,
        category: str = "",
        classification: str = "",
        origin: str = "",
        maroc_relevant: Optional[bool] = None,
        use_cache: bool = True,
    ) -> RegulatoryAnalysis:
        """Analyse une alerte reglementaire.

        Les metadonnees category, classification et origin sont transmises au
        classifieur fine-tune. risk_decision n'est jamais utilise.
        """
        target_countries = target_countries or []
        cache_key = hashlib.md5(
            (
                f"{text[:200]}{hs_code}{''.join(target_countries)}"
                f"{category}{classification}{origin}{maroc_relevant}"
            ).encode("utf-8")
        ).hexdigest()[:12]

        if use_cache and self.use_cache:
            cached = self._cache_get(cache_key)
            if cached:
                self._cache_hits += 1
                return self._dict_to_analysis(cached)

        entities = self.extractor.extract_entities(text)
        entities_payload = [
            {
                "type": entity.type_,
                "value": entity.value,
                "start_char": entity.start_char,
                "end_char": entity.end_char,
                "confidence": entity.confidence,
            }
            for entity in entities
        ]

        countries_found = self.extractor.extract_countries(text)
        hs_codes_found = self.extractor.extract_hs_codes(text)
        dates_found = self.extractor.extract_dates(text)

        if hs_code and hs_code not in hs_codes_found:
            hs_codes_found.append(hs_code)
        if target_countries:
            countries_found.extend(target_countries)
            countries_found = list(set(countries_found))

        context = {
            "hs_code": hs_code,
            "target_countries": target_countries,
        }

        logger.info("OpenSourceRegulatoryAnalyzer using fine-tuned classifier")
        alert_classification = self.classifier.classify(
            text,
            category=category,
            classification=classification,
            origin=origin,
            context=context,
        )

        impact_data = self.impact_calc.calculate_export_impact(
            impact_score=alert_classification.impact_score,
            target_countries=countries_found,
            hs_codes=hs_codes_found,
        )
        final_impact_score = impact_data["combined_impact"]

        summary = self.summarizer.summarize(text)
        titre_fr = self._translate_title(text, alert_classification.level)
        resume_fr = summary.short
        action_requise = "\n".join(summary.action_items) if summary.action_items else "A determiner"
        impact_export = FrenchContentGenerator.generate_impact_summary(
            alert_title=titre_fr,
            countries=countries_found,
            risk_level=alert_classification.level,
            products=hs_codes_found,
        )
        date_vigueur = self._extract_date(dates_found) if dates_found else None

        analysis = RegulatoryAnalysis(
            titre_fr=titre_fr,
            niveau=alert_classification.level,
            pays_concernes=countries_found,
            produits=hs_codes_found,
            impact_score=final_impact_score,
            resume_fr=resume_fr,
            impact_export=impact_export,
            action_requise=action_requise,
            date_vigueur=date_vigueur,
            source_fiable=True,
            confiance=alert_classification.confidence,
            keywords=alert_classification.keywords,
            reasoning=alert_classification.reasoning,
            entities=entities_payload,
            category=category,
            classification=classification,
            origin=origin,
            maroc_relevant=maroc_relevant,
        )

        if use_cache and self.use_cache:
            self._cache_set(cache_key, asdict(analysis))

        self._call_count += 1
        logger.info("OpenSourceRegulatoryAnalyzer analysis completed")
        return analysis

    def _translate_title(self, text: str, level: str) -> str:
        """Genere un titre francais concis."""
        first_sentence = (text.split(".")[0] if text else "").strip()
        first_sentence = first_sentence[:100] or "Alerte reglementaire"
        return f"[{level}] {first_sentence}"

    def _extract_date(self, dates: List[str]) -> Optional[str]:
        """Extrait une date deja normalisee au format YYYY-MM-DD."""
        if not dates:
            return None

        import re

        date_str = dates[0]
        match = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_str)
        return date_str if match else None

    def upgrade_regulatory_watch(self, alerts: List[Dict]) -> List[RegulatoryAnalysis]:
        """Analyse un batch d'alertes brutes de regulatory_watch.py."""
        results = []
        for alert in alerts:
            text = f"{alert.get('titre', '')} {alert.get('resume', alert.get('description', ''))}"
            analysis = self.analyze(
                text=text,
                hs_code=alert.get("hs_code", ""),
                target_countries=alert.get("target_countries", []),
                category=alert.get("category", ""),
                classification=alert.get("classification", ""),
                origin=alert.get("origin", ""),
                maroc_relevant=alert.get("maroc_relevant"),
            )
            results.append(analysis)
        return results

    def _cache_get(self, key: str) -> Optional[Dict]:
        """Recupere une entree du cache."""
        cache_file = CACHE_DIR / f"nlp_{key}.json"
        if not cache_file.exists():
            return None

        age = (datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)).days
        if age > CACHE_TTL_DAYS:
            cache_file.unlink()
            return None

        try:
            with open(cache_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _cache_set(self, key: str, data: Dict):
        """Sauvegarde une entree en cache."""
        cache_file = CACHE_DIR / f"nlp_{key}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        except Exception as exc:
            logger.warning("Cache write error: %s", exc)

    def _dict_to_analysis(self, data: Dict) -> RegulatoryAnalysis:
        """Convertit un dict en RegulatoryAnalysis."""
        return RegulatoryAnalysis(
            titre_fr=data.get("titre_fr", ""),
            niveau=data.get("niveau", "INFO"),
            pays_concernes=data.get("pays_concernes", []),
            produits=data.get("produits", []),
            impact_score=data.get("impact_score", 0),
            resume_fr=data.get("resume_fr", ""),
            impact_export=data.get("impact_export", ""),
            action_requise=data.get("action_requise", ""),
            date_vigueur=data.get("date_vigueur"),
            source_fiable=data.get("source_fiable", True),
            confiance=data.get("confiance", 0.0),
            keywords=data.get("keywords"),
            reasoning=data.get("reasoning", ""),
            entities=data.get("entities"),
            category=data.get("category", ""),
            classification=data.get("classification", ""),
            origin=data.get("origin", ""),
            maroc_relevant=data.get("maroc_relevant"),
        )

    @property
    def stats(self) -> Dict:
        """Retourne les statistiques d'utilisation."""
        return {
            "calls": self._call_count,
            "cache_hits": self._cache_hits,
            "tokens_saved": self._cache_hits * 500,
            "cache_hit_rate": self._cache_hits / max(1, self._call_count),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = OpenSourceRegulatoryAnalyzer(language="en", use_gpu=False)

    test_alert = (
        "Salmonella spp. in sesame seeds from Nigeria. Border rejection "
        "notification for nuts, nut products and seeds."
    )
    result = analyzer.analyze(
        text=test_alert,
        category="nuts, nut products and seeds",
        classification="border rejection notification",
        origin="Nigeria",
        maroc_relevant=True,
    )

    print(f"Niveau: {result.niveau}")
    print(f"Impact: {result.impact_score:.1f}/100")
    print(f"Confiance: {result.confiance:.2f}")
    print(f"Keywords: {result.keywords}")
    print(f"Reasoning: {result.reasoning}")
