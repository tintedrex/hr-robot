# HR-SRS-SW — Software Requirements Specification

| Field | Value |
| --- | --- |
| Document ID | HR-SRS-SW |
| Version | 0.2 |
| Status | Draft |
| Date | 2026-11-25 |
| Standard | ISO/IEC/IEEE 29148 |
| System | Modular Autonomous Humanoid Robot (HR) |
| Parent | HR-SRS-SYS v0.1 (Hussain Ahmad, 24 Nov 2026) |
| Classification | Internal engineering draft |

---

## 1. Purpose and scope

### 1.1 Purpose

This SRS defines verifiable **software** requirements for the HR platform. It allocates and refines software concerns from **HR-SRS-SYS v0.1** (modular COTS integration, ROS 2 HAL, mobility/manipulation/autonomy targets) into shall/should statements with verification methods.

### 1.2 Relationship to HR-SRS-SYS

| SyRS theme | Software implication in this SRS |
| --- | --- |
| Modular / plug-and-play modules | HAL + capability API; module identity; no rewrite of high-level AI on compatible swap |
| ROS 2 / ros2_control / URDF | Mandated middleware and robot description interfaces |
| EtherCAT / CAN-FD | Bus support via adapters; timing budgets |
| Full-size biped + walking / payload | Phased software: Phase-0 balance; Phase-1 walk/manip stubs |
| Supplier SDK / safety hooks | Drivers expose STO, faults, watchdog behaviour to the platform |
| Central computer + distributed controllers | Jetson-class host + real-time controllers (MCU / module masters) |

### 1.3 Phasing

| Phase | Software focus | Maps to SyRS sequence |
| --- | --- | --- |
| **Phase-0 (this document baseline)** | Module HAL skeleton, ICD, upright balance / SafeStop on level ground | SyRS stages 1–3 (interfaces, early limb bring-up) |
| **Phase-1** | Walking, arm/hand via MoveIt 2, perception topics | SyRS stages 4–6 |
| **Phase-2** | Autonomous task execution without routine teleop | SyRS autonomy target |

Phase-0 Must requirements below are normative for v0.2. Phase-1 items are marked **Phase-1** and may be Should until scheduled.

### 1.4 Scope (in / out)

**In:** Host software (ROS 2 Humble), hardware abstraction, real-time control software owned by the project, module adapters, safety/logging software paths, balance baseline.

**Out:** Mechanical/electrical pinouts (SyRS + HW drawings); supplier commercial terms; formal ISO certification dossiers (see HR-SAFE); training of foundation models.

---

## 2. References

| ID | Reference |
| --- | --- |
| REF-001 | ISO/IEC/IEEE 29148 |
| REF-002 | HR-SRS-SYS v0.1 — System Requirements Specification |
| REF-003 | HR-SAD v0.2, HR-ICD v0.2, HR-TEST-SW v0.2, HR-SAFE v0.2 |
| REF-004 | ROS 2 Humble, ros2_control, MoveIt 2 |
| REF-005 | Platform: Jetson-class Linux host; RT controllers; EtherCAT and/or CAN-FD |

---

## 3. Definitions

| Term | Definition |
| --- | --- |
| Module | Replaceable assembly (arm, hand, leg, head, …) conforming to platform ICD |
| HAL | Hardware abstraction layer exposing common capabilities to AI/apps |
| Host | Central computer running ROS 2 (Jetson-class or equivalent) |
| RT controller | Real-time MCU or module master enforcing timing/safety |
| Phase-0 | Balance + HAL + safety baseline |
| Shall / Should | Must / recommended |

Parent SyRS statements are cited as **SYS** (section themes from HR-SRS-SYS). Formal `SYS-xxx` IDs should be added when SyRS is ID’d; until then use section tags below.

| Parent tag | SyRS theme |
| --- | --- |
| SYS-MOD | Modular / plug-and-play (§2) |
| SYS-PARAM | System-level parameters (§4) |
| SYS-SUP | Supplier software/safety info (§6) |
| SYS-SW | Communication and software standards (§7) |
| SYS-SEQ | Development sequence (§8) |
| SYS-ARM | Arm subsystem (§9) |

---

