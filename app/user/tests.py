import time

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

    def test_generate_otp_api(self):
        response = self.client.post("/api/auth/generate-otp", data={"email": "test@test.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "OTP has been generated")
        self.assertTrue("otp" in response.json())

        otp = response.json()["otp"]

        response = self.client.post("/api/auth/verify-otp", data={"email": "test@test.com", "otp": otp})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "OTP has been verified")

        response = self.client.post("/api/auth/verify-otp",  data={"email": "test@test.com", "otp": 1234})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid OTP")

        time.sleep(5)

        response = self.client.post("/api/auth/verify-otp", data={"email": "test@test.com", "otp": otp})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "OTP has expired")
