# Novelty re-verification — have these claims already been made?

**13 September 2026.** Scope: the **published literature only**. For each novelty claim in
`NOVELTY_CLAIMS.md`, and for each **assumption about other people's work** those claims rely on, an
adversarial search for papers that already make the claim or contradict the assumption. ASTRA's own
data is out of scope here.

## Evidence levels

| tag | meaning |
|---|---|
| `PDF-READ` | pages of the PDF read directly |
| `FULL-TEXT` | HTML full text via automated extraction, relevant section located |
| `ABSTRACT` | abstract or landing page only |
| `SEARCH` | search result only — a lead, not evidence |

Findings are paraphrased; section numbers are given for checking.

---

## 0 · Result

**No paper found makes any of the six claims.** But:

- **All six claims had to be narrowed.**
- **Four of the eight literature assumptions** behind them were **false or only partly true** as
  previously stated.
- The largest single threat, to the Paper 2 direction as well as to Paper 1's framing, is
  **Ruchkin et al., ICCPS 2022**, which estimates at runtime whether a verified system's safety
  guarantees still hold by composing calibrated monitors of its assumptions — including assumptions
  about sensor observation models.

| claim | made before? | after verification |
|---|---|---|
| **N1** integrity failure at the safety gate | not found | **narrowed** — integrity information *is* used in planning, and observation-model assumptions *are* monitored (CoCo) |
| **N2** coverage met, detection zero | not found | **narrowed** — conformal assurance monitors exist; none found reports missed detection under sensor faults |
| **N3** the persistent-fault regime | not found | **narrowed** — "excluded" is true of PID-Piper only; DeLorean evaluates attacks lasting 15–30 s |
| **N4** below-baseline masking under a learned controller | not found | **unchanged** — still rests on absence of evidence |
| **N5** cross-layer disagreement | not found | **narrowed and downgraded** — cross-layer diagnosis aggregation and diagnostic graphs exist |
| **N6** evaluation protocol | not found | **narrowed and downgraded** — fault duration is already a protocol parameter elsewhere |

---

## 1 · Assumptions about the literature

These are the statements about other people's work that the claims depend on.

### A1 — "Runtime assurance and safety filters assume their inputs are correct"

**Verdict: SUPPORTED for most work — but not universal.**

| evidence | what it shows | read |
|---|---|---|
| Bansal et al., *Synergistic Simplex*, arXiv 2605.08190 (2026) | Assumes nominal sensors as **Assumption 8** | `FULL-TEXT` |
| **Rober, Jia & How**, *Learning-Based Measurement-Robust Control Barrier Functions for Obstacle Avoidance under State Estimation Error*, arXiv 2608.20467 (Aug 2026) | States that **most existing safety filters assume perfect state information** — an independent 2026 statement of the assumption | `ABSTRACT` |
| **Counter-evidence:** Dean, Taylor, Cosner, Recht & Ames, CoRL 2020; Rober et al. 2026 | Safety filters robust to **bounded** estimation error | `ABSTRACT` |
| **Counter-evidence:** Ruchkin et al., ICCPS 2022 (see A3) | Monitors **observation-model** assumptions of verified neural-network controllers at runtime | `FULL-TEXT` |

**Correct form:** *most* runtime assurance assumes correct state; a minority handles bounded estimation
error or monitors observation-model assumptions. Cite Rober et al. for "most".

---

### A2 — "Integrity monitoring is not connected to safety or control decisions"

**Verdict: FALSE as stated.**

| evidence | what it shows | read |
|---|---|---|
| **Lee, Seo & Kassas**, *Integrity-Based Path Planning Strategy for Urban Autonomous Vehicular Navigation Using GPS and Cellular Signals*, ION GNSS+ 2020 | Path planning with the **horizontal protection level as a cost** and **HPL below the alert limit as a constraint** — predicted **before driving** using ray-tracing | `PDF-READ` p. 1 |
| **Maharmeh, Resende & Nashashibi**, *Integrity as a Control Problem: Smooth and Adaptive Protection Levels for Multi-Modal Localization*, Sensors 2026 | Designs protection levels to be smooth **for use by motion planners**, but does not integrate or evaluate a planner | `FULL-TEXT` |
| Nayak & Barth, arXiv 2502.04874 (2025) | Survey: does not address downstream safety monitors reading the estimate | `FULL-TEXT` |

**Correct form:** integrity information is used in **offline path planning** and is being designed for
planners. **Not found:** integrity information consumed **online** by the **runtime-assurance gate** of
a **learned controller**.

---

### A3 — "Nothing monitors whether a monitor can be trusted"

**Verdict: FALSE as stated.** Three distinct forms of monitoring-the-monitor exist.

| evidence | form | read |
|---|---|---|
| **Harder, Kulkarni & Behl**, *HALO: Fault-Tolerant Safety Architecture for High-Speed Autonomous Racing*, arXiv 2503.10341 (2025) | **Liveness.** The node-health monitor emits its own heartbeat, and a graceful-stop node halts the vehicle if it stops (§10.2). Voting among monitors rejected as infeasible (§2). No quantitative detection or false-alarm results (§11) | `FULL-TEXT` |
| *Fault-Adaptive Autonomy in Systems with Learning-Enabled Components*, Sensors 21(18):6089 (2021) | **Instance-level confidence.** An inductive-conformal assurance monitor gives credibility and confidence for each classification of a learned fault-detection network, and can reject low-confidence decisions. Faults are **thruster degradation**, not sensor faults; missed detections not evaluated | `FULL-TEXT` |
| **Ruchkin, Cleaveland, Ivanov, Lu, Carpenter, Sokolsky & Lee**, *Confidence Composition for Monitors of Verification Assumptions*, ICCPS 2022, arXiv 2111.03782 | **Assumption confidence.** Represents the conditions for verified safety as a logical formula over assumptions — initial states, dynamics, and **observation models capturing sensor uncertainty** (§4.2); builds Platt-calibrated monitors for each; composes them into confidence that the guarantee holds at runtime; predicts safety violations. Case studies: mountain car, unmanned underwater vehicle. Assumes monitors stay informative; composes rather than using disagreement | `FULL-TEXT` |
| Boursinos & Koutsoukos, conformal assurance monitoring of learning-enabled CPS, arXiv 2001.05014; AI EDAM 2021 (arXiv 2110.03120) | Conformal assurance monitors with calibrated error rates | `SEARCH` / `ABSTRACT` |

