from .backends.in_memory import InMemoryBackend

class RateLimiter:
    def __init__(self, capacity=None, refill_rate=None, backend=None):
        if backend is None:
            if capacity is None or refill_rate is None:
                raise ValueError("Capacity and Refill rate is needed!")
            backend = InMemoryBackend(capacity, refill_rate)
        self.backend = backend
    def allow_request(self,user):
        return self.backend.allow_request(user)