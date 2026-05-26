"""
transformers_classifier.py — Classification d'alertes réglementaires
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Utilise DistilBERT et RoBERTa (HuggingFace transformers) pour :
- Classifier les alertes (CRITIQUE / ATTENTION / INFO)
- Calculer un score d'impact (0-100)
- Déterminer les produits concernés
"""

from typing import Dict, Tuple, List
from dataclasses import dataclass
import torch
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
import numpy as np


@dataclass
class AlertClassification:
    """Résultat de classification d'une alerte."""
    level: str          # "CRITIQUE", "ATTENTION", "INFO"
    impact_score: float # 0-100
    confidence: float   # 0-1 (confiance du modèle)
    keywords: List[str] # Mots-clés identifiés
    reasoning: str      # Explication de la classification


class TransformersAlertClassifier:
    """
    Classifie les alertes réglementaires en niveaux de risque
    en utilisant des modèles transformers fine-tunés.
    """

    def __init__(self, use_gpu: bool = False):
        """
        Args:
            use_gpu: Utiliser GPU si disponible (plus rapide)
        """
        self.device = 0 if use_gpu and torch.cuda.is_available() else -1
        
        # Pipeline zero-shot classification (flexible, pas d'entraînement préalable)
        # Alternative : utiliser un modèle fine-tuné custom
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",  # Multilingue, multilabel
            device=self.device
        )
        
        # Modèle pour estimer l'impact (utilisation de NLI pour inférence)
        self.tokenizer = AutoTokenizer.from_pretrained(
            "facebook/bart-large-mnli"
        )
        
        # Thresholds de classification
        self.risk_keywords = {
            "CRITIQUE": [
                "blocage", "interdiction", "bannir", "suspendu", "recall",
                "pathogène", "contaminé", "cancérigène", "toxique", "dangereux",
                "urgence", "immédiat", "arrêté", "fermé"
            ],
            "ATTENTION": [
                "nouveau", "norme", "obligation", "conformité", "délai",
                "prochainement", "applicable", "modification", "changement",
                "doit", "devra", "sera", "seront"
            ],
            "INFO": [
                "clarification", "mise à jour", "information", "consultation",
                "proposition", "draft", "commentaires", "feedback"
            ]
        }

    def classify(self, text: str, context: Dict = None) -> AlertClassification:
        """
        Classe une alerte réglementaire par rapport à la PME marocaine.
        
        Args:
            text: Texte de l'alerte
            context: Contexte optionnel {
                "hs_code": "151590",
                "target_countries": ["FRA", "DEU"]
            }
        
        Returns:
            AlertClassification structuré
        """
        context = context or {}
        
        # Enrichir le texte avec le contexte si disponible
        enriched_text = text
        if context.get("hs_code"):
            enriched_text += f"\nCode HS de l'exportateur: {context['hs_code']}"
        if context.get("target_countries"):
            enriched_text += f"\nMarchés cibles: {', '.join(context['target_countries'])}"
        
        # Hypothèses de classification pour zero-shot
        candidate_labels = ["CRITIQUE: Blocage possible", "ATTENTION: Action requise", "INFO: Veille"]
        
        # Zero-shot classification
        result = self.classifier(
            enriched_text[:512],  # Limiter à 512 tokens (limite BERT)
            candidate_labels,
            multi_class=False
        )
        
        # Parser les résultats
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        
        # Extraire le niveau de risque du label
        if "CRITIQUE" in top_label:
            level = "CRITIQUE"
            base_impact = 85
        elif "ATTENTION" in top_label:
            level = "ATTENTION"
            base_impact = 60
        else:
            level = "INFO"
            base_impact = 25
        
        # Ajuster l'impact par analyse des mots-clés
        impact_score = self._calculate_impact_score(text, level, top_score)
        keywords = self._extract_keywords(text)
        reasoning = self._generate_reasoning(text, level, keywords)
        
        return AlertClassification(
            level=level,
            impact_score=impact_score,
            confidence=top_score,
            keywords=keywords,
            reasoning=reasoning
        )

    def _calculate_impact_score(self, text: str, level: str, classifier_confidence: float) -> float:
        """
        Calcule le score d'impact (0-100) basé sur le niveau et mots-clés.
        """
        base_scores = {
            "CRITIQUE": 85,
            "ATTENTION": 60,
            "INFO": 25
        }
        
        score = base_scores[level]
        
        # Bonus si mots-clés critiques trouvés
        text_lower = text.lower()
        critical_keywords_count = sum(1 for kw in self.risk_keywords["CRITIQUE"] if kw in text_lower)
        score += critical_keywords_count * 3
        
        # Multiplicateur de confiance
        score = score * (0.5 + 0.5 * classifier_confidence)
        
        # Clamper entre 0 et 100
        return min(100.0, max(0.0, score))

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés de risque présents dans le texte."""
        text_lower = text.lower()
        found_keywords = set()
        
        for level_keywords in self.risk_keywords.values():
            for kw in level_keywords:
                if kw in text_lower:
                    found_keywords.add(kw)
        
        return list(found_keywords)[:10]  # Top 10

    def _generate_reasoning(self, text: str, level: str, keywords: List[str]) -> str:
        """Génère une explication de la classification."""
        if not keywords:
            return f"Classification {level} basée sur analyse contextuelle du texte."
        
        return f"Classification {level} en raison de la présence de mots-clés : {', '.join(keywords[:3])}."

    def batch_classify(self, texts: List[str], contexts: List[Dict] = None) -> List[AlertClassification]:
        """Classifie un batch de textes (plus efficace)."""
        contexts = contexts or [{}] * len(texts)
        return [self.classify(text, ctx) for text, ctx in zip(texts, contexts)]


class ImpactCalculator:
    """
    Calcule l'impact sur les exportations marocaines en cross-checking
    avec les produits et marchés cibles.
    """

    # Poids par marché
    MARKET_WEIGHTS = {
        "FRA": 0.15, "DEU": 0.14, "ESP": 0.12, "ITA": 0.10, "NLD": 0.08,  # UE
        "USA": 0.12,  # USA
        "SAU": 0.06, "ARE": 0.05, "QAT": 0.04, "KWT": 0.03,  # Arabie
        "EGY": 0.05, "JPN": 0.04,  # Autres
    }

    # Sensibilité par produit
    PRODUCT_SENSITIVITY = {
        "151590": 0.95,  # Huile argan très sensible
        "160413": 0.92,  # Sardines
        "080410": 0.85,  # Dattes
        "09102010": 0.80,  # Safran
        "090920": 0.80,  # Cumin
        "570110": 0.60,  # Tapis
    }

    def calculate_export_impact(
        self,
        impact_score: float,
        target_countries: List[str],
        hs_codes: List[str]
    ) -> Dict:
        """
        Calcule l'impact réel sur les exportations.
        
        Returns:
            {
                "markets_affected": 0-1,
                "products_affected": 0-1,
                "combined_impact": 0-100
            }
        """
        # Impact par marché
        market_impact = sum(
            self.MARKET_WEIGHTS.get(country, 0.01)
            for country in target_countries
        )
        market_impact = min(1.0, market_impact)
        
        # Impact par produit
        product_impact = max(
            (self.PRODUCT_SENSITIVITY.get(code, 0.5) for code in hs_codes),
            default=0.5
        )
        
        # Impact combiné
        combined = impact_score * 0.7 + (market_impact * product_impact * 100) * 0.3
        
        return {
            "markets_affected": market_impact,
            "products_affected": product_impact,
            "combined_impact": min(100.0, combined)
        }


# Test
if __name__ == "__main__":
    classifier = TransformersAlertClassifier(use_gpu=False)
    
    # Test texte
    test_alert = """
    FDA ALERT: Recalled sardines from Morocco (HS 160413).
    Potential botulism contamination. All shipments must be seized.
    Immediate detention required at US ports.
    """
    
    result = classifier.classify(test_alert, context={"hs_code": "160413"})
    print(f"Niveau: {result.level}")
    print(f"Impact Score: {result.impact_score:.1f}")
    print(f"Confiance: {result.confidence:.2f}")
    print(f"Raison: {result.reasoning}")
