# Project Timeline

This document outlines the development roadmap for the **Python Rate Limiter** project.

The goal of this project is to build a production-ready rate limiter incrementally while learning backend engineering, software architecture, concurrency, testing, packaging, deployment, and distributed systems.

---

# Project Roadmap

| Version | Milestone                        | Status    |
|----------|---------------------------------|-----------|
| ✅ v0.1.0 | Core Token Bucket Algorithm   | Completed |
| ✅ v0.2.0 | Multi-User Rate Limiter       | Completed |
| ✅ v0.3.0 | Thread-Safe Rate Limiter      | Completed |
| ✅ v0.4.0 | Testing & Quality             | Completed |
| ✅ v0.5.0 | Packaging & Project Structure | Completed |
| ✅ v0.6.0 | FastAPI Integration           | Completed |
| 🔄 v0.7.0 | Redis Backend                 | Planned   |
| 🔄 v0.8.0 | Docker                        | Planned   |
| 🔄 v0.9.0 | CI/CD                         | Planned   |
| 🎯 v1.0.0 | Production-Ready Release      | Goal      |

---

# Release Details

## ✅ v0.1.0 — Core Token Bucket

### Objectives
- Understand the Token Bucket algorithm.
- Implement a basic in-memory token bucket.
- Support configurable capacity and refill rate.
- Implement lazy token refill.
- Validate constructor inputs.

### Outcome
Successfully implemented a working Token Bucket capable of allowing or rejecting requests based on available tokens.

---

## ✅ v0.2.0 — Multi-User Rate Limiter

### Objectives
- Introduce the `RateLimiter` class.
- Manage one token bucket per user.
- Implement lazy bucket creation.
- Improve object-oriented architecture.

### Outcome
Each user now has an independent token bucket, allowing separate rate limits while maintaining clean code organization.

---

## ✅ v0.3.0 — Thread-Safe Rate Limiter

### Objectives
- Make bucket creation thread-safe.
- Protect shared bucket state from race conditions.
- Make token consumption thread-safe.
- Support concurrent requests safely.

### Outcome
The project now supports concurrent access using `threading.Lock`. Shared resources are protected, race conditions are prevented, and each token bucket maintains its own synchronization.

### Concepts Learned
- Thread synchronization
- Race conditions
- Mutual exclusion
- Fine-grained locking
- Concurrent programming fundamentals

---

## ✅ v0.4.0 — Testing & Quality

### Objectives

- Introduce automated testing using Python's `unittest` framework.
- Replace manual verification with repeatable automated tests.
- Validate the behavior of both `RateLimiter` and `TokenBucket`.
- Organize tests separately from the implementation.

### Outcome

The project now includes automated unit tests that verify the core functionality of the rate limiter. Both the `RateLimiter` and `TokenBucket` classes are covered by dedicated test suites, improving confidence in future changes and reducing the risk of regressions.

### Features Implemented

- Automated unit testing using Python's `unittest`
- Dedicated `RateLimiter` test suite
- Dedicated `TokenBucket` test suite
- Constructor validation tests
- Request allowance and rejection tests
- Multi-user behavior verification
- Token refill verification

### Concepts Learned

- Unit testing
- Test automation
- Regression testing
- Test organization
- Software quality practices

---

## ✅ v0.5.0 — Packaging & Project Structure

### Objectives
- Refactor the project into a proper Python package.
- Organize the code into modules.
- Improve maintainability and scalability.
- Prepare the project for installation via `pip`.

### Key Learning Objectives
- Python packaging
- Project organization
- Module design

### Outcome

The project was successfully reorganized into a reusable Python package with a dedicated `ratelimiter/` package, modern packaging configuration through `pyproject.toml`, and separate directories for tests and documentation.

The package can now be installed locally using standard Python packaging tools.

---

## ✅ v0.6.0 — FastAPI Integration

### Objectives

- Expose the rate limiter through HTTP APIs.
- Integrate the existing `RateLimiter` package with FastAPI.
- Keep the core rate-limiting logic independent from the web framework.
- Build reusable API endpoints.
- Add API-level testing alongside the existing unit tests.

### Features Implemented

- Added FastAPI integration through the `api/` directory.
- Added `api/main.py` containing the FastAPI application.
- Added a root `GET /` endpoint.
- Added a `POST /allow` endpoint for processing rate-limit requests.
- Added dependency injection for the `RateLimiter` instance.
- Added HTTP `429` responses when the rate limit is exceeded.
- Added request validation for missing or invalid `user` values.
- Added `tests/test_api.py` for API integration testing.
- Added API tests for successful requests, rate-limit rejection, validation errors, and independent users.

### Outcome

The project now exposes the reusable rate limiter through a FastAPI-based HTTP layer while keeping the underlying `RateLimiter` and `TokenBucket` components independent from the web framework.

The v0.6.0 milestone extends the project from a standalone Python package into a backend component that can be consumed through HTTP APIs.

### Concepts Learned

- FastAPI
- HTTP API design
- HTTP request and response handling
- Dependency injection
- Request validation
- API integration testing
- Separation between core business logic and framework-specific integration

---

## 🔄 v0.7.0 — Redis Backend

### Objectives
- Replace in-memory bucket storage with Redis.
- Enable shared state across multiple application instances.
- Prepare for horizontal scalability.

### Key Learning Objectives
- Redis
- Shared storage
- Distributed state management

---

## 🔄 v0.8.0 — Docker

### Objectives
- Containerize the application.
- Create Docker images.
- Simplify deployment across environments.

### Key Learning Objectives
- Docker
- Containerization
- Deployment fundamentals

---

## 🔄 v0.9.0 — CI/CD

### Objectives
- Automatically run tests on every GitHub push.
- Configure GitHub Actions.
- Maintain code quality through automated workflows.

### Key Learning Objectives
- GitHub Actions
- Continuous Integration
- Continuous Deployment

---

## 🎯 v1.0.0 — Production-Ready Release

### Objectives
- Final code cleanup.
- Performance optimization.
- Complete documentation.
- Stable public release.

### Expected Outcome
A well-tested, maintainable, scalable, and production-oriented Python Rate Limiter demonstrating the complete engineering journey from a simple algorithm to a deployable backend component.

---

# Learning Journey

This project is intentionally built through versioned milestones.

Each release introduces one major software engineering concept instead of implementing everything at once. The objective is not only to build a rate limiter but also to understand the engineering decisions behind it.

The roadmap may evolve as the project grows, but every release focuses on one major engineering milestone. This incremental approach encourages learning the reasoning behind each feature instead of simply adding functionality.

The long-term objective is not just to build a rate limiter, but to understand how production software evolves through architecture, testing, packaging, APIs, infrastructure, and deployment.