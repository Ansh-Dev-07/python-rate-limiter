# Python Rate Limiter

A production-oriented **Token Bucket Rate Limiter** implemented in Python, built incrementally from a simple in-memory algorithm into a reusable, well-tested package.

This project documents the complete engineering journey of designing, testing, packaging, and evolving a backend component using modern software engineering practices.

Current Version: **v0.5.0**

---

## Why this project?

Most tutorials focus on writing code that works.

This project focuses on **building software the way it evolves in the real world**.

Each release introduces a single engineering milestone instead of implementing everything at once.

The repository demonstrates the progression from:

- A basic Token Bucket algorithm
- Multi-user request handling
- Thread-safe concurrency
- Automated testing
- Python package organization
- (Upcoming) FastAPI integration
- (Upcoming) Redis backend
- (Upcoming) Docker support
- (Upcoming) CI/CD automation

Every version remains available through GitHub Releases, allowing the evolution of the project to be explored step by step.

---

## Features

### Core Features

- ✅ Token Bucket rate limiting algorithm
- ✅ Configurable capacity and refill rate
- ✅ Lazy token refill
- ✅ Independent buckets for multiple users
- ✅ Thread-safe implementation
- ✅ Automated unit tests
- ✅ Packaged as a reusable Python library
- ✅ Installable using `pip`

### Current Scope

- Single-process execution
- In-memory storage
- Thread-safe
- Fully tested using `unittest`
- Modular package structure
- Ready for future backend integrations

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Ansh-Dev-07/python-rate-limiter.git
cd python-rate-limiter
```

Install the package locally:

```bash
pip install -e .
```

Alternatively, install directly from the project root:

```bash
pip install .
```
> **Note:** Beginning with **v0.5.0**, the project is organized as a reusable Python package and can be installed locally using standard Python packaging tools.

---

## Quick Start

```python
from ratelimiter import RateLimiter

# Create a rate limiter
limiter = RateLimiter(capacity=5, refill_rate=1)

# Simulate a request from a user
if limiter.allow_request("Ansh"):
    print("✅ Request Allowed")
else:
    print("❌ Rate Limit Exceeded")
```

---

## Running the Test Suite

Execute all automated tests using:

```bash
python -m unittest discover tests
```

Expected output:

```text
......
----------------------------------------------------------------------
Ran XX tests in X.XXXs

OK
```

All tests should pass successfully before introducing new features or refactoring existing code.

Need a deeper understanding of the project?

Explore the detailed documentation available in the **docs/** directory.

## Project Structure

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

### File Overview

| File / Directory | Purpose |
|------------------|---------|
| `ratelimiter/` | Core Python package containing the implementation. |
| `tests/` | Automated unit tests. |
| `docs/` | Detailed project documentation. |
| `pyproject.toml` | Python package configuration. |
| `README.md` | Project overview and quick start guide. |
| `CHANGELOG.md` | Version history. |
| `PROJECT_TIMELINE.md` | Long-term roadmap. |
| `LICENSE` | MIT License. |
| `.gitignore` | Git ignore rules. |

> **Note:** Beginning with **v0.5.0**, the project has been reorganized into a reusable Python package following standard Python packaging conventions.



## Current Limitations

Although the project now includes automated testing and thread safety, it is still intentionally focused on core backend engineering concepts.

The following features are **not** included in **v0.5.0**

- No automatic cleanup of inactive user buckets
- In-memory storage only
- No Redis integration
- No REST API
- Not yet published to PyPI (local installation supported)
- No Docker support
- No CI/CD pipeline
- No distributed deployment

These capabilities are planned for future releases.

---

## Roadmap

The project will continue to evolve through incremental releases.

| Version | Planned Feature               | Status        |
|---------|-------------------------------|---------------|
| v0.1.0  | Core Token Bucket             | ✅ Completed |
| v0.2.0  | Multi-User Rate Limiter       | ✅ Completed |
| v0.3.0  | Thread-Safe Rate Limiter      | ✅ Completed |
| v0.4.0  | Testing & Quality             | ✅ Completed |
| v0.5.0  | Packaging & Project Structure | ✅ Completed |
| v0.6.0  | FastAPI Integration           | 🔄 Planned   |
| v0.7.0  | Redis Backend                 | 🔄 Planned   |
| v0.8.0  | Docker                        | 🔄 Planned   |
| v0.9.0  | CI/CD                         | 🔄 Planned   |
| v1.0.0  | Production Ready              | 🎯 Goal      |

---

## 📚 Documentation

Detailed documentation has been moved into the `docs/` directory to keep this README focused and easy to navigate.

| Document | Description |
|----------|-------------|
| `docs/ARCHITECTURE.md` | System architecture, package structure, request flow, and design diagrams. |
| `docs/TOKEN_BUCKET.md` | In-depth explanation of the Token Bucket algorithm and rate limiting concepts. |
| `docs/DESIGN_DECISIONS.md` | Engineering decisions, design rationale, and implementation choices. |
| `docs/TESTING.md` | Testing strategy, test structure, and how to run and extend the test suite. |
| `CHANGELOG.md` | Complete version history and release notes. |
| `PROJECT_TIMELINE.md` | Project roadmap and upcoming milestones. |

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