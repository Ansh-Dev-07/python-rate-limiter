# Design Decisions

This document explains the major engineering decisions made while developing the **Python Rate Limiter** project.

Unlike the architecture document, which explains **how the project is organized**, or the Token Bucket document, which explains **how the algorithm works**, this document answers a different question:

> **Why was the project designed this way?**

Every software project involves trade-offs. There are usually multiple valid solutions to the same problem.

The decisions documented here were made after considering simplicity, maintainability, scalability, learning objectives, and future extensibility.

Current Version: **v0.8.0**

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

The project may introduce additional storage and infrastructure mechanisms, but the underlying rate-limiting algorithm will continue to use the Token Bucket model.

This separation allows implementation details such as storage and deployment to evolve without changing the fundamental rate-limiting behavior.

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

The bucket's stored token count is updated only when the bucket is accessed.

While an inactive bucket is not being accessed, its stored value is not proactively updated to reflect elapsed time.

When the next request arrives, the elapsed time is calculated and the bucket is brought up to date before the request is evaluated.

This behavior is intentional and avoids unnecessary background work without affecting the correctness of the algorithm.

---

## Future Evolution

The lazy refill strategy continues to be used across the project's current backends.

For the in-memory implementation, refill calculations are performed when a bucket is accessed.

For the Redis implementation, the same lazy refill principle is performed atomically inside the Redis Lua script.

The refill strategy is expected to remain unchanged as the project evolves through Docker deployment, CI/CD automation, and future infrastructure improvements.

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

The project maintains one independent rate-limit bucket state for each user.
For `InMemoryBackend`, this state is represented by a `TokenBucket` object.
For `RedisBackend`, the bucket state is stored in Redis.

---

## Why This Decision?

Using one bucket per user provides several important benefits:

- Independent rate limits for every user.
- Fair resource allocation.
- Simple request routing.
- Easy to understand and maintain.
- Consistent logical behavior across different storage backends.
- Natural support for shared storage such as Redis.

Each user's activity affects only their own bucket, ensuring predictable behavior across the system.

The logical relationship remains the same regardless of where the bucket state is stored.

---

## Trade-offs

Maintaining separate bucket state for every user increases the amount of stored state as the number of users grows.
For the in-memory backend, this increases application memory usage because each active user's `TokenBucket` is stored in the Python process.
For the Redis backend, bucket state is stored externally and can expire automatically through Redis TTL.
These trade-offs are acceptable because per-user isolation is an important requirement of the rate limiter.

---

## Future Evolution

The one-bucket-per-user model remains part of the project's current design.
The storage mechanism can evolve independently:
- `InMemoryBackend` stores each user's `TokenBucket` in memory.
- `RedisBackend` stores each user's bucket state in Redis.
- Future backends may provide additional storage or deployment capabilities.
The logical relationship between a user and their rate-limit state remains unchanged.

---

# Decision 4 — Dictionary-Based Bucket Storage

## Problem

The in-memory backend must quickly locate the correct `TokenBucket` for every incoming request.

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

The `InMemoryBackend` stores user buckets inside a Python **dictionary**.

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

This makes them well suited for the in-memory backend, where every incoming request must quickly locate the appropriate user's bucket.

Additional benefits include:

- Fast bucket lookup.
- Fast bucket creation.
- Simple implementation.
- Clean integration with `InMemoryBackend`.
- Easy reasoning about the in-memory storage model.

Because dictionary storage is isolated inside `InMemoryBackend`, other backends can use different storage mechanisms without changing the public `RateLimiter` interface.

---

## Trade-offs

Dictionary storage exists only in application memory.
As a result:
- Bucket data is lost when the application restarts.
- State is not shared between separate application instances using the in-memory backend.
- Memory usage increases as more user buckets are stored.
- Inactive buckets remain in memory unless explicitly removed.
These limitations are specific to the in-memory backend.
The Redis backend addresses the external-storage requirement by storing bucket state in Redis and applying a TTL to user bucket keys.

---

## Future Evolution

The dictionary remains the storage mechanism for `InMemoryBackend`.
For applications that require externally shared state, `RedisBackend` provides an alternative storage implementation.
The backend abstraction allows additional storage mechanisms to be introduced without changing the public `RateLimiter` interface.

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

The project uses **fine-grained locking** for the in-memory implementation.

Two independent locking mechanisms are employed:

- One lock inside `InMemoryBackend` to protect the shared user-to-bucket dictionary.
- One lock inside every `TokenBucket` to protect that bucket's mutable token state.

