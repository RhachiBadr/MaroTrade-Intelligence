"""Classification d'alertes reglementaires avec Transformers.

Le classifieur principal est le modele RASFF XLM-RoBERTa fine-tune
Benchmark 4. L'ancien zero-shot facebook/bart-large-mnli reste disponible
en fallback si le modele local est absent ou echoue.
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline


logger = logging.getLogger(__name__)

DEFAULT_LABELS = {
    0: "ATTENTION",
    1: "CRITIQUE",
    2: "INFO",
}


@dataclass
class AlertClassification:
    """Resultat de classification d'une alerte."""

    level: str
    impact_score: float
    confidence: float
    keywords: List[str]
    reasoning: str


class TransformersAlertClassifier:
    """Classifie les alertes en CRITIQUE / ATTENTION / INFO."""

    def __init__(self, use_gpu: bool = False, model_path: str = None):
        """
        Args:
            use_gpu: Utiliser CUDA si disponible.
            model_path: Chemin optionnel vers le modele fine-tune RASFF.
        """
        self.use_gpu = use_gpu
        self.local_device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
        self.zero_shot_device = 0 if self.local_device.type == "cuda" else -1

        self.local_model_available = False
        self.local_model = None
        self.local_tokenizer = None
        self.classifier = None
        self.tokenizer = None
        self.id2label = DEFAULT_LABELS.copy()
        self.zero_shot_enabled = os.getenv("NLP_ZERO_SHOT_FALLBACK_ENABLED", "false").lower() == "true"
        self.local_model_enabled = os.getenv("NLP_LOCAL_MODEL_ENABLED", "true").lower() == "true"

        project_root = Path(__file__).resolve().parents[2]
        self.model_path = Path(
            model_path
            or os.getenv("RASFF_NLP_MODEL_PATH", "")
            or project_root / "models" / "final_rasff_nlp_pipeline"
        )

        self.risk_keywords = {
            "CRITIQUE": [
                "blocage", "interdiction", "bannir", "suspendu", "recall",
                "pathogene", "contamine", "cancerigene", "toxique", "dangereux",
                "urgence", "immediat", "arrete", "ferme", "contamination",
                "withdrawal", "serious", "danger",
            ],
            "ATTENTION": [
                "nouveau", "norme", "obligation", "conformite", "delai",
                "prochainement", "applicable", "modification", "changement",
                "doit", "devra", "sera", "seront", "warning", "updated",
            ],
            "INFO": [
                "clarification", "mise a jour", "information", "consultation",
                "proposition", "draft", "commentaires", "feedback",
            ],
        }

        if self.local_model_enabled and self._load_local_classifier():
            logger.info("Loaded fine-tuned RASFF classifier")
            logger.info("Using local fine-tuned classifier")
        else:
            if not self.local_model_enabled:
                logger.info("Fine-tuned RASFF classifier disabled by NLP_LOCAL_MODEL_ENABLED")
            if self.zero_shot_enabled and self._load_zero_shot_fallback():
                logger.warning("Fine-tuned classifier unavailable, using zero-shot fallback")
            else:
                logger.warning("Fine-tuned classifier unavailable, using lightweight rule-based fallback")

    def _load_local_classifier(self) -> bool:
        """Charge le modele RASFF local si le dossier est disponible."""
        if not self.model_path.exists():
            return False

        try:
            self.local_tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.local_model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.local_model.to(self.local_device)
            self.local_model.eval()
            self.id2label = self._load_label_mapping()
            self.local_model_available = True
            return True
        except Exception as exc:
            if "1455" in str(exc) or "paging file is too small" in str(exc).lower():
                logger.warning(
                    "Fine-tuned classifier unavailable: insufficient Windows virtual memory (error 1455)"
                )
            else:
                logger.exception("Fine-tuned classifier unavailable: %s", exc)
            self.local_model_available = False
            self.local_model = None
            self.local_tokenizer = None
            return False

    def _load_label_mapping(self) -> Dict[int, str]:
        """Charge label_mapping.json si disponible."""
        mapping_path = self.model_path / "label_mapping.json"
        if not mapping_path.exists():
            return DEFAULT_LABELS.copy()

        try:
            with open(mapping_path, encoding="utf-8") as f:
                payload = json.load(f)
            id2label = payload.get("id2label", {})
            return {int(k): str(v) for k, v in id2label.items()} or DEFAULT_LABELS.copy()
        except Exception as exc:
            logger.warning("Could not load label_mapping.json, using default mapping: %s", exc)
            return DEFAULT_LABELS.copy()

    def _load_zero_shot_fallback(self) -> bool:
        """Charge l'ancien fallback zero-shot."""
        if not self.zero_shot_enabled:
            return False
        logger.info("Using zero-shot fallback classifier")
        try:
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=self.zero_shot_device,
            )
            self.tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
            return True
        except Exception as exc:
            logger.warning("Zero-shot fallback unavailable, using lightweight rules: %s", exc)
            self.classifier = None
            self.tokenizer = None
            return False

    def build_model_input(
        self,
        text: str,
        category: str = "",
        classification: str = "",
        origin: str = "",
    ) -> str:
        """Construit l'entree exacte du modele Benchmark 4, sans risk_decision."""
        return (
            f"Texte alerte : {text}. "
            f"Catégorie produit : {category}. "
            f"Type notification : {classification}. "
            f"Pays origine : {origin}."
        )

    def classify(
        self,
        text: str,
        category: str = "",
        classification: str = "",
        origin: str = "",
        context: Dict = None,
    ) -> AlertClassification:
        """
        Classe une alerte reglementaire.

        Les champs category, classification et origin sont les features du
        modele RASFF Benchmark 4. risk_decision n'est jamais utilise.
        """
        if isinstance(category, dict) and context is None:
            # Compatibilite avec l'ancien appel classify(text, context).
            context = category
            category = ""

        if self.local_model_available:
            try:
                return self._classify_with_local_model(
                    text=text,
                    category=category,
                    classification=classification,
                    origin=origin,
                )
            except Exception as exc:
                logger.exception("Local fine-tuned inference failed: %s", exc)
                if self.classifier is None and self.zero_shot_enabled:
                    self._load_zero_shot_fallback()

        if self.classifier is not None:
            return self._classify_with_zero_shot(text=text, context=context or {})
        return self._classify_with_rules(text)

    def _classify_with_local_model(
        self,
        text: str,
        category: str = "",
        classification: str = "",
        origin: str = "",
    ) -> AlertClassification:
        """Inference avec le modele local XLM-RoBERTa fine-tune."""
        logger.info("Using local fine-tuned classifier")
        model_input = self.build_model_input(text, category, classification, origin)
        encoded = self.local_tokenizer(
            model_input,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        encoded = {key: value.to(self.local_device) for key, value in encoded.items()}

        with torch.no_grad():
            outputs = self.local_model(**encoded)
            probabilities = torch.softmax(outputs.logits, dim=-1).squeeze(0)

        predicted_id = int(torch.argmax(probabilities).item())
        confidence = float(probabilities[predicted_id].item())
        level = self.id2label.get(predicted_id, DEFAULT_LABELS.get(predicted_id, "INFO"))
        if level not in {"ATTENTION", "CRITIQUE", "INFO"}:
            level = "INFO"

        keywords = self._extract_keywords(text)
        return AlertClassification(
            level=level,
            impact_score=self._calculate_impact_score(text, level, confidence),
            confidence=confidence,
            keywords=keywords,
            reasoning=self._generate_reasoning(text, level, keywords),
        )

    def _classify_with_zero_shot(self, text: str, context: Dict = None) -> AlertClassification:
        """Ancien classifieur zero-shot conserve comme fallback."""
        logger.info("Using zero-shot fallback classifier")
        if self.classifier is None and not self._load_zero_shot_fallback():
            return self._classify_with_rules(text)

        context = context or {}
        enriched_text = text
        if context.get("hs_code"):
            enriched_text += f"\nCode HS de l'exportateur: {context['hs_code']}"
        if context.get("target_countries"):
            enriched_text += f"\nMarches cibles: {', '.join(context['target_countries'])}"

        candidate_labels = ["CRITIQUE: Blocage possible", "ATTENTION: Action requise", "INFO: Veille"]
        result = self.classifier(enriched_text[:512], candidate_labels, multi_label=False)

        top_label = result["labels"][0]
        top_score = float(result["scores"][0])

        if "CRITIQUE" in top_label:
            level = "CRITIQUE"
        elif "ATTENTION" in top_label:
            level = "ATTENTION"
        else:
            level = "INFO"

        keywords = self._extract_keywords(text)
        return AlertClassification(
            level=level,
            impact_score=self._calculate_impact_score(text, level, top_score),
            confidence=top_score,
            keywords=keywords,
            reasoning=self._generate_reasoning(text, level, keywords),
        )

    def _classify_with_rules(self, text: str) -> AlertClassification:
        """Fallback leger et deterministe lorsque les modeles sont indisponibles."""
        logger.info("Using lightweight rule-based classifier")
        text_lower = text.lower()
        matches = {
            level: [keyword for keyword in keywords if keyword in text_lower]
            for level, keywords in self.risk_keywords.items()
        }

        if matches["CRITIQUE"]:
            level, confidence = "CRITIQUE", min(0.80, 0.62 + len(matches["CRITIQUE"]) * 0.03)
        elif matches["ATTENTION"]:
            level, confidence = "ATTENTION", min(0.75, 0.58 + len(matches["ATTENTION"]) * 0.03)
        else:
            level, confidence = "INFO", 0.52

        keywords = self._extract_keywords(text)
        return AlertClassification(
            level=level,
            impact_score=self._calculate_impact_score(text, level, confidence),
            confidence=confidence,
            keywords=keywords,
            reasoning=self._generate_reasoning(text, level, keywords),
        )

    def _calculate_impact_score(self, text: str, level: str, classifier_confidence: float) -> float:
        """Calcule le score d'impact 0-100."""
        base_scores = {
            "CRITIQUE": 85,
            "ATTENTION": 60,
            "INFO": 25,
        }

        score = base_scores.get(level, 25)
        text_lower = text.lower()
        critical_keywords_count = sum(
            1 for kw in self.risk_keywords["CRITIQUE"] if kw in text_lower
        )
        score += critical_keywords_count * 3
        score = score * (0.5 + 0.5 * classifier_confidence)
        return min(100.0, max(0.0, score))

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-cles de risque presents dans le texte."""
        text_lower = text.lower()
        found_keywords = set()

        for level_keywords in self.risk_keywords.values():
            for keyword in level_keywords:
                if keyword in text_lower:
                    found_keywords.add(keyword)

        return list(found_keywords)[:10]

    def _generate_reasoning(self, text: str, level: str, keywords: List[str]) -> str:
        """Genere une explication courte de la classification."""
        if not keywords:
            return f"Classification {level} basee sur analyse contextuelle du texte."

        return f"Classification {level} en raison de la presence de mots-cles : {', '.join(keywords[:3])}."

    def batch_classify(self, texts: List[str], contexts: List[Dict] = None) -> List[AlertClassification]:
        """Classifie un batch de textes avec compatibilite ancien contexte."""
        contexts = contexts or [{}] * len(texts)
        return [self.classify(text, context=context) for text, context in zip(texts, contexts)]


class ImpactCalculator:
    """Calcule l'impact sur les exportations marocaines."""

    MARKET_WEIGHTS = {
        "FRA": 0.15, "DEU": 0.14, "ESP": 0.12, "ITA": 0.10, "NLD": 0.08,
        "USA": 0.12,
        "SAU": 0.06, "ARE": 0.05, "QAT": 0.04, "KWT": 0.03,
        "EGY": 0.05, "JPN": 0.04,
    }

    PRODUCT_SENSITIVITY = {
        "151590": 0.95,
        "160413": 0.92,
        "080410": 0.85,
        "09102010": 0.80,
        "090920": 0.80,
        "570110": 0.60,
    }

    def calculate_export_impact(
        self,
        impact_score: float,
        target_countries: List[str],
        hs_codes: List[str],
    ) -> Dict:
        """Calcule l'impact combine marche / produit."""
        market_impact = sum(self.MARKET_WEIGHTS.get(country, 0.01) for country in target_countries)
        market_impact = min(1.0, market_impact)

        product_impact = max(
            (self.PRODUCT_SENSITIVITY.get(code, 0.5) for code in hs_codes),
            default=0.5,
        )

        combined = impact_score * 0.7 + (market_impact * product_impact * 100) * 0.3

        return {
            "markets_affected": market_impact,
            "products_affected": product_impact,
            "combined_impact": min(100.0, combined),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    classifier = TransformersAlertClassifier(use_gpu=False)

    test_alert = (
        "FDA ALERT: Recalled sardines from Morocco. Potential botulism "
        "contamination. All shipments must be seized."
    )

    result = classifier.classify(
        test_alert,
        category="fish and fish products",
        classification="alert notification",
        origin="Morocco",
        context={"hs_code": "160413"},
    )
    print(f"Niveau: {result.level}")
    print(f"Impact Score: {result.impact_score:.1f}")
    print(f"Confiance: {result.confidence:.2f}")
    print(f"Raison: {result.reasoning}")
