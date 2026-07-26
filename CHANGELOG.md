# Changelog

All notable changes to this project will be documented in this file.

This project follows Semantic Versioning.

---

## [v0.1.0] - July 2026

### Added

- Implemented the Token Bucket rate limiting algorithm.
- Added lazy token refill mechanism.
- Added constructor input validation.
- Added request allow/reject logic.
- Added manual testing examples.

### Limitations

- Single in-memory bucket.
- Not thread-safe.
- No Redis support.
- No API integration.
- No automated tests.