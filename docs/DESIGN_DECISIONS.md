# Design Decisions

This document explains the major engineering decisions made while developing the **Python Rate Limiter** project.

Unlike the architecture document, which explains **how the project is organized**, or the Token Bucket document, which explains **how the algorithm works**, this document answers a different question:

> **Why was the project designed this way?**

Every software project involves trade-offs. There are usually multiple valid solutions to the same problem.

The decisions documented here were made after considering simplicity, maintainability, scalability, learning objectives, and future extensibility.

Current Version: **v0.6.0**

---

# Design Philosophy

The project follows a simple philosophy:

> **Build one engineering concept at a time, understand it thoroughly, and evolve the project incrementally.**

Instead of implementing every feature in a single release, each version introduces one significant software engineering milestone.

This incremental approach provides several benefits:

- Easier debugging
- Better understanding of each concept
- Cleaner Git history
- Well-defined release milestones
- Stable public API
- Improved maintainability

The project is intentionally designed to evolve through multiple versions while keeping the core Token Bucket algorithm stable.

Every design decision documented below supports that long-term goal.

---

# Decision 1 — Algorithm Selection

## Problem

The project required a rate-limiting algorithm that was simple to understand, efficient to implement, and suitable for demonstrating real-world backend engineering concepts.

The chosen algorithm also needed to support future enhancements such as thread safety, FastAPI integration, Redis-backed storage, and distributed deployments.

---

## Alternatives Considered

Several rate-limiting algorithms were considered.

### Fixed Window Counter

**Advantages**

- Very simple implementation.
- Low memory usage.

**Disadvantages**

- Suffers from boundary problems.
- Allows sudden spikes at the start of a new time window.

---

### Sliding Window

**Advantages**

- Provides smoother request distribution.
- Reduces sudden traffic spikes.

**Disadvantages**

- More complex implementation.
- Requires maintaining additional request history or timestamps.

---

### Leaky Bucket

**Advantages**

- Produces a constant request rate.
- Smooths outgoing traffic.

**Disadvantages**

- Does not allow temporary traffic bursts.
- Less suitable for APIs where occasional bursts are acceptable.

---

## Decision

The project uses the **Token Bucket algorithm**.

---

## Why This Decision?

The Token Bucket algorithm was selected because it provides a good balance between simplicity, flexibility, and performance.

Key reasons include:

- Supports configurable burst traffic.
- Controls the long-term request rate through token replenishment.
- Constant-time request processing.
- Minimal memory overhead.
- Easy to explain during interviews.
- Commonly used in networking and backend systems.
- Naturally supports future project milestones.

---

## Trade-offs

The algorithm requires refill calculations whenever requests are processed.

Although this introduces a small amount of additional computation, the overhead remains constant for every request and is negligible compared to the flexibility gained.

---

## Future Evolution

The core Token Bucket algorithm is expected to remain unchanged throughout future releases.

Upcoming versions may change how bucket state is stored (for example, Redis), but the algorithm itself will continue to be the foundation of the project.

---

# Decision 2 — Lazy Token Refill

## Problem

The Token Bucket algorithm requires tokens to be replenished over time.

The project needed a refill mechanism that was efficient, simple to maintain, and scalable as the number of users increased.

---

## Alternatives Considered

### Background Timer

A dedicated background thread periodically refills every bucket.

**Advantages**

- Bucket state is always up to date.
- Simple conceptual model.

**Disadvantages**

- Requires continuous CPU activity.
- Difficult to manage as the number of users grows.
- Introduces synchronization complexity.
- Performs unnecessary work for inactive users.

---

### Scheduled Tasks

A scheduler periodically scans all buckets and refills them.

**Advantages**

- Centralized refill logic.
- Predictable execution intervals.

**Disadvantages**

- Requires iterating over all buckets.
- Inefficient when most users are inactive.
- Additional scheduling infrastructure is required.

---

## Decision

The project uses a **lazy refill strategy**.

Tokens are replenished only when a request is received.

---

## Why This Decision?

Lazy refill offers several practical advantages:

- No background threads are required.
- No scheduler is needed.
- CPU time is consumed only when requests arrive.
- Inactive users consume virtually no processing resources.
- The implementation remains simple and easy to understand.
- Constant-time request processing is preserved.

This approach provides an excellent balance between efficiency and implementation simplicity.

---

## Trade-offs

The bucket is updated only when it is accessed.

The bucket's stored token count is updated only when the bucket is accessed. While an inactive bucket is not being accessed, its stored value is not proactively updated to reflect elapsed time.

When the next request arrives, the elapsed time is calculated and the bucket is brought up to date before the request is evaluated.

This behavior is intentional and avoids unnecessary background work.

This behavior is intentional and does not affect the correctness of the algorithm.

---

## Future Evolution

