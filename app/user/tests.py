from django.test import TestCase


class UserTestCase(TestCase):
    def test_signup_api(self):
        response = self.client.post("/api/auth/signup",
                                    data={"username": "test", "password": "test", "email": "dhwpdn21@kakao.com"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'email': 'dhwpdn21@kakao.com', 'username': 'test'})
