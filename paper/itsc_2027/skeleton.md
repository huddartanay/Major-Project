# Paper 1 skeleton — IEEE ITSC 2027 submission

**Draft target:** IEEE ITSC 2027, deadline **1 March 2027**, 6-8 pages.
**Working title:** *Silent Safety Gates in Autonomous Vehicles: A Label-Free
Monitor for Detecting Runtime Blindness under Sensor Faults.*

This file is a **skeleton**, not a manuscript. It fixes the structure, the
main claims, the figure list, and points every claim at the evidence file
that has to survive review. It is committed so any change to the story
leaves a trace, per handoff §14 working practice.

Owner: Tanay Huddar. Co-authors: Sushanth C (per handoff §0.6, author order
still to be decided when Sushanth is back); institutional affiliation and
guide (Dr. Chaitra R.) TBD.

---

## Abstract (~200 words, drafted late)

Placeholder. Fill from §7 "one-sentence claim" once every claim in §5 has a
green tick.

## 1 · Introduction

**Hook.** A single motivating figure: the plant's true state diverges from
its reference (up to 60 % more lateral offset, speed decayed to 0 m/s)
while every gate in the assurance stack reports NOMINAL, for the full
duration of a sustained IMU dropout. Same run, two axes.

**Contribution list.**
1. First systematic characterisation of L6 conformal gate silence under
   sustained sensor faults (**G1**): the median non-conformity score
   moves 0.3 % while the alarm rate collapses 38× — a threshold-crossing
   effect on a distribution held constant by the estimator, not a
   variance-inflation effect as one might expect.
2. **G2 · GateBlindnessMonitor:** the first label-free monitor of gate
   blindness built on the L1-vs-L6 comparison. Matches L1's detection on
   `imu_dropout` with zero clean false alarms; correctly restricts to
   the *gate-blindness* subset of L1-detected events; beats KS(conf) on
   clean false-alarm rate (0.000 vs 0.733).
3. **Held-out evidence** on `20261201+i` for the G1 story (E21 L1 30/30
   / 5-tick / 0-FP replicates dev exactly; Stage A mechanism ratios
   replicate bit-identically).

**Non-goals.** Adversarial faults (G5), semantic errors (G6),
re-certification after a monitor was blind (G4). Explicit list of
things the paper does **not** claim, per handoff §3.

## 2 · Related Work

The 20-paper landscape from `docs/LESSONS_FROM_20_PAPERS.md` and
`docs/NOVELTY_REVERIFICATION.md`. Structured around three shelves:

- Conformal monitors and their calibration (Lindemann; Cleaveland 2023
  and 2025; Peper 2025; Mao 2025; Volkhonskiy et al.).
- Runtime monitor validity (CoCo; HALO; Lukina et al.; Antonante et al.).
- Label-free distribution shift (KS(conf) — Sun & Lampert 1804.04171;
  Amoukou et al. 2412.12910; D3M 2506.05047; ModelGuard 2104.15006).

Positioning: G1 is a *specific mode of monitor failure* not called out in
any of the above. G2 is the *first application* of a label-free shift
detector at the interface between two safety layers rather than within one.

## 3 · System Under Study

Nine-layer pipeline (L1 sensing → L9 arbitration), specifically the L6
conformal gate. Frozen threshold `P1 = 3.7024`, calibrated per
`experiments/phase5_od8_h7/E18_R3/final_decision.md`. Six sustained faults
injected at the sensor boundary from tick 200 through the run's end.

Reference figure: Fig. 1, one-page pipeline diagram with the L1 stream-
health path and the L6 gate path highlighted.

## 4 · Method

### 4.1 The mechanism experiment (G1)

Pre-registration: `experiments/phase5_od8_h7/STEP1_MECHANISM/preregistration.md`.
Three hypotheses (σ inflation, departure collapse, threshold drift) with
pre-committed ratio bounds. Verdict: **H-none** on both dev and held-out.
Sharpened mechanism (Stage A `observations.md`): L6-visible signals held
within 1 % of clean baseline; alarm suppression is a tail effect on a
distribution pinned near the threshold.

### 4.2 The G2 monitor

Pre-registration: `experiments/phase5_od8_h7/STEP3_G2_MONITOR/preregistration.md`.
`GateBlindnessMonitor` fires when L1 stream health is unhealthy AND the L6
gate is not alarming for `patience = 5` consecutive ticks. Rationale: no
L6-internal signal moves under fault, so the comparison must span layers.

### 4.3 Baselines

`L1OnlyMonitor` (E21 `health` reused); `KSConfMonitor` (Sun & Lampert);
`ConformalMartingaleMonitor` (Volkhonskiy et al.); `OracleMonitor` (ceiling,
reads ground truth). Amoukou et al. and D3M explicitly deferred; noted as
a limitation.

## 5 · Results

Each subsection ends with **▸ file:** pointing at the committed evidence.

### 5.1 The gate is silent under sustained sensor faults (G1)