The lazy refill strategy will continue to be used as the project evolves through:

- Redis-backed storage
- Distributed deployments
- Docker deployment
- CI/CD automation

The storage and deployment mechanisms may change, but the refill strategy itself is expected to remain unchanged.

---

# Decision 3 — One Bucket Per User

## Problem

The project needed a strategy for managing requests from multiple users while ensuring that each user's request rate remained independent.

A shared bucket would cause all users to compete for the same pool of tokens, leading to unfair request handling.

---

## Alternatives Considered

### Single Shared Bucket

All users share one common Token Bucket.

**Advantages**

- Very simple implementation.
- Minimal memory usage.

**Disadvantages**

- Unfair request distribution.
- Heavy users can exhaust tokens for everyone.
- Cannot enforce user-specific rate limits.

---

### Group-Based Buckets

Users are grouped together, and each group shares one bucket.

**Advantages**

- Useful for organization-wide rate limiting.
- Reduces memory usage compared to one bucket per user.

**Disadvantages**

- More complex bucket management.
- Still allows users within the same group to affect one another.

---

## Decision

The project assigns **one independent `TokenBucket` to each user**.

The `RateLimiter` is responsible for creating and managing these buckets.

---

## Why This Decision?

Using one bucket per user provides several important benefits:

- Independent rate limits for every user.
- Fair resource allocation.
- Simple request routing.
- Easy to understand and maintain.
- Naturally supports future storage backends such as Redis.
- Scales well as new users are added.

Each user's activity affects only their own bucket, ensuring predictable behavior across the system.

---

## Trade-offs

Maintaining a separate bucket for every user with stored state increases memory usage as the number of users grows.

However, each bucket stores only a small amount of state, making this trade-off acceptable for the current implementation.

Future releases may introduce automatic cleanup of inactive buckets to optimize memory usage.

---

## Future Evolution

The one-bucket-per-user model will remain unchanged in future releases.

Only the storage mechanism is expected to evolve:

- v0.7.0 — Redis-backed bucket storage.
- Future distributed deployments with shared state.

The logical relationship between a user and their bucket will remain the same.

---

# Decision 4 — Dictionary-Based Bucket Storage

## Problem

The `RateLimiter` must quickly locate the correct `TokenBucket` for every incoming request.

As the number of users increases, searching for a user's bucket should remain efficient without significantly increasing request processing time.

---

## Alternatives Considered

### List

Store every user's bucket inside a list.

**Advantages**

- Very simple implementation.
- Easy to understand.

**Disadvantages**

- Requires a linear search to locate a user's bucket.
- Performance degrades as the number of users grows.
- Unsuitable for applications with many active users.

---

### Database

Store bucket information inside a database.

**Advantages**

- Persistent storage.
- Suitable for distributed systems.
- Survives application restarts.

**Disadvantages**

- Requires additional infrastructure.
- Introduces network latency.
- Unnecessarily complex for the current learning objectives.

---

## Decision

The project stores user buckets inside a Python **dictionary**.

Each entry maps a unique user identifier to its corresponding `TokenBucket`.

Conceptually:

```text
{
    "Alice" : TokenBucket,
    "Bob"   : TokenBucket,
    "Charlie": TokenBucket
}
```

---

## Why This Decision?

Python dictionaries provide average **O(1)** lookup and insertion.

This makes them well suited for request routing, where every incoming request must quickly locate the appropriate bucket.

Additional benefits include:

- Fast bucket lookup.
- Fast bucket creation.
- Simple implementation.
- Clean integration with the `RateLimiter`.
- Easy replacement with another storage backend in future versions.

---

## Trade-offs

Dictionary storage exists only in memory.

As a result:

- Bucket data is lost when the application restarts.
- State cannot be shared between multiple application instances.
- Memory usage increases with the number of users with stored buckets.

These limitations are acceptable for the current implementation because the primary goal is to build and understand the core rate-limiting logic.

---

## Future Evolution

Beginning with **v0.7.0**, the dictionary implementation is planned to be replaced by Redis-backed storage.

The public API of the `RateLimiter` will remain unchanged, while only the underlying storage mechanism evolves.

This separation between interface and storage makes the architecture easier to extend without affecting users of the package.

---

# Decision 5 — Fine-Grained Locking

## Problem

Beginning with **v0.3.0**, the project needed to support concurrent request processing.

Without synchronization, multiple threads accessing shared resources simultaneously could produce race conditions, resulting in inconsistent bucket states or duplicate bucket creation.

The challenge was to provide thread safety without unnecessarily reducing concurrency.

---

## Alternatives Considered

### No Locking

Allow every thread to access shared data without synchronization.

**Advantages**

- Maximum performance.
- Simplest implementation.

**Disadvantages**

