# HR-TEST-SW — Software Test Plan

| Field | Value |
| --- | --- |
| Document ID | HR-TEST-SW |
| Version | 0.2 |
| Status | Draft |
| Date | 2026-11-25 |
| Standard | IEEE 829 |
| Parent | HR-SRS-SYS v0.1 |
| Related | HR-SRS-SW v0.2, HR-ICD v0.2, HR-SAFE v0.2 |
| Google Doc | https://docs.google.com/document/d/1LsWwxxnh3zkzsrSEet2SOepofPLYDHwFdMnZ5n7l0dY/edit |
| Classification | Internal engineering draft |

---

## 1. Objectives and scope

Verify **HR-SRS-SW v0.2** Phase-0 (HAL, ICD, balance, safety) and prepare hooks for Phase-1 (walk/manip). Align evidence with SyRS modular integration sequence.

**In:** Build/CI, adapter identity, IF-HR/IF-BUS behaviours, stance/SafeStop, module profile inspections.  
**Out:** Full SyRS payload benchmarking (system test); commercial acceptance of suppliers; ML metrics.

---

## 2. Test items

| ID | Item |
| --- | --- |
| TI-01 | `hr-robot` Docker / CI colcon build |
| TI-02 | HAL / capability API stubs |
| TI-03 | Host outer balance + bringup |
| TI-04 | RT balance / watchdog / estimation |
| TI-05 | Bus adapter (EtherCAT or CAN-FD) or HIL mock |
| TI-06 | Module identity + profile inspection |
| TI-07 | E-stop / STO path |

---

## 3. Features to be tested

| Feature | SRS | Phase |
| --- | --- | --- |
| HAL / no vendor in AI | SW-MOD-001/002 | 0 |
| Module identity | SW-MOD-003 | 0 |
| ROS 2 / ros2_control / URDF | SW-MOD-004…006 | 0 |
| Stance / fall / Sit-Stand | SW-BAL-* | 0 |
| Timing / stale | SW-TIM-* | 0 |
| ICD versioning / telemetry | SW-COM-* | 0 |
| Estimation safety | SW-EST-* | 0 |
| SafeStop / E-stop / latch | SW-SAF-* | 0 |
| Logging | SW-LOG-* | 0 |
| Walk / MoveIt (smoke) | SW-MOB-001, SW-MAN-* | 1 (when ready) |

---

## 4. Approach

| Level | Description |
| --- | --- |
| L1 Build | CI `humble-build` + Docker colcon |
| L2 SIL | Host nodes + mock RT/adapter |
| L3 HIL | Real bus + module or drive rack |
| L4 System | Harnessed biped stance |

Methods: Test / Analysis / Inspection / Demonstration per SRS.

---

## 5. Pass / fail

- All Phase-0 **Must** in the execution scope have recorded evidence.  
- CI green on PR.  
- SF paths in HR-SAFE (E-stop, watchdog, sensor invalid, fall) demonstrated with logs.  
- Phase-1 Should failures do not block Phase-0 exit.

---

## 6. Suspension

Suspend L3/L4 if E-stop/STO fails, uncontrolled fall risk without harness, or missing calibrated sensors. Resume after HR-SAFE checks and retest of related TC-SAF-*.

---

## 7. Deliverables

Test Plan (this), case list, logs/bags, summary report after campaign.

---

## 8. Test cases

### 8.1 Build / HAL / module

| TC ID | Title | Expected | SRS |
| --- | --- | --- | --- |
| TC-BLD-001 | Docker colcon build | Exit 0 | — |
| TC-BLD-002 | Bringup launch | Nodes/topics up | SW-MOD-004 |
| TC-MOD-001 | Capability API inspection | No vendor proto in AI pkgs | SW-MOD-001 |
| TC-MOD-002 | Adapter swap demo | AI unchanged | SW-MOD-002 |
| TC-MOD-003 | Module identity publish | Fields present | SW-MOD-003 |
| TC-MOD-005 | ros2_control smoke | Joint command works | SW-MOD-005 |
| TC-MOD-006 | URDF check | check_urdf pass | SW-MOD-006 |
| TC-MOD-010 | Module profile inspection | Profile complete vs ICD §7 | SW-COM-003 |

### 8.2 Balance / timing / safety (Phase-0)

| TC ID | Title | SRS |
| --- | --- | --- |
| TC-BAL-001 | 60 s stance | SW-BAL-001 |
| TC-BAL-002 | Ref ≥ 50 Hz | SW-BAL-002 |
| TC-BAL-003 | ±5° hold | SW-BAL-003 |
| TC-BAL-004 | Push 8/10 | SW-BAL-004 |
| TC-BAL-005 | Fall detect ≤ 100 ms | SW-BAL-005 |
| TC-BAL-006 | Protective stop | SW-BAL-006 |
| TC-BAL-007 | Sit/Stand | SW-BAL-007 |
| TC-TIM-001 | RT cycle | SW-TIM-001 |
| TC-TIM-002 | Host→RT latency | SW-TIM-002 |
| TC-TIM-003 | Bus cycle | SW-TIM-003 |
| TC-TIM-004 | Stale ref SafeStop | SW-TIM-004 |
| TC-COM-002 | Bad schema reject | SW-COM-002 |
| TC-EST-002 | IMU loss SafeStop | SW-EST-002 |
| TC-SAF-001 | Heartbeat loss | SW-SAF-001 |
| TC-SAF-004 | STO/disable timing | SW-SAF-004 |
| TC-SAF-005 | E-stop | SW-SAF-005 |
| TC-SAF-006 | Fault latch | SW-SAF-006 |
| TC-LOG-001 | Event log | SW-LOG-001 |

### 8.3 Phase-1 (deferred)

| TC ID | Title | SRS |
| --- | --- | --- |
| TC-MOB-001 | Walk interface smoke | SW-MOB-001 |
| TC-MAN-001 | MoveIt plan/execute | SW-MAN-001 |
| TC-MAN-002 | Payload envelope reject | SW-MAN-002 |

---

## 9. Environment

Harnessed cell; E-stop verified; Docker/CI; HIL bus tools as needed.

---

## 10. Responsibilities

| Role | Focus |
| --- | --- |
| V&V | Plan, summary |
| Host software | L1/L2, HAL |
| RT / adapters | L3 timing/safety |
| Procurement liaison | Module profile completeness |
| Lead | L4 go/no-go |

---

## 11. Schedule (indicative)

| Window | Activity |
| --- | --- |
| Near term | L1 + L2 HAL/balance SIL |
| Post arm down-select | L3 adapter + profile TCs |
| Leg integrate | L4 stance; later walk smoke |

---

## 12. Document history

| Version | Date | Notes |
| --- | --- | --- |
| 0.1 | 2026-11-25 | Balance-only plan |
| 0.2 | 2026-11-25 | SyRS HAL/module cases; Phase-1 hooks |
