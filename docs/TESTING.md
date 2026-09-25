# Testing Guide

This document describes the testing strategy used in the **Python Rate Limiter** project.

Testing is an essential part of software engineering. As the project evolves through multiple releases, automated tests help ensure that new features do not break existing functionality.

Unlike the README, which introduces the project, or the architecture and design documents, this guide focuses entirely on verifying correctness and maintaining software quality.

Current Testing Version: **v0.8.0**

---

# Testing Philosophy

The testing strategy for this project is based on one simple principle:

> **Every feature should be verifiable through automated tests.**

Instead of relying on manual execution and visual inspection, the project uses repeatable automated tests to validate the behavior of its core components and integration layers.

This approach provides several benefits:

- Detects regressions early.
- Improves confidence when refactoring code.
- Documents expected behavior.
- Encourages modular design.
- Makes future development safer.

Testing is treated as an integral part of the development process rather than an activity performed after implementation.

---

# Test Structure

Beginning with **v0.4.0**, the project introduced a dedicated `tests/` directory to separate production code from automated tests.

The repository follows a clear structure:

```text
python-rate-limiter/
│
├── ratelimiter/
│   ├── rate_limiter.py
│   ├── token_bucket.py
│   └── backends/
│       ├── base.py
│       ├── in_memory.py
│       └── redis_backend.py
│
└── tests/
    ├── __init__.py
    ├── test_rate_limiter.py
    ├── test_token_bucket.py
    ├── test_api.py
    └── test_redis_backend.py
```

Separating tests from the implementation improves maintainability and makes the project easier to understand as it grows.
The test suite is organized by the component or integration layer being verified.

---

## Test Responsibilities

Each test module focuses on a specific component of the project.

| Test File | Purpose |
|-----------|---------|
| `test_rate_limiter.py` | Verifies the behavior of the `RateLimiter` class, including bucket creation, multi-user handling, and constructor validation. |
| `test_token_bucket.py` | Verifies the Token Bucket algorithm, including token consumption, request rejection, and automatic token refill. |
| `test_api.py` | Verifies the FastAPI integration, including the root endpoint, successful requests, rate-limit rejection (`429`), request validation (`422`), and independent buckets for different users. |
| `test_redis_backend.py` | Verifies the Redis backend, including bucket creation, capacity handling, token refill, independent users, validation, concurrent requests, and bucket expiration. |

This separation follows the same design philosophy as the production code: each test module focuses on a specific component or integration boundary.

---

## Current Testing Scope

At **v0.8.0**, the automated test suite validates:
- Constructor input validation.
- Token consumption.
- Request acceptance.
- Request rejection.
- Token refill after elapsed time.
- Multi-user bucket isolation.
- Bucket reuse.
- FastAPI root endpoint behavior.
- Successful API request handling.
- HTTP `429` responses when the rate limit is exceeded.
- Request validation for missing or invalid `user` fields.
- Independent rate-limiting behavior for different users through the API.
- Redis bucket creation and state persistence.
- Redis token refill behavior.
- Redis user isolation.
- Redis-backed concurrent request handling.
- Redis bucket expiration through TTL.
The tests focus on validating observable behavior rather than unnecessarily coupling tests to internal implementation details.
The current suite contains **23 automated tests**, including **8 Redis backend integration tests**.

---

## Why Separate Tests?

Keeping tests separate from production code provides several advantages:

- Cleaner project organization.
- Easier navigation.
- Better maintainability.
- Independent development of tests and implementation.
- Simpler integration with Continuous Integration (CI) pipelines.

As the project evolves, the `tests/` directory will continue growing alongside the implementation without affecting the package structure.

---

# Running the Test Suite

The project uses Python's built-in **`unittest`** framework for automated testing.

All tests are located inside the `tests/` directory and can be executed using Python's test discovery mechanism.

---

## Running All Tests

From the project root directory, execute:

```bash
python -m unittest discover
```

Example output:

```text
.......................
----------------------------------------------------------------------
Ran 23 tests in XX.XXXs

OK
```

A successful execution confirms that the implemented unit, API, and Redis integration tests pass.

---

## Running a Specific Test File

To execute only the `RateLimiter` tests:

```bash
python -m unittest tests.test_rate_limiter
```

To execute only the `TokenBucket` tests:

```bash
python -m unittest tests.test_token_bucket
```

To execute the FastAPI tests:

```bash
python -m unittest tests.test_api
```

Running individual test modules is useful while developing or debugging a specific component.

To execute the Redis backend tests:

```bash
python -m unittest tests.test_redis_backend
```

Example successful output:

```text
........
----------------------------------------------------------------------
Ran 8 tests in XX.XXXs

OK
```

The Redis tests require a running Redis-compatible server.

---

## Running Tests Verbosely

For more detailed output, use verbose mode:

```bash
python -m unittest discover -v
```

Example:

