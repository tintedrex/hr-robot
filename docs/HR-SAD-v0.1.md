# HR-SAD — Software Architecture Document

| Field | Value |
| --- | --- |
| Document ID | HR-SAD |
| Version | 0.1 |
| Status | Draft |
| Date | 2026-11-25 |
| Standard | ISO/IEC/IEEE 42010 (architecture description) |
| System | Humanoid Robot (HR) — default control stack |
| Related | HR-SRS-SW v0.1 |
| Classification | Internal engineering draft |

---

## 1. Purpose and scope

### 1.1 Purpose

This Software Architecture Document (SAD) describes the architecture of the Humanoid Robot (HR) control software: stakeholders and concerns, viewpoints, views, architecture decisions, and how the design satisfies HR-SRS-SW v0.1.

### 1.2 Scope (in)

- Software on Jetson (high-level), real-time MCU (mid-level), and motor-drive interfaces (low-level).
- Balance / upright stance baseline and supporting timing, communication, estimation, safety, and logging.
- Interfaces between control levels and ROS 2 packages in the `hr-robot` workspace.

### 1.3 Scope (out)

- Mechanical and electrical board design details.
- Full gait library, manipulation, and trained perception models (future architecture increments).
- Formal functional-safety certification artifacts.

### 1.4 Intended audience

Project lead, software/controls engineers, V&V, and contributors named for simulation, AI, real-time link, and safety.

---

## 2. References

| ID | Reference |
| --- | --- |
| REF-001 | ISO/IEC/IEEE 42010 — Architecture description |
| REF-002 | ISO/IEC/IEEE 29148 — Requirements engineering |
| REF-003 | HR-SRS-SW v0.1 — Software Requirements Specification |
| REF-004 | `hr-robot` repository — ROS 2 Humble workspace |
| REF-005 | ROS 2 Humble documentation |

---

## 3. Stakeholders and concerns

| Stakeholder | Concerns |
| --- | --- |
| Project lead | Delivery of balance baseline; clear ownership by control level |
| Controls / real-time | Deterministic MCU loops; latency budgets; SafeStop behavior |
| AI / learning | Jetson nodes for estimation/planning without bypassing MCU safety |
| Perception | Sensor data paths into Jetson; not on MCU critical path for v0.1 |
| Simulation | Ability to run Jetson-side stubs without full hardware |
| V&V | Traceability from architecture elements to SW-* requirements |
| Operators | Clear modes, E-stop path, diagnostics |

---

## 4. Architecture overview

### 4.1 Context

The HR software controls a bipedal humanoid for upright stance on level ground. An operator (or test harness) commands modes; the system maintains balance or enters SafeStop / FallDetected reactions defined in HR-SRS-SW.

### 4.2 Control-level decomposition

```text
  [ Operator / UI / Logging ]
              |
         Jetson (high-level)
           ROS 2 Humble: planning, outer balance, telemetry
              |  balance refs, mode, heartbeat
              v
         RT MCU (mid-level)
           Inner balance, estimation, watchdog, drive arbitration
              |  setpoints, limits, enable / STO request
              v
         Motor drives (low-level)
           FOC servo, local faults, STO
              |
              +--> feedback / faults --> MCU --> Jetson
```

| Level | Responsibility | Typical tech |
| --- | --- | --- |
| Jetson | Outer loops, orchestration, logging, operator interface | Linux, ROS 2 Humble, Python/C++ |
| MCU | Hard real-time inner balance, sensor validity, SafeStop | RTOS / bare-metal, 1 kHz loop |
| Drives | Torque/current/velocity tracking, fault bits | FOC firmware / vendor drive stack |

### 4.3 Key architecture principles

1. **Safety authority on MCU** — Jetson may advise; MCU decides SafeStop / FallDetected / sensor-invalid reactions (SW-SAF, SW-EST).
2. **Hard timing below Jetson** — MCU and drive command periods meet SW-TIM; Jetson is soft real-time.
3. **Versioned ICD** — Jetson↔MCU and MCU↔drive messages are versioned (SW-COM).
4. **Observable by default** — Mode, faults, and recent telemetry are dumpable after SafeStop (SW-LOG).

---

## 5. Viewpoints and views (42010)

### 5.1 Context view

- **Actors:** Operator, V&V harness, (optional) simulator.
- **System boundary:** HR software + drive command/feedback interface.
- **External:** Power, E-stop hardware line, STO, body IMU, joint encoders.

### 5.2 Logical / functional view

| Function | Primary location | SRS mapping (examples) |
| --- | --- | --- |
| Outer balance references | Jetson `hr_balance_jetson` | SW-BAL-002, SW-BAL-007, SW-BAL-010 |
| Inner balance / stance | MCU firmware | SW-BAL-003, SW-BAL-004, SW-BAL-005, SW-BAL-008 |
| Torque tracking | Drives | SW-BAL-009 |
| Attitude / joint estimation | MCU (+ optional Jetson parallel) | SW-EST-001 … SW-EST-004 |
| Watchdog / SafeStop / E-stop | MCU + drives | SW-SAF-001 … SW-SAF-006 |
| Logging / fault codes | Jetson + MCU | SW-LOG-001 … SW-LOG-004 |

### 5.3 Process / concurrency view

