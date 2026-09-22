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

### 5.5 (Stage C1) L1-vs-gate quadrant table

**Pending Stage C1 sweep completion (~60 min at time of writing).** The
pre-committed rule (`STEP2_MAGNITUDE_SWEEP/preregistration.md §5`)
decides whether cell A is non-empty for ≥ 2 faults. Table goes here on
completion; the paper's paragraph adapts to whichever cell counts hold.

### 5.6 (Stage C3) Outcome experiment: with vs without the monitor

Time in NOMINAL under fault; time to reach DEGRADED / LIMP; needless
escalation on clean runs. This experiment is scaffolded but not yet run;
it requires wiring the G2 monitor to L8 via the abstention path (ADR to
be written under `docs/adr/`).
▸ file: `STEP4_OUTCOME_EXPERIMENT/` (pending).

### 5.7 Held-out replication (§0.3)

All of the above numbers on the frozen held-out seed set (`20261201+i`).
Stage A held-out is landed and identical to dev; E21 L1 identical.
▸ files: `STEP1_MECHANISM/processed_results/*_heldout.*`.

## 6 · Discussion

- **Why the mechanism experiment was worth running even though the
  verdict was H-none.** Pre-registration prevented an over-strong claim
  about σ inflation and produced a sharper story (tail contraction on
  a distribution held constant by upstream absorption).
- **Why G2 cannot beat L1 on raw detection rate — and why that is not
  a limitation.** G2's semantic contribution is the classification of an
  L1 event as "gate blindness" vs "gate reacting". Downstream (L8) can
  now condition on that distinction.
- **Limitations.** No held-out C1/C2 outcome numbers at time of
  submission; no adversarial faults; no cross-controller replication.

## 7 · One-sentence claim

*Under sustained sensor faults, the L6 conformal gate goes silent
because everything it reads is held constant while the plant diverges;
comparing L1 stream health with L6 alarms flags this blindness
label-free, with zero clean false alarms, at the same latency L1
achieves alone (5 ticks on `imu_dropout`), on both dev and held-out
seeds.*

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

- [ ] Stage C1 sweep complete + quadrant figure.
- [ ] Stage C3 outcome experiment written, run, analysed.
- [ ] Held-out Stage C1 + Stage C2 replication (Stage D).
- [ ] Amoukou et al. and D3M baseline implementations (§4.3 defer).
- [ ] ADR under `docs/adr/` for G2 → L8 abstention wiring.
- [ ] KS(conf) sequential correction patch (fixable engineering).
- [ ] Author order and affiliation (with Sushanth on his return).
- [ ] Licence update (LICENSE / NOTICE / README) once §0.6 licence choice
      is made (handoff §14).
