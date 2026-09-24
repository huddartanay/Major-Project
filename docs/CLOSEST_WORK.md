# Closest work, and re-verification of gaps L1–L6

**13 September 2026.** An adversarial pass over `LITERATURE_GAPS.md`: for each gap, search for the
papers that come **closest to solving it**, read them, and decide whether the gap still genuinely
exists. This pass was set up to close gaps, not to support them.

## Evidence levels

| tag | meaning |
|---|---|
| `PDF-READ` | pages of the PDF read directly |
| `FULL-TEXT` | HTML full text opened via automated extraction and the relevant section located |
| `ABSTRACT` | abstract or landing page only |
| `SEARCH` | seen in a search result only — **a lead, not evidence** |

Findings are paraphrased. Section numbers are given so they can be checked in the PDF.

---

## 0 · Verdict

| gap | before | after this pass | what changed |
|---|---|---|---|
| **L1** monitor assumes true state | genuine | **Genuine, narrowed** | Navigation **integrity monitoring** already detects an estimate that is wrong while the system believes it. The gap is now at the runtime-assurance gate, not at the estimate |
| **L2** recovery assumes detection | genuine | **Genuine, strengthened** | PID-Piper's threat model **excludes persistent drastic sensor manipulation** — the exact regime where ASTRA's gate goes blind |
| **L3** combining monitors | open | **Partially addressed** | Voting across redundant perception models and verifiable cross-checks exist; cross-checking monitors *of different layers*, quantitatively, does not |
| **L4** nothing tells a monitor it is blind | genuine | **Genuine, narrowed** | Runtime failure prediction exists for **perception components**, and assumption monitoring exists for **plans**. Neither targets a safety gate's loss of detection |
| **L5** conformal bounds false alarms only | genuine | **Genuine** | The closest adaptive-conformal anomaly detector still controls false alarms only |
| **L6** masking studied only under classical control | genuine, low confidence | **Genuine, low confidence** | No learned-controller masking study found; evidence is absence, not presence |

**No gap was closed.** L1 and L4 must be **restated more narrowly** before they are claimed (§3). One
finding changes framing rather than scope: ASTRA's blind spot is a form of what navigation integrity
calls **hazardously misleading information**, occurring one layer higher, at the gate (§4).

---

## 1 · Closest work, by gap

### L1 — Runtime assurance assumes the monitor sees the true state

| work | what it solves | what it does not | evidence |
|---|---|---|---|
| **Nayak & Barth**, *The Role of Integrity Monitoring in Connected and Automated Vehicles*, arXiv 2502.04874 (2025) | **Integrity monitoring** of the vehicle's position estimate: detects **hazardously misleading information** — the system underestimating its own error while claiming safety — using protection levels, alert limits, time-to-alert and integrity risk. Covers GNSS, IMU and odometry faults via RAIM, Kalman-filter residuals and cross-sensor consistency checks | Does **not** address a downstream safety monitor or controller reading the corrupted estimate. Names integrity of AI/ML systems as largely unexplored. No runtime assurance, no learned controllers | `FULL-TEXT` |
| **Dean, Taylor, Cosner, Recht & Ames**, *Guaranteeing Safety of Learned Perception Modules via Measurement-Robust Control Barrier Functions*, CoRL 2020, arXiv 2010.16001 | Safety filter that stays safe under **bounded** measurement error from a learned perception model | Assumes the error is bounded; **does not detect faults**. A persistent sensor failure outside the bound is not covered | `ABSTRACT` |
| **Bansal, Kim, Yu, Li, Hovakimyan, Caccamo & Sha**, *Perception Simplex*, STVR 2024, arXiv 2209.01710 | Detects **obstacle-existence** faults of a DNN detector by cross-checking with a verifiable detector | Perception faults (obstacles), not state-estimation sensor faults; checks the perception output, not the gate | `ABSTRACT` |
| **Or**, *Silent Failures in Physical AI: A Literature Review of Runtime Action Authorization for Autonomous Systems*, arXiv 2606.00090 (2026) | Defines **silent physical-action failure**, including authorising an action when runtime evidence is insufficient; lists a **state-validity** guardrail function fed by sensor integrity and state-estimate consistency (§3) | A review — no method or evaluation. Lists **how to quantify runtime state reliability** and **how to evaluate for silent failures** as open questions (§9.5). Notes runtime-assurance approaches assume known dynamics and verified safe sets | `FULL-TEXT` |
| Bansal et al., *Synergistic Simplex*, arXiv 2605.08190 (2026) | — | States no sensor failure as **Assumption 8**, out of scope | `FULL-TEXT` (prior pass) |