- Under sustained `imu_dropout` the alarm rate is **0.13 %** vs **5.00 %**
  clean (30 dev seeds; held-out identical).
  ▸ file: `experiments/phase5_od8_h7/E18_R3c/final_decision.md`; replicated
  ▸ in `STEP1_MECHANISM/processed_results/{final_decision_dev.md,final_decision_heldout.md}`.
- The suppression is a **38× tail effect** on a distribution whose median
  moves only 0.3 %; σ, departure and quantile are all pinned at 1.00 ×
  clean.
  ▸ file: `STEP1_MECHANISM/processed_results/observations.md`.

### 5.2 An independent layer sees the same fault at once

E21 L1: **30/30 detection, 5-tick median latency, 0/30 clean FP** on both
dev and held-out.
▸ file: `experiments/phase5_od8_h7/E21_BASELINE_COMPARISON/final_decision.md`;
held-out: `STEP1_MECHANISM/processed_results/e21_l1_heldout.json`.

### 5.3 The proposed monitor flags gate blindness with the same latency
    and zero clean false alarms

`GateBlindnessMonitor` on `imu_dropout` medium: **1.000 detection, 5-tick
latency, 0.000 clean FP** (dev). Same shape on other L6-blind cells; correctly
suppressed to 29/30 on `position_bias medium` where L6 does react on the
missing run.
▸ file: `STEP3_G2_MONITOR/processed_results/final_decision_dev.md`.

### 5.4 Label-free baselines either false-alarm on clean or share the
    architectural blindness

- KS(conf) clean FP **0.733** at the pre-registered alpha with the naive
  sequential correction (fixable engineering; see `observations.md`).
- Conformal martingale correctly detects `lateral_noise`, `position_bias`
  and `position_drift`, and correctly reports the score stream is exchangeable
  under `imu_dropout` / `speed_bias` / `speed_stuck` — i.e. blind for the
  same architectural reason L6 is.
  ▸ file: `STEP3_G2_MONITOR/processed_results/{final_decision_dev.md,observations.md}`.

### 5.5 (Stage C1 → C1b) The L1-vs-gate quadrant restricts G2's regime

Stage C1's sweep across four value-corruption faults produced
**WALK_AWAY_OR_SHIFT** per its pre-committed rule (`STEP2_MAGNITUDE_
SWEEP/preregistration.md §5`): cell A empty on 3 of 3 completed faults
(position_bias, position_drift, speed_bias) at every tested magnitude
(subthreshold, low, mid_low, medium, high). Position faults trigger
BOTH L1 and L6 correctly (cell B); speed faults trigger NEITHER at
any magnitude (cell D).
▸ file: `STEP2_MAGNITUDE_SWEEP/processed_results/{final_decision_dev.md,observations.md}`.

The pre-committed shift branch was taken. Stage C1b (`STEP5_SENSOR_
LOSS_SWEEP`) then swept graded IMU dropout at four probabilities on
30 dev seeds. Verdict per pre-registration §5: **NARROW**. Cell A
populated only at p = 1.00 (total loss); at partial dropouts the
estimator's uncertainty is high enough that L6's non-conformity score
crosses threshold and L6 does its job.

| dropout p | L1 (of 30) | gate alarm rate (400-3399) | cell |
|---|---:|---:|---|
| 0.25 | 12 | 0.133 | D |
| 0.50 | 30 | 0.494 | B (both react) |
| 0.75 | 30 | 1.000 | B (both react) |
| **1.00** | **30** | **0.0002** | **A (gate silent)** |

▸ file: `STEP5_SENSOR_LOSS_SWEEP/processed_results/final_decision_dev.md`.

The paper's compelling case is therefore total sensor loss. `speed_stuck`
in Stage A shows the analogous invariant-inputs pattern, so the
architectural claim generalises across sensor-loss modes.

### 5.6 (Stage C3) Outcome experiment: with vs without the monitor

Two-part result on the offline lower-bound counterfactual (full L8
wired counterfactual is scoped to Stage D).

**Pre-committed primary at medium magnitude / p = 1.00** (per
`STEP4_OUTCOME_EXPERIMENT/preregistration.md §3`): CF speed-up **0
ticks** because L1's integrity counter already drives L8 escalation
at tick 205, the same tick G2 fires. Fallback case (2): monitor is
**safe to add** (zero clean false alarms) with **null outcome benefit
at total dropout**.

**Held below the primary verdict, reported in the discussion.** At
partial dropouts G2's L1-vs-L6 comparison catches situations L8's
integrity counter takes much longer to escalate on:

| dropout p | median escalation tick | G2 fire tick | CF speed-up (lb) |
|---|---:|---:|---:|
| 0.25 | 2128 | 412 | **1640 ticks (~82 s)** |
| 0.50 | 314 | 227 | 71 ticks (~3.5 s) |
| 0.75 | 212 | 210 | 0 |
| 1.00 | 205 | 205 | 0 |

The 1,640-tick lower-bound at p = 0.25 is the paper's headline outcome
number. It says: when the fault is subtle enough that L1's sustained-
fire criterion accumulates slowly, the cross-layer comparison catches
the situation an order of magnitude earlier. Reported as evidence for
Stage D and future work.

▸ file: `STEP4_OUTCOME_EXPERIMENT/processed_results/{final_decision_dev.md,observations.md}`.

