# HR-SAD — Software Architecture Document

| Field | Value |
| --- | --- |
| Document ID | HR-SAD |
| Version | 0.2 |
| Status | Draft |
| Date | 2026-11-25 |
| Standard | ISO/IEC/IEEE 42010 |
| Parent | HR-SRS-SYS v0.1 |
| Related | HR-SRS-SW v0.2, HR-ICD v0.2 |
| Classification | Internal engineering draft |

---

## 1. Purpose and scope

Describe the software architecture of the **modular autonomous humanoid** so COTS limbs and project-built torso/compute integrate through a stable HAL, while Phase-0 balance/safety remain deterministic.

**In:** Module adapters, ROS 2 host, RT controllers, ICD, simulation hooks.  
**Out:** Mechanical CAD; supplier commercial selection (lives in SyRS); ML training pipelines.

---

## 2. Stakeholders and concerns

| Stakeholder | Concerns |
| --- | --- |
| Project lead | SyRS sequence; costed modular platform |
| Procurement / Hussain | Supplier SDK, URDF, bus fit |
| Software / AI | Stable capability API across module swaps |
| Real-time / safety | Deterministic loops; SafeStop authority |
| Perception | Head/sensors not on RT critical path (Phase-0) |
| V&V | Trace to SW-* and SYS themes |

---

## 3. Architecture drivers (from SyRS)

1. Modularity and plug-and-play **compatible** modules (not arbitrary vendor magic).
2. Common ROS 2 / ros2_control / URDF surface.
3. EtherCAT preferred for multi-axis sync; CAN-FD where reviewed.
4. Full-size biped targets with phased software delivery.
5. Central computer + distributed controllers.

---

## 4. Logical views

### 4.1 Modular platform view

```text
  [ AI / Apps / MoveIt / Autonomy ]
              |
        Capability API (ROS 2)
              |
        HAL / ros2_control managers
         /        |         \
   ArmAdapter  LegAdapter  HeadAdapter ...
         \        |         /
        Bus adapters (EtherCAT / CAN-FD / bridge)
              |
     COTS modules + torso I/O
```

High-level nodes must not speak vendor protocols directly (SW-MOD-001/002).

### 4.2 Compute / control view (Phase-0)

```text
  Host (Jetson-class / x86) — ROS 2 Humble
       outer balance, planning stubs, logging, HAL
              |
              | ICD IF-HR (versioned)
              v
  RT domain — MCU and/or module masters
       inner balance, watchdog, arbitration
              |
              | EtherCAT / CAN-FD (IF-BUS)
              v
  Actuators / COTS limb controllers / drives
```

**Principle:** Safety authority stays in the RT domain (SW-SAF, HR-SAFE). Host may advise; it must not bypass SafeStop.

### 4.3 Deployment view

| Node | Software | Notes |
| --- | --- | --- |
| Host PC / Jetson | `hr-robot` ROS 2 workspace + Docker dev image | SyRS “central computer” |
| RT MCU / masters | Project firmware and/or supplier masters | Cycle ~1 ms preferred |
| Arm/hand/leg modules | Supplier firmware + project adapter | Selected per SyRS §9+ |
| Dev PC | Docker Compose / CI | Windows-friendly builds |

### 4.4 Development view (packages)

| Package / component | Role |
| --- | --- |
| `hr_msgs` | Shared modes, references, faults, module identity |
| `hr_bringup` | Launch compositions |
| `hr_balance_jetson` | Host outer balance (Phase-0) |
| `hr_hal` (planned) | Capability API + controller_manager glue |
| `hr_<module>_adapter` (planned) | Per-vendor bridges |
| Description pkg (planned) | Assembled URDF/Xacro |

---

## 5. Process / timing view

| Loop | Target | Source |
| --- | --- | --- |
| RT balance / stance | 1 kHz (≤ 2 ms with waiver) | SW-TIM-001 |
| EtherCAT axis cycle | ~1 ± 0.1 ms when used | SyRS §7, SW-TIM-003 |
| Host balance refs | ≥ 50 Hz; ≤ 20 ms latency | SW-BAL-002, SW-TIM-002 |
| Host heartbeat | ≤ 50 ms; trip 100 ms | SW-SAF-001 |
| Telemetry RT→host | ≥ 100 Hz | SW-COM-004 |

---

## 6. Interface architecture

See **HR-ICD v0.2** for normative field dictionaries.

| Interface | Role |
| --- | --- |
| IF-CAP | Capability API (ROS 2 topics/services/actions) |
| IF-HR | Host ↔ RT control/telemetry/heartbeat |
| IF-BUS | RT/adapters ↔ modules (EtherCAT / CAN-FD) |
| IF-MOD | Module identity + profile |
| IF-OP | E-stop / operator clear |

---

## 7. Architecture decisions

| ID | Decision | Rationale | Status |
| --- | --- | --- | --- |
| AD-001 | HAL + adapters over vendor lock-in in AI nodes | SyRS modularity | Accepted |
| AD-002 | ROS 2 Humble + ros2_control preferred | SyRS §7 | Accepted |
| AD-003 | EtherCAT preferred; CAN-FD allowed per review | SyRS §7; OpenArm etc. | Accepted |
| AD-004 | RT domain owns SafeStop | SyRS supplier safety + SW-SAF | Accepted |
| AD-005 | Phase-0 balance before walk/manip Must | SyRS sequence; risk | Accepted |
| AD-006 | COTS limbs with project torso | SyRS sourcing strategy | Accepted |
| AD-007 | Dockerized host builds | Reproducible Humble on mixed OS | Accepted |

---

## 8. Quality attributes

| Attribute | Approach |
| --- | --- |
| Modifiability | Adapters + capability API |
| Safety | RT watchdog, limits, STO, latch |
| Real-time | Bus cycle + RT loop budgets |
| Integrability | URDF, ros2_control, ICD profiles |
| Testability | SW-* methods; HR-TEST-SW |
| Simulability | Gazebo / Isaac hooks per SyRS | Preferred when module models exist |

---

## 9. Risks

| Risk | Mitigation |
| --- | --- |
| Arm mass vs 75 kg robot cap | Software envelopes + SyRS mass budget ownership |
| Mixed buses (EtherCAT + CAN-FD) | Explicit adapters; no silent bridging |
| Supplier without ROS 2 | Project adapter mandatory before AI use |
| Balance on COTS legs with closed firmware | Require balance-control access in purchase (SyRS legs) |

---

## 10. Traceability

| View element | SW IDs |
| --- | --- |
| HAL / adapters | SW-MOD-001 … 006 |
| Host/RT balance | SW-BAL-*, SW-TIM-*, SW-EST-* |
| Safety | SW-SAF-*, HR-SAFE |
| Phase-1 manip/walk | SW-MAN-*, SW-MOB-* |

---

## 11. Document history

| Version | Date | Notes |
| --- | --- | --- |
| 0.1 | 2026-11-25 | Jetson/MCU/drives balance draft |
| 0.2 | 2026-11-25 | Modular SyRS alignment; HAL; phased compute |
