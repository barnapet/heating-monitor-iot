# Edge Layer – Boiler Status Detection

## Audience
- IoT Engineers
- Embedded / Edge Developers
- Cloud Architects

---

## Problem Statement

The goal of the edge layer is to reliably detect the operational state of a solid‑fuel boiler **without modifying the boiler itself** or interfering with its control logic.

Instead of measuring temperature directly, the system **infers boiler activity** by monitoring the power state of the circulation pump. This provides a clear, binary signal that is strongly correlated with active heating cycles.

---

## Hardware Design

The edge hardware stack consists of:

- **Solid‑fuel boiler circulation pump (230V AC)**
- **MVPDM‑1PHS opto‑isolated detection module**
- **Raspberry Pi Zero 2 W**

The pump’s AC power line is connected to the opto‑isolated detection module, which safely converts the presence of mains voltage into a low‑voltage digital signal suitable for GPIO input on the Raspberry Pi.

---

## Electrical Safety Considerations

Electrical safety was a primary design constraint:

- Full **galvanic isolation** between mains voltage and logic‑level signals
- No direct voltage or current measurement
- Passive signal detection only
- No modification of the boiler’s electrical system

This design minimizes risk while maintaining reliable operational state detection.

---

## Edge Compute Logic

The Raspberry Pi Zero 2 W runs a lightweight Python application responsible for:

- Reading GPIO input from the opto‑isolated module
- Debouncing and stabilizing the signal
- Translating electrical state into logical boiler states:
  - `ACTIVE`
  - `INACTIVE`
- Publishing state changes to the cloud

**Python 3.11+** was selected due to its mature ecosystem, long‑term support, and native compatibility with the AWS IoT SDK.

---

## Cloud Communication

The edge device communicates securely with AWS using:

- **AWS IoT SDK for Python**
- **MQTT protocol**
- **TLS 1.2 with X.509 certificate authentication**

State changes are published to a dedicated MQTT topic:

```text
home/heating/status
```

This enables secure, low‑latency, event‑driven communication with downstream cloud services and automations.

---

## Design Decisions

### Why power‑based detection?
- Binary and deterministic signal
- Independent of ambient temperature
- No sensor calibration required

### Why Raspberry Pi instead of a microcontroller?
- Native Linux environment
- Easier certificate and key management
- Faster development and iteration during prototyping

### Why MQTT over REST?
- Lower protocol overhead
- Event‑driven architecture
- Native integration with AWS IoT Core

---

## Failure Modes & Mitigations

| Failure Mode     | Mitigation                          |
|------------------|--------------------------------------|
| Power outage     | State restored on reboot              |
| Network loss     | Local retry and reconnect logic       |
| Signal noise     | Software debouncing and filtering     |

---

## Summary

This edge‑layer design provides a **safe, non‑intrusive, and reliable** method for detecting boiler activity. By leveraging opto‑isolated power detection and a Linux‑based edge device, the system achieves high reliability while remaining simple, maintainable, and cloud‑ready.

