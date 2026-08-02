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
| 🔄 v0.4.0 | Testing & Quality             | Planned   |
| 🔄 v0.5.0 | Packaging & Project Structure | Planned   |
| 🔄 v0.6.0 | FastAPI Integration           | Planned   |
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

## 🔄 v0.4.0 — Testing & Quality

### Objectives
- Learn testing philosophy.
- Learn Python's `unittest` framework.
- Write automated tests for all public methods.
- Replace manual testing with automated test cases.
- Create a dedicated `tests/` directory.

### Expected Learning
- Unit testing
- Test-driven thinking
- Regression testing
- Software quality practices

---

## 🔄 v0.5.0 — Packaging & Project Structure

### Objectives
- Refactor the project into a proper Python package.
- Organize the code into modules.
- Improve maintainability and scalability.
- Prepare the project for installation via `pip`.

### Expected Learning
- Python packaging
- Project organization
- Module design

---

## 🔄 v0.6.0 — FastAPI Integration

### Objectives
- Expose the rate limiter through REST APIs.
- Integrate the core logic with FastAPI.
- Build reusable API endpoints.

### Expected Learning
- FastAPI
- REST API design
- Backend service development

---

## 🔄 v0.7.0 — Redis Backend

### Objectives
- Replace in-memory bucket storage with Redis.
- Enable shared state across multiple application instances.
- Prepare for horizontal scalability.

### Expected Learning
- Redis
- Shared storage
- Distributed state management

---

## 🔄 v0.8.0 — Docker

### Objectives
- Containerize the application.
- Create Docker images.
- Simplify deployment across environments.

### Expected Learning
- Docker
- Containerization
- Deployment fundamentals

---

## 🔄 v0.9.0 — CI/CD

### Objectives
- Automatically run tests on every GitHub push.
- Configure GitHub Actions.
- Maintain code quality through automated workflows.

### Expected Learning
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

The roadmap may evolve as the project grows, but every release aims to improve both the implementation and the developer's understanding of backend systems and software engineering.