**Correct form:** monitors are checked for **liveness**, for **per-decision confidence**, and for
**whether their verification assumptions hold**. **Not found:** detecting that a **safety gate has
lost detection capability** — it is alive, confident and calibrated, and blind — for **sensor faults**,
using **disagreement with another layer** as the evidence.

This distinction — **liveness and confidence versus functional detection capability** — is now the
load-bearing boundary of the whole programme.

---

### A4 — "Detect-and-recover work excludes persistent sensor faults"

**Verdict: PARTLY TRUE.** True of one paper, not of the line of work.

| evidence | what it shows | read |
|---|---|---|
| Dash, Li, Chen, Karimibiuki & Pattabiraman, *PID-Piper*, DSN 2021 | Threat model **excludes persistent drastic sensor manipulation and attacks on all sensors** (§II-E) | `PDF-READ` pp. 1–5 |
| **Dash, Li, Karimibiuki & Pattabiraman**, *Diagnosis-guided Attack Recovery for Securing Robotic Vehicles from Sensor Deception Attacks* (DeLorean), ASIA CCS 2024, arXiv 2209.04554 | Attacker may manipulate **any number of sensors** (§2.3) — lifting one PID-Piper exclusion. **Attack duration not stated** in the threat model; evaluated attacks last **15–30 s**; recovery for whole-mission persistence not shown. **Assumes an existing detector** and uses PID-Piper's (§5.4) | `FULL-TEXT` |
| Dash, Chan & Pattabiraman, *SpecGuard*, CCS 2024 | Detection out of scope; detector not measured | `FULL-TEXT` |

**Correct form:** PID-Piper **excludes** persistent manipulation; its successor DeLorean **evaluates
attacks of 15–30 s** and **assumes detection is given**. Across the line, **faults persisting for the
remainder of a mission are not evaluated**, and the detector relied on is not measured in that regime.

---

### A5 — "Combining monitors, or cross-layer consistency, is open"

**Verdict: PARTLY TRUE — narrowed further.**

| evidence | what it shows | read |
|---|---|---|
| **Orf, Ochs, Doll, Schotschneider, Heinrich, Zofka & Zöllner**, *Modular Fault Diagnosis Framework for Complex Autonomous Driving Systems*, arXiv 2411.09643 (2024) | **Cross-layer** aggregation over a dependency graph spanning sensors, localization, perception, prediction, planning and execution; OR-aggregation with dependency-aware suppression and root-cause traversal (§IV-E, §V-A). **Not disagreement-based**; diagnosis modules not self-monitored; **qualitative evaluation only** (§VI) | `FULL-TEXT` |
| **Antonante, Nilsen & Carlone**, *Monitoring of Perception Systems: Deterministic, Probabilistic, and Learning-based Fault Detection and Identification*, arXiv 2205.10906 (2022) | Diagnostic graphs of consistency tests between perception modules, with fault-identification guarantees; evaluated in LGSVL with Apollo | `ABSTRACT` |
| Ruchkin et al., ICCPS 2022 | Composes monitor confidences | `FULL-TEXT` |
| Aslam et al., *Connected Dependability Cage*, arXiv 2604.27728 (2026) | Voting across redundant perception models; monitors sequential, qualitative | `FULL-TEXT` |
| Harder et al., HALO (2025) | Data-health and behavioural-safety monitors run **independently**; no arbitration between them (§10) | `FULL-TEXT` |
| Ferreira et al. survey, arXiv 2412.06869 | Names combining monitors and verifying consistency as open (§8) | `FULL-TEXT` |

**Correct form:** cross-layer **dependency** aggregation, inter-module **consistency tests within
perception**, and **confidence composition** all exist. **Not found:** using **disagreement** between a
monitor on the controller's output and a monitor on sensor health as **evidence that the former is
blind**, evaluated **quantitatively in closed loop**.

---

### A6 — "Conformal runtime monitors are not evaluated for missed detection under sensor faults"

**Verdict: SUPPORTED at abstract level.**

| evidence | what it shows | read |
|---|---|---|
| Fault-Adaptive Autonomy, Sensors 2021 | Conformal assurance monitor on a learned fault detector; **missed detections not evaluated** | `FULL-TEXT` |
| Boursinos & Koutsoukos, 2020–2021 | Calibrated error rates, small alarm counts | `ABSTRACT` |
| Martinez Gil et al., arXiv 2604.20122 (2026) | Adaptive conformal anomaly detection; false-alarm control only | `ABSTRACT` |
| Zhao et al. 2024; Strawn et al. 2023 | Coverage only; no sensor faults | `FULL-TEXT` / `ABSTRACT` |
| **Lindemann, Qin, Deshmukh & Pappas**, *Conformal Prediction for STL Runtime Verification*, arXiv 2211.01539 (Allerton per Semantic Scholar) | Conformal predictive runtime verification; i.i.d. calibration assumed, observations taken as true state, no faults, trajectory counts at one time instant (see §6) | `PDF-READ` |
| **Volkhonskiy, Nouretdinov, Gammerman, Vovk & Burnaev**, *Inductive Conformal Martingales for Change-Point Detection*, arXiv 1706.03415 (2017) | **Conformal change-point detection** — sequential, accumulating evidence against exchangeability | `ABSTRACT` |

