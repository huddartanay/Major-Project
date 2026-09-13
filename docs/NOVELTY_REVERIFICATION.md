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
| **Henzinger & Saraç, *Monitorability Under Assumptions*, RV 2020** — cited by CoCo for monitoring other monitors' assumptions | Could close B1 | hours |
| **Carpenter et al., *ModelGuard*, ADHS 2021** — would its model invalidation flag sensor dropout? | Decides the baseline in experiment 2.4 | hours |
| **Papers citing CoCo** (2022–2026) | The most likely place for "gate blindness" to have been addressed since | hours |
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
