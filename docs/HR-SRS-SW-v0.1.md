# HR-SRS-SW — Software Requirements Specification

| Field | Value |
| --- | --- |
| Document ID | HR-SRS-SW |
| Version | 0.1 |
| Status | Draft |
| Date | 2026-11-24 |
| Standard | ISO/IEC/IEEE 29148 (requirements engineering) |
| System | Humanoid Robot (HR) — default control stack |
| Classification | Internal engineering draft |

---

## 1. Purpose and scope

### 1.1 Purpose

This Software Requirements Specification (SRS) defines verifiable software requirements for the Humanoid Robot (HR) control software. Requirements are allocated by control level (Jetson, real-time MCU, motor drives) and are written so each requirement can be verified by Test, Analysis, Inspection, or Demonstration.

### 1.2 Scope (in)

- High-level control, planning, and orchestration software on an NVIDIA Jetson-class SoC.
- Hard real-time balance/stance and arbitration software on a real-time MCU.
- Drive-level servo command/feedback software interfaces and fault handling.
- Cross-cutting timing, communication, estimation, safety, and diagnostics needed for upright balance on level ground.

### 1.3 Scope (out)

- Mechanical design, structural FEA, and actuator sizing (covered by mechanical design docs).
- Pure electrical / PCB hardware requirements (covered by HW SRS).
- Full locomotion gait catalog, manipulation, and perception ML model training (deferred beyond v0.1 balance baseline).
- Formal functional-safety certification (ISO 13849 / IEC 61508) — safety requirements here are engineering controls only.

### 1.4 Intended audience

Software, controls, systems, and V&V engineers implementing and verifying HR software.

---

## 2. References

| ID | Reference |
| --- | --- |
| REF-001 | ISO/IEC/IEEE 29148 — Systems and software engineering — Life cycle processes — Requirements engineering |
| REF-002 | HR-SyRS (System Requirements) — placeholder upstream document (TBD); parent IDs `SYS-*` in this SRS are provisional |
| REF-003 | Platform assumption: NVIDIA Jetson Orin-class SoC running Linux + middleware (e.g. ROS 2) |
| REF-004 | Platform assumption: Real-time MCU (Cortex-M/R or equivalent) with hard real-time scheduler |
| REF-005 | Platform assumption: FOC-capable motor drives with torque/current/velocity modes and fault reporting |

---

## 3. Definitions and acronyms

| Term | Definition |
| --- | --- |
| CoM | Center of Mass |
| CoP | Center of Pressure |
| Drive | Motor drive / servo amplifier for one or more joints |
| E-stop | Emergency stop |
| FOC | Field-Oriented Control |
| Jetson | High-level compute SoC control level |
| MCU | Real-time microcontroller control level |
| STO | Safe Torque Off |
| Shall | Mandatory requirement (Must priority) |
| Should | Recommended requirement (Should priority) |
| SyRS | System Requirements Specification |
| Watchdog | Independent timeout that forces a safe reaction on missed heartbeats |

---

## 4. System overview

### 4.1 Control levels

```text
  [ Operator / UI ]
         |
    Jetson (high-level)
      planning, outer balance, logging, orchestration
         |  state estimates, trajectories, mode commands
         v
    RT MCU (mid-level)
      inner balance/stance, timing, watchdog, drive arbitration
         |  setpoints, limits, enable
         v
    Motor drives (low-level)
      current/torque/velocity servo, local faults, STO interface
         |  feedback, fault codes
         +----> MCU ----> Jetson (telemetry)
```

### 4.2 Assumptions

- Level ground, indoor lab environment for v0.1 balance verification.
- Bilateral lower-limb joints required for upright stance are driven and instrumented (position/velocity/torque or current).
- At least one body IMU is available to the MCU within the real-time loop.
- Jetson↔MCU link is deterministic enough to meet SW-TIM deadlines under nominal load.

### 4.3 Requirement attributes

Each software requirement includes:

| Attribute | Values |
| --- | --- |
| ID | `SW-<AREA>-NNN` |
| Level | Jetson \| MCU \| Drives \| System |
| Priority | Must \| Should |
| Statement | Shall/Should text |
| Rationale | One-line justification |
| Verification | Test \| Analysis \| Inspection \| Demonstration |
| Parent | Provisional `SYS-*` ID |

---

## 5. Software requirements

### 5.1 Balance — SW-BAL

