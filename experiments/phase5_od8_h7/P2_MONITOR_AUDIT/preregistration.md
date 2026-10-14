# P2 — Monitor informativeness audit (pre-registration)

**Phase P1, task T1.2 · written 14 October 2026 · Sushanth.**
**Status: DRAFT. Not frozen.** It becomes binding when Sushanth and Tanay have both read it and it is committed
with the status line changed to FROZEN. No P2 seed may be run before that commit, and the runner will refuse a
dirty working tree.

Fault classes and metrics follow `docs/FAULT_MODEL_EVALUATION.md`.

---

## 1 · The claim under test (C1)

> A monitor can meet its calibration target and still be insensitive to the quantity it is meant to judge.
> A label-free audit — needing no fault injection — can tell such a monitor from an informative one, and its
> verdict predicts whether the monitor detects real faults.

The first sentence is already observed once (`FINDING_TWIN_CHANNEL_MISMATCH_2026-10-07`: the shipped L6 score is
87.2 % throttle, 12.8 % brake, 0.04 % steer). This study asks whether the **audit** is a method, not an anecdote.

## 2 · The audit

For a monitor with score `s(x)`, threshold `τ`, and declared monitored quantity `Q`:

**A1 · Channel share (CS).** For monitors whose score compares a proposal `π` with a reference `π̂`:
`CS = Σ_{j∈M} (π_j − π̂_j)² / Σ_j (π_j − π̂_j)²`, where `M` is the set of channels the reference model actually
predicts (non-zero row of the platform effectiveness `B`, or the channels the reference was trained on). Per run:
median over evaluation ticks. Not defined for monitors without a proposal/reference pair (reported "n/a").

**A2 · Perturbation response (d).** Counterfactual: on each logged clean tick, recompute the score with the
proposal changed by a known amount in the monitored quantity, using the monitor's own score function on the
logged inputs. No run is altered.

`d(Δ) = [ median_t s(π ⊕ Δ) − median_t s(π) ] / max(IQR_t s(π), 1e-9)` per run.

| perturbation | operator | sizes |
|---|---|---|
| lateral (primary) | steer += Δ / 120 (implied lateral acceleration changes by Δ m/s²) | Δ ∈ {0.5, **1.0**, 2.0} |
| longitudinal (secondary) | throttle += Δ / 3.0 (implied longitudinal acceleration changes by Δ m/s²; acceleration authority 3.0) | Δ ∈ {0.5, 1.0, 2.0} |

The primary size, 1.0 m/s², is the magnitude of the lateral-acceleration offset that put the car 10.9 m off
centre in the exploratory run of 7 October; it is fixed here, before any audit value is computed.

Descriptive alongside: counterfactual alarm rate `P_t[s(π ⊕ Δ) > τ]`.

**Verdict per monitor** (on the per-run values; median over runs, 95 % bootstrap interval, 2,000 resamples of runs):

| verdict | rule |
|---|---|
| **INFORMATIVE** | (CS ≥ 0.5 or CS n/a) **and** median d(1.0) ≥ 1.0 with lower bound > 0.5, for the monitor's declared Q |
| **UNINFORMATIVE** | CS < 0.05, **or** median d(1.0) < 0.25 with upper bound < 0.5 |
| **INCONCLUSIVE** | anything else |

## 3 · Monitors

| id | monitor | score | threshold | declared Q | M (channels modelled) |
|---|---|---|---|---|---|
| **M1** | Shipped L6 statistical gate | `non_conformity_score` from `layers/l6_statistical_gate/gate.py` | per-tick `conformal_quantile` from the gate's evidence | lateral control | {steer} |
| **M2** | Lateral score (STEP 7) | `|B·π − B·π̂| / σ`, B = (0, 0, 120) | τ = 9.18967 (`STEP7…/threshold.json`) | lateral control | {steer} |
| **M3** | L7b model-divergence check | `|B·π − B·π̂|` (m/s²) | 4.0 m/s² (`[physical] admissible_divergence_mps2`) | lateral control | {steer} |
| **M4** | Behaviour reference monitor (independent) | `‖(π − π_ref) / σ_ref‖₂`, π_ref from a ridge regression of the command on the fast state estimate, σ_ref the per-channel residual s.d. on its training data | 0.95 quantile on its calibration seeds | all three channels | {throttle, brake, steer} |
| **M4b** | M4 deliberately mis-built | same, but the reference is trained to predict steer only (zero targets for throttle and brake) | 0.95 quantile on its calibration seeds | lateral control | {steer} |

M4 is a re-implementation in the spirit of a learned feed-forward reference (PID-Piper, DSN 2021): built without
the twin, by a different method, on different seeds. M4b reproduces M1's defect in M4's family on purpose; it is
the known-answer control for the audit. M4 and M4b code is written and committed with this document frozen, before
any of their data is generated.

