import unittest
from contextlib import redirect_stdout
from io import StringIO

from services.watch.regulatory_watch import (
    RegulatoryWatchEngine,
    _is_product_relevant_alert,
)


class TestRegulatoryProductFilter(unittest.TestCase):
    def test_leather_alert_matches_hs_4205(self):
        alert = {
            "titre": "New customs guidance for leather articles",
            "resume": "Import requirements for leather goods and other articles of leather.",
            "produits": ["4205"],
        }

        self.assertTrue(_is_product_relevant_alert(alert, "4205", "cuir"))

    def test_food_alert_does_not_match_hs_4205(self):
        alert = {
            "titre": "Salmonella spp. in turkey meat from Poland",
            "resume": "RASFF notification for poultry meat products.",
            "category": "poultry meat and poultry meat products",
        }

        self.assertFalse(_is_product_relevant_alert(alert, "4205", "cuir"))

    def test_engine_static_base_excludes_off_product_alerts(self):
        engine = RegulatoryWatchEngine(use_nlp=False)

        with redirect_stdout(StringIO()):
            alerts = engine.run("4205", "cuir", ["FRA"], include_live=False)

        self.assertTrue(all(alert.get("product_match") is True for alert in alerts))


if __name__ == "__main__":
    unittest.main()