```text
test_new_user_request_allowed ... ok
test_existing_user_reuses_bucket ... ok
test_invalid_capacity_raises_error ... ok

...

----------------------------------------------------------------------
Ran 23 tests in XX.XXXs

OK
```

Verbose mode displays the name and result of every individual test, making it easier to identify failures.

---

## When Should Tests Be Run?

The test suite should be executed:

- Before every Git commit.
- Before creating a new GitHub release.
- After adding a new feature.
- After refactoring existing code.
- Before opening a pull request.

Running tests frequently helps detect regressions early and keeps the project stable throughout development.

---

# Current Test Coverage

The automated test suite focuses on verifying the public behavior of the Python Rate Limiter rather than its internal implementation.

This approach ensures that the tests remain stable even if the internal implementation changes, provided the public API continues to behave correctly.

---

## RateLimiter Test Coverage

The `RateLimiter` class is tested for the following scenarios.

| Test Case | Purpose |
|-----------|---------|
| Constructor validation | Ensures invalid capacity and refill rate values raise exceptions. |
| New user requests | Verifies that a new user receives new rate-limit bucket state through the configured backend. |
| Existing user requests | Ensures an existing user's rate-limit state is reused by the configured backend. |
| Multi-user isolation | Confirms that each user maintains an independent bucket. |

---

## TokenBucket Test Coverage

The `TokenBucket` class is tested for the following scenarios.

| Test Case | Purpose |
|-----------|---------|
| Initial request | Verifies that the first request is accepted when tokens are available. |
| Token consumption | Ensures tokens are consumed correctly after each request. |
| Capacity exhaustion | Confirms requests are rejected after all available tokens have been consumed. |
| Automatic refill | Verifies that tokens are replenished after sufficient time has elapsed. |

---

## RedisBackend Test Coverage

The `RedisBackend` is tested for the following scenarios.

| Test Case | Purpose |
|-----------|---------|
| New user request | Verifies that a new Redis-backed bucket is created with the expected initial state. |
| Capacity exhaustion | Confirms requests are rejected after the available tokens have been consumed. |
| Token refill | Verifies that tokens are replenished after sufficient time has elapsed. |
| Independent users | Confirms that different users maintain independent Redis-backed bucket state. |
| Constructor validation | Ensures invalid capacity and refill rate values raise exceptions. |
| Concurrent requests | Verifies that concurrent requests are processed correctly through the Redis backend. |
| Bucket expiration | Confirms that inactive Redis bucket state expires through TTL. |

---

## Validation Testing

The project includes tests for invalid constructor parameters.

Examples include:

- Capacity less than or equal to zero.
- Refill rate less than or equal to zero.

These tests ensure that invalid configurations are detected immediately rather than allowing undefined behavior during execution.

---

## Testing Approach

The project primarily uses **behavior-focused unit testing**.

Instead of verifying private variables or internal implementation details, the tests validate observable behavior through the public interface.

Examples include:

- Whether a request is accepted.
- Whether a request is rejected.
- Whether a bucket is reused.
- Whether independent users remain isolated.

This approach makes the tests more resilient to internal refactoring while ensuring that the external behavior of the package remains correct.

---

## Current Limitations

The current automated test suite covers the core rate-limiting implementation, FastAPI integration, and Redis backend integration.

It does not yet include:
- Performance benchmarks.
- Load testing.
- Stress testing.
- Distributed deployment testing.
- Redis failure and recovery testing.

These areas will be introduced gradually as new project milestones are completed.

---

# Writing New Tests

As the project grows, every new feature should be accompanied by appropriate automated tests.

The goal is to ensure that new functionality does not introduce regressions or unintentionally break existing behavior.

---

## General Guidelines

When writing a new test:

- Test one behavior at a time.
- Use descriptive test names.
- Keep each test independent.
- Avoid relying on the execution order of other tests.
- Verify expected behavior through the public API.

Every test should answer a single question:

> **"Does this specific behavior work as expected?"**

---

## Test Naming

Test names should clearly describe the scenario being verified.

Examples:

```python
test_new_user_request_allowed()

test_existing_user_reuses_bucket()

test_request_allowed_after_refill()

test_invalid_capacity_raises_error()
```

A reader should understand the purpose of the test without opening its implementation.

---

## Test Setup and Independence

Each test should create or reset the state it depends on so that tests remain independent.
For tests that require a shared test fixture, `setUp()` can be used to create a fresh environment before each test.
For example:

```python
def setUp(self):
    self.limiter = RateLimiter(capacity=5, refill_rate=1)
```

By using isolated test state, the test suite remains reliable regardless of execution order.

---

## What Should Be Tested?

Whenever a new feature is added, consider testing:

- Valid input.
- Invalid input.
- Boundary conditions.
- Expected behavior.
- Error handling.
- Edge cases.

Thinking about these scenarios early helps produce more robust and maintainable code.

---

## Avoid Testing Private Implementation Details

Tests should focus on the **public behavior** of the package rather than internal implementation details.

