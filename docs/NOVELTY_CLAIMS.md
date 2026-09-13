# Novelty claims for the conference submission

**Prepared 13 September 2026** for Paper 1 (target IEEE ITSC; alternative IEEE ISSRE).
Derived from the literature gaps in `docs/LITERATURE_GAPS.md` and the evidence in
`docs/GAP_VERIFICATION.md`. Evidence is on branch `3.0`.

This document says **what may be claimed as new, against which prior work, on what evidence, and
with what wording** — and, just as importantly, what may not.

---

## 0 · Three rules before anything else

1. **Claim a contribution only against a named limitation of named prior work.** "Existing work does
   not…" must be followed by who, and where they say so.
2. **Do not write "first" or "novel" until V2 is done** (§6). Until then the wording is "to our
   knowledge", and even that only after the searches are logged.
3. **The architecture is not the contribution.** Simplex over neural controllers, conformal safety
   filters and learned digital twins all exist. ASTRA is the **instrument** that made the measurements
   possible. Presenting it as the novelty is the fastest route to rejection.

---

## 1 · The headline, in one sentence

> We show that runtime assurance for learned controllers rests on an assumption that fails
> measurably: a conformal monitor whose calibration is valid goes **quieter than its own healthy
> baseline** for as long as a sensor failure persists, while a check two layers upstream in the same
> stack detects the fault within five ticks — so the monitor's formal guarantee holds while its safety
> function does not, and the failure is architectural rather than statistical.

**Conditions on this sentence:** it holds for the stack, policy and severity measured (P1, `medium`,
one synthetic plant). "Architectural rather than statistical" needs A2(c) — see N2.

---

## 2 · Claims supportable in Paper 1

Each claim lists: the gap in prior work, what is new, the evidence, how confident the novelty is, and
what must be done before submission.

**Novelty confidence** is about the *literature*, not the data:
**High** — prior work checked says so of itself; **Medium** — prior work checked does not show it, but
targeted searches are incomplete; **Low** — plausibly already published.

---

### N1 — A measured counter-example to the "the monitor sees the true state" assumption

| | |
|---|---|
| **Gap in prior work** | Runtime assurance assumes its safety monitor's inputs are correct. **Synergistic Simplex** (Bansal … Hovakimyan, Sha; arXiv 2605.08190, 2026) states it as **Assumption 8 — no sensor failure**, declared out of scope. **Zhao et al.** (robust conformal STL verification, arXiv 2311.09482, 2024) assume perfect state observation. **Neural Simplex** (Phan et al., NFM 2020) does not evaluate sensor faults. **Ferrando & Malvone** (arXiv 2408.11627, 2024) identify the perfect-information assumption for runtime verification but address it for discrete temporal-logic monitors, not continuous control |
| **What is new** | A measurement, on a learned-controller runtime-assurance stack, of what happens when that assumption is broken by a sustained sensor fault: the monitor reading the fused estimate misses it completely, while evidence of the fault exists at the sensor layer |
| **Evidence** | Conformal gate detects sustained `imu_dropout` on **0 / 30** runs (E18-R3c, E21). A stream-health check detects it on **30 / 30**, **0 / 30** clean false positives, median latency **5 ticks** (E21). Pre-registered, paired seeds |
| **Novelty confidence** | **High** that the assumption exists and is made. **Medium** that no one has measured its failure this way — pending V2 |
| **Before submission** | V1 (confirm Assumption 8 in the PDF); V2; A1 independent reproduction from `3.0` |
| **Safe wording** | *"Recent runtime-assurance architectures explicitly assume nominal sensors [Synergistic Simplex, Assumption 8]. We measure the consequence of relaxing that assumption…"* |

---

### N2 — A satisfied guarantee coexisting with zero detection

