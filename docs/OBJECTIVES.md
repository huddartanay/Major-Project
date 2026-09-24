# ASTRA — Objectives

**Revised 13 September 2026 — gap-driven.** Supersedes the version at `93648b7`, which organised
objectives around ASTRA's own shortfalls. This version organises them around the **limitations of
existing published work** recorded in `docs/LITERATURE_GAPS.md` (gaps L1–L6), so that every objective
exists to close a gap someone else's work leaves open. A mapping from the old numbering is in §9.

Evidence referred to is on branch `3.0`; see `docs/GAP_VERIFICATION.md`.

---

## 0 · Corrections carried forward

1. **SAFECOMP is not IEEE** (Springer LNCS). IEEE candidates: ITSC, ISSRE, DSN.
2. **comma2k19 replay is open-loop**, so closed-loop masking cannot occur in it. External validation
   there tests sensor- and estimator-level evidence only.
3. **The placeholder policy is not a classical-controller baseline.** `KinematicPlaceholderPolicy`
   holds speed and centres steering and does not read lateral position, so it cannot compensate a
   position fault. Any learned-versus-classical comparison needs a matched controller (see A3).

---

## 1 · The direction

> **Monitor-aware runtime assurance.** An architecture that does not assume its monitors see the
> truth. It measures at runtime whether each monitor can currently detect faults, using consistency
> between layers as the evidence; it routes decisions away from monitors that have gone blind; and it
> triggers fault-specific recovery only on detections it has reason to trust.

Existing runtime assurance asks *"is the action safe?"* ASTRA adds the question it does not ask:
**"can my monitor currently see?"**

| gap in existing work | Paper 1 establishes | Paper 2 closes |
|---|---|---|
| **L1** Runtime assurance assumes the monitor sees the true state | A1 | B3 |
| **L2** Recovery assumes detection is solved | A5 | B4 |
| **L3** Combining monitors and checking consistency is open | A6 | B2 |
| **L4** Nothing tells a monitor it has gone blind | A4 | **B1 — the core contribution** |
| **L5** Conformal guarantees bound false alarms, not missed detection | A2 | B5 |
| **L6** Masking studied only under classical control | A3 | B5 |

---

## 2 · Rules every objective is held to

1. **Pre-registered before any run.** Design, metric and decision rule committed first.
2. **The run is the unit.** Ticks are never samples.
3. **Development and evaluation seeds are separate.** Seeds `20260731 + i`, `i < 30`, are
   *development* — already seen by E17–E21. Every Paper 2 method is tuned on those and evaluated on a
   **held-out block `20261201 + i`, `i < 30`**, with every threshold frozen before the held-out runs
   are touched.
4. **No algebraic path from method to metric.** Checked explicitly, after Phase 2's identity confound.
5. **Runtime methods may not read ground truth.** Nothing deployed may use the injected-fault identity,
   the injector's state, or simulator truth (`truth_y`, `truth_speed`). Ground truth is used only to
   *score*.
6. **Confidence intervals on every headline number.**
7. **No novelty claim before V1 and V2** (§3).
8. **Every result updates the claim ledger**, including failures.

### The shared protocol

Unless stated otherwise every objective is scored on the E21 design: policy P1; six fault classes at
`medium` severity; **sustained** injection opening at tick 200 and never closing; 3,400 ticks; 30
faulted runs per class and a 30-run clean arm.

- **Detection** — the run's monitor fires at any point after onset.
- **Clean false positive** — the monitor fires at all on a clean run.
- **Bars** — detection ≥ 0.90 and clean false positive ≤ 0.10.

### Definition used by A4 and B1

A monitor is **blind** to a fault over a window when the fault is active for the whole window and the
monitor's alarm rate in that window is at or below its own clean median false-alarm rate. Windows are
200 ticks. This is a **scoring label**, computed from ground truth offline; it is never available to a
runtime method.

---

## 3 · Literature verification — gates on every claim

| # | Objective | Done when |
|---|---|---|
| **V1** | Confirm the evidence for L1–L6 in the PDFs | Synergistic Simplex Assumption 8, SpecGuard's threat model, the monitoring survey's §8, and Zhao et al.'s assumptions each confirmed first-hand, with page numbers recorded |
| **V2** | Confirm L3 and L4 are unclaimed since 2024 | Targeted searches run and logged for runtime detection of monitor blindness or degradation, cross-monitor consistency checking, detector health monitoring and monitor self-assessment; papers citing Synergistic Simplex, SpecGuard and the Ferreira survey checked. **Gates any novelty claim for B1 and B2** |
| **V3** | Read both closed-loop masking papers in full | Full text of Gómez-González et al. and Zhang et al. read; venue and year of the former confirmed; recorded whether either reports alarms falling below baseline. **Gates A3's framing** |

---

## 4 · Paper 1 — establish that the gaps are real

