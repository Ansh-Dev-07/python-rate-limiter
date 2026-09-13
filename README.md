# Python Rate Limiter

A production-focused **Token Bucket Rate Limiter** implemented in Python, built incrementally from a simple in-memory algorithm into a reusable, well-tested package with a FastAPI HTTP interface.

This project documents the engineering journey of designing, testing, packaging, and exposing a backend component through modern software engineering practices.

Current Version: **v0.7.0**

---

## Why this project?

Most tutorials focus on writing code that works.

This project focuses on **building software the way it evolves in the real world**.

Each release introduces a single engineering milestone instead of implementing everything at once.

The repository demonstrates the progression from:

* A basic Token Bucket algorithm
* Multi-user request handling
* Thread-safe concurrency
* Automated testing
* Python package organization
* FastAPI integration
* Redis-backed storage
* Backend abstraction
* (Upcoming) Docker support
* (Upcoming) CI/CD automation

Every version remains available through GitHub Releases, allowing the evolution of the project to be explored step by step.

---

## Features

### Core Features

* ✅ Token Bucket rate limiting algorithm
* ✅ Configurable capacity and refill rate
* ✅ Lazy token refill
* ✅ Independent buckets for multiple users
* ✅ Thread-safe implementation
* ✅ Automated unit tests
* ✅ Reusable Python package
* ✅ Installable using `pip`
* ✅ FastAPI HTTP interface
* ✅ Redis backend
* ✅ Pluggable backend abstraction
* ✅ Atomic Redis operations using Lua
* ✅ Redis server-side time
* ✅ Redis TTL-based bucket cleanup

### Current Scope

* In-memory and Redis-backed storage
* Pluggable rate limiter backend architecture
* Thread-safe in-memory rate limiting
* Atomic Redis-backed request processing
* Redis TTL-based cleanup of inactive buckets
* Automated unit, API, and Redis integration tests
* Modular Python package structure
* FastAPI-based HTTP API
* Shared external rate-limit state through Redis

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Ansh-Dev-07/python-rate-limiter.git
cd python-rate-limiter
```

Install the project:

```bash
pip install .
```

For editable development installation:

```bash
pip install -e .
```
> **Redis note:** v0.7.0 includes the Redis Python client as a project dependency. A running Redis server is required when using `RedisBackend` or running the Redis integration tests.

> **Note:** Beginning with **v0.5.0**, the project is organized as a reusable Python package following standard Python packaging conventions.

---

## Quick Start

The core rate limiter can be used directly as a Python library.

```python
from ratelimiter import RateLimiter

# Create a rate limiter
limiter = RateLimiter(capacity=5, refill_rate=1)

# Simulate a request from a user
if limiter.allow_request("Ansh"):
    print("Request Allowed")
else:
    print("Rate Limit Exceeded")
```

Each user receives an independent token bucket, while the underlying token bucket implementation handles token consumption and refill.

---

## Redis Backend

Beginning with **v0.7.0**, the project supports Redis as an alternative storage backend.

The rate limiter now uses a backend abstraction:

```text
RateLimiter
     ↓
RateLimiterBackend
     ↓
┌────┴────────────┐
↓                 ↓
InMemoryBackend  RedisBackend
                    ↓
                 Lua Script
                    ↓
                  Redis
```
The in-memory backend stores user buckets inside the Python process, while the Redis backend stores bucket state externally in Redis.

Each Redis-backed user bucket is stored using a Redis hash containing:

ratelimiter:user:<user>
├── current_tokens
└── last_refill_time

The Redis backend performs the token refill, request decision, state update, and TTL refresh inside a Lua script.

Redis server-side time is used for refill calculations, and inactive buckets are automatically removed through Redis key expiration.

For a detailed explanation of the Redis architecture, data model, Lua script, server-side time, TTL behavior, and testing, see:

docs/REDIS_BACKEND.md

---

## FastAPI API

Beginning with **v0.6.0**, the rate limiter can also be accessed through a FastAPI HTTP interface.

### Start the API

From the project root:

```bash
uvicorn api.main:app --reload
```

The API will start locally and can be accessed through:

```text
http://127.0.0.1:8000
```

FastAPI also provides interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

### Available Endpoints

#### Health Check

```http
GET /
```

Returns a simple response confirming that the API is running.

#### Allow Request

```http
POST /allow
```

Request body:

```json
{
  "user": "Ansh"
}
```

The endpoint passes the user identifier to the underlying `RateLimiter`.

If a token is available, the request is allowed.

If the user's bucket has no available tokens, the API responds with HTTP `429 Too Many Requests`.

The FastAPI layer is intentionally kept separate from the core rate-limiting implementation. The API handles HTTP concerns while `RateLimiter` and `TokenBucket` remain responsible for rate-limiting behavior.

---

## Running the Test Suite

Execute all automated tests using:

```bash
python -m unittest discover
```

The current test suite contains **23 tests** covering the core rate limiter and FastAPI API and Redis.

Expected result:

```text
Ran 23 tests in XX.XXXs

