# Novelty claims for the conference submission

**Revised 13 September 2026** against the closest-work pass in `docs/CLOSEST_WORK.md`, and again
against the literature re-verification in `docs/NOVELTY_REVERIFICATION.md`. Supersedes earlier versions.

> **Re-verification result.** No published paper found makes any of these claims, but **all six were
> narrowed**, and four assumptions about the literature were corrected: integrity information *is* used
> in planning decisions; monitors *are* monitored — for liveness (HALO), per-decision confidence
> (conformal assurance monitors) and assumption validity (**CoCo, Ruchkin et al., ICCPS 2022**); the
> persistent-fault exclusion is PID-Piper's, not the whole line of work (DeLorean evaluates 15–30 s
> attacks); and cross-layer diagnosis aggregation exists. **The boundary every claim now rests on:
> liveness and confidence are checked in prior work; functional detection capability of the safety
> gate is not.**

For Paper 1 (target IEEE ITSC; alternative IEEE ISSRE). Evidence is on branch `3.0`; see
`docs/GAP_VERIFICATION.md`.

**How novelty is preserved here.** Every claim is narrowed to the **intersection the closest work does
not reach**, and that closest work is cited inside the claim. None of this is done by wording: a claim
that merely sounds different from Nayak & Barth or PID-Piper will be caught by any reviewer who knows
them. Where a claim is still exposed, it says so.

---

## 0 · Rules

1. **Claim against named prior work.** Every "existing work does not…" names who, and where.
2. **No "first", no "novel" until V2 is logged.** Then "to our knowledge", and only for claims rated
   high or medium.
3. **The architecture is not the contribution.** It is the instrument.
4. **Borrow the vocabulary of the closest field; don't compete with it.** Integrity monitoring already
   names the core phenomenon at the estimator level. ASTRA's claims sit one layer higher and say so.
5. **Prior terminology is cited, not claimed** — *hazardously misleading information* (integrity
   monitoring), *silent failure* (Zudaire et al. 2021; Or 2026).

---

## 1 · Positioning in one paragraph

Navigation integrity monitoring detects when a **position estimate** is wrong while the system claims
it is safe. Runtime assurance for learned controllers guards the **controller**, and assumes — in its
most recent form, explicitly — that the sensors feeding its gate are nominal. Between the two sits the
safety gate itself, and no checked work asks whether **the gate** can still see. We measure a gate that
cannot: under a persistent sensor failure it goes quieter than its healthy baseline, a condition
analogous to hazardously misleading information but occurring at the governance layer, while an
integrity-style check on the sensor layer of the same stack detects the fault within five ticks.

## 2 · The headline sentence

> In a runtime-assurance stack supervising a learned controller, a conformal safety gate with valid
> calibration goes quieter than its own healthy baseline for as long as a sensor failure persists —
> a failure analogous to hazardously misleading information, occurring at the gate rather than the
> estimate — while an integrity-style check on the sensor layer of the same stack detects the fault
> within five ticks.

**Conditions:** P1, `medium` severity, one synthetic plant. "Analogous to" is deliberate: the
integrity-monitoring definition is formal (an error exceeding a protection level without an alert
within the time-to-alert), and ASTRA has not computed protection levels.

---

## 3 · The claims

Ratings: **Evidence** is about our data. **Novelty** is about the literature — **High**: closest work
checked states its own limitation; **Medium**: closest work checked does not reach the claim, searches
incomplete; **Low**: plausibly published.

---

### N1 — Integrity failure at the safety gate, not the estimate

**Revised from:** "a measured counter-example to the nominal-sensor assumption." That framing ignored
that detecting a wrong estimate is a mature field.