Each lock protects only the data owned by its respective component.

---

## Why This Decision?

Fine-grained locking provides a balance between correctness and concurrency.

Benefits include:

- Prevents race conditions.
- Protects concurrent bucket creation.
- Protects individual `TokenBucket` state.
- Allows requests for different users to process concurrently.
- Reduces unnecessary blocking.
- Keeps synchronization localized to the component that owns the shared state.

By limiting the scope of each lock, the in-memory implementation maintains thread safety without serializing all token-bucket operations behind a single global lock.

---

## Trade-offs

Compared to a single global lock, fine-grained locking introduces additional implementation complexity.
Multiple locks require careful ownership and consistent synchronization to avoid programming mistakes.
However, the improved concurrency and modularity outweigh the added complexity for this project.

---

## Future Evolution

The current locking strategy protects shared in-memory state within a single Python process.
The Redis backend uses a different concurrency model: refill, request decision, state update, and TTL refresh are performed atomically inside a Redis Lua script.
This allows synchronization of Redis-backed state to occur at the Redis execution layer rather than through Python in-memory locks.
Future distributed deployments may build further on this external-state approach.

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

Beginning with **v0.5.0**, the project was reorganized into a reusable Python package named `RateLimiter`.

The implementation was split into focused modules:

- `rate_limiter.py`
- `token_bucket.py`
- `backends/base.py`
- `backends/in_memory.py`
- `backends/redis_backend.py`
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

This structure made the FastAPI integration in v0.6.0 easier to maintain and allowed the backend abstraction and Redis implementation to be introduced in v0.7.0 without redesigning the public `RateLimiter` interface.
The package structure now separates the public rate-limiting interface, algorithm implementation, and backend-specific storage behavior.

---

## Trade-offs

Compared to a single-file implementation, a packaged project introduces additional files and configuration.
Developers must understand Python packages, imports, and project structure.
However, these trade-offs are worthwhile because they significantly improve maintainability and scalability.

---

## Future Evolution

Future releases will continue building on this package structure.
Additional modules may be introduced for:
- Additional storage backends.
- Configuration management.
- Infrastructure integrations.
- Other supporting functionality.
The package layout introduced in **v0.5.0** and extended with the backend architecture in **v0.7.0** is expected to remain the foundation of the project through **v1.0.0**.

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
As the project evolved, the same `unittest` foundation was extended to cover FastAPI behavior and Redis backend integration.

---

## Trade-offs

Compared to frameworks such as `pytest`, `unittest` requires more boilerplate code and offers fewer convenience features.
However, its simplicity and standard-library availability make it an excellent choice for establishing a strong testing foundation.
Future migration to another framework remains possible without changing the production code.

---

## Future Evolution

Future releases may expand the testing strategy with:
- Performance testing.
- Load testing.
- Additional integration testing.
- Failure and recovery testing.
- CI/CD automation using GitHub Actions.
The current test suite already includes:
- `TokenBucket` unit tests.
- `RateLimiter` tests.
- FastAPI tests.
- Redis backend integration tests.
Automated testing will remain a fundamental part of the project's development workflow.

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
- `TokenBucket` manages in-memory token state, refill calculation, and request allowance.
- `InMemoryBackend` manages in-memory user-to-bucket state.
- `RedisBackend` manages Redis-backed bucket processing.
- `RateLimiter` provides the public interface and delegates requests to the configured backend.
- FastAPI handles HTTP requests, validation, and responses.
This allows infrastructure and storage implementations to evolve without moving rate-limiting logic into the web framework.

---

## Trade-offs

Introducing FastAPI adds an external dependency and increases the overall project surface area.
The application also requires HTTP-specific request and response handling that was not necessary when the rate limiter was used directly as a Python library.
However, these costs are acceptable because the integration demonstrates how the reusable package can be incorporated into a real backend service without coupling the core algorithm to the framework.

---

## Future Evolution

The FastAPI integration is intended to remain an integration layer rather than becoming part of the core rate-limiting implementation.
Future releases can extend or replace the underlying backend and infrastructure without requiring the API layer to contain storage-specific rate-limiting behavior.
The v0.7.0 Redis backend demonstrates this separation by adding Redis-backed state without requiring Redis-specific logic inside the FastAPI layer.

---
# Decision 9 — Backend Abstraction and Redis Backend

## Problem

