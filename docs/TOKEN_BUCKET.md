# Token Bucket Algorithm

This document explains the **Token Bucket algorithm**, which forms the core of the Python Rate Limiter project.

Rather than focusing on the project architecture or implementation details, this document explains the algorithm itself—why it exists, how it works, and why it is widely used in networking and backend systems.

Current Algorithm Version: **v0.6.0**

---

# What is Rate Limiting?

Rate limiting is the process of controlling how many requests a client can make within a given period of time.

Instead of allowing unlimited access to a resource, a rate limiter enforces predefined limits to ensure fairness, protect system resources, and maintain service availability.

Without rate limiting, a single client could consume excessive resources, negatively affecting the experience of other users or even causing service outages.

Common examples include:

- API request limits
- Login attempt restrictions
- File upload limits
- Payment API protection
- Messaging systems
- Authentication services

Rate limiting is a fundamental technique used in modern distributed systems, cloud platforms, and web applications.

---

# Why Do We Need Rate Limiting?

Modern applications often serve thousands or even millions of users simultaneously.

Without request control, systems become vulnerable to problems such as:

- Resource exhaustion
- Denial-of-Service (DoS) attacks
- Unfair resource usage
- Increased infrastructure costs
- Reduced application availability

A well-designed rate limiter helps maintain predictable system behavior by ensuring that every client receives a fair share of available resources.

It improves both system reliability and user experience while protecting backend services from overload.

---

# What is the Token Bucket Algorithm?

The **Token Bucket** algorithm is one of the most widely used rate-limiting algorithms in networking and backend systems.

The basic idea is simple:

> A bucket holds a limited number of **tokens**. Every incoming request must consume one token. If no tokens are available, the request is rejected until new tokens are added.

Unlike algorithms that enforce a fixed number of requests within strict time windows, the Token Bucket algorithm allows short bursts of traffic while still enforcing an average request rate over time.

This balance between flexibility and protection makes it a popular choice for APIs, gateways, cloud services, and networking equipment.

---

## Core Concepts

The algorithm is built around four key concepts.

### 1. Bucket Capacity

The bucket has a maximum number of tokens it can hold.

Example:

```
Capacity = 5

┌───────────────┐
│ ● ● ● ● ● │
└───────────────┘

5 Tokens Available
```

Once the bucket reaches its maximum capacity, additional tokens are discarded.

---

### 2. Tokens

Each token represents permission to process **one request**.

For every accepted request:

```
1 Request
      │
      ▼
Consume 1 Token
```

If no tokens remain, the request is rejected.

---

### 3. Refill Rate

Tokens are continuously replenished over time.

For example:

```
Refill Rate = 1 token / second
```

means one new token becomes available every second until the bucket reaches its maximum capacity.

---

### 4. Burst Handling

One of the biggest advantages of the Token Bucket algorithm is its ability to allow temporary bursts of traffic.

Suppose the bucket capacity is five tokens.

```
Initial State

● ● ● ● ●

5 requests arrive immediately.

↓

All 5 requests succeed.

↓

Bucket becomes empty.

○ ○ ○ ○ ○
```

Future requests must wait for new tokens to be generated.

This allows occasional bursts while still enforcing a long-term average request rate.

---

## High-Level Workflow

The algorithm follows the same sequence for every request.

```
Incoming Request
        │
        ▼
Refill Tokens
        │
        ▼
Token Available?
     │        │
   Yes        No
    │          │
    ▼          ▼
Consume     Reject
 Token      Request
    │
    ▼
Allow Request
```

This simple workflow makes the Token Bucket algorithm efficient, predictable, and easy to implement.

---

# Lazy Refill Strategy

A naive implementation of the Token Bucket algorithm continuously adds tokens to the bucket at fixed time intervals.

For example:

```
Every Second
      │
      ▼
Add One Token
```

Although this approach is simple, it has an important drawback.

The application must continue running a background timer or thread even when no requests are arriving.

This wastes CPU time and system resources.

---

## What is Lazy Refill?

Instead of continuously generating tokens, this project uses a **lazy refill strategy**.

Tokens are replenished **only when a request arrives**.

The algorithm calculates how much time has passed since the previous request and adds the appropriate number of tokens at that moment.

```
Incoming Request
        │
        ▼
Calculate Elapsed Time
        │
        ▼
Generate Missing Tokens
        │
        ▼
Process Request
```

No background thread is required.

---

### Fractional Token Accumulation

The implementation tracks the token count using a numeric value rather than requiring tokens to be generated only as whole units.

For example, if the refill rate is:

```text
1 token / second
```

and 0.5 seconds have elapsed, the bucket may accumulate:

```text
0.5 tokens
```

A request is allowed only when at least one complete token is available.

This allows the refill calculation to represent elapsed time accurately without requiring a background timer.

---

## Example

Suppose:

```
Capacity = 5 Tokens
Refill Rate = 1 Token / Second
```

Initial state:

```
● ● ● ● ●
```

A user consumes all five tokens.

```
○ ○ ○ ○ ○
```

