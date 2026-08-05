# Changelog

All notable changes to this project are documented in this file.

The project follows [Semantic Versioning](https://semver.org/) to manage releases.

---

## [v0.5.0] - 2026-08-06

### Added
- Reorganized the project into a reusable Python package.
- Introduced the `ratelimiter/` package containing the core implementation.
- Added `pyproject.toml` for modern Python packaging.
- Added support for local installation using `pip install .` and `pip install -e .`.
- Added a dedicated `docs/` directory for project documentation.
- Added `ARCHITECTURE.md`.
- Added `TOKEN_BUCKET.md`.
- Added `DESIGN_DECISIONS.md`.
- Added `TESTING.md`.

### Changed
- Refactored the project from a single-file implementation into a modular package structure.
- Improved separation between implementation, tests, and documentation.
- Updated imports to support package-based usage.
- Improved repository organization following standard Python packaging practices.

### Documentation
- Updated `README.md` for the new package structure.
- Updated installation instructions.
- Added documentation index through the `docs/` directory.
- Updated project roadmap.
- Updated version history.
- Expanded project documentation with architecture, algorithm, design decisions, and testing guides.

### Known Limitations
- In-memory storage only.
- No automatic cleanup of inactive buckets.
- No FastAPI integration.
- No Redis backend.
- Package not yet published to PyPI.
- No Docker support.
- No CI/CD pipeline.
- No distributed deployment.

---

## [v0.4.0] - 2026-08-05

### Added
- Added automated unit tests using Python's built-in `unittest` framework.
- Added a dedicated test suite for the `RateLimiter` class.
- Added a dedicated test suite for the `TokenBucket` class.
- Added validation tests for invalid constructor parameters.
- Added functional tests for request allowance and rejection.
- Added multi-user behavior verification.
- Added token refill verification tests.

### Changed
- Replaced manual testing with automated unit tests.
- Improved project reliability and maintainability.
- Established a testing foundation for future development.
- Updated project documentation to reflect the new testing strategy.

### Documentation
- Updated `README.md` for v0.4.0.
- Updated project roadmap.
- Updated version history.
- Added instructions for running the automated test suite.

### Known Limitations
- In-memory storage only.
- No automatic cleanup of inactive buckets.
- No package structure yet.
- No FastAPI integration.
- No Redis backend.
- No Docker support.
- No CI/CD pipeline.
- No distributed deployment.

---

## [v0.3.0] - 2026-08-02

### Added
- Added thread-safe bucket creation using `threading.Lock`.
- Added thread-safe token consumption.
- Added thread-safe token refill operations.
- Added independent locking for each `TokenBucket`.
- Added synchronization for shared bucket management inside the `RateLimiter`.

### Changed
- Improved concurrency support while preserving the existing public API.
- Protected shared resources from race conditions.
- Refined the internal architecture for safe multi-threaded execution.

### Documentation
- Updated the README to reflect thread-safe functionality.
- Updated the project roadmap and version history.

### Known Limitations
- In-memory storage only.
- No automatic cleanup of inactive buckets.
- No Redis or external storage.
- No REST API integration.
- No Docker support.
- No automated unit tests.
- No CI/CD pipeline.
- No distributed deployment.

---

## [v0.2.0] - 2026-07-28

### Added
- Introduced the `RateLimiter` class as the primary interface for processing requests.
- Added support for independent token buckets for multiple users.
- Implemented lazy bucket creation using the `_get_or_create_bucket()` method.
- Added in-memory bucket management using a Python dictionary.
- Improved object-oriented architecture by separating request routing from token bucket logic.

### Changed
- Requests are now handled through the `RateLimiter` instead of interacting directly with the `TokenBucket`.
- Enhanced code organization and separation of responsibilities.

### Documentation
- Added a comprehensive `README.md`.
- Added the MIT `LICENSE`.
- Improved project documentation for GitHub.

### Known Limitations
- Not thread-safe.
- In-memory storage only.
- No automatic cleanup of inactive buckets.
- No Redis or distributed storage.
- No REST API integration.
- No automated unit tests.

---

## [v0.1.0] - 2026-07-27

### Added
- Initial implementation of the Token Bucket rate limiting algorithm.
- Configurable bucket capacity.
- Configurable token refill rate.
- Automatic lazy token refill based on elapsed time.
- Request allow/reject mechanism.
- Input validation for invalid capacity and refill rate.
- Manual testing examples.

### Known Limitations
- Supported only a single token bucket.
- No multi-user support.
- No thread safety.
- No persistence.
- No distributed architecture.

---