## 4. Software requirements

Each requirement: **ID**, **Level** (Host | RT | Adapter | System), **Priority**, **Phase**, **Parent**, **Verification**, **Statement**, **Test method**.

### 4.1 Modularity and HAL — SW-MOD

#### SW-MOD-001

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-MOD |
| Verification | Inspection |
| Statement | The software architecture shall provide a ROS 2 hardware abstraction so that high-level AI/task nodes command robot **capabilities** (e.g. joint trajectories, gripper, balance mode) without embedding vendor-specific protocols. |
| Test method | Inspect package boundaries and topic/service contracts in HR-ICD / HR-SAD. |

#### SW-MOD-002

| Attribute | Value |
| --- | --- |
| Level | Adapter |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-MOD |
| Verification | Demonstration |
| Statement | Replacing a compatible module shall require at most adapter configuration, calibration, and validation — not changes to core AI/application node source. |
| Test method | Swap mock adapter A→B with same capability API; AI nodes unchanged; demo succeeds. |

#### SW-MOD-003

| Attribute | Value |
| --- | --- |
| Level | Adapter |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-MOD |
| Verification | Test |
| Statement | Each connected module adapter shall publish module identity: manufacturer, model, hardware revision, firmware version, and capability flags. |
| Test method | Connect stub module; verify identity topic/fields present. |

#### SW-MOD-004

| Attribute | Value |
| --- | --- |
| Level | Host |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SW |
| Verification | Test |
| Statement | The host software shall use ROS 2 Humble as the integration middleware for modules that expose ROS 2 drivers or project adapters. |
| Test method | `ros2 doctor` / bringup launch; nodes discoverable. |

#### SW-MOD-005

| Attribute | Value |
| --- | --- |
| Level | Host |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SW |
| Verification | Demonstration |
| Statement | Module joint interfaces should integrate through **ros2_control** where the supplier or project adapter supports it. |
| Test method | Load a ros2_control controller for a stub or real module; command a joint. |

#### SW-MOD-006

| Attribute | Value |
| --- | --- |
| Level | Host |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SW |
| Verification | Inspection |
| Statement | The platform shall maintain a URDF/Xacro (or equivalent) robot description assembled from module models, including joint names, limits, and frames needed for control and planning. |
| Test method | Inspect description package; `check_urdf` or equivalent passes. |

---

### 4.2 Balance (Phase-0) — SW-BAL

#### SW-BAL-001

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-PARAM (bipedal standing) |
| Verification | Test |
| Statement | The HR software shall maintain upright bipedal stance on level ground for at least 60 s without external support when initialized in Stand with zero base velocity (harnessed lab OK if noted). |
| Test method | Timed stance run; no tip-over / knee buckle. |

#### SW-BAL-002

| Attribute | Value |
| --- | --- |
| Level | Host |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SW |
| Verification | Test |
| Statement | Host software shall publish balance outer-loop references / stance mode to the RT layer at ≥ 50 Hz while Stand is active. |
| Test method | Topic rate ≥ 50 Hz for ≥ 30 s. |

#### SW-BAL-003

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-PARAM |
| Verification | Test |
| Statement | RT balance/stance control shall keep torso pitch/roll within ±5° of the commanded upright reference during undisturbed stance (≥ 95% samples over 60 s). |
| Test method | Log attitude vs reference. |

#### SW-BAL-004

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-PARAM |
| Verification | Test |
| Statement | RT software shall recover from a documented small disturbance (lab push / 20 N·s equivalent) to SW-BAL-003 limits within 3.0 s without FallDetected in ≥ 8 of 10 trials. |
| Test method | Instrumented or documented push protocol. |

#### SW-BAL-005

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP (safety) |
| Verification | Test |
| Statement | FallDetected shall assert within 100 ms when torso pitch/roll exceeds ±25° from upright in Stand. |
| Test method | Controlled tilt / IMU override. |

#### SW-BAL-006

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP |
| Verification | Demonstration |
| Statement | On FallDetected, software shall enter protective stop: clear locomotion intent and reduce drive/module torque demand per HR-SAFE / SW-SAF within 50 ms. |
| Test method | Harnessed demo + logs. |

