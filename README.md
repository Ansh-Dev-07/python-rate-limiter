# Python Rate Limiter

A production-oriented **Token Bucket Rate Limiter** implemented in Python, built incrementally from a simple in-memory algorithm into a reusable, well-tested package with a FastAPI HTTP interface.

This project documents the engineering journey of designing, testing, packaging, and exposing a backend component through modern software engineering practices.

Current Version: **v0.6.0**

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
* (Upcoming) Redis backend
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

### Current Scope

* Single-process execution
* In-memory storage
* Thread-safe rate limiting
* Automated unit and API tests
* Modular Python package structure
* FastAPI-based HTTP API
* Ready for future Redis-backed storage

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
python -m unittest discover tests
```

The current test suite contains **15 tests** covering the core rate limiter and FastAPI API.

Expected result:

```text
Ran 15 tests in X.XXXs

OK
```

All tests should pass successfully before introducing new features or refactoring existing code.

For more detailed output:

```bash
python -m unittest discover tests -v
```

---

## Project Structure

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

### File Overview

| File / Directory      | Purpose                                                                     |
| --------------------- | --------------------------------------------------------------------------- |
| `ratelimiter/`        | Core Python package containing the rate-limiting implementation.            |
| `api/`                | FastAPI application layer exposing the rate limiter through HTTP endpoints. |
| `tests/`              | Automated test suite for the core package and API.                          |
| `docs/`               | Detailed project documentation.                                             |
| `pyproject.toml`      | Python package configuration and project metadata.                          |
| `README.md`           | Project overview, installation, usage, and API quick start.                 |
| `CHANGELOG.md`        | Version history and notable changes.                                        |
| `PROJECT_TIMELINE.md` | Long-term roadmap and engineering milestones.                               |
| `LICENSE`             | MIT License.                                                                |
| `.gitignore`          | Prevents unnecessary files from being committed to Git.                     |

---

## Current Limitations

Although the project now includes automated testing, thread safety, package organization, and a FastAPI interface, it is still intentionally focused on core backend engineering concepts.

The following capabilities are **not** included in **v0.6.0**:

* No automatic cleanup of inactive user buckets
* In-memory storage only
* No Redis integration
* No distributed rate limiting
* Not yet published to PyPI
* No Docker support
* No CI/CD pipeline

These capabilities are planned for future releases.

---

## Roadmap

The project continues to evolve through incremental releases.

| Version | Milestone                     | Status      |
| ------- | ----------------------------- | ----------- |
| v0.1.0  | Core Token Bucket             | ✅ Completed |
| v0.2.0  | Multi-User Rate Limiter       | ✅ Completed |
| v0.3.0  | Thread-Safe Rate Limiter      | ✅ Completed |
| v0.4.0  | Testing & Quality             | ✅ Completed |
| v0.5.0  | Packaging & Project Structure | ✅ Completed |
| v0.6.0  | FastAPI Integration           | ✅ Completed |
| v0.7.0  | Redis Backend                 | 🔄 Planned  |
| v0.8.0  | Docker                        | 🔄 Planned  |
| v0.9.0  | CI/CD                         | 🔄 Planned  |
| v1.0.0  | Production Ready              | 🎯 Goal     |

---

## Documentation

Detailed documentation is available in the `docs/` directory.

| Document                   | Description                                                                               |
| -------------------------- | ----------------------------------------------------------------------------------------- |
| `docs/ARCHITECTURE.md`     | Software architecture, package structure, request flow, concurrency, and API integration. |
| `docs/TOKEN_BUCKET.md`     | In-depth explanation of the Token Bucket algorithm and rate-limiting concepts.            |
| `docs/DESIGN_DECISIONS.md` | Engineering decisions, alternatives, trade-offs, and implementation rationale.            |
| `docs/TESTING.md`          | Testing strategy, test structure, current coverage, and future testing roadmap.           |
| `CHANGELOG.md`             | Complete release history.                                                                 |
| `PROJECT_TIMELINE.md`      | Project roadmap and engineering milestones.                                               |

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
