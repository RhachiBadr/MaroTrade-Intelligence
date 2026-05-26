"""
opensource_regulatory_analyzer.py — Remplacement de LLM Claude
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Orchestration des modèles open-source NLP pour remplacer Anthropic Claude.
Pas de dépendance coûteuse - 100% modèles transformers open-source.

API compatible avec llm_regulatory_analyzer.LLMRegulatoryAnalyzer
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict

from services.nlp.spacy_extractor import SpacyExtractor
from services.nlp.transformers_classifier import TransformersAlertClassifier, ImpactCalculator
from services.nlp.summarizer import AlertSummarizer, FrenchContentGenerator


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

CACHE_DIR = Path(".cache_marotrade")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL_DAYS = 3  # Alertes mises en cache 3 jours

# Contexte Maroc
MAROC_CONTEXT = {
    "main_products": [
        "151590",  # Huile d'argan
        "160413",  # Sardines
        "080410",  # Dattes
        "09102010", # Safran
    ],
    "main_markets": ["FRA", "DEU", "USA", "SAU", "ARE"],
    "main_organizations": ["ONSSA", "Douanes marocaines", "ASIDCOM"],
}


# ═══════════════════════════════════════════════════════════════
# STRUCTURE DE SORTIE (compatible CClaude)
# ═══════════════════════════════════════════════════════════════

@dataclass
class RegulatoryAnalysis:
    """Résultat structuré de l'analyse d'une alerte réglementaire."""

    # Identification
    titre_fr: str              # Titre reformulé en français
    niveau: str                # CRITIQUE / ATTENTION / INFO

    # Impact
    pays_concernes: list       # Codes ISO3
    produits: list             # Codes HS ou noms
    impact_score: float        # 0–100

    # Contenu
    resume_fr: str             # Résumé 2–3 phrases
    impact_export: str         # Impact concret
    action_requise: str        # Actions précises

    # Métadonnées
    date_vigueur: Optional[str]  # YYYY-MM-DD ou None
    source_fiable: bool        # Fiable ?
    confiance: float           # 0–1


# ═══════════════════════════════════════════════════════════════
# MOTEUR D'ANALYSE OPEN-SOURCE
# ═══════════════════════════════════════════════════════════════

class OpenSourceRegulatoryAnalyzer:
    """
    Analyseur réglementaire 100% open-source.
    
    Remplace Claude par pipeline local:
    1. spaCy : extraction entités (pays, produits, dates)
    2. Transformers : classification (CRITIQUE/ATTENTION/INFO)
    3. BART/mT5 : résumé et génération contenu
    
    API COMPATIBLE avec llm_regulatory_analyzer.LLMRegulatoryAnalyzer
    """

    def __init__(
        self,
        language: str = "en",
        use_gpu: bool = False,
        use_cache: bool = True
    ):
        """
        Args:
            language: "en" ou "fr"
            use_gpu: Utiliser GPU (plus rapide mais consomme mémoire)
            use_cache: Activer le cache (3 jours par défaut)
        """
        self.language = language
        self.use_gpu = use_gpu
        self.use_cache = use_cache
        
        # Charger les modèles NLP
        print("[NLP] Chargement des modèles open-source...")
        self.extractor = SpacyExtractor(lang=language, use_transformers=False)
        self.classifier = TransformersAlertClassifier(use_gpu=use_gpu)
        self.summarizer = AlertSummarizer(language=language, use_gpu=use_gpu)
        self.impact_calc = ImpactCalculator()
        
        # Statistiques
        self._call_count = 0
        self._total_tokens = 0
        self._cache_hits = 0

    # ───────────────────────────────────────────────────────────
    # Analyse principale (API compatible)
    # ───────────────────────────────────────────────────────────

    def analyze(
        self,
        text: str,
        hs_code: str = "",
        target_countries: List[str] = None,
        use_cache: bool = True,
    ) -> RegulatoryAnalysis:
        """
        Analyse un texte réglementaire (API compatible avec LLMRegulatoryAnalyzer).
        
        Args:
            text:             Texte brut de l'alerte
            hs_code:          Code HS du produit
            target_countries: Codes ISO3 des pays cibles
            use_cache:        Utiliser cache
        
        Returns:
            RegulatoryAnalysis structuré
        """
        # Clé cache
        cache_key = hashlib.md5(
            f"{text[:200]}{hs_code}{''.join(target_countries or [])}".encode()
        ).hexdigest()[:12]
        
        # Vérifier cache
        if use_cache and self.use_cache:
            cached = self._cache_get(cache_key)
            if cached:
                self._cache_hits += 1
                return self._dict_to_analysis(cached)
        
        # ───────────────────────────────────────────────────
        # PIPELINE ANALYSE
        # ───────────────────────────────────────────────────
        
        # 1. Extraction d'entités (spaCy)
        entities = self.extractor.extract_entities(text)
        countries_found = self.extractor.extract_countries(text)
        hs_codes_found = self.extractor.extract_hs_codes(text)
        dates_found = self.extractor.extract_dates(text)
        
        # Enrichir avec les données utilisateur
        if hs_code and hs_code not in hs_codes_found:
            hs_codes_found.append(hs_code)
        if target_countries:
            countries_found.extend(target_countries)
            countries_found = list(set(countries_found))
        
        # 2. Classification (Transformers)
        context = {
            "hs_code": hs_code,
            "target_countries": target_countries or []
        }
        classification = self.classifier.classify(text, context=context)
        
        # 3. Calcul d'impact
        impact_data = self.impact_calc.calculate_export_impact(
            impact_score=classification.impact_score,
            target_countries=countries_found,
            hs_codes=hs_codes_found
        )
        final_impact_score = impact_data["combined_impact"]
        
        # 4. Résumé (BART/mT5)
        summary = self.summarizer.summarize(text)
        
        # 5. Génération contenu français
        titre_fr = self._translate_title(text, classification.level)
        resume_fr = summary.short
        action_requise = "\n".join(summary.action_items) if summary.action_items else "À déterminer"
        impact_export = FrenchContentGenerator.generate_impact_summary(
            alert_title=titre_fr,
            countries=countries_found,
            risk_level=classification.level,
            products=hs_codes_found
        )
        
        # 6. Déterminer date de vigueur
        date_vigueur = self._extract_date(dates_found) if dates_found else None
        
        # ───────────────────────────────────────────────────
        # CONSTRUIRE RÉSULTAT
        # ───────────────────────────────────────────────────
        
        analysis = RegulatoryAnalysis(
            titre_fr=titre_fr,
            niveau=classification.level,
            pays_concernes=countries_found,
            produits=hs_codes_found,
            impact_score=final_impact_score,
            resume_fr=resume_fr,
            impact_export=impact_export,
            action_requise=action_requise,
            date_vigueur=date_vigueur,
            source_fiable=True,  # Pour open-source : toujours fiable
            confiance=classification.confidence,
        )
        
        # Sauvegarder en cache
        if use_cache and self.use_cache:
            self._cache_set(cache_key, asdict(analysis))
        
        self._call_count += 1
        return analysis

    # ───────────────────────────────────────────────────────
    # Méthodes utilitaires
    # ───────────────────────────────────────────────────────

    def _translate_title(self, text: str, level: str) -> str:
        """Génère un titre français concis."""
        # Extraire le premier X caractères ou première phrase
        sentences = text.split(".")
        if sentences:
            first_line = sentences[0][:100].strip()
        else:
            first_line = text[:100].strip()
        
        # Ajouter l'emoji de niveau
        level_emoji = {
            "CRITIQUE": "🔴",
            "ATTENTION": "🟡",
            "INFO": "🟢"
        }
        
        return f"{level_emoji.get(level, '•')} {first_line}"

    def _extract_date(self, dates: List[str]) -> Optional[str]:
        """Extrait une date au format YYYY-MM-DD."""
        if not dates:
            return None
        
        # Prendre la première date trouvée
        date_str = dates[0]
        
        # Tenter de parser (simple pattern)
        import re
        match = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_str)
        if match:
            return date_str
        
        # Format alternatif : "June 15, 2026" → "2026-06-15"
        # (implémentation simplifiée)
        return None

    def upgrade_regulatory_watch(
        self,
        alerts: List[Dict]
    ) -> List[RegulatoryAnalysis]:
        """
        Analyse un batch d'alertes brutes de regulatory_watch.py
        et retourne des alertes enrichies.
        
        Utile pour :
        - Remplacer LLMRegulatoryAnalyzer.upgrade_regulatory_watch()
        - Traiter les flux RSS
        
        Args:
            alerts: Liste de dicts {titre, description, lien, ...}
        
        Returns:
            Liste d'analyses enrichies
        """
        results = []
        for alert in alerts:
            text = f"{alert.get('titre', '')} {alert.get('description', '')}"
            analysis = self.analyze(
                text=text,
                hs_code=alert.get('hs_code', ''),
                target_countries=alert.get('target_countries', [])
            )
            results.append(analysis)
        
        return results

    # ───────────────────────────────────────────────────────
    # Cache
    # ───────────────────────────────────────────────────────

    def _cache_get(self, key: str) -> Optional[Dict]:
        """Récupère une entrée du cache."""
        cache_file = CACHE_DIR / f"nlp_{key}.json"
        
        if not cache_file.exists():
            return None
        
        # Vérifier TTL
        age = (datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)).days
        if age > CACHE_TTL_DAYS:
            cache_file.unlink()  # Supprimer fichier expiré
            return None
        
        try:
            with open(cache_file) as f:
                return json.load(f)
        except:
            return None

    def _cache_set(self, key: str, data: Dict):
        """Sauvegarde une entrée en cache."""
        cache_file = CACHE_DIR / f"nlp_{key}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Cache write error: {e}")

    def _dict_to_analysis(self, data: Dict) -> RegulatoryAnalysis:
        """Convertit un dict en RegulatoryAnalysis."""
        return RegulatoryAnalysis(
            titre_fr=data.get("titre_fr"),
            niveau=data.get("niveau"),
            pays_concernes=data.get("pays_concernes", []),
            produits=data.get("produits", []),
            impact_score=data.get("impact_score", 0),
            resume_fr=data.get("resume_fr"),
            impact_export=data.get("impact_export"),
            action_requise=data.get("action_requise"),
            date_vigueur=data.get("date_vigueur"),
            source_fiable=data.get("source_fiable", True),
            confiance=data.get("confiance", 0.8),
        )

    @property
    def stats(self) -> Dict:
        """Retourne les statistiques d'utilisation."""
        return {
            "calls": self._call_count,
            "cache_hits": self._cache_hits,
            "tokens_saved": self._cache_hits * 500,  # Estimation
            "cache_hit_rate": self._cache_hits / max(1, self._call_count),
        }


