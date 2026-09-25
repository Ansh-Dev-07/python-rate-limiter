# Docker Deployment

This document explains how Docker is used to containerize and run the Python Rate Limiter project with its FastAPI and Redis components.
Current Deployment Version: **v0.8.0**

---

## Overview

Starting with v0.8.0, the project can be run as a containerized application using Docker and Docker Compose.
The Docker deployment consists of two services:
- A FastAPI application container.
- A Redis container used by the `RedisBackend` for rate-limit state.
Docker Compose creates a shared network between the services, allowing the FastAPI application to communicate with Redis using the Redis service name.
The containerized architecture is:

```text
                    Client
                      │
                      │ HTTP :8000
                      ▼
             ┌─────────────────┐
             │    FastAPI      │
             │    Container    │
             │                 │
             │  RateLimiter    │
             │       │         │
             │ RedisBackend     │
             └───────┬─────────┘
                     │
            Docker Compose Network
                     │
                     ▼
             ┌─────────────────┐
             │      Redis      │
             │    Container    │
             │                 │
             │  Bucket State   │
             └─────────────────┘
```

---

## Why Docker?

Before v0.8.0, the application could be run directly in a local Python environment.
Docker adds a reproducible runtime environment around the existing application.
The v0.8.0 milestone focuses on:
* Containerizing the FastAPI application.
* Running Redis as a separate container.
* Connecting the application and Redis through Docker networking.
* Configuring Redis connection details through environment variables.
* Providing a repeatable local deployment using Docker Compose.
Docker does not change the Token Bucket algorithm or the backend abstraction introduced in v0.7.0.
Instead, it provides deployment infrastructure around the existing application.

---

## v0.8.0 Changes

The Docker milestone introduces:
* `Dockerfile`
* `.dockerignore`
* `docker-compose.yml`
* Containerized FastAPI application
* Containerized Redis service
* Docker Compose networking
* Environment-based Redis configuration
* Redis-backed FastAPI deployment
The existing `RateLimiter`, `RedisBackend`, and Redis Lua processing remain responsible for rate-limiting behavior.
Docker is responsible for packaging and running the application and its Redis dependency.

---

# Dockerfile

The project includes a `Dockerfile` at the repository root.
The current Dockerfile:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
```

## Dockerfile Breakdown

### Base Image

```dockerfile
FROM python:3.12-slim
```

The application uses the Python 3.12 slim image as its container base.
The slim image provides Python while keeping the base environment smaller than the standard Python image.

---

### Working Directory

```dockerfile
WORKDIR /app
```

The application files are placed inside `/app` within the container.

---

### Copy Project Files

```dockerfile
COPY . .
```

The project is copied into the container image.
Files excluded by `.dockerignore` are not included in the Docker build context.

---

### Install the Package

```dockerfile
RUN pip install .
```

The project is installed using the packaging configuration defined in `pyproject.toml`.
This means the Docker image uses the same Python package structure as the local project.

---

### Start FastAPI

```dockerfile
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
```

The container starts the FastAPI application using Uvicorn.
The application listens on all container interfaces so that Docker can expose the service to the host machine.

---

# `.dockerignore`

The project includes a `.dockerignore` file to prevent unnecessary local files from being included in the Docker build context.
Current exclusions include:

```text
.venv/
.git/
__pycache__/
*.pyc
.env
python_rate_limiter.egg-info/
```

This prevents development environments, Git metadata, Python cache files, environment files, and generated package metadata from being copied into the Docker build context.
The `.env` exclusion is particularly important because environment files may contain configuration or secrets that should not be included in an image.

---

# Docker Compose

The project uses Docker Compose to run the FastAPI application and Redis together.
The Compose deployment contains two services:

```text
api
redis
```

The `api` service builds the FastAPI application from the project's `Dockerfile`.
The `redis` service uses the Redis 7 image.
The services communicate through the Docker Compose network.

---

## API Container

The API container runs the FastAPI application.
The container exposes the application through port `8000`.
The application receives its Redis connection configuration through environment variables:

```text
REDIS_HOST
REDIS_PORT
```

The configured Redis host is the Compose service name:

```text
rate-limiter-redis
```

and the Redis port is:

```text
6379
```

---

## Redis Container

The Redis service uses Redis 7.
Redis stores the bucket state used by `RedisBackend`.
The Redis backend stores values such as:

```text
current_tokens
last_refill_time
```

for individual user buckets.
The rate-limit processing itself remains implemented by the Redis Lua script introduced in v0.7.0.

---

# Container Networking

Docker Compose provides a network that allows the API container and Redis container to communicate.
The API does not connect to Redis using:

```text
localhost
```

Instead, it connects using the Redis service name configured by Docker Compose.
Conceptually:

```text
FastAPI Container
       │
       │ REDIS_HOST=rate-limiter-redis
       ▼
Docker Compose Network
       │
       ▼
