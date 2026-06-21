import os
import unittest
from unittest.mock import patch

from services.nlp.transformers_classifier import TransformersAlertClassifier
from services.watch.regulatory_watch import RegulatoryWatchEngine
from services.watch.regulatory_text import build_french_summary, translate_regulatory_title


class TestNlpResilience(unittest.TestCase):
    def test_rule_fallback_does_not_load_zero_shot_by_default(self):
        with (
            patch.dict(
                os.environ,
                {
                    "NLP_LOCAL_MODEL_ENABLED": "true",
                    "NLP_ZERO_SHOT_FALLBACK_ENABLED": "false",
                },
                clear=False,
            ),
            patch.object(TransformersAlertClassifier, "_load_local_classifier", return_value=False),
            patch.object(
                TransformersAlertClassifier,
                "_load_zero_shot_fallback",
                side_effect=AssertionError("zero-shot should remain disabled"),
            ),
        ):
            classifier = TransformersAlertClassifier(use_gpu=False)
            result = classifier.classify("Salmonella contamination and product recall")

        self.assertEqual(result.level, "CRITIQUE")
        self.assertGreater(result.confidence, 0.5)

    def test_regulatory_watch_initializes_nlp_lazily(self):
        engine = RegulatoryWatchEngine(use_nlp=True, lazy_nlp=True)

        self.assertIsNone(engine.nlp_analyzer)
        self.assertFalse(engine._nlp_initialization_attempted)

    def test_rasff_presentation_is_concise_and_french(self):
        alert = {
            "source": "RASFF",
            "category": "poultry meat and poultry meat products",
            "classification": "information notification for attention",
            "origin": "Poland",
        }
        title = translate_regulatory_title(
            "Salmonella spp. in turkey meat from Poland",
            alert["origin"],
        )
        summary = build_french_summary(alert, title)

        self.assertIn("viande de dinde", title)
        self.assertIn("Pologne", title)
        self.assertIn("Le réseau RASFF signale", summary)
        self.assertIn("notification d’information", summary)

    def test_curated_regulation_keeps_authoritative_level(self):
        class FakeAnalyzer:
            def analyze(self, **kwargs):
                return {
                    "niveau": "CRITIQUE",
                    "confidence": 0.99,
                    "impact_score": 64,
                    "reasoning": "Raw model signal.",
                }

        engine = RegulatoryWatchEngine(use_nlp=False, lazy_nlp=True)
        engine.nlp_analyzer = FakeAnalyzer()
        engine._nlp_initialization_attempted = True
        alert = {
            "id": "USA-CUSTOMS-TEST",
            "titre": "Droits compensateurs sur huiles végétales marocaines",
            "niveau": "INFO",
            "source": "US Customs",
            "pays": "USA",
            "date": "2022-05-01",
            "resume": "Le Maroc bénéficie de droits à 0 %.",
            "score_impact": 20,
            "relevance": 26,
            "product_match": True,
        }

        enriched = engine._enrich_alerts_with_nlp([alert], "151590", ["USA"])[0]

        self.assertEqual(enriched["niveau"], "INFO")
        self.assertEqual(enriched["raw_nlp_level"], "INFO")
        self.assertEqual(enriched["model_nlp_level"], "CRITIQUE")
        self.assertEqual(enriched["classification_basis"], "curated_source_level")
        self.assertIn("réglementation de référence", enriched["business_explanation"])


if __name__ == "__main__":
    unittest.main()