OK
```
Execute Redis automated tests using:

```bash
python -m unittest tests.test_redis_backend
```

The current test suite contains **8 tests**.

Expected results:

```text
Ran 8 tests in 21.732s

OK
```

All tests should pass successfully before introducing new features or refactoring existing code.

For more detailed output:

```bash
python -m unittest discover -v
```

---

## Project Structure

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

### File Overview

| File / Directory              | Purpose                                                                          |
|-------------------------------|----------------------------------------------------------------------------------|
| `ratelimiter/`                | Core Python package containing the rate-limiting implementation.                 |
| `ratelimiter/backends/`       | Backend abstraction and storage implementations for the rate limiter.            |
| `api/`                        | FastAPI application layer exposing the rate limiter through HTTP endpoints.      |
| `tests/`                      | Automated test suite for the core package and API.                               |
| `tests/test_redis_backend.py` | Integration tests for Redis-backed rate limiting.                                |
| `docs/`                       | Detailed project documentation.                                                  |
| `pyproject.toml`              | Python package configuration and project metadata.                               |
| `README.md`                   | Project overview, installation, usage, and API quick start.                      |
| `CHANGELOG.md`                | Version history and notable changes.                                             |
| `PROJECT_TIMELINE.md`         | Long-term roadmap and engineering milestones.                                    |
| `LICENSE`                     | MIT License.                                                                     |
| `.gitignore`                  | Prevents unnecessary files from being committed to Git.                          |

---

## Current Limitations

The project now supports both in-memory and Redis-backed rate limiting, but several production infrastructure capabilities are intentionally outside the current scope.

The following capabilities are **not** included in **v0.7.0**:
* No automatic cleanup of inactive in-memory buckets
* No Redis connection health checks
* No automatic Redis reconnection
* No Redis failure recovery
* No dedicated Redis configuration management
* No authentication or TLS configuration layer for Redis
* FastAPI currently uses the default in-memory backend
* No demonstrated multi-server deployment
* Not yet published to PyPI
* No Docker support
* No CI/CD pipeline

These capabilities are planned for future releases.

---

## Roadmap

The project continues to evolve through incremental releases.

| Version | Milestone                           | Status        |
| ------- | ----------------------------------- | ------------- |
| v0.1.0  | Core Token Bucket                   | ✅ Completed |
| v0.2.0  | Multi-User Rate Limiter             | ✅ Completed |
| v0.3.0  | Thread-Safe Rate Limiter            | ✅ Completed |
| v0.4.0  | Testing & Quality                   | ✅ Completed |
| v0.5.0  | Packaging & Project Structure       | ✅ Completed |
| v0.6.0  | FastAPI Integration                 | ✅ Completed |
| v0.7.0  | Redis Backend & Backend Abstraction | ✅ Completed |
| v0.8.0  | Docker                              | 🔄 Planned   |
| v0.9.0  | CI/CD                               | 🔄 Planned   |
| v1.0.0  | Production Ready                    | 🎯 Goal      |

---

## Documentation

Detailed documentation is available in the `docs/` directory.

| Document                   | Description                                                                                 |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| `docs/ARCHITECTURE.md`     | Software architecture, package structure, request flow, concurrency, and API integration.   |
| `docs/TOKEN_BUCKET.md`     | In-depth explanation of the Token Bucket algorithm and rate-limiting concepts.              |
| `docs/DESIGN_DECISIONS.md` | Engineering decisions, alternatives, trade-offs, and implementation rationale.              |
| `docs/TESTING.md`          | Testing strategy, test structure, current coverage, and future testing roadmap.             |
| `CHANGELOG.md`             | Complete release history.                                                                   |
| `PROJECT_TIMELINE.md`      | Project roadmap and engineering milestones.                                                 |
| `docs/REDIS_BACKEND.md`    | Redis backend architecture, data model, Lua processing, server-side time, TTL, and testing. |

> For the complete release history, see **CHANGELOG.md**.

---

## Author

**Ansh Soni**

GitHub: https://github.com/Ansh-Dev-07

---

## License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.

---

## Support the Project

If you find this project helpful, consider giving it a ⭐ on GitHub.

Feedback, suggestions, and contributions are always welcome.