#### SW-BAL-001

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Must |
| Parent | SYS-BAL-001 |
| Verification | Test |
| Statement | The HR software shall maintain upright bipedal stance on level ground for at least 60 s without external support when initialized in a standing pose with zero commanded base velocity. |
| Rationale | Establishes the baseline balance capability for v0.1. |
| Test method | Stand the robot on a level floor; command Stand mode; measure continuous upright stance duration ≥ 60 s with no tip-over or knee buckle. |

#### SW-BAL-002

| Attribute | Value |
| --- | --- |
| Level | Jetson |
| Priority | Must |
| Parent | SYS-BAL-001 |
| Verification | Test |
| Statement | The Jetson software shall provide a balance outer-loop that publishes desired CoM / torso orientation targets and stance mode commands to the MCU at a rate of at least 50 Hz while Stand mode is active. |
| Rationale | Outer loop sets the reference the MCU tracks. |
| Test method | Log Jetson→MCU balance reference messages; verify rate ≥ 50 Hz for ≥ 30 s in Stand mode. |

#### SW-BAL-003

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-BAL-001 |
| Verification | Test |
| Statement | The MCU software shall execute an inner balance/stance controller that computes joint torque or velocity setpoints from IMU and joint feedback to keep torso pitch and roll within ±5° of the Jetson-commanded upright reference during undisturbed stance. |
| Rationale | Hard real-time inner loop is required for stable stance. |
| Test method | Undisturbed stance test; record torso pitch/roll vs reference; verify within ±5° for ≥ 95% of samples over 60 s. |

#### SW-BAL-004

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-BAL-002 |
| Verification | Test |
| Statement | The MCU software shall reject balance disturbances equivalent to a horizontal impulse at the torso of 20 N·s (or lab-equivalent push) such that the robot recovers to within SW-BAL-003 limits within 3.0 s without entering FallDetected state, for at least 8 of 10 trials. |
| Rationale | Small disturbance recovery is part of usable stance. |
| Test method | Instrumented push or calibrated impulse; 10 trials; count recoveries meeting timing and angle criteria. |

#### SW-BAL-005

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-BAL-003 |
| Verification | Test |
| Statement | The MCU software shall enter FallDetected state within 100 ms when torso pitch or roll exceeds ±25° from upright while Stand mode is active. |
| Rationale | Early fall detection enables safe stop. |
| Test method | Controlled tilt or simulated IMU override; measure latency from threshold crossing to FallDetected assertion. |

#### SW-BAL-006

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Must |
| Parent | SYS-BAL-003 |
| Verification | Demonstration |
| Statement | Upon FallDetected, the software shall command a safe-stop sequence that removes locomotion intent, applies MCU-defined protective joint limits, and signals drives to reduce torque demand per SW-SAF-004 within 50 ms of FallDetected. |
| Rationale | Fall must not continue applying aggressive balance torques. |
| Test method | Trigger FallDetected in a harnessed demo; verify sequence timing and torque reduction on logs. |

#### SW-BAL-007

| Attribute | Value |
| --- | --- |
| Level | Jetson |
| Priority | Must |
| Parent | SYS-BAL-004 |
| Verification | Demonstration |
| Statement | The Jetson software shall support commanded Sit and Stand transitions that sequence MCU stance modes and inhibit unsupported mid-transition free balance commands. |
| Rationale | Controlled transitions reduce tip risk. |
| Test method | Operator commands Sit then Stand; verify mode sequence on logs and successful completion without FallDetected. |

#### SW-BAL-008

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-BAL-001 |
| Verification | Analysis |
| Statement | The MCU software shall enforce CoP / support-polygon constraints (or equivalent ankle/hip torque limits) so commanded setpoints do not request statically infeasible stance on level ground under the documented mass model. |
| Rationale | Prevents commanded self-destabilization. |
| Test method | Offline analysis of controller equations / limiters against the mass model; spot-check with stance logging. |

#### SW-BAL-009

| Attribute | Value |
| --- | --- |
| Level | Drives |
| Priority | Must |
| Parent | SYS-BAL-001 |
| Verification | Test |
| Statement | Each stance-critical drive shall track MCU torque (or current) setpoints with steady-state error ≤ 5% of commanded value at constant load within the drive’s continuous rating, when enabled and not faulted. |
| Rationale | Balance depends on faithful low-level torque delivery. |
| Test method | Bench torque/current step and hold; compare feedback vs command. |

#### SW-BAL-010

| Attribute | Value |
| --- | --- |
| Level | Jetson |
| Priority | Should |
| Parent | SYS-BAL-001 |
| Verification | Demonstration |
| Statement | The Jetson software should expose an operator status for balance health (Stand / Sit / Transition / FallDetected / Fault) updated at least once per second. |
| Rationale | Operators need clear balance state. |
| Test method | Exercise each state; verify UI/status topic updates within 1 s. |

