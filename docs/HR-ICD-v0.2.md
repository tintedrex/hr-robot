# HR-ICD — Interface Control Document

| Field | Value |
| --- | --- |
| Document ID | HR-ICD |
| Version | 0.2 |
| Status | Draft |
| Date | 2026-11-25 |
| Parent | HR-SRS-SYS v0.1 |
| Related | HR-SRS-SW v0.2, HR-SAD v0.2 |
| Google Doc | https://docs.google.com/document/d/1-ebccTA3ErIerhoI9qA0i0ZkHVCAOYju8nQHdDmVHtU/edit |
| Classification | Internal engineering draft |

---

## 1. Purpose

Define interfaces so **COTS modules** and **project compute** integrate without ambiguous units, versions, or timing — implementing SyRS modularity (§2) and software standards (§7).

---

## 2. Interface index

| ID | From | To | Purpose |
| --- | --- | --- | --- |
| IF-CAP | AI / apps | HAL | Capability commands (vendor-agnostic) |
| IF-HR | Host | RT domain | Balance refs, mode, heartbeat, telemetry |
| IF-BUS | RT / adapters | Modules | EtherCAT or CAN-FD setpoints/feedback |
| IF-MOD | Module | Host/RT | Identity, profile, faults |
| IF-OP | Operator / E-stop HW | Host+RT | Stop and clear |

Mechanical/electrical connector ICDs remain in HW packs; this document is **software/comms logical ICD** plus bus norms.

---

## 3. Conventions

| Topic | Rule |
| --- | --- |
| Endianness | Little-endian for project binary fields |
| Units | SI |
| Angles | rad; RPY roll-pitch-yaw |
| Schema | `uint16 schema_version`; incompatible ⇒ reject |
| Clocks | Document domain per field; latency measured end-to-end |

---

## 4. IF-CAP — Capability API (ROS 2)

High-level nodes use these contracts only (SW-MOD-001).

| Capability | Interface (v0.2) | Notes |
| --- | --- | --- |
| Stance mode | `hr/balance/mode` (`hr_msgs/BalanceMode`) | Sit/Stand/SafeStop/… |
| Balance reference | `hr/balance/reference` | Outer loop |
| Fault status | `hr/faults` | Bitfield + code |
| Module identity | `hr/modules/<name>/identity` | SW-MOD-003 |
| Joint command (Phase-0/1) | ros2_control command interfaces | Preferred |
| Arm plan (Phase-1) | MoveIt 2 action | When arms online |

AI nodes shall not open raw EtherCAT/CAN sockets.

---

## 5. IF-HR — Host ↔ RT

### 5.1 Timing

| Property | Value | SRS |
| --- | --- | --- |
| Balance ref rate | ≥ 50 Hz | SW-BAL-002 |
| Latency | ≤ 20 ms p95 | SW-TIM-002 |
| Telemetry | ≥ 100 Hz | SW-COM-004 |
| Heartbeat | ≤ 50 ms; trip 100 ms | SW-SAF-001 |

### 5.2 Messages

| Message | Dir | Fields (logical) |
| --- | --- | --- |
| Heartbeat | H→RT | stamp, seq |
| BalanceModeCmd | H→RT | mode enum |
| BalanceReference | H→RT | schema, stamp, com_xyz, torso_rpy, yaw_rate, mode |
| JointStateSummary | RT→H | positions, velocities, efforts |
| ImuAttitudeSummary | RT→H | quat or rpy + valid flag |
| FaultStatus | RT→H | flags per SW-COM / SW-SAF |
| BalanceModeStatus | RT→H | active mode |

### 5.3 Mode enum

UNKNOWN=0, SIT=1, STAND=2, TRANSITION=3, FALL_DETECTED=4, SAFE_STOP=5, FAULT=6.

### 5.4 Stale policies

| Condition | Action |
| --- | --- |
| Ref age > 100 ms | Hold ≤ 200 ms then SafeStance/SafeStop |
| Heartbeat loss > 100 ms | WatchdogTrip → SafeStop |

---

## 6. IF-BUS — EtherCAT / CAN-FD

### 6.1 Selection (from SyRS §7)

| Bus | Use |
| --- | --- |
| EtherCAT | Preferred synchronized multi-axis (e.g. many industrial arms) |
| CAN-FD | Cost-conscious / limbs such as OpenArm-class; subject to review |

### 6.2 Normative logical PDO / frame content (per joint)

**Command:** joint_id, control_mode (POS/VEL/TORQUE), setpoint, limits, enable, seq.  
**Feedback:** joint_id, position, velocity, effort, fault_code, enabled.

Cycle: **~1 ms** preferred (EtherCAT 1±0.1 ms when claimed by supplier). Missed command > 5 ms (or one missed cycle) raises drive/module comm fault (SW-TIM-005 class).

### 6.3 STO / disable

Disable or STO request ⇒ torque-producing output removed ≤ **20 ms** if supported; else document supplier bound in module profile (SW-SAF-004).

---

## 7. IF-MOD — Module identity and profiles

### 7.1 Identity (required)

| Field | Type | Notes |
| --- | --- | --- |
| manufacturer | string | |
| model | string | |
| hw_revision | string | |
| fw_version | string | |
| capabilities | bitfield/string list | e.g. TORQUE, STO, BRAKES, ROS2_CONTROL |
| bus_type | enum | ETHERCAT, CANFD, OTHER |
| schema_version | uint16 | Profile schema |

### 7.2 Module profile document (per SKU)

Each shortlisted module gets a profile annex covering SyRS §6 software/safety asks:

- Protocol + cycle time + sync
- ROS 2 / ros2_control / SDK entry points
- URDF availability
- STO / brakes / comm-loss behaviour
- Joint map and SI scaling
- Power/enable prerequisites (pointer to electrical ICD)

### 7.3 Arm profile placeholders

Populate after down-select (SyRS §9 candidates: OpenArm, NERO, ROKAE, FAIRINO, TIANJI, NEXFORM, …).

| Profile ID | Status |
| --- | --- |
| MOD-ARM-TBD | Pending supplier recommendation |

---

## 8. IF-OP — Operator / E-stop

| Signal | Bound | Effect |
| --- | --- | --- |
| E-stop assert | ≤ 20 ms SW path | SafeStop + torque removal |
| Fault clear | After condition gone | Clears latch (SW-SAF-006) |

Hardware STO may precede software; software still latches observed state.

---

## 9. Change control

1. Incompatible field changes ⇒ bump schema major; both sides reject mismatch (SW-COM-002).  
2. ICD changes affecting timing/safety require SRS + TEST + SAFE impact notes.  
3. New module SKUs add profiles without breaking IF-CAP.

---

## 10. Open items

1. Freeze physical medium for IF-HR (Eth/UART/shared mem).  
2. Publish IDL (ROS IDL / protobuf / ESI).  
3. Joint naming map vs URDF.  
4. Fill first arm/leg profiles post-RFQ.

---

## 11. Document history

| Version | Date | Notes |
| --- | --- | --- |
| 0.1 | 2026-11-25 | Jetson↔MCU↔drive only |
| 0.2 | 2026-11-25 | SyRS modular HAL; IF-CAP/BUS/MOD; EtherCAT/CAN-FD |