#### SW-BAL-007

| Attribute | Value |
| --- | --- |
| Level | Host |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-PARAM |
| Verification | Demonstration |
| Statement | Host software shall support commanded Sit/Stand transitions that sequence RT modes without unsupported free-balance commands mid-transition. |
| Test method | Operator Sit then Stand; no FallDetected. |

---

### 4.3 Timing — SW-TIM

#### SW-TIM-001

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SW (deterministic control) |
| Verification | Test |
| Statement | RT balance loop shall run at 1.0 ms ± 0.1 ms (1 kHz) while Stand is active, or at the module-master cycle documented in HR-ICD if a COTS master replaces a bare MCU — but not slower than 2 ms without a written waiver. |
| Test method | GPIO / timestamp stats ≥ 10 s. |

#### SW-TIM-002

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SW |
| Verification | Test |
| Statement | Host→RT balance references shall arrive with end-to-end latency ≤ 20 ms (95th) under nominal host load. |
| Test method | Synchronized latency probe. |

#### SW-TIM-003

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SW |
| Verification | Test |
| Statement | Actuator command updates for stance-critical joints shall meet the bus cycle agreed in HR-ICD (EtherCAT ~1 ms preferred; CAN-FD as reviewed). |
| Test method | Capture bus/command period. |

#### SW-TIM-004

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP |
| Verification | Test |
| Statement | If host balance references are older than 100 ms, RT shall hold ≤ 200 ms then enter SafeStance/SafeStop. |
| Test method | Link stall fault injection. |

---

### 4.4 Interfaces — SW-COM

#### SW-COM-001

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-MOD, SYS-SW |
| Verification | Inspection |
| Statement | Jetson/host↔RT and module buses shall follow HR-ICD v0.2: versioned messages, SI units, mode/fault/heartbeat set. |
| Test method | Inspect ICD vs implementation headers/IDL. |

#### SW-COM-002

| Attribute | Value |
| --- | --- |
| Level | Host |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-MOD |
| Verification | Test |
| Statement | Host software shall reject unsupported ICD schema versions and log a fault without applying contents to motion commands. |
| Test method | Inject bad version. |

#### SW-COM-003

| Attribute | Value |
| --- | --- |
| Level | Adapter |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SW |
| Verification | Inspection |
| Statement | Adapters for EtherCAT or CAN-FD modules shall document endianness, scaling, and cycle time in HR-ICD annex or module profile. |
| Test method | Inspect module profile document. |

#### SW-COM-004

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SW |
| Verification | Test |
| Statement | RT shall publish telemetry to host at ≥ 100 Hz including joint summary, attitude, mode, and faults while linked. |
| Test method | Record rate and fields ≥ 30 s. |

---

### 4.5 Estimation — SW-EST

#### SW-EST-001

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-PARAM |
| Verification | Test |
| Statement | RT shall update torso attitude from IMU + joint feedback every balance cycle. |
| Test method | Update rate + tilt fixture check. |

#### SW-EST-002

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP |
| Verification | Test |
| Statement | IMU invalid/missing > 10 RT cycles ⇒ SensorInvalid and SafeStop. |
| Test method | Disconnect/invalidate IMU. |

#### SW-EST-003

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP |
| Verification | Test |
| Statement | Joint feedback older than 5 ms (or one agreed bus cycle) shall be stale and not used for balance torque computation. |
| Test method | Delay/drop joint packets. |

---

### 4.6 Safety software — SW-SAF

#### SW-SAF-001

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP |
| Verification | Test |
| Statement | RT watchdog shall expect host heartbeat ≤ every 50 ms; loss > 100 ms ⇒ SafeStop. |
| Test method | Stop heartbeat; measure trip. |

#### SW-SAF-002

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP |
| Verification | Test |
| Statement | RT shall enforce configurable per-joint torque/current limits with saturation and LimitClamp events. |
| Test method | Over-limit command test. |

#### SW-SAF-003

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP |
| Verification | Demonstration |
| Statement | SafeStop shall zero locomotion intent, keep limits, and require explicit clear after condition removal. |
| Test method | Trigger from ≥ 3 causes. |

#### SW-SAF-004

