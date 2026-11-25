# HR-ICD — Interface Control Document

| Field | Value |
| --- | --- |
| Document ID | HR-ICD |
| Version | 0.1 |
| Status | Draft |
| Date | 2026-11-25 |
| System | Humanoid Robot (HR) |
| Related | HR-SRS-SW v0.1, HR-SAD v0.1 |
| Google Doc | https://docs.google.com/document/d/1-ebccTA3ErIerhoI9qA0i0ZkHVCAOYju8nQHdDmVHtU/edit |
| Classification | Internal engineering draft |

---

## 1. Purpose and scope

### 1.1 Purpose

This Interface Control Document (ICD) defines the logical and (where known) physical interfaces between HR software control levels so teams can integrate Jetson, real-time MCU, and motor drives without ambiguous units, versions, or timing.

### 1.2 Interfaces covered

| Interface ID | From | To | Medium (v0.1 assumption) |
| --- | --- | --- | --- |
| IF-JM | Jetson | MCU | Ethernet / UART / USB-serial (TBD physical) |
| IF-MJ | MCU | Jetson | Same link as IF-JM (bidirectional) |
| IF-MD | MCU | Drives | CAN-FD or EtherCAT (TBD) |
| IF-DM | Drives | MCU | Same bus as IF-MD |
| IF-OP | Operator / E-stop HW | Jetson + MCU | GPIO / safety circuit + software mirror |

### 1.3 Out of scope

- Mechanical mounting and connector pinouts (HW drawings).
- Full gait / manipulation message catalogs beyond balance baseline.
- Cryptographic authentication of bus traffic (future).

---

## 2. Conventions

| Topic | Convention |
| --- | --- |
| Endianness | Little-endian for binary fields |
| Units | SI (m, rad, N·m, A, s) unless noted |
| Time | Timestamps are host monotonic or synchronized time_msg; document clock domain per field |
| Angles | Radians; RPY order roll-pitch-yaw unless noted |
| Booleans | 0 = false, 1 = true |
| Schema version | `uint16 schema_version`; major mismatch ⇒ reject |
| Byte alignment | Prefer packed structs with explicit padding documented |

---

## 3. IF-JM / IF-MJ — Jetson ↔ MCU

### 3.1 Link requirements (logical)

| Property | Requirement | SRS |
| --- | --- | --- |
| Balance reference rate | ≥ 50 Hz Jetson → MCU | SW-BAL-002 |
| End-to-end latency | ≤ 20 ms (95th percentile) | SW-TIM-002 |
| Telemetry rate | ≥ 100 Hz MCU → Jetson | SW-COM-004 |
| Heartbeat | Jetson heartbeat ≤ 50 ms; trip at 100 ms | SW-SAF-001 |
| Versioning | Unsupported schema rejected + logged | SW-COM-002 |

### 3.2 Message set (minimum)

| Message | Direction | Purpose |
| --- | --- | --- |
| `Heartbeat` | Jetson → MCU | Liveness |
| `BalanceModeCmd` | Jetson → MCU | Sit / Stand / Transition / Clear |
| `BalanceReference` | Jetson → MCU | CoM / torso orientation targets |
| `JointStateSummary` | MCU → Jetson | Positions / velocities / efforts |
| `ImuAttitudeSummary` | MCU → Jetson | Torso attitude estimate |
| `FaultStatus` | MCU → Jetson | Latched / active faults |
| `BalanceModeStatus` | MCU → Jetson | Active mode |

### 3.3 Field dictionaries

#### BalanceReference (Jetson → MCU)

| Field | Type | Unit | Notes |
| --- | --- | --- | --- |
| schema_version | uint16 | — | Start at 1 |
| stamp_ns | uint64 | ns | Producer clock |
| com_x / com_y / com_z | float32 | m | Desired CoM |
| torso_roll / pitch / yaw | float32 | rad | Desired orientation |
| yaw_rate_cmd | float32 | rad/s | Optional |
| mode | uint8 | enum | See mode table |

#### FaultStatus (MCU → Jetson)

| Field | Type | Notes |
| --- | --- | --- |
| fall_detected | bool | SW-BAL-005 / SW-BAL-006 |
| sensor_invalid | bool | SW-EST-002 |
| watchdog_trip | bool | SW-SAF-001 |
| e_stop | bool | SW-SAF-005 |
| joint_feedback_stale | bool | SW-EST-003 |
| drive_comm_fault | bool | SW-TIM-005 / SW-LOG-004 |
| raw_code | uint32 | Shared enum with MCU |
| detail | string/bytes | Optional human-readable |