**Correct form:** unchanged for the claim. **Note for remedies:** sequential conformal change detection
is **prior art**, so any persistence-accumulating conformal detector ASTRA builds (objective B5) is an
application, not a contribution.

---

### A7 — "Closed-loop masking has not been studied with learned controllers"

**Verdict: NO COUNTER-EVIDENCE FOUND — weak.** Searches across closed-loop fault masking, learned or
reinforcement-learning controllers and anomaly detection returned only classical-controller masking
(Zhang et al. 2026, PID; Gómez-González et al., adaptive PID/RLS) and work where reinforcement learning
is the *remedy* for faults. This is absence of evidence from a limited search.

---

### A8 — "Evaluation protocols don't treat fault duration as a factor"

**Verdict: PARTLY FALSE.**

| evidence | what it shows | read |
|---|---|---|
| **Tsai & Hariri**, *Mission-Level Runtime Assurance Framework for Autonomous Driving*, arXiv 2606.06996 (2026) | Fault taxonomy **varies duration — persistent versus partial recovery** (Table II). But faults are injected into **mission commands, not sensors**; detection during versus after a fault not compared; false alarms on nominal operation not evaluated | `FULL-TEXT` |
| *Bench2Drive-Robust*, arXiv 2605.18059 (2026) | Closed-loop perturbations including **ego-state estimation errors** — evaluates driving agents, not monitors | `SEARCH` |

**Correct form:** duration is a known injection parameter and closed-loop perturbation benchmarks exist.
**Not found:** a protocol evaluating **runtime monitors** under **persistent sensor faults** with a
**duration-matched** comparison of detection **during versus after** the fault.

---

## 2 · The claims, re-verified

### N1 — Integrity failure at the safety gate

- **Made before?** Not found.
- **Closest:** CoCo (Ruchkin et al. 2022) monitors observation-model assumptions for verified NN
  controllers; integrity-based path planning (Lee, Seo & Kassas 2020) uses protection levels in
  decisions; integrity monitoring (Nayak & Barth 2025).
- **Distinction that survives:** none of these measures a **runtime-assurance gate** of a **learned
  controller** failing silently under **persistent** sensor failure, nor sets it against a sensor-layer
  check in the same stack.
- **Must drop:** any implication that integrity information is unused in decisions (A2) or that
  nothing monitors observation assumptions (A3).
- **Novelty:** **medium**, with CoCo and Lee et al. as mandatory citations.

### N2 — Coverage specification met, detection zero

- **Made before?** Not found.
- **Closest:** conformal assurance monitors (Boursinos & Koutsoukos; Fault-Adaptive Autonomy 2021) —
  calibrated, but missed detections not evaluated; adaptive conformal anomaly detection (2026).
- **Distinction that survives:** a conformal runtime monitor measured to stay within its false-alarm
  specification while detecting **nothing** under closed-loop persistent sensor failure.
- **Wording correction from the literature:** a conformal guarantee is **marginal**, not a per-run
  property — write *"its false-alarm rate stays within specification on every run"*, not *"the
  guarantee holds on every run"*.
- **Novelty:** **medium**.

### N3 — The persistent-fault regime

- **Made before?** Not found.
- **Closest:** PID-Piper (excludes persistent manipulation); **DeLorean** (15–30 s attacks, detection
  assumed); SpecGuard (detection out of scope).
- **Must change:** "the regime prior work excludes" is **accurate only for PID-Piper**. Restate: *prior
  detect-and-recover work either excludes persistent manipulation or evaluates attacks lasting tens of
  seconds, and assumes a detector whose behaviour under faults persisting for the mission is not
  measured.*
- **Novelty:** **medium** — down from medium–high, because the single-paper exclusion was being
  generalised.

### N4 — Below-baseline masking under a learned controller

- **Made before?** Not found.
- **Novelty:** **low–medium**, unchanged; still conditional on reading both masking papers in full.

### N5 — Disagreement between monitors of different layers

- **Made before?** Not found in this form.
- **Closest:** Orf et al. 2024 (cross-layer **dependency** aggregation); Antonante et al. 2022
  (**consistency tests** between perception modules); CoCo 2022 (**composition**); HALO 2025
  (independent monitors); Dependability Cage 2026 (voting).
- **Distinction that survives:** **disagreement as evidence of a monitor's blindness**, quantified in
  closed loop. Complementarity of monitors alone is not distinctive.
- **Novelty:** **low–medium** — down from medium.

### N6 — Evaluation protocol

- **Made before?** Not found in this form.
- **Closest:** Tsai & Hariri 2026 vary fault duration (mission-command faults); closed-loop perturbation
  benchmarks for driving agents.
- **Distinction that survives:** runtime **monitors**, **sensor** faults, **duration-matched**
  comparison of detection **during versus after**, with a clean-arm false-alarm bar.
- **Novelty:** **low–medium** — down from medium.

---

## 3 · Consequences

### For Paper 1

The claims that survive most strongly are the ones set against the **functional** question no closest
work asks: **is the gate still able to detect?**

| rank | claim | novelty |
|---|---|---|
| 1 | **N1** gate-level integrity failure | medium |
| 2 | **N3** faults persisting for the mission, restated | medium |
| 3 | **N2** specification met, detection zero | medium |
| 4 | **N4** below-baseline masking | low–medium |
| 5 | **N5** cross-layer disagreement | low–medium |
| 6 | **N6** protocol | low–medium |

