# Stage A observations (dev seeds) — not a verdict amendment

`final_decision_dev.md` records the verdict — **H-none**, per the pre-committed
rule in `preregistration.md §5`. That verdict does not change on the basis of
anything in this file. What follows is what the data show *beyond* the pass /
fail of the three registered hypotheses, kept separate on purpose so a
post-hoc pattern-match cannot leak back into the decision that landed us in
Stage C rather than Stage B.

The Stage C design (§8 of the handoff, ITSC path) reads these observations to
say what a label-free blindness monitor would have to detect. That is why the
document exists.

---

## 1. What the L6 gate sees does not change under the fault

Every ratio of `(faulted median) / (clean median)` on the seed-paired arms is
essentially 1.00, for σ, departure and quantile, on every fault, for 3,400
ticks. `imu_dropout` (P400_999 phase, 30 dev seeds):

| field | median ratio | 95 % CI |
|---|---:|---|
| σ | 1.00 | [1.00, 1.00] |
| departure | 1.00 | [1.00, 1.00] |
| conformal_quantile | 1.00 | [1.00, 1.00] |
| true lane deviation | **1.55** | [1.31, 1.92] |

Tick-level spot-check at t = 500 (seed 20260731), same-seed pairing:

| field | faulted | clean |
|---|---:|---:|
| σ | 0.187867 | 0.187867 |
| departure | 0.693707 | 0.695613 |
| non_conformity_score | 3.692535 | 3.702684 |
| conformal_quantile | 5.429836 | 5.429836 |
| lane_deviation_m (truth) | 0.249802 | 0.151851 |
| **speed_mps (truth)** | **0.000000** | **10.950503** |

The plant has stopped moving. The gate does not know.

## 2. The suppression is at the tail, not the median

Median non-conformity score drops from 3.702684 (clean) to 3.692535 (faulted)
— about 0.3 %. Yet the alarm rate `P(score > 3.7024)` over ticks 400–3399 is:

- clean:   0.0500
- faulted: 0.0013

A **38× suppression** for a ≈0.3 % shift in the median. The distribution's
mean is pinned near the threshold, so its 95th percentile shifts a rank in
each seed, and every rank crossing on the clean side becomes a non-crossing
on the faulted side.

## 3. The three registered hypotheses were the wrong shape

H1 predicted σ inflation. **σ does not move at all.** The state-covariance
propagator holds control-dimension variance at a steady-state value even
during total sensor loss — that is a specific claim about the estimator's
covariance model, not this experiment's finding, but the fingerprint is
consistent with it.

H2 predicted departure collapse. Departure moves by less than 0.3 %.

H3 predicted threshold drift. The quantile is bit-identical (`5.429836` in
both arms every tick spot-checked; the shift detector is unwired for upward
motion, as the pre-registration notes).

None of the three describes what actually happens.

## 4. A working description of what actually happens (candidate for Stage C)

For every fault except the pure longitudinal ones (`speed_bias`,
`speed_stuck`), the plant's true tracking error diverges by 1.5× to 7× while
the L6 gate's inputs are held within 1 % of the clean baseline. The mechanism
appears to be **upstream absorption**: L2's estimator does not propagate an
unresolved fault as growing uncertainty, so L4 proposes against a self-
consistent (but wrong) belief, and L6 measures agreement between two things
neither of which knows the fault happened.

If this is right, the G2 blindness monitor (Stage C) cannot depend on any
signal internal to the L6 gate — score, σ, quantile, departure — because
none of them moves. The signal it can depend on is exactly what
E21 already showed: the L1 stream-health layer sees the fault directly (30/30
detections, 5-tick latency, on dev seeds), and G2's job is to notice the gap
between "L1 flagged" and "L6 remains passing".

## 5. What this file does not do

- Change the primary verdict. **H-none** stands.
- Justify submitting to IV. That is closed for Paper 1.
- Constitute a formal hypothesis. Section 4's description is a *candidate*
  Stage C hypothesis, to be pre-registered before any Stage C run measures it.
- Substitute for held-out replication. The held-out sweep still runs and
  either replicates these observations or contradicts them. If it
  contradicts, this file is deleted (or amended with a dated note); the
  primary verdict is unaffected either way.
