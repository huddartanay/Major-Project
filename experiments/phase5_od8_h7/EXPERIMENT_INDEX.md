# Experiment Index

| Experiment | Question | Status | Main result | Decision |
|---|---|---|---|---|
| E17 | Controlled fault observability | **Complete** | Heterogeneous observability; 1 of 6 faults well-posed absorption | Baseline |
| E17-Position | Does absorption survive correct injection? | **Complete** | Absorbed in 0 of 12 cells | Claim withdrawn |
| **E18** | Can OD-8 be validly calibrated? | **Complete, verdict revised** | D_s does not predict detection; P1 verdict withdrawn after window-mismatch correction | **PARTIAL** |
| **E18-R1** | Can run-local calibration recover P3? | **Complete** | P3 9/30; mechanism removed but estimator too noisy; **found E18 window defect** | **FAIL-P3** |
| **E18-R2** | Does matched-window pooled calibration work? | **Complete** | P1 13/30 (best of 3); obstacle is the score process, not the threshold | **PARTIAL-R2** |
| **E18-R3** | Precision-limited or dynamics-limited? | **Complete** | P1 30/30 at n=3200 (160 s). Precision-limited | **PASS-R3** |
| **E18-R3b** | Does it detect faults at the long window? | **Complete** | 4/6 at 100 %. Detection comes from the post-fault transient, not statistical power | **PASS, mechanism refuted** |
| **E18-R3c** | Duration-matched control: is detection aftermath or sustained? | **Complete** | Sustained `imu_dropout` alarms at 0.2 %, below clean baseline. Only 3 of 6 faults detected under sustained injection | **H-AFTERMATH SUPPORTED** |
| E19 | Does the observability profile predict monitor placement? | **Unblocked for P1** | - | - |
| E20 | How does single-channel manipulation propagate? | **Future** | - | - |

## E18 headline

OD-8's failure was **calibration-set provenance**, not threshold value: a global recalibration
reproduces the original defect exactly (0.00 % clean false alarms on P1/P3, 11.06 % on P2).
Policy-conditional calibration fixes it for one policy.

Frozen thresholds, version 1: **P1 3.7095 | P2 5.9024 | P3 3.4000** at eps = 0.05.

| policy | pooled FAR | per-run median [IQR] | runs in band | drift/SD | class |
|---|--:|---|:--:|--:|---|
| P1 | 5.47 % | 4.88 % [3.25, 7.25] | **21/30** | 0.09 | **VALID** |
| P3 | 8.16 % | 1.00 % [0.75, 12.56] | 4/30 | 0.03 | CONDITIONAL |
| P2 | 4.67 % | 0.00 % [0.00, 0.00] | 0/30 | **1.28** | **INVALID** |

**Pooled false-alarm rates were misleading for P2 and P3.** Changing the unit of analysis from tick
to run reduced the valid set from two policies to one.

## Findings carried forward

1. **`D_s` does not predict operational detection.** 17 of 28 cells disagree. `D_L1` vs detection:
   Spearman rho = **-0.480**, p = 0.0088 - a *negative* association.
2. **Fault-induced alarm suppression replicates** - 11 of 28 cells, all p < 0.05. `imu_dropout` on P1
   makes the monitor 55x *less* likely to alarm than clean operation.
3. **`speed_stuck` and `imu_dropout` are undetectable** by OD-8 at any tested severity, correctly
   calibrated, on both P1 and P3.
4. **P2 is INVALID for fixed-quantile calibration** - non-stationary score, 30/30 runs drift upward.

Updated after every experiment.


## E18-R1 correction to E18

E18 measured **false-alarm rate over ticks 0-399** and **detection over ticks 200-399**. On the
matched window:

| policy | E18 reported (whole run) | matched window | R1 run-local |
|---|--:|--:|--:|
| P1 runs in band /30 | 21 | **4** | 3 |
| P3 runs in band /30 | 4 | 5 | **9** |

