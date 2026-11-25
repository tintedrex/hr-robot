# HR-TEST-SW — Software Test Plan

| Field | Value |
| --- | --- |
| Document ID | HR-TEST-SW |
| Version | 0.1 |
| Status | Draft |
| Date | 2026-11-25 |
| Standard | IEEE 829 (test documentation) |
| System | Humanoid Robot (HR) software |
| Related | HR-SRS-SW v0.1, HR-SAD v0.1, HR-ICD v0.1 |
| Google Doc | https://docs.google.com/document/d/1LsWwxxnh3zkzsrSEet2SOepofPLYDHwFdMnZ5n7l0dY/edit |
| Classification | Internal engineering draft |

---

## 1. Introduction (IEEE 829)

### 1.1 Objectives

Verify that HR software meets HR-SRS-SW v0.1 for the balance baseline across Jetson, MCU, and drives, using the verification methods stated per requirement (Test, Analysis, Inspection, Demonstration).

### 1.2 Background

HR uses a three-level control stack (Jetson / RT MCU / drives). v0.1 focuses on upright stance, disturbance recovery, SafeStop / FallDetected, and interface timing.

### 1.3 Scope

**In scope:** SW-BAL, SW-TIM, SW-COM, SW-EST, SW-SAF, SW-LOG requirements in HR-SRS-SW v0.1; ROS 2 package smoke builds; ICD field checks.

**Out of scope:** Full gait regression, ML model accuracy suites, formal safety certification tests, mechanical durability.

### 1.4 References

- IEEE 829
- HR-SRS-SW v0.1
- HR-SAD v0.1
- HR-ICD v0.1
- HR-SAFE v0.1 (safety-related test hooks)

---

## 2. Test items

| ID | Item | Location |
| --- | --- | --- |
| TI-01 | Jetson ROS 2 workspace build | `hr-robot` / Docker `hr-robot:humble-dev` |
| TI-02 | `hr_balance_jetson` outer loop | Jetson |
| TI-03 | MCU balance / watchdog / estimation firmware | MCU image under test |
| TI-04 | Drive command/feedback path | Bench drives or HIL |
| TI-05 | Jetson↔MCU ICD bridge | Integration build |
| TI-06 | E-stop / SafeStop software path | System harness |

---

## 3. Features to be tested

| Feature | SRS IDs | Level |
| --- | --- | --- |
| Upright stance hold | SW-BAL-001, SW-BAL-003 | System / MCU |
| Outer-loop rate | SW-BAL-002 | Jetson |
| Disturbance recovery | SW-BAL-004 | MCU |
| Fall detect + safe-stop | SW-BAL-005, SW-BAL-006 | MCU / System |
| Sit / Stand transitions | SW-BAL-007 | Jetson |
| Drive torque tracking | SW-BAL-009 | Drives |
| Timing budgets | SW-TIM-001 … SW-TIM-005 | MCU / System / Drives |
| ICD versioning & telemetry | SW-COM-001 … SW-COM-005 | System / Jetson / MCU / Drives |
| Sensor validity | SW-EST-001 … SW-EST-003 | MCU |
| Safety / latch | SW-SAF-001 … SW-SAF-006 | MCU / Drives / System |
| Logging | SW-LOG-001 … SW-LOG-004 | Jetson / MCU / System |

---

## 4. Features not tested (v0.1)

- Walking, turning, push catalog beyond SW-BAL-004 envelope
- Perception ML accuracy
- Long-duration soak beyond stated stance duration
- Cybersecurity penetration of links

---

## 5. Approach

### 5.1 Levels

| Level | What | Where |
| --- | --- | --- |
| L1 Build | `colcon build`, message generation | CI + Docker |
| L2 SIL | Jetson nodes + logged fake MCU topics | Dev PC / Docker |
| L3 HIL | MCU + drives on bench, Jetson linked | Lab rack |
| L4 System | Harnessed robot on level floor | Lab cell |

### 5.2 Methods mapping

| Method | Use |
| --- | --- |
| Test | Measured pass/fail (rates, angles, latencies) |
| Analysis | Limiters / CoP constraints offline |
| Inspection | ICD / schemas / enums |
| Demonstration | Observed SafeStop / Sit-Stand sequences |

### 5.3 Tools

- ROS 2 Humble, `ros2 topic hz`, bag record
- Logic analyzer / GPIO toggle for MCU period
- Calibrated push fixture (or documented lab equivalent)
- Fault injection: drop heartbeat, invalidate IMU, stall drive commands

---

## 6. Pass / fail criteria

| Criterion | Pass rule |
| --- | --- |
| Requirement claim | All Must items in scope have recorded evidence matching SRS test method |
| Build | CI `humble-build` green on PR |
| Safety-critical demos | E-stop, WatchdogTrip, SensorInvalid, FallDetected each demonstrated once with logs |
| No critical regressions | No unexpected FallDetected during undisturbed SW-BAL-001 run |

