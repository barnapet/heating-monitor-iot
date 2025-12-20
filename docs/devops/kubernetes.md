# Kubernetes Deployment – Helm Charts

## Audience
- DevOps Engineers
- Platform Engineers
- Cloud Architects

---

## Role in the System

The Helm charts define how the backend service and its dependencies are deployed into a Kubernetes cluster.

This layer is responsible for:
- Declarative infrastructure definition
- Environment-specific configuration
- Repeatable and predictable deployments

Helm acts as the bridge between **application code** and **runtime infrastructure**, enabling consistent deployments across environments.

---

## Chart Structure

The chart follows standard Helm conventions:

- `Chart.yaml` – chart metadata and versioning
- `values.yaml` – default and overridable configuration
- `templates/` – Kubernetes resource templates

All environment-specific settings are externalized via values files, allowing the same chart to be reused across **local, staging, and production** environments.

---

## Deployment Model

### Backend Service

- Deployed as a **stateless Kubernetes Deployment**
- Horizontally scalable via replica count
- Configuration injected through environment variables

### Database

- PostgreSQL deployed as a **stateful workload**
- PersistentVolumeClaims (PVCs) ensure data durability
- Database lifecycle decoupled from application pods

This separation guarantees that application restarts or redeployments do **not impact persisted data**.

---

## Configuration Management

Configuration is managed using Helm values and native Kubernetes primitives:

- Environment variables for application configuration
- Kubernetes Secrets for sensitive data (credentials, tokens)
- Clear separation between code, configuration, and secrets

This approach aligns with **Twelve-Factor App** principles and supports secure, environment-specific customization.

---

## Image Management

The Helm chart supports flexible container image strategies:

- Explicit image tags for reproducibility
- Configurable image pull policies
- Compatibility with:
  - Local registries (e.g. Minikube)
  - Remote registries (e.g. GitHub Container Registry)

This enables fast local iteration while remaining fully production-ready.

---

## Health & Lifecycle Management

The backend integrates tightly with Kubernetes lifecycle mechanisms:

- **Liveness probes** detect and recover from unhealthy containers
- **Readiness probes** control traffic routing to pods
- Rolling updates provide **zero-downtime deployments**

These mechanisms allow Kubernetes to manage application health autonomously with minimal operational intervention.

---

## Design Decisions

### Why Helm instead of raw manifests?
- Parameterized, reusable deployments
- Reduced YAML duplication
- Easier environment management

### Why a single chart?
- Simpler dependency management
- Clear ownership boundaries
- Easier onboarding for new contributors

### Trade-offs
- Slightly higher abstraction cost
- Requires Helm-specific knowledge

For this project’s scope, the benefits clearly outweigh the added complexity.

---

## Failure Modes & Recovery

| Scenario              | Handling                    |
|-----------------------|-----------------------------|
| Pod crash             | Automatic restart           |
| Node failure          | Pod rescheduling            |
| Application upgrade   | Rolling update              |
| Database pod restart  | PVC-backed recovery         |

---

## Summary

The Helm-based Kubernetes deployment provides a **robust, repeatable, and environment-agnostic** deployment strategy. By combining declarative configuration, stateless application design, and Kubernetes-native health management, it ensures reliable operation across the full application lifecycle.

