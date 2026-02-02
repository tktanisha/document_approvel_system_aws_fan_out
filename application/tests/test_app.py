import unittest

from app import app
from exceptions.app_exceptions import AppException
from fastapi.testclient import TestClient


class TestMainApp(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "Healthy"})

    def test_app_exception_handler(self):
        @app.get("/test-app-exception")
        def raise_app_exception():
            raise AppException(status_code=400, message="test error")

        response = self.client.get("/test-app-exception")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
