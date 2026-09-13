from .base import RateLimiterBackend

class RedisBackend(RateLimiterBackend):
    KEY_PREFIX = "ratelimiter:user:"
    BUCKET_TTL = 60
    LUA_SCRIPT= """
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local bucket_ttl = tonumber(ARGV[3])
    
        local time = redis.call("TIME")
        local seconds = tonumber(time[1])
        local microseconds = tonumber(time[2])
    
        local current_time_ms = (seconds * 1000) + (microseconds / 1000)
    
        local tokens = tonumber(
            redis.call("HGET", KEYS[1], "current_tokens")
        )
    
        local last_time = tonumber(
            redis.call("HGET", KEYS[1], "last_refill_time")
        )
    
        if tokens == nil then
            tokens = capacity
            last_time = current_time_ms
        end
    
        local elapsed_ms = current_time_ms - last_time
    
        local new_tokens = (elapsed_ms / 1000) * refill_rate
    
        local refilled_tokens = math.min(
            capacity,
            tokens + new_tokens
        )
    
        local allowed = false
    
        if refilled_tokens >= 1 then
            refilled_tokens = refilled_tokens - 1
            allowed = true
        end
    
        redis.call(
            "HSET",
            KEYS[1],
            "current_tokens",
            refilled_tokens,
            "last_refill_time",
            current_time_ms
        )

        redis.call("EXPIRE", KEYS[1], bucket_ttl)
    
        return {
            allowed,
            refilled_tokens
        }
    """
    def __init__(self,capacity,refill_rate,client):
        if(capacity<=0):
            raise ValueError("Capacity must be greater than 0")
        self.capacity=capacity
        if(refill_rate<=0):
            raise ValueError("Refill rate must be greater than 0")
        self.refill_rate=refill_rate
        self.client=client
    def allow_request(self, user):
        key = f"{self.KEY_PREFIX}{user}"
        result = self.client.eval(
            self.LUA_SCRIPT,
            1,
            key,
            self.capacity,
            self.refill_rate,
            self.BUCKET_TTL
        )
        return bool(result[0])