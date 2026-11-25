# HR-SAFE — Safety Requirements

| Field | Value |
| --- | --- |
| Document ID | HR-SAFE |
| Version | 0.2 |
| Status | Draft |
| Date | 2026-11-25 |
| Standards (guidance) | ISO 13482 · ISO 10218 (engineering controls; **not** a certification claim) |
| Parent | HR-SRS-SYS v0.1 |
| Related | HR-SRS-SW v0.2, HR-ICD v0.2, HR-TEST-SW v0.2 |
| Google Doc | https://docs.google.com/document/d/1XlJmceu1TX94vy3Gg1vuONQEk5ou3MHaYhsmn0wl0OA/edit |
| Classification | Internal engineering draft |

---

## 1. Purpose and disclaimer

Define software-related safety requirements for lab integration of a **modular full-size humanoid**, consistent with SyRS supplier safety expectations (E-stop/STO, watchdog, overload, comm-loss) and HR-SRS-SW `SW-SAF-*`.

This is **not** a certified ISO 13482 / 10218 compliance file.

---

## 2. Context from SyRS

| SyRS input | Safety implication |
| --- | --- |
| ≤ 75 kg class biped, payloads, walking targets | Envelope limits in software; harness until proven |
| COTS arms/legs with own controllers | Require STO/watchdog/fault docs before enable (SyRS §6) |
| Mixed vendors | Module profiles must state brakes, comm-loss, E-stop behaviour |
| Lab sequence before autonomy | Phase-0 SafeStop before unattended tasks |

---

## 3. Safety functions

| ID | Function | Reaction | Bound | SRS |
| --- | --- | --- | --- | --- |
| SF-01 | Host heartbeat loss | SafeStop | trip > 100 ms | SW-SAF-001 |
| SF-02 | IMU invalid | SafeStop | > 10 RT cycles | SW-EST-002 |
| SF-03 | Fall detect | Protective stop | detect ≤ 100 ms; torque ↓ ≤ 50 ms | SW-BAL-005/006 |
| SF-04 | E-stop | SafeStop + torque off | ≤ 20 ms SW; STO ≤ 20 ms if supported | SW-SAF-005/004 |
| SF-05 | Torque limit | Saturate | same cycle | SW-SAF-002 |
| SF-06 | Bus command loss | Fault → SafeStop path | per ICD | SW-TIM / ICD |
| SF-07 | Stale outer loop | SafeStance/SafeStop | SW-TIM-004 | SW-TIM-004 |
| SF-08 | Fault latch | No auto-resume | until clear | SW-SAF-006 |
| SF-09 | Module STO/disable | Torque remove | ≤ 20 ms or profile waiver | SW-SAF-004 |

---

## 4. Requirements

### SAFE-001 — SafeStop behaviour

Shall provide SafeStop that zeros locomotion intent, enforces limits, and requires explicit clear after the condition is removed. **Must. Demo+Test.** → SW-SAF-003/006

### SAFE-002 — E-stop

Software recognition ≤ 20 ms culminating in torque removal per SAFE-003. **Must. Test.** → SW-SAF-005

### SAFE-003 — STO / disable

Module STO or disable from RT removes torque-producing output ≤ 20 ms when supported; else documented supplier bound with waiver. **Must. Test.** → SW-SAF-004, SyRS §6 Safety

### SAFE-004 — Torque limiting

Configurable per-joint limits with saturation events. **Must. Test.** → SW-SAF-002

### SAFE-005 — Fall detect

±25° torso threshold ⇒ FallDetected ≤ 100 ms in Stand. **Must. Test.** → SW-BAL-005

### SAFE-006 — Lab gating

No unharnessed powered stance/walk until SF-01…SF-04 evidence exists and E-stop verified that day. **Must. Inspection/Demo.** → HR-TEST-SW

### SAFE-007 — No automatic resume

Critical faults latch until clear. **Must. Test.** → SW-SAF-006

### SAFE-008 — Operator visibility

Should show mode/fault health ≥ 1 Hz. **Should. Demo.** → SW-BAL-010 (v0.1) / host UI

### SAFE-009 — Sensor loss

Blind balance prohibited; IMU invalid ⇒ SafeStop. **Must. Test.** → SW-EST-002

### SAFE-010 — Logging

Critical safety events timestamped for review. **Must. Test.** → SW-LOG-001

### SAFE-011 — Supplier safety gate (new in v0.2)

A module shall not be enabled in Stand/Walk until its **module profile** records: E-stop/STO behaviour, watchdog/comm-loss response, overload protection, and fault codes (SyRS §6 Safety). **Must. Inspection.**

### SAFE-012 — Envelope awareness (new in v0.2)

Host/RT software shall enforce configured joint/torque/payload software limits derived from SyRS parameters and the selected module ratings (not silent use of peak marketing figures). **Must. Test.** → SW-MAN-002 (Phase-1) / Phase-0 joint limits

---

## 5. Qualitative hazards

| Hazard | Reduction |
| --- | --- |
| Tip-over | SF-03, harness, SAFE-006 |
| Unexpected motion | SF-01, SF-04, SF-05 |
| Crush/impact | SF-05, STO, brakes per profile |
| Module without safety docs | SAFE-011 block enable |
| Mass/payload exceedance | SyRS budget + SAFE-012 |

Full ISO 12100 scoring deferred before public/unharnessed demos.

---

## 6. Lab rules

1. E-stop reachable during all powered motion.  
2. Verify STO/E-stop before L4.  
3. Trained operators only for clear/enable.  
4. After FallDetected/E-stop, inspect before clear.  
5. Do not bypass RT safety from host-only commands.  
6. Do not enable modules lacking SAFE-011 profile fields.

---

## 7. Traceability

| SAFE | Maps to |
| --- | --- |
| SAFE-001…010 | SW-SAF / SW-BAL / SW-EST / SW-LOG as above |
| SAFE-011 | SyRS §6 Safety; HR-ICD IF-MOD |
| SAFE-012 | SyRS §4 parameters; module ratings |

---

## 8. Open items

1. PLr/SIL targets if productizing.  
2. Collaborative workspace definition (10218) if industrial use.  
3. Battery isolation interlock with software enable.  
4. Update after arm/leg down-select (brakes gaps, e.g. some candidates).

---

## 9. Document history

| Version | Date | Notes |
| --- | --- | --- |
| 0.1 | 2026-11-25 | Lab balance safety draft |
| 0.2 | 2026-11-25 | SyRS supplier gate SAFE-011; envelope SAFE-012 |