Paper 1 should now be framed as **one sharp empirical finding with a clear boundary**, not six
contributions: *a runtime-assurance gate can be alive, calibrated and confident while blind to a
persistent sensor fault — a failure that liveness watchdogs, confidence monitors and assumption
monitors are not designed to catch.* N2–N6 support it.

### For Paper 2

**B1 (runtime detection of a blind gate) must be positioned against CoCo explicitly.** CoCo asks *do the
assumptions behind the guarantee hold?*; HALO asks *is the monitor alive?*; conformal assurance monitors
ask *is this output confident?* B1's remaining distinct question is *can this gate still detect the
faults it exists for?* — and it should show on the same protocol that assumption-confidence monitors and
liveness checks do **not** flag the blindness it flags. Without that comparison, B1 will be read as a
variant of CoCo.

**B5** is an application of sequential conformal change detection (Volkhonskiy et al. 2017), not a new
method.

---

## 4 · Still not verified

| item | why it matters | effort |
|---|---|---|
| ~~CoCo full evaluation~~ — **done 13 Sept, PDF read in full; see §5** | — | done |
| ~~Henzinger & Saraç~~ — **read 15 Sept (§11): theory only, B1 holds** | — | done |
| ~~ModelGuard~~ — **read 15 Sept (§11): required baseline; bias may evade it** | — | done |
| **Papers citing CoCo** (2022–2026) — 16 listed by Semantic Scholar; Lindemann et al. read (§6) | The most likely place for "gate blindness" to have been addressed since | hours |
| ~~Luo et al.~~ — **read 15 Sept (§11): narrows B1's provable half; sharpens the core-finding mechanism** | — | done |
| **Cairoli, Bortolussi & Paoletti, *Neural Predictive Monitoring under Partial Observability*, RV 2021** | Noisy observations inside a predictive-monitor guarantee | hours |
| **Lukina, Schilling & Henzinger, *Into the Unknown: Active Monitoring of Neural Networks*, RV 2021** | A monitor that adapts when it meets the unknown | hours |
| **Granig et al., *Weakness Monitors for Fail-Aware Systems*, FORMATS 2020** | Name suggests a monitor of a system's own weakness | hours |
| **Antonante et al. full text** — do the diagnostic graphs include localization / state estimation? | Could close N5 | hours |
| **Papers citing DeLorean** — whole-mission persistent attacks? | Could close N3 | hours |
| Boursinos & Koutsoukos full texts — any false-negative evaluation? | N2 | hours |
| Both closed-loop masking papers in full | N4 | hours + access |
| Hobbs et al. run-time assurance tutorial — its state assumption | A1 (fetch failed: file too large) | hours |
| Bench2Drive-Robust | N6 | hours |

---

## 5 · CoCo — read in full from the PDF (13 September 2026)

Ruchkin, Cleaveland, Ivanov, Lu, Carpenter, Sokolsky & Lee, *Confidence Composition for Monitors of
Verification Assumptions*, ICCPS 2022, arXiv 2111.03782v3. **All 13 pages read directly** (`PDF-READ`);
this supersedes the earlier `FULL-TEXT` extraction. Page numbers are PDF pages.

| question | answer | where |
|---|---|---|
| Are observation / sensor assumptions monitored? | **Yes.** Verification rests on initial states, dynamics, and observation models capturing known sensor uncertainty; case-study assumptions bound measurement-noise parameters, monitored by a particle filter and by statistical model invalidation (ModelGuard) | §4.2 pp. 4–5; §4.3 p. 5; §5.1–5.2 pp. 8–9 |
| Is a sensor fault injected during operation? | **No.** Violations come from a steeper hill than modelled (mountain car), initial states outside the verified set, and a 33 % chance of a stuck fin — an actuator fault — in the underwater vehicle | §5.1–5.2 pp. 8–9 |
| Does confidence respond to a sensor fault over time? | **Not evaluated.** Results are episode-aggregate calibration error, Brier score and AUC | Tables 1–2 p. 8; §5.3 p. 9 |
| Is a monitor that runs but cannot detect considered? | **No.** Composition assumes each monitor carries the relevant information about its assumption; the discussion conditions detection on monitors being well-calibrated and accurate | §4.4 p. 5; §6 pp. 9–10 |
| Is monitoring other monitors discussed? | **As future work only.** A longer-term goal is to monitor the assumptions of other monitors, citing Henzinger & Saraç (RV 2020) | §6 p. 10 |

**Structural note.** CoCo's monitors consume the same observations the controller consumes, so a faulted
sensor corrupts their inputs as well — the shared-path condition ASTRA's gate-blindness monitor must avoid.
Its model-invalidation monitor, however, tests the consistency of the observation trace with the dynamics
and could plausibly flag a sensor dropout; this is untested in the paper.

**Effect.**

| item | change |
|---|---|
| Core finding | **Strengthened** — CoCo does not test sensor faults and presumes its monitors stay accurate |
| B1 | **Distinction holds** — the closest work lists monitoring other monitors as future work (2022) |
| Experiment 2.4 | **ModelGuard-style model invalidation added as a required baseline** |
| New must-reads | Henzinger & Saraç, *Monitorability Under Assumptions*, RV 2020 (could close B1); Carpenter et al., *ModelGuard*, ADHS 2021; Ruchkin et al. 2021, *Confidence Monitoring and Composition for Dynamic Assurance of Learning-Enabled Autonomous Systems*; Cimatti et al., assumption-based runtime verification with partial observability; Sokolsky et al., monitoring assumptions in assume-guarantee contracts |
| Still open | Papers citing CoCo, 2022–2026 |

