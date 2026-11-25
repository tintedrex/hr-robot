# HR-SAFE — Safety Requirements

| Field | Value |
| --- | --- |
| Document ID | HR-SAFE |
| Version | 0.1 |
| Status | Draft |
| Date | 2026-11-25 |
| Standards (guidance) | ISO 13482 (personal care robots) · ISO 10218 (industrial robot safety) — engineering controls, not certification claim |
| System | Humanoid Robot (HR) |
| Related | HR-SRS-SW v0.1, HR-SAD v0.1, HR-ICD v0.1, HR-TEST-SW v0.1 |
| Google Doc | https://docs.google.com/document/d/1XlJmceu1TX94vy3Gg1vuONQEk5ou3MHaYhsmn0wl0OA/edit |
| Classification | Internal engineering draft |

---

## 1. Purpose and disclaimer

### 1.1 Purpose

Define safety-related requirements and risk-reduction measures for the HR software-controlled system during laboratory balance testing, aligned in spirit with ISO 13482 and ISO 10218 practices.

### 1.2 Disclaimer

This document does **not** constitute a certified compliance dossier for ISO 13482 or ISO 10218. It captures engineering safety requirements and maps them to HR-SRS-SW (`SW-SAF-*` and related). Formal PL/SIL assessment, notified-body review, and complete risk assessment files are out of scope for v0.1.

---

## 2. System context and assumptions

| Assumption | Implication |
| --- | --- |
| Lab use with trained operators | No public/personal-care unsupervised use in v0.1 |
| Overhead harness available for L4 tests | Limits fall energy during development |
| Level ground only | No stairs/slopes in v0.1 envelope |
| E-stop and STO hardware present | Software complements, does not replace, hardwired stop |
| MCU owns safety reactions | Jetson hang must not keep applying aggressive torque |

---

## 3. Safety functions (software-related)

| ID | Safety function | Trigger | Reaction | Max reaction time | SRS |
| --- | --- | --- | --- | --- | --- |
| SF-01 | Watchdog stop | Jetson heartbeat loss > 100 ms | SafeStop | Per SW-SAF-001 | SW-SAF-001 |
| SF-02 | Sensor invalid stop | IMU invalid > 10 MCU cycles | SafeStop | Per SW-EST-002 | SW-EST-002 |
| SF-03 | Fall detect | Torso tilt > ±25° | FallDetected → protective stop | Detect ≤ 100 ms; torque reduce ≤ 50 ms | SW-BAL-005, SW-BAL-006 |
| SF-04 | E-stop | Operator E-stop | SafeStop + drive torque off | ≤ 20 ms software path; STO ≤ 20 ms | SW-SAF-005, SW-SAF-004 |
| SF-05 | Torque limiting | Command > limit | Saturate + LimitClamp event | Same control cycle | SW-SAF-002 |
| SF-06 | Stale command stop | Drive cmd missing > 5 ms | Drive fault → MCU SafeStop path | One drive cycle visibility | SW-TIM-005 |
| SF-07 | Stale outer loop | Balance ref age policy | SafeStance/SafeStop | Per SW-TIM-004 | SW-TIM-004 |
| SF-08 | Fault latch | Critical faults | Remain until explicit clear | N/A | SW-SAF-006 |

---

## 4. Requirements (shall statements)

### 4.1 Protective stop and SafeStop

#### SAFE-001

| Attribute | Value |
| --- | --- |
| Priority | Must |
| Statement | The system shall provide a SafeStop software state that zeros locomotion intent, enforces torque limits, and requires explicit operator clear after the fault condition is removed. |
| Verification | Demonstration + Test |
| Related | SW-SAF-003, SW-SAF-006 |

#### SAFE-002

| Attribute | Value |
| --- | --- |
| Priority | Must |
| Statement | Activation of the operator E-stop shall be recognized by software within 20 ms and shall culminate in drive torque removal within the SW-SAF-004 bound. |
| Verification | Test |
| Related | SW-SAF-005, SW-SAF-004 |

#### SAFE-003

| Attribute | Value |
| --- | --- |
| Priority | Must |
| Statement | Safe Torque Off (or drive disable) requested by the MCU shall remove torque-producing output within 20 ms, with status observed by the MCU. |
| Verification | Test |
| Related | SW-SAF-004 |

### 4.2 Speed / force / stability related controls

