# Architecture

This document explains the architecture of the **Python Rate Limiter** project.

Unlike the README, which provides a high-level overview, this document focuses on the internal software architecture, package organization, component responsibilities, and request flow.

The architecture evolves with each project release and is intentionally designed to demonstrate software engineering principles such as modularity, separation of concerns, maintainability, and scalability.

Current Architecture Version: **v0.6.0**

---

# High-Level Architecture

At **v0.6.0**, the project consists of a reusable Python package and a FastAPI-based HTTP integration layer.

The FastAPI layer exposes the existing rate limiter through HTTP endpoints while keeping the core rate-limiting implementation independent from the web framework.

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
                           │
                           ▼
                    ┌──────────────┐
                    │ RateLimiter  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ TokenBucket  │
                    └──────┬───────┘
                           │
                           ▼
                    Token Refill Logic
```

Each layer has a distinct responsibility.

- The **client** sends HTTP requests to the API.
- **FastAPI** handles HTTP routing, request validation, and HTTP responses.
- `RateLimiter` manages users and their corresponding token buckets.
- `TokenBucket` enforces the rate-limiting rules for an individual user.
- The **token refill logic** replenishes tokens based on elapsed time.

The FastAPI layer acts as an integration boundary around the existing rate-limiting package. The core `RateLimiter` and `TokenBucket` classes do not depend on FastAPI.

This separation allows the same rate-limiting implementation to be used directly as a Python library or through the HTTP API.

The architecture also provides a foundation for future integrations such as Redis-backed storage, Docker deployment, and CI/CD automation.

---

# Package Structure 

Beginning with **v0.5.0**, the project adopts a modular package structure instead of keeping all implementation inside a single Python file. In **v0.6.0**, a separate `api/` directory was added to contain the FastAPI integration layer.

The repository is organized into separate directories, each with a clear responsibility.

```text
python-rate-limiter/
│
├── ratelimiter/
│   ├── __init__.py
│   ├── rate_limiter.py
│   └── token_bucket.py
│
├── api/
│   ├── __init__.py
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   ├── test_rate_limiter.py
│   ├── test_token_bucket.py
│   └── test_api.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── TOKEN_BUCKET.md
│   ├── DESIGN_DECISIONS.md
│   └── TESTING.md
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
| `rate_limiter.py` | Manages users and routes requests to their corresponding token buckets. |
| `token_bucket.py` | Implements the Token Bucket algorithm and token refill logic. |

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

Beginning with **v0.6.0**, the architecture is divided into two major layers:

1. The **API integration layer**
2. The **core rate-limiting package**

The API layer handles HTTP-specific concerns, while the core package remains responsible for rate-limiting behavior.

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
                    │ Core Package │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       User "Alice"               User "Bob"
              │                         │
              ▼                         ▼
       TokenBucket                 TokenBucket
              │                         │
              └────────────┬────────────┘
                           ▼
                   Token Refill Logic
```

The important architectural boundary is between the FastAPI integration and the `ratelimiter` package.

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

It is responsible for:

- Managing users.
- Creating buckets when a new user appears.
- Reusing existing buckets.
- Routing incoming requests to the correct bucket.
- Protecting shared bucket storage using thread synchronization.

The `RateLimiter` does not implement HTTP handling.

It also does not implement the Token Bucket algorithm itself.

Instead, it delegates token-level decisions to the appropriate `TokenBucket`.

### Why This Separation?

Separating request management from token management keeps the core package modular.

The API layer can therefore change independently from the rate-limiting implementation.

Similarly, future storage changes can occur without requiring the FastAPI endpoints to contain rate-limiting logic.

---

## `TokenBucket`

### Responsibility

Each `TokenBucket` represents the rate-limit state for a single user.

It is responsible for:

- Tracking the current number of available tokens.
- Refilling tokens based on elapsed time.
- Allowing or rejecting requests.
- Ensuring thread-safe access to token state.

The `TokenBucket` is independent of FastAPI.

It operates entirely within the core rate-limiting package.

### Why One Bucket Per User?

Maintaining an independent bucket for every user ensures that one user's traffic does not consume another user's available tokens.

This provides isolated rate limiting while keeping the implementation straightforward.

---

## Relationship Between Components

The components communicate through clear boundaries:

```text
HTTP Request
     │
     ▼
FastAPI
     │
     ▼
RateLimiter
     │
     ▼
Dictionary
(user → TokenBucket)
     │
     ▼
TokenBucket
     │
     ▼
Token Refill Logic
```

The `api/` layer owns HTTP concerns.

The `RateLimiter` owns user-to-bucket management.

Each `TokenBucket` owns the rate-limit state for one user.

This separation reduces coupling and prepares the project for future storage backends such as Redis.

---

# Request Lifecycle

At **v0.6.0**, requests can reach the rate-limiting core through two entry points:

1. Direct Python library usage.
2. The FastAPI HTTP integration.

Both paths eventually use the same `RateLimiter` and `TokenBucket` implementation.

This ensures that the HTTP API does not duplicate or redefine the core rate-limiting logic.

---

## HTTP Request Lifecycle

When a client uses the FastAPI integration, the request follows this flow:

```text
HTTP Client
     │
     │ POST /allow
     │
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
Does the user already exist?
     │
     ├───────────────┐
     │               │
    Yes              No
     │               │
     ▼               ▼
Retrieve Bucket   Create TokenBucket
     │               │
     └───────┬───────┘
             ▼
   TokenBucket.allow_request()
             │
             ▼
      Refill Available Tokens
             │
             ▼
 Is at least one token available?
        │             │
       Yes            No
        │             │
        ▼             ▼