---

## 6 · Lindemann et al. — read in full from the PDF (15 September 2026)

Lindemann, Qin, Deshmukh & Pappas, *Conformal Prediction for STL Runtime Verification*, arXiv
2211.01539v2 (venue listed by Semantic Scholar as Allerton; confirm). Cites CoCo. **All 24 pages read
directly** (`PDF-READ`). Page numbers are PDF pages.

| question | answer | where |
|---|---|---|
| What does it guarantee? | With probability ≥ 1−δ, the true trajectory satisfies an STL specification whenever the predicted robustness exceeds a conformal constant. Coverage is **marginal** over test and calibration data, not conditional on the calibration set | Theorems 1–2 pp. 8, 10; Remark 2 p. 8 |
| Are observation / sensor assumptions monitored? | **No.** Calibration and test trajectories are assumed independent draws from one distribution; the observed prefix is treated as the true state (robustness for past times is computed directly from observations) | Assumption 1 p. 4; §2.3 p. 6; §3.3 p. 9 |
| Is a sensor fault injected? | **No.** F-16: randomised initial conditions. CARLA: Gaussian noise on control inputs and random initial pose | §4.1 p. 11; §4.2 p. 13 |
| Per-tick behaviour reported? | **No.** One evaluation instant per case study; results are counts over 100 test trajectories | §4.1 pp. 11–12; §4.2 p. 15 |
| Is a monitor that runs but cannot detect considered? | **No.** Nothing checks whether the running trajectory still comes from the calibration distribution; outside it the guarantee lapses without any signal | Remark 2 p. 8; §5 p. 16 |

**Structural note.** The trajectory predictor reads the same observations whose correctness the guarantee
presumes, so a corrupted sensor corrupts both the prediction and the prefix it is scored against — the same
shared-path condition as ASTRA's L6 gate (proposer and twin read the same L2 state).

**Effect.**

| item | change |
|---|---|
| Core finding | **Strengthened** — a second conformal runtime monitor from the CoCo lineage assumes exchangeable, uncorrupted observations and never tests sensor faults |
| A6 | Evidence upgraded with a `PDF-READ` entry |
| B1 | **Distinction holds** — no mechanism signals that the marginal guarantee has lapsed |
| Framing for the paper | The guarantee is valid only while the monitored trajectory resembles calibration data; a persistent sensor fault is exactly the case where it silently stops applying |
| New must-reads (from its references) | Luo et al., arXiv 2109.14082 (conformal bound on a monitor's false-negative rate — **could narrow B1's provable half**); Cairoli, Bortolussi & Paoletti, RV 2021 (predictive monitoring under partial observability); Lukina, Schilling & Henzinger, RV 2021 (active monitoring of neural networks) |

---

## 7 · Cleaveland et al. — read in full from the PDF (15 September 2026)

Cleaveland, Sokolsky, Lee & Ruchkin, *Conservative Safety Monitors of Stochastic Dynamical Systems*,
arXiv 2301.11330v2 (venue listed by Semantic Scholar as NASA Formal Methods 2023; confirm). Same group as
CoCo, and cites it. **All 17 pages read directly** (`PDF-READ`). Page numbers are PDF pages.

**Method.** At design time the closed loop (dynamics, perception, state estimator, controller) is
abstracted into a probabilistic automaton; PRISM computes bounded-time safety probability for every abstract
state and control action into a lookup table. At runtime the state estimator's distribution is combined with
the table to give a safety estimate.

| question | answer | where |
|---|---|---|
| What does it guarantee? | Safety estimates are **conservative** provided (i) the abstraction is conservative, (ii) the state estimator is **well-calibrated**, and (iii) safety given the true state is independent of the monitor's output | Theorem 1 p. 10 |
| Are observation / sensor assumptions monitored? | **No.** Estimator calibration is an assumption of the theorem, validated **once offline** (ECE 0.00656). The authors state conservatism of the perception/state-estimation part cannot be formally proved | §6 pp. 9–10; §7.2 p. 15 |
| Is a sensor fault injected? | **Partly — in-distribution only.** Tank sensors have Gaussian noise and, with a constant probability each step, output 0 or full scale. These spurious readings are i.i.d., transient, and learned into the design-time perception-error model. No persistent or out-of-model fault | §7.1 p. 11; §5.1 p. 7 |
| Per-tick behaviour reported? | **No.** Two example trials plotted per step; otherwise pooled calibration (ECE, a new conservative ECCE, Brier) and ROC-AUC over 500 trials (74 unsafe) | Figs. 2–4 pp. 13–14; Table 1 p. 15 |
| Is a monitor that runs but cannot detect considered? | **No.** Conservative perception abstractions are future work | §8 p. 15 |

**Structural note.** The monitor's only runtime input is the state estimator's output — the same estimate
the controller acts on (U = c(X̂)). A persistent sensor fault that biases or freezes the estimator breaks
assumption (ii), and the theorem's conservatism lapses with no signal: the shared-path condition again.
The paper's **true-state monitor** (an oracle fed ground truth, AUC 0.870 vs 0.867) is a useful evaluation
device for ASTRA — the gap between gate-on-estimate and gate-on-truth is a direct measure of blindness.

**Effect.**

| item | change |
|---|---|
| Core finding | **Strengthened** — a third monitor from the CoCo group conditions its guarantee on a calibrated estimator and never tests a fault outside the calibrated model |
| A1 | **Theorem-level citation** — Theorem 1 explicitly assumes a well-calibrated state estimator |
| N3 wording | Must say **persistent, out-of-model** sensor faults: modelled transient spurious readings *are* handled here |
| B1 | **Distinction holds** |
| Experiment design | Add a ground-truth-fed gate as an oracle reference, following this paper's true-state monitor |
| New must-read | Granig et al., *Weakness Monitors for Fail-Aware Systems*, FORMATS 2020 |

