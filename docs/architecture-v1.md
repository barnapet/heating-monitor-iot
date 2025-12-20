# Early Architecture – AWS IoT Edge Pipeline (v1)

> **Context**  
> This document captures the initial architecture and design decisions of the first iteration of the project.  
> It focuses on the AWS IoT–centric, event-driven pipeline that formed the foundation of the system before the later introduction of a Kubernetes-based backend.

---

## Project Overview

This early version of the project focuses on building a **reliable and cost-efficient IoT solution** for monitoring a dual home heating system.

The primary engineering goal was to **detect the operational state of a solid-fuel boiler without modifying the boiler itself**, by observing the power status of its circulation pump. This approach enables:

- Safe, non-intrusive detection
- Real-time alerting
- Historical data collection for later analysis

---

## Key Engineering Goals

- Non-invasive boiler state detection
- Event-driven architecture
- Secure device-to-cloud communication
- Low operational complexity
- Clear separation between edge and cloud responsibilities

---

## Architecture Design (System Design – v1)

The system was designed as an **event-driven IoT pipeline** built around **AWS IoT Core**.

The edge device publishes boiler state changes in real time using MQTT. Incoming events are routed through AWS IoT Rules to downstream services, enabling both immediate notifications and long-term data persistence.

```mermaid
flowchart TD
    subgraph Edge_Layer [Edge Layer – Home]
        Pump[Solid-Fuel Boiler Pump (230V AC)] -- 230V AC --> Opto[MVPDM-1PHS Opto-Isolated Module]
        Opto -- 3.3V Logic --> Pi[Raspberry Pi Zero 2 W]
        Pi -- "Python (AWS IoT SDK)" --> MQTT_Out(MQTT Topic: home/heating/status)
    end

    subgraph AWS_Cloud [AWS Cloud]
        IoT[AWS IoT Core]
        MQTT_Out -.-> |TLS 1.2 / X.509| IoT

        subgraph Hot_Path [Hot Path – Real-Time Alerting]
            Rule_Alert{IoT Rule: status = 'INACTIVE'}
            Lambda[AWS Lambda – Notification Service]
            Telegram_API[Telegram Bot API]
            Discord_API[Discord Webhook]
        end

        subgraph Cold_Path [Cold Path – Event Storage]
            Rule_Store{IoT Rule: All Messages}
            DynamoDB[(Amazon DynamoDB)]
        end

        IoT --> Rule_Alert
        IoT --> Rule_Store

        Rule_Alert --> Lambda
        Lambda --> Telegram_API
        Lambda --> Discord_API

        Rule_Store --> DynamoDB
    end
```

---

## Technology Stack (v1)

| Category | Technology | Purpose |
|--------|-----------|---------|
| Edge Compute | Raspberry Pi Zero 2 W | Runs the edge monitoring logic |
| Edge Sensing | MVPDM-1PHS | Opto-isolated detection of 230V AC pump power |
| Programming | Python 3.11+ | Edge logic, Lambda handlers |
| Cloud Ingestion | AWS IoT Core | Secure MQTT broker and rules engine |
| Serverless | AWS Lambda | Stateless notification processing |
| Alerting | Telegram, Discord | Multi-channel user notifications |
| Storage | Amazon DynamoDB | Append-only storage of boiler state events |
| IaC / DevOps | AWS CDK, GitHub Actions | Infrastructure provisioning and automation |

---

## Design Characteristics

- **Binary signal detection** instead of noisy sensor telemetry
- **Certificate-based device authentication** (X.509)
- **Event-driven routing** using managed cloud services
- **Hot and cold data paths** separated from the start

---

## Limitations of This Version

This early architecture intentionally focused on simplicity and rapid validation. As a result:

- Long-term analytics capabilities were limited
- No dedicated backend API existed
- Data modeling was constrained by the raw event store

These limitations directly informed the next iteration of the system.

---

## Evolution Beyond v1

Later versions of the project introduced:

- A dedicated, cloud-native backend service (Java, PostgreSQL)
- Kubernetes-based deployment with Helm
- A structured system-of-record separate from raw events
- A full CI/CD pipeline with immutable artifacts

These evolutions are documented in the main project README and subsequent architecture documents.

---

## Why This Document Is Kept

This document is preserved intentionally to:

- Show the **evolution of system design**
- Demonstrate early architectural reasoning
- Provide context for later design decisions

Maintaining design history reflects a **production-oriented engineering mindset**, rather than a throwaway prototype approach.