# Architecture

This document explains the architecture of the **Python Rate Limiter** project.

Unlike the README, which provides a high-level overview, this document focuses on the internal software architecture, package organization, component responsibilities, and request flow.

The architecture evolves with each project release and is intentionally designed to demonstrate software engineering principles such as modularity, separation of concerns, maintainability, and scalability.

Current Architecture Version: **v0.7.0**

---

# High-Level Architecture

At **v0.7.0**, the project consists of a reusable Python package, a FastAPI-based HTTP integration layer, and a pluggable backend architecture supporting both in-memory and Redis-backed rate limiting.

The `RateLimiter` acts as the main public interface and delegates rate-limiting operations to a backend implementing the `RateLimiterBackend` interface.

```text
                         Client
                           │
                           │ HTTP Request
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    │  API Layer   │
                    └──────┬───────┘
                           │
                           │ Python call
                           ▼
                    ┌──────────────┐
                    │ RateLimiter  │
                    │    Facade    │
                    └──────┬───────┘
                           │
                           ▼
                 ┌─────────────────────┐
                 │ RateLimiterBackend  │
                 │     Interface      │
                 └─────────┬───────────┘
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
        ┌─────────────────┐   ┌─────────────────┐
        │ InMemoryBackend │   │  RedisBackend   │
        └────────┬────────┘   └────────┬────────┘
                 │                     │
                 ▼                     ▼
          TokenBucket              Lua Script
                                       │
                                       ▼
                                     Redis
```
Each component has a distinct responsibility.

• The client sends requests through the available interface.
• FastAPI handles HTTP routing, request validation, and HTTP responses.
• RateLimiter provides the main public interface and delegates requests to the configured backend.
• RateLimiterBackend defines the common backend contract.
• InMemoryBackend manages user buckets stored in the Python process.
• TokenBucket implements token state and refill behavior for the in-memory backend.
• RedisBackend manages Redis-backed rate limiting using an atomic Lua script.
• Redis stores bucket state externally for Redis-backed requests.

The FastAPI layer remains separate from the core rate-limiting package. The ratelimiter package does not depend on FastAPI.

The v0.7.0 backend abstraction allows storage implementations to evolve independently from the public RateLimiter interface.

---

# Package Structure 

Beginning with **v0.5.0**, the project adopts a modular package structure instead of keeping all implementation inside a single Python file.
In **v0.6.0**, a separate `api/` directory was added to contain the FastAPI integration layer. 
In **v0.7.0**, the `ratelimiter/backends/` package was introduced to provide a backend abstraction and separate in-memory and Redis storage implementations.

The repository is organized into separate directories, each with a clear responsibility.

```text
python-rate-limiter/
│
├── ratelimiter/
│   ├── __init__.py
│   ├── rate_limiter.py
│   ├── token_bucket.py
│   └── backends/
│       ├── __init__.py
│       ├── base.py
│       ├── in_memory.py
│       └── redis_backend.py
│
├── api/
│   ├── __init__.py
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   ├── test_rate_limiter.py
│   ├── test_token_bucket.py
│   ├── test_api.py
│   └── test_redis_backend.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── TOKEN_BUCKET.md
│   ├── DESIGN_DECISIONS.md
│   ├── TESTING.md
│   └── REDIS_BACKEND.md
│
├── README.md
├── CHANGELOG.md
├── PROJECT_TIMELINE.md
├── pyproject.toml
├── LICENSE
└── .gitignore
```

---

## Directory Responsibilities

### `ratelimiter/`

This package contains the production implementation of the project.

| File | Responsibility |
|------|----------------|
| `__init__.py` | Exposes the public API of the package. |
| `rate_limiter.py` | Provides the main `RateLimiter` interface and delegates requests to the configured backend. |
| `token_bucket.py` | Implements token state, token consumption, and refill logic used by the in-memory backend. |

---

### `ratelimiter/backends/`

This package contains the backend abstraction and the available rate-limit state storage implementations introduced in **v0.7.0**.

