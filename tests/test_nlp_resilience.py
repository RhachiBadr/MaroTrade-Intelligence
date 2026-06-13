import os
import unittest
from unittest.mock import patch

from services.nlp.transformers_classifier import TransformersAlertClassifier
from services.watch.regulatory_watch import RegulatoryWatchEngine


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


if __name__ == "__main__":
    unittest.main()
