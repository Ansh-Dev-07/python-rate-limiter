# Testing Guide

This document describes the testing strategy used in the **Python Rate Limiter** project.

Testing is an essential part of software engineering. As the project evolves through multiple releases, automated tests help ensure that new features do not break existing functionality.

Unlike the README, which introduces the project, or the architecture and design documents, this guide focuses entirely on verifying correctness and maintaining software quality.

Current Testing Version: **v0.6.0**

---

# Testing Philosophy

The testing strategy for this project is based on one simple principle:

> **Every feature should be verifiable through automated tests.**

Instead of relying on manual execution and visual inspection, the project uses repeatable unit tests to validate the behavior of the core components.

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
│   └── token_bucket.py
│
└── tests/
    ├── __init__.py
    ├── test_rate_limiter.py
    ├── test_token_bucket.py
    └── test_api.py
```

Separating tests from the implementation improves maintainability and makes the project easier to understand as it grows.

---

## Test Responsibilities

Each test module focuses on a specific component of the project.

| Test File | Purpose |
|-----------|---------|
| `test_rate_limiter.py` | Verifies the behavior of the `RateLimiter` class, including bucket creation, multi-user handling, and constructor validation. |
| `test_token_bucket.py` | Verifies the Token Bucket algorithm, including token consumption, request rejection, and automatic token refill. |
| `test_api.py` | Verifies the FastAPI integration, including the root endpoint, successful requests, rate-limit rejection (`429`), request validation (`422`), and independent buckets for different users. |

This separation follows the same design philosophy as the production code—each file has a single responsibility.

---

## Current Testing Scope

At **v0.6.0**, the automated test suite validates:

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

The tests focus on validating observable behavior rather than internal implementation details.

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
python -m unittest discover tests
```

Example output:

```text
..................
----------------------------------------------------------------------
Ran XX tests in X.XXXs

OK
```

A successful execution confirms that all implemented features behave as expected.

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

---

## Running Tests Verbosely

For more detailed output, use verbose mode:

```bash
python -m unittest discover tests -v
```

Example:

```text
test_new_user_request_allowed ... ok
test_existing_user_reuses_bucket ... ok
test_invalid_capacity_raises_error ... ok

...

----------------------------------------------------------------------
Ran XX tests

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
| New user requests | Verifies that a new user receives a fresh `TokenBucket`. |
| Existing user requests | Ensures an existing user's bucket is reused instead of creating a new one. |
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

The current automated test suite covers the core rate-limiting implementation and the FastAPI integration.

It does not yet include:

- Performance benchmarks.
- Load testing.
- Stress testing.
- Redis backend testing.
- Docker environment testing.
- Distributed deployment testing.

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

## Test Independence

Each test should create its own environment using the `setUp()` method.

This prevents one test from affecting another and ensures consistent, repeatable results.

Example:

```python
def setUp(self):
    self.limiter = RateLimiter(capacity=5, refill_rate=1)
```

By creating a fresh instance before every test, the test suite remains reliable regardless of execution order.

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

FastAPI integration was introduced as an HTTP layer around the existing rate-limiting package.

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

Introducing Redis changes the storage layer of the application.

Additional tests will verify:

- Redis bucket creation.
- Token persistence.
- Shared bucket state.
- Redis connection handling.
- Failure recovery scenarios.

These tests will ensure that replacing in-memory storage does not change the public behavior of the package.

---

## v0.8.0 — Docker

Containerization introduces another deployment environment.

Testing goals include:

- Container startup verification.
- Dependency validation.
- Environment configuration testing.
- Consistent behavior across different systems.

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

- Integration testing.
- Performance benchmarking.
- Load testing.
- Stress testing.
- Concurrency testing.
- Expanded API integration testing.

These additional testing layers will complement the existing unit tests and provide greater confidence in the project's reliability.

---

## Long-Term Vision

The testing strategy is intended to evolve alongside the architecture.

Every major feature should introduce corresponding automated tests so that the project remains reliable as its complexity increases.

The goal is not simply to increase the number of tests, but to ensure that every significant behavior can be verified automatically.

---

# Summary

Testing plays a fundamental role in the development of the **Python Rate Limiter** project.

Beginning with **v0.4.0**, automated unit tests became an integral part of the development process, ensuring that new features could be added with confidence while preserving the correctness of existing functionality.

Throughout this document, we explored:

- The testing philosophy adopted by the project.
- The organization of the test suite.
- How to execute automated tests.
- The current scope of test coverage.
- Guidelines for writing new tests.
- The long-term testing roadmap.

The project currently focuses on **behavior-focused unit testing**, validating the public interface of the package rather than its internal implementation details.

This approach keeps the tests maintainable and resilient to future refactoring.

As the project evolves, the testing strategy will expand alongside new architectural milestones. The current v0.6.0 release has already introduced FastAPI integration testing, while future milestones will add:

- Redis backend testing.
- Docker environment validation.
- Continuous Integration with GitHub Actions.
- Performance and load testing.

The objective is not simply to increase the number of tests, but to ensure that every major feature is accompanied by reliable, repeatable, and automated verification.

A well-tested project is easier to maintain, easier to extend, and inspires greater confidence in both developers and users.

Ultimately, testing is not treated as a separate phase of development—it is considered an essential part of building reliable software from the very beginning.

---