| Process | Rate / deadline | Notes |
| --- | --- | --- |
| MCU balance loop | 1.0 ms ± 0.1 ms | SW-TIM-001 |
| Drive command stream | ≤ 2.0 ms period | SW-TIM-003 |
| Jetson balance reference publish | ≥ 50 Hz | SW-BAL-002 |
| Jetson→MCU latency | ≤ 20 ms (95th) | SW-TIM-002 |
| Jetson heartbeat | ≤ 50 ms interval; trip at 100 ms | SW-SAF-001 |
| MCU→Jetson telemetry | ≥ 100 Hz | SW-COM-004 |

Missed Jetson references / heartbeats force degraded SafeStance or SafeStop (SW-TIM-004, SW-SAF-001).

### 5.4 Deployment view

| Node | Deployed software | Notes |
| --- | --- | --- |
| Jetson Orin-class | Ubuntu + ROS 2 Humble workspace (`hr-robot`) | Dev via Docker `hr-robot:humble-dev` |
| Real-time MCU | Balance / watchdog / ICD firmware (out of ROS tree) | Separate build/flash pipeline |
| Motor drives | Vendor or custom FOC | Configured via MCU ICD |
| Developer PC | Docker Compose build/test | Windows host supported via container |

### 5.5 Development view (ROS 2 packages)

| Package | Role |
| --- | --- |
| `hr_msgs` | Shared messages: mode, balance reference, status, faults |
| `hr_balance_jetson` | Outer balance node stub (≥ 50 Hz references) |
| `hr_bringup` | Launch entrypoint |

MCU and drive firmware repositories are logically separate; they consume the same ICD concepts as `hr_msgs` / SW-COM.

---

## 6. Interface design

### 6.1 Jetson ↔ MCU

Minimum message set (SW-COM-001):

- Stance / balance mode
- Balance references (CoM / torso orientation targets)
- Joint state summary
- IMU / attitude summary
- Fault bitfield
- Heartbeat

Schema version is mandatory; unsupported versions are rejected (SW-COM-002).

### 6.2 MCU ↔ drives

- Setpoints: torque/current/velocity with SI units and documented scaling (SW-COM-003)
- Feedback: position, velocity, measured torque/current, fault status (SW-COM-005)
- Disable / STO request path with ≤ 20 ms torque removal (SW-SAF-004)

### 6.3 Operator / E-stop

Hardware E-stop is observed in software within 20 ms and leads to SafeStop + drive torque removal (SW-SAF-005). Critical faults latch until explicit clear (SW-SAF-006).

---

## 7. Architecture decisions

| ID | Decision | Rationale | Status |
| --- | --- | --- | --- |
| AD-001 | Three control levels: Jetson / MCU / drives | Separates soft RT AI/planning from hard RT balance and power electronics | Accepted |
| AD-002 | ROS 2 Humble on Jetson | Team standard; package ecosystem; matches A-02 workspace | Accepted |
| AD-003 | MCU owns safety reactions | Meets SW-SAF / SW-EST; Jetson hang must not keep driving | Accepted |
| AD-004 | Docker-based Jetson/dev builds | Reproducible Humble environment on Windows/Linux | Accepted |
| AD-005 | Balance-first v0.1 scope | Delivers testable upright stance before gait/manipulation | Accepted |
| AD-006 | Provisional SYS-* parents until HR-SyRS | Unblocks SRS/SAD while system requirements mature | Accepted |

---

## 8. Quality attributes

| Attribute | Approach |
| --- | --- |
| Safety | MCU watchdog, limits, latched faults, STO path |
| Real-time performance | Fixed MCU period; drive deadline faults |
| Reliability | Versioned ICD; stale-data policies |
| Observability | Mode/fault events + ring buffer dump (SW-LOG) |
| Modifiability | Clear package and firmware boundaries by level |
| Testability | Each SW-* requirement has a verification method in HR-SRS-SW |

---

## 9. Risks and open items

1. Concrete bus choice (EtherCAT / CAN-FD / other) for MCU↔drives — TBD in ICD.
2. Mass model and push-test fixture numbers for SW-BAL-004 — refine in Wk 2–4.
3. Sit/Stand trajectory waypoints and harness policy — TBD.
4. Formal safety standard alignment if required later.
5. Split MCU/drive firmware into dedicated repos with CI.

---

## 10. Traceability summary

| Architecture element | Primary SRS IDs |
| --- | --- |
| Jetson outer balance | SW-BAL-002, SW-BAL-007, SW-BAL-010 |
| MCU inner balance | SW-BAL-003 … SW-BAL-006, SW-BAL-008 |
| Drives torque path | SW-BAL-009, SW-TIM-005, SW-SAF-004 |
| Timing framework | SW-TIM-001 … SW-TIM-004 |
| ICD / messaging | SW-COM-001 … SW-COM-005 |
| Estimation | SW-EST-001 … SW-EST-004 |
| Safety | SW-SAF-001 … SW-SAF-006 |
| Logging | SW-LOG-001 … SW-LOG-004 |

---

## 11. Document history

| Version | Date | Author | Notes |
| --- | --- | --- | --- |
| 0.1 | 2026-11-25 | HR software (draft) | Initial SAD aligned to HR-SRS-SW v0.1 and `hr-robot` workspace |