| | |
|---|---|
| **Gap in prior work** | Conformal runtime methods guarantee **coverage** — equivalently, a bound on false alarms — under assumptions of open-loop prediction and correct observation (**Zhao et al.** 2024; **Strawn, Ayanian & Lindemann**, RA-L 2023, whose guarantee covers trajectory-prediction uncertainty with no sensor faults). A coverage guarantee is satisfied perfectly by a monitor that never fires. No checked work measures detection alongside a satisfied guarantee under closed-loop sensor failure |
| **What is new** | The two measured together: the monitor meets its false-alarm specification **and** detects nothing, under the conditions the guarantee's assumptions exclude |
| **Evidence** | Calibration in band `[2.5 %, 10 %]` on **30 / 30** runs at a 160 s window, clean false-alarm median **5.84 %** (E18-R3). Under sustained fault, alarm rate **≈ 0.2 %** in every post-onset phase and **0 / 30** detection (E18-R3c) |
| **Novelty confidence** | **Medium** |
| **Before submission** | **A2(c) — adaptive conformal inference on the same protocol.** Without it, this claim must be restricted to *split* conformal prediction, and a reviewer will ask why adaptive methods were not tried. A2(b) — confidence intervals on the discriminability–detection correlation |
| **Safe wording** | *"The monitor satisfies its false-alarm specification on every run and detects no sustained fault; the guarantee holds while the safety function fails."* Do **not** write "conformal prediction fails" |

---

### N3 — Apparent detection that does not transfer from faults that end to faults that persist

| | |
|---|---|
| **Gap in prior work** | Monitor evaluations in the checked literature measure detection on faults that end, or offline, and treat detection rates as properties of the monitor. **Guérin et al.** (arXiv 2208.14660, 2022) unify single-monitor metrics without closed-loop evaluation. The ML safety-monitoring survey (**Ferreira et al.**, arXiv 2412.06869) calls for system-level evaluation. Range-based and time-series metrics that account for post-anomaly periods have been reported (Tatbul et al.; TaPR) — **not yet verified first-hand** |
| **What is new** | A duration-matched control showing that the same fault, on the same seeds and threshold, is detected almost entirely by its **recovery transient**: the detection rate measured on a fault that ends does not transfer to one that persists |
| **Evidence** | Alarm rate in ticks 400–999: **99.06 %** when the fault ends at tick 399 (E18-R3b) against **0.18 %** when it never ends (E18-R3c). Identical 0.38 % during ticks 200–399 |
| **Novelty confidence** | **Medium** — the post-anomaly period is recognised in time-series evaluation; the transfer failure to persistent faults in runtime assurance is not shown in checked work |
| **Before submission** | Read Tatbul et al. and TaPR first-hand; cite them and state the distinction |
| **Safe wording** | *"Detection measured on transient faults overstates detection of persistent ones: in our measurement the apparent detection came from the recovery transient."* |

---

### N4 — Closed-loop masking that drives a calibrated monitor below its healthy baseline, under a learned controller

| | |
|---|---|
| **Gap in prior work** | Closed-loop fault masking is established — **Zhang, Yang, Dandago & Li** (Springer, 2026) with PID control; **Gómez-González, Fischer et al.** (Springer, doi 10.1007/978-3-032-29254-4_6) with adaptive PID/RLS and data-driven detectors on a two-tank plant. Both use **classical controllers** and neither, at abstract level, reports alarms falling **below** the healthy baseline or involves a runtime-assurance monitor |
| **What is new** | Masking under a **learned policy**, against a **calibrated conformal runtime-assurance monitor**, strong enough to push its alarm rate **below** its clean baseline — so silence becomes false evidence of health |
| **Evidence** | ≈ 0.2 % alarm rate under sustained fault against a 5.84 % clean median (E18-R3c); PPO policy |
| **Novelty confidence** | **Low to medium.** This is the claim most at risk |
| **Before submission** | **V3 — read both masking papers in full.** If either reports below-baseline alarms, N4 becomes an extension of a known result. **A3 — matched classical controller.** Without it, the claim must be *"under a learned controller"*, never *"caused by the learned controller"* |
| **Safe wording** | *"Consistent with closed-loop fault masking [Zhang et al.; Gómez-González et al.], and extending it to a conformal runtime-assurance monitor supervising a learned policy, the monitor's alarm rate falls below its healthy baseline."* **Always cite the masking work first** |

---

### N5 — The fault evidence is present in the stack and unused