| | |
|---|---|
| **Closest work** | **Nayak & Barth**, integrity monitoring for CAVs, arXiv 2502.04874 (2025): detects hazardously misleading information in the **position estimate**; does not address a downstream safety monitor reading that estimate; names integrity of AI/ML systems as largely unexplored. **Dean et al.**, measurement-robust CBFs, CoRL 2020: safety under **bounded** estimation error, no fault detection. **Bansal et al.**, Synergistic Simplex, 2026: assumes nominal sensors (**Assumption 8**). **Bansal et al.**, Perception Simplex, STVR 2024: cross-checks **obstacle-detection** faults, not state sensors. **Ruchkin et al.**, *Confidence Composition for Monitors of Verification Assumptions* (CoCo), ICCPS 2022: monitors **observation-model assumptions** of verified NN controllers at runtime and composes them into confidence that guarantees hold. **Lee, Seo & Kassas**, ION GNSS+ 2020: **protection levels used as cost and constraint in path planning** (offline). **Rober, Jia & How**, arXiv 2608.20467 (2026): states that most safety filters assume perfect state information |
| **What remains unreached** | A runtime-assurance **gate** for a **learned controller** measured under **persistent** sensor failure — beyond the bound robust filters assume, and inside the regime Synergistic Simplex declares out of scope — and shown to fail while integrity-style evidence in the same stack does not |
| **Claim** | Integrity failure is shown at the **safety gate** of a learned-controller runtime-assurance stack: the gate reports no hazard throughout a persistent sensor failure, while an integrity-style sensor-layer check detects it |
| **Evidence** | Gate **0 / 30** under sustained `imu_dropout`; sensor-layer health check **30 / 30**, **0 / 30** clean false positives, median **5 ticks** (E18-R3c, E21) |
| **Evidence rating** | Strong |
| **Novelty rating** | **Medium.** The estimator-level problem is solved; the gate-level measurement is not found |
| **Must do** | **Read the integrity-monitoring literature beyond the survey** — any work feeding protection levels into a safety or control decision could close this claim. V1 (Assumption 8 in the PDF). A1 reproduction |
| **Wording** | *"Integrity monitoring detects misleading position estimates [Nayak & Barth], and recent runtime-assurance architectures assume nominal sensors [Synergistic Simplex, Assumption 8]. We show the missing case between them: the safety gate itself fails silently under persistent sensor failure, while an integrity-style check in the same stack does not."* |

---

### N2 — A satisfied coverage guarantee with zero detection

**Revised:** adds the closest adaptive conformal detector as a named comparator; claim unchanged in
substance.

| | |
|---|---|
| **Closest work** | **Zhao et al.**, robust conformal STL verification, 2024: coverage under a known f-divergence bound; open-loop; perfect observation. **Strawn, Ayanian & Lindemann**, RA-L 2023: coverage of trajectory-prediction uncertainty; no sensor faults. **Martinez Gil et al.**, adaptive conformal anomaly detection, arXiv 2604.20122 (2026): false-alarm control under shift; no closed loop or sensor faults mentioned. **Guérin et al.**, AAAI 2023: monitors can give a false impression of safety — offline, perception. **Conformal assurance monitors** — Boursinos & Koutsoukos (2020–2021); *Fault-Adaptive Autonomy in Systems with Learning-Enabled Components*, Sensors 2021 — calibrated confidence on learned components; **missed detections not evaluated**, and faults are actuator degradation |
| **What remains unreached** | A conformal runtime monitor measured to **meet** its false-alarm specification while **detecting nothing**, under closed-loop persistent sensor failure |
| **Claim** | The gate's false-alarm rate stays within its specification on every run while its detection of a persistent sensor fault is zero: the specification is met while the gate's detection function fails. *(A conformal guarantee is marginal, not per-run — do not write that "the guarantee holds on every run".)* |
| **Evidence** | Calibration in band on **30 / 30** runs, clean false-alarm median **5.84 %** (E18-R3); **0 / 30** detection, alarm rate **≈ 0.2 %** under sustained fault (E18-R3c) |
| **Evidence rating** | Strong |
| **Novelty rating** | **Medium** |
| **Must do** | **A2(c): run adaptive conformal inference and the Martinez Gil et al. weighted-conformal detector** on the shared protocol. If either catches sustained `imu_dropout`, restrict this claim to split conformal. A2(b) confidence intervals |
| **Wording** | *"The monitor's false-alarm rate stays within specification on every run, and it detects no persistent sensor fault."* Never "conformal prediction fails" |

---

### N3 — Evaluating the excluded regime

**Revised and strengthened** by PID-Piper's threat model.