---

### 5.2 Timing — SW-TIM

#### SW-TIM-001

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-TIM-001 |
| Verification | Test |
| Statement | The MCU balance control loop shall execute at a fixed period of 1.0 ms ± 0.1 ms (1 kHz) while Stand mode is active. |
| Rationale | Deterministic inner-loop timing for balance. |
| Test method | Timestamp loop start events with a hardware timer or GPIO toggle; measure period statistics over ≥ 10 s. |

#### SW-TIM-002

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Must |
| Parent | SYS-TIM-001 |
| Verification | Test |
| Statement | Jetson→MCU balance reference messages shall arrive with end-to-end latency ≤ 20 ms (95th percentile) under nominal Jetson CPU load defined in the test plan. |
| Rationale | Outer-loop freshness bound. |
| Test method | Synchronized timestamps or round-trip probe; compute latency distribution. |

#### SW-TIM-003

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-TIM-002 |
| Verification | Test |
| Statement | The MCU shall send drive setpoints to all stance-critical drives at a period ≤ 2.0 ms while Stand mode is active. |
| Rationale | Drives need timely commands. |
| Test method | Capture bus/command timestamps; verify period ≤ 2 ms. |

#### SW-TIM-004

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-TIM-002 |
| Verification | Test |
| Statement | If a Jetson balance reference is older than 100 ms, the MCU shall hold the last valid reference for at most 200 ms additional, then enter a degraded SafeStance or SafeStop mode per SW-SAF-003. |
| Rationale | Stale outer-loop data must not run indefinitely. |
| Test method | Fault-inject link stall; measure MCU mode transitions and timing. |

#### SW-TIM-005

| Attribute | Value |
| --- | --- |
| Level | Drives |
| Priority | Must |
| Parent | SYS-TIM-001 |
| Verification | Test |
| Statement | Each drive shall report that a missed command deadline (no valid setpoint within 5 ms of expected period) raises a drive communication fault visible to the MCU within one subsequent drive cycle. |
| Rationale | Detects lost command streams early. |
| Test method | Stop MCU command stream; verify fault assertion timing. |

---

### 5.3 Interfaces / communication — SW-COM

#### SW-COM-001

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Must |
| Parent | SYS-COM-001 |
| Verification | Inspection |
| Statement | The Jetson↔MCU interface shall define a versioned message set including at minimum: stance mode, balance references, joint state, IMU summary, fault bitfield, and heartbeat. |
| Rationale | Stable ICD is required for integration. |
| Test method | Inspect ICD document/schema against this list; version field present. |

#### SW-COM-002

| Attribute | Value |
| --- | --- |
| Level | Jetson |
| Priority | Must |
| Parent | SYS-COM-001 |
| Verification | Test |
| Statement | The Jetson software shall reject MCU messages with unsupported schema version and shall log an interface-version fault without applying their contents to balance commands. |
| Rationale | Prevents silent misinterpretation. |
| Test method | Inject wrong version; verify reject + log + no command apply. |

#### SW-COM-003

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-COM-001 |
| Verification | Inspection |
| Statement | MCU↔drive framing shall specify endianness, units (SI), and scaling for position, velocity, torque/current, and fault codes in a single interface control document. |
| Rationale | Avoids unit/scale bugs at the drive boundary. |
| Test method | Inspect ICD; confirm fields and SI units. |

#### SW-COM-004

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-COM-002 |
| Verification | Test |
| Statement | The MCU shall publish telemetry to Jetson at ≥ 100 Hz including joint positions, estimated torso attitude, active mode, and latched faults while powered and communicating. |
| Rationale | High-level monitoring and logging need fresh state. |
| Test method | Record telemetry rate and required fields for ≥ 30 s. |

#### SW-COM-005

| Attribute | Value |
| --- | --- |
| Level | Drives |
| Priority | Must |
| Parent | SYS-COM-002 |
| Verification | Test |
| Statement | Each drive shall provide feedback of position, velocity, measured torque or current, and fault status at the MCU command period when enabled. |
| Rationale | Inner loop and diagnostics require drive feedback. |
| Test method | Capture drive feedback stream; verify fields and period. |

---

### 5.4 Sensing / estimation — SW-EST