| | |
|---|---|
| **Gap in prior work** | The ML safety-monitoring survey (**Ferreira et al.**, §8) lists **combining several safety monitors and verifying the consistency of their outputs** as an important open challenge. Recovery work such as **SpecGuard** (Dash, Chan & Pattabiraman, CCS 2024) declares detection out of scope and does not measure the detector it relies on. Budgeted monitor combination (**Hua et al.**, arXiv 2507.15886, 2025) combines scores in an AI code-review setting and does not treat disagreement as a signal |
| **What is new** | Evidence, on the whole monitoring surface of one stack, that monitors are **complementary** and that their **disagreement is informative**: the gate is blind where a sensor-layer check sees the fault, and vice versa. And that a detect-then-recover pipeline gated on the gate would not trigger on a persistent fault |
| **Evidence** | Health check catches `imu_dropout` (gate **0.00**); gate catches `lateral_noise` (health check **0.00**); union covers **4 of 6** faults against the gate's **3 of 6** (E21). Gate detection of 0 / 30 implies a pipeline gated on it triggers on 0 / 30 sustained dropouts; the full six-fault trigger analysis is **A5, not yet written** |
| **Novelty confidence** | **Medium** — the survey states the problem is open as of 2024; work since has not been searched |
| **Before submission** | V2; A5 (zero compute); A4 — show the disagreement signature holds across 30 seeds, not on single ticks |
| **Safe wording** | *"Addressing an open challenge identified in the safety-monitoring literature [Ferreira et al.], we show the monitors are complementary and that their disagreement carries the evidence the gate lacks."* Do **not** claim a fusion method — Paper 1 has none |

---

### N6 — An evaluation protocol for runtime monitors under persistent faults *(methodological)*

| | |
|---|---|
| **Gap in prior work** | No unified benchmark for safety monitors (**Ferreira et al.**, §8); single-monitor, offline metrics (**Guérin et al.**) |
| **What is new** | A protocol that exposes the failures above and is reusable: sustained versus transient injection with a duration-matched control; phase-resolved detection; a clean-arm false-positive bar alongside detection; the run as the unit of analysis; pre-registration with frozen thresholds and recorded withdrawals |
| **Evidence** | Applied across E17–E21 and Phase 2; pre-registration commits precede results (`ae997b3` before `4615cdc`; `db090f2` before `236330e`) |
| **Novelty confidence** | **Medium** as a protocol; the rigour itself is a strength reviewers reward in a negative-result paper |
| **Before submission** | Release the protocol and harness with the paper |
| **Safe wording** | *"We contribute a pre-registered evaluation protocol for runtime monitors under persistent faults, and release it."* |

---

## 3 · Claims ranked for the submission

| rank | claim | evidence | novelty | ready? |
|---|---|---|---|---|
| 1 | **N1** assumption fails, measured | strong | high / medium | after V1, V2, A1 |
| 2 | **N2** guarantee holds, detection zero | strong | medium | **after A2(c)** |
| 3 | **N5** evidence present and unused | strong | medium | after V2, A4, A5 |
| 4 | **N3** transient detection doesn't transfer | strong | medium | after reading TaPR / Tatbul |
| 5 | **N6** evaluation protocol | strong | medium | when released |
| 6 | **N4** below-baseline masking, learned controller | strong | **low–medium** | **after V3 and A3** |

**Lead with N1 and N2.** They rest on assumptions prior work states about itself, which is the hardest
kind of gap to dispute. **N4 is the most interesting and the most exposed** — keep it, but frame it as
an extension of the masking literature, not a discovery.

---

## 4 · Not novel — cite, do not claim

| topic | prior work | evidence read |
|---|---|---|
| Simplex runtime assurance over neural controllers | Phan et al., *Neural Simplex Architecture*, NFM 2020 | abstract |
| Conformal prediction as a safety filter for RL | Strawn, Ayanian & Lindemann, RA-L 2023 | abstract |
| Closed-loop fault masking | Zhang et al., Springer 2026; Gómez-González, Fischer et al., Springer | abstract |
| Offline metrics not predicting deployed reliability (general form) | Rashidi, arXiv 2606.29506, 2026 | full text |
| Recovery from sensor attacks | Dash, Chan & Pattabiraman, SpecGuard, CCS 2024 | full text |
| Semantic anomaly detection | Elhafsi, Sinha, Agia, Schmerling, Nesnas & Pavone, 2023 | abstract |
| Secure state estimation under sensor attack | Fawzi/Tabuada; Pasqualetti et al. | **not yet read** |

