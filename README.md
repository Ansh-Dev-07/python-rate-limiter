# Python Rate Limiter

A Python implementation of the **Token Bucket Rate Limiting Algorithm** built incrementally with a focus on software engineering principles, clean architecture, and versioned development.

This project is not just an implementation of a rate limiter—it is a learning journey from a basic in-memory token bucket to a production-oriented rate limiting system.

Current Version: **v0.2.0**

---

## Table of Contents

- [About the Project](#about-the-project)
- [Why Rate Limiting?](#why-rate-limiting)
- [Why Token Bucket?](#why-token-bucket)
- [Current Features](#current-features)
- [Project Structure](#project-structure)
- [Architecture Overview](#architecture-overview)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Example Usage](#example-usage)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Version History](#version-history)
- [License](#license)

## About the Project

Rate limiting is a technique used to control the number of requests a client can make to a service within a specific period of time. It helps protect applications from abuse, prevents server overload, and ensures fair resource usage among users.

This project implements the **Token Bucket Algorithm**, one of the most widely used rate limiting algorithms in modern backend systems. Instead of maintaining a single global bucket, the current implementation (v0.2.0) manages an independent token bucket for each user, allowing requests from different users to be limited separately.

The project is being developed incrementally using semantic versioning. Each release introduces a new concept while preserving backward compatibility whenever possible. This approach reflects how real-world software evolves over time and makes the repository useful as both a learning resource and a software engineering portfolio project.

## Why Rate Limiting?

Modern applications often receive thousands or even millions of requests from users, bots, and automated systems. Without any control mechanism, a sudden spike in traffic can overwhelm servers, increase response times, or even make a service unavailable.

Rate limiting is a defensive mechanism that controls how frequently a client can access a resource. Instead of allowing unlimited requests, it enforces predefined limits to ensure that the system remains stable and responsive.

Some common use cases include:

- Protecting public APIs from abuse and denial-of-service attacks.
- Preventing brute-force login attempts.
- Ensuring fair usage among multiple users.
- Controlling resource consumption in cloud applications.
- Managing request quotas for third-party APIs.

Rate limiting is widely used in API gateways, web servers, cloud platforms, and distributed systems. It is considered a fundamental building block for designing scalable and reliable backend services.

## Why Token Bucket?

There are several algorithms available for implementing rate limiting, including Fixed Window, Sliding Window, Leaky Bucket, and Token Bucket. Each algorithm has its own advantages and trade-offs.

This project uses the **Token Bucket Algorithm** because it provides a good balance between flexibility, simplicity, and performance.

In the Token Bucket algorithm:

- A bucket contains a fixed number of tokens.
- Each incoming request consumes one token.
- Tokens are regenerated over time at a constant refill rate.
- If at least one token is available, the request is allowed.
- If no tokens remain, the request is rejected until new tokens are added.

One of the biggest advantages of the Token Bucket algorithm is that it allows **short bursts of traffic** while still enforcing an average request rate over time. This makes it suitable for APIs and backend services where occasional bursts are expected but unlimited traffic should be prevented.

### Why Not Other Algorithms?

| Algorithm                | Limitation                                                                    |
|--------------------------|-------------------------------------------------------------------------------|
| Fixed Window             | Can allow traffic spikes at window boundaries.                                |
| Sliding Window           | More accurate but requires additional memory and computation.                 |
| Leaky Bucket             | Produces a constant output rate but does not naturally support burst traffic. |
| **Token Bucket**         | Allows controlled bursts while maintaining an average request rate.           |

For the current version of this project, the Token Bucket algorithm offers the best combination of simplicity, efficiency, and real-world applicability.

## Current Features

The current implementation (**v0.2.0**) includes the following features:

### Core Functionality

- ✅ Token Bucket rate limiting algorithm
- ✅ Configurable bucket capacity
- ✅ Configurable token refill rate
- ✅ Automatic (lazy) token refill based on elapsed time
- ✅ Request allow/reject mechanism
- ✅ Input validation for invalid capacity and refill rate

### Multi-User Support

- ✅ Independent token bucket for each user
- ✅ Automatic bucket creation for new users
- ✅ In-memory bucket storage using a Python dictionary
- ✅ Requests are processed independently for each user

### Design Highlights

- ✅ Object-Oriented Design (OOP)
- ✅ Separation of responsibilities between `RateLimiter` and `TokenBucket`
- ✅ Lazy bucket initialization (buckets are created only when required)
- ✅ Clean and modular code structure for future enhancements

### Current Implementation Scope

- In-memory implementation
- Single-process execution
- No external dependencies
- Suitable for learning, experimentation, and understanding the Token Bucket algorithm

## Project Structure

```text
python-rate-limiter/
│
├── main.py                 # Entry point containing the RateLimiter and TokenBucket implementations
├── README.md               # Project documentation
├── CHANGELOG.md            # Version history and release notes
├── PROJECT_TIMELINE.md     # Planned project milestones
├── LICENSE                 # MIT License
└── .gitignore              # Files ignored by Git
```

### File Overview

| File                    | Purpose                                                                                                  |
|-------------------------|----------------------------------------------------------------------------------------------------------|
| `main.py`               | Contains the complete implementation of the Token Bucket algorithm and the `RateLimiter` class.          |
| `README.md`             | Explains the project, its architecture, usage, and future roadmap.                                       |
| `CHANGELOG.md`          | Records the changes introduced in every released version.                                                |
| `PROJECT_TIMELINE.md`   | Outlines the project's planned evolution from basic implementation to a production-ready rate limiter.   |
| `LICENSE`               | Defines how others can use and distribute the project.                                                   |
| `.gitignore`            | Prevents unnecessary files (such as cache files and virtual environments) from being committed to Git.   |

> **Note:** The current implementation keeps everything in a single file (`main.py`) for simplicity. As the project grows in future releases, the repository will be reorganized into a modular package structure.

## Architecture Overview

The project follows a simple object-oriented design with two main classes:

- **`RateLimiter`** – Acts as the entry point for incoming requests. It manages user-specific token buckets and forwards requests to the appropriate bucket.
- **`TokenBucket`** – Implements the Token Bucket algorithm, including token refilling and request validation.

### Request Flow

```text
                 Incoming Request
                        │
                        ▼
            RateLimiter.allow_request(user)
                        │
                        ▼
          _get_or_create_bucket(user)
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
     Bucket Exists?             Create Bucket
            │                       │
            └───────────┬───────────┘
                        ▼
              TokenBucket.allow_request()
                        │
                        ▼
                 Refill Tokens
                        │
                        ▼
              Tokens Available?
                  │           │
                 Yes          No
                  │           │
                  ▼           ▼
           Consume Token   Reject Request
                  │
                  ▼
             Return True
```

### Class Responsibilities

| Class         | Responsibility                                                                                              |
|---------------|-------------------------------------------------------------------------------------------------------------|
| `RateLimiter` | Maintains a collection of token buckets and routes requests to the correct bucket.                          |
| `TokenBucket` | Stores bucket state, refills tokens over time, and decides whether a request should be allowed or rejected. |

### Design Principles

- **Single Responsibility Principle (SRP):** Each class has one primary responsibility.
- **Lazy Initialization:** A token bucket is created only when a user sends their first request.
- **Encapsulation:** Bucket state is managed internally by the `TokenBucket` class.
- **Modularity:** The separation between request routing and rate-limiting logic makes the project easier to extend in future versions.

## How It Works

The rate limiter follows the Token Bucket algorithm to determine whether an incoming request should be accepted or rejected.

### Step 1: Create or Retrieve a Bucket

When a request is received, the `RateLimiter` checks whether the user already has a token bucket.

- If the bucket exists, it is reused.
- If the bucket does not exist, a new `TokenBucket` is created and stored.

This ensures that each user has an independent rate limit.

---

### Step 2: Refill Tokens

Before processing every request, the bucket calculates how much time has passed since the last refill.

The number of new tokens is calculated using:

```text
New Tokens = Elapsed Time × Refill Rate
```

The bucket is then updated as:

```text
Current Tokens = min(Capacity, Current Tokens + New Tokens)
```

This guarantees that the bucket never stores more tokens than its configured capacity.

---

### Step 3: Process the Request

After refilling:

- If at least one token is available:
  - One token is consumed.
  - The request is allowed.
  - `True` is returned.

- If no tokens are available:
  - No token is consumed.
  - The request is rejected.
  - `False` is returned.

---

### Example

Suppose the bucket has the following configuration:

- Capacity = **5**
- Refill Rate = **1 token/second**

Initially:

```text
Tokens = 5
```

Five consecutive requests are allowed.

```text
Request 1 ✅
Request 2 ✅
Request 3 ✅
Request 4 ✅
Request 5 ✅
```

The sixth request is rejected because the bucket is empty.

```text
Request 6 ❌
```

After waiting **2 seconds**, the bucket receives **2 new tokens**.

```text
Tokens = 2
```

The next two requests are allowed again.

```text
Request 7 ✅
Request 8 ✅
```

---

### Time Complexity

| Operation         | Complexity   |
|-------------------|--------------|
| Get/Create Bucket | O(1) Average |
| Refill Tokens     | O(1)         |
| Allow Request     | O(1)         |

The current implementation performs all operations in constant time, making it efficient for in-memory rate limiting.

## Getting Started

### Prerequisites

Before running the project, ensure you have:

- Python 3.8 or later installed
- A terminal or command prompt
- Any Python IDE or code editor (VS Code, PyCharm, etc.)

### Clone the Repository

```bash
git clone https://github.com/Ansh-Dev-07/python-rate-limiter.git

cd python-rate-limiter
```

### Run the Project

Execute the following command:

```bash
python main.py
```

The project contains sample requests demonstrating how the rate limiter behaves for different users.

### Example Usage

```python
limiter = RateLimiter(capacity=5, refill_rate=1)

print(limiter.allow_request("User A"))
print(limiter.allow_request("User A"))
print(limiter.allow_request("User B"))
```

Each user receives an independent token bucket. Requests from one user do not affect the rate limit of another user.

## Example Output

```text
True
True
True
True
True
False

True
True
False
```

The exact output depends on the configured bucket capacity, refill rate, and the time elapsed between requests.

## Current Limitations

The current implementation is intentionally simple to focus on understanding the Token Bucket algorithm. The following features are **not** included in v0.2.0:

- No thread safety (not suitable for concurrent access)
- No persistent storage (all data is stored in memory)
- No automatic cleanup of inactive user buckets
- No distributed rate limiting
- No Redis or external storage integration
- No REST API or web framework integration
- No automated unit tests

These limitations will be addressed in future versions as the project evolves.

---

## Roadmap

The project will continue to evolve through incremental releases.

| Version | Planned Feature            | Status        |
|---------|----------------------------|---------------|
| v0.1.0  | Core Token Bucket          | ✅ Completed |
| v0.2.0  | Multi-User Rate Limiter    | ✅ Completed |
| v0.3.0  | Thread-Safe Implementation | 🔄 Planned   |
| v0.4.0  | Redis-Based Storage        | 🔄 Planned   |
| v0.5.0  | Distributed Rate Limiter   | 🔄 Planned   |
| v1.0.0  | Production-Ready Release   | 🎯 Goal      |

---

## Version History

### v0.2.0

**Added**

- `RateLimiter` class
- Per-user token bucket management
- Lazy bucket creation
- Dictionary-based bucket storage
- Improved object-oriented design

**Changed**

- Requests are now processed through the `RateLimiter` instead of interacting directly with the `TokenBucket`.
- Separated request routing from token bucket logic.

---

### v0.1.0

Initial implementation of the Token Bucket algorithm.

**Features**

- Configurable bucket capacity
- Configurable refill rate
- Lazy token refill
- Request allow/reject mechanism
- Input validation

---

## Learning Objectives

This project is being developed to strengthen understanding of:

- Rate limiting algorithms
- Object-oriented programming (OOP)
- Backend system design
- Software architecture
- Version control using Git and GitHub
- Incremental software development
- Technical documentation
- Open-source project practices

Each release focuses on introducing one major engineering concept while maintaining a clean and well-documented codebase.

---

## Author

**Ansh Soni**

GitHub: https://github.com/Ansh-Dev-07

---

## License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.