#### SW-EST-001

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-EST-001 |
| Verification | Test |
| Statement | The MCU shall fuse body IMU and joint feedback into a torso attitude estimate updated every balance loop period (SW-TIM-001). |
| Rationale | Balance feedback depends on timely attitude. |
| Test method | Log estimate update rate; compare against known tilt fixture within specified accuracy in the test plan. |

#### SW-EST-002

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-EST-001 |
| Verification | Test |
| Statement | If IMU data is missing or marked invalid for more than 10 consecutive MCU cycles, the MCU shall assert SensorInvalid and transition to SafeStop per SW-SAF-003. |
| Rationale | Blind balance is unsafe. |
| Test method | Disconnect or invalidate IMU; verify SensorInvalid and SafeStop timing. |

#### SW-EST-003

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-EST-002 |
| Verification | Test |
| Statement | Joint feedback older than 5 ms shall be treated as stale; the MCU shall not use stale joint data for balance torque computation and shall raise JointFeedbackStale. |
| Rationale | Stale joints corrupt the inner loop. |
| Test method | Delay or drop joint packets; verify flag and that setpoints freeze/safe behavior per design. |

#### SW-EST-004

| Attribute | Value |
| --- | --- |
| Level | Jetson |
| Priority | Should |
| Parent | SYS-EST-001 |
| Verification | Demonstration |
| Statement | The Jetson software should run a parallel state estimator for logging and outer-loop references, but shall not bypass MCU SensorInvalid / SafeStop decisions. |
| Rationale | Outer estimate aids planning; safety authority stays on MCU. |
| Test method | Force MCU SensorInvalid while Jetson estimator still runs; verify SafeStop remains authoritative. |

---

### 5.5 Safety / faults — SW-SAF

#### SW-SAF-001

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-SAF-001 |
| Verification | Test |
| Statement | The MCU shall run a watchdog that expects a Jetson heartbeat at least every 50 ms; missed heartbeat beyond 100 ms shall force SafeStop. |
| Rationale | Detects high-level host hang. |
| Test method | Stop Jetson heartbeat; measure time to SafeStop. |

#### SW-SAF-002

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-SAF-002 |
| Verification | Test |
| Statement | The MCU shall enforce per-joint torque (or current) limits configurable in N·m (or A); commands exceeding limits shall be saturated and counted as LimitClamp events. |
| Rationale | Prevents over-torque from software faults. |
| Test method | Command over-limit setpoints; verify saturation and event counters. |

#### SW-SAF-003

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-SAF-001 |
| Verification | Demonstration |
| Statement | SafeStop mode shall set locomotion intent to zero, hold or collapse to a defined protective posture policy, and keep drives within SW-SAF-002 limits until an explicit operator clear is received. |
| Rationale | Common safe reaction for multiple fault paths. |
| Test method | Trigger SafeStop from at least three causes (heartbeat loss, sensor invalid, FallDetected path); verify common behavior. |

#### SW-SAF-004

| Attribute | Value |
| --- | --- |
| Level | Drives |
| Priority | Must |
| Parent | SYS-SAF-003 |
| Verification | Test |
| Statement | When the MCU asserts drive disable or STO request, each drive shall remove torque-producing output within 20 ms, and the MCU shall observe the corresponding drive status. |
| Rationale | Fast torque removal on safety request. |
| Test method | Assert disable/STO; measure torque/current collapse and status bit timing. |

#### SW-SAF-005

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Must |
| Parent | SYS-SAF-004 |
| Verification | Demonstration |
| Statement | An operator E-stop input shall be recognized by software within 20 ms and shall result in MCU SafeStop and drive torque removal per SW-SAF-004. |
| Rationale | Operator must be able to halt the robot. |
| Test method | Press E-stop during stance; verify timing and SafeStop/torque removal. |

#### SW-SAF-006

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-SAF-001 |
| Verification | Test |
| Statement | Critical faults (FallDetected, SensorInvalid, WatchdogTrip, E-stop) shall latch until cleared by an authenticated operator command after the fault condition is no longer present. |
| Rationale | Prevents automatic unsafe re-enable. |
| Test method | Raise each fault; attempt auto-clear; verify latch until clear command. |

---

### 5.6 Logging / diagnostics — SW-LOG

#### SW-LOG-001

| Attribute | Value |
| --- | --- |
| Level | Jetson |
| Priority | Must |
| Parent | SYS-LOG-001 |
| Verification | Test |
| Statement | The Jetson software shall record timestamped events for mode changes, FallDetected, SafeStop, SensorInvalid, WatchdogTrip, and E-stop with monotonic timestamps suitable for post-event review. |
| Rationale | Debugging and V&V evidence. |
| Test method | Induce each event; verify log entries and ordering. |

