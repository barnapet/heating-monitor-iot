# 🚀 Heating Monitor IoT – Enterprise DevOps Upgrade Roadmap

**Project:** Heating Monitor IoT
**Current Version:** v1.0.0 (Serverless MVP - Python/AWS Lambda)
**Goal:** Enhance the existing system with a Hybrid Cloud architecture to demonstrate modern DevOps competencies (Java, K8s, IaC, CI/CD).

---

## 📅 Phase 0: Foundation & Version Control
**Focus:** Safely preparing the development environment without compromising existing "Production" code.

- [x] **Gitflow Setup:** Create `develop` and `feature/java-backend` branches to protect `main`.
- [x] **Monorepo Config:** Update `.gitignore` (support for Java + Python in one place).
- [x] **Java Skeleton:** Initialize Spring Boot 3.x project (Maven, Java 17/21).
- [x] **Health Check:** Implement `Actuator` and a basic REST endpoint.
- [x] **Documentation:** Create `ROADMAP.md`.

**✅ Definition of Done:** Project compiles (`mvn clean package`), the `main` branch is untouched, and the repo structure is clean.

---

## 🐳 Phase 1: Containerization
**Focus:** Ensuring environment-agnostic execution ("Build once, run anywhere").

- [x] **Dockerfile (Java):** Create a multi-stage build (Build: Maven image, Run: Distroless or Alpine JRE).
- [x] **Optimization:** Layer caching and image size optimization.
- [x] **Docker Compose (Dev):** Setup local development environment (Java App + Environment variables).
- [ ] **Edge Docker (Optional):** Containerize Raspberry Pi Python code for testing purposes.

**✅ Definition of Done:** The `docker compose up` command starts the full stack, and the Java API responds to `localhost:8080/actuator/health`.

---

## ☸️ Phase 2: Kubernetes Orchestration
**Focus:** Scalability and manageability.

- [x] **Local Cluster:** Setup Minikube or Kind (Kubernetes in Docker).
- [x] **K8s Manifests:**
    - `Deployment.yaml` (ReplicaSet, Resources limits).
    - `Service.yaml` (ClusterIP/NodePort).
    - `Ingress.yaml` (Optional).
- [x] **Helm Chart:** Templatize manifests, use `values.yaml` for configuration.

**✅ Definition of Done:** Application installs via `helm install`, Pods reach `Running` status, and the service is accessible.

---

## 💾 Phase 3: Database & Persistence (Stateful Workloads)
**Focus:** Managing data in a containerized environment.

- [x] **PostgreSQL Setup:** Add Postgres container to Docker Compose and Helm Chart.
- [x] **Secrets Management:** Use K8s Secrets for passwords (avoid hardcoding).
- [x] **Persistence:** Configure PersistentVolume (PV) and PersistentVolumeClaim (PVC) to prevent data loss.
- [x] **Java Integration:** Integrate Spring Data JPA, create Entity model for reports.

**✅ Definition of Done:** Java app successfully reads/writes to the DB, and data persists after a Pod restart.

---

## 🔄 Phase 4: Advanced CI/CD
**Focus:** Automation, Quality Assurance, and Delivery.

- [x] **GitHub Actions (Java):** Create workflow for Java Build and Unit Test execution with Maven.
- [x] **Integration Testing:** Use **Service Containers** (PostgreSQL) within GitHub Actions for real DB testing.
- [x] **Docker Build & Push:** Automatic multi-stage image build and push to **GitHub Container Registry (GHCR)**.
- [x] **Pipeline Optimization:** Implemented Path Filtering (Monorepo support) to save resources.

**✅ Definition of Done:** Every `git push` triggers tests, and successful builds are published to GHCR.

---

## 🛠 Tech Stack Summary
* **Language:** Java 17+ (Spring Boot 3), Python 3.9+
* **Build Tool:** Maven
* **Container:** Docker (Multi-stage)
* **Orchestration:** Kubernetes, Helm
* **Database:** PostgreSQL, AWS DynamoDB (Legacy/Edge)
* **CI/CD:** GitHub Actions
* **Cloud:** AWS (IoT Core, Lambda)