**E18's "P1 VALID" is withdrawn.** No policy currently has defensible run-level false-alarm behaviour
on the window where detection decisions are made. E19 is blocked until E18-R2 resolves this.


## Experiments from 18 September 2026 onward

Status key: **C** confirmatory (pre-registered before results, held-out confirmed) · **E** exploratory ·
**F** finding read from code. Every folder holds its own pre-registration, runner and decision.

| folder | question | type | result | decision |
|---|---|---|---|---|
| `EXPLORATORY_DEESCALATION` | Does L8 step down while a fault persists? | E | `position_drift` steps down in 5/5 dev runs; speed faults stay NOMINAL 100 % | Evidence for G4; not a result |
| `STEP1_MECHANISM` (Stage A) | Why is the gate silent? H1 σ / H2 departure / H3 threshold | **C** | All three rejected; σ, departure, quantile ratios 1.00 on dev and held-out | **H-none** |
| `STEP1_MECHANISM/heldout_reconfirm` | Do R3c and E21's L1 numbers hold on held-out seeds? | **C** | Gate alarm 0.00 %; L1 30/30, 5 ticks, 0 false alarms | **CONFIRMED** |
| `STEP2_MAGNITUDE_SWEEP` (C1) | Do value faults populate "L1 detects, gate quiet"? | C (dev only; `lateral_noise` arm crashed, L1 reconstructed) | Cell A empty on 3 of 4 faults | **WALK_AWAY_OR_SHIFT** |
| `STEP5_SENSOR_LOSS_SWEEP` (C1b) | Does graded IMU loss populate it? | **C** | Cell A only at 100 % loss, dev and held-out | **NARROW** |
| `STEP3_G2_MONITOR` (C2) | Does the G2 monitor pass its rule? | **E** (pre-registration not prior to results — see `REVIEW_NOTE.md`) | 1.000 / 5 ticks / 0 false alarms — **identical to L1-only** | Not a contribution yet |
| `STEP4_OUTCOME_EXPERIMENT` (C3) | Does acting on G2 help? | **E** (see `REVIEW_NOTE.md`) | 0 ticks at 100 % loss; 1,181–1,640 at 25 % (censored; vs L8 counter, not L1-only) | Not a result |
| `EXPLORATORY_MECHANISM_2026-10-06` | Is the silence caused by L8 stopping the car? | E | Silence persists with L8's integrity path off; score is 3.689 ± 0.009 | Led to STEP 6 |
| `STEP6_MECHANISM_FROZEN_ESTIMATE` | H-indep / H-freeze / H-noise | **C** (held-out block `20270101+i`) | H-indep and H-freeze confirmed; H-noise refuted. Frozen sensor: L1 0/30, gate ≈0 %, speed estimate wrong by ≈12 m/s | **Final** |
| `EXPLORATORY_SCORE_DIRECTION_2026-10-07` | Why does the score move down? | E | Score ≈ size of the proposal (corr 0.98–0.999); falls with lateral offset, which grows under the fault | Led to the finding below |
| `FINDING_TWIN_CHANNEL_MISMATCH_2026-10-07` | What does the twin predict? | **F** | Twin models steer only; 99.96 % of the L6 score is throttle + brake | Affects every L6-score result |
| `STEP7_EFFECT_SPACE_GATE` | Does G1 survive a correctly specified (lateral, effect-space) score? | **C** (calibration `20260901+i`, held-out `20270201+i`) | Valid on both splits (calibration 30/30; positive control detected). **Not suppressed** under sensor loss on either split. Dev G1-ARTEFACT; held-out MIXED — detection not confirmed; response is split across runs (≈55–65 % alarm > 2×, ≈20 % quiet) | **No outcome confirmed; G1-SILENT rejected** |

**Reading the older rows above in light of the twin finding:** every experiment that uses the L6 /
OD-8 score (E17, E18 and its revisions, R3b, R3c, E21's OD-8 column, Phase 2, STEP 1–6) measured a
score dominated by the size of the longitudinal command. The numbers stand; their interpretation as
"proposer–twin physical disagreement" does not.