As the project evolved beyond a single-process in-memory implementation, storing rate-limit state directly inside the core `RateLimiter` became increasingly restrictive.
An in-memory dictionary is simple and fast, but its state is limited to a single application process.
The project needed a design that could support alternative storage mechanisms without changing the public `RateLimiter` interface.

---

## Alternatives Considered

### Keep Storage Inside `RateLimiter`

Continue allowing `RateLimiter` to directly manage the in-memory bucket dictionary.
**Advantages**
- Simple architecture.
- Minimal number of components.
- Easy to understand for small applications.

**Disadvantages**
- Couples the public interface to one storage implementation.
- Makes additional storage backends harder to introduce.
- Makes distributed storage difficult to integrate cleanly.
- Increases the responsibility of `RateLimiter`.

---

### Backend Abstraction

Introduce a common backend interface and move storage-specific behavior into backend implementations.
**Advantages**
- Separates the public interface from storage.
- Allows multiple backend implementations.
- Keeps `RateLimiter` simple.
- Makes testing and extension easier.
- Supports both in-memory and external storage.

**Disadvantages**
- Adds an abstraction layer.
- Requires additional classes and modules.
- Slightly increases architectural complexity.

---

## Decision

Beginning with **v0.7.0**, the project uses a **backend abstraction**.
The `RateLimiterBackend` abstract interface defines the backend contract.
Two implementations currently exist:
- `InMemoryBackend`
- `RedisBackend`
The `RateLimiter` delegates `allow_request()` calls to the configured backend.

---

## Why This Decision?

The backend abstraction separates the public rate-limiting interface from backend-specific state management.
This allows:
- The same `RateLimiter` interface to work with different storage mechanisms.
- The in-memory implementation to remain simple.
- Redis to be introduced without changing the public API.
- Backend-specific concurrency mechanisms to remain isolated.
- Future storage backends to be added independently.
The abstraction also keeps the FastAPI integration independent from storage-specific implementation details.

---

## Why Redis?

Redis was selected as the first external backend because it provides fast in-memory data access and atomic server-side operations.
It also provides a natural foundation for sharing rate-limit state between application instances.
The Redis backend stores each user's bucket state using a Redis hash containing:
- `current_tokens`
- `last_refill_time`
User bucket keys use the prefix:
```text
ratelimiter:user:
```

## Why Lua

The Redis backend performs the complete rate-limit operation inside a Lua script.
The script performs:
- Reading the current bucket state.
- Obtaining the current time using Redis TIME.
- Calculating elapsed time.
- Refilling tokens.
- Limiting tokens to bucket capacity.
- Determining whether the request is allowed.
- Consuming a token when allowed.
- Writing the updated state.
- Refreshing the bucket TTL.
Keeping these operations inside one Redis script provides atomic execution at the Redis server.
This prevents concurrent requests from observing partially updated bucket state.

## Why Redis Time

The Redis backend obtains the current time using Redis TIME rather than relying on the application server's local clock.
This keeps the refill calculation based on the clock associated with the Redis state being modified.
It also avoids making the backend dependent on the local application process's wall-clock time for Redis-backed bucket calculations.

## Why Inject the Redis Client

The Redis client is provided to RedisBackend through its constructor rather than being created internally.
This decision keeps connection creation and configuration outside the backend.
It provides:
- Easier testing.
- Greater flexibility in Redis client configuration.
- Clear separation between connection management and rate-limiting behavior.
- Better control for applications embedding the backend.
The current implementation does not perform Redis health checks, automatic reconnection, or failure recovery.

## TTL-Based Bucket Cleanup

Redis-backed user buckets use a TTL to prevent inactive bucket state from remaining indefinitely.
The current implementation refreshes the bucket TTL after each request.
This provides automatic cleanup for inactive users without requiring a separate cleanup process.

## Trade-offs

The backend abstraction introduces additional architectural complexity compared with directly storing buckets inside `RateLimiter`.
Redis also introduces an external infrastructure dependency and operational considerations that do not exist in the in-memory implementation.
The Redis backend additionally requires Redis-compatible server infrastructure and does not currently provide built-in connection management, health checks, or failure recovery.
These trade-offs are accepted because the abstraction provides a cleaner path toward shared external state and future distributed deployments.

## Future Evolution

Future releases may introduce additional backend implementations or infrastructure capabilities.
Potential areas include:
- Additional storage backends.
- Redis configuration management.
- Health checks.
- Connection and failure handling.
- Distributed deployment testing.
- CI/CD automation.
The Docker deployment introduced in **v0.8.0** provides the current containerized deployment foundation for the FastAPI application and Redis backend.

