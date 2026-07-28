# Project Timeline

This document outlines the planned development roadmap for the **Python Rate Limiter** project.

The objective is to evolve the project incrementally from a basic in-memory implementation into a production-ready distributed rate limiting system while learning software engineering principles, system design, and backend development practices.

---

# Project Roadmap

| Version | Milestone                   | Status        |
|---------|-----------------------------|---------------|
| v0.1.0  | Core Token Bucket Algorithm | ✅ Completed |
| v0.2.0  | Multi-User Rate Limiter     | ✅ Completed |
| v0.3.0  | Thread-Safe Rate Limiter    | 🔄 Planned   |
| v0.4.0  | Redis-Based Storage         | 🔄 Planned   |
| v0.5.0  | Distributed Rate Limiter    | 🔄 Planned   |
| v1.0.0  | Production-Ready Release    | 🎯 Goal      |

---

# Release Details

## ✅ v0.1.0 — Core Token Bucket

### Objectives
- Understand the Token Bucket algorithm.
- Implement a basic in-memory bucket.
- Support configurable capacity.
- Support configurable refill rate.
- Implement lazy token refill.
- Validate constructor inputs.

### Outcome
A functional Token Bucket implementation capable of allowing or rejecting requests based on available tokens.

---

## ✅ v0.2.0 — Multi-User Rate Limiter

### Objectives
- Introduce the `RateLimiter` class.
- Manage one bucket per user.
- Implement lazy bucket creation.
- Improve code organization using object-oriented principles.

### Outcome
Each user now has an independent token bucket, allowing requests to be rate-limited separately while keeping the implementation simple and extensible.

---

## 🔄 v0.3.0 — Thread-Safe Rate Limiter

### Objectives
- Protect shared resources from race conditions.
- Introduce synchronization using Python threading primitives.
- Support concurrent requests safely.
- Demonstrate thread safety through examples and tests.

### Expected Learning
- Thread synchronization
- Locks and mutual exclusion
- Concurrent programming concepts

---

## 🔄 v0.4.0 — Redis Integration

### Objectives
- Store bucket state in Redis.
- Allow multiple application instances to share rate-limiting data.
- Prepare the project for horizontal scalability.

### Expected Learning
- Redis fundamentals
- External state management
- Backend scalability concepts

---

## 🔄 v0.5.0 — Distributed Rate Limiter

### Objectives
- Extend the project to support distributed deployments.
- Handle rate limiting across multiple servers.
- Explore consistency and scalability challenges.

### Expected Learning
- Distributed systems
- System design
- Fault tolerance
- Scalability patterns

---

## 🎯 v1.0.0 — Production-Ready Release

### Objectives
- Refactor into a modular package structure.
- Add comprehensive automated tests.
- Improve documentation.
- Optimize performance.
- Finalize project architecture.

### Expected Outcome
A well-documented, maintainable, and extensible rate limiter demonstrating the evolution from a simple algorithm to a production-oriented backend component.

---

# Learning Journey

This project is intentionally developed in small, versioned milestones.

Each release introduces a new engineering concept instead of implementing everything at once. This approach helps build a deeper understanding of backend engineering, system design, software architecture, and maintainable code.

The roadmap may evolve as new ideas, optimizations, or architectural improvements are discovered during development.