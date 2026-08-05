from threading import Lock
from .token_bucket import TokenBucket

class RateLimiter:
    def __init__(self,capacity,refill_rate):
        if(capacity<=0):
            raise ValueError("Capacity must be greater than 0")
        self.capacity=capacity
        if(refill_rate<=0):
            raise ValueError("Refill rate must be greater than 0") 
        self.refill_rate=refill_rate
        self.buckets={}
        self.lock=Lock()
    def allow_request(self,user):
        bucket=self._get_or_create_bucket(user)
        return bucket.allow_request()

    def _get_or_create_bucket(self,user):
        with self.lock:
            if(user in self.buckets):
                return self.buckets[user]
            else:
                bucket=TokenBucket(self.capacity,self.refill_rate)
                self.buckets[user]=bucket
                return bucket