---

# Decision 10 — Docker-Based Deployment

## Problem

As the project evolved to include both a FastAPI application and an external Redis backend, running the complete system required multiple services and environment-specific configuration.
The project needed a deployment approach that could package the application consistently and provide a simple way to run the FastAPI service together with Redis.

---

## Alternatives Considered

### Manual Local Setup

Run the FastAPI application and Redis server directly on the development machine.

**Advantages**

- Simple during development.
- Easy to inspect individual components.
- Minimal infrastructure overhead.

**Disadvantages**

- Requires Redis to be installed and configured separately.
- Environment differences can affect behavior.
- Multiple services must be started and configured manually.
- Reproducing the same environment on another machine is more difficult.

---

### Docker-Based Deployment

Package the FastAPI application into a Docker image and run the application together with Redis using Docker Compose.

**Advantages**

- Consistent application environment.
- Redis can run as a separate service without requiring a local Redis installation.
- Simple multi-service deployment using Docker Compose.
- Clear separation between the application container and Redis container.
- Easier reproduction of the deployment environment.

**Disadvantages**

- Introduces Docker as an additional development and deployment dependency.
- Adds container configuration and networking concepts.
- The current setup does not provide persistent Redis storage.
- The current Compose configuration does not include service health checks.

---

## Decision

Beginning with **v0.8.0**, the project uses **Docker-based deployment** for the containerized FastAPI and Redis environment.
The deployment consists of:
- A Docker container running the FastAPI application.
- A separate Redis container providing the Redis backend.
- Docker Compose for coordinating the application and Redis services.
The FastAPI application receives the Redis connection configuration through environment variables and uses `RedisBackend` for rate-limit state.
Docker is treated as a **deployment layer** rather than part of the core rate-limiting implementation.

---

## Why This Decision?

Docker provides a practical way to package and run the project's multi-service environment consistently.
The v0.8.0 deployment provides:
- A reproducible Python application environment.
- Containerized FastAPI execution.
- A dedicated Redis service.
- Automatic service networking through Docker Compose.
- Environment-based Redis host and port configuration.
- A straightforward way to start and stop the complete application stack.
Most importantly, the core `RateLimiter`, backend abstraction, and rate-limiting algorithm remain independent of Docker.
The same package can therefore still be used directly from Python without requiring the Docker deployment layer.

---

## Deployment Structure

The v0.8.0 deployment follows this structure:

```text
Client
  |
  v
FastAPI Container
  |
  v
RateLimiter
  |
  v
RedisBackend
  |
  v
Redis Container
```
Docker Compose manages the application and Redis services and provides the network through which the FastAPI container communicates with Redis.

## Trade-offs

Docker introduces additional configuration and tooling compared with running the Python application directly.
The deployment also depends on Docker and Docker Compose being available on the host machine.
The current configuration does not define a persistent Redis volume, so Redis state is not configured for persistence across removal and recreation of the Redis container.
The current Compose configuration also does not define Redis health checks or automated recovery behavior.
These limitations are intentional for the current milestone and can be addressed in future infrastructure-focused releases.

## Future Evolution

Future releases may extend the deployment architecture with:
- Redis health checks.
- Persistent Redis storage.
- Improved service startup and recovery handling.
- Production-oriented container configuration.
- Container image publishing.
- CI/CD automation.
- Distributed deployment testing.
Docker therefore establishes the deployment foundation for future infrastructure improvements without changing the core rate-limiting design.

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
- Using dictionary-based storage for the in-memory backend.
- Applying fine-grained locking to in-memory shared state.
- Organizing the project as a reusable Python package.
- Introducing automated testing with Python's built-in `unittest` framework.
- Using FastAPI as an integration layer for HTTP access.
- Introducing a backend abstraction.
- Implementing Redis as an alternative backend.
- Using Redis Lua scripting for atomic rate-limit processing.
- Using Redis `TIME` for Redis-backed refill calculations.
- Using TTL-based cleanup for inactive Redis buckets.
- Using Docker and Docker Compose for containerized deployment.
With **v0.8.0**, the project has evolved from a single-process in-memory implementation into a backend-independent rate-limiting system with both in-memory and Redis-backed implementations, together with a containerized FastAPI and Redis deployment environment.
The goal is not only to build a working rate limiter but also to document the engineering reasoning behind the decisions that transformed a simple algorithm into a production-focused software project.

---