#### Mode enumeration

| Value | Name |
| --- | --- |
| 0 | UNKNOWN |
| 1 | SIT |
| 2 | STAND |
| 3 | TRANSITION |
| 4 | FALL_DETECTED |
| 5 | SAFE_STOP |
| 6 | FAULT |

### 3.4 ROS 2 mapping (Jetson side)

| Topic (v0.1) | Type package | Notes |
| --- | --- | --- |
| `hr/balance/reference` | `hr_msgs/BalanceReference` | Outer loop publish |
| `hr/balance/mode` | `hr_msgs/BalanceMode` | Mode status / command mirror |
| (TBD bridge) | — | MCU bridge node translates ICD ↔ ROS |

Physical framing (protobuf / CDR / custom binary) is TBD; logical fields above are normative for v0.1.

---

## 4. IF-MD / IF-DM — MCU ↔ drives

### 4.1 Link requirements

| Property | Requirement | SRS |
| --- | --- | --- |
| Command period | ≤ 2.0 ms while Stand active | SW-TIM-003 |
| Missed command | Fault if no setpoint within 5 ms of expected | SW-TIM-005 |
| Feedback | Position, velocity, torque/current, fault each cycle | SW-COM-005 |
| Disable / STO | Torque removed ≤ 20 ms | SW-SAF-004 |
| Units / scale | Documented in this ICD | SW-COM-003 |

### 4.2 Per-joint command (MCU → drive)

| Field | Type | Unit | Notes |
| --- | --- | --- | --- |
| joint_id | uint8 | — | Project joint map |
| control_mode | uint8 | enum | TORQUE / CURRENT / VELOCITY |
| setpoint | float32 | N·m or A or rad/s | Per mode |
| torque_limit | float32 | N·m | Soft limit hint |
| enable | bool | — | 0 ⇒ attempt disable |
| seq | uint16 | — | Detect drops |

### 4.3 Per-joint feedback (drive → MCU)

| Field | Type | Unit | Notes |
| --- | --- | --- | --- |
| joint_id | uint8 | — | |
| position | float32 | rad | |
| velocity | float32 | rad/s | |
| measured_effort | float32 | N·m or A | Match control_mode |
| fault_code | uint16 | enum | Vendor + project codes |
| enabled | bool | — | |

### 4.4 Drive fault codes (project subset)

| Code | Name | Action on MCU |
| --- | --- | --- |
| 0 | OK | — |
| 1 | COMM_TIMEOUT | drive_comm_fault; SafeStop path |
| 2 | OVERCURRENT | Limit / SafeStop |
| 3 | OVERTEMP | Limit / SafeStop |
| 4 | STO_ACTIVE | Treat as disabled |
| 5 | INTERNAL | Fault latch |

---

## 5. IF-OP — Operator and E-stop

| Signal | Consumer | Latency | Behavior |
| --- | --- | --- | --- |
| E-stop assert | MCU (primary), Jetson (log) | ≤ 20 ms software recognition | SafeStop + drive torque removal |
| Mode command Sit/Stand | Jetson → MCU | Per IF-JM | Transition sequencing |
| Fault clear | Operator → Jetson → MCU | After condition cleared | Clears latched faults (SW-SAF-006) |

Hardware STO may bypass software; software must still observe and latch state.

---

## 6. Timing and stale-data policies

| Condition | Policy | SRS |
| --- | --- | --- |
| Balance reference age > 100 ms | Hold ≤ 200 ms more, then SafeStance/SafeStop | SW-TIM-004 |
| IMU invalid > 10 MCU cycles | SensorInvalid → SafeStop | SW-EST-002 |
| Joint feedback age > 5 ms | Stale; do not use for torque calc | SW-EST-003 |
| Jetson heartbeat loss > 100 ms | WatchdogTrip → SafeStop | SW-SAF-001 |

---

## 7. Compatibility and change control

1. Increment `schema_version` on any incompatible field change.
2. Compatible additions (optional trailing fields) keep major version; document in revision history.
3. ICD changes that affect SW-COM / SW-TIM require SRS impact check and TEST updates.

---

## 8. Open items

1. Select physical buses and connector pinouts.
2. Publish binary IDL (protobuf / ROS IDL / custom header).
3. Joint ID map for the mechanical design.
4. Clock sync method Jetson ↔ MCU (PTP / exchange offsets).

---

## 9. Document history

| Version | Date | Notes |
| --- | --- | --- |
| 0.1 | 2026-11-25 | Initial ICD aligned to HR-SRS-SW / HR-SAD v0.1 |