| File | Responsibility |
|------|----------------|
| `__init__.py` | Initializes the backend package. |
| `base.py` | Defines the `RateLimiterBackend` abstract interface. |
| `in_memory.py` | Stores user buckets in memory and delegates token decisions to `TokenBucket`. |
| `redis_backend.py` | Implements Redis-backed rate limiting using Redis state and an atomic Lua script. |

The backend abstraction allows `RateLimiter` to remain independent from a specific storage implementation.

---
### `api/`

This directory contains the FastAPI integration layer introduced in **v0.6.0**.

| File | Responsibility |
|------|----------------|
| `__init__.py` | Initializes the `api` package. |
| `main.py` | Defines the FastAPI application, API endpoints, request model, and integration with the `RateLimiter`. |

The API layer is responsible for HTTP-specific concerns while the core rate-limiting logic remains inside the `ratelimiter/` package.

---

### `tests/`

Contains automated tests for both the core rate-limiting package and the FastAPI integration.

| File | Responsibility |
|------|----------------|
| `test_rate_limiter.py` | Tests the `RateLimiter` class and multi-user bucket management. |
| `test_token_bucket.py` | Tests token consumption, rejection, and token refill behavior. |
| `test_api.py` | Tests the FastAPI endpoints, request validation, API responses, and rate-limit behavior. |
| `test_redis_backend.py` | Tests Redis-backed rate limiting, concurrent requests, validation, and bucket expiration. |

Separating tests from production code improves maintainability and makes it easier to extend the project while preventing regressions.

---

### `docs/`

Contains detailed technical documentation.

Unlike the README, these documents explain the internal engineering decisions, architecture, testing philosophy, and algorithm implementation.

---

### Root Directory

The root directory contains project-level configuration and documentation.

| File | Purpose |
|------|---------|
| `README.md` | Project overview, installation, usage, and API quick start guide. |
| `CHANGELOG.md` | Release history. |
| `PROJECT_TIMELINE.md` | Long-term roadmap. |
| `pyproject.toml` | Python package configuration and project metadata. |
| `LICENSE` | MIT License. |
| `.gitignore` | Prevents unnecessary files from being committed to Git. |

---

# Component Responsibilities

The project follows the **Single Responsibility Principle (SRP)**, where each component has one clearly defined purpose.

Beginning with **v0.7.0**, the architecture consists of three major areas:

1. The **API integration layer**
2. The **core rate-limiting interface**
3. The **backend implementations**

The API layer handles HTTP-specific concerns, `RateLimiter` provides the main public interface, and backend implementations handle the storage and rate-limiting state management.

---

## Architecture Overview

```text
                         Client
                           │
                           │ HTTP
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    │  API Layer   │
                    └──────┬───────┘
                           │
                           │ Python call
                           ▼
                    ┌──────────────┐
                    │ RateLimiter  │
                    │    Facade    │
                    └──────┬───────┘
                           │
                           ▼
                 ┌─────────────────────┐
                 │ RateLimiterBackend  │
                 │     Interface      │
                 └─────────┬───────────┘
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
        ┌─────────────────┐   ┌─────────────────┐
        │ InMemoryBackend │   │  RedisBackend   │
        └────────┬────────┘   └────────┬────────┘
                 │                     │
                 ▼                     ▼
          TokenBucket              Lua Script
                                       │
                                       ▼
                                     Redis
```
The architecture contains two important boundaries.
The first is the boundary between the FastAPI integration and the `ratelimiter` package. The API layer does not implement rate-limiting behavior.
The second is the boundary between `RateLimiter` and `RateLimiterBackend`. `RateLimiter` does not depend on a specific storage implementation. It delegates requests to the configured backend.
The API layer does not implement rate-limiting rules itself. It delegates those decisions to the core package.

---

## `api/`

### Responsibility

The `api/` directory contains the FastAPI integration introduced in **v0.6.0**.

The API layer is responsible for:

- Creating the FastAPI application.
- Defining HTTP routes.
- Validating incoming request data.
- Calling the core `RateLimiter`.
- Converting rate-limiter results into HTTP responses.
- Returning appropriate HTTP status codes.

The API layer currently exposes:

- `GET /`
- `POST /allow`

### Why Keep the API Layer Separate?

FastAPI should handle HTTP concerns without becoming part of the core rate-limiting implementation.