Consume Token     Reject Request
        │             │
        ▼             ▼
   Return True    Return False
        │             │
        ▼             ▼
 HTTP 200         HTTP 429
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

### Step 4 — Locate the User Bucket

The `RateLimiter` checks whether a `TokenBucket` already exists for the user.

If the user already has a bucket, the existing bucket is reused.

If the user is new, a new `TokenBucket` is created.

---

### Step 5 — Delegate to TokenBucket

The request is forwarded to the corresponding `TokenBucket`.

The bucket is responsible for deciding whether the request can be allowed.

---

### Step 6 — Refill Tokens

Before processing the request, the bucket calculates how much time has elapsed since the previous refill.

Instead of continuously generating tokens in the background, tokens are replenished only when the bucket is accessed.

This strategy is known as **lazy refill**.

---

### Step 7 — Allow or Reject

After the refill:

- If at least one token is available, one token is consumed and the request is allowed.
- If no token is available, the request is rejected.

The resulting decision is returned to the API layer.

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

# Direct Python Request Lifecycle

The core package can also be used without FastAPI.

In this case, the application calls the `RateLimiter` directly:

```python
limiter.allow_request("Alice")
```

The flow is:

```text
Python Application
       │
       ▼
RateLimiter.allow_request(user)
       │
       ▼
Does the user already exist?
       │
       ├───────────────┐
       │               │
      Yes              No
       │               │
       ▼               ▼
Retrieve Bucket    Create TokenBucket
       │               │
       └───────┬───────┘
               ▼
      TokenBucket.allow_request()
               │
               ▼
       Refill Available Tokens
               │
               ▼
   Is at least one token available?
          │             │
         Yes            No
          │             │
          ▼             ▼
   Consume Token    Reject Request
          │             │
          ▼             ▼
        True         False
```

The core behavior is identical to the HTTP path.

The only difference is the entry point.

---

# Core Request Lifecycle

Regardless of how a request enters the system, the core rate-limiting process remains:

```text
RateLimiter
     │
     ▼
Find or Create User Bucket
     │
     ▼
TokenBucket
     │
     ▼
Refill Tokens
     │
     ▼
Check Available Tokens
     │
     ├───────────────┐
     │               │
   Available      Unavailable
     │               │
     ▼               ▼
Consume Token      Reject
     │               │
     ▼               ▼
  Allowed         Rejected
```

This shared core flow is important because the API layer does not contain a separate rate-limiting implementation.

---

## Why This Flow?

The request lifecycle keeps responsibilities separated.

- **FastAPI** handles HTTP routing and request validation.
- `RateLimiter` handles user-to-bucket management.
- `TokenBucket` handles token availability and refill behavior.
- The API layer converts the core decision into an HTTP response.

This separation allows the same rate-limiting logic to be reused by different interfaces without duplicating implementation.

It also provides a stable foundation for future integrations such as Redis-backed storage.

---

# Thread Safety Architecture

Beginning with **v0.3.0**, the project became thread-safe to support concurrent request processing within a single Python process.

Without synchronization, multiple threads accessing shared data simultaneously could produce inconsistent behavior, resulting in race conditions.

To prevent this, the project uses **fine-grained locking** with Python's `threading.Lock`.

---

## Locking Strategy

The architecture uses two independent locks.

```
                 RateLimiter
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
 Current Tokens             Current Tokens
 Last Refill Time           Last Refill Time
```

Each lock protects only the data that belongs to its own component.

---

## RateLimiter Lock

The `RateLimiter` owns a shared dictionary containing every user's bucket.

Its lock protects:

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

The current implementation guarantees thread safety only within a **single Python process**.

It does **not** synchronize state across multiple processes or machines.

The FastAPI integration does not change this limitation. Multiple API workers or application instances would maintain separate in-memory rate-limiter state.

Distributed synchronization is planned for **v0.7.0** through the Redis backend.
---

# Future Architecture

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
                    Storage Backend
                      │         │
                      │         │
                      ▼         ▼
                In-Memory      Redis
                 (Current)    (v0.7.0)
```

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

## v0.7.0 — Redis Backend

The current implementation stores buckets in memory.

The FastAPI integration introduced in v0.6.0 currently uses the same in-memory `RateLimiter` state.

This means the application loses all rate-limiting state after a restart.

In v0.7.0, bucket storage will be moved from local in-memory state to Redis.

Instead of storing user buckets inside a local dictionary, the application will persist bucket state in Redis.

Benefits include:

- Shared state across application instances
- Horizontal scalability
- Externalized bucket storage
- Preparation for distributed deployments

---

## v0.8.0 — Docker

The application will be containerized using Docker.

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

The final release aims to combine all previous milestones into a maintainable, reusable, and production-oriented Python package.

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
  → User and bucket management

TokenBucket
  → Token state and rate-limiting decisions
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

- Core rate-limiting logic.
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

For example, the current in-memory storage can eventually be replaced by Redis without requiring the FastAPI layer to implement the storage mechanism itself.

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
v0.7.0 → Redis Backend
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
TokenBucket
  │
  ▼
In-Memory State
```

Future releases will extend the lower layers without unnecessarily changing the API boundary:

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
Storage Backend
  │
  ├── In-Memory
  │
  └── Redis (v0.7.0)
```

The goal is to evolve the implementation while preserving clear boundaries between interfaces, core logic, and infrastructure.