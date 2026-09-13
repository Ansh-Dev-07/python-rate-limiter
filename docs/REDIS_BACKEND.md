# Redis Backend

## Overview

Version `v0.7.0` introduces Redis as an alternative storage backend for the rate limiter.

The earlier versions of the project stored user buckets inside a Python dictionary:

```text
RateLimiter
    ↓
Python Dictionary
    ↓
User → TokenBucket
````

This approach works well for a single application process, but the bucket state exists only inside that process.

If the application is running on multiple servers, each server would have its own independent dictionary:

```text
                ┌── Server 1 ── Python Dictionary
                │
User Requests ──┤
                │
                └── Server 2 ── Python Dictionary
```

The same user could therefore have different rate-limit states depending on which server handled the request.

Redis provides shared external storage for the bucket state:

```text
                ┌── Server 1 ──┐
                │              │
User Requests  ─┤              ├── Redis
                │              │
                └── Server 2 ──┘
```

Instead of keeping bucket state inside the application process, the `RedisBackend` stores it in Redis.

This makes the rate limiter architecture suitable as a foundation for applications where multiple application processes or servers need to access the same rate-limit state.

---

## What Changed in v0.7.0

The main change in v0.7.0 is not a change to the Token Bucket algorithm itself.

The Token Bucket algorithm remains responsible for:

* capacity
* refill rate
* token calculation
* request allowance
* request rejection

The major change is **where and how the bucket state is stored and updated**.

Previously:

```text
RateLimiter
    ↓
InMemoryBackend
    ↓
TokenBucket
    ↓
Python memory
```

With Redis:

```text
RateLimiter
    ↓
RateLimiterBackend
    ↓
RedisBackend
    ↓
Lua Script
    ↓
Redis
```

The project can therefore use different storage implementations while keeping the public `RateLimiter` interface simple.

---

# 1. Why Redis?

## The Limitation of In-Memory Storage

The in-memory backend stores buckets in a Python dictionary:

```python
self.buckets = {}
```

Each user is associated with a `TokenBucket` instance:

```text
buckets
├── user_1 → TokenBucket
├── user_2 → TokenBucket
├── user_3 → TokenBucket
└── ...
```

This is simple and efficient, but the state belongs to the Python process.

For example:

```text
Application Server 1
└── user_1 → 3 tokens

Application Server 2
└── user_1 → 5 tokens
```

Both servers believe they have different states for the same user.

This becomes a problem when the application is scaled across multiple processes or servers.

## Shared external state with Redis

Redis moves the bucket state outside the application process:

```text
Application Server 1 ──┐
                       │
Application Server 2 ──┼── Redis
                       │
Application Server 3 ──┘
```

All application instances can access the same user bucket.

The important architectural change is therefore:

```text
Process-local state
        ↓
External shared state
```

Redis does not replace the Token Bucket algorithm. It provides a shared location in which the bucket state can be stored and updated.

---

# 2. Redis Backend Architecture

The Redis backend follows the same backend abstraction introduced in v0.7.0.

```text
                    RateLimiter
                         │
                         ▼
                RateLimiterBackend
                         │
                         ▼
                   RedisBackend
                         │
                         ▼
                    Lua Script
                         │
                         ▼
                       Redis
```

The `RateLimiter` no longer needs to know whether the state is stored in memory or Redis.

It delegates the request to the configured backend:

```python
def allow_request(self, user):
    return self.backend.allow_request(user)
```

The backend is responsible for handling the storage-specific implementation.

---

## Backend Abstraction

The common backend interface is defined by `RateLimiterBackend`:

```python
class RateLimiterBackend(ABC):

    @abstractmethod
    def allow_request(self, user):
        pass
```

Both storage implementations follow this interface:

```text
RateLimiterBackend
       │
       ├── InMemoryBackend
       │
       └── RedisBackend
```

This allows the same `RateLimiter` class to work with different storage systems.

---

# 3. Redis Data Model

Each user receives a separate Redis key.

The key format is:

```text
ratelimiter:user:<user>
```

For example, for a user named `Ansh`:

```text
ratelimiter:user:Ansh
```

The backend stores the bucket state as a Redis hash.

Conceptually:

```text
ratelimiter:user:Ansh
├── current_tokens
└── last_refill_time
```

### `current_tokens`

Stores the current number of tokens available in the bucket.

### `last_refill_time`

Stores the timestamp used as the reference point for calculating token refill.

The Redis hash contains the state required by the backend to calculate and update the bucket on subsequent requests.
---

# 4. Redis Token Bucket Flow

When a request arrives, `RedisBackend.allow_request()` generates the user's Redis key:

```python
key = f"{self.KEY_PREFIX}{user}"
```

The backend then executes the Lua script using Redis `EVAL`.

The operation follows this general flow:

```text
Request
   ↓