| | |
|---|---|
| **Closest work** | **Dash et al.**, PID-Piper, DSN 2021 (`PDF-READ`): detects and recovers using a learned model of the controller whose deviation from the real controller is thresholded; its **threat model excludes persistent drastic sensor manipulation and attacks on all sensors at once (§II-E)**. **Dash, Li, Karimibiuki & Pattabiraman**, DeLorean, ASIA CCS 2024: lifts the all-sensor exclusion; attack duration not stated in its threat model; **evaluated attacks last 15–30 s**; **assumes an existing detector** (PID-Piper's). **Dash, Chan & Pattabiraman**, SpecGuard, CCS 2024: detection out of scope; detector not measured. **Tatbul et al.**; **TaPR**: account for post-anomaly periods in time-series evaluation (*not yet read*) |
| **What remains unreached** | Detection measured for faults that **persist for the remainder of the mission** — excluded by PID-Piper and not evaluated by DeLorean or SpecGuard — with a duration-matched control showing that detection measured on faults that end does not transfer to faults that persist |
| **Claim** | For sensor faults that persist for the remainder of a mission — a regime prior detect-and-recover work either excludes or does not evaluate — a residual gate comparing a learned controller's output against a learned reference fails to detect a persistent sensor dropout, and its apparent detection of that fault when transient came from the recovery transient |
| **Evidence** | Ticks 400–999 alarm rate **99.06 %** when the fault ends against **0.18 %** when it persists; identical 0.38 % during the fault (E18-R3b vs R3c) |
| **Evidence rating** | Strong |
| **Novelty rating** | **Medium.** Downgraded from medium–high: the explicit exclusion is PID-Piper's alone; DeLorean evaluates attacks of tens of seconds rather than excluding persistence |
| **Must do** | Read Tatbul et al. and TaPR; forward citations of PID-Piper for anyone who has lifted the exclusion |
| **Wording** | *"Prior detect-and-recover work either excludes persistent sensor manipulation [PID-Piper, §II-E] or evaluates attacks lasting tens of seconds while assuming a working detector [DeLorean]. We evaluate faults that persist for the rest of the mission."* **Do not** claim that PID-Piper itself would fail — ASTRA's gate is only *structurally similar* to its detector, and PID-Piper was not run |

---

### N4 — Below-baseline masking against a runtime-assurance gate under a learned controller

**Unchanged in substance; still the most exposed claim.**

| | |
|---|---|
| **Closest work** | **Zhang, Yang, Dandago & Li**, Springer 2026: closed-loop masking under **PID**. **Gómez-González, Fischer et al.**, Springer: masking of data-driven detectors under **adaptive PID/RLS** |
| **What remains unreached** | Masking under a **learned policy**, against a **runtime-assurance gate**, strong enough to push the alarm rate **below** the healthy baseline |
| **Claim** | Extending closed-loop fault masking to a runtime-assurance gate supervising a learned policy, the gate's alarm rate falls below its healthy baseline |
| **Evidence** | ≈ 0.2 % under sustained fault against 5.84 % clean median (E18-R3c) |
| **Evidence rating** | Strong |
| **Novelty rating** | **Low–medium** |
| **Must do** | **V3** — both masking papers in full. **A3** — a matched classical controller. Until A3: "under a learned controller", never "caused by" |
| **Wording** | *"Consistent with closed-loop fault masking [Zhang et al.; Gómez-González et al.] and extending it to…"* — **cite the masking work before stating the result** |

---

### N5 — Disagreement between monitors of different layers carries the missing evidence

**Revised and narrowed.** Within-function redundancy is not claimed.

| | |
|---|---|
| **Closest work** | **Aslam et al.**, Connected Dependability Cage, arXiv 2604.27728 (2026): a function monitor **voting across redundant perception models** plus an anomaly monitor; run **sequentially**, not cross-checked; **qualitative evaluation only**. **Perception Simplex** (Bansal et al. 2024): verifiable cross-check **within perception**. **Hua et al.** 2025: budgeted **score** combination, AI code review. **Ferreira et al.** survey §8: combining monitors and verifying consistency is open. **Orf et al.**, arXiv 2411.09643 (2024): **cross-layer dependency-graph aggregation** from sensors to execution — OR-aggregation and root-cause traversal, not disagreement; qualitative. **Antonante, Nilsen & Carlone**, arXiv 2205.10906 (2022): diagnostic graphs of **consistency tests between perception modules**. **Harder et al.**, HALO (2025): data-health and behavioural monitors run independently, no arbitration. **CoCo** (2022): composes monitor confidences |
| **What remains unreached** | Monitors observing **different layers** — a sensor-integrity check and a statistical gate on the controller's output — whose **disagreement** is used as **evidence that one of them is blind**, **quantitatively, in closed loop**. Complementarity alone is not distinctive. **Novelty downgraded to low–medium** |
| **Claim** | Across layers, the stack's monitors are complementary: each is blind where the other sees, and their disagreement locates the faults the gate misses |
| **Evidence** | Health check catches `imu_dropout` (gate 0.00); gate catches `lateral_noise` (health 0.00); union 4 of 6 against the gate's 3 of 6; 30 seeds, clean-arm bar (E21) |
| **Evidence rating** | Strong for complementarity; **systematic disagreement signature not yet measured** |
| **Novelty rating** | **Medium** |
| **Must do** | **A4** — the disagreement signature across 30 seeds, not single ticks. V2. Read the diverse-redundancy consistency literature (search lead only) |
| **Wording** | *"Voting across redundant perception models [Dependability Cage] and verifiable cross-checks within perception [Perception Simplex] address redundancy within a function. We show that disagreement between monitors of different layers carries the evidence a gate lacks."* **No fusion method is claimed** — Paper 1 has none |

---

### N6 — An evaluation protocol that detects silent failure beyond task completion

**Revised and strengthened**: it answers questions the closest reviews state as open.

| | |
|---|---|
| **Closest work** | **Or**, Silent Failures in Physical AI, arXiv 2606.00090 (2026): lists **what evaluation methods detect silent failures beyond task completion** as an open question (§9.5). **Ferreira et al.** §8: no unified benchmark. **Guérin et al.**, AAAI 2023: evaluate monitors on errors caught, not OOD scores. **Guérin et al.** 2022: single-monitor, offline metrics. **Tsai & Hariri**, arXiv 2606.06996 (2026): fault injection **varying duration — persistent versus partial recovery** — but for mission-command faults, without during-versus-after comparison or nominal false-alarm evaluation |
| **What remains unreached** | A released, pre-registered protocol for runtime **monitors** under persistent **sensor** faults, in closed loop, with a **duration-matched** comparison of detection **during versus after** the fault and a clean-arm false-alarm bar. Duration as a parameter alone is not distinctive. **Novelty downgraded to low–medium** |
| **Claim** | A pre-registered evaluation protocol that exposes silent gate failure: sustained versus transient injection with a duration-matched control; phase-resolved detection; a clean-arm false-positive bar alongside detection; the run as the unit; frozen thresholds; recorded withdrawals |
| **Evidence** | Applied across E17–E21 and Phase 2; pre-registrations precede results (`ae997b3` → `4615cdc`; `db090f2` → `236330e`) |
| **Evidence rating** | Strong |
| **Novelty rating** | **Medium** |
| **Must do** | Release the protocol and harness with the paper |
| **Wording** | *"Addressing an open question on evaluating silent failures beyond task completion [Or, §9.5], we contribute and release…"* |

---

## 4 · Ranking for the submission

| rank | claim | evidence | novelty | ready? |
|---|---|---|---|---|
| 1 | **N1** integrity failure at the gate | strong | medium | after reading CoCo's case studies and papers citing CoCo; V1; A1 |
| 2 | **N3** faults persisting for the mission | strong | medium | after papers citing DeLorean; TaPR / Tatbul |
| 3 | **N2** specification met, detection zero | strong | medium | after A2(c) and Boursinos & Koutsoukos full texts |
| 4 | **N4** below-baseline masking | strong | low–medium | after V3 and A3 |
| 5 | **N5** cross-layer disagreement as evidence of blindness | strong / partial | **low–medium** | after A4; Antonante et al. full text |
| 6 | **N6** protocol | strong | **low–medium** | when released |

**What changed after re-verification:** N3 drops from medium–high to medium, because the explicit
exclusion belongs to PID-Piper alone. N5 and N6 drop to low–medium, because cross-layer diagnosis
aggregation and duration-varied fault injection both exist. N1 returns to first: it rests on the one
boundary that held across every search — **no work checks whether a safety gate can still detect**.

**Frame Paper 1 as one sharp finding, not six contributions:** *a runtime-assurance gate can be alive,
calibrated and confident while blind to a persistent sensor fault — a failure that liveness watchdogs,
confidence monitors and assumption monitors are not designed to catch.* N2–N6 support it.

---

## 5 · Not novel — cite, do not claim

| topic | prior work | read |
|---|---|---|
| Detecting a wrong estimate held with false confidence | Integrity monitoring — Nayak & Barth 2025 and the RAIM / Kalman-integrity literature | survey full text; primary sources **not yet** |
| Safety under bounded estimation error | Dean et al., CoRL 2020 | abstract |
| Detect-and-recover from sensor attacks | PID-Piper, DSN 2021; SpecGuard, CCS 2024 | PDF pp. 1–5; full text |
| Runtime prediction of a perception component's misses | Yang et al., Sensors 2021 | full text |
| Runtime monitoring of plan assumptions; "silent mission failure" | Zudaire et al., ICRA 2021 | PDF pp. 1–2 |
| "Silent physical-action failure" as a framing | Or, arXiv 2606.00090, 2026 | full text |
| Voting across redundant perception models | Aslam et al., 2026 | full text |
| Verifiable cross-checks within perception | Bansal et al., Perception Simplex, 2024 | abstract |
| Simplex over neural controllers | Phan et al., NFM 2020 | abstract |
| Conformal safety filters for RL | Strawn, Ayanian & Lindemann, RA-L 2023 | abstract |
| Adaptive conformal anomaly detection under shift | Martinez Gil et al., 2026 | abstract |
| Monitors that look good while missing errors | Guérin et al., AAAI 2023 | abstract |
| Closed-loop fault masking | Zhang et al. 2026; Gómez-González et al. | abstract |
| Offline metrics vs deployed reliability (general) | Rashidi, 2026 | full text |
| **Monitoring a verified system's assumptions, including observation models, and composing confidence that guarantees hold** | **Ruchkin et al., CoCo, ICCPS 2022** | full text |
| Liveness watchdogs on safety monitors | Harder, Kulkarni & Behl, HALO, 2025 | full text |
| Conformal (ICP) assurance monitors on learned components | Boursinos & Koutsoukos 2020–2021; Fault-Adaptive Autonomy, Sensors 2021 | abstract / full text |
| Protection levels used in path-planning decisions | Lee, Seo & Kassas, ION GNSS+ 2020 | PDF p. 1 |
| Cross-layer dependency-aware fault-diagnosis aggregation | Orf et al., arXiv 2411.09643, 2024 | full text |
| Consistency tests between perception modules with guarantees | Antonante, Nilsen & Carlone, arXiv 2205.10906, 2022 | abstract |
| Recovery from attacks on multiple sensors, detection assumed | Dash et al., DeLorean, ASIA CCS 2024 | full text |
| Fault duration as an injection parameter | Tsai & Hariri, arXiv 2606.06996, 2026 | full text |
| Sequential conformal change-point detection | Volkhonskiy et al., arXiv 1706.03415, 2017 | abstract |
| Semantic anomaly detection | Elhafsi et al., 2023 | abstract |
| Secure state estimation under attack | Fawzi/Tabuada; Pasqualetti et al. | **not yet read** |

---

## 6 · Reserved for Paper 2 — not claimable now

| future claim | closes | positioning after the closest-work pass |
|---|---|---|
| **B1** runtime detection that a safety gate has gone blind | L4 | **Introspection for safety gates** — extends runtime failure prediction from perception components (Yang et al. 2021) and assumption monitoring from plans (Zudaire et al. 2021) to the gate. **Must be positioned against CoCo** (assumption confidence), HALO (liveness) and conformal assurance monitors (per-decision confidence), and must show on the same protocol that those do **not** flag the blindness B1 flags. Candidate formalism: integrity-style **protection levels** answering "can this gate currently see?" |
| **B2** cross-layer consistency fusion | L3 | Beyond within-function voting (Dependability Cage) and within-perception cross-checks (Perception Simplex) |
| **B3** governed stack with no sustained silence | L1 | Consumes integrity information at the gate, relaxing Assumption 8 |
| **B4** recovery gated on trusted detection | L2 | Recovery in the persistent regime PID-Piper excludes |
| **B5** masking-robust detection statistic | L5, L6 | An **application** of sequential conformal change-point detection (Volkhonskiy et al. 2017), not a new method. Comparators: adaptive conformal inference; Martinez Gil et al. |

Paper 1 may say this motivates monitor-aware runtime assurance as future work. It may not claim any of
it.

---

## 7 · Before submission

| # | item | gates | effort |
|---|---|---|---|
| **new** | **Integrity-monitoring primary literature** — especially any use of protection levels in a safety or control decision | **N1**, and B1's positioning | a day |
| **new** | Forward citations of PID-Piper and Yang et al. 2021 | N3, B1 | hours |
| V1 | Assumption 8, SpecGuard threat model, survey §8, Zhao et al. assumptions — in the PDFs | N1, N2, N5 | hours |
| V2 | Targeted searches since 2024; any "to our knowledge" | all | a day |
| V3 | Both masking papers in full | N4 | hours + access |
| A2(c) | Adaptive conformal inference **and** Martinez Gil et al. on the shared protocol | N2 | ~90 min compute each |
| A3 | Matched classical controller | N4 | build + run |
| A4 | Disagreement signature across 30 seeds | N5 | ~90 min compute |
| A5 | Recovery-trigger analysis, all faults | N3 support | zero compute |
| — | Tatbul et al.; TaPR | N3 | hours |

---

## 8 · Draft contributions paragraph

Brackets must be resolved by §7 before submission.

> Navigation integrity monitoring detects when a position estimate is misleading, and runtime assurance
> for learned controllers guards the controller while assuming its gate receives nominal sensor data.
> The safety gate between them is not itself checked. We measure a gate that fails silently. Our
> contributions are:
>
> 1. **Faults that persist, evaluated.** Detect-and-recover work either excludes persistent sensor
>    manipulation or evaluates attacks lasting tens of seconds while assuming a working detector. For a
>    sensor dropout persisting for the rest of the mission, a residual gate comparing a learned
>    controller's output with a learned reference does not detect it, and its apparent detection of the
>    same fault when transient came from the recovery transient.
> 2. **Integrity failure at the gate.** Throughout a persistent sensor failure the gate reports no
>    hazard, while an integrity-style check on the sensor layer of the same stack detects the fault
>    within five ticks on every run, without false alarms.
> 3. **A guarantee without safety.** The gate meets its false-alarm specification on every run and
>    detects no persistent fault [, and adaptive conformal variants do / do not remedy this].
> 4. **Cross-layer disagreement.** Monitors of different layers are complementary, and their disagreement
>    carries the evidence the gate lacks [, systematically across seeds].
> 5. **Masking below baseline.** Extending closed-loop fault masking to a runtime-assurance gate under a
>    learned policy, the gate's alarm rate falls below its healthy baseline [, and this does / does not
>    occur under a matched classical controller].
> 6. **A released, pre-registered protocol** for evaluating runtime monitors for silent failure under
>    persistent faults.