**Thesis.** The assumptions behind runtime assurance fail in a measurable way: a calibrated monitor
reading the fused estimate goes quieter than its healthy baseline for as long as a sensor failure
persists, while another layer of the same stack sees the fault — and nothing in the architecture
consumes that disagreement.

| # | Gap | Objective | Done when | Status |
|---|---|---|---|---|
| **A1** | L1 | **The monitor does not see the true state** | Shown on the shared protocol that a monitor reading the fused estimate misses a sustained sensor fault that sensor-level evidence catches; **independently reproduced from branch `3.0`** | Measured: gate 0/30, health 30/30 (R3c, E21). **Awaiting push and independent reproduction** |
| **A2** | L5 | **A satisfied conformal guarantee coexists with zero detection — and not only for vanilla split-conformal** | (a) Calibration in band on 30/30 runs alongside 0/30 detection — *met*. (b) Bootstrap CIs and a per-fault breakdown for the discriminability–detection correlation. (c) **Adaptive conformal inference** run on the shared protocol at ε = 0.05; outcome recorded either way — if ACI also misses sustained `imu_dropout`, the failure is architectural; if it catches it, the claim narrows to split-conformal | (a) met; (b), (c) not started |
| **A3** | L6 | **Masking under a learned policy — is it the policy?** | A **matched classical controller** — lateral and speed feedback reading the same estimated state the learned policy reads — run on the same faults and seeds. Recorded whether it also drives the gate below its clean baseline. *Same outcome:* the finding is about runtime-assurance monitors under closed-loop control. *Learned policy only:* the finding is specific to learned controllers | Not started. **Requires building the matched controller** |
| **A4** | L4 | **The blindness signature is systematic** | Pre-registered, 30 seeds: the fraction of post-onset ticks in which L1 or L3 reports degradation **while** L6 is not alarming, against the same fraction on clean runs, with CIs, for every fault class. Supports L4 when, under sustained `imu_dropout`, the signature holds on ≥ 90 % of post-onset ticks and ≤ 10 % of clean ticks | Observed on single ticks only |
| **A5** | L2 | **A recovery pipeline gated on this monitor would never trigger** | For all six faults: the fraction of runs in which a detect-then-recover pipeline gated on the gate would trigger, and the trigger-latency distribution — from recorded detections, with the health check for comparison | Derivable from R3c and E21; not written up |
| **A6** | L3 | **Monitors are complementary; their disagreement carries information** | Coverage of each monitor and of their union on the shared protocol | **Met**: health catches `imu_dropout` (gate 0.00), gate catches `lateral_noise` (health 0.00); union 4/6 against the gate's 3/6 (E21) |
| **A7** | L1 | **Sensor-level evidence holds on real sensor noise** | comma2k19 acquired and split frozen; the cross-check and L1 evidence of A1 reproduced on real logs with injected faults; first `[M-ext]` row; the open-loop limitation stated | Not started. The long pole |
| **A8** | — | **Paper written and submitted** | Every claim maps to a ledger row and a table; every number re-measured from `3.0`; prior art cited (Simplex, conformal safety filters, masking); zero open P0; submitted to the chosen venue | Not started |

**Out of scope for Paper 1:** proposing a fix beyond A6's indicative union, adversarial sensors,
semantic errors, recovery, CARLA, P2 and P3, severities other than `medium`.

---

## 5 · Paper 2 — ASTRA 2.0 closes the gaps

Every B-objective is tuned on development seeds and scored on the held-out block.

### B1 — Runtime blind-monitor detection *(closes L4 — the core contribution)*

A runtime estimator that flags when a given monitor has lost the ability to detect, from
cross-layer consistency, without reading ground truth.

**Done when, on held-out seeds:**
- it flags ground-truth blindness of the conformal gate under sustained `imu_dropout` in **≥ 27 / 30**
  runs, within **20 ticks (1 s)** of the blindness window opening;
- it raises a false blindness flag on **≤ 3 / 30** clean runs;
- **leave-one-fault-out:** tuned without a given fault class, it still flags blindness for that class
  in ≥ 0.80 of runs — for every class where some other layer carries evidence;
- it beats two naive baselines: using the raw L1 health flag as a blindness proxy, and counting
  disagreeing monitors.

**Stated limit.** Consistency-based blindness detection can only flag blindness where *some* layer
still sees the fault. Today no monitor sees `speed_bias` or `speed_stuck`, so B1 cannot flag the gate's
blindness to them. That is closed by B3's coverage requirement, not by B1.

### B2 — Consistency-based monitor fusion *(closes L3)*

A principled way to combine monitors that uses their agreement and disagreement, not just their
scores.

**Done when, on held-out seeds:**
- the fused decision reaches detection ≥ 0.90 on **every fault class that at least one member monitor
  detects**, at clean false positive ≤ 0.10;
- it achieves a lower false-positive rate than the OR-union of its members;
- it achieves higher detection, at matched false-positive rate, than majority vote and than
  likelihood-ratio score combination of the kind used for budgeted monitor ensembles.