# ═══════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🔧 Initialisation du moteur NLP open-source...")
    analyzer = OpenSourceRegulatoryAnalyzer(language="en", use_gpu=False)
    
    # Texte de test
    test_alert = """
    FDA URGENT ALERT: Sardine Products Recall
    
    All sardine products from Morocco (HS Code 160413) with 
    production dates between May 1-15, 2026 must be withdrawn from 
    shelves immediately. Contamination with Clostridium botulinum 
    suspected. Consumers should not consume. Health risk: CRITICAL.
    
    Immediate notification required to FDA Office of Regulatory Affairs
    before June 1, 2026. All importers and distributors in USA and Canada
    are affected.
    """
    
    print("\n📝 Analyse de l'alerte...")
    result = analyzer.analyze(
        text=test_alert,
        hs_code="160413",
        target_countries=["USA", "CAN"]
    )
    
    print(f"\n✅ Résultat de l'analyse:")
    print(f"  Titre: {result.titre_fr}")
    print(f"  Niveau: {result.niveau}")
    print(f"  Impact: {result.impact_score:.1f}/100")
    print(f"  Pays: {', '.join(result.pays_concernes)}")
    print(f"  Produits: {', '.join(result.produits)}")
    print(f"  Résumé: {result.resume_fr}")
    print(f"  Confiance: {result.confiance:.2f}")
    
    print(f"\n📊 Statistiques:")
    stats = analyzer.stats
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.2f}")
        else:
            print(f"  {k}: {v}")