Redis Container
```

This is necessary because `localhost` inside the API container refers to the API container itself rather than the Redis container.

---

# Environment-Based Redis Configuration

The FastAPI application reads Redis connection details from environment variables.
The relevant configuration is:

```text
REDIS_HOST
REDIS_PORT
```

This allows the application to use different Redis hosts without changing the application code.
For the Docker Compose deployment, the configuration points to the Redis service inside the Compose network.
This keeps deployment-specific connection information outside the core rate-limiting implementation.

---

# Running the Application

## Prerequisites

The Docker deployment requires:
* Docker
* Docker Compose support

The Python virtual environment is not required to run the containerized application.

---

## Build the Containers

From the project root:

```bash
docker compose build
```

This builds the FastAPI application image using the project's `Dockerfile`.

---

## Start the Services

Run:

```bash
docker compose up -d
```

This starts the FastAPI and Redis containers in the background.
Check the running services with:

```bash
docker compose ps
```

Both services should be running.

---

## View Container Logs

To view logs for all services:

```bash
docker compose logs
```

To view only the API logs:

```bash
docker compose logs api
```

To view Redis logs:

```bash
docker compose logs redis
```

---

# Testing the Containerized API

Once the containers are running, the FastAPI application is available through:

```text
http://localhost:8000
```

The root endpoint can be tested with:

```bash
curl http://localhost:8000/
```

The rate-limit endpoint is:

```text
POST /allow
```

For example:

```json
Invoke-RestMethod `
    -Uri http://localhost:8000/allow `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"user":"DockerTest"}'
```

The API communicates with the Redis container through the Docker Compose network.

---

## Rate-Limit Verification

The containerized deployment was verified using the Redis-backed FastAPI application.
With the configured rate limit:

```text
Capacity = 5
```

the observed behavior was:

```text
Request 1 → Allowed
Request 2 → Allowed
Request 3 → Allowed
Request 4 → Allowed
Request 5 → Allowed
Request 6 → HTTP 429
```

This verifies the complete path:

```text
HTTP Request
     ↓
FastAPI
     ↓
RateLimiter
     ↓
RedisBackend
     ↓
Redis Lua Script
     ↓
Redis Bucket State
     ↓
Allow / Reject
     ↓
HTTP Response
```

---

# Redis-Backed Rate Limiting

Docker does not implement rate limiting itself.
The responsibilities remain separated:

```text
FastAPI
→ HTTP interface

RateLimiter
→ Public rate-limiting interface

RedisBackend
→ Redis-backed rate-limit processing

Lua Script
→ Atomic refill, decision, state update, and TTL refresh

Redis
→ External bucket state storage

Docker
→ Application and infrastructure containerization
```

This separation allows Docker to provide deployment infrastructure without coupling the Token Bucket algorithm to Docker-specific code.

---

# Container Lifecycle

The services can be stopped with:

```bash
docker compose down
```

They can then be started again with:

```bash
docker compose up -d
```

The current Compose configuration does not define a persistent Redis volume.
Redis state therefore is not configured for persistence across removal and recreation of the Redis container.
The Redis container in this milestone provides the external runtime state required by the application without attempting to provide a complete production persistence configuration.

---

# Current Scope

The v0.8.0 Docker implementation provides:
* Containerized FastAPI application.
* Containerized Redis service.
* Docker Compose orchestration.
* Container networking between FastAPI and Redis.
* Environment-based Redis connection configuration.
* Redis-backed rate limiting through `RedisBackend`.
* Repeatable local containerized deployment.
The existing rate-limiting architecture remains unchanged.
Docker operates around the application and backend infrastructure rather than replacing the underlying Token Bucket implementation.

---

# Current Limitations

The current Docker implementation does not include:
* Redis persistent volumes.
* Redis health checks.
* Automatic Redis reconnection.
* Redis failure recovery.
* Authentication/TLS configuration management.
* Kubernetes deployment.
* Production orchestration.
* CI/CD automation.
* Container image publishing.
These capabilities may be considered in future releases.

---

# Future Improvements

Future infrastructure milestones may extend the Docker deployment with:
* CI/CD automation.
* Automated Docker image builds.
* Container image publishing.
* Health checks.
* Improved failure handling.
* Persistent Redis configuration.
* Additional deployment environments.
These improvements will build upon the existing Docker and backend architecture rather than replacing it.

---

# Summary

v0.8.0 introduces Docker-based deployment for the Python Rate Limiter project.
The release packages the FastAPI application into a Docker container and runs Redis as a separate container using Docker Compose.
The two services communicate through a Docker network, while Redis connection details are supplied through environment variables.
The resulting deployment provides:

```text
Client
  ↓
FastAPI Container
  ↓
RateLimiter
  ↓
RedisBackend
  ↓
Redis Container
```

This milestone extends the project from a locally runnable backend component into a reproducible containerized deployment while keeping the core rate-limiting architecture independent from Docker.