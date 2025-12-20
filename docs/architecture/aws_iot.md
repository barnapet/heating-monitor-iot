# AWS IoT Layer – Secure Event Ingestion & Routing

## Audience
- Cloud Engineers
- DevOps Engineers
- Solution Architects

---

## Role in the System

AWS IoT Core acts as the **central ingestion and routing layer** between edge devices and cloud services.

It provides:
- Secure device authentication
- Scalable MQTT message ingestion
- Event‑driven routing to downstream services

This layer **decouples edge devices from backend implementations**, enabling independent evolution and scaling of both sides.

---

## Secure Device Connectivity

Each edge device is registered as an **AWS IoT Thing** and authenticated using:

- **X.509 certificates**
- **TLS 1.2 encrypted connections**
- **Fine‑grained IoT policies**

This approach ensures:
- Strong device‑level identity
- Least‑privilege access control
- No shared credentials between devices

Certificate‑based authentication was chosen over token‑based mechanisms to align with AWS IoT best practices and support long‑lived, unattended device deployments.

---

## MQTT Topic Design

The system uses a structured MQTT topic hierarchy:

```text
home/heating/status
```

### Design considerations
- Clear semantic meaning
- Event‑driven communication (state changes, not polling)
- Easy filtering via IoT Rules

Messages represent **state transitions** rather than raw sensor signals, significantly reducing downstream processing complexity.

---

## IoT Rules Engine

AWS IoT Rules are used to route messages to downstream services **without custom MQTT consumers**.

---

### Hot Path – Real‑Time Alerting

- **Rule condition:** `status = 'INACTIVE'`
- **Action:** Invoke AWS Lambda
- **Purpose:** Immediate user notification

This path prioritizes **low latency** and **operational awareness**.

---

### Cold Path – Storage & Analytics

- **Rule condition:** All messages
- **Action:** Persist to Amazon DynamoDB
- **Purpose:** Historical analysis and ML readiness

Separating hot and cold paths avoids coupling alerting logic with long‑term storage and analytics concerns.

---

## Serverless Integration

AWS Lambda functions are triggered directly by IoT Rules.

### Responsibilities
- Message validation
- Notification formatting
- Integration with external services:
  - Telegram Bot API
  - Discord Webhooks

This keeps the IoT layer lightweight and prevents business logic from being embedded directly into routing rules.

---

## Data Persistence Strategy

Raw events are stored in **Amazon DynamoDB** as immutable records.

### Rationale
- Low‑latency writes
- Fully serverless scaling
- Natural fit for event‑based data models

The DynamoDB table serves as a **source of truth** for:
- Historical analysis
- Future ML pipelines
- System observability and auditing

---

## Design Decisions

### Why AWS IoT Core instead of a REST API?
- Native MQTT support
- Built‑in device security
- Managed horizontal scalability
- Rule‑based routing without custom infrastructure

### Why IoT Rules instead of custom consumers?
- Declarative, configuration‑driven routing
- Reduced operational overhead
- Easier evolution of downstream integrations

### Why DynamoDB for raw events?
- Append‑only event model
- Cost‑efficient at low to medium scale
- No schema migration overhead for raw telemetry

---

## Failure Modes & Resilience

| Scenario               | Handling                               |
|------------------------|----------------------------------------|
| Network interruption   | MQTT reconnect and retry               |
| Duplicate messages     | At‑least‑once delivery tolerated       |
| Lambda failure         | Automatic retry via IoT Rules          |
| Downstream outage      | Hot and cold paths isolated            |

---

## Summary

The AWS IoT layer provides a **secure, scalable, and event‑driven backbone** for the system. By combining certificate‑based device identity, MQTT messaging, declarative routing, and serverless integrations, it enables reliable real‑time alerting while preserving clean separation between ingestion, processing, and storage.

