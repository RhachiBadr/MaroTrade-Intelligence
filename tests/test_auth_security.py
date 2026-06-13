import unittest

from fastapi.testclient import TestClient

import api
from services.auth.security import (
    create_access_token,
    decode_access_token,
    hash_one_time_token,
    hash_password,
    verify_password,
)


class TestAuthSecurity(unittest.TestCase):
    def test_passwords_are_hashed_and_verified(self):
        password_hash = hash_password("MotDePasse2026!")

        self.assertNotEqual(password_hash, "MotDePasse2026!")
        self.assertTrue(verify_password("MotDePasse2026!", password_hash))
        self.assertFalse(verify_password("MauvaisMotDePasse", password_hash))

    def test_access_token_contains_tenant_context(self):
        token, max_age = create_access_token(
            user_id="user-1",
            organization_id="org-1",
            membership_role="OWNER",
            email="owner@pme.ma",
        )
        auth = decode_access_token(token)

        self.assertEqual(auth.user_id, "user-1")
        self.assertEqual(auth.organization_id, "org-1")
        self.assertEqual(auth.membership_role, "OWNER")
        self.assertGreater(max_age, 0)

    def test_one_time_tokens_are_hashed_deterministically(self):
        self.assertEqual(hash_one_time_token("token-test"), hash_one_time_token("token-test"))
        self.assertNotEqual(hash_one_time_token("token-test"), "token-test")

    def test_private_score_endpoint_requires_authentication(self):
        client = TestClient(api.app)
        response = client.post(
            "/api/score",
            json={"product_name": "huile d'olive", "hs_code": "1509", "top_n": 3},
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
