import unittest

from services.watch.sources.rasff_client import RASFFStructuredClient


class TestRASFFOfficialLinks(unittest.TestCase):
    def test_search_notification_uses_exact_public_detail_url(self):
        client = RASFFStructuredClient()

        alert = client._normalize_search_notification(
            {
                "notifId": 123456,
                "reference": "2026.1234",
                "subject": "Salmonella spp. in sesame seeds from Nigeria",
                "productCategory": {"description": "nuts, nut products and seeds"},
                "notificationClassification": {"description": "border rejection notification"},
                "originCountries": [{"organizationName": "Nigeria"}],
                "ecValidationDate": "2026-06-12",
            }
        )

        self.assertEqual(
            alert["url"],
            "https://webgate.ec.europa.eu/rasff-window/screen/notification/123456",
        )
        self.assertNotIn("/screen/search", alert["url"])

    def test_detail_notification_uses_exact_public_detail_url_and_keeps_api_url(self):
        client = RASFFStructuredClient()

        alert = client._normalize_detail(
            {"reference": "2026.1234", "product": {"description": "Sesame seeds"}},
            entry={},
            notification_id="123456",
        )

        self.assertEqual(
            alert["url"],
            "https://webgate.ec.europa.eu/rasff-window/screen/notification/123456",
        )
        self.assertEqual(
            alert["api_url"],
            "https://webgate.ec.europa.eu/rasff-window/backend/public/notification/view/id/123456/",
        )

    def test_reference_fallback_does_not_use_generic_search_page(self):
        client = RASFFStructuredClient()

        url = client._build_public_notification_url(reference="2026.1234")

        self.assertEqual(
            url,
            "https://webgate.ec.europa.eu/rasff-window/screen/notification/2026.1234",
        )
        self.assertNotIn("/screen/search", url)

    def test_reference_is_not_truncated_into_fake_numeric_id(self):
        client = RASFFStructuredClient()

        alert = client._normalize_search_notification(
            {
                "reference": "2026.1234",
                "subject": "RASFF notification without numeric id",
            }
        )

        self.assertEqual(
            alert["url"],
            "https://webgate.ec.europa.eu/rasff-window/screen/notification/2026.1234",
        )
        self.assertNotEqual(
            alert["url"],
            "https://webgate.ec.europa.eu/rasff-window/screen/notification/2026",
        )

    def test_cached_generic_rasff_url_is_repaired(self):
        client = RASFFStructuredClient()

        alerts = client._repair_cached_alert_urls(
            [
                {
                    "id": "RASFF-2026.1234",
                    "source": "RASFF",
                    "reference": "2026.1234",
                    "url": "https://webgate.ec.europa.eu/rasff-window/",
                }
            ]
        )

        self.assertEqual(
            alerts[0]["url"],
            "https://webgate.ec.europa.eu/rasff-window/screen/notification/2026.1234",
        )


if __name__ == "__main__":
    unittest.main()
