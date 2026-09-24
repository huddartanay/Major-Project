# STEP 4 · Outcome experiment — Pre-Registration (Stage C3 of the 19 Sep 2026 handoff)

**Written 22 September 2026, before any counterfactual is computed.** Any
change requires an `amendment.md`.

Owner: Tanay Huddar. Sushanth C unavailable this session.

---

## 1 · Why this experiment exists

Stage C2 established that `GateBlindnessMonitor` fires correctly on
gate-blindness episodes with zero clean false alarms and 5-tick latency.
The remaining question the ITSC paper has to answer, from handoff §8
Stage C3: *does acting on the flag help?*

The action the handoff (§11 SI-3) names is **L6 abstention**: when G2
fires, L6's verdict is treated as ABSTAIN (via ADR-0016's path), so the
per-tick decision falls to L7a / L7b and L8 escalates on its integrity
counter alone rather than partly on OD-8's silence.

This experiment does not wire that change into `src/astra/`. Doing so
requires an ADR under `docs/adr/` and re-driving the pipeline. Instead
it computes the counterfactual **offline**: for each committed run, take
the recorded per-tick state, and reconstruct what the L8 failsafe machine
would have done if the L6 verdict were forced to ABSTAIN from the tick G2
first fires. The full-fidelity closed-loop version follows in Stage D
once the ADR is written.

Justification for the offline approach: the L8 escalation rule is the
worse-of-two counters (OD + integrity, `l8_failsafe/machine.py`); its
next-state is a pure function of the per-tick counters and the current
state. Both counters are already in the Stage A tick JSONL. The
counterfactual is therefore a deterministic replay, not a simulation.

## 2 · Design

**Input.** Every faulted run under `STEP1_MECHANISM/raw_results/` and
`STEP2_MAGNITUDE_SWEEP/raw_results/`. Each carries the failsafe state
and both counters per tick.

**Counterfactual reconstruction.** For each run:

1. Replay the run's per-tick records through every monitor
   (`benchmarks.g2_monitor`) to determine when G2 fires.
2. Reconstruct the L8 state trajectory assuming L6 abstained from
   tick `g2_fire_tick` onward. Since L8's state depends on the OOD
   counter (partly driven by L6 vetoes), abstention makes L6's
   contribution to that counter effectively neutral: OD-8 no longer
   passes (which is the current behaviour) nor vetoes, so the OOD
   counter follows integrity-only dynamics.

**Metrics per run:**

- **`ticks_in_nominal_faulted`** — number of ticks between fault onset
  and end-of-run where L8 was NOMINAL, under the counterfactual.
  Compared against the actual run's ticks_in_nominal_faulted.
- **`escalation_tick`** — first tick after fault onset where L8 left
  NOMINAL (moved to DEGRADED or lower), or `None` if it stayed NOMINAL.
- **`needless_escalation_on_clean`** — for clean runs (`arm = "clean"`),
  did L8 leave NOMINAL under the counterfactual? Should be `no` on almost
  all clean runs; a monitor that flips clean runs to LIMP is not worth
  the cost.

**Aggregated per (fault, magnitude):**

- Median ticks_in_nominal_faulted, with and without the monitor.
- Median escalation_tick, with and without the monitor.
- Fraction of clean runs with needless_escalation.

## 3 · Pre-committed pass rule

The G2 monitor's outcome contribution **passes Stage C3** iff, on
`imu_dropout` at medium (the headline case) across dev seeds:

1. `ticks_in_nominal_faulted` drops by ≥ **50 %** under the
   counterfactual (i.e. the vehicle spends less than half as long in
   NOMINAL when the monitor triggers L6 abstention),
2. `escalation_tick` drops by ≥ **20 ticks** median (the vehicle leaves
   NOMINAL detectably earlier),
3. `needless_escalation_on_clean` stays under **0.05** on the 30 dev
   clean seeds.

If all three hit → Stage D (held-out replication + generality) proceeds.
If (1) or (2) misses but (3) holds → the paper reports "the monitor is
safe to add (no clean false escalations) but its outcome benefit is
modest / null"; the framing shifts from "helps" to "does not hurt".
If (3) misses → the monitor as designed is unsafe to add; back to
Stage C2 with a tighter design.

## 4 · Integrity

- No `src/astra/` change; L8 reconstruction is a benchmark module.
- L8 rules quoted from `src/astra/layers/l8_failsafe/machine.py`; a
  unit test in `tests/unit/test_c3_l8_replay.py` (to be added with
  the runner) pins the reconstructed transitions against the real
  machine on a handful of committed runs, so a rename in L8 fails
  loudly.
- Frozen threshold `3.7024`.
- Same dev seeds as Stage A / C1 / C2; no new randomness in the
  counterfactual.

## 5 · What Stage C3 does not do

- Wire G2 to L8 in the live pipeline. Stage D.
- Held-out replication. Stage D.
- Adversarial faults or semantic errors.
- Any statement about "safety in the wild". The plant is synthetic;
  every result carries the `[M-syn]` reservation the repo already
  uses in claim ledger entries.