---

## 8 · Peper et al. — read in full from the PDF (15 September 2026)

Peper, Miao, Mitra & Ruchkin, *Towards Unified Probabilistic Verification and Validation of Vision-Based
Autonomy*, ATVA 2025 (Springer), arXiv 2508.14181v1. Cites CoCo. **All 31 pages read directly**
(`PDF-READ`). Page numbers are PDF pages.

**Method.** (1) Build an interval-MDP abstraction of the closed loop from training data, with
Clopper–Pearson intervals on perception transition probabilities (confidence α). (2) Model-check a
safety property (chance 1−β). (3) In a new environment, update a Dirichlet posterior over perception
parameters from validation data and compute the posterior probability that it falls inside the IMDP
intervals (confidence 1−γ, median over abstract states). Theorem 2 gives a nested guarantee that
degrades with γ.

| question | answer | where |
|---|---|---|
| Does it detect that the perception assumption no longer holds? | **Yes — offline.** Validation is framed as a design-time problem on a dataset of i.i.d. trajectories collected in the new environment | Problem 3 p. 5; §4.3 p. 11 |
| Does it need ground truth? | **Yes.** Validation bins **state/estimate pairs**; the true state must be known for each sample | Alg. 3 lines 2–3 p. 13; §5.1 p. 16 |
| Is a sensor fault injected? | **A persistent bias, as a separate environment.** State-estimate noise offset by a scalar; 1000 trajectories per environment. Shifts ≥ 2.45 → confidence 0.0000; in-distribution 0.65–0.78; **shifts between 0 and 2.45 excluded** as not conclusively in or out of distribution | §5.1 p. 17; Table 2 p. 18 |
| Is it evaluated within a run, online? | **No.** One confidence value per environment dataset | Table 2 p. 18 |
| Is a monitor that runs but cannot detect considered? | **No.** It validates the perception model, not a monitor's detection capability | §4.3; §6 p. 20 |
| Statements usable as gap citations | Intro: a fundamental gap remains between assume-guarantee verification and the validity of the assumptions in the deployed system. Related work: perception-contract approaches have not been investigated under changed visual distributions | §1 p. 2; §2 p. 4 |

**Effect.**

| item | change |
|---|---|
| Core finding | **Holds, but must be worded precisely.** Detecting that a persistent estimation bias invalidates a perception-based guarantee **is done — offline, with ground truth, per environment dataset**. ASTRA's distinction: **online, within a run, at fault onset, with no ground truth** |
| N3 | Persistent bias is studied as a *deployment environment*, not as a fault arriving mid-run |
| B1 | **Distinction holds** — the object validated is a model, not a monitor's detection capability |
| Positioning | **Closest analogue found so far.** Cite as the offline, ground-truth counterpart of what ASTRA does online |
| Evaluation design | Their exclusion of small shifts (0–2.45) marks the hard, ambiguous regime; ASTRA should report detection across a magnitude sweep that *includes* it rather than excluding it |
| New must-reads | Ruchkin et al., *Compositional Probabilistic Analysis of Temporal Properties over Stochastic Detectors*, IEEE TCAD 2020 (runtime confidence monitoring of model validity); Waite et al., arXiv 2502.21308; Dutta et al., HSCC 2025 |

---

## 9 · Mao et al. 2025 — read from the PDF (15 September 2026)

Mao, Umasudhan & Ruchkin, *How Safe Will I Be Given What I Saw? Calibrated Safety Prediction for
Image-Controlled Autonomy*, arXiv 2508.09346v3 (March 2026; journal extension of L4DC 2023). Cites CoCo.
Pages 1–25 read directly (`PDF-READ`); references skimmed.

| question | answer | where |
|---|---|---|
| What is it? | Image-sequence safety-chance predictors (monolithic or world-model composite), post-hoc calibration, per-bin conformal bounds on calibration error, and test-time adaptation (MEMO) of the safety evaluator | §4 pp. 10–17 |
| Is a shift detected at runtime? | **Ambiguous.** Introduction describes the adaptation module as detecting shifts; the method applies adaptation to every sample with no detection step | §1 p. 3; §4.3 pp. 13–15 |
| Sensor faults? | **Not injected.** Shift is prediction-induced (decoder artifacts); OOD test subset is 500 manually labelled predicted images | §4.3; §5.2 p. 23 |
| Assumptions | Calibration data drawn from independent trajectories to satisfy exchangeability. For trajectory-level OOD the paper **asserts** that predicted chances become more uncertain and intervals wider, alerting the controller — **no experiment tests this** | p. 10; p. 15; Thm 1 p. 17 |
| Per-tick results? | **No** — pooled metrics per test set | Tables 1–4 |

**Effect.**

| item | change |
|---|---|
| Core finding | **Strengthened** — no sensor faults, no online detection |
| Literature assumption | New, citable instance of the belief ASTRA's results contradict: **a calibrated monitor's uncertainty will rise when its inputs leave the training distribution** (asserted, untested, p. 15) |
| B1 | **Distinction holds** |

---

## 10 · Cleaveland et al. 2025 — read in full from the PDF (15 September 2026)

Cleaveland, Lu, Sokolsky, Lee & Ruchkin, *Conservative Perception Models for Probabilistic Verification*,
arXiv 2503.18077v3 (July 2025; venue not stated). Cites CoCo. **All 13 pages read directly** (`PDF-READ`).

