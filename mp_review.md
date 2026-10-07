# ASTRA — Major Project Review

**Status on 7 October 2026.** Team: Sushanth C., Tanay S. Huddar, Tarun Gowda V., T. Tilak Reddy.
Guide: Dr. Chaitra R. · BMS College of Engineering.

> **3D simulation:** open [`mp_review_sim.html`](mp_review_sim.html) in a browser (needs internet once, to load the 3D
> library). One tab shows the **target behaviour** for each sensor defect and change of surroundings; the other replays
> **what the code does today** from 24 recorded runs. Section 4 explains both and tabulates every case.

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

## 4 · The 3D simulation: target behaviour, and what the code does today

File: [`mp_review_sim.html`](mp_review_sim.html). Open it in a browser. Drag to rotate, scroll to zoom.

The page has two tabs.

| tab | what it is | is it a run of the code? |
|---|---|---|
| **Target behaviour** | How ASTRA is designed to react to each sensor defect and change of surroundings | **No.** A hand-written illustration of the specification. It proves nothing |
| **What the code does today** | 24 recorded runs: 17 as the experiments configure it, 7 with dormant features switched on | Yes. One run per case, seed 20260731, exploratory |

Each target case has a button that jumps to the matching recorded run, so the gap between the two is visible.

### What you see

| on screen | meaning |
|---|---|
| Solid car | The real car: real speed (road markings), real sideways position, brake lights, hazard lights when stopped |
| Blue outline car | Where ASTRA believes the car is |
| Ring under the car | Driving mode: green NOMINAL, amber DEGRADED (cap 40 km/h), orange LIMP (cap 20 km/h), red HALT |
| Surroundings | Open road, a tunnel (walls, roof ribs and lamps), or rain at night |
| Left column | Layers L9 to L1 with a coloured dot and live status |
| Sensor strip | IMU, GPS and LIDAR position sources, speed, lateral acceleration; the defective one is marked |
| Top cards | Real speed, believed speed, distance from lane centre, mode, surroundings, active calibration |
| Charts | Speed and sideways position over time, with the surroundings shaded and the defect's start and end marked |
| Right panel | The exact case, a timed list of what each layer did, and the result |

### Target behaviour: the intended reaction to each situation

This table is the specification the project is working towards. The third column says how much of it exists.

| situation | intended reaction | state of the code |
|---|---|---|
| Rain at night begins | Calibration search finds `rain_night`; it runs in shadow for 5 s beside the active one; if they agree the switch is committed (30 km/h), otherwise rolled back. Mode stays NOMINAL. Switches back when the rain ends | Coded, never switched on in experiments. Recorded once: shadow execution started and never resolved |
| Tunnel (no calibration covers it) | Bounded safe exploration: half speed, no lane change, steering within 15°. Ends by itself when a calibration fits again | Coded. Recorded once: engages correctly, **never exits** |
| One of three position sources wrong | Excluded by cross-check within about 0.5 s; car continues at full speed on the other two; reported as reduced redundancy; re-admitted 5 s after it reads correctly again | Cross-check works. Response today is a full stop within 2.4–3.75 s |
| Two position sources agree on a lie | Treated as "cannot tell who is right": LIMP, then a controlled stop in lane | Stops, but for the wrong reason (it blames the honest source) |
| Speed sensor freezes, is offset, or uses the wrong unit | Cross-check against speed worked out from position change, within about 1 s; switch to that; LIMP (20 km/h), keep driving | **Not built.** Today unnoticed; the car speeds up or crawls |
| Lateral-acceleration reading wrong | Cross-check against speed × turning rate; switch to that; DEGRADED with gentle steering; stays in lane | **Not built.** Today one run left the lane by 10.9 m |
| IMU stream stops for 10 s | DEGRADED, then LIMP while missing; back to NOMINAL within 3 s of its return | Fail-safe part works today |
| IMU stream stops for good | LIMP for 30 s, then a controlled stop | Today: LIMP and the car stops at once |
| Tunnel and a 10 s IMU outage together | Exploration handles the surroundings, the fail-safe handles the sensor; full recovery | Today: latched HALT |

The reactions in this table are our proposed design. Three choices in it are open and should be agreed by the
team: LIMP rather than DEGRADED for a bad speed sensor; a 5 s probation before re-admitting a repaired sensor; and
30 s as the point where a missing stream is treated as permanent.

### What the code does today: defects, as the experiments configure it (one run each)

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

### What the code does today: with dormant features switched on (one run each)

| run | what was switched on | what happened |
|---|---|---|
| open road only | cold path | L9 found a better calibration (`urban_clear`, trust 0.71–0.74) and ran it in shadow for the whole 120 s. **It never committed and never rolled back.** Driving unaffected, 40 km/h |
| road → tunnel (20 s) → road (50 s) → rain at night (75 s) → road (105 s) | cold path, changing surroundings | Safe exploration engaged at the first check after the tunnel began and the car slowed (18 km/h after 20 s). **It never exited**: back on the open road and in rain the car was still exploring at about 4 km/h. No calibration switch for rain |
| GPS reads 1.0 m off | cold path, tolerance 1 | Fail-safe stayed in NOMINAL (no stop). But one check after L1 flagged GPS, L9 entered safe exploration and stayed; car ended at 4 km/h. L1's flag flickered throughout |
| LIDAR reads 1.0 m off | cold path, tolerance 1 | Same: NOMINAL, exploration within a second, ended at 4 km/h |
| IMU + GPS both read 1.0 m off | cold path, tolerance 1 | L1 blamed LIDAR. One flagged source is within tolerance, so **the fail-safe never left NOMINAL** and the car was never stopped; it only crawled because of exploration |
| IMU stream off for 10 s | cold path | **Graded response and recovery worked**: DEGRADED at 0.25 s, LIMP at 0.75 s, NOMINAL again 1.8 s after the stream returned. But L9 had entered exploration and never left; the car was at 0 km/h at the end with the mode at NOMINAL |
| tunnel, then IMU stream off for 10 s | cold path | Exploration engaged in the tunnel; when the stream stopped the fail-safe went to HALT in 3 s and stayed (latched) |

**What these suggest (single runs, to be tested):**

1. **Safe exploration is a one-way door.** In every run where it engaged, it never ended. A likely cause, not yet
   verified: the context signature includes the car's own speed, exploration halves the speed, so afterwards no
   stored calibration matches.
2. **Any L1 flag pushes L9 into exploration**, because sensor health is part of the context signature. So raising
   the fail-safe's tolerance does not keep the car driving normally; it trades a stop for a permanent crawl.
3. **Tolerance 1 hides a two-source lie** from the fail-safe, because L1 flags only the honest source.
4. **Shadow execution never resolved** on the open road in 120 s.
5. **The fail-safe's own recovery path works** for a defect that ends, as long as HALT is not reached.

**How far to trust the recorded tables.** One run per case, not pre-registered: they show what *can* happen, not how
often. Item 1 and the two STEP 6 rows of the first table agree with our 30-run studies. Everything else is new and
is what the STEP 8 study (phase P3) and the paper-2 phases (P6–P8) must measure properly. Details:
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
