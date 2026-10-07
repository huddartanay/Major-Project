# STEP 7 — Does G1 survive a correctly specified gate? (pre-registration)

**Written 7 October 2026, before any run of this study.** Author: Sushanth. Tanay has not yet read it;
the dev run proceeds on Sushanth's instruction and that fact is recorded here.

## 1 · Why

`FINDING_TWIN_CHANNEL_MISMATCH_2026-10-07`: the shipped L6 score is a Euclidean distance over
(throttle, brake, steer), but the twin models only the lateral channel; 99.96 % of the clean score comes
from throttle and brake. STEP 6 confirmed the shipped score is suppressed under sensor loss. This study
asks whether that suppression is a property of gates of this kind or of the mis-specified score.

## 2 · The corrected score (benchmark code only — no change under `src/`)

`s_lat = | B·π_proposed − B·π_twin | / σ`, with `B = (0, 0, 120)` — the twin's configured
`control_effectiveness` — and `σ` the value the gate itself reports each tick. This is the difference, in
m/s², between the lateral acceleration the proposal implies and the one the twin predicts, normalised as
the gate normalises. The twin and its checkpoint are unchanged.

Note: the plant's own `steer_effectiveness` is 140, the twin's is 120. The twin's value is used because
the question is about the gate as built. The mismatch is recorded, not corrected.

## 3 · Calibration (fixed now)

Threshold `τ` = 0.95 quantile of `s_lat` pooled over ticks 400–3399 of **30 clean calibration runs**,
seeds `20260901 + i`. Calibration seeds are used for nothing else. `τ` is committed before any
evaluation run.

## 4 · Design

| arm | fault from tick 200 | purpose |
|---|---|---|
| `clean` | none | baseline |
| `dropout` | `imu_dropout` | sensor loss, governed |
| `dropout_noL8` | `imu_dropout`, L8 integrity path neutralised | sensor loss without L8's stop |
| `stuck` | `STUCK_AT` on speed and lateral acceleration | frozen sensor, L1 blind |
| `position_bias` | E21 medium `position_bias` | **positive control** — a fault that changes steering |

30 runs per arm, 3,400 ticks, evaluation window ticks 400–3399, policy `var/policy/synthetic.pt`,
`demo_speed_assist` off. **Dev seeds** `20260731 + i`. **Held-out seeds** `20270201 + i` (new block).
Runner refuses a dirty working tree.

## 5 · Preconditions (reported with every verdict)

- **P-cal:** at least 24 of 30 clean evaluation runs have a per-run alarm rate in [0.025, 0.10].
- **P-sens:** `position_bias` is classified DETECTS (below).

If either fails, the corrected gate is itself not a valid instrument and the outcome is
**NO-VALID-GATE**; arm classifications are still reported, flagged.

## 6 · Classification of each fault arm

Paired ratio `alarm(arm, seed) / alarm(clean, seed)`; median over seeds; 95 % bootstrap interval
(2,000 resamples of seeds). Seeds with a clean alarm rate of 0 are excluded from ratios and counted.

| class | rule |
|---|---|
| **SUPPRESSED** | median ≤ 0.25 and upper bound < 0.50 |
| **DETECTS** | median ≥ 2.0 and lower bound > 1.0 |
| **UNCHANGED** | median within [0.5, 2.0] and interval within [0.25, 4.0] |
| **INCONCLUSIVE** | anything else |

## 7 · Outcomes and what each means

Decided on `dropout_noL8` and `stuck` (the two arms where L8's stop does not confound).

| outcome | rule | meaning for the paper |
|---|---|---|
| **G1-SILENT** | both SUPPRESSED | The silence survives a correctly specified score: G1 is a property of the estimate-fed gate |
| **G1-BLIND** | both UNCHANGED (or one UNCHANGED, one SUPPRESSED) | The corrected gate does not go quiet, but does not notice either: blindness without silence. G1 is restated accordingly |
| **G1-ARTEFACT** | either DETECTS | The corrected gate reacts to sensor loss: the shipped gate's silence was produced by the mis-specified score. G1 is withdrawn; the paper is about calibration not revealing an uninformative score |
| **MIXED / INCONCLUSIVE** | anything else | Reported as such |

An outcome is **confirmed** only if it is the same on dev and held-out. Held-out runs once, after the dev
verdict is committed, with no change to code, threshold or rules.

## 8 · Descriptive outputs

Per arm: `s_lat` p50 / p95 / sd; steer of proposal and twin (mean, sd); mean |estimated − true speed|;
L1 detection (first unhealthy tick).

## 9 · Deviations

Recorded in `amendment.md`, with reason, before the affected run.