---

## 5 · Not claimable in Paper 1 — reserved for Paper 2

These are the likely strongest novelties of the programme and **must not appear as contributions in
Paper 1**, because none is built. They may appear only as future work.

| future claim | closes | objective |
|---|---|---|
| Runtime detection that a monitor has gone blind | L4 | B1 — the core of Paper 2 |
| Consistency-based monitor fusion | L3 | B2 |
| Governed stack with no sustained silence | L1 | B3 |
| Recovery gated on trusted detection, with isolation | L2 | B4 |
| Masking-robust detection statistic | L5, L6 | B5 |

Saying in Paper 1 that *"this motivates monitor-aware runtime assurance, which we pursue in future
work"* is fine and strengthens the paper. Claiming any of it is not.

---

## 6 · Must be done before these claims go into a submission

| # | item | gates | effort |
|---|---|---|---|
| V1 | Confirm Assumption 8, SpecGuard's threat model, survey §8, Zhao et al.'s assumptions in the PDFs | N1, N2, N5 | hours |
| V2 | Targeted searches since 2024: monitor blindness, cross-monitor consistency, detector health monitoring; papers citing Synergistic Simplex, SpecGuard, Ferreira et al. | N1, N5 — and any use of "to our knowledge" | a day |
| V3 | Full text of both masking papers | **N4** | hours, plus access |
| A2(c) | Adaptive conformal inference on the shared protocol | **N2** generality | ~90 min compute |
| A3 | Matched classical controller | **N4** attribution | build + run |
| A4 | Blindness signature across 30 seeds | N5 | ~90 min compute |
| A5 | Recovery-trigger analysis, all six faults | N5 | zero compute |
| — | Read Tatbul et al. and TaPR | N3 | hours |

---

## 7 · Draft contributions paragraph

For the introduction. **Conditional wording in brackets** must be resolved by §6 before submission.

> Runtime assurance for learned controllers is typically evaluated by its false-alarm guarantee and
> offline separability, and recent architectures explicitly assume nominal sensors. We measure what
> happens when that assumption fails. Our contributions are:
>
> 1. **A measured counter-example to the nominal-sensor assumption.** On a runtime-assurance stack
>    supervising a learned controller, a conformal monitor misses a sustained sensor failure on every
>    run, while a stream-health check in the same stack detects it on every run within five ticks,
>    without false alarms.
> 2. **A satisfied guarantee without safety.** The monitor meets its false-alarm specification on every
>    run and detects no sustained fault [— and adaptive conformal inference does / does not remedy
>    this].
> 3. **Detection that does not transfer.** Apparent detection of a transient fault arises from its
>    recovery transient, and vanishes when the fault persists.
> 4. **Masking below baseline.** Extending closed-loop fault masking to a conformal monitor supervising
>    a learned policy, the monitor's alarm rate falls below its healthy baseline [, and this does / does
>    not occur under a matched classical controller].
> 5. **Unused evidence.** The stack's monitors are complementary and their disagreement carries the
>    evidence the gate lacks — an open challenge in the safety-monitoring literature.
> 6. **A pre-registered evaluation protocol** for runtime monitors under persistent faults, released
>    with the paper.

---

## 8 · Wording traps

| do not write | because | write instead |
|---|---|---|
| "We propose ASTRA, a novel architecture" | the architecture is prior art | "We use a runtime-assurance stack to measure…" |
| "Conformal prediction fails" | one configuration, one plant | "The conformal monitor, as configured, …" |
| "The monitor separates faulted from clean at AUC 0.998" | **0.998 is the sensor layer**; the monitor's score is **0.737** | "separable at the sensor (0.998) and at the monitor's score (0.737)" |
| "about 5 % false alarms" | the measured median is **5.84 %** | "5.84 % (median; 4.66–8.22 %)" |
| "We are the first to…" | V2 not done | "To our knowledge…" — only after V2 |
| "Learned controllers cause masking" | A3 not done | "under a learned controller" |
| "We reduce false alarms by 90 %" | inverts the finding: the low rate is a **miss**, not an improvement | "the alarm rate falls below the healthy baseline" |