**Re-verified.** Detecting a wrong estimate is **not** open: integrity monitoring does it for
positioning, and bounded-error safety filters tolerate it. What remains open is narrower: **runtime
assurance gates for learned controllers do not consume integrity information, and no checked work
measures what the gate does under persistent sensor failure** — beyond the bound robust filters
assume, and inside the regime the newest Simplex work declares out of scope.

---

### L2 — Recovery research assumes detection is solved

| work | what it solves | what it does not | evidence |
|---|---|---|---|
| **Dash, Li, Chen, Karimibiuki & Pattabiraman**, *PID-Piper: Recovering Robotic Vehicles from Physical Attacks*, IEEE/IFIP DSN 2021 | **Detects and recovers together.** An LSTM feed-forward controller predicts the PID controller's output from current state, target and sensor-derived features; when the deviation exceeds a threshold it declares an attack and takes over. Reports 0 % false positives, recovery in 83 % of overt attacks, and limits stealthy-attack impact | **§II-E threat model excludes attacks causing persistent drastic sensor manipulation, and attacks on all sensors simultaneously.** Its feed-forward model takes the attacked sensor quantities as input | `PDF-READ` pp. 1–5 |
| **Dash, Chan & Pattabiraman**, *SpecGuard*, ACM CCS 2024 | Deep-RL recovery under attacks on GPS, gyroscope, accelerometer, magnetometer, optical flow, barometer | Detection and diagnosis **out of scope**; reuses PID-Piper's detector without measuring it | `FULL-TEXT` (prior pass) |
| **Lin & Lee**, *Monitor and Recover*, arXiv 2504.13484 (2025) | Argues for recovery over abstention | States the monitor must itself stay reliable under shift, without a mechanism | `FULL-TEXT` (prior pass) |

**Re-verified and strengthened.** The closest work that *does* detect and recover together
explicitly excludes persistent sensor failure from its threat model. PID-Piper's detector — a learned
model of the controller whose deviation from the real controller is thresholded — is structurally
close to ASTRA's gate, which compares the learned proposal with a twin's prediction. **ASTRA measures
that class of detector in precisely the regime these works exclude.**

---

### L3 — Combining monitors and checking consistency is open

| work | what it solves | what it does not | evidence |
|---|---|---|---|
| **Aslam et al.**, *Connected Dependability Cage: Run-Time Function and Anomaly Monitoring for the Development and Operation of Safe Automated Vehicles*, arXiv 2604.27728 (2026) | Two monitors: a **function monitor** that checks consistency across heterogeneous AI perception models **by voting**, and an **anomaly monitor** for out-of-distribution scenes, with fallback to deterministic perception | Monitors run **sequentially**, not cross-checking each other; no detection of a monitor failing; no state-estimation sensor faults; **qualitative evaluation only**, each monitor evaluated independently; automated fallback not validated | `FULL-TEXT` |
| Perception Simplex (above) | Cross-checks an unverifiable DNN detector against a verifiable one | Redundancy within perception, not between monitors of different layers | `ABSTRACT` |
| **Hua et al.**, *Combining Cost-Constrained Runtime Monitors for AI Safety*, arXiv 2507.15886 (2025) | Budgeted combination of monitor scores | AI code review; disagreement not used as a signal | `ABSTRACT` (prior pass) |
| **Ferreira et al.**, *Safety Monitoring of ML Perception Functions: A Survey*, arXiv 2412.06869 | Names combining monitors and verifying their consistency as an important open challenge (§8) | — | `FULL-TEXT` (prior pass) |
| Diverse-redundancy architectures for automated driving (replica indeterminism, decision fusion) | Consistency checks among diverse redundant channels | **Not read** | `SEARCH` |