| question | answer | where |
|---|---|---|
| What is it? | Offline, data-driven construction of interval-MDP perception models that are provably conservative with probability 1−α: per-bin Clopper–Pearson intervals, enlarged by a logistic-regression estimate of within-bin change | §V pp. 5–7; Lemma 1, Thm 1 p. 7 |
| Runtime monitoring? | **No** — verification only | — |
| Sensor faults? | **No.** Synthetic detector with distance-dependent detection probability; YOLO11 in CARLA with constant-speed data collection | §VII pp. 8–9 |
| Key assumptions | Detection depends only on current state with independent noise — **no temporal memory** (conditioning on previous outputs is future work); enlargement bounds within-bin variation (empirically "largely upheld", theory open); ground-truth states available for model construction | Eq. 7 p. 4; fn. 5 p. 7; §VIII p. 10 |

**Effect.**

| item | change |
|---|---|
| Core finding / B1 | **No overlap** |
| N3 | **Supporting citation** — the perception model is memoryless by construction, so temporally persistent faults (stuck or frozen outputs) lie outside what the guarantee can represent |
| CoCo-citing papers | 5 of 15 now read in full; 8 cleared at abstract; 1 skipped; **only Arnez et al. 2022 remains** |

---

## 11 · ModelGuard, Luo et al., Henzinger & Saraç — read in full from the PDFs (15 September 2026)

All three `PDF-READ`. Page numbers are PDF pages.

### Carpenter, Ivanov, Lee & Weimer, *ModelGuard*, ADHS 2021, arXiv 2104.15006v1 (7 pp.)

| question | answer | where |
|---|---|---|
| What is it? | Sampling-based runtime model validation for black-box Lipschitz models: a trace is *consistent* if some parameter (incl. initial state) reproduces it within ε (guaranteed), otherwise *inconsistent* with confidence γ | §2–3 pp. 2–4; Thm 2 |
| Faults evaluated | Random noise added to half the mountain-car traces; UUV fin damage (actuator); real F1tenth LiDAR with no injected fault | §4.1–4.3 pp. 4–5 |
| Online? | Sketched only: 1 s window, alarm if > 2/3 inconsistent, 4 F1tenth trials (would warn ~3 s before crash). Consistent labels < 0.5 s; high-confidence inconsistency infeasible at runtime | §4.4, Table 1, Fig. 4 p. 6 |
| Monitors another monitor? | **No** | — |

**My inference, not stated in the paper:** a frozen or dropped sensor contradicts the dynamics and should be flagged; a constant offset within the parameter bounds can be absorbed into the initial state and pass as consistent. **Effect:** required baseline for experiment 2.4 — include bias and drift, where it may fail. B1 holds.

### Luo et al., *Sample-Efficient Safety Assurances using Conformal Prediction*, arXiv 2109.14082v5 (15 pp.)

| question | answer | where |
|---|---|---|
| What does it guarantee? | Warning system with FNR ≤ ε + 1/(1+n), n = number of labelled unsafe calibration examples (class-conditional conformal) | Prop. 1 p. 7 |
| Assumption | Each test sample exchangeable with the calibration pairs (simulator prediction, true future) | Assumption 1 p. 6 |
| Faults? | **None.** nuScenes / Lyft with Trajectron++; DexNet grasping | §4–5 |
| Uninformative detector | Surrogate score replaced by pure noise: FNR stays within bound, FPR rises to 0.90–0.95 — the system **always alarms** | Fig. 13d p. 13 |
| Shift | Handled by recollecting calibration data; non-exchangeable conformal is future work | p. 6; §6 p. 13 |

**Effect.**

| item | change |
|---|---|
| B1 provable half | **Narrowed.** Few-sample conformal bounds on a warning system's error rate are prior art; ASTRA's bound on false "blind" flags is an application. Novelty rests on *what* is monitored — the gate's detection capability |
| Core finding | **Mechanism sharpened, citable.** Under exchangeability an uninformative detector fails *loudly* (Luo, Fig. 13d). ASTRA's gate fails *silently* (≈0.2 % alarms under sustained `imu_dropout`) because the persistent fault breaks exchangeability — precisely the case outside the guarantee |

### Henzinger & Saraç, *Monitorability Under Assumptions*, RV 2020 (16 pp.)

| question | answer | where |
|---|---|---|
| What is it? | Theory of whether a trace property is monitorable in principle when traces are restricted to an assumption A: boolean closure, relative safety/co-safety, register-monitor resources, topological constructions of assumptions | §2–5 |
| Is the assumption checked at runtime? | **No** — taken as given | — |
| Monitoring monitors? | Assumptions may come from "another, connected monitor"; assume-guarantee monitoring and networks of monitors are **future work** | §1 p. 1; §6 p. 15 |
| Probability, sensors, faults, experiments? | **None** | — |

**Effect.** B1 distinction **holds** — CoCo's pointer to this paper leads to static theory, not a runtime check of a monitor. Vocabulary: *zero monitoring information* (Peled & Havelund 2019) is the qualitative analogue of a blind gate. Correction: Cimatti, Tian & Tonetta, *Assumption-based runtime verification with partial observability and resets*, is **RV 2019**.

### Not read

`1.pdf`, supplied for Granig et al., contains only the FORMATS 2020 front matter; the chapter (pp. 283–300) is still needed. The contents page adds a lead: Kempa et al., *Embedding Online Runtime Verification for Fault Disambiguation on Robonaut2*, FORMATS 2020.

---

## 12 · Conformal under shift: Volkhonskiy et al., Gibbs & Candès, Barber et al. (15 September 2026)

Read via full-text extraction of the PDFs (`PDF-READ`; Barber et al. §5 skimmed, appendices not read).
Purpose: check whether B1 — detecting that the gate has gone blind — is already an established conformal
technique.

