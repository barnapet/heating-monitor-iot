# Backend Service – Cloud-Native Telemetry API

## Audience
- Backend Engineers
- Platform Engineers
- Tech Leads

---

## Role in the System

The backend service is responsible for **persisting heating telemetry data** and exposing it through a stable, well-defined **REST API**.

It represents the **system of record** for structured, queryable data and is intentionally **decoupled from real-time alerting**, which is handled upstream by AWS IoT Core and serverless components.

---

## Architecture Overview

The service follows a classic layered architecture:

```text
Controller → Service → Repository
```

### Key characteristics
- Stateless application design
- Externalized configuration
- Clear separation of concerns
- Infrastructure-agnostic runtime

This architecture enables **horizontal scaling**, predictable behavior, and smooth operation in containerized and orchestrated environments.

---

## API Design

The service exposes RESTful endpoints for telemetry ingestion and retrieval.

### Design principles
- Explicit API versioning (`/api/v1`)
- DTO-based request and response models
- Input validation at the API boundary
- No direct entity exposure

**Java Records** are used for DTOs to enforce immutability, clarity, and strict API contracts.

---

## Persistence Model

Telemetry data is persisted in **PostgreSQL** using **Spring Data JPA**.

### Key aspects
- Relational schema optimized for time-series-like workloads
- Clear entity boundaries
- Automatic `createdAt` auditing

The relational model complements the raw, append-only event storage in DynamoDB by enabling **structured queries, reporting, and analytics**.

---

## Database Migrations

Database schema evolution is managed using **Flyway**.

### Benefits
- Version-controlled schema definitions
- Repeatable and deterministic migrations
- Environment-agnostic deployment

Schema changes are treated as code and evolve alongside application logic, ensuring consistency across environments.

---

## Containerization

The service is packaged as a Docker image using **multi-stage builds**.

### Goals
- Minimal runtime image size
- Fast startup time
- Reproducible and deterministic builds

The resulting container image runs unchanged across **local, staging, and production** environments.

---

## Kubernetes Readiness

The application is Kubernetes-native by design.

### Features
- Liveness and readiness probes via Spring Boot Actuator
- Configuration through environment variables
- Stateless pods with externalized persistence

Stateful concerns are delegated to managed services (e.g. databases) or Kubernetes primitives such as PersistentVolumeClaims where applicable.

---

## Design Decisions

### Why Java & Spring Boot?
- Mature and battle-tested ecosystem
- Strong typing and validation guarantees
- Excellent observability, tooling, and community support

### Why a relational database?
- Strong consistency guarantees
- Powerful and expressive querying
- Clear data ownership and lifecycle

### Why Flyway instead of auto-DDL?
- Predictable and explicit schema evolution
- Full control over migration order and behavior
- Production-safe database changes

---

## Failure Modes & Resilience

| Scenario               | Handling                          |
|------------------------|-----------------------------------|
| Database unavailable   | Pod restart and retry             |
| Partial writes         | Transactional boundaries          |
| Schema mismatch        | Migration-first startup           |
| Pod restart            | Stateless recovery                |

---

## Summary

This backend service provides a **robust, cloud-native foundation** for telemetry persistence and access. By combining a clean layered architecture, relational data modeling, and container-first deployment practices, it delivers predictable behavior, scalability, and long-term maintainability.
