import time
from threading import Lock
from threading import Thread
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
        
class TokenBucket:
    def __init__(self,capacity,refill_rate):
        if(capacity<=0):
            raise ValueError("Capacity must be greater than 0")
        self.capacity=capacity
        if(refill_rate<=0):
            raise ValueError("Refill rate must be greater than 0") 
        self.refill_rate=refill_rate
        self.current_tokens=capacity
        current_time=time.time()
        self.last_refill_time=current_time
        self.lock=Lock()

    def allow_request(self):
        with self.lock:
            self._refill_tokens()
            if(self.current_tokens>=1):
                self.current_tokens-=1
                return True
            else:
                return False
    
    def _refill_tokens(self):
        current_time=time.time()
        elapsed_time=current_time-self.last_refill_time
        new_token_amt=elapsed_time*self.refill_rate
        self.current_tokens=min(self.capacity,self.current_tokens+new_token_amt)
        self.last_refill_time=current_time
