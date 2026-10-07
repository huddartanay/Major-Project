# Exploratory — why the gate's score moves down under a frozen sensor (7 October 2026)

**Exploratory. Not pre-registered. Dev seeds 20260731, 20260733, 20260735; arms `clean` and `stuck`
(STEP 6 definitions); ticks 400–3399.** Script `drift_explore.py`.

## Observations

| quantity | clean | stuck |
|---|---|---|
| corr(departure, ‖proposal‖) | 0.98 – 0.996 | 0.99 – 0.999 |
| twin prediction (three channels) | ≈ (0.000, −0.006, 0.013), sd ≤ 0.0015 | same, sd ≤ 0.0001 |
| proposal | ≈ (0.647, 0.243, 0.000) | ≈ (0.62–0.64, 0.26–0.29, 0.000) |
| corr(departure, estimated lateral position) | −0.71 to −0.72 | −0.54 to −0.80 |
| estimated lateral position, mean | 0.156 m | **0.30 – 0.40 m** |
| estimated speed sd | 0.10 – 0.34 | 0.000 |
| departure mean | 0.6930 | 0.6900 – 0.6915 |
| true speed, mean | 11.2 m/s | 0.5 – 1.5 m/s |

Alarm threshold in departure units: 3.7024 × 0.1879 = 0.6957.

## Reading

1. **The score is, to within 2 %, the size of the proposer's command divided by a constant.** The twin's
   prediction is close to zero and nearly constant, so it contributes almost nothing to the departure.
2. **The score falls as the estimated lateral offset grows** (correlation ≈ −0.7 in clean driving).
3. Under the frozen sensor the vehicle crawls and **settles further from the lane centre** (estimated
   offset roughly doubles). By (2) that lowers the score — which is the downward shift.
4. So the direction of the shift is an **operating-point effect in closed loop**, not a loss of spread:
   the lateral estimate still varies under the fault (sd ≈ 0.04 m in both arms).

A linear fit from the clean runs predicts the right sign and about twice the observed size of the shift.

## What this changes

- STEP 6's verdicts stand, but the sentence "the estimate stops moving, so the gate stops moving" is too
  strong: only the speed estimate freezes. Better: *the fault moves the closed loop to an operating point
  where the proposer's command is smaller, and the gate's score is essentially that command's size.*
- It raises a design question that needs checking in code before anything is claimed: **why does the twin
  predict ≈ 0 while the proposer commands ≈ 0.69**, and is a score that *decreases* with lateral offset
  what L6 is meant to measure?

## To make this confirmatory

Pre-register: fit departure on the estimated state using clean runs only; predict the per-run shift in
each fault arm on fresh seeds; state in advance the fraction of the shift the fit must explain.