Generate user key
   ↓
Execute Lua script
   ↓
Read bucket state
   ↓
Get current Redis time
   ↓
Calculate elapsed time
   ↓
Calculate refill
   ↓
Cap tokens at capacity
   ↓
Consume one token if available
   ↓
Update bucket state
   ↓
Refresh TTL
   ↓
Return result
```

The Python application does not perform these individual operations separately.

They are performed inside Redis through the Lua script.

---

# 5. Why Lua?

A rate limiter needs to perform several related operations:

```text
Read current state
        ↓
Calculate refill
        ↓
Check availability
        ↓
Consume token
        ↓
Write new state
```

If these operations were performed independently from Python, another request could execute between them.

## Unsafe Approach

A simplified non-atomic approach could look like:

```text
Request A                Request B

GET tokens
                         GET tokens
Calculate
                         Calculate
Consume
                         Consume
SET tokens
                         SET tokens
```

Both requests could read the same old state before either request updates it.

This creates a race condition.

For a rate limiter, that could result in more requests being accepted than the configured capacity allows.

---

## Atomic Lua Execution

The Redis backend instead executes the complete operation through one Lua script:

```text
             Lua Script
                 │
        ┌────────┴────────┐
        │                 │
      Read              Calculate
        │                 │
        └────────┬────────┘
                 │
              Consume
                 │
              Update
                 │
               TTL
```

The script performs:

1. Read the existing bucket state.
2. Obtain the current Redis server time.
3. Calculate elapsed time.
4. Calculate newly available tokens.
5. Cap the result at bucket capacity.
6. Consume one token if at least one token is available.
7. Write the updated state back to Redis.
8. Refresh the bucket expiration time.

The complete bucket operation is executed inside a single Redis Lua script invocation.

This keeps the read → calculate → consume → update sequence together instead of spreading it across multiple client-side commands.

---

# 6. Redis Server Time

The Redis backend uses:

```lua
redis.call("TIME")
```

to obtain the current time.

The Lua script receives:

```text
seconds
microseconds
```

and converts them into milliseconds.

```text
Redis TIME
    ↓
seconds + microseconds
    ↓
current_time_ms
```

The resulting timestamp is used to calculate how much time has passed since the previous refill.

---

## Why Use Redis Time?

The bucket state is stored and updated in Redis.

Using Redis's own clock keeps the time calculation inside the same system that performs the state update.

The Redis backend therefore does not depend on the application server's local `time.time()` value for its refill calculation.

This is different from the in-memory `TokenBucket`, which continues to use Python's:

```python
time.time()
```

The two backends therefore use different clocks appropriate to their storage models:

```text
InMemoryBackend
      ↓
TokenBucket
      ↓
Python time.time()

RedisBackend
      ↓
Lua Script
      ↓
Redis TIME
```

---

# 7. Lazy Refill in Redis

The Redis backend also uses lazy token refill.

Tokens are not continuously generated in the background.

Instead, when a request arrives, the Lua script calculates how many tokens should have been added since the previous refill.

The calculation is based on:

```text
elapsed time × refill rate
```

The resulting token count is capped at the configured capacity:

```text
refilled_tokens =
    min(capacity, current_tokens + new_tokens)
```

If at least one token is available:

```text
refilled_tokens >= 1
```

one token is consumed and the request is allowed.

Otherwise, the request is rejected.

---

# 8. TTL and Automatic Cleanup

Redis introduces another useful feature: key expiration.

The backend defines:

```python
BUCKET_TTL = 60
```

After processing a request, the Lua script executes:

```lua
redis.call("EXPIRE", KEYS[1], bucket_ttl)
```

This gives the bucket a limited lifetime.

## Active User

When a user continues making requests:

```text
Request
   ↓
Bucket exists
   ↓
Request processed
   ↓
TTL refreshed
   ↓
Bucket remains
```

## Inactive User

When the user stops making requests:

```text
Bucket exists
   ↓
No more requests
   ↓
TTL expires
   ↓