**Re-verified: partially addressed.** Combining **redundant models within one function** — voting
across perception networks, verifiable cross-checks — exists. What is **not** shown in checked work is
cross-checking **monitors that observe different layers** (a sensor-integrity check against a
statistical gate on the controller's output), using their **disagreement as evidence**, evaluated
**quantitatively in closed loop**. The 2026 Dependability Cage confirms the survey's open challenge is
not yet met quantitatively.

---

### L4 — Nothing tells a monitor it has gone blind

| work | what it solves | what it does not | evidence |
|---|---|---|---|
| **Yang, Chen, Chen & Su**, *Introspective False Negative Prediction for Black-Box Object Detectors in Autonomous Driving*, Sensors 2021 | **Predicts at runtime, without ground truth, when an object detector will miss objects** — 81.95 % precision at 88.10 % recall on KITTI | Camera 2D object detection only; monitors a **perception component**, not a safety monitor; no state-estimation sensors | `FULL-TEXT` |
| **Zudaire, Gorostiaga, Sánchez, Schneider & Uchitel**, *Assumption Monitoring Using Runtime Verification for UAV Temporal Task Plan Executions*, ICRA 2021 | Monitors a plan's **explicit and implicit assumptions** at runtime with stream runtime verification, flagging **silent mission failures** — where the mission appears successful because its assumptions were violated | Discrete task planning (labelled transition systems, fluent LTL); monitors the **plan's** assumptions, not whether a **safety monitor** can still detect; no learned controllers | `PDF-READ` pp. 1–2 |
| **Guérin, Delmas, Ferreira & Guiochet**, *Out-Of-Distribution Detection Is Not All You Need*, AAAI 2023 | Shows monitors with strong OOD scores can **give a false impression of safety** by missing actual errors; argues monitors should be evaluated on errors they catch | Offline evaluation of perception monitors; no runtime mechanism for detecting the monitor's own failure | `ABSTRACT` |
| **Ferrando & Malvone**, *Runtime Verification via Rational Monitor with Imperfect Information*, arXiv 2408.11627 | Monitors under imperfect information | LTL over discrete traces | `ABSTRACT` (prior pass) |
| **Or**, *Silent Failures in Physical AI*, 2026 | Frames silent failure, including insufficient runtime evidence | Does not isolate monitors being blind, or cross-checking monitors, as open problems (§9) | `FULL-TEXT` |
| Introspective sensor-fusion weighting by predicted per-sensor failure | Weights fusion by predicted sensor failure | **Not read** | `SEARCH` |

**Re-verified, narrowed.** Two adjacent ideas exist: **runtime prediction of a component's misses**
(for object detectors) and **runtime monitoring of assumptions** (for plans). Neither detects that a
**safety gate** has lost its ability to detect **sensor faults**. The gap is real, but it must be
stated as that specific intersection, and both adjacent lines must be cited — a reviewer from either
community will otherwise say it has been done.

---

### L5 — Conformal runtime guarantees bound false alarms only

| work | what it solves | what it does not | evidence |
|---|---|---|---|
| **Martinez Gil, O'Donncha, Gifford, Zhou, Patel & Vaculin**, *Adaptive Conformal Anomaly Detection with Time Series Foundation Models for Signal Monitoring*, arXiv 2604.20122 (2026) | Adaptive, weighted conformal anomaly scores interpretable as false-alarm rates; calibration under distribution shift | False-alarm control only; closed-loop control, sensor faults and persistent faults not mentioned | `ABSTRACT` |
| Zhao et al., robust conformal STL verification, 2024 | Coverage under a known f-divergence bound | Open-loop; perfect observation; no detection guarantee | `FULL-TEXT` (prior pass) |
| Strawn, Ayanian & Lindemann, RA-L 2023 | Coverage of trajectory-prediction uncertainty | No sensor faults | `ABSTRACT` (prior pass) |

**Re-verified: genuine.** The adaptive and robust variants improve calibration under shift; none
checked provides a detection guarantee or evaluates under closed-loop sensor failure. **Martinez Gil
et al. is a natural comparator for objective A2(c)** alongside adaptive conformal inference.

---

### L6 — Masking studied only under classical control

| work | what it solves | what it does not | evidence |
|---|---|---|---|
| **Zhang, Yang, Dandago & Li**, *The negative impact of closed-loop control on fault detection*, Springer 2026 | Faulted closed-loop systems can behave like healthy ones | **PID**, 2-DOF aircraft | `ABSTRACT` (prior pass) |
| **Gómez-González, Fischer et al.**, *Anomaly Detection Under Closed-Loop Fault Masking*, Springer | Masking of data-driven detectors | **Adaptive PID/RLS**, two-tank plant | `ABSTRACT` (prior pass) |
| Closed-loop fault identification with deep networks; RL-based fault-tolerant control | Note that feedback reduces fault amplitude; use RL to *compensate* or *detect* faults | Classical loops; RL is the remedy, not studied as a source of masking | `SEARCH` |

**Re-verified: genuine, low confidence.** Nothing found studies a learned policy as the cause of
masking against a runtime-assurance monitor. That is absence of evidence from a limited search, and
both masking papers remain unread in full.

---

## 2 · The closest group, in one table

The papers a reviewer is most likely to raise, ranked by how close they come.

| rank | work | threatens | how close | ASTRA's distinction |
|---|---|---|---|---|
| 1 | Nayak & Barth 2025 — integrity monitoring | L1, L4 | **Very close in concept**: detecting a wrong estimate with false confidence | Operates on the estimate, not the runtime-assurance gate; no learned controllers; not connected to the gate's decision |
| 2 | Dash et al. — PID-Piper, DSN 2021 | L2, L1 | **Very close in mechanism**: learned model of the controller, deviation thresholded, detect-and-recover | Excludes persistent drastic sensor manipulation (§II-E) — the regime ASTRA measures |
| 3 | Yang et al. 2021 — introspective false-negative prediction | L4 | **Close in concept**: runtime prediction of a component's misses | Perception component, camera only; not a safety gate; not sensor faults |
| 4 | Zudaire et al., ICRA 2021 — assumption monitoring | L4 | Close in intent: detecting silent failures from violated assumptions | Plans, not monitors; discrete; no learned control |
| 5 | Aslam et al. 2026 — Connected Dependability Cage | L3 | Close in architecture: two monitors with fallback | Voting within perception; monitors not cross-checked; qualitative |
| 6 | Or 2026 — Silent Failures in Physical AI | L1, L4 framing | Names silent failure and a state-validity guardrail | Review; lists the relevant questions as open |
| 7 | Bansal et al. 2024 — Perception Simplex | L1, L3 | Cross-checks a DNN detector against a verifiable one | Obstacle perception, not state sensors or gates |
| 8 | Guérin et al., AAAI 2023 | L4, L5 | Monitors that look good while missing errors | Offline perception monitors |
| 9 | Dean et al., CoRL 2020 — measurement-robust CBFs | L1 | Safety under estimation error | Bounded error; no detection |
| 10 | Martinez Gil et al. 2026 | L5 | Adaptive conformal under shift | False-alarm control only |

---

## 3 · Gap statements, restated after re-verification

These replace the corresponding statements in `LITERATURE_GAPS.md` wherever they are quoted.

**L1 (narrowed).** Integrity monitoring detects when a navigation estimate is wrong while the system
believes it, and measurement-robust safety filters tolerate bounded estimation error. But runtime
assurance for learned controllers does not consume that integrity information, recent architectures
assume nominal sensors, and no checked work measures what a runtime-assurance gate does under
**persistent** sensor failure.

**L2 (strengthened).** Detect-and-recover work for autonomous vehicles either declares detection out of
scope or excludes persistent sensor manipulation from its threat model; the detector class it relies
on has not been evaluated in that regime.

**L3 (narrowed to what remains).** Combining redundant models within a perception function exists.
Cross-checking monitors that observe different layers, and using their disagreement as evidence,
evaluated quantitatively in closed loop, is not shown.

**L4 (narrowed).** Runtime failure prediction exists for perception components and runtime assumption
monitoring exists for plans. Runtime detection that a **safety gate** has lost the ability to detect
**sensor faults** is not shown.

**L5 (unchanged).** Conformal runtime methods, including adaptive and robust variants, control false
alarms or coverage; none checked offers detection guarantees or is evaluated under closed-loop sensor
failure.

**L6 (unchanged, low confidence).** Closed-loop masking is shown for PID-family controllers; not
studied with learned policies against runtime-assurance monitors.

---

## 4 · What this does to ASTRA's framing

**Adopt the integrity-monitoring vocabulary rather than competing with it.** In integrity terms, the
conformal gate under sustained IMU dropout exhibits **hazardously misleading information at the
governance layer**: the gate's silence claims safety while the vehicle's state is not trustworthy.
E21's `health` detector is, in effect, a rudimentary integrity check on the sensor layer — and it
caught what the gate missed.

That turns a vulnerability into a sharper contribution:

> ASTRA connects **navigation integrity monitoring** to **runtime assurance for learned controllers**,
> and extends **introspection** from perception components to the **safety gate itself**.

Concretely, for the documents downstream:

1. **`NOVELTY_CLAIMS.md` N1** must cite integrity monitoring (Nayak & Barth) and measurement-robust
   CBFs, and claim only the gate-level gap.
2. **N3** is strengthened by PID-Piper's threat-model exclusion.
3. **N5** must cite the Connected Dependability Cage and Perception Simplex, and claim only
   cross-layer monitor disagreement, quantitatively.
4. **Do not claim to introduce "silent failure".** The term is used by Zudaire et al. (2021) and Or
   (2026).
5. **Objective B1** (Paper 2) should be positioned as *introspection for safety gates*, citing Yang
   et al. and Zudaire et al. as the adjacent lines it extends, and should consider integrity-style
   **protection levels** as a candidate formalism for "can this gate currently see?".
6. **Objective A2(c)** should include Martinez Gil et al.'s adaptive conformal detector as a
   comparator.

---

## 5 · Still not done

- **Integrity monitoring needs a proper read.** Nayak & Barth is a survey; the RAIM and Kalman-filter
  integrity literature it cites — especially any work applying protection levels to control or
  safety decisions — is the single most likely place for L1 or L4 to be closed outright.
- Read in full: Perception Simplex, the Dependability Cage's related work, Guérin et al. (AAAI 2023),
  both masking papers.
- Follow the two `SEARCH` leads: diverse-redundancy consistency architectures (L3), and introspective
  per-sensor failure weighting in fusion (L4).
- Forward citations of PID-Piper and of Yang et al. 2021, for anyone who has lifted the persistent-fault
  exclusion or applied introspection to a safety monitor.
