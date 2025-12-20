# 💰 Cloud Cost Estimation & Capacity Planning

## Purpose
This document provides a breakdown of the operational costs for the Heating Monitor system. It compares the **Serverless (v1)** architecture against the **Containerized (v2)** architecture to highlight the trade-offs between "Pay-as-you-go" efficiency and "Enterprise" portability.

---

## 📉 Scenario A: Serverless Production (v1.0 Architecture)
*Optimized for: Home use, Low cost, Low maintenance.*

In this scenario, the system runs purely on AWS managed services (IoT Core, Lambda, DynamoDB).

| Service | Metric | Est. Usage / Month | Unit Cost (eu-central-1) | Monthly Cost |
| :--- | :--- | :--- | :--- | :--- |
| **AWS IoT Core** | Connectivity | 24/7 Connection | Free Tier (12 mo) | $0.00 |
| **AWS IoT Core** | Messages | ~45,000 msgs (1/min) | $1.00 / million | $0.05 |
| **AWS Lambda** | Invocations | ~100 alerts (Hot path) | Free Tier | $0.00 |
| **DynamoDB** | Write Units | On-Demand | $1.25 / million | $0.06 |
| **DynamoDB** | Storage | < 1 GB | Free Tier | $0.00 |
| **Secrets Manager**| Secrets | 3 Secrets | $0.40 / secret | $1.20 |
| **Total** | | | | **~$1.31 / month** |

**Verdict:** Extremely cost-efficient for individual deployments. The cost is negligible.

---

## 📈 Scenario B: Enterprise Kubernetes (v2.0 Architecture)
*Optimized for: Scalability, Portability, High Availability.*

In this scenario, we deploy the v2.0 stack (Java Backend + Postgres) into a managed Kubernetes environment (AWS EKS).

| Service | Metric | Configuration | Unit Cost | Monthly Cost |
| :--- | :--- | :--- | :--- | :--- |
| **EKS Control Plane** | Cluster | 1 Cluster | $0.10 / hour | $72.00 |
| **EC2 Worker Nodes** | Compute | 2x t3.medium (HA) | ~$30.00 / node | $60.00 |
| **ELB (Load Balancer)** | Ingress | 1 Application LB | ~$18.00 / month | $18.00 |
| **EBS Storage** | PVC (DB) | 10 GB gp3 | $0.08 / GB | $0.80 |
| **ECR Registry** | Storage | 1 GB | $0.10 / GB | $0.10 |
| **Total** | | | | **~$150.90 / month** |

**Verdict:** The "Enterprise" stack carries a significant base cost (Control Plane + Compute).
* **For a Production Enterprise:** This is acceptable for a system handling thousands of sensors.
* **For Home Use:** This is overkill.

### 💡 Alternative: VPS / Edge Hosting (Self-Hosted K3s)
To run the v2.0 stack cost-effectively for personal use, we can deploy to a VPS (e.g., Hetzner, DigitalOcean) or a local Raspberry Pi 4 cluster.

* **VPS Cost:** ~$6 - $10 / month
* **Local Hardware:** $0 (Capital Expenditure only)

---

## 🧠 Strategic Conclusion

The evolution from v1 to v2 was **not driven by cost optimization**, but by **architectural requirements**:

1.  **v1 (Serverless)** is the correct choice for a single-tenant home solution (Lowest TCO).
2.  **v2 (Kubernetes)** is the correct choice for a multi-tenant SaaS platform where **portability** and **vendor-independence** are required.

This project demonstrates the ability to architect for **both** scenarios.
