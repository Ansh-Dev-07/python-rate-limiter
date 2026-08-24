from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from ratelimiter import RateLimiter

class AllowRequest(BaseModel):
    user:str

app = FastAPI()
limiter=RateLimiter(capacity=5,refill_rate=1)

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