**Predictions, written now:** M1 UNINFORMATIVE (CS ≈ 0.0004 expected). M2 INFORMATIVE. M3 INFORMATIVE on d, with a
low counterfactual alarm rate at Δ = 1.0 because its threshold is 4.0. M4 INFORMATIVE. M4b UNINFORMATIVE.

## 4 · Does the audit predict detection? (validation, labelled)

Positive controls, on the same seeds as the audit:

| control | injection | path |
|---|---|---|
| PC-pos | IMU position +1.0 m from tick 200 | `RedundantSensing.build(faulted=IMU, bias=1.0)` — per-channel path that reaches the estimator |
| PC-lat | lateral acceleration +1.0 m/s² from tick 200 | `FaultInjector` bias on channel `a` |

Integrity check (`docs/FAULT_MODEL_EVALUATION.md` §6, item 1): every faulted run must differ from its clean control; a run that does not
is excluded and counted, and if more than 2 of 30 are excluded for a control, that control is void.

Detection per monitor and control uses the STEP 7 rule: paired alarm ratio to the same seed's clean run; median
over seeds with bootstrap interval; DETECTS if median ≥ 2.0 and lower bound > 1.0.

**The audit is validated on a split if**, for every monitor whose verdict is not INCONCLUSIVE:
INFORMATIVE ⇒ DETECTS at least one control, and UNINFORMATIVE ⇒ DETECTS neither.

**Calibration status** of each monitor is also reported: clean runs with alarm rate in [2.5 %, 10 %], at least
24 of 30. C1 requires at least one monitor that is calibrated **and** UNINFORMATIVE.

## 5 · Outcomes

| outcome | rule | meaning |
|---|---|---|
| **C1-SUPPORTED** | validated on dev and held-out; at least one calibrated UNINFORMATIVE monitor; M4b UNINFORMATIVE and M4 INFORMATIVE | The audit is a method, shown in two independently built monitor families |
| **C1-NARROW** | validated, but only within the twin family (M1–M3) | Holds for our gate; generality not shown. Paper 1 becomes a case study (decision point T2.6) |
| **C1-NOT-SUPPORTED** | validation fails on either split | The audit does not predict detection; C1 is dropped as a method |
| **INCONCLUSIVE** | anything else | Reported as such |

An outcome is confirmed only if the same on dev and held-out.

## 6 · Design

| item | value |
|---|---|
| Ticks per run | 3,400; evaluation window 400–3,399 |
| Fault onset (controls) | tick 200, sustained |
| Policy | `var/policy/synthetic.pt`; `demo_speed_assist` off |
| Runs per arm | 30 |
| Dev seeds | `20260731 + i` |
| Held-out seeds (new block, used once) | `20270401 + i` |
| M4 / M4b training seeds | `20270501 + i`, i < 10 |
| M4 / M4b calibration seeds | `20270601 + i`, i < 30 |
| Arms per seed | clean, PC-pos, PC-lat |

Seed blocks `2027040x`, `2027050x`, `2027060x` are unused anywhere in the repository as of this draft (checked 14
October). `20270301 + i` stays reserved for STEP 8.

## 7 · A trap this design must avoid

`PHASE2_MONITORABILITY` (9 September) pre-registered a metric that turned out to be a monotone transform of the
score median against the threshold, so its correlation with alarm rate was largely an identity. Here: CS does not
involve the threshold at all, and d is normalised by the clean score spread, not by the threshold. The validation
target (detection of injected faults) is a different quantity from the audit's counterfactual (a perturbation of
the proposal only, with the estimate untouched). The analysis will additionally report, per monitor, whether the
counterfactual alarm rate at Δ = 1.0 alone would have given the same validation result; if it would, that is
stated as a limitation.

## 8 · Descriptive outputs

Per monitor and run: CS; d at all six (perturbation, size) pairs; counterfactual alarm rates; clean alarm rate;
alarm ratios for both controls; first-detection tick. Per seed for the controls: L8 mode timeline (HALT and
non-HALT runs reported separately — see `STEP7…/POST_HOC_NOTE_2026-10-07.md`).

## 9 · Decisions (settled by Sushanth, 14 October 2026)

1. Primary perturbation size **1.0 m/s²**, with 0.5 and 2.0 reported for dose-response.
2. **M4 and M4b included**; M4's reference is a ridge regression (simpler and more reproducible than a neural
   network; a neural reference may be added later only by amendment).
3. Thresholds in §2 kept as written (CS 0.5 / 0.05; d 1.0 / 0.25).
4. The L3 innovation score and the MMD shift detector are reported **descriptively only** and do not count
   towards C1, because for them a perturbation is itself a fault injection.

Still required before FROZEN: Tanay's written agreement.

## 10 · Deviations

Recorded in `amendment.md`, with reason, before the affected run.
