# 🌟 Project Overview: Boiler Status Monitor (AWS IoT Edge)

## 🎯 Key Engineering Goals

This project demonstrates a robust, cost-optimized, and event-driven Internet of Things (IoT) pipeline 
designed to monitor a dual home heating system. The core function is to detect the operational state of 
a solid-fuel boiler by monitoring the power status of its circulation pump.


## 📐 Architecture Design (System Design)

The project utilizes an event-driven IoT pipeline to monitor the boiler's status in real-time and provide alerts.

```mermaid
flowchart TD
    subgraph Edge_Layer [Edge Layer - Home]
        Pump[Solid-Fuel Boiler Pump 230V] -- 230V AC --> Opto[MVPDM-1PHS Module]
        Opto -- 3.3V Logic --> Pi[Raspberry Pi Zero 2W]
        Pi -- "Python script (AWS IoT SDK)" --> MQTT_Out(MQTT Topic: home/heating/status)
    end

    subgraph AWS_Cloud [AWS Cloud]
        IoT[AWS IoT Core]
        
        MQTT_Out -.-> |TLS 1.2 / X.509| IoT
        
        subgraph Hot_Path [Hot Path - Real-time Alerting]
            Rule_Alert{IoT Rule: status = 'INACTIVE'} 
            Lambda[AWS Lambda: TelegramNotifier]
            Telegram_API[Telegram API]
        end
        
        subgraph Cold_Path [Cold Path - Storage for ML]
            Rule_Store{IoT Rule: All Messages}
            DynamoDB[(Amazon DynamoDB)]
        end
        
        IoT --> Rule_Alert
        IoT --> Rule_Store
        
        Rule_Alert -- Trigger --> Lambda
        Lambda --> Telegram_API
        
        Rule_Store --> DynamoDB
    end

    classDef aws fill:#FF9900,stroke:#232F3E,color:white;
    classDef edge fill:#232F3E,stroke:#FF9900,color:white;
    classDef ext fill:#ddd,stroke:#333,color:black;
    
    class IoT,Lambda,DynamoDB,Rule_Alert,Rule_Store aws;
    class Pi,Opto,Pump edge;
    class Telegram_API ext;
```	
	
## 🛠️ Technologies Used

| Category          | Technology                | Purpose                                                                 |
|-------------------|---------------------------|-------------------------------------------------------------------------|
| Edge Compute      | Raspberry Pi Zero 2 W     | Edge device running the status monitoring Python script.                |
| Edge Sensing      | MVPDM-1PHS Module         | Safe galvanic isolation and detection of 230V AC pump status.           |
| Programming       | Python (3.11+)            | Edge logic, Lambda handler, and AWS CDK IaC definition.                 |
| Cloud Ingestion   | AWS IoT Core              | Secure MQTT Message Broker and Rule Engine.                             |
| Serverless Logic  | AWS Lambda                | Executing the stateless Telegram notification logic.                    |
| Alerting          | Telegram Bot API          | Free, reliable, cross-platform push notifications.                      |
| Data Storage      | Amazon DynamoDB           | Low-latency storage of historical status events for analytics.          |
| Deployment/DevOps | AWS CDK, GitHub Actions   | Automated deployment of cloud resources (Infrastructure as Code).       |
