import os
import redis
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from ratelimiter import RateLimiter
from ratelimiter.backends.redis_backend import RedisBackend

class AllowRequest(BaseModel):
    user:str

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(
    host=redis_host,
    port=redis_port
)

app = FastAPI()
redis_backend = RedisBackend(
    capacity=5,
    refill_rate=1,
    client=redis_client
)

limiter = RateLimiter(backend=redis_backend)

def get_limiter():
    return limiter

@app.get("/")
def root():
    return {"message" : "Rate Limiter API is running"}

@app.post("/allow")
def allow(request : AllowRequest, limiter: RateLimiter = Depends(get_limiter)):
    allowed = limiter.allow_request(request.user)
    if allowed:
        return {"user" : request.user, "allowed" : allowed}
    else:
        raise HTTPException(status_code=429, detail="Too Many Requests!")
