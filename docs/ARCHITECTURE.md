# Architecture

This document explains the architecture of the **Python Rate Limiter** project.

Unlike the README, which provides a high-level overview, this document focuses on the internal software architecture, package organization, component responsibilities, and request flow.

The architecture evolves with each project release and is intentionally designed to demonstrate software engineering principles such as modularity, separation of concerns, maintainability, and scalability.

Current Architecture Version: **v0.5.0**

---

# High-Level Architecture

At **v0.5.0**, the project is organized as a reusable Python package.

```
Application
      │
      ▼
RateLimiter
      │
      ▼
TokenBucket
      │
      ▼
Token Refill Logic
```

Each layer has a single responsibility.

- The application sends requests.
- `RateLimiter` manages users and their buckets.
- `TokenBucket` enforces rate limiting.
- The refill logic replenishes tokens based on elapsed time.

This separation keeps the implementation modular and prepares the project for future integrations such as FastAPI, Redis, and distributed deployments.

---

# Package Structure

Beginning with **v0.5.0**, the project adopts a modular package structure instead of keeping all implementation inside a single Python file.

The repository is organized into separate directories, each with a clear responsibility.

```text
python-rate-limiter/
│
├── ratelimiter/
│   ├── __init__.py
│   ├── rate_limiter.py
│   └── token_bucket.py
│
├── tests/
│   ├── __init__.py
│   ├── test_rate_limiter.py
│   └── test_token_bucket.py
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

### `tests/`

Contains automated unit tests for validating the behavior of the package.

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
| `README.md` | Project overview and quick start guide. |
| `CHANGELOG.md` | Release history. |
| `PROJECT_TIMELINE.md` | Long-term roadmap. |
| `pyproject.toml` | Python package configuration. |
| `LICENSE` | MIT License. |
| `.gitignore` | Git ignore rules. |

---

# Component Responsibilities

The project follows the **Single Responsibility Principle (SRP)**, where each component has one clearly defined purpose.

This separation makes the code easier to understand, test, maintain, and extend.

## Architecture Overview

```
                    Application
                         │
                         ▼
                RateLimiter
             (Request Manager)
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
  User "Alice"                    User "Bob"
         │                               │
         ▼                               ▼
  TokenBucket                     TokenBucket
         │                               │
         └───────────────┬───────────────┘
                         ▼
                 Token Refill Logic
```

Each user owns an independent `TokenBucket`, while the `RateLimiter` manages bucket creation and request routing.

---

## `RateLimiter`

### Responsibility

The `RateLimiter` acts as the public interface of the package.

It does **not** implement the Token Bucket algorithm itself.

Instead, it is responsible for:

- Managing all users.
- Creating buckets when a new user appears.
- Reusing existing buckets.
- Routing incoming requests to the correct bucket.
- Protecting shared bucket storage using thread synchronization.

### Why this separation?

Separating request management from token management keeps the architecture modular.

If the internal bucket implementation changes in the future (for example, Redis-backed buckets), the public interface can remain unchanged.

---

## `TokenBucket`

### Responsibility

Each `TokenBucket` represents the rate limit state for a single user.

It is responsible for:

- Tracking the current number of available tokens.
- Refilling tokens based on elapsed time.
- Allowing or rejecting requests.
- Ensuring thread-safe access to token state.

### Why one bucket per user?

Maintaining an independent bucket for every user ensures that one user's traffic never affects another user's available tokens.

This approach naturally supports multi-user rate limiting while keeping the implementation simple.

---

## Relationship Between Components

```
Application
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
Token Refill
```

The `RateLimiter` owns the collection of buckets, while each `TokenBucket` independently manages its own token state.

This separation reduces coupling between components and prepares the architecture for future storage backends such as Redis.

---

# Request Lifecycle

Every incoming request follows the same sequence of operations before being either **allowed** or **rejected**.

The following diagram illustrates the complete request flow.

```
               Incoming Request
                       │
                       ▼
        RateLimiter.allow_request(user)
                       │
                       ▼
          Does the user already exist?
                 │             │
               Yes             No
                │               │
                ▼               ▼
      Retrieve Bucket     Create TokenBucket
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
                 │               │
               Yes               No
                │                │
                ▼                ▼
        Consume One Token    Reject Request
                │
                ▼
          Return True
```

---

## Step-by-Step Flow

### Step 1 — Receive Request

The application sends a request to the `RateLimiter`.

Example:

```python
limiter.allow_request("Alice")
```

---

### Step 2 — Locate the User Bucket

The `RateLimiter` checks whether a `TokenBucket` already exists for the user.

If no bucket exists, a new one is created automatically.

---

### Step 3 — Delegate the Decision

The request is forwarded to the corresponding `TokenBucket`.

From this point onward, the `RateLimiter` is no longer involved.

---

### Step 4 — Refill Tokens

Before processing the request, the bucket calculates how much time has elapsed since the previous refill.

Instead of continuously generating tokens in the background, tokens are replenished only when the bucket is accessed.

This strategy is known as **lazy refill**.

---

### Step 5 — Allow or Reject

After the refill:

- If at least one token is available, one token is consumed and the request is allowed.
- Otherwise, the request is rejected.

The result is returned back to the application.

---

## Why This Flow?

The request lifecycle keeps responsibilities separated.

- The `RateLimiter` focuses on request routing.
- The `TokenBucket` focuses on rate-limiting logic.
- The refill mechanism remains internal to the bucket.

This design improves readability, simplifies testing, and prepares the project for future extensions such as Redis-backed storage and HTTP APIs.

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

As the project evolves, this architecture will make it easier to replace the in-memory storage with external systems such as Redis without significantly changing the public API.

---

## Current Scope

The current implementation guarantees thread safety only within a **single Python process**.

It does **not** synchronize state across multiple processes or machines.

Distributed synchronization will be introduced in future releases using Redis.

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
                 RateLimiter API
                       │
                       ▼
                RateLimiter Package
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      Redis Storage        Local Memory
             │
             ▼
      TokenBucket State
```

---

## v0.6.0 — FastAPI Integration

The `RateLimiter` package will be exposed through REST endpoints.

Example:

```
POST /request/{user}
```

The API layer will remain thin.

Its responsibility will be:

- Accept HTTP requests
- Validate input
- Call the package
- Return responses

The rate-limiting logic will continue to reside inside the `ratelimiter` package.

---

## v0.7.0 — Redis Backend

The current implementation stores buckets in memory.

This means the application loses all rate-limiting state after a restart.

In v0.7.0, bucket storage will become pluggable.

Instead of storing user buckets inside a local dictionary, the application will persist bucket state in Redis.

Benefits include:

- Shared state across application instances
- Horizontal scalability
- Persistent bucket storage
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
- Incremental evolution

Rather than implementing every feature from the beginning, the project evolves through small, well-defined engineering milestones.

This approach mirrors how production software is commonly developed and maintained.