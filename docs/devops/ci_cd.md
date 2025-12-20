# CI/CD Pipeline – Automated Build, Test & Delivery

## Audience
- DevOps Engineers
- Platform Engineers
- Tech Leads

---

## Role in the System

The CI/CD pipeline ensures that every change to the codebase is **automatically built, tested, and packaged** into a deployable artifact.

It enforces quality gates and provides fast feedback, enabling **safe, repeatable, and auditable delivery** across all environments.

---

## Pipeline Overview

The pipeline is implemented using **GitHub Actions** and is triggered on:

- Pull requests
- Pushes to the `main` branch

### High-level stages
1. Build & test
2. Container image creation
3. Image publishing

Each stage produces **immutable artifacts** that can be promoted consistently across environments.

---

## Build & Test

The backend service is built using the **Maven lifecycle**.

### Testing strategy
- Unit tests executed during the standard build phase
- Integration tests running against a temporary **PostgreSQL service container**

This approach validates real database interactions while remaining fully self-contained and independent of external infrastructure.

---

## Container Image Pipeline

After successful tests, the application is packaged into a Docker image.

### Key characteristics
- Deterministic and reproducible builds
- Explicit, versioned image tags
- No mutable `latest` dependency in production workflows

Built images are published to **GitHub Container Registry (GHCR)**.

---

## Security & Quality Gates

The pipeline enforces multiple quality and safety guarantees:

- All tests must pass before image creation
- Images are immutable once published
- Build artifacts are reproducible from source

These controls reduce the risk of configuration drift, hidden state, and environment-specific behavior.

---

## Deployment Integration

The CI/CD pipeline integrates cleanly with Kubernetes-based deployments:

- Helm charts reference **explicit image tags**
- Image promotion is decoupled from deployment execution
- The same image can be deployed across multiple environments

This separation enables controlled rollouts, progressive delivery, and reliable rollback strategies.

---

## Design Decisions

### Why GitHub Actions?
- Native integration with GitHub repositories
- Declarative, version-controlled workflows
- No external CI infrastructure required

### Why container-based integration testing?
- High environment parity
- Reduced “works on my machine” issues
- Faster and more reliable feedback loops

### Why immutable images?
- Predictable and repeatable deployments
- Simple and safe rollback via image tags
- Strong auditability and traceability

---

## Failure Modes & Feedback

| Scenario           | Handling                         |
|--------------------|----------------------------------|
| Test failure       | Pipeline stops immediately       |
| Build error        | No artifact published            |
| Registry outage   | Deployment blocked               |
| Deployment issue  | Rollback via previous image tag  |

---

## Summary

This CI/CD pipeline provides a **robust, automated delivery backbone** for the system. By combining strong test coverage, immutable container artifacts, and