- Race conditions.
- Data corruption.
- Duplicate bucket creation.
- Unpredictable behavior.

---

### Global Lock

Protect the entire application using one shared lock.

**Advantages**

- Very easy to implement.
- Strong thread safety.

**Disadvantages**

- Only one request can be processed at a time.
- Poor scalability.
- High lock contention.

---

## Decision

The project uses **fine-grained locking**.

Two independent locking mechanisms are employed:

- One lock inside the `RateLimiter`.
- One lock inside every `TokenBucket`.

Each lock protects only the data owned by its respective component.

---

## Why This Decision?

Fine-grained locking provides a balance between correctness and performance.

Benefits include:

- Prevents race conditions.
- Allows requests for different users to execute concurrently.
- Reduces unnecessary blocking.
- Keeps synchronization localized to individual components.
- Supports future scalability.

By limiting the scope of each lock, the project maintains thread safety without serializing every request.

---

## Trade-offs

Compared to a single global lock, fine-grained locking introduces additional implementation complexity.

Multiple locks require careful ownership and consistent synchronization to avoid programming mistakes.

However, the improved concurrency and modularity outweigh the added complexity for this project.

---

## Future Evolution

The current locking strategy protects shared state within a single Python process.

Future releases that introduce Redis-backed storage or distributed deployments will move synchronization beyond in-memory locks.

Even then, the principle of protecting only the necessary shared resources will remain unchanged.

---

# Decision 6 — Python Package Structure

## Problem

In the initial versions of the project, the entire implementation was contained in a single Python file.

While this approach worked for learning the Token Bucket algorithm, it became increasingly difficult to maintain as new features such as multi-user support, thread safety, and automated testing were introduced.

The project required a structure that would improve maintainability, reusability, and scalability.

---

## Alternatives Considered

### Single Python File

Keep all implementation inside one file.

**Advantages**

- Very easy to start.
- Suitable for small projects.
- Minimal project structure.

**Disadvantages**

- Difficult to maintain as the project grows.
- Responsibilities become mixed together.
- Harder to reuse as a library.
- Not aligned with common Python package practices.

---

### Modular Python Package

Separate the implementation into multiple modules inside a package.

**Advantages**

- Better organization.
- Easier maintenance.
- Improved code reuse.
- Clear separation of responsibilities.
- Standard Python project structure.

**Disadvantages**

- Slightly more initial setup.
- Requires understanding package imports and project organization.

---

## Decision

Beginning with **v0.5.0**, the project was reorganized into a reusable Python package named `ratelimiter`.

The implementation was split into focused modules:

- `rate_limiter.py`
- `token_bucket.py`
- `__init__.py`

Automated tests and documentation were also moved into their own dedicated directories.

---

## Why This Decision?

Packaging the project provides several long-term benefits:

- Clear separation of concerns.
- Easier navigation of the codebase.
- Simpler testing and maintenance.
- Reusable library interface.
- Standard Python project layout.
- Better preparation for future publishing and distribution.

This structure made the FastAPI integration in v0.6.0 easier to implement and provides a foundation for future integrations such as Redis.

---

## Trade-offs

Compared to a single-file implementation, a packaged project introduces additional files and configuration.

Developers must understand Python packages, imports, and project structure.

However, these trade-offs are worthwhile because they significantly improve maintainability and scalability.

---

## Future Evolution

Future releases will continue building on this package structure.

New modules may be added for:

- Redis storage
- Docker support
- Utility functions
- Configuration management

The package layout introduced in **v0.5.0** is expected to remain the foundation of the project through **v1.0.0**.

---

# Decision 7 — Automated Testing with `unittest`

## Problem

As the project evolved, manual testing became increasingly difficult and unreliable.

Every new feature introduced the risk of unintentionally breaking existing functionality.

The project required an automated testing solution that was simple to adopt, easy to understand, and well integrated with Python.

---

## Alternatives Considered

### Manual Testing

Run the application and verify behavior by observing console output.

**Advantages**

- Easy to begin.
- No additional code required.

**Disadvantages**

- Time-consuming.
- Difficult to repeat consistently.
- High risk of missing regressions.
- Not suitable for long-term maintenance.

---

### Third-Party Testing Frameworks

Use external frameworks such as `pytest`.

**Advantages**

- Rich ecosystem.
- Powerful features.
- Concise test syntax.

**Disadvantages**

- Additional dependency.
- More concepts to learn initially.
- Beyond the learning objectives of this project at this stage.

---

## Decision

The project uses Python's built-in **`unittest`** framework for automated testing.

Dedicated test modules validate both the `RateLimiter` and `TokenBucket` classes.

---

## Why This Decision?

`unittest` was selected because it provides a solid foundation for learning automated testing while remaining part of Python's standard library.

Key benefits include:

- No external dependencies.
- Easy setup and execution.
- Structured test organization.
- Reliable regression testing.
- Industry-recognized testing framework.
- Seamless integration with future CI/CD pipelines.

The focus of the original testing milestone was understanding testing principles rather than exploring advanced testing frameworks.

---

## Trade-offs

Compared to frameworks such as `pytest`, `unittest` requires more boilerplate code and offers fewer convenience features.

However, its simplicity and standard-library availability make it an excellent choice for establishing a strong testing foundation.

Future migration to another framework remains possible without changing the production code.

---

## Future Evolution

Future releases may expand the testing strategy with:

- Performance testing
- Integration testing
- API testing
- Load testing
- Redis backend testing
- CI/CD automation using GitHub Actions

Regardless of the framework used, automated testing will remain a fundamental part of the project's development workflow.

---

# Decision 8 — FastAPI Integration

## Problem

The rate limiter initially existed only as a Python library that could be called directly from application code.

While this demonstrated the core algorithm and backend component design, the project also needed to demonstrate how the rate limiter could operate as part of an HTTP-based backend service.

The integration needed to expose the existing rate-limiting functionality without moving the core algorithm into the web framework.

---

## Alternatives Considered

### Direct Framework-Specific Implementation

Implement the rate-limiting logic directly inside FastAPI route handlers.

**Advantages**

- Simple initial implementation.
- Minimal number of files.

**Disadvantages**

- Couples rate-limiting logic to the web framework.
- Makes the core component harder to reuse.
- Mixes business logic with HTTP handling.
- Makes future framework changes more difficult.

---

### FastAPI as an Integration Layer

Keep the existing `RateLimiter` as the core component and use FastAPI only to expose it through HTTP endpoints.

**Advantages**

- Preserves separation of concerns.
- Keeps the core rate-limiting logic framework-independent.
- Allows the same `RateLimiter` to be used outside FastAPI.
- Provides a clear boundary between HTTP handling and rate-limiting logic.
- Builds directly on the package structure introduced in v0.5.0.

**Disadvantages**

- Introduces an additional web framework dependency.
- Requires API-specific request and response handling.
- Adds another layer to the application.

---

## Decision

The project uses **FastAPI as an integration layer** rather than embedding the rate-limiting algorithm directly into API route handlers.

The existing `RateLimiter` remains responsible for rate-limiting behavior, while FastAPI handles HTTP request processing and exposes the functionality through API endpoints.

This keeps the core algorithm independent from the web framework.

---

## Why This Decision?

The primary reason for this approach is separation of concerns.

The responsibilities remain clearly divided:

- `TokenBucket` manages token calculation and request allowance.
- `RateLimiter` manages users and their buckets.
- FastAPI handles HTTP requests and responses.

This allows the v0.6.0 integration to add HTTP functionality without redesigning the underlying rate-limiting component.

It also creates a cleaner foundation for future infrastructure changes such as Redis-backed storage and distributed deployment.

---

## Trade-offs

Introducing FastAPI adds an external dependency and increases the overall project surface area.

The application also requires HTTP-specific request and response handling that was not necessary when the rate limiter was used directly as a Python library.

However, these costs are acceptable because the integration demonstrates how the reusable package can be incorporated into a real backend service without coupling the core algorithm to the framework.

---

## Future Evolution

The FastAPI integration is intended to remain an integration layer rather than becoming part of the core rate-limiting algorithm.

Future releases can replace or extend the underlying storage mechanism without requiring the API layer to contain rate-limiting implementation details.

In **v0.7.0**, Redis-backed storage is planned as the next major infrastructure evolution while preserving the existing separation between the API layer, rate limiter, and storage mechanism.

---

# Summary

Every engineering decision made throughout this project was guided by a common objective:

> **Build a maintainable, extensible, and educational rate limiter while understanding the reasoning behind every implementation choice.**

Rather than selecting technologies based solely on popularity, each decision was made by considering:

- Simplicity
- Maintainability
- Performance
- Scalability
- Learning objectives
- Future extensibility

The project intentionally evolves through incremental milestones.

Each release introduces one major engineering concept while preserving the existing architecture and public API whenever possible.

The key design decisions documented in this file include:

- Choosing the Token Bucket algorithm.
- Using lazy token refill.
- Maintaining one bucket per user.
- Using dictionary-based storage.
- Applying fine-grained locking.
- Organizing the project as a reusable Python package.
- Introducing automated testing with Python's built-in `unittest` framework.
- Using FastAPI as an integration layer for HTTP access.

With FastAPI now integrated in **v0.6.0**, future releases will document the design reasoning behind Redis, Docker, CI/CD, and other significant engineering changes.

The goal is not only to build a working rate limiter but also to document the engineering thought process that transformed a simple algorithm into a production-oriented software project.

---