#### SW-LOG-002

| Attribute | Value |
| --- | --- |
| Level | MCU |
| Priority | Must |
| Parent | SYS-LOG-001 |
| Verification | Inspection |
| Statement | The MCU shall maintain a fault code enumeration shared with Jetson (ICD) covering at minimum the faults named in SW-LOG-001 plus drive communication faults. |
| Rationale | Common language for diagnostics. |
| Test method | Inspect shared enum/ICD against required set. |

#### SW-LOG-003

| Attribute | Value |
| --- | --- |
| Level | System |
| Priority | Should |
| Parent | SYS-LOG-001 |
| Verification | Demonstration |
| Statement | The system should retain at least the last 30 s of high-rate balance telemetry (joint state, attitude, setpoints) in a ring buffer dumpable after SafeStop. |
| Rationale | Post-fall analysis. |
| Test method | Run stance ≥ 30 s; trigger SafeStop; dump buffer; verify coverage. |

#### SW-LOG-004

| Attribute | Value |
| --- | --- |
| Level | Drives |
| Priority | Must |
| Parent | SYS-LOG-001 |
| Verification | Test |
| Statement | Drive fault codes reported to the MCU shall be forwarded to Jetson telemetry within 50 ms of MCU receipt. |
| Rationale | Operators see drive faults promptly. |
| Test method | Inject drive fault; measure Jetson visibility latency. |

---

## 6. Traceability (provisional)

| SW ID | Parent SYS ID | Capability |
| --- | --- | --- |
| SW-BAL-001 … SW-BAL-010 | SYS-BAL-001 … SYS-BAL-004 | Upright balance / stance / transitions / fall |
| SW-TIM-001 … SW-TIM-005 | SYS-TIM-001 … SYS-TIM-002 | Real-time timing and deadlines |
| SW-COM-001 … SW-COM-005 | SYS-COM-001 … SYS-COM-002 | Control-level interfaces |
| SW-EST-001 … SW-EST-004 | SYS-EST-001 … SYS-EST-002 | Sensing and estimation |
| SW-SAF-001 … SW-SAF-006 | SYS-SAF-001 … SYS-SAF-004 | Watchdog, limits, SafeStop, E-stop |
| SW-LOG-001 … SW-LOG-004 | SYS-LOG-001 | Diagnostics and post-event data |

Replace provisional `SYS-*` IDs when HR-SyRS is baselined.

---

## 7. Requirements summary by level

| Level | Requirement IDs |
| --- | --- |
| System | SW-BAL-001, SW-BAL-006, SW-TIM-002, SW-COM-001, SW-SAF-005, SW-LOG-003 |
| Jetson | SW-BAL-002, SW-BAL-007, SW-BAL-010, SW-COM-002, SW-EST-004, SW-LOG-001 |
| MCU | SW-BAL-003, SW-BAL-004, SW-BAL-005, SW-BAL-008, SW-TIM-001, SW-TIM-003, SW-TIM-004, SW-COM-003, SW-COM-004, SW-EST-001, SW-EST-002, SW-EST-003, SW-SAF-001, SW-SAF-002, SW-SAF-003, SW-SAF-006, SW-LOG-002 |
| Drives | SW-BAL-009, SW-TIM-005, SW-COM-005, SW-SAF-004, SW-LOG-004 |

**Count:** 34 requirements (Must: 31, Should: 3).

---

## 8. Verification methods legend

| Method | Meaning |
| --- | --- |
| Test | Measured against pass/fail criteria under controlled conditions |
| Analysis | Calculation, review of algorithms/limits, or offline simulation evidence |
| Inspection | Review of documents, schemas, or code/ICD artifacts |
| Demonstration | Observed scenario showing required behavior without full metrology |

---

## 9. Open items (v0.2+)

1. Baseline HR-SyRS and replace provisional `SYS-*` parents.
2. Quantify mass model, friction, and exact push-test fixture for SW-BAL-004.
3. Define Sit/Stand kinematic waypoints and harness policy.
4. Select concrete buses (e.g. EtherCAT, CAN-FD) and fold into SW-COM ICD.
5. Align SW-SAF with any formal functional-safety goals if required.
6. Expand beyond balance: walk, turn, push recovery catalog, arm/manipulation software requirements.

---

## 10. Document history

| Version | Date | Author | Notes |
| --- | --- | --- | --- |
| 0.1 | 2026-11-24 | HR software (draft) | Initial SRS: Jetson / MCU / drives; balance-first baseline |