| Attribute | Value |
| --- | --- |
| Level | Adapter |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP |
| Verification | Test |
| Statement | Module disable / STO request from RT shall remove torque-producing output within 20 ms where the module supports STO; otherwise within the supplier-stated bound documented in the module profile (waiver required if > 20 ms). |
| Test method | Assert disable; measure effort collapse. |

#### SW-SAF-005

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP |
| Verification | Demonstration |
| Statement | Operator E-stop shall be recognized in software ≤ 20 ms and lead to SafeStop + torque removal. |
| Test method | Press E-stop during stance. |

#### SW-SAF-006

| Attribute | Value |
| --- | --- |
| Level | RT |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP |
| Verification | Test |
| Statement | Critical faults latch until authenticated clear after condition cleared. |
| Test method | Attempt auto-clear; verify latch. |

---

### 4.7 Logging — SW-LOG

#### SW-LOG-001

| Attribute | Value |
| --- | --- |
| Level | Host |
| Priority | Must |
| Phase | 0 |
| Parent | SYS-SUP |
| Verification | Test |
| Statement | Host shall log mode changes, FallDetected, SafeStop, SensorInvalid, WatchdogTrip, E-stop with monotonic timestamps. |
| Test method | Induce each event. |

#### SW-LOG-002

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Should |
| Phase | 0 |
| Parent | SYS-SW |
| Verification | Demonstration |
| Statement | System should retain ≥ 30 s high-rate balance telemetry dumpable after SafeStop. |
| Test method | Dump ring buffer post-stop. |

---

### 4.8 Mobility and manipulation (Phase-1) — SW-MOB / SW-MAN

#### SW-MOB-001

| Attribute | Value |
| --- | --- |
| Level | Host |
| Priority | Should |
| Phase | 1 |
| Parent | SYS-PARAM (walking 1.0 m/s) |
| Verification | Test |
| Statement | Host software should provide a walking/gait interface that commands the lower-body module toward ≥ 1.0 m/s forward walk on level ground once legs are integrated. |
| Test method | Deferred until leg module selected. |

#### SW-MAN-001

| Attribute | Value |
| --- | --- |
| Level | Host |
| Priority | Should |
| Phase | 1 |
| Parent | SYS-ARM, SYS-SW |
| Verification | Demonstration |
| Statement | Host software should plan and execute arm motions via MoveIt 2 (or equivalent) against the platform URDF once arm adapters are available. |
| Test method | Plan/execute stub or real arm trajectory. |

#### SW-MAN-002

| Attribute | Value |
| --- | --- |
| Level | Host |
| Priority | Should |
| Phase | 1 |
| Parent | SYS-PARAM (payload) |
| Verification | Test |
| Statement | Manipulation software should enforce software payload/reach limits consistent with SyRS rated figures and the selected arm module profile. |
| Test method | Reject commands beyond configured envelope. |

---

## 5. Traceability summary

| SW group | Parent tags | Notes |
| --- | --- | --- |
| SW-MOD-* | SYS-MOD, SYS-SW | Core SyRS modularity |
| SW-BAL-*, SW-TIM-*, SW-EST-* | SYS-PARAM, SYS-SW, SYS-SUP | Phase-0 stance |
| SW-COM-* | SYS-MOD, SYS-SW | ICD-backed |
| SW-SAF-*, SW-LOG-* | SYS-SUP | Aligns HR-SAFE |
| SW-MOB-*, SW-MAN-* | SYS-PARAM, SYS-ARM, SYS-SW | Phase-1 |

---

## 6. Open items

1. Assign formal `SYS-xxx` IDs inside HR-SRS-SYS and replace section tags.
2. Freeze host hardware (Jetson Orin-class vs other) and RT topology per selected limbs.
3. Complete arm/leg module profiles after supplier down-select.
4. Promote Phase-1 items to Must when SyRS stage schedule reaches them.

---

## 7. Document history

| Version | Date | Notes |
| --- | --- | --- |
| 0.1 | 2026-11-24 | Balance-first draft with provisional SYS-* |
| 0.2 | 2026-11-25 | Re-baselined to HR-SRS-SYS v0.1; HAL/modularity; phased MOB/MAN |
