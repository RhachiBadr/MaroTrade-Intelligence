import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

import api
import data_sources
import dynamic_growth
from services.scoring.scoring_engine import MarketScoringEngine
from services.auth.security import AuthContext, get_current_auth


def _dimension(name: str, score: float = 80.0) -> SimpleNamespace:
    return SimpleNamespace(
        nom=name,
        score=score,
        poids=0.2,
        contribution=score * 0.2,
        detail={"source": "test"},
        interpretation="Interprétation de test.",
    )


def _market_result(rank: int, code: str, score: float) -> SimpleNamespace:
    return SimpleNamespace(
        rank=rank,
        country_code=code,
        country_name={"ESP": "Espagne", "FRA": "France", "ITA": "Italie"}.get(code, code),
        score_final=score,
        score_weighted=score - 5,
        score_xgboost=score - 3,
        score_ml_v6=score,
        scoring_method="v6_market_attractiveness",
        v6_features_used=["log_value_usd", "distance_km"],
        v6_explanation=f"Explication v6 pour {code}.",
        v6_strengths=["Demande import significative."],
        v6_risks=["À valider commercialement."],
        v6_feature_snapshot={"import_value_usd": 10_000_000.0, "distance_km": 1_000.0},
        data_freshness={"trade_data": "données locales"},
        dimensions=[_dimension("Potentiel de marché")],
        shap_values={"Volume du marché": 1.5},
        top_atouts=["Demande import significative."],
        top_risques=["À valider commercialement."],
        accord_info={"accord": "Accord test", "droits": 0.0, "type": "ALE", "zone": "UE"},
        logistique_info={"distance_km": 1_000.0, "lpi": 3.8, "cout_conteneur_usd": 900.0},
    )


class TestPmeCalibration(unittest.TestCase):
    def setUp(self):
        # Calibration is stateless, so avoid loading the model artifact for unit tests.
        self.engine = MarketScoringEngine.__new__(MarketScoringEngine)

    def test_calibration_rewards_actionable_market(self):
        scores = np.array([80.0, 80.0])
        features = pd.DataFrame(
            [
                {
                    "log_value_usd": np.log1p(20_000_000),
                    "distance_km": 1_000,
                    "droits": 0,
                    "ocde_risk_score": 1,
                    "trend_score": 70,
                    "wb_available": 1,
                    "accord_score": 100,
                    "growth_lag1": 10,
                },
                {
                    "log_value_usd": np.log1p(500_000),
                    "distance_km": 9_000,
                    "droits": 15,
                    "ocde_risk_score": 6,
                    "trend_score": 30,
                    "wb_available": 0,
                    "accord_score": 0,
                    "growth_lag1": -5,
                },
            ]
        )

        calibrated = self.engine.calibrate_v6_scores_for_pme(scores, features)

        self.assertAlmostEqual(calibrated[0], 100.0)
        self.assertGreater(calibrated[0], calibrated[1])
        self.assertGreaterEqual(calibrated[1], 0.0)
        self.assertLessEqual(calibrated[1], 100.0)

    def test_empty_features_preserve_scores(self):
        scores = np.array([75.0, 50.0])
        calibrated = self.engine.calibrate_v6_scores_for_pme(scores, pd.DataFrame())
        np.testing.assert_array_equal(calibrated, scores)

    def test_tiny_fast_growing_market_is_penalized_for_sme_actionability(self):
        scores = np.array([100.0, 75.0])
        features = pd.DataFrame(
            [
                {
                    "log_value_usd": np.log1p(20_000),
                    "distance_km": 1_000,
                    "droits": 0,
                    "ocde_risk_score": 1,
                    "trend_score": 70,
                    "wb_available": 1,
                    "accord_score": 100,
                    "growth_lag1": 100,
                },
                {
                    "log_value_usd": np.log1p(20_000_000),
                    "distance_km": 2_000,
                    "droits": 0,
                    "ocde_risk_score": 1,
                    "trend_score": 60,
                    "wb_available": 1,
                    "accord_score": 100,
                    "growth_lag1": 8,
                },
            ]
        )

        calibrated = self.engine.calibrate_v6_scores_for_pme(scores, features)

        self.assertGreater(calibrated[1], calibrated[0])