### B3 — No sustained silence *(closes L1)*

The governed stack does not assume its monitors see the truth: decisions are routed away from monitors
B1 flags as blind, and every sensor channel is observed by at least one monitor.

**Done when, on held-out seeds:**
- for **every** sustained fault class, the governed stack's alarm rate during the fault is **never
  below** its clean false-alarm rate;
- **all six** fault classes are detected at ≥ 0.90 with clean false positive ≤ 0.10 — which requires a
  monitor that observes the speed channel;
- an ablation with blind-monitor routing **disabled** — the "no sensor failure" assumption of existing
  runtime assurance, in force — reproduces the sustained silence, and with routing **enabled** it does
  not.

### B4 — Recovery gated on trusted detection *(closes L2)*

Fault isolation first, then recovery that acts on the specific faulty channel.

**Done when, on held-out seeds:**
- the faulty channel is correctly isolated in ≥ 0.90 of runs;
- recovery triggers in ≥ 0.90 of sustained-fault runs;
- after recovery the vehicle returns to NOMINAL, and its mean absolute lateral deviation is lower than
  under the graduated fallback (NOMINAL → DEGRADED → LIMP → HALT), by a paired Wilcoxon test across
  30 seeds at p < 0.05;
- it outperforms the **same recovery gated on the conformal gate alone** — the detect-then-recover
  structure of existing work — which A5 predicts will rarely trigger.

### B5 — Detection that survives masking *(closes L5 and L6)*

Show that the statistic itself — not only the plumbing — can be made robust to masking.

**Done when, on held-out seeds:**
- a detector operating on the L6 score **without access to L1 health** detects sustained
  `imu_dropout` at ≥ 0.90 with clean false positive ≤ 0.10, by responding to changes in spread and to
  persistence rather than to level alone;
- a dispersion-augmented monitorability metric, **pre-registered fresh**, predicts detection at
  identity-free ρ ≥ 0.70;
- the monitor reports an estimate of its detection power per fault class alongside its coverage
  guarantee.

---

## 6 · Beyond Paper 2

| # | Gap it extends | Objective | Precondition |
|---|---|---|---|
| **B6** | L1, L4 under attack | A strategic attacker that deliberately exploits the masking channel is detected or tolerated; compared against secure-estimation baselines, with prior art conceded | B1–B4 met |
| — | semantic anomalies | **Not targeted.** An established field. ASTRA's only possible contribution is routing semantic evidence through B1's blindness mechanism, and that is not yet shown to be a gap | V2 extended to semantic monitors |

---

## 7 · Venue

Deadlines must be taken from each official call for papers.

| venue | fit |
|---|---|
| **IEEE ITSC** — recommended for Paper 1 | Vehicle framing; most tolerant of simulation-based evaluation |
| **IEEE ISSRE** — alternative | Runtime-monitor failure analysis and measurement methodology in scope |
| **IEEE/IFIP DSN** | Hold until external validation is stronger than replay-only |

---

## 8 · Order of work

```
push 3.0 ─► A1 reproduced ─┐
V1, V3 ────────────────────┤
A2(b) CIs  ─ zero compute ─┤
A5         ─ zero compute ─┤
A2(c) ACI  ─ ~90 min ──────┼─► A8 ─► submit (Paper 1)
A4         ─ ~90 min ──────┤
A3 build controller, run ──┤
A7 comma2k19 ── long pole ─┘   (start first)

V2 ─┐
    ├─► B1 ─► B2 ─► B3 ─► B4        (Paper 2)
A4 ─┘      B5 alongside B1
```

**Zero-compute items first** (A2b, A5), then the ~90-minute pre-registered runs (A2c, A4). **A7 starts
immediately** because it is the longest. **V2 before B1**, because B1 is the claimed contribution.

---

## 9 · Decisions that are yours

1. **Venue** — ITSC or ISSRE.
2. **Push `3.0` to the team remote** — A1 cannot complete without it.
3. **Build the matched classical controller for A3** — adds a benchmark controller; without it L6 can be
   evidenced but not attributed to the learned policy.
4. **Whether Paper 1 needs a second policy** — P1 only is honest but narrow.

### Mapping from the previous numbering (`93648b7`)

| old | new |
|---|---|
| O1 make verifiable | A1 (+ A2b) |
| O2 confirm unpublished | V1, V2, V3 |
| O3 adaptive conformal | A2c |
| O4 external validation | A7 |
| O5 indicative remedy | A6 |
| O6, O7 rewrite and submit | A8 |
| S1 cross-layer fusion | B2 |
| S2 self-trust | **B1** |
| S3 channel coverage | B3 |
| S4 persistence and spread | B5 |
| S5 isolation and response | B4 |
| S6 adversarial | B6 |
| S7 semantic | not targeted |
| — | **A3, A4, A5 are new**: they establish L6, L4 and L2 directly |
