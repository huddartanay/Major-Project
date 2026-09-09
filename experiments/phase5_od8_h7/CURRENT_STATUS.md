# Phase 5 — Current Status

**Updated 9 September 2026.** Supersedes the 1 September version, which still described E18 Part 2
as running; R1, R2, R3, R3b, R3c and Phase 2 have all completed since.

| | |
|---|---|
| Active experiment | none — **E21 complete: BASELINE WINS** |
| Last completed | **E21 — baseline comparison** |
| E18 series | **Closed.** R3c is the terminal result |
| E19 | Unblocked for P1, **not** pre-registered. Waiting on E21 |
| E20 | Future |

## Where the programme actually is

The E18 series is finished and its terminal finding is E18-R3c:

> **A persistent sensor failure is invisible to the conformal monitor for as long as it persists.**

Alarm rate 0.2 % under sustained `imu_dropout` against a ~5 % clean baseline, for 160 continuous
seconds, on all 30 seeds, at a frozen threshold, with a duration-matched control. Under sustained
injection **3 of 6** faults are detected; R3b's fourth was the post-fault recovery transient.

Phase 2 then asked whether a monitorability metric predicts that detection. It **partially deleted
the ASTRA 2.0 proposal**, which is what it was for:

- Identity-free ρ = 0.654 (p = 0.0113) — the **weak** band, not the pass band.
- The pre-registered primary (ρ = 0.895) is inflated by an identity between the metric and its
  outcome. The confound was in the frozen definition, and it is reported rather than buried.
- **The location-only formulation is withdrawn.** It reads sustained `imu_dropout` as mildly
  elevated while the monitor is running 25× quieter than clean — a dispersion failure a location
  statistic structurally cannot see.
- `D_s` is confirmed dead as a predictor a second time, now with no algebraic path to the outcome:
  ρ = 0.077, p = 0.7192.

## What E21 decided

E18-R3c's negative result has never been compared against anything. `benchmarks/detectors.py` has
held three simple detectors since P2.7 — one of which its own docstring calls "the principled
candidate" — and none has ever been run against OD-8.

E21 asks whether they detect the faults OD-8 misses. Pre-registered at `ae997b3`, paired with R3c
on the same 30 seeds, same six faults, sustained injection, 3,400 ticks, plus a clean arm.

**A baseline won.** `health` detects `imu_dropout` 30/30 at 0.000 clean false positives, against
OD-8's 0/30, with a median latency of 5 ticks. **The contribution reframes: the blind spot is
architectural.** The evidence was present at L1 and the gate does not consult it.

`trust` was disqualified by firing on 77 % of clean runs — predicted as the risk in §9 of the
pre-registration. `innovation`, the detector its own docstring calls "the principled candidate",
detected essentially nothing. `speed_bias` and `speed_stuck` are undetected by **everything** tested.

## Immediate next steps

1. **E21 completes** and its decision is written.
2. **E19 / H7** pre-registered — but only after E21, because E19 measures where to place a monitor
   and E21 decides which monitor is worth placing.
3. **Literature review.** Still the gating item for the novelty claim, and unaffected by any of the
   above.

## Known open items, carried

- Two integration tests (`test_not_one_gate_fires_while_it_happens`,
  `test_the_posture_escalates_on_sensor_health_rather_than_on_a_verdict`) have been red since before
  the dashboard work and are still unexplained. Confirmed to predate it at `1b09738`.
- A demo speed-reset sits in `training/closed_loop.py`, the shared harness. **Measured inert** —
  0 of 6 paired runs differ, bit-for-bit, because the `NOMINAL` guard never coincides with a speed
  below 1 m/s. It is a latent trap, not a live contaminant.
- OD-10 (innovation covariance omits `H Q Hᵀ`, ~1.24× inflation at the median) is uncorrected.
- `[M-ext]` remains **0 of 30**. Everything here is one synthetic plant, P1 only, `medium` severity.