class TestLocalFirstData(unittest.TestCase):
    def test_trade_and_growth_local_first_do_not_call_comtrade(self):
        with (
            patch.object(data_sources, "_fetch_comtrade_raw", side_effect=AssertionError("Comtrade must not be called")),
            patch.object(dynamic_growth, "fetch_yearly_data", side_effect=AssertionError("Comtrade growth must not be called")),
        ):
            trade = data_sources.get_trade_data("1509", force_refresh=False)
            growth = dynamic_growth.fetch_growth_data("1509", set(trade["country_code"]), force_refresh=False)

        self.assertFalse(trade.empty)
        self.assertIn("ESP", set(trade["country_code"]))
        self.assertIn("ESP", growth)

    def test_detailed_leather_code_uses_local_hs2_family_data(self):
        with (
            patch.object(data_sources, "_fetch_comtrade_raw", side_effect=AssertionError("Comtrade must not be called")),
            patch.object(dynamic_growth, "fetch_yearly_data", side_effect=AssertionError("Comtrade growth must not be called")),
        ):
            trade = data_sources.get_trade_data("4205", force_refresh=False)
            growth = dynamic_growth.fetch_growth_data("4205", set(trade["country_code"]), force_refresh=False)

        self.assertFalse(trade.empty)
        self.assertGreater(trade["value_usd"].nunique(), 1)
        self.assertIn("FRA", set(trade["country_code"]))
        self.assertIn("FRA", growth)


class TestTopFiveRanking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = MarketScoringEngine()
        if not cls.engine.v6_available:
            raise unittest.SkipTest("The local v6 model artifact is not installed.")

    def test_top_five_are_sorted_unique_and_explained(self):
        results = self.engine.run("huile d'olive", "1509", top_n=5, force_refresh=False)

        self.assertEqual(len(results), 5)
        self.assertEqual([result.rank for result in results], [1, 2, 3, 4, 5])
        self.assertEqual(len({result.country_code for result in results}), 5)
        self.assertEqual(
            [result.score_final for result in results],
            sorted((result.score_final for result in results), reverse=True),
        )
        for result in results:
            self.assertGreaterEqual(result.score_final, 0.0)
            self.assertLessEqual(result.score_final, 100.0)
            self.assertEqual(result.scoring_method, "v6_market_attractiveness")
            self.assertTrue(result.v6_explanation)


class TestScoreEndpoint(unittest.TestCase):
    def setUp(self):
        api.app.dependency_overrides[get_current_auth] = lambda: AuthContext(
            user_id="user-test",
            organization_id="org-test",
            membership_role="OWNER",
            email="owner@test.ma",
        )
        self.client = TestClient(api.app)
        self.fake_engine = Mock()
        self.fake_engine.run.return_value = [
            _market_result(1, "ESP", 100.0),
            _market_result(2, "FRA", 89.0),
            _market_result(3, "ITA", 87.0),
        ]
        self.save_analysis = AsyncMock()

    def tearDown(self):
        api.app.dependency_overrides.clear()

    def test_score_endpoint_contract_and_arguments(self):
        with (
            patch.object(api, "scoring_engine", self.fake_engine),
            patch.object(api.auth_repository, "save_workspace_analysis", self.save_analysis),
        ):
            response = self.client.post(
                "/api/score",
                json={
                    "product_name": "huile d'olive",
                    "hs_code": "1509",
                    "top_n": 3,
                    "force_refresh": False,
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 3)
        self.assertEqual([item["rank"] for item in payload], [1, 2, 3])
        self.assertEqual(payload[0]["country"]["code"], "ESP")
        self.assertEqual(payload[0]["scoring_method"], "v6_market_attractiveness")
        self.assertIn("v6_explanation", payload[0])
        self.assertIn("dimensions", payload[0])
        self.fake_engine.run.assert_called_once_with(
            "huile d'olive",
            "1509",
            top_n=3,
            force_refresh=False,
        )
        self.save_analysis.assert_awaited_once()

    def test_score_endpoint_returns_clean_error_when_engine_fails(self):
        self.fake_engine.run.side_effect = RuntimeError("scoring unavailable")

        with (
            patch.object(api, "scoring_engine", self.fake_engine),
            patch.object(api.auth_repository, "save_workspace_analysis", self.save_analysis),
        ):
            response = self.client.post(
                "/api/score",
                json={"product_name": "test", "hs_code": "1509"},
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "scoring unavailable")


if __name__ == "__main__":
    unittest.main()
