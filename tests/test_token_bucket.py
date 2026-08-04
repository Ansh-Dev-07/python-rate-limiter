import unittest
import time
from main import TokenBucket

class TestTokenBucket(unittest.TestCase):
    def setUp(self):
        self.bucket=TokenBucket(capacity=5,refill_rate=1)

    def test_first_request_allowed(self):
        self.assertTrue(self.bucket.allow_request())

    def test_fifth_request_allowed(self):
        for _ in range(4):
            self.bucket.allow_request()
        self.assertTrue(self.bucket.allow_request())

    def test_sixth_request_rejected(self):
        for _ in range(5):
            self.bucket.allow_request()
        self.assertFalse(self.bucket.allow_request())
        
    def test_request_allowed_after_refill(self):
        for _ in range(5):
            self.bucket.allow_request()
        time.sleep(2)
        self.assertTrue(self.bucket.allow_request())