For example, instead of checking private variables directly, verify the observable result of calling a public method.

This approach keeps the tests stable even if the internal implementation changes.

---

## Maintaining the Test Suite

As new versions are released:

- Add tests for every new public feature.
- Update existing tests when behavior intentionally changes.
- Remove obsolete tests only when the corresponding functionality is removed.

The test suite should evolve alongside the project and continue to reflect the current public behavior of the package.

---

# Future Testing Roadmap

Testing will continue to evolve alongside the project.

As new features are introduced, the test suite will expand to validate both functional correctness and overall system reliability.

The long-term objective is to build a comprehensive testing strategy that supports production-quality software development.

---

## v0.6.0 — FastAPI Integration

FastAPI integration was introduced as an HTTP layer around the rate-limiting package.
The API test suite was added to verify the behavior of this integration while keeping the existing unit tests for `RateLimiter` and `TokenBucket` independent from the API layer.

The current API tests cover:

- Root endpoint availability.
- Successful `/allow` requests.
- Rate-limit rejection with HTTP `429`.
- Request validation for missing `user` fields.
- Request validation for invalid `user` types.
- Independent rate-limiting behavior for different users.

The API tests use FastAPI's `TestClient` and override the limiter dependency so that each test can use a controlled `RateLimiter` instance.

The existing unit tests continue validating the core `RateLimiter` and `TokenBucket` behavior independently from the API layer.

---

## v0.7.0 — Redis Backend

Redis backend integration testing was introduced alongside the Redis backend.
The Redis test suite verifies:
- Redis bucket creation.
- Token state persistence.
- Token refill behavior.
- Independent user state.
- Constructor validation.
- Concurrent request handling.
- Bucket expiration through TTL.
The Redis tests ensure that the Redis-backed implementation preserves the expected rate-limiting behavior while using external state.

---

## v0.8.0 — Docker

Docker deployment was introduced in v0.8.0 to provide a containerized environment for the FastAPI application and Redis backend.
Docker verification covered:
- Docker image build verification.
- FastAPI container startup.
- Redis service startup through Docker Compose.
- Redis host and port environment configuration.
- FastAPI connectivity to the Redis backend.
- Redis-backed `/allow` request behavior.
- Rate-limit enforcement through the containerized application.
- Docker Compose service lifecycle using `up` and `down`.
The containerized deployment was verified by sending requests through the FastAPI container and confirming that the Redis-backed rate limiter enforced the configured limit, including successful requests followed by HTTP `429` after the available tokens were exhausted.
Docker environment verification is treated as deployment testing rather than as part of the 23-test Python `unittest` suite.

---

## v0.9.0 — Continuous Integration

Automated testing will become part of the development workflow through GitHub Actions.

Every push and pull request should automatically:

```
Developer Push
       │
       ▼
GitHub Actions
       │
       ▼
Install Dependencies
       │
       ▼
Run Unit Tests
       │
       ▼
Report Success / Failure
```

Continuous Integration helps detect regressions before changes are merged into the main branch.

---

## Future Testing Goals

As the project approaches **v1.0.0**, the testing strategy may expand to include:

- Performance benchmarking.
- Load testing.
- Stress testing.
- Expanded concurrency testing.
- Redis failure and recovery testing.
- Expanded API integration testing.
- Deployment and environment testing.

---

## Long-Term Vision

The testing strategy is intended to evolve alongside the architecture.

Every major feature should introduce corresponding automated tests so that the project remains reliable as its complexity increases.

The goal is not simply to increase the number of tests, but to ensure that every significant behavior can be verified automatically.

---

# Summary

Testing plays a fundamental role in the development of the **Python Rate Limiter** project.
Beginning with **v0.4.0**, automated tests became an integral part of the development process, ensuring that new features could be added with confidence while preserving the correctness of existing functionality.
Throughout this document, we explored:
- The testing philosophy adopted by the project.
- The organization of the test suite.
- How to execute automated tests.
- The current scope of test coverage.
- Guidelines for writing new tests.
- The long-term testing roadmap.
The project currently focuses on **behavior-focused testing**, validating the public behavior of the package while using targeted integration tests where external components such as FastAPI and Redis are involved.
At **v0.8.0**, the test suite contains **23 automated tests**, including:
- `TokenBucket` tests.
- `RateLimiter` tests.
- FastAPI integration tests.
- Redis backend integration tests.
The Redis backend tests additionally verify concurrency, token refill, independent users, and TTL-based bucket expiration.
As the project evolves, the testing strategy will expand alongside future architectural milestones, including Continuous Integration with GitHub Actions, performance testing, load testing, and additional failure and recovery scenarios.
The objective is not simply to increase the number of tests, but to ensure that every major feature is accompanied by reliable, repeatable, and automated verification.
A well-tested project is easier to maintain, easier to extend, and inspires greater confidence in both developers and users.
Ultimately, testing is not treated as a separate phase of development—it is considered an essential part of building reliable software from the beginning.
---