This allows the `ratelimiter` package to remain usable without requiring application code to interact directly with HTTP.

The same core package can therefore be used:

```text
Direct Python Usage
        │
        ▼
   RateLimiter
```

or:

```text
HTTP Client
     │
     ▼
  FastAPI
     │
     ▼
 RateLimiter
```

---

## `RateLimiter`

### Responsibility

The `RateLimiter` acts as the main public interface of the core package.

In **v0.7.0**, it delegates rate-limiting requests to a configured `RateLimiterBackend`.

It is responsible for:

- Providing the public rate-limiting interface.
- Creating the default `InMemoryBackend` when no backend is supplied.
- Storing the configured backend.
- Delegating `allow_request()` calls to that backend.

The `RateLimiter` does not directly manage user buckets or implement the Token Bucket algorithm.

### Why This Separation?

Keeping `RateLimiter` independent from the storage implementation allows the same public interface to work with different backends.

For example:

```text
RateLimiter
     │
     ├── InMemoryBackend
     │
     └── RedisBackend
```
This allows backend-specific storage and concurrency mechanisms to remain outside the public interface.

---

## `RateLimiterBackend`

### Responsibility

`RateLimiterBackend` defines the common interface that rate-limiter storage backends must implement.

The interface currently exposes:

```python
allow_request(user)
```

Both available backends implement this contract:

```text
             RateLimiterBackend
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
 InMemoryBackend        RedisBackend
```

This abstraction allows RateLimiter to delegate requests without knowing how bucket state is stored or processed.

### Why Use an Interface?

The backend abstraction separates the rate-limiter's public interface from its storage mechanism.

A backend can therefore change its internal implementation while RateLimiter continues to expose the same allow_request() method.

---

## `InMemoryBackend`

### Responsibility

`InMemoryBackend` provides the default in-memory storage implementation.

It is responsible for:

- Maintaining the mapping of users to `TokenBucket` instances.
- Lazily creating a bucket when a new user appears.
- Protecting the shared bucket dictionary with a lock.
- Delegating token-level decisions to the corresponding `TokenBucket`.

Its internal structure can be represented as:

```text
InMemoryBackend
      │
      ▼
 user → TokenBucket
      │
      ├── Alice → TokenBucket
      ├── Bob   → TokenBucket
      └── ...
```

The backend retains the thread-safe behavior introduced in v0.3.0.

The backend lock protects the shared dictionary, while each individual TokenBucket protects its own token state.

---

## `RedisBackend`

### Responsibility

`RedisBackend` provides Redis-backed rate limiting.

Instead of maintaining `TokenBucket` objects inside the Python process, it stores the required bucket state in Redis.

Each user is represented by a Redis hash:

```text
ratelimiter:user:<user>
├── current_tokens
└── last_refill_time
```

The backend performs the complete bucket operation through a Redis Lua script.

The script:

• Reads the current bucket state.
• Obtains the current time from Redis.
• Calculates token refill.
• Determines whether the request is allowed.
• Consumes a token when allowed.
• Updates the bucket state.
• Refreshes the bucket TTL.

The complete operation is executed as one Redis script invocation, providing atomic state processing at the Redis level.

RedisBackend receives an existing Redis client through dependency injection. It does not create or manage the Redis connection itself.

For detailed Redis-specific architecture and implementation behavior, see docs/REDIS_BACKEND.md.

---

## `TokenBucket`

### Responsibility

`TokenBucket` implements the Token Bucket state and refill logic used by the `InMemoryBackend`.
Each `TokenBucket` represents the rate-limit state for a single user in the in-memory backend.

It is responsible for:

- Tracking the current number of available tokens.
- Refilling tokens based on elapsed time.
- Allowing or rejecting requests.
- Ensuring thread-safe access to token state.

The Redis backend does not create Python `TokenBucket` instances. Instead, it performs equivalent bucket state transitions inside its Redis Lua script.

### Why One Bucket Per User?

Maintaining an independent bucket for every user ensures that one user's traffic does not consume another user's available tokens.

This provides isolated rate limiting while keeping the implementation straightforward.

---

## Relationship Between Components

