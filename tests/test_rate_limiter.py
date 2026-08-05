import unittest
from ratelimiter import RateLimiter

class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.limiter = RateLimiter(capacity=5, refill_rate=1)

    def test_new_user_request_allowed(self):
        self.assertTrue(self.limiter.allow_request("Ansh"))

    def test_existing_user_reuses_bucket(self):
        for _ in range(5):
            self.limiter.allow_request("Ansh")
        self.assertFalse(self.limiter.allow_request("Ansh"))

    def test_different_users_have_independent_buckets(self):
        for _ in range(5):
            self.limiter.allow_request("Ansh")
        self.assertTrue(self.limiter.allow_request("Rishi"))

    def test_invalid_capacity_raises_error(self):
        with self.assertRaises(ValueError):
            RateLimiter(capacity=0,refill_rate=1)

    def test_invalid_refill_rate_raises_error(self):
        with self.assertRaises(ValueError):
            RateLimiter(capacity=5,refill_rate=0)