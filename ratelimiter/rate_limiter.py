from .backends.in_memory import InMemoryBackend

class RateLimiter:
    def __init__(self,capacity,refill_rate,backend=None):
        if backend is None:
            backend = InMemoryBackend(capacity, refill_rate)
        self.backend=backend
    def allow_request(self,user):
        return self.backend.allow_request(user)