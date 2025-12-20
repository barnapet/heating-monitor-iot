# Heating Monitor IoT
### End-to-End Edge-to-Cloud Heating Monitoring Platform

---

## One-Sentence Overview

A production-grade IoT reference project demonstrating end-to-end ownership of an edge-to-cloud system, from physical signal detection to a Kubernetes-deployed, cloud-native backend.

---

## Why This Project Exists

This project solves a real-world engineering problem: **detecting the operational state of a solid-fuel boiler without modifying the boiler itself**.

Instead of invasive sensors or control-system changes, the system relies on **non-intrusive electrical signal detection at the edge**, combined with **secure cloud ingestion** and a **scalable backend architecture**.

The goal of the project is not a demo application, but a **production-oriented reference system** that reflects real engineering trade-offs, constraints, and best practices.

---

## What This Project Demonstrates

This project demonstrates the ability to:

- Design and implement an **end-to-end distributed system**
- Own the full lifecycle from **hardware-adjacent edge logic** to **cloud and platform layers**
- Apply **cloud-native principles** in a pragmatic way
- Build systems that are **secure, observable, and operable**

It is intentionally structured the way a real production system would be.

---

## High-Level Architecture

The system is composed of clearly separated layers:

- **Edge Layer** – Safe, opto-isolated detection of boiler activity using pump power state
- **Cloud Ingestion Layer** – Secure, certificate-based MQTT ingestion via AWS IoT Core
- **Backend Service** – Java-based REST API acting as the system of record for telemetry
- **Platform Layer** – Kubernetes deployment using Helm, with automated CI/CD

Each layer can evolve independently, reflecting real-world system design.

---

## Key Engineering Highlights

- Non-intrusive hardware design (no boiler modification)
- Per-device identity using X.509 certificates and TLS
- Event-driven architecture with clear hot and cold data paths
- Cloud-native backend with explicit data ownership
- Kubernetes-ready deployment model
- Fully automated CI/CD pipeline with immutable artifacts

---

## Technology Stack (Summary)

- **Edge:** Raspberry Pi Zero 2 W, Python
- **Cloud:** AWS IoT Core, AWS Lambda, DynamoDB
- **Backend:** Java 17, Spring Boot, PostgreSQL, Flyway
- **Platform:** Docker, Kubernetes, Helm
- **CI/CD:** GitHub Actions, GitHub Container Registry

---

## Security Model (High-Level)

- Edge devices authenticate using **unique X.509 certificates**
- All communication is encrypted using **TLS**
- No shared credentials between devices
- Backend services are isolated from direct device access
- Least-privilege principles applied across cloud and platform layers

---

## How This Project Is Used

This repository is intended as:

- A **technical portfolio project** for senior backend, cloud, or platform roles
- A reference architecture for **event-driven IoT systems**
- A demonstration of **production-oriented engineering practices**

Individual components can be run and evaluated independently; detailed technical documentation is provided per layer.

---

## Project Documentation

Each major subsystem is documented separately for clarity:

- **Edge Layer:** Hardware sensing and edge logic
- **AWS IoT Layer:** Secure ingestion and event routing
- **Backend Service:** Java API, persistence, and data modeling
- **Kubernetes Deployment:** Helm charts and runtime configuration
- **CI/CD Pipeline:** Automated build, test, and delivery

---

## Future Improvements

If extended further, the system could evolve toward:

- Anomaly detection on heating cycles
- Advanced observability dashboards
- Cost optimization and data lifecycle policies
- Fleet-level device management

---

## About This Project

This project was designed and implemented as a **personal, production-oriented reference system** to demonstrate senior-level ownership of cloud-native, distributed architectures.