The components communicate through clear boundaries:

```text
HTTP Request / Python Call
           │
           ▼
      RateLimiter
           │
           ▼
  RateLimiterBackend
       │         │
       │         │
       ▼         ▼
 InMemory     Redis
 Backend      Backend
    │            │
    ▼            ▼
TokenBucket   Lua Script
                  │
                  ▼
                Redis
```

The `api/` layer owns HTTP concerns.
`InMemoryBackend` owns the in-memory user-to-bucket mapping, while `RedisBackend` manages bucket state in Redis.
Each `TokenBucket` owns the rate-limit state for one user.
This separation reduces coupling and allows additional storage backends to be introduced without changing the public `RateLimiter` interface.

---

# Request Lifecycle

At **v0.7.0**, requests can reach the rate-limiting core through two entry points:

1. Direct Python library usage.
2. The FastAPI HTTP integration.

The request is then processed by the configured backend.

---

## HTTP Request Lifecycle

When a client uses the FastAPI integration, the request follows this flow:

```text
HTTP Client
     │
     │ POST /allow
     ▼
FastAPI
     │
     │ Validate Request
     ▼
Request Model
     │
     │ Extract User
     ▼
RateLimiter.allow_request(user)
     │
     ▼
Configured Backend
     │
     ├───────────────────────┐
     │                       │
     ▼                       ▼
InMemoryBackend          RedisBackend
     │                       │
     ▼                       ▼
Find/Create             Redis Lua Script
TokenBucket                  │
     │                       ▼
     ▼                    Redis State
TokenBucket
Processing
     │
     └───────────┬───────────┘
                 ▼
           True / False
                 │
                 ▼
              FastAPI
                 │
          ┌──────┴──────┐
          ▼             ▼
       HTTP 200      HTTP 429
```

The FastAPI layer handles the HTTP-specific part of the request and delegates the actual rate-limiting decision to the core package.

---

## Step-by-Step HTTP Flow

### Step 1 — Receive HTTP Request

A client sends a request to the FastAPI application.

Example:

```http
POST /allow
```

with a request body:

```json
{
  "user": "Alice"
}
```

---

### Step 2 — Validate Request

FastAPI validates the incoming request using the request model defined by the API layer.
The request must contain the required user information before the request reaches the rate-limiting core.

---

### Step 3 — Call the RateLimiter

After validation, the API extracts the user identifier and calls:

```python
limiter.allow_request(user)
```

The API does not implement token counting or refill logic itself.

---

### Step 4 — Process Through the Configured Backend

The `RateLimiter` delegates the request to the configured `RateLimiterBackend`.
The exact processing depends on the backend.
For `InMemoryBackend`, the backend finds or creates the user's `TokenBucket`.
For `RedisBackend`, the backend sends the request to the Redis Lua script, which reads and updates the user's bucket state in Redis.

---

### Step 5 — Perform Rate-Limit Processing

For `InMemoryBackend`, the request is forwarded to the corresponding `TokenBucket`, which performs the refill and request decision.
For `RedisBackend`, the Lua script performs the refill, request decision, state update, and TTL refresh directly in Redis.

---

### Step 6 — Refill Tokens

The configured backend performs the token refill calculation.
For `InMemoryBackend`, `TokenBucket` calculates elapsed time using Python's time source.
For `RedisBackend`, the Lua script obtains the current time from Redis and calculates the refill inside Redis.
Both implementations use lazy refill: tokens are replenished when the bucket is accessed rather than continuously in the background.

---

### Step 7 — Allow or Reject

The configured backend determines whether the request can be allowed.
If sufficient tokens are available, one token is consumed and the request is allowed.
Otherwise, the request is rejected.
The backend returns the resulting boolean decision to `RateLimiter`.

---

### Step 8 — Convert Result to HTTP Response

The FastAPI layer converts the rate-limiter decision into an HTTP response.
A successful request returns a successful HTTP response containing the request result.
A rate-limited request returns:

```text
HTTP 429 Too Many Requests
```

The HTTP layer therefore translates the core package's result into an API-level response without changing the underlying rate-limiting behavior.

---

### Backend Processing