| paper | what it does | what it assumes / lacks | effect |
|---|---|---|---|
| **Volkhonskiy et al.**, COPA 2017, arXiv 1706.03415 | Inductive conformal test martingales on p-values for change-point detection | Truncated martingale valid only empirically (§3.4); synthetic 1-D mean increases only; constant betting function bets on small p-values | **B1 mechanism narrowed** — a test martingale on the gate's p-values is an application. Remaining contribution: one-sided test for too-large p-values; closed-loop temporal correlation |
| **Gibbs & Candès**, NeurIPS 2021, arXiv 2106.00170 | Online α_t update restores long-run coverage under any shift | Needs the label Y_t every step (§7) | Not applicable to an unlabelled detection gate; applied to alarms it would force the alarm rate to α and **mask** both silence and alarm bursts (my inference). Add as a baseline in 2.5 |
| **Barber et al.**, Ann. Stat. 2023, arXiv 2202.13415 | Coverage-gap bound via total variation; weighted / nonsymmetric conformal | Weights fixed in advance; direction of error (under/over-coverage) cannot be known in advance (p. 16) | **Gap citation for B1:** p. 18 lists as an open question determining adaptively whether coverage will hold. Over-coverage = silent gate |

**Consequences for the paper.**

1. **B1 is not a new statistical method.** Its pieces — conformal p-values, test martingales, coverage-gap
   theory — are established. The claim must be: *a runtime detector of a safety gate's loss of
   detection capability in closed loop, with evidence that it catches the silent failure* — for which no prior work was found (never "the first"). Cite Volkhonskiy
   for the tool, Barber for the open question, Luo for the loud-versus-silent contrast.
2. **Design requirement discovered.** A standard two-sided exchangeability test fires both when the gate
   correctly alarms on a fault and when it goes blind. The blindness monitor must test **one-sidedly for
   too-large p-values** (under-alarming), and must be calibrated on **whole clean runs** because tick
   scores are temporally correlated.
3. **Reviewer defence.** "Why not adaptive conformal?" — it needs labels and, used on alarms, restores the
   alarm *rate* while destroying its *meaning*.
4. Vovk, Nouretdinov & Gammerman (ICML 2003) no longer needs a full read; Volkhonskiy covers the technique.

---

## 13 · Lukina, Schilling & Henzinger — read in full (18 September 2026)

*Into the Unknown: Active Monitoring of Neural Networks*, RV 2021, arXiv 2009.06429v4 (`PDF-READ`, 20 pp.).

| question | answer | where |
|---|---|---|
| What is it? | A monitor beside an image classifier flags inputs of unknown classes; a human labels flagged inputs; the monitor and network adapt when run-time precision drops | §4 pp. 6–10 |
| Does the monitor assess itself? | **Yes, but only its precision** — the share of its warnings that were correct. Run-time precision can only be computed on samples the monitor reported | §3 p. 5 |
| Could it notice a monitor that stopped warning? | **No.** Unflagged inputs are never labelled, so missed detections are invisible; fewer warnings would, if anything, look like higher precision (my inference) | — |
| Sensors, control, faults? | **None** — MNIST, FMNIST, CIFAR10, GTSRB, EMNIST | §5 |

**Effect.** B1 distinction **holds and sharpens**: the nearest self-assessing monitor found can detect
*false alarms* but, by construction, not *silence*. New must-read from its references: **Sun & Lampert,
KS(conf), IJCV 2020** — a distribution test on classifier confidence scores against validation data, the
closest mechanism to B1 yet named.

---

## 14 · Sun & Lampert, KS(conf) — read (18 September 2026)

arXiv 1804.04171v1 (IJCV 2020). §1–4 read; per-network figures skimmed (`PDF-READ`, text extraction).

| question | answer | where |
|---|---|---|
| What is it? | Two-sided Kolmogorov–Smirnov test of batches of a classifier's own top-1 confidences against a calibration distribution; no labels; FPR = α with universal thresholds | §2.2 pp. 4–7 |
| Faults? | **Camera/sensor faults** on images: blur, Gaussian noise, dead/hot pixels, exposure, geometry/colour — all detected at sufficient strength and batch size; small noise (σ = 5) undetectable for some networks | §3.6 pp. 16–28 |
| Direction | Confidences do not always fall out of spec (NASNet more confident on pure noise); one-sided mean tests fail, hence a two-sided test | Table 2 p. 12; §3.5 p. 16; §3.6.3 p. 22 |
| Stated limit | An output-based test could miss input changes that leave the outputs unchanged | §2 p. 4 |
| Scope | Classifier, i.i.d. batches, open loop; no safety monitor, no control | — |

**Effect on B1 — the most important narrowing so far.**

- **Score-only B1 ≈ KS(conf) on the gate.** A distribution test on the gate's own scores is an application
  of a 2018 method. KS(conf) must be the **primary baseline**.
- **What KS(conf) cannot do**, and B1 must:
  1. **Tell blind from working.** Being two-sided, it fires both when the gate correctly alarms on a fault
     and when it goes silent — it detects *inputs out of spec*, not *loss of detection capability*.
  2. **Handle closed-loop correlation.** Its thresholds assume i.i.d. batches.
  3. **See faults that leave the gate's scores unchanged.** Its own authors state this limit. Here only
     **cross-layer evidence** can help — another layer reports a fault while the gate stays silent.
- **Consequence:** B1's distinct form is **cross-layer**: detect gate blindness from the *disagreement*
  between an independent fault indicator and the gate's silence, with a score-distribution test (KS(conf) /
  conformal martingale) as the baseline it must beat. This matches the "correct form" recorded under A3.
