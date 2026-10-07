# STEP 7 — final decision (7 October 2026)

Pre-registration at `361ffd1`; threshold τ = 9.1897 frozen at `109beea`; dev run at `109beea`, verdict
committed at `7f2c35b`; held-out run once at `7f2c35b` on seeds `20270201 + i`. No amendment.

## Outcome

| split | outcome |
|---|---|
| dev | **G1-ARTEFACT** |
| held-out | **MIXED / INCONCLUSIVE** |

**By the pre-registered rule the dev outcome is not confirmed.** No outcome is confirmed.

## What holds on both splits

| item | dev | held-out |
|---|---|---|
| P-cal — clean runs in the calibration band | 30/30 (median 5.02 %) | 30/30 (median 4.88 %) |
| P-sens — `position_bias` | DETECTS, 11.0× [7.6, 17.6] | DETECTS, 17.2× [11.5, 18.3] |
| `dropout_noL8` SUPPRESSED? | no (median 2.87×) | no (median 2.16×) |
| `stuck` SUPPRESSED? | no (median 5.24×) | no (median 5.20×) |

So: **the corrected score is a valid instrument, and under sensor loss it is not suppressed** — on either
split. The pre-registered outcome **G1-SILENT is rejected on both**.

## What does not replicate

The DETECTS class needs the interval's lower bound above 1.0. Dev: 1.48 and 2.17. Held-out: 0.61 and 0.92.
The medians agree; the intervals do not clear the bar.

## Why — per-seed ratios (descriptive, not a pre-registered analysis)

Runs out of 30 by ratio to the same seed's clean alarm rate:

| arm | split | < 0.25 | 0.25–0.5 | 0.5–2 | > 2 |
|---|---|---:|---:|---:|---:|
| dropout_noL8 | dev | 6 | 0 | 5 | 19 |
| dropout_noL8 | held-out | 6 | 3 | 6 | 15 |
| stuck | dev | 6 | 1 | 3 | 20 |
| stuck | held-out | 5 | 3 | 5 | 17 |
| position_bias | dev | 0 | 1 | 1 | 28 |
| position_bias | held-out | 0 | 0 | 3 | 27 |

The response to sensor loss is **split across runs**: in roughly 50–65 % the corrected gate alarms at more
than twice its clean rate, and in roughly 20 % it is nearly silent. A median with a bootstrap interval
summarises that poorly, which is why the class is unstable.

## Conclusions that may be stated

1. A score restricted to the channel the twin models **passes calibration and detects the positive
   control**, on dev and held-out.
2. That score is **not suppressed** under total IMU loss or a frozen sensor. The suppression of the
   shipped score is therefore **not a general property of this gate**; it is tied to the shipped score's
   construction. *"Conformal safety gates go silent under sensor loss"* must not be claimed.
3. It is **not established** that the corrected gate reliably detects sensor loss. In about one run in
   five it stays quiet.

## Open

- What decides whether a run alarms or stays quiet (candidate: the values the frozen channels hold at
  onset). Needs its own pre-registration with a **run-level** outcome (share of runs detected at a fixed
  run-level false-alarm rate) in place of a median ratio.
- The corrected score still carries a constant offset (≈8.5), i.e. a systematic twin bias on steer
  (twin effectiveness 120 vs plant 140 is a candidate).
- Other controllers, gates, sensors.
