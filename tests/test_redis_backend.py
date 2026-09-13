import unittest
from ratelimiter.backends.redis_backend import RedisBackend
import redis
import time
from threading import Thread
from ratelimiter.rate_limiter import RateLimiter

class TestRedisBackend(unittest.TestCase):
    def setUp(self):
        self.client=redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True
        )
        self.client.delete("ratelimiter:user:Ansh")
        self.client.delete("ratelimiter:user:Rishi")
        self.backend = RedisBackend(
            capacity=2,
            refill_rate=1,
            client=self.client
        )
        self.limiter=RateLimiter(backend=self.backend)

    def tearDown(self):
        self.client.delete("ratelimiter:user:Ansh")
        self.client.delete("ratelimiter:user:Rishi")

    def test_new_user_request(self):
        allowed = self.limiter.allow_request("Ansh")
        self.assertTrue(allowed)
        remaining_tokens = self.client.hget(
            "ratelimiter:user:Ansh",
            "current_tokens"
        )
        self.assertEqual(remaining_tokens,"1")

    def test_capacity_exhaustion(self):
        first_request = self.limiter.allow_request("Ansh")
        second_request = self.limiter.allow_request("Ansh")
        third_request = self.limiter.allow_request("Ansh")
        self.assertTrue(first_request)
        self.assertTrue(second_request)
        self.assertFalse(third_request)

    def test_refill(self):
        first_request = self.limiter.allow_request("Ansh")
        second_request = self.limiter.allow_request("Ansh")
        third_request = self.limiter.allow_request("Ansh")
        self.assertTrue(first_request)
        self.assertTrue(second_request)
        self.assertFalse(third_request)
        time.sleep(1.1)
        fourth_request = self.limiter.allow_request("Ansh")
        self.assertTrue(fourth_request)

    def test_independent_users(self):
        first_request = self.limiter.allow_request("Ansh")
        second_request = self.limiter.allow_request("Ansh")
        third_request = self.limiter.allow_request("Ansh")
        self.assertTrue(first_request)
        self.assertTrue(second_request)
        self.assertFalse(third_request)
        rishi_first_request = self.limiter.allow_request("Rishi")
        rishi_second_request = self.limiter.allow_request("Rishi")
        rishi_third_request = self.limiter.allow_request("Rishi")
        self.assertTrue(rishi_first_request)
        self.assertTrue(rishi_second_request)
        self.assertFalse(rishi_third_request)

    def test_invalid_capacity_raises_error(self):
        with self.assertRaises(ValueError):
            RedisBackend(capacity=0,refill_rate=1,client=self.client)
    
    def test_invalid_refill_rate_raises_error(self):
        with self.assertRaises(ValueError):
            RedisBackend(capacity=2,refill_rate=0,client=self.client)

    def test_concurrent_requests(self):
        concurrency_backend = RedisBackend(
            capacity=5,
            refill_rate=0.000001,
            client=self.client
        )
        concurrency_limiter = RateLimiter(
            backend=concurrency_backend
        )
        results=[]
        def make_request():
            result = concurrency_limiter.allow_request("Ansh")
            results.append(result)
        threads = []
        for _ in range(20):
            thread = Thread(target=make_request)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        allowed_count = results.count(True)
        self.assertEqual(allowed_count, 5)
        self.assertEqual(results.count(False), 15)

    def test_bucket_expiration(self):
        expiration_backend = RedisBackend(
            capacity=2,
            refill_rate=1,
            client=self.client
        )
        expiration_backend.BUCKET_TTL=2
        expiration_limiter = RateLimiter(
            backend=expiration_backend
        )
        allowed = expiration_limiter.allow_request("Ansh")
        self.assertTrue(allowed)
        self.assertTrue(self.client.exists("ratelimiter:user:Ansh"))
        time.sleep(2.1)
        self.assertFalse(self.client.exists("ratelimiter:user:Ansh"))