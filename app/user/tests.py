from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.core.cache import cache

User = get_user_model()


class UserTestCase(TestCase):
    def setUp(self):
        cache.clear()
        return super().setUp()

    def test_signup_api(self):
        response = self.client.post("/api/auth/signup",
                                    data={"username": "test", "password": "test", "email": "dhwpdn21@kakao.com"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'email': 'dhwpdn21@kakao.com', 'username': 'test'})

    def test_user_list_api(self):
        User.objects.create_user(username="test", password="test", email="test1@test.com")
        User.objects.create_user(username="test2", password="test", email="test2@test.com")
        # 캐시 초기화
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get("/api/auth/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(len(queries), 1)

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get("/api/auth/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(len(queries), 0)
