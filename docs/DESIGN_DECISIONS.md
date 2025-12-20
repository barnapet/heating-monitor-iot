# 💡 Design Decisions and Rationale

### 1. Edge Ingestion Protocol (MQTT vs. HTTPS)

| Decision | Rationale |
| :--- | :--- |
| **Protocol:** MQTT (using AWS IoT Device SDK) | MQTT is a **lightweight** protocol, ideal for low-power edge devices like the Raspberry Pi Zero 2 W and unreliable network conditions (e.g., in a basement/boiler room). It significantly reduces bandwidth usage compared to HTTPS. |
| **Quality of Service (QoS):** QoS 1 | QoS 1 (At Least Once) is implemented to ensure that status change messages, which are critical for alerting, are **not lost** if the device briefly loses its Wi-Fi connection. |
| **Authentication:** X.509 Certificates | Status reporting is secured using device certificates (X.509) managed by AWS IoT Core, preventing unauthorized devices from injecting data into the system. |
| **Edge Reliability:** **Offline Queueing / Persistence** | **The MQTT client is configured to persistently store status messages locally on the device's disk when network connectivity is lost.** |
| **Edge Protocol:** **Pipelined Publish** | **Optimizes the transmission efficiency and ensures the correct chronological order of status messages when the device reconnects after being offline.** |

### 2. Hot Path Architecture (Alerting)

The Hot Path is designed for **real-time alerting** with minimal latency.

| Decision | Rationale |
| :--- | :--- |
| **Architecture:** Event-Driven (IoT Rule $\rightarrow$ Lambda) | This approach is more **cost-effective** and **faster** than traditional polling mechanisms. The AWS Lambda function only executes (and costs money) when the critical `status = 'INACTIVE'` event is triggered, adhering to the Free Tier constraints. |
| **Notification System:** **Multi-channel Notification Interface** | **The system implements an Abstract Notification Interface (Strategy Pattern) supporting both Telegram and Discord.** This design adheres to the **Open/Closed Principle**, allowing the system to be easily extended with new channels (e.g., Slack, Email) without modifying the core business logic. It also provides redundancy: if one API fails, the others can still deliver the alert. |
| **Security:** Environment Variables (SSM) & KMS | Sensitive secrets (Telegram Bot Token, Chat ID, Discord Webhook URL) are injected as **Environment Variables** (retrieved from SSM Parameter Store) into Lambda, preventing hardcoded credentials in the source code. |
| **Fault Tolerance (DLQ):** SQS Dead Letter Queue (DLQ) | An SQS queue is configured as the Lambda function's DLQ. If the Lambda fails repeatedly (e.g., an external API is down), the message is routed to the DLQ for manual inspection and reprocessing, ensuring no critical alert is missed. |
| **Lambda Retry Policy:** **Retry Policy set to 3 attempts** | **Standard retry count to account for transient errors before moving the message to the DLQ. Configured via the CDK `on_failure` property.** |

### 3. Cold Path Architecture (Storage and Analytics)

The Cold Path is dedicated to durable data storage for future analytics and machine learning tasks.

| Decision | Rationale |
| :--- | :--- |
| **Database:** Amazon DynamoDB (On-Demand Mode) | Chosen for its **low-latency read/write access** and **flexible schema** to store status events. **On-Demand** mode is selected to minimize recurring costs; we only pay for the exact read/write capacity consumed, ideal for a sporadic IoT workload. |
| **Partition & Sort Keys:** `device_id` (PK) + `timestamp` (SK) | This composite key design optimizes for time-series queries (e.g., "Show all events for device X in the last 24 hours") and ensures event uniqueness. |
| **Cost Optimization:** Time To Live (TTL) | A **TTL policy** is enabled on the DynamoDB table based on the `timestamp` attribute. This automatically prunes records older than a defined retention period (e.g., 3 years), reducing storage costs and maintaining data hygiene without requiring manual intervention. |

### 4. Infrastructure Delivery

| Decision | Rationale |
| :--- | :--- |
| **Delivery Method:** AWS Cloud Development Kit (CDK) in Python | CDK is used to define and deploy the entire AWS cloud infrastructure **as code**. This ensures the infrastructure is **version-controlled**, reproducible, and easily updated, aligning with modern DevOps and MLOps practices. |

### 5. Architecture Evolution & Refactoring Log

This section tracks significant architectural changes and the context behind them.

| Date | Change | Driver / Context | Status |
| :--- | :--- | :--- | :--- |
| **2025-11-26** | **Initial Design** | Initial Serverless IoT architecture using direct Telegram API integration for alerting. | *Superseded* |
| **2025-12-09** | **Notification Interface & Multi-Channel Support** | **Refactored the alerting logic to use an Abstract Interface.** Added Discord Webhook support alongside Telegram. This decoupling improves code maintainability and allows for future channel expansions without risking core logic stability. | **Active** |
| **2025-12-10** | **Hybrid Cloud Expansion (v2.0)** | **Enterprise DevOps Demo:** Added a Java Spring Boot microservice (Reporting API) and PostgreSQL on Kubernetes. The goal is to demonstrate management of stateful workloads, container orchestration, and hybrid networking alongside the existing Serverless ingestion path. | **Completed** |
| **2025-12-20** | **Resilience Hardening (v2.1)** | **Integrated Resilience4j to protect the Hot Path.** Added Circuit Breaker and Rate Limiter patterns to handle potential downstream latency or outages from Telegram/Discord APIs. | **In Progress** |

### 6. Enterprise Backend Upgrade (v2.0 Decisions)

With the shift to v2.0, the system introduces a containerized backend to demonstrate cloud-agnostic engineering.

| Decision | Rationale |
| :--- | :--- |
| **Runtime:** Java 17 + Spring Boot 3 | Selected for its **strict typing**, robust ecosystem, and dominance in enterprise environments. Unlike the Python scripts used at the edge, Java provides better maintainability for complex business logic and data modeling in large-scale teams. |
| **Orchestration:** Kubernetes (K8s) | Replaced AWS Lambda for the backend API to achieve **provider independence** (No Vendor Lock-in). This demonstrates how the workload can run on AWS EKS, Azure AKS, or on-premise hardware without code changes. |
| **Persistence:** PostgreSQL (Relational) | While DynamoDB (NoSQL) is excellent for raw event ingestion (Cold Path), PostgreSQL was introduced to handle **structured data** and complex queries, representing a typical "Polyglot Persistence" architecture found in enterprise systems. |
| **Migration:** Flyway | Adopted **Schema-as-Code** principles. Unlike DynamoDB's schema-less nature, the relational model requires strict version control for database structures to ensure reproducible deployments across environments. |

### 7. System Resilience & Stability (v2.1 Decisions)

As the system evolved into an enterprise-grade backend, ensuring stability during partial failures became a priority.

| Decision | Rationale |
| :--- | :--- |
| **Fault Tolerance Library:** Resilience4j | Chosen over legacy Netflix Hystrix for its lightweight, modular design, better support for Java 17+, and seamless integration with the Spring Boot 3 ecosystem. |
| **Pattern:** Circuit Breaker | Implemented on the `NotificationService` to prevent cascading failures. If external APIs (Discord/Telegram) fail or time out, the circuit opens to protect the backend resources and trigger fallback mechanisms. |
| **Pattern:** Rate Limiter | Applied to prevent the system from being throttled by external API providers during high-frequency event bursts (e.g., rapid boiler state oscillations). |
| **Fallback Strategy:** Graceful Degradation | In case of notification failure, the system is designed to log the event as a "Critical Warning" and ensure the Cold Path (Persistence) remains unaffected. |
