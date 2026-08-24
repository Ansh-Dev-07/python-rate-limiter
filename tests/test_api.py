import unittest
from fastapi.testclient import TestClient
from api.main import app, get_limiter
from ratelimiter import RateLimiter

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_limiter = RateLimiter(capacity=5,refill_rate=1)
        app.dependency_overrides[get_limiter] = lambda: self.test_limiter

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message" : "Rate Limiter API is running"})

    def test_allow_request(self):
        response = self.client.post("/allow", json={"user": "Ansh"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), { "user": "Ansh", "allowed": True })

    def test_existing_user_allow_request(self):
        self.test_limiter = RateLimiter(capacity=1,refill_rate=0.1)
        self.client.post("/allow", json={"user": "Ansh"})
        response = self.client.post("/allow", json={"user": "Ansh"})
        self.assertEqual(response.status_code, 429)

    def test_missing_user(self):
        response = self.client.post("/allow", json={})
        self.assertEqual(response.status_code, 422)

    def test_invalid_type(self):
        response = self.client.post("/allow", json={ "user" : 123})
        self.assertEqual(response.status_code, 422)

    def test_different_users_have_independent_buckets(self):
        self.test_limiter = RateLimiter(capacity=1, refill_rate=0.1)
        response1 = self.client.post("/allow", json={"user": "Ansh"})
        response2 = self.client.post("/allow", json={"user": "Rishi"})
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)