---

## 9 · Wording traps

| do not write | because | write instead |
|---|---|---|
| "We propose ASTRA, a novel architecture" | architecture is prior art | "We use a runtime-assurance stack to measure…" |
| "We are the first to detect a wrong state estimate" | **integrity monitoring does this** | "at the safety gate, not the estimate" |
| "The gate exhibits hazardously misleading information" | HMI has a formal definition; no protection levels computed | "analogous to hazardously misleading information, at the gate" |
| "We introduce the notion of silent failure" | Zudaire et al. 2021; Or 2026 | "silent failure [Zudaire et al.; Or]" |
| "PID-Piper would fail under persistent faults" | PID-Piper was not run; only structurally similar | "in the regime PID-Piper's threat model excludes" |
| "We are the first to combine safety monitors" | Dependability Cage; Perception Simplex | "monitors of *different layers*, quantitatively" |
| "The first runtime failure prediction for monitors" | introspection exists for detectors | reserve B1 for Paper 2; cite Yang et al. |
| "Conformal prediction fails" | one configuration | "the conformal gate, as configured" |
| "Learned controllers cause masking" | A3 not done | "under a learned controller" |
| "The gate separates faulted from clean at AUC 0.998" | 0.998 is the sensor layer | "0.998 at the sensor, 0.737 at the gate's score" |
| "about 5 % false alarms" | measured 5.84 % | "5.84 % (median)" |
| "90 % fewer false alarms" | inverts the finding — the low rate is a miss | "the alarm rate falls below the healthy baseline" |
| "Integrity information is not used in decisions" | Lee, Seo & Kassas 2020 use protection levels in path planning | "not consumed online by a runtime-assurance gate" |
| "Nothing monitors the monitors" | HALO (liveness), conformal assurance monitors (confidence), CoCo (assumptions) | "nothing checks whether the gate can still *detect*" |
| "Prior work excludes persistent faults" | only PID-Piper excludes; DeLorean evaluates 15–30 s attacks | "excludes or does not evaluate faults persisting for the mission" |
| "The conformal guarantee holds on every run" | conformal guarantees are marginal | "the false-alarm rate stays within specification on every run" |
| "We are the first to aggregate faults across layers" | Orf et al. 2024 | "disagreement as evidence of blindness" |
