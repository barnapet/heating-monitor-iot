# 💡 Design Decisions and Rationale

This document details the critical architectural choices made for the AWS IoT Boiler Monitor pipeline, focusing on security, cost-efficiency, and fault tolerance.

## 1. Edge Ingestion Protocol (MQTT vs. HTTPS)

| Decision | Rationale |
| :--- | :--- |
| **Protocol:** MQTT (using AWS IoT Device SDK) | MQTT is a **lightweight** protocol, ideal for low-power edge devices like the Raspberry Pi Zero 2 W and unreliable network conditions (e.g., in a basement/boiler room). It significantly reduces bandwidth usage compared to HTTPS. |
| **Quality of Service (QoS):** QoS 1 | QoS 1 (At Least Once) is implemented to ensure that status change messages, which are critical for alerting, are **not lost** if the device briefly loses its Wi-Fi connection. |
| **Authentication:** X.509 Certificates | Status reporting is secured using device certificates (X.509) managed by AWS IoT Core, preventing unauthorized devices from injecting data into the system. |

## 2. Hot Path Architecture (Alerting)

The Hot Path is designed for **real-time alerting** with minimal latency.

| Decision | Rationale |
| :--- | :--- |
| **Architecture:** Event-Driven (IoT Rule $\rightarrow$ Lambda) | This approach is more **cost-effective** and **faster** than traditional polling mechanisms. The AWS Lambda function only executes (and costs money) when the critical `status = 'INACTIVE'` event is triggered, adhering to the Free Tier constraints. |
| **Notification Channel:** Telegram API | A third-party API is used via Lambda to send **free** push notifications, avoiding the recurring costs associated with SMS and the development complexity of native mobile push (SNS Mobile Push). |
| **Security:** Environment Variables & KMS | Sensitive secrets (e.g., Telegram Bot Token) are stored as encrypted **Environment Variables** in Lambda, preventing hardcoded credentials in the source code. |
| **Fault Tolerance (DLQ):** SQS Dead Letter Queue (DLQ) | An SQS queue is configured as the Lambda function's DLQ. If the Lambda fails repeatedly (e.g., Telegram API is down), the message is routed to the DLQ for manual inspection and reprocessing, ensuring no critical alert is missed. |

## 3. Cold Path Architecture (Storage and Analytics)

The Cold Path is dedicated to durable data storage for future analytics and machine learning tasks.

| Decision | Rationale |
| :--- | :--- |
| **Database:** Amazon DynamoDB (On-Demand Mode) | Chosen for its **low-latency read/write access** and **flexible schema** to store status events. **On-Demand** mode is selected to minimize recurring costs; we only pay for the exact read/write capacity consumed, ideal for a sporadic IoT workload. |
| **Partition & Sort Keys:** `device_id` (PK) + `timestamp` (SK) | This composite key design optimizes for time-series queries (e.g., "Show all events for device X in the last 24 hours") and ensures event uniqueness. |
| **Cost Optimization:** Time To Live (TTL) | A **TTL policy** is enabled on the DynamoDB table based on the `timestamp` attribute. This automatically prunes records older than a defined retention period (e.g., 3 years), reducing storage costs and maintaining data hygiene without requiring manual intervention. |

## 4. Infrastructure Delivery

| Decision | Rationale |
| :--- | :--- |
| **Delivery Method:** AWS Cloud Development Kit (CDK) in Python | CDK is used to define and deploy the entire AWS cloud infrastructure **as code**. This ensures the infrastructure is **version-controlled**, reproducible, and easily updated, aligning with modern DevOps and MLOps practices. |