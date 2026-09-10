from abc import ABC, abstractmethod

class RateLimiterBackend(ABC):

    @abstractmethod
    def allow_request(self, user):
        pass