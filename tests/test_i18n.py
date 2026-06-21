import unittest

from fastapi.testclient import TestClient

import api
from services.i18n import localize_api_message, request_locale


class TestInternationalization(unittest.TestCase):
    def test_locale_defaults_to_french(self):
        self.assertEqual(request_locale(None), "fr")
        self.assertEqual(request_locale("fr-FR,fr;q=0.9"), "fr")
        self.assertEqual(request_locale("en-US,en;q=0.9"), "en")

    def test_known_api_message_is_translated(self):
        self.assertEqual(
            localize_api_message("Authentification requise.", "en"),
            "Authentication required.",
        )

    def test_protected_endpoint_uses_accept_language(self):
        client = TestClient(api.app)
        response = client.post(
            "/api/score",
            json={"product_name": "Olive oil", "hs_code": "1509", "top_n": 3},
            headers={"Accept-Language": "en"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Authentication required.")


if __name__ == "__main__":
    unittest.main()
