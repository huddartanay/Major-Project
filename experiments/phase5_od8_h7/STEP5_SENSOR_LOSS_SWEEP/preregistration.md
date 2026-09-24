# STEP 5 · Sensor-loss magnitude sweep — Pre-Registration (Stage C1b, shift branch)

**Written 24 September 2026, before any run of this experiment.** Any change
requires a dated `amendment.md`. Existing raw results are not re-analysed
under the amended rule.

Owner (drafting and reviewing): Tanay Huddar (repo owner). Sushanth C
unavailable; Tanay proceeding as sole authoriser per his standing
instruction ("I am the owner, you do the review, do it properly").

---

## 1 · Why this experiment exists

Stage C1's completed 450 runs delivered **WALK_AWAY_OR_SHIFT** per its
pre-committed §5 rule -- cell A (L1 detects, gate silent) is empty on the
parameterised faults tested (`position_bias`, `position_drift`,
`speed_bias`). The `observations.md` alongside that verdict explains why:
value-corruption faults propagate through the estimator, so the L6 gate
sees them; **only sensor-loss faults** produce the "invariant inputs" +
"tail contraction" pattern Stage A documented, and none of C1's four
faults is a sensor-loss fault.

The **shift** branch of that pre-commitment says: narrow the ITSC
contribution from "G2 for the gate-blindness regime" to "**G2 for the
sensor-loss regime**", and produce the graded-magnitude evidence C1 owes
the paper on that regime specifically.

This experiment is that evidence. It sweeps `imu_dropout` at four graded
severities from partial to total on 30 dev seeds and applies the same
L1-vs-gate quadrant rule the C1 pre-reg §4 committed.

## 2 · Design at a glance

**Fault library extension.** `benchmarks/graded_dropout.py` adds
`graded_dropout_injector(probability=p, ...)`. `p = 1.0` reproduces the
shipped all-or-nothing `dropout()`; intermediate values Bernoulli-sample
per tick under a seeded RNG. Ground truth ("was this tick dropped?") is
carried on the returned `FaultInjector` unchanged, so the mechanism logger
and every downstream detector work without modification.

**Fault set:** `imu_dropout` at four probabilities `{0.25, 0.50, 0.75, 1.0}`.
The 1.0 point is the R3c / Stage A / E21 baseline, included so the rerun
under this experiment's runner is self-consistent with the earlier
committed evidence.

**Window:** sustained from tick 200 through tick 3399, identical to R3c.
**Ticks per run:** 3,400 (as Stage A).
**Seeds:** dev `20260731 + i` for `i ∈ [0, 30)`.
**Clean baseline:** reused from Stage A (`STEP1_MECHANISM/raw_results/
clean_<seed>.jsonl`, seed-deterministic; no re-execution).
**Cost:** 4 magnitudes × 30 seeds = **120 runs** faulted, no new clean.
At the Stage A observed ~7 s/run, **~14 min wall time**.

## 3 · Fields recorded

Same 15 per-tick fields as Stage A / Stage C1, via
`benchmarks/mechanism_logger.py`. In addition, per run, the same
`detector_summary.json` fields Stage C1's runner emits: `l1_detected`,
`l1_first_fire_tick`, `l1_latency_ticks`, `l1_false_alarm`.

## 4 · The four quadrants — same rule as Stage C1 §4

For each of the four probabilities the run population is placed in one
of the four cells:

|  | **L1 detects** | **L1 misses** |
|---|---|---|
| **Gate quieter than baseline** | **A** (G2's target) | **C** (both blind) |
| **Gate at baseline or louder** | **B** (nominal) | **D** (no fault effect) |

L1-detect axis: ≥ 15 of 30 runs fire L1 with `first_fire_tick ≥ 200`.
Gate-quiet axis: median faulted alarm rate over ticks 400–3399 ≤ 50 %
of the clean-baseline median (0.05 from Stage A). Both thresholds match
the C1 pre-reg verbatim.

## 5 · Pre-committed decision, one sentence

**If cell A is non-empty for at least 2 of the 4 probabilities** → the
paper's G2 story is complete: the monitor's compelling regime is
characterised on graded severity. Stage C2's PASS verdict stands and
Stage D proceeds (held-out replication + wired L8 counterfactual).

**If cell A is non-empty for exactly 1 of 4 probabilities** → the paper
reports the single-cell result honestly ("G2's compelling case is total
IMU loss; partial loss falls into cell B or D and G2 shares L6's fate
there"). Stage D still proceeds but the framing narrows to `p = 1.0`.

**If cell A is empty across all four probabilities** → walk away.
Nothing on this pipeline shows the L1-fires-and-L6-silent regime except
the pre-existing R3c / Stage A / E21 result on `p = 1.0`, and if this
experiment does not reproduce that, the earlier evidence is called into
question and the paper does not ship. This is the strictest off-ramp
possible; committing it here is the cost of the shift branch's
credibility.

## 6 · Integrity checklist

- Frozen threshold `3.7024`, hard-coded, never recomputed.
- Stage 0's `demo_speed_assist=False` default enforced by the runner's
  integrity check (delegated to the same helper as Stage A / C1).
- Git working tree clean at run start.
- Same seed set as Stage A dev; clean baseline reused, so this sweep
  contributes no new source of clean-arm variance.
- Runner script committed **before** the first run and its git SHA in
  every JSONL header.
- Raw JSONL git-ignored (same pattern as Stage A / C1); the
  `detector_summary.json` and `processed_results/` enter the repo.

## 7 · What this experiment cannot establish

- The wired L8 counterfactual (needs the abstention ADR).
- Held-out replication (Stage D).
- Non-dropout sensor-loss faults (e.g. `speed_stuck` with graded onset
  delay). That is a natural extension; not this sweep.
- Anything about adversarial faults or semantic errors.

## 8 · Cost cap

15 minutes wall time on dev. If the sweep is still running after 25
minutes, kill it, diagnose, and either resume or restart clean. Same
policy as Stage C1 §9.