The exact processing after `RateLimiter.allow_request(user)` depends on the configured backend.

For `InMemoryBackend`:

```text
RateLimiter
     ↓
InMemoryBackend
     ↓
Find/Create TokenBucket
     ↓
TokenBucket.allow_request()
```

For RedisBackend:

```text
RateLimiter
     ↓
RedisBackend
     ↓
Redis Lua Script
     ↓
Redis Bucket State
```

The FastAPI layer remains unaware of these backend-specific details.
This is cleaner than rewriting every HTTP step.

---

# Direct Python Request Lifecycle

The core package can also be used without FastAPI.

In this case, the application calls the `RateLimiter` directly:

```python
limiter.allow_request("Alice")
```

The RateLimiter delegates the request to the configured backend.

`In-Memory Backend`
When using the default InMemoryBackend, the request flows through a TokenBucket for the user:

```text
Python Application
       │
       ▼
RateLimiter
       │
       ▼
InMemoryBackend
       │
       ▼
TokenBucket
       │
       ▼
Refill / Check / Consume
       │
       ▼
True / False
```
`Redis Backend`
When using RedisBackend, the request is processed by the Redis Lua script instead of a Python TokenBucket:

```text
Python Application
       │
       ▼
RateLimiter
       │
       ▼
RedisBackend
       │
       ▼
Redis Lua Script
       │
       ▼
Refill / Check / Consume / Update
       │
       ▼
True / False
```

The public call remains the same:
```python
limiter.allow_request("Alice")
```

Only the backend responsible for processing the request changes.

---

# Core Request Lifecycle

Regardless of how a request enters the system, the core rate-limiting process remains:

```text
RateLimiter
     │
     ▼
RateLimiterBackend
     │
     ├────────────────┐
     │                │
     ▼                ▼
InMemoryBackend   RedisBackend
     │                │
     ▼                ▼
TokenBucket       Lua Script
     │                │
     └────────┬───────┘
              ▼
       Allow / Reject
```

The shared part of the architecture is the `RateLimiter` → `RateLimiterBackend` boundary.
The API layer does not contain a separate rate-limiting implementation. Backend-specific processing occurs behind the common backend interface.

---

## Why This Flow?

The request lifecycle keeps responsibilities separated.

- FastAPI
   → HTTP interface
- RateLimiter
   → Public rate-limiting interface and backend delegation
- InMemoryBackend
   → In-memory user-to-bucket management
- TokenBucket
   → In-memory token state and refill behavior
- RedisBackend
   → Redis-backed bucket processing
- The API layer converts the core decision into an HTTP response.

This separation allows the same rate-limiting logic to be reused by different interfaces without duplicating implementation.

It also provides a stable foundation for additional backend and infrastructure integrations.

---

# Thread Safety Architecture

Beginning with **v0.3.0**, the project became thread-safe to support concurrent request processing within a single Python process.
Without synchronization, multiple threads accessing shared data simultaneously could produce inconsistent behavior, resulting in race conditions.
To prevent this, the project uses **fine-grained locking** with Python's `threading.Lock`.
In **v0.7.0**, thread safety for the in-memory implementation remains based on Python locks, while Redis-backed request processing relies on the atomic execution of the Redis Lua script rather than Python `threading.Lock`.

---

## Locking Strategy

The architecture uses two independent locks.

```
                InMemoryBackend
                       │
               Lock (Dictionary)
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
   User "Alice"                User "Bob"
         │                           │
         ▼                           ▼
 TokenBucket Lock             TokenBucket Lock
         │                           │
         ▼                           ▼
 Current Tokens              Current Tokens
 Last Refill Time            Last Refill Time
```

Each lock protects only the data that belongs to its own component.

---

## InMemoryBackend Lock

The `InMemoryBackend` owns the shared dictionary containing each user's `TokenBucket`.

Its backend lock protects:

- Bucket creation
- Bucket lookup
- Shared dictionary modifications

Without this lock, two threads could attempt to create the same user's bucket simultaneously.

---

## TokenBucket Lock

Every `TokenBucket` maintains its own lock.

This lock protects:

- Current token count
- Last refill timestamp
- Token refill calculations
- Token consumption

