# 🚀 Heating Monitor IoT – Enterprise DevOps Upgrade Roadmap

**Project:** Heating Monitor IoT
**Current Version:** v1.0.0 (Serverless MVP - Python/AWS Lambda)
**Goal:** Enhance the existing system with a Hybrid Cloud architecture to demonstrate modern DevOps competencies (Java, K8s, IaC, CI/CD).

---

## 📅 Phase 0: Foundation & Version Control
**Focus:** Safely preparing the development environment without compromising existing "Production" code.

- [ ] **Gitflow Setup:** Create `develop` and `feature/java-backend` branches to protect `main`.
- [ ] **Monorepo Config:** Update `.gitignore` (support for Java + Python in one place).
- [ ] **Java Skeleton:** Initialize Spring Boot 3.x project (Maven, Java 17/21).
- [ ] **Health Check:** Implement `Actuator` and a basic REST endpoint.
- [ ] **Documentation:** Create `ROADMAP.md`.

**✅ Definition of Done:** Project compiles (`mvn clean package`), the `main` branch is untouched, and the repo structure is clean.

---

## 🐳 Phase 1: Containerization
**Focus:** Ensuring environment-agnostic execution ("Build once, run anywhere").

- [ ] **Dockerfile (Java):** Create a multi-stage build (Build: Maven image, Run: Distroless or Alpine JRE).
- [ ] **Optimization:** Layer caching and image size optimization.
- [ ] **Docker Compose (Dev):** Setup local development environment (Java App + Environment variables).
- [ ] **Edge Docker (Optional):** Containerize Raspberry Pi Python code for testing purposes.

**✅ Definition of Done:** The `docker compose up` command starts the full stack, and the Java API responds to `localhost:8080/actuator/health`.

---

## ☸️ Phase 2: Kubernetes Orchestration
**Focus:** Scalability and manageability.

- [ ] **Local Cluster:** Setup Minikube or Kind (Kubernetes in Docker).
- [ ] **K8s Manifests:**
    - `Deployment.yaml` (ReplicaSet, Resources limits).
    - `Service.yaml` (ClusterIP/NodePort).
    - `Ingress.yaml` (Optional).
- [ ] **Helm Chart:** Templatize manifests, use `values.yaml` for configuration.

**✅ Definition of Done:** Application installs via `helm install`, Pods reach `Running` status, and the service is accessible.

---

## 💾 Phase 3: Database & Persistence (Stateful Workloads)
**Focus:** Managing data in a containerized environment.

- [ ] **PostgreSQL Setup:** Add Postgres container to Docker Compose and Helm Chart.
- [ ] **Secrets Management:** Use K8s Secrets for passwords (avoid hardcoding).
- [ ] **Persistence:** Configure PersistentVolume (PV) and PersistentVolumeClaim (PVC) to prevent data loss.
- [ ] **Java Integration:** Integrate Spring Data JPA, create Entity model for reports.

**✅ Definition of Done:** Java app successfully reads/writes to the DB, and data persists after a Pod restart.

---

## 🔄 Phase 4: Advanced CI/CD & Security
**Focus:** Automation and Quality Assurance.

- [ ] **GitHub Actions (Java):** Create new workflow for Java Build and Unit Test execution.
- [ ] **Docker Build & Push:** Automatic image build and push (e.g., to GitHub Container Registry - GHCR).
- [ ] **Security Scanning:** Integrate Trivy or similar scanner into the pipeline (Vulnerability check).
- [ ] **Helm Lint:** Validate Chart during the pipeline process.

**✅ Definition of Done:** Every `git push` to the feature branch automatically triggers tests and security checks.

---

## 🛠 Tech Stack Summary
* **Language:** Java 17+ (Spring Boot 3), Python 3.9+
* **Build Tool:** Maven
* **Container:** Docker (Multi-stage)
* **Orchestration:** Kubernetes, Helm
* **Database:** PostgreSQL, AWS DynamoDB (Legacy/Edge)
* **CI/CD:** GitHub Actions
* **Cloud:** AWS (IoT Core, Lambda)