Should items may be deferred with waiver note.

---

## 7. Suspension / resumption

**Suspend** if: uncontrolled fall risk without harness; E-stop path fails; drive STO non-functional; missing calibrated sensors.

**Resume** after: hazard cleared, root cause logged, harness verified, related SW-SAF cases re-run.

---

## 8. Test deliverables (IEEE 829 set for v0.1)

| Deliverable | Notes |
| --- | --- |
| This Test Plan (HR-TEST-SW) | v0.1 |
| Test Design specs | Per feature group (BAL/TIM/…) — short tables OK |
| Test Case specs | IDs TC-BAL-001 … linked to SW-* |
| Test logs / bags | Stored under `test/evidence/` (TBD repo path) |
| Test Summary Report | After v0.1 execution campaign |

---

## 9. Test cases (initial set)

### 9.1 Build / smoke

| TC ID | Title | Steps (summary) | Expected | SRS |
| --- | --- | --- | --- | --- |
| TC-BLD-001 | Docker colcon build | `docker compose build && run colcon build` | Exit 0 | — |
| TC-BLD-002 | Launch bringup | `ros2 launch hr_bringup bringup.launch.py` | Node up; topics alive | SW-BAL-002 |

### 9.2 Balance

| TC ID | Title | Expected | SRS |
| --- | --- | --- | --- |
| TC-BAL-001 | 60 s undisturbed stance | Upright ≥ 60 s | SW-BAL-001 |
| TC-BAL-002 | Reference ≥ 50 Hz | `ros2 topic hz` ≥ 50 | SW-BAL-002 |
| TC-BAL-003 | Attitude within ±5° | Log analysis | SW-BAL-003 |
| TC-BAL-004 | Push recovery 8/10 | Recover ≤ 3 s | SW-BAL-004 |
| TC-BAL-005 | Fall detect ≤ 100 ms | Inject tilt | SW-BAL-005 |
| TC-BAL-006 | Fall safe-stop sequence | Torque down ≤ 50 ms | SW-BAL-006 |
| TC-BAL-007 | Sit/Stand demo | Completes without FallDetected | SW-BAL-007 |
| TC-BAL-009 | Drive torque error ≤ 5% | Bench step | SW-BAL-009 |

### 9.3 Timing / COM / EST / SAF / LOG

| TC ID | Title | SRS |
| --- | --- | --- |
| TC-TIM-001 | MCU loop 1 ms ± 0.1 | SW-TIM-001 |
| TC-TIM-002 | Jetson→MCU latency ≤ 20 ms p95 | SW-TIM-002 |
| TC-TIM-003 | Drive cmd ≤ 2 ms | SW-TIM-003 |
| TC-TIM-004 | Stale reference → SafeStop | SW-TIM-004 |
| TC-TIM-005 | Missed drive cmd fault | SW-TIM-005 |
| TC-COM-001 | ICD inspection | SW-COM-001 |
| TC-COM-002 | Bad schema rejected | SW-COM-002 |
| TC-EST-002 | IMU loss → SafeStop | SW-EST-002 |
| TC-SAF-001 | Heartbeat loss → SafeStop | SW-SAF-001 |
| TC-SAF-004 | STO torque off ≤ 20 ms | SW-SAF-004 |
| TC-SAF-005 | E-stop ≤ 20 ms | SW-SAF-005 |
| TC-SAF-006 | Fault latch until clear | SW-SAF-006 |
| TC-LOG-001 | Events logged | SW-LOG-001 |

---

## 10. Environmental needs

- Level floor cell with overhead harness
- Jetson + MCU + drives powered per HW checklist
- E-stop pendant tested before motion
- Docker Desktop (dev) / CI Ubuntu 22.04

---

## 11. Responsibilities

| Role | Responsibility |
| --- | --- |
| V&V lead | Plan execution, summary report |
| Jetson software | L1/L2 evidence |
| MCU / real-time | L3 timing and safety cases |
| Drives owner | Torque / STO bench cases |
| Project lead | Go/no-go for L4 |

---

## 12. Schedule (indicative)

| Window | Activity |
| --- | --- |
| Wk 1–2 | L1 CI + L2 SIL smoke |
| Wk 3 | L3 HIL timing / ICD |
| Wk 4 | L4 harnessed stance + summary |

---

## 13. Risks and contingencies

| Risk | Contingency |
| --- | --- |
| Hardware late | Continue SIL; defer L4 |
| No push fixture | Documented manual push with video + IMU |
| Flaky network timing | Wired link only for TIM tests |

---

## 14. Document history

| Version | Date | Notes |
| --- | --- | --- |
| 0.1 | 2026-11-25 | Initial IEEE 829-aligned plan for SRS v0.1 |
