# Exploratory mechanism probe — why the gate is silent under IMU loss (6 October 2026)

**Exploratory. Not pre-registered. Dev seeds 20260731–20260735 only.** Script `mech_explore.py`, raw
summaries `results.json`. Ticks 400–3399, sustained `imu_dropout` from tick 200. One arm neutralises
L8's integrity path from a benchmark hook (`on_assembled`); nothing in `src/` was changed.

## Question

Stage A's spot check showed the plant at 0 m/s under the fault. Is the gate silent **because of the sensor
loss**, or only **because L8 (via L1) has already stopped the car**?

## Result (mean over 5 seeds)

| arm | L8 state | alarm rate | score p50 | score p95 | score sd | true speed | estimated speed |
|---|---|---:|---:|---:|---:|---:|---:|
| clean | NOMINAL | 0.0519 | 3.689 | 3.702 | 0.0092 | 11.17 | 11.17 |
| clean, integrity path off | NOMINAL | 0.0519 | 3.689 | 3.702 | 0.0092 | 11.17 | 11.17 |
| dropout, governed | LIMP | 0.0017 | 3.682 | 3.693 | 0.0074 | **0.00** | **11.99** |
| dropout, integrity path off | **NOMINAL** | **0.0021** | 3.678 | 3.693 | 0.0092 | **1.09** | **11.99** |

Threshold 3.7024. σ = 0.1879 in every arm.

## What it shows

1. **The silence is caused by the sensor loss, not by the stop.** With L8's integrity path off the car
   stays in NOMINAL and the gate is just as silent (0.0021 vs 0.0519 clean).
2. **The estimated speed freezes exactly** (standard deviation 0.0 within a run) at its value at fault
   onset, while the true speed falls to 0–2 m/s. The estimator has no other source of speed.
3. **The score is almost a constant.** Clean: 3.689 ± 0.009 (0.25 %). The threshold sits at the 95th
   percentile of that band. Under the fault the score moves down by about 0.007–0.011 — roughly one
   standard deviation — and that is enough to take the alarm rate from 5 % to 0.2 %.
   The "100× suppression" is therefore a **small location shift of a near-constant score**, not a
   collapse of its spread (score sd is unchanged in the integrity-off arm). The tail-collapse wording in
   Stage A's observations is not supported as stated.
4. **Why the car stops in the governed arm:** L9 enforces L8's speed cap using the *estimated* speed
   (`arbiter.py`, `_speed_capped`), which is frozen above the LIMP cap, so braking never releases.
5. **With the integrity path off** the vehicle sits in NOMINAL at about 1 m/s while the estimator reports
   about 12 m/s, and no gate objects.

## Consequences

- **G1 survives the control**, but must be stated precisely: the gate compares two quantities computed
  from the same estimate, so it cannot register a fault that leaves that estimate self-consistent. Its
  score has very little dynamic range in this regime.
- The 5.84 % → 0.2 % figure must always be shown with the score distribution beside it.
- New, separate finding: **estimated and true speed diverge by ~11 m/s under IMU loss with no layer
  flagging the estimate itself** (L1 flags the sensor; nothing flags the state).

## Not yet known

Why the score moves *down* (candidate: the proposer's input loses the noise of the lost channel, and a
norm of a less noisy vector is smaller). Needs a pre-registered test.
