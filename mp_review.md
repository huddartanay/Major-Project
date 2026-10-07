# ASTRA — Major Project Review

**Status on 7 October 2026.** Team: Sushanth C., Tanay S. Huddar, Tarun Gowda V., T. Tilak Reddy.
Guide: Dr. Chaitra R. · BMS College of Engineering.

> **3D walkthrough:** open [`mp_review_sim.html`](mp_review_sim.html) in a browser (needs internet once, to
> load the 3D library). It shows the car, its sensors, the nine ASTRA layers stacked above it, and how each
> layer reacts in four situations. Section 4 explains what you are looking at and what is real in it.

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

## 4 · The 3D walkthrough

File: [`mp_review_sim.html`](mp_review_sim.html). Drag to rotate, scroll to zoom.

**What you see**

- The **solid car** is where the vehicle really is. The **blue outline** is where ASTRA believes it is.
  When they separate, the system's picture of the world is wrong.
- **Five dots on the car** are the sensors: three position sources, speed, lateral acceleration.
- **Nine plates above the car** are the layers, L1 at the bottom to L9 at the top. A white pulse climbs the
  stack each cycle (sensor data going up); an arrow comes back down (the command going to the wheels —
  blue from the learned controller, orange from the fallback).
- Plate colour: green working · amber flagged a problem · red blocking or stopped ·
  **purple says OK but is wrong** · grey not connected.

**The four situations**

| situation | what happens | which finding |
|---|---|---|
| Normal driving | All green; learned controller drives | baseline |
| Sensor stops sending | L1 turns amber at once, L8 steps down to 20 km/h, the fallback takes over. L6 turns purple: it goes quiet when it should be loudest | F1, F2 |
| Sensor freezes | Sensors still look healthy. Every layer except the proposer turns purple. The solid car slows to a crawl; the blue outline keeps going at 41 km/h. Mode stays NOMINAL | F3, F7 |
| One sensor lies | One of three position sources shifts. The cross-check catches it in under half a second and the car is brought to a stop | F5 |

Tick "Show parts that are built but not connected" to list the dormant components.

**What is real and what is not.** Which layer reacts, the final driving mode, and the size of the speed gap
come from STEP 6 and STEP 7 held-out results. The motion between start and end, the timing (compressed),
how far the blue outline is drawn from the car, and the wiggle on the score bar are an illustration. The
page is an explainer; it does not execute ASTRA. A replay driven by a recorded run is possible and would
be the honest next version.

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
