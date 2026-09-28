# Stage C1 observations (dev) — WALK_AWAY_OR_SHIFT

## The quadrant is honest and the verdict binds

Pre-registration §5 committed: cell A non-empty for ≥ 2 of 4 parameterised
faults → PROCEED_TO_STAGE_C2. **Cell A count on the 3 completed faults is
0.** The rule fires **WALK_AWAY_OR_SHIFT**.

| cell | count | meaning |
|---|--:|---|
| A (L1 detects, gate quiet) | 0 | G2's target — empty |
| B (L1 detects, gate loud) | 5 | nominal: L1 fires and L6 does its job |
| C (L1 misses, gate quiet) | 0 | subthresholds are silent for both |
| D (L1 misses, gate at baseline) | 10 | no fault effect |

The 3 completed faults (`position_bias`, `position_drift`, `speed_bias`;
`lateral_noise` was in flight when the runner crashed on a subthreshold
magnitude violation, fixed for future runs) show a consistent split:

- **Position faults at low+ magnitudes are cell B.** L1 detects them (via
  the stream-consistency check on lateral position), the L6 gate also
  reacts (departure ratio 1.26-1.27, see Stage A observations), the
  gate does its job. No blindness to catch.
- **Position faults below `low` are cell D.** L1 misses, gate stays at
  baseline (alarm rate near clean 0.058), plant tolerates the fault.
  Nothing worth detecting.
- **All `speed_bias` magnitudes are cell D.** Neither L1 nor the gate
  reacts to a longitudinal speed error — consistent with the Stage A
  observation that speed faults leave true lateral tracking unchanged
  (err ratio 1.00 at every phase).

## Why cell A is empty here but non-empty for `imu_dropout`

`imu_dropout` is parameterless and was not part of the C1 sweep, but it
is where G2's story lives. The compelling case is:

| fault | L1 detects | gate quiet | cell |
|---|---|---|---|
| `imu_dropout` (Stage A) | yes (30/30, 5-tick) | yes (0.002 alarm rate) | **A** |
| `position_bias` at medium (C1) | yes (30/30, 13-tick) | no (1.0 alarm rate) | B |
| `speed_bias` at any tested magnitude | no | at baseline | D |

The pattern is: **sensor-loss faults** (DROPOUT, and by extension
STUCK_AT — see the Stage A speed_stuck row) produce cell A because the
estimator's covariance model does not propagate missing information as
growing uncertainty. **Value-corruption faults** (BIAS, DRIFT, NOISE) do
not, because the corrupted value still moves the L2 estimate, which
still moves the L4 proposer's plan, which the L6 gate does see.

## What "shift" looks like for the paper

The pre-committed §5 walk-away has two branches. The **shift** branch:

> Paper 1's ITSC contribution is narrowed from "G2 for the gate-blindness
> regime" to "**G2 for the sensor-loss regime**". The Stage A mechanism
> observations extend to `imu_dropout` and `speed_stuck` (parameterless,
> both show the invariant-inputs pattern); the parameterised value-
> corruption faults are documented as *out of scope* for G2 with a clear
> reason, and are cited as future work with the D3M / Amoukou baselines
> as the natural direction.

The **walk away** branch is exactly what its name says: the ITSC
contribution as pre-registered does not carry a paper on its own,
Sushanth and Dr. Chaitra R. are notified on his return, and the effort
is redirected.

The choice between the two branches is Sushanth's -- and this
observation was not fabricated to make one look easier than the other.
The evidence is the evidence.

## Follow-up sweep the shift branch would need

For the shift branch to publish, the paper needs the analogous C1 sweep
on the sensor-loss regime -- concretely, `imu_dropout` at graded severity
(partial dropout: 25 %, 50 %, 75 %, full) and `speed_stuck` at graded
onset delays. The current DROPOUT injector is all-or-nothing, so this
would need a small extension to `training/faults.py` (a
`FaultChannel`-selective dropout with a probability parameter). That
extension is code, not a research question; if the shift branch is
chosen, this is the first PR.

## Runner fix that landed with this file

`stage_c1_run.py`'s `_magnitudes` function used `0.1 x low` for the
subthreshold point, which for `lateral_noise` produced 0.5 -- below
NOISE_BURST's floor of 1.0. Runner now branches: NOISE_BURST subthreshold
= 1.5 (smallest defensible value above the floor), everything else keeps
`0.1 x low`. The 3 completed faults were unaffected by the fix; the
lateral_noise data is missing from this dev sweep and will be regenerated
in a rerun if the shift branch is chosen.

## What was NOT changed

- The pre-registration itself. §5's rule and §4's cell definitions stand
  exactly as committed.
- The primary verdict. WALK_AWAY_OR_SHIFT is the verdict.
- Any earlier committed evidence. Stage A dev + held-out, E21 L1
  held-out, Stage C2 dev PASS all still hold — they described the
  `imu_dropout` case that is now the whole story.
