from django.test import TestCase
from django.core.cache import cache


class TestUtilAPI(TestCase):
    def setUp(self):
        cache.clear()
        return super().setUp()

    def test_api_count(self):
        response = self.client.get("/api/auth/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/util/api-count?api_path=api/auth/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["api_path"], "/api/auth/")
        self.assertEqual(response.json()["request_count"], 1)
