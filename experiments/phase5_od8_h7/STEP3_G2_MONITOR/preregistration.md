# STEP 3 · G2 Monitor — Pre-Registration (Stage C2 of the 19 Sep 2026 handoff)

**Written 22 September 2026, before any evaluation run of the monitor.** Any
change requires a dated `amendment.md`. Existing raw results are not
re-analysed under the amended rule.

Owner (drafting): Tanay Huddar. Sushanth C unavailable this session;
primary author proceeding under his authorisation.

---

## 1 · Why this experiment exists

Stage A landed at H-none, held-out replicates. The finding stands: the L6
conformal gate goes silent under sustained faults because everything it
reads is held near its clean-baseline value while the plant diverges 1.5-7×.
Handoff §7 Stage C says the ITSC contribution is **G2 · a label-free
monitor for gate blindness**. This is that monitor's design, its baselines
and its pass criterion, all committed before any evaluation is run.

## 2 · Design — one sentence per monitor

- **`GateBlindnessMonitor` (the contribution).** Fires when L1 stream health
  is unhealthy AND L6 is not alarming for ``patience`` consecutive ticks.
  Rationale is direct from Stage A: no L6-internal signal moves under
  fault, so the comparison must be across layers.

Baselines (label-free unless noted):

- **`L1OnlyMonitor`.** Fires when L1 stream health has been unhealthy for
  ``patience`` ticks. E21's `health` detector reused verbatim; the
  strongest existing detector on this pipeline (30/30 sustained
  `imu_dropout` on dev, held-out replicates).
- **`KSConfMonitor`.** Two-sample Kolmogorov-Smirnov on a sliding window
  of L6 non-conformity scores vs a reference clean window (Sun & Lampert,
  arXiv 1804.04171). Bonferroni over tests-run for level control.
- **`ConformalMartingaleMonitor`.** Volkhonskiy et al. exchangeability
  martingale (arXiv 1706.03415) on the score stream. Fires when the
  martingale exceeds ``1 / alpha``.
- **`OracleMonitor`.** Fires the first tick `fault_active` becomes True.
  Not a deployable detector; a ceiling.

Amoukou et al. (2412.12910) and D3M (2506.05047) are named as future
baselines in the handoff; they are heavier to implement and are deferred
to a follow-up PR. The first pass compares against L1-alone, KS(conf), the
martingale and the oracle. Adding Amoukou/D3M later does not alter this
pre-registration's rule; the analyser reads whatever monitors are on the
`ALL_MONITORS` tuple at run time.

## 3 · Evaluation dataset

The Stage A dev sweep (`experiments/phase5_od8_h7/STEP1_MECHANISM/
raw_results/`) already provides 30 clean + 6 × 30 faulted runs at 3,400
ticks each. This experiment does not re-drive the pipeline; it re-plays
the recorded `DecisionRecord`s through every monitor. That is why C2 costs
seconds, not hours.

Stage C1's magnitude sweep (`STEP2_MAGNITUDE_SWEEP/raw_results/`) will
extend the evaluation dataset to 4 faults × 5 magnitudes × 30 seeds when
it completes. C2's rule and design do not depend on C1's outcome; the
same monitors run against whichever raw sets are present at analysis time.

## 4 · Metrics per monitor per (fault, magnitude, seed)

- `fired` — bool.
- `first_fire_tick` — int | None.
- `latency_ticks` — first_fire_tick minus fault_onset, or None.
- `false_alarm` — bool: fired on a clean run, or fired before onset on
  a faulted run.

Aggregated per (monitor, fault, magnitude) across seeds:

- Detection rate = fraction of runs with `fired` True and no `false_alarm`.
- Median latency (over runs that detected).
- Clean false-alarm rate = fraction of clean runs with `fired` True.

## 5 · Pass criterion, pre-committed

The G2 monitor **passes Stage C2** iff, on the Stage A dev sweep and any
available C1 cells:

1. Its detection rate on `imu_dropout` is at least as high as `L1OnlyMonitor`'s,
   AND
2. Its median latency is within 2× `L1OnlyMonitor`'s median latency,
   AND
3. Its clean false-alarm rate is at most **0.10** (matches E21's `CLEAN_BAR`).

If it also **beats** every label-free baseline (L1-alone, KS(conf),
martingale) on the fraction of (fault, magnitude) cells where it
uniquely detects — i.e. it fires and at least one label-free baseline
does not — then Stage C3 (outcome experiment) proceeds to the ITSC
headline. If it merely matches the best label-free baseline, Paper 1's
G2 contribution shifts from "beats the field" to "the first monitor
built on the L1-vs-L6 comparison; performance is on par with X".

If it fails all three criteria, the ITSC contribution has to shift or
Paper 1 walks away — same pre-committed off-ramp as Stage C1 §5.

## 6 · Integrity checklist

- Frozen threshold `3.7024`, quoted from `benchmarks.g2_monitor`.
- No new `src/astra/` changes; monitor code is under `benchmarks/`.
- Every monitor is a fresh instance per run; the factory `build_monitors`
  is the only entry point, and the unit test in
  `tests/unit/test_g2_monitor.py` pins that identity.
- Ground truth (`fault_active`) is fed to each monitor but only
  `OracleMonitor` reads it. A regression that leaked ground truth to a
  label-free monitor would show up as its detection rate matching the
  oracle exactly, and Stage C1's per-run summary is on disk to catch
  that.

## 7 · What Stage C2 does not do

- Design G2's reaction (L6 abstention path). That is Stage D, and needs
  an ADR per handoff §11 SI-3. C2 measures the monitor; C3 measures the
  outcome of acting on it.
- Include Amoukou et al. or D3M. Deferred to a follow-up.
- Replicate on held-out. Held-out C2 runs after C3 lands; combined into
  Stage D's single held-out sweep.
