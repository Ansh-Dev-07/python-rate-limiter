import time
from threading import Lock

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