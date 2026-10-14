# ASTRA evaluation fault model

**Phase P1, task F1.1 · draft of 14 October 2026 · Sushanth.** Status: **DRAFT — to be agreed by Sushanth and
Tanay before any P2 or P3 run.** Every system fact below was read from code or configuration on 14 October.

This document fixes *which* faults and attackers ASTRA is **evaluated** against, and which it is not. A result
reported outside these classes is not a result about ASTRA's resilience.

**Relation to `docs/THREAT_MODEL.md`.** That document (10 August 2026) is the *security* threat model: assets,
trust boundaries and adversary tiers T0–T4 (wrong proposer, one-channel influencer, multi-channel influencer T1',
artefact substituter, evidence forger, platform-code executor). It is not replaced. This document narrows it to
what the experiments inject and measure, under its own labels **F0–F5** so the two sets of tiers are not
confused. Tolerance bounds (n ≥ 2f+1 for crash faults, n ≥ 3f+1 for coherent Byzantine ones) are stated there and
not repeated here.

---

## 1 · System boundary

| element | in the evaluated system | trusted? |
|---|---|---|
| Position sources | IMU (σ 0.10 m), GPS (σ 0.20 m), LIDAR (σ 0.06 m); fused by median (`training/closed_loop.py`) | **no** — may be faulty |
| Speed source | one stream, channel `v` | **no** |
| Lateral-acceleration source | one stream, channel `a` | **no** |
| Sensor bus, timestamps, staleness budget (50 ms) | L1 | yes |
| Estimator (L2), trust (L3), twin (L5), gates (L6, L7a, L7b), fail-safe (L8), arbiter (L9) | Core-B and L1–L3 | yes — assumed to execute as written |
| Learned controller (L4) | Core-A | **untrusted output**, but its code is not compromised |
| Configuration, calibration corpus, policy checkpoint, twin checkpoint | files loaded at start | yes |
| Actuators, plant | simulator | yes — not faulted |
| Clock | injected clock | yes |

Trust here means *not subject to injected faults in our experiments*. It is a fault-containment boundary, not a
security boundary: no cryptographic or access-control property is claimed.

## 2 · Fault and attacker classes

| class | name | what it is | intent | adapts to the detector | in scope for claims |
|---|---|---|---|---|---|
| **F0** | Sensor loss | one stream stops or arrives late | no | no | **yes** |
| **F1** | Single-source value fault | one stream delivers on time but wrong: offset, drift, noise burst, frozen value, wrong unit, flipped sign | no | no | **yes** |
| **F2** | Common-mode value fault | the same wrong value on two of three position sources, or two different streams faulted together (e.g. speed and lateral acceleration frozen) | no | no | **yes** — as a known limit, not as a resilience claim |
| **F3** | Adaptive single-source attacker | changes one stream and knows the thresholds, so stays under them (slow drift, mimicry) | yes | yes | **no claim** — may be explored and labelled exploratory |
| **F4** | Colluding majority | adaptive control of two or more of the three position sources, or of a source together with what it is cross-checked against | yes | yes | **out of scope** |
| **F5** | Full compromise | all inputs and outputs, the controller's code, the configuration, the calibration corpus, the clock or the actuators | yes | yes | **out of scope** |

Why F4 and F5 are out of scope: a colluding majority cannot be corrected by redundancy (Fawzi, Tabuada &
Diggavi 2014; Shoukry et al. 2017), and an attacker controlling all inputs and outputs is undetectable
(Griffioen, Krogh & Sinopoli). Detecting replay against a passive detector needs an active test signal
(Porter et al. 2020); ASTRA has none, so replayed data counts as a F1 frozen value, not as a F3 replay attack.

### 2.1 · Mapping to the security threat model

| fault class (this document) | adversary tier (`docs/THREAT_MODEL.md`) |
|---|---|
| F0 sensor loss, F1 single-source value fault | T1 one-channel influencer, non-adaptive case |
| F2 common-mode value fault | T1' multi-channel influencer, non-adaptive case |
| F3 adaptive single-source attacker | T1, adaptive case |
| F4 colluding majority | T1', adaptive case |
| F5 full compromise | T2 artefact substituter, T3 evidence forger, T4 platform-code executor |
| (not a sensor fault) | T0 wrong proposer — the design case every experiment already covers |

## 3 · Tolerance the architecture can at best offer

| quantity | sources | faulty sources that can in principle be tolerated | basis |
|---|---|---|---|
| Lateral position | 3 | 1 (non-colluding) | median of three; fewer-than-half bound |
| Speed | 1 | 0 by redundancy; any detection must come from consistency with other quantities (e.g. position change) | 2s-sparse observability |
| Lateral acceleration | 1 | 0 by redundancy; same as speed (e.g. speed × turn rate) | same |

"Tolerated" means the estimate stays correct. Detection without tolerance (noticing and slowing down) is possible
for more cases and is what most of ASTRA's response does.

## 4 · What the system is required to do, per class

| class | required property | how it is measured (STEP 8) |
|---|---|---|
| F0 | detect; degrade in steps; recover when the stream returns | time to leave NOMINAL; final mode; time back to NOMINAL after the fault ends |
| F1, position | detect; keep driving on the honest sources | detection time; lane-centre distance; speed relative to the healthy run |
| F1, speed or lateral acceleration | detect; degrade; stay in lane | detection time; lane departure (yes / no); speed relative to the healthy run |
| F2 | detect that the sources disagree; reach a controlled stop in lane | detection; which source is blamed; lane departure; final mode |
| any | no false alarms on clean runs beyond the configured rate | clean-run alarm rate and mode changes |

These are requirements to test, not properties the current code already has. The exploratory single runs of
7 October show that F1 on speed and lateral acceleration and F2 currently fail them.

## 5 · Metrics fixed by this document

- **Detected (run level):** the fail-safe leaves NOMINAL, or L1 marks a stream unhealthy, at or after the fault
  opens; reported per detector separately.
- **Detection time:** ticks from fault onset to the first detection event.
- **Lane departure:** |true lateral offset| > 1.75 m at any tick after onset.
- **Availability:** mean true speed after onset divided by the healthy run's mean true speed on the same seed.
- **Final mode** and **steps outside NOMINAL**.
- **Run-level false-alarm rate:** share of clean runs with any detection event after tick 200.

## 6 · Assumptions that, if broken, invalidate a result

1. Faults are injected at the sensor boundary only (ADR-0022) and are confirmed to reach the estimator — a
   faulted run must differ from its clean control. (This check exists because a defect of exactly this kind
   invalidated the position-fault results in September and in the ICDCN v21 paper.)
2. Thresholds and calibration are fixed before evaluation seeds are run.
3. One plant, one controller, one policy checkpoint; generality beyond them is not claimed.

## 7 · How this maps to the plan

| class | studied in |
|---|---|
| F0, F1, F2 | STEP 8 fault taxonomy (P3) |
| Monitor informativeness, independent of fault class | P2 monitor audit |
| F3 | optional exploratory arm in STEP 8, labelled as such |
| F4, F5 | not studied; stated as limits in every paper and report |