#### SAFE-004

| Attribute | Value |
| --- | --- |
| Priority | Must |
| Statement | Per-joint torque (or current) limits shall be enforced in software on the MCU; excessive commands shall be saturated and counted. |
| Verification | Test |
| Related | SW-SAF-002, ISO 10218 force/speed limiting concepts (engineering analog) |

#### SAFE-005

| Attribute | Value |
| --- | --- |
| Priority | Must |
| Statement | During Stand mode, FallDetected shall be asserted within 100 ms of torso pitch/roll exceeding ±25° from upright. |
| Verification | Test |
| Related | SW-BAL-005; personal-care stability / falling hazard thinking (ISO 13482) |

#### SAFE-006

| Attribute | Value |
| --- | --- |
| Priority | Must |
| Statement | Undisturbed stance tests and powered motion shall not proceed without a verified E-stop and harness (or equivalent risk reduction) per the test plan suspension rules. |
| Verification | Inspection / Demonstration |
| Related | HR-TEST-SW |

### 4.3 Modes and collaborative-style restrictions (lab)

#### SAFE-007

| Attribute | Value |
| --- | --- |
| Priority | Must |
| Statement | Automatic resume after critical faults shall be prohibited; a deliberate clear command is required (SW-SAF-006). |
| Verification | Test |
| Related | SW-SAF-006 |

#### SAFE-008

| Attribute | Value |
| --- | --- |
| Priority | Should |
| Statement | The operator interface should display balance health / fault state at least once per second while powered. |
| Verification | Demonstration |
| Related | SW-BAL-010 |

### 4.4 Sensing and diagnostics

#### SAFE-009

| Attribute | Value |
| --- | --- |
| Priority | Must |
| Statement | Loss of IMU validity beyond the SRS threshold shall force SafeStop; balance control shall not continue blind. |
| Verification | Test |
| Related | SW-EST-002 |

#### SAFE-010

| Attribute | Value |
| --- | --- |
| Priority | Must |
| Statement | Critical safety events shall be logged with timestamps suitable for post-event review. |
| Verification | Test |
| Related | SW-LOG-001 |

---

## 5. Risk register (initial, qualitative)

| Hazard | Cause example | Severity | Exposure | Risk reduction (v0.1) |
| --- | --- | --- | --- | --- |
| Tip-over / fall | Disturbance, sensor loss | High | Lab, harnessed | SF-03, SF-02, harness |
| Unexpected motion | Host hang, bad command | High | Lab | SF-01, SF-04, SF-05 |
| Crush / impact | Excess torque | High | Lab | SF-05, SF-04, STO |
| Silent fault | Missing logs | Medium | Lab | SF-10 / SAFE-010 |

Detailed numerical risk scoring (ISO 12100 style) is deferred; update before any unharnessed or public demo.

---

## 6. Operational rules (lab)

1. E-stop reachable by operator at all times during powered stance.
2. No unharnessed L4 tests until SF-01…SF-04 evidence recorded.
3. Only trained operators change mode clear / enable.
4. After any FallDetected or E-stop, inspect hardware before clear.
5. Do not bypass MCU safety authority with Jetson-only commands.

---

## 7. Traceability

| SAFE ID | SRS / other |
| --- | --- |
| SAFE-001 | SW-SAF-003, SW-SAF-006 |
| SAFE-002 | SW-SAF-005, SW-SAF-004 |
| SAFE-003 | SW-SAF-004 |
| SAFE-004 | SW-SAF-002 |
| SAFE-005 | SW-BAL-005, SW-BAL-006 |
| SAFE-006 | HR-TEST-SW suspension rules |
| SAFE-007 | SW-SAF-006 |
| SAFE-008 | SW-BAL-010 |
| SAFE-009 | SW-EST-002 |
| SAFE-010 | SW-LOG-001 |

---

## 8. Open items (toward certification-oriented work)

1. Full ISO 12100 hazard analysis and risk estimation.
2. PLr / SIL targets if productizing beyond lab.
3. Validation per ISO 13482 / 10218 clauses with independent review.
4. Mechanical pinch-point guards and collaborative workspace definition.
5. Battery / electrical safety linkage to software enable chain.

---

## 9. Document history

| Version | Date | Notes |
| --- | --- | --- |
| 0.1 | 2026-11-25 | Initial lab-focused safety requirements mapped to SRS |