### 5.7 Held-out replication (§0.3)

Every headline number is now held-out-confirmed on the frozen seed set
`20261201 + i`:

| result | dev | held-out |
|---|---|---|
| L6 alarm rate under sustained `imu_dropout` | 0.13 % | 0.00 % |
| E21 L1 detection (30/30) | latency 5 ticks | 5 ticks |
| E21 L1 clean FP | 0/30 | 0/30 |
| Stage A σ / departure / quantile ratios | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| Stage C1b p=1.00 cell A gate alarm rate | 0.02 % | 0.00 % |
| C2 gate_blindness detection @ imu_dropout medium | 1.000 / 5t / 0 FP | 1.000 / 5t / 0 FP |
| C3 CF speed-up @ p=0.25 partial dropout | 1640 ticks | 1181 ticks |
| C3 CF speed-up @ p=0.50 partial dropout | 71 ticks | 47.5 ticks |

▸ files: `STEP1_MECHANISM/processed_results/*_heldout.*`,
`STEP5_SENSOR_LOSS_SWEEP/processed_results/final_decision_heldout.md`,
`STEP3_G2_MONITOR/processed_results_heldout/*`,
`STEP4_OUTCOME_EXPERIMENT/processed_results_heldout/*`.

## 6 · Discussion

- **Why the mechanism experiment was worth running even though the
  verdict was H-none.** Pre-registration prevented an over-strong claim
  about σ inflation and produced a sharper story (tail contraction on
  a distribution held constant by upstream absorption).
- **Why G2 cannot beat L1 on raw detection rate — and why that is not
  a limitation.** G2's semantic contribution is the classification of an
  L1 event as "gate blindness" vs "gate reacting". Downstream (L8) can
  now condition on that distinction.
- **The Stage C1 → C1b path.** Pre-committed to WALK_AWAY_OR_SHIFT, we
  took the shift branch: the parameterised value-corruption faults are
  handled by L6 as designed (cell B), so G2's compelling regime is
  sensor loss. C1b's NARROW verdict pins that to total loss for the
  primary result while the graded-severity outcome numbers extend the
  discussion.
- **Partial-dropout outcome is where G2 delivers the biggest number.**
  Not a pre-committed pass criterion, but the 1,640-tick lower-bound
  speed-up at p = 0.25 is the strongest single-number result the paper
  produces. Framed as evidence for Stage D and future work rather than
  as the paper's headline.
- **Limitations.** Full L8 wired counterfactual awaits the abstention
  ADR (Stage D). No adversarial faults; no cross-controller
  replication. Amoukou et al. and D3M baselines deferred to follow-up.

## 7 · One-sentence claim

*Under total IMU loss, the L6 conformal gate goes silent because
everything it reads is held constant while the plant diverges (dev
and held-out); a label-free monitor comparing L1 stream health with
L6 alarms flags this blindness with zero clean false alarms at the
same 5-tick latency L1 achieves alone, and — at graded partial-dropout
severities that L8's own integrity path takes far longer to escalate
on — would bring escalation forward by 1,181 - 1,640 ticks (~59 - 82 s)
under the pre-registered lower-bound counterfactual, on both dev and
held-out seeds.*

## 8 · Figure list (numbers to be finalised)

1. Motivating figure: plant true state vs L6 alarms, one run, tick axis.
2. Pipeline diagram (Fig. 1 in §3).
3. Alarm-rate cumulative distribution: clean vs faulted, overlaid.
4. Mechanism ratio panels (σ, departure, quantile, true err) by phase,
   dev and held-out side-by-side.
5. L1-vs-gate quadrant heatmap (from Stage C1 when it lands).
6. Monitor comparison table (from Stage C2).
7. Outcome plot: time in NOMINAL, with / without G2 (from Stage C3).

## 9 · Todo before submission

- [x] Stage C1 sweep complete (WALK_AWAY_OR_SHIFT) + shift branch executed.
- [x] Stage C1b sensor-loss sweep dev (NARROW at p=1.00).
- [x] Stage C1b sensor-loss sweep held-out (NARROW replicates).
- [x] Stage C2 monitor + baselines dev + held-out (PASS both).
- [x] Stage C3 outcome dev + held-out: primary case (2) + partial-
      dropout 1181-1640-tick speed-up as observation.
- [x] Held-out G1 core (R3c + E21 L1) re-confirmed (§0.3).
- [x] CI (stage-0): ruff format, ruff check, mypy, import-linter,
      3074 tests all green after the pyproject.toml ignore expansion
      and mypy per-module overrides.
- [ ] Full L8 wired counterfactual (Stage D): needs ADR for G2 →
      L6 abstention path.
- [ ] Amoukou et al. and D3M baseline implementations (§4.3 defer).
- [ ] KS(conf) sequential correction patch (fixable engineering).
- [ ] Author order and affiliation.
- [ ] Licence update (LICENSE / NOTICE / README) once §0.6 licence choice
      is made (handoff §14).
- [ ] Rebase every stacked branch (#2-#10) onto the new stage-0 tip
      so downstream PRs inherit the CI fixes.