Redis removes the key
```

This provides automatic cleanup for inactive Redis-backed buckets.

The TTL is refreshed whenever the bucket is accessed, so the expiration represents inactivity rather than a fixed lifetime from bucket creation.

---

## In-Memory vs Redis Cleanup

The cleanup behavior differs between the two backends.

### In-memory

```text
Python Dictionary
      ↓
Bucket remains stored
```

There is currently no automatic expiration mechanism for inactive in-memory buckets.

### Redis

```text
Redis Hash
      ↓
     TTL
      ↓
Automatic expiration
```

Redis therefore provides automatic cleanup of inactive bucket state.

---

# 9. RedisBackend Configuration

`RedisBackend` receives three values:

```python
RedisBackend(
    capacity,
    refill_rate,
    client
)
```

The Redis client is injected into the backend rather than being created internally.

Conceptually:

```text
Application
    │
    ├── creates Redis client
    │
    └── passes client
             ↓
       RedisBackend
             ↓
          Redis
```

This keeps connection creation outside the backend itself and makes the backend easier to control and test.

The current implementation does not provide a dedicated Redis configuration or connection-management layer.

---

# 10. Current Scope

The Redis backend currently provides:

* Redis-backed bucket storage
* Per-user rate-limit state
* Token Bucket refill logic
* Atomic request processing through Lua
* Redis server-side time
* Redis key expiration
* Shared external bucket state
* Backend abstraction through `RateLimiterBackend`
* Injected Redis client
* Automated Redis integration tests

The current implementation does **not** yet provide:

* Redis connection health checks
* Automatic Redis reconnection
* Redis failure recovery
* Authentication configuration
* TLS configuration
* Redis persistence configuration
* A Redis-backed FastAPI configuration
* Automatic switching between Redis and in-memory backends
* A demonstrated multi-server deployment

Therefore, v0.7.0 should be understood as the introduction of a **Redis-backed storage architecture**, rather than a complete production distributed deployment.

---

# 11. Testing

Redis-specific behavior is tested in:

```text
tests/test_redis_backend.py
```

The test suite currently contains 8 Redis backend tests.

### New User Request

Verifies that a new user's first request is allowed and that the expected token state is stored in Redis.

### Capacity Exhaustion

Verifies that requests are rejected after the configured bucket capacity is exhausted.

### Token Refill

Verifies that tokens become available again after sufficient time has elapsed.

### Independent Users

Verifies that different users receive independent Redis-backed buckets.

### Invalid Capacity

Verifies that invalid capacity values raise `ValueError`.

### Invalid Refill Rate

Verifies that invalid refill rates raise `ValueError`.

### Concurrent Requests

Uses multiple threads to verify that concurrent requests are processed safely and that capacity is respected.

### Bucket Expiration

Verifies that an inactive Redis bucket expires after its configured TTL.

---

## Redis Test Environment

The Redis tests require:

1. The Python `redis` package.
2. A running Redis server.
3. Redis accessible at:

```text
localhost:6379
```

The Redis test suite is therefore different from the purely in-memory unit tests because it depends on an external Redis service.

---

# 12. Architecture Summary

The evolution of the project can now be represented as:

```text
v0.1
Single Token Bucket
        ↓
v0.2
Multi-user Dictionary
        ↓
v0.3
Thread-safe In-memory Backend
        ↓
v0.4
Automated Testing
        ↓
v0.5
Python Package
        ↓
v0.6
FastAPI Integration
        ↓
v0.7
Backend Abstraction
        ↓
 ┌──────┴───────┐
 ↓              ↓
In-Memory      Redis
Backend        Backend
                  ↓
                 Lua
                  ↓
             Atomic State
                  ↓
                 TTL
```

The important architectural transition in v0.7.0 is:

```text
Application-owned state
        ↓
Backend abstraction
        ↓
Externally shared state
```

This creates the foundation for further infrastructure and deployment improvements in later versions.

---

# 13. Future Evolution

The Redis backend provides the foundation for future improvements, but those improvements are outside the current v0.7.0 implementation.

Potential future work includes:

* Redis connection management
* Failure handling and recovery
* Configuration management
* Redis-backed FastAPI deployment
* Docker-based Redis development environment
* Multi-instance application deployment
* CI/CD integration with Redis
* Production deployment
* Additional backend implementations

These features should be implemented and tested before being considered part of the project's supported functionality.