Because every bucket owns an independent lock, requests for different users can still execute concurrently.

---

## Redis Atomicity

The Redis backend does not use Python locks to protect bucket state.

Instead, the complete read, refill calculation, request decision, state update, and TTL refresh are performed inside a single Redis Lua script invocation.

```text
RedisBackend
     │
     ▼
Redis EVAL
     │
     ▼
Lua Script
     │
     ├── Read state
     ├── Get Redis time
     ├── Refill tokens
     ├── Check request
     ├── Consume token
     ├── Update state
     └── Refresh TTL
```

This prevents concurrent Redis operations from interleaving between the read and update stages of the bucket operation.

---

## Why Fine-Grained Locking?

Instead of locking the entire application for every request, each component protects only the data it owns.

This approach provides several advantages:

- Better concurrency
- Reduced lock contention
- Improved scalability
- Clear ownership of shared state

The fine-grained locking strategy protects the in-memory state while allowing requests for different users to proceed concurrently.

The FastAPI integration introduced in **v0.6.0** uses the same thread-safe `RateLimiter` implementation. The API layer does not introduce a separate concurrency mechanism for rate limiting.

As the project evolves, this architecture will make it easier to replace the in-memory storage with external systems such as Redis without significantly changing the public API.

---

## Current Scope

The in-memory implementation guarantees thread safety within a **single Python process**.
Multiple API workers or application instances using the in-memory backend would maintain separate rate-limiter state.
The Redis backend stores bucket state externally and performs request processing atomically through a Redis Lua script. This provides a foundation for sharing rate-limit state across multiple application instances.
However, the project has not yet demonstrated a multi-server deployment or full distributed deployment architecture.
The current architecture also does not include Redis health checks, automatic reconnection, failure recovery, authentication/TLS configuration, or dedicated Redis configuration management.

---

# Architecture Evolution

The current architecture is intentionally designed to evolve incrementally while maintaining a stable public API.

Instead of redesigning the project for every new feature, each release extends the existing architecture in a controlled manner.

The following roadmap illustrates how the system will grow.

```
                         Client
                           │
                           ▼
                    FastAPI Service
                           │
                           ▼
                     RateLimiter
                           │
                           ▼
                RateLimiterBackend
                      │       │
                      │       │
                      ▼       ▼
                In-Memory   Redis
                 Backend    Backend
```

The current architecture already supports both in-memory and Redis-backed storage. Future releases will extend the surrounding infrastructure without unnecessarily changing the core backend boundary.

---

## ✅ v0.6.0 — FastAPI Integration

FastAPI integration has been implemented as an HTTP interface around the existing `RateLimiter` package.

The API currently exposes:

```text
GET  /
POST /allow
```

The `POST /allow` endpoint accepts a user identifier through the request body and delegates the rate-limiting decision to the existing `RateLimiter`.

The API layer remains intentionally thin.

Its responsibilities are:

- Accept HTTP requests.
- Validate request data.
- Call the `RateLimiter`.
- Convert the result into an HTTP response.
- Return appropriate HTTP status codes.

The rate-limiting logic remains inside the `ratelimiter` package.

This architecture allows the core package to continue functioning independently from the FastAPI integration.

---

## v0.7.0 — Redis Backend & Backend Abstraction

Version **v0.7.0** introduces a pluggable backend architecture.

The `RateLimiter` now delegates request processing to a `RateLimiterBackend` implementation.

Two backends are currently available:

```text
             RateLimiter
                  │
                  ▼
        RateLimiterBackend
             │         │
             ▼         ▼
     InMemoryBackend  RedisBackend
```

`InMemoryBackend` preserves the existing Python-based bucket storage model, where each user maps to a `TokenBucket`.
`RedisBackend` provides externally stored bucket state using Redis hashes and an atomic Lua script.
The Redis implementation also uses Redis server-side time and TTL-based cleanup for inactive buckets.
The backend abstraction allows the public RateLimiter interface to remain independent of the underlying storage mechanism.
Detailed Redis architecture is documented separately in: `docs/REDIS_BACKEND.md`

---

## v0.8.0 — Docker

The application is planned to be containerized using Docker.

