# Changelog

All notable changes to this project are documented in this file.

The project follows [Semantic Versioning](https://semver.org/) to manage releases.

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

## Upcoming Releases

### v0.3.0 (Planned)
- Thread-safe implementation using synchronization primitives.
- Support for concurrent request processing.
- Concurrency testing.

### v0.4.0 (Planned)
- Redis-backed bucket storage.
- Shared rate limiting across multiple application instances.

### v0.5.0 (Planned)
- Distributed rate limiting architecture.
- Improved scalability and fault tolerance.

### v1.0.0 (Goal)
- Production-ready implementation.
- Modular package structure.
- Comprehensive automated test suite.
- Performance benchmarking.
- Complete project documentation.