# ASTRA — Major Project Review

**Status on 7 October 2026.** Team: Sushanth C., Tanay S. Huddar, Tarun Gowda V., T. Tilak Reddy.
Guide: Dr. Chaitra R. · BMS College of Engineering.

> **3D walkthrough:** open [`mp_review_sim.html`](mp_review_sim.html) in a browser (needs internet once, to
> load the 3D library). It replays 17 recorded runs of the ASTRA code — one per sensor defect — showing the car, its sensors and
> the nine layers, and exactly when each layer reacted. Section 4 explains it and tabulates every run.

---

## 1 · The project in one paragraph

A self-driving controller that has been *learned* (ours is a PPO neural network) cannot be trusted on its
own: it gives a confident command even when its inputs are wrong. ASTRA is a nine-layer supervisor built
around such a controller. It watches the sensors, estimates the car's state, checks every proposed command
against an independent model and against fixed rules, and — when something is wrong — steps the car down
through reduced-speed modes to a stop instead of failing abruptly.

**Goal:** a system that detects faults, reacts to them in proportion, and brings the vehicle to a better
functional state, with stated limits against faulty, manipulated and semantically wrong sensors.

## 2 · Architecture

| layer | name | job | state today |
|---|---|---|---|
| L1 | Sensing | Is each sensor stream arriving on time? Cross-check of redundant position sources | Works. Cannot see a sensor whose value has frozen |
| L2 | Estimation | Fuse sensors into position, speed, heading (unscented Kalman filter) | Works. Trusts a frozen reading |
| L3 | Trust | Score how far readings are from expectation | Computed every tick; **nothing acts on it** |
| L4 | Proposer | Learned controller proposes throttle, brake, steer | Works |
| L5 | Digital twin | Independent prediction of a sound command | **Mis-specified**: models steering only |
| L6 | Statistical gate | Block proposals too far from the twin (conformal threshold) | **Mis-specified**: score dominated by channels the twin does not model |
| L7 | Shield and physical gate | Fixed rules; physical-limit checks | Shield works; physical gate inherits the twin's error |
| L8 | Fail-safe | NOMINAL → DEGRADED (40 km/h) → LIMP (20 km/h) → HALT, with recovery | Works |
| L9 | Arbitration | Issue the command or hand over to a fallback controller; speed caps | Hot path works. Calibration switching and safe exploration are **coded but switched off** |