Containerization provides:

- Consistent development environments
- Simplified deployment
- Easy dependency management
- Improved portability

---

## v0.9.0 — CI/CD

Continuous Integration will automatically verify code quality for every GitHub push.

Planned workflow:

```
Git Push
    │
    ▼
GitHub Actions
    │
    ▼
Run Tests
    │
    ▼
Build Package
    │
    ▼
Success / Failure
```

This ensures that every change is automatically validated before integration.

---

## v1.0.0 — Production Ready

The final release aims to combine all previous milestones into a maintainable, reusable, and production-focused Python package.

Expected characteristics include:

- Modular architecture
- Automated testing
- Thread-safe implementation
- Redis-backed storage
- FastAPI integration
- Docker support
- CI/CD automation
- Comprehensive documentation

---

# Architecture Principles

Throughout every release, the architecture follows several guiding principles:

- Separation of concerns
- Single Responsibility Principle (SRP)
- Modularity
- Maintainability
- Extensibility
- Integration-layer separation
- Incremental evolution

---

## Separation of Concerns

Each component should have a clearly defined responsibility.

The FastAPI layer handles HTTP concerns, while the `ratelimiter` package handles rate-limiting behavior.

This prevents web-framework-specific logic from becoming part of the core algorithm.

---

## Single Responsibility Principle

Each major component is responsible for one primary concern.

```text
FastAPI
  → HTTP interface

RateLimiter
  → Public interface and backend delegation

RateLimiterBackend
  → Backend contract

InMemoryBackend
  → In-memory bucket management

TokenBucket
  → In-memory token state and refill logic

RedisBackend
  → Redis-backed bucket processing
```

Keeping these responsibilities separate makes individual components easier to understand, test, and modify.

---

## Integration-Layer Separation

The FastAPI integration introduced in **v0.6.0** is treated as an integration layer around the core package.

The API communicates with the `RateLimiter` through its public interface rather than implementing rate-limiting behavior itself.

This allows the same core package to be used through different interfaces without duplicating the underlying logic.

---

## Modularity

The project is divided into focused modules and packages rather than keeping all functionality in a single file.

The current structure separates:

- Core rate-limiting interface and algorithm components.
- Backend implementations.
- FastAPI integration.
- Automated tests.
- Technical documentation.

This structure provides a foundation for future architectural changes.

---

## Maintainability

The architecture favors simple components with clear responsibilities over unnecessary abstraction.

New functionality should be introduced only when it provides a clear architectural or functional benefit.

---

## Extensibility

The current architecture is designed to accommodate future integrations.

For example, the backend abstraction allows the existing in-memory implementation and Redis implementation to coexist without requiring the FastAPI layer to implement storage-specific behavior.

---

## Incremental Evolution

The project is intentionally developed through versioned milestones.

Each release introduces a major engineering concept:

```text
v0.1.0 → Core Algorithm
v0.2.0 → Multi-User Support
v0.3.0 → Thread Safety
v0.4.0 → Automated Testing
v0.5.0 → Python Packaging
v0.6.0 → FastAPI Integration
v0.7.0 → Backend Abstraction + Redis Backend
v0.8.0 → Docker
v0.9.0 → CI/CD
v1.0.0 → Production Ready
```

Rather than implementing every feature from the beginning, the project evolves through small, well-defined engineering milestones.

This approach allows each architectural change to be implemented, tested, documented, and understood before the next major capability is introduced.

---

## Architectural Direction

The architecture currently follows this direction:

```text
Client
  │
  ▼
FastAPI
  │
  ▼
RateLimiter
  │
  ▼
RateLimiterBackend
  │
  ├── InMemoryBackend
  │       │
  │       ▼
  │   TokenBucket
  │
  └── RedisBackend
          │
          ▼
      Lua Script
          │
          ▼
        Redis
```

The architecture now separates the public rate-limiting interface from backend-specific state management.
This allows the in-memory and Redis implementations to evolve independently while preserving the same `RateLimiter` interface.
Future releases will extend the infrastructure around this architecture rather than replacing the existing backend boundary.
Planned additions such as Docker and CI/CD will operate around the existing application and package structure.