The user waits for **3 seconds** before making another request.

When the next request arrives:

```
Elapsed Time = 3 seconds

↓

New Tokens = 3

↓

Bucket

● ● ● ○ ○
```

The refill happens **only when the request is processed**.

---

## Why is Lazy Refill Better?

Compared with continuous refill, lazy refill provides several advantages.

### Lower Resource Usage

No timer thread is required.

The application performs work only when requests arrive.

---

### Simpler Architecture

There is no need to manage background schedulers or synchronization between refill threads and request threads.

---

### Better Scalability

As the number of users grows, the refill logic remains efficient because inactive users consume almost no processing time.

---

### Widely Used

Many production systems implement some variation of lazy refill because it provides excellent performance while keeping the implementation relatively simple.

---

## Implementation in this Project

The refill operation occurs immediately before every request is evaluated.

The algorithm:

1. Calculates the elapsed time since the previous refill.
2. Calculates the number of tokens generated during that elapsed time.
3. Adds the generated tokens to the current token count.
4. Caps the token count at the bucket capacity.
5. Updates the last refill timestamp.
6. Processes the incoming request.

This guarantees that the bucket state is always up to date without requiring continuous background processing.

### Refill Calculation

The implementation calculates newly available tokens using the elapsed time and configured refill rate:

```text
New Tokens = Elapsed Time × Refill Rate
```

The resulting token count is then capped at the configured bucket capacity:

```text
Current Tokens =
    min(Capacity, Current Tokens + New Tokens)
```

For example, with:

```text
Refill Rate = 2 tokens / second
Elapsed Time = 1.5 seconds
```

the refill calculation produces:

```text
New Tokens = 1.5 × 2
           = 3 tokens
```

The implementation then adds those tokens to the current bucket state without allowing the total to exceed the bucket capacity.

---

# Advantages

The Token Bucket algorithm is one of the most popular rate-limiting algorithms because it provides a good balance between performance, flexibility, and simplicity.

## Allows Burst Traffic

Unlike fixed-window algorithms, the Token Bucket algorithm allows clients to send multiple requests in a short period if tokens have been accumulated.

This makes applications feel more responsive while still enforcing a long-term average request rate.

---

## Efficient Resource Utilization

Using lazy refill eliminates the need for background schedulers or continuously running refill threads.

The algorithm performs work only when requests arrive.

---

## Predictable Request Rate

Although short bursts are allowed, the refill rate controls the long-term rate at which new requests can be sustained after the available tokens are consumed.

This provides fairness while protecting backend resources.

---

## Easy to Implement

The algorithm requires only a small amount of state:

- Bucket capacity
- Current token count
- Refill rate
- Last refill timestamp

This simplicity makes the algorithm easy to understand, maintain, and extend.

---

## Scalable Design

Each user maintains an independent token bucket.

This naturally supports multi-user rate limiting and prepares the project for future distributed storage using Redis.

---

# Limitations

Although the Token Bucket algorithm is highly effective, it is not a perfect solution for every use case.

---

## Temporary Bursts Are Allowed

Because unused tokens accumulate over time, a client may send several requests at once after being inactive.

This behavior is intentional, but some systems require stricter request spacing.

---

## In-Memory Storage

The current implementation stores bucket state in memory.

If the application restarts, all bucket information is lost.

Redis-backed storage is planned for **v0.7.0** to address this limitation.

---

## Single-Process Scope

The current implementation supports thread-safe execution inside a single Python process.

Multiple application instances do not currently share rate-limiting state.

Distributed synchronization is planned for **v0.7.0** through the Redis backend.

---

## Time Dependency

The current implementation uses `time.time()` to measure elapsed time.

If the system clock changes unexpectedly, token calculations may become inaccurate.

A future implementation could use a monotonic clock such as `time.monotonic()` for elapsed-time measurement, since monotonic clocks are not affected by system clock adjustments.

---

## Future Improvements

The current implementation intentionally focuses on learning software engineering concepts step by step.

Future releases will extend the surrounding system with:

- Redis-backed bucket storage
- Distributed rate limiting
- Docker deployment
- CI/CD automation
- Performance benchmarking

Each improvement will build upon the existing architecture without changing the fundamental Token Bucket algorithm.

---

# Time & Space Complexity

The Token Bucket algorithm is designed to make request processing extremely efficient.

Each incoming request performs only a small number of operations regardless of how long the application has been running or how many requests have been processed previously.

---

## Time Complexity

### Request Processing

For every incoming request, the algorithm performs:

- Calculate elapsed time
- Refill tokens (if necessary)
- Check token availability
- Consume one token (if available)

Each of these operations takes constant time.

```
Time Complexity = O(1)
```
This applies to the processing of an individual bucket request. The calculation does not iterate through previous requests or generated tokens.

The execution time does not depend on:

- Number of previous requests
- Number of elapsed seconds
- Bucket capacity
- Number of generated tokens

Every request requires approximately the same amount of work.

---

### Bucket Creation

When a new user sends their first request:

- Create a new `TokenBucket`
- Store it inside the user dictionary

Average complexity:

```
O(1)
```

because Python dictionary insertion is an average constant-time operation.

---

## Space Complexity

A single `TokenBucket` maintains only a fixed amount of state:

- Bucket capacity
- Current token count
- Refill rate
- Last refill timestamp
- Thread lock

Therefore, the space required by an individual bucket is:

```text
Space Complexity = O(1)
```

In the project's multi-user `RateLimiter`, one bucket is maintained for each user with stored state.

Therefore, the overall memory usage of the rate limiter is:

```text
Space Complexity = O(n)
```

where:

```text
n = Number of Users with Stored Buckets
```

As more unique users access the application, one bucket is created for each user and remains stored until the limiter instance is discarded or bucket cleanup is introduced.

This distinction separates the complexity of the Token Bucket itself from the memory requirements of the project's multi-user implementation.

---

## Why is the Algorithm Efficient?

The Token Bucket algorithm avoids expensive operations such as:

- Iterating over previous requests
- Maintaining request history
- Background refill loops
- Periodic cleanup tasks

Instead, each request updates only the bucket that belongs to the requesting user.

This constant-time behavior makes the algorithm suitable for high-throughput backend systems.

---

## Performance Characteristics

| Operation | Complexity |
|-----------|------------|
| Allow Request | **O(1)** |
| Refill Tokens | **O(1)** |
| Create Bucket | **O(1)** *(average)* |
| Lookup Bucket | **O(1)** *(average)* |
| Memory Usage | **O(n)** |

These performance characteristics remain the same regardless of how long the application has been running.

---

# Real-World Applications

The Token Bucket algorithm is widely used across networking, cloud computing, and backend systems because it provides predictable request control while allowing temporary bursts of traffic.

Some common applications include:

---

## API Rate Limiting

Modern REST APIs often limit the number of requests that a client can make within a given period.

Examples include:

- GitHub API
- Stripe API
- Google Cloud APIs
- AWS APIs
- OpenAI APIs

A Token Bucket helps ensure that one client cannot overwhelm the service while still allowing short bursts of legitimate traffic.

---

## Authentication Systems

Login endpoints are common targets for brute-force attacks.

A Token Bucket can restrict the number of login attempts made by a single user or IP address, helping to reduce unauthorized access attempts while still allowing normal users to authenticate successfully.

---

## Messaging Systems

Applications such as chat platforms and notification services often limit how quickly messages can be sent.

Examples include:

- Chat applications
- Email services
- SMS gateways
- Push notification systems

Rate limiting helps prevent spam and abusive behavior.

---

## Cloud Infrastructure

Cloud providers frequently use rate limiting to protect shared infrastructure.

Examples include:

- API gateways
- Load balancers
- Reverse proxies
- Service meshes

This ensures fair resource allocation among multiple tenants sharing the same infrastructure.

---

## Network Traffic Shaping

The Token Bucket algorithm originated in computer networking.

Routers and switches use it to regulate network bandwidth, smooth traffic bursts, and prevent congestion while maintaining an average transmission rate.

---

## Microservices

In a microservice architecture, services communicate through APIs.

Applying a Token Bucket at service boundaries helps:

- Prevent cascading failures.
- Protect downstream services from overload.
- Improve overall system stability.
- Maintain predictable performance under heavy traffic.

---

# Why This Project Uses the Token Bucket Algorithm

This project uses the Token Bucket algorithm because it offers an excellent balance between simplicity, efficiency, and practical usefulness.

It demonstrates several important software engineering concepts, including:

- Object-oriented design
- Thread safety
- Request management
- Resource protection
- Automated testing
- Package organization

These concepts make it an ideal project for learning backend development and system design while building a reusable software component.

---

# Summary

The **Token Bucket algorithm** is one of the most practical and widely adopted rate-limiting algorithms used in modern software systems.

By allowing controlled bursts of traffic while enforcing a configurable average request rate, it provides an excellent balance between performance, fairness, and simplicity.

Throughout this document, we explored:

- Why rate limiting is essential in modern applications.
- How the Token Bucket algorithm operates.
- The concept of lazy token refill.
- The advantages and limitations of the algorithm.
- Its computational complexity.
- Common real-world applications.

This project builds upon these concepts by implementing the Token Bucket algorithm as a reusable, thread-safe Python package.

Rather than implementing every possible feature at once, the project evolves incrementally through versioned releases. Each release introduces a single software engineering milestone while preserving the core principles of the Token Bucket algorithm.

With FastAPI now providing an HTTP integration in v0.6.0, future releases will extend the surrounding architecture with Redis, Docker, and CI/CD while the underlying algorithm remains unchanged. This demonstrates an important software engineering principle:

> **A well-designed core algorithm should remain stable while the surrounding architecture continues to evolve.**

The Token Bucket algorithm therefore serves not only as the foundation of this project, but also as an excellent example of how a simple algorithm can scale into a production-oriented backend component through thoughtful engineering and incremental design.