Feedback loops: FB1 (command back to the estimator) is live. FB2 (learn the car's steering response) and
FB3 (update thresholds online) run only in shadow — they compute what they would do and change nothing.

Size: nine layers under `src/astra/`, 3,076 automated tests passing.

## 3 · What we have established

Every item points at a committed experiment. Studies from STEP 6 on were pre-registered: the hypothesis and
decision rule were committed before the runs, and each held-out seed block was used once.

| # | finding | evidence | confidence |
|---|---|---|---|
| F1 | A flagged sensor loss is handled: L1 notices within one tick and L8 slows or stops the car | STEP 1–5 (Tanay), STEP 6 | High — 30/30 runs, two seed blocks |
| F2 | During that same loss the statistical gate goes *quieter*, not louder. This is not caused by the car stopping | STEP 6, H-indep confirmed | High |
| F3 | A sensor that freezes (keeps sending the same value) is never flagged by L1 (0/30) and silences the gate. The car slows to 0–2 m/s while ASTRA believes ≈ 11.5 m/s | STEP 6, H-freeze confirmed | High |
| F4 | The gate's score is ≈ 87 % throttle, 13 % brake, 0.04 % steering — but the twin models only steering. The gate passed every calibration check while being almost blind to what it claims to monitor | `FINDING_TWIN_CHANNEL_MISMATCH_2026-10-07` | High (read from code and measured) |
| F5 | A score restricted to steering is a valid instrument (calibrated; detects a lying position source at 11–17× the clean alarm rate) and is not suppressed by sensor loss | STEP 7, both splits | High |
| F6 | That corrected score does **not** reliably detect sensor loss: the outcome differed between dev and held-out | STEP 7 | The inconclusiveness is the finding |
| F7 | In about a third of frozen-sensor runs L8 still reaches HALT; we have not identified which check causes it | STEP 7 `POST_HOC_NOTE_2026-10-07.md` | Observation only |

Guesses of ours that the experiments refuted, and which we report: that the gate's silence came from
inflated uncertainty; that sensor noise on a frozen channel would restore detection (H-noise).

**The central result is F4:** *calibration is not validity.* A safety monitor can meet its statistical
guarantee and still be uninformative.

## 4 · The 3D replay: how the car reacts to each sensor defect

File: [`mp_review_sim.html`](mp_review_sim.html). Open it in a browser. Drag to rotate, scroll to zoom.

**This is a replay of real runs of the ASTRA code**, not an animation we drew. For each defect the pipeline was
run once in its simulator for 120 s (2,400 ticks at 20 per second) with the defect switched on at 10.0 s, and
what it recorded is played back.

### How to use it

1. Pick a sensor, then a defect. There are 17 runs: 16 defects across the sensors, plus a healthy reference.
2. Watch the car. Playback is 8× by default; the slider and the chart at the bottom let you jump anywhere.

### What you see

| on screen | meaning |
|---|---|
| Solid car | The real car: its real speed (road markings), real sideways position, brake lights, hazard lights when stopped |
| Blue outline car | Where ASTRA *believes* the car is. If it separates from the solid car, ASTRA's picture is wrong |
| Glow under the car | Driving mode: green NOMINAL, amber DEGRADED (40 km/h cap), orange LIMP (20 km/h cap), red HALT |
| Five dots on the car | IMU, GPS and LIDAR position sources; speed; lateral acceleration. The defective one pulses and is labelled "DEFECT, flagged by L1" or "DEFECT, not flagged" |
| Nine plates above the car | Layers L1–L9. Green no objection, amber flagging or limiting, red blocking, purple "no objection, but its picture is wrong" |
| Top cards | Real speed, believed speed, real distance from lane centre, mode, where the command came from |
| Bottom chart | Real speed (white), believed speed (blue dashes), healthy run (green dots); sideways position with the lane edges; mode strip |
| Right panel | Exact defect, a timed list of what each layer did, the result of the run, and each layer's live status |

Purple is the page's own judgement, made by comparing ASTRA's estimate with the simulator's ground truth, which
ASTRA never sees. Everything else is recorded output.

### What each defect did (one run each, seed 20260731)

| sensor | exact defect | L1 flags it | fail-safe leaves NOMINAL | final mode | real speed at end | worst speed belief error | worst distance from lane centre |
|---|---|---|---|---|---|---|---|
| — | none (healthy reference) | — | never | NOMINAL | 40 km/h | 0 km/h | 0.24 m |
| Position · IMU | reads 1.0 m to the side; GPS, LIDAR honest | IMU, after 0.45 s | 0.65 s | HALT at 2.40 s | 0 | 2 km/h | 0.47 m |
| Position · GPS | reads 1.0 m to the side; IMU, LIDAR honest | GPS, after 0.80 s | 1.00 s | HALT at 3.75 s | 0 | 2 km/h | 0.42 m |
| Position · LIDAR | reads 1.0 m to the side; IMU, GPS honest | LIDAR, after 0.45 s | 0.65 s | HALT at 2.40 s | 0 | 2 km/h | 0.57 m |
| Position · LIDAR | drifts sideways 4 cm/s | LIDAR, after 16.40 s (0.66 m of drift) | 16.60 s | HALT at 21.90 s | 0 | 2 km/h | 0.46 m |
| Position · IMU + GPS | both read 1.0 m to the side; only LIDAR honest | **LIDAR** (the honest one), after 0.45 s | 0.65 s | HALT at 2.40 s | 0 | 2 km/h | 0.95 m |
| Position · IMU + GPS | both drift sideways 4 cm/s | **LIDAR** (the honest one), after 15.65 s | 17.95 s | HALT at 22.40 s | 0 | 2 km/h | 0.48 m |
| Speed | freezes | never | **never** | NOMINAL | **53 km/h** | 15 km/h | 0.24 m |
| Speed | reads 3.0 m/s too high | never | **never** | NOMINAL | 29 km/h | 11 km/h | 0.23 m |
| Speed | reads 3.0 m/s too low | never | **never** | NOMINAL | **51 km/h** | 11 km/h | 0.30 m |
| Speed | drifts to 5.0 m/s too low | never | **never** | NOMINAL | **55 km/h** | 18 km/h | 0.26 m |
| Speed | reported in km/h instead of m/s | never | 0.45 s, then back to NOMINAL | NOMINAL | 4 km/h | 100 km/h | 0.56 m |
| Lateral acceleration | freezes | never | **never** | NOMINAL | 21 km/h | 0 | 0.50 m |
| Lateral acceleration | reads 1.0 m/s² too high | never | 0.65 s | HALT at 5.15 s | 0 | 2 km/h | **10.91 m — left the lane** |
| Lateral acceleration | sign flipped | never | **never** | NOMINAL | 4 km/h | 0 | 0.74 m |
| Speed + lateral acceleration | both freeze (STEP 6 arm) | never | **never** | NOMINAL | 0 km/h | 38 km/h | 0.38 m |
| IMU message stream | stops sending (STEP 6 arm) | IMU, after 0.05 s | 0.25 s | LIMP | 0 km/h | 38 km/h | 0.25 m |

Times are measured from the moment the defect starts (10.0 s into the run). Lane edge is 1.75 m from centre.

**What these single runs suggest — to be tested, not yet claimed:**

1. **Position defects are the well-covered case.** Any one of the three sources lying by 1.0 m is flagged within
   0.45–0.80 s and the car is stopped within 2.4–3.75 s. A slow drift is caught too, but only after 16 s.
2. **When two position sources agree on a lie, L1 blames the honest third one.** The car is still stopped, but for
   the wrong reason, and it moved 0.95 m off centre first.
3. **Every speed defect went unnoticed.** With a frozen or under-reading speed sensor the car ended 11–15 km/h
   *faster* than the healthy run while the fail-safe stayed in NOMINAL. Speed has a single source and nothing to
   cross-check it against.
4. **A lateral-acceleration reading 1.0 m/s² too high put the car 10.9 m off the lane centre** before the fail-safe
   stopped it at 5.15 s. L1 never flagged it. This is the most serious outcome in the set.
5. **A wrong unit was noticed and then forgotten.** The gates blocked at once and the fail-safe went to DEGRADED
   after 0.45 s, then returned to NOMINAL with the defect still present, the car crawling at 4 km/h.
6. **Freezing both speed and lateral acceleration stops the car without any layer knowing**; freezing speed alone
   speeds it up. The same kind of defect has opposite effects depending on which channels it hits.

**How far to trust this table.** It is one run per defect, not pre-registered, so it shows what *can* happen, not
how often. Item 1 and the two STEP 6 rows agree with our 30-run studies. Items 2–6 are new and are exactly
what the STEP 8 study (phase P3) will measure properly. Details:
`experiments/phase5_od8_h7/EXPLORATORY_SENSOR_DEFECT_TRACES_2026-10-07/`.

## 5 · Literature position

About 95 papers reviewed across conformal safety gates, runtime monitors, and sensor attacks and faults
(`docs/MANUAL_NOVELTY_CHECK.md`, `docs/LITERATURE_SYNTHESIS.md`, `docs/THREAT_LITERATURE_STUDY.md`).

- Each individual ingredient — layered resilient architectures, tolerating a minority of bad sensors,
  staged degradation, online recalibration — is published. We do not claim any of them as new.
- What we did not find: a check of whether a calibrated monitor actually depends on the quantity it
  monitors. A recent survey notes that recovery work assumes the recovery module itself is safe (Lu et al.).
- Hard limits we work inside: redundancy can correct only a minority of bad sources; an attacker who
  controls every input and output is undetectable; replayed data needs an active test signal.

We never write "first" or "resilient to all attacks".

## 6 · What is not done

| gap | consequence |
|---|---|
| Twin and gate are mis-specified (F4) | The statistical gate contributes little today |
| No frozen-value check | F3 |
| Speed and lateral acceleration have one source each | No cross-check is possible on those channels |
| L3 trust has no authority | A low trust score triggers nothing |
| Safe exploration and calibration switching never switched on | "Explores instead of stopping" is untested |
| FB2, FB3 shadow only | The system does not learn while driving |
| Colluding sources, slow drift, unit and sign errors | Untested |
| One simulator, one controller | Generality unknown |

**So today ASTRA is not yet a "self-learning, exploring, resilient" system.** It is a well-tested
supervisor that handles announced faults, with a measured blind spot and a measured defect in its own
monitor — and a method for finding such defects.

## 7 · Plan

Full task list: `docs/TASK_PLAN_2026-10-07.md`.

| phase | when | outcome |
|---|---|---|
| P1 Define | 8–18 Oct | Threat model; pre-registered monitor audit |
| P2 Prove the monitor problem | 19 Oct – 8 Nov | The audit catches the defect on two different monitors |
| P3 Map the faults | 9 Nov – 13 Dec | Eight fault types × four detectors, measured |
| P4 Repair the monitor | 14 Dec – 10 Jan | Retrained twin; gate passes the audit |
| P5 Write | 11 Jan – 1 Mar | Paper to IEEE ITSC 2027; this report |
| P6–P10 | after March | Guarded learning, safe exploration, adaptive thresholds, second platform; journal paper |

## 8 · Questions a reviewer is likely to ask

**Is this just a bug you found in your own code?** The twin/gate mismatch is specific to ours. The point is
that every standard calibration check passed anyway. Phase P2 tests whether the audit catches the same
kind of defect in a second, independently built monitor; if it does not, we say so and narrow the claim.

**If the car slows down when a sensor freezes, where is the harm?** The vehicle is nearly stationary in a
live lane while reporting normal operation at 41 km/h. Nothing downstream — an operator, a fleet system,
the fail-safe — is told. It is an unannounced failure.

**Why not just add a stuck-value check?** We will, as a baseline (P3). It will probably catch this fault
better than the statistical gate. That is part of the result: an elaborate monitor missed what a simple
one catches.

**Does it work against a hacked sensor?** Against one bad position source out of three: yes, measured.
Against two colluding sources, slow drift, or a manipulated single-source channel: untested, and theory
says redundancy alone cannot handle the first.

**Is it real-time, is it on a real car?** Simulation only, our own simulator. No hardware.

**What is novel?** The audit of monitor informativeness, and — in the second paper — using it to decide
when the system is allowed to learn.

## 9 · Where things are

| | |
|---|---|
| Code | `src/astra/` (layers, runtime), `training/` (closed loop, faults), `benchmarks/` |
| Experiments | `experiments/phase5_od8_h7/` — `EXPERIMENT_INDEX.md`, `CLAIM_LEDGER.md` |
| Direction and plan | `docs/DIRECTION_2026-10-07.md`, `docs/TASK_PLAN_2026-10-07.md` |
| Literature | `docs/THREAT_LITERATURE_STUDY.md` and the earlier review files |
| Paper skeleton | `paper/itsc_2027/skeleton.md` |
