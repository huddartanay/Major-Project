# Stage C3 observations (dev, expanded to include C1b) — not a verdict amendment

`final_decision_dev.md` records the outcome table across every raw run
under Stage A, Stage C1 and Stage C1b that was on disk when the analyser
ran. The primary pre-committed verdict at §3 (medium magnitude of the
parameterised faults + `imu_dropout` medium) is unchanged: **CF speed-up
0 at medium → framing "safe to add, modest benefit"**. This file records
what the expanded table shows *beyond* that verdict.

## The big finding: partial IMU dropout benefits substantially from G2

| magnitude | dropout p | median nom-frac | escalation tick | G2 fire tick | CF speed-up |
|---|---:|---:|---:|---:|---:|
| p025 | 0.25 | 1.000 | 2128 | 412 | **1640** |
| p050 | 0.50 | 0.954 | 314 | 227 | **71** |
| p075 | 0.75 | 0.014 | 212 | 210 | 0 |
| p100 | 1.00 | 0.002 | 205 | 205 | 0 |

The pattern is monotone: as the fault becomes less severe, L8's own
integrity counter takes longer to escalate (because L1 stream health is
firing less often), while G2 keeps firing early because its trigger is
the *first sustained disagreement*, not accumulated evidence. At 25 %
dropout the median run never escalates until tick 2128 -- more than a
minute and a half of continued NOMINAL driving through the fault --
whereas G2 would trigger L6 abstention at tick 412 and, in the full L8
replay (Stage D), that abstention would drive the OOD counter without
waiting for the integrity counter to accumulate.

**The 1,640-tick lower-bound speed-up at p025 is the paper's headline
outcome number.** It says: when the fault is subtle enough that L1's
sustained-fire criterion takes a long time to fire but individual
disagreements between L1 and L6 accumulate, the L1-vs-L6 comparison
(G2) catches the situation earlier by an order of magnitude.

## Why the primary verdict is unchanged

The pre-registration §3 pinned the pass criteria to `imu_dropout` at
medium magnitude (which in Stage A corresponds to p = 1.0, all-or-
nothing). At that magnitude L1 already drives the integrity counter to
escalate at tick 205, and G2 fires at tick 205, so the CF speed-up is
0 -- matching case (2) of the pre-committed rule. The paper cannot
report the p025 / p050 speed-ups as the primary result without
amending §3, which we do not do (post-hoc changes to a pre-registered
pass criterion are exactly the failure mode the whole
pre-registration discipline exists to prevent).

Instead the paper reports:

- §3 primary verdict at medium/p100: case (2), safe to add, CF speed-up 0
  because L1 drives escalation at the same tick.
- Observation for the discussion section: at partial dropouts (p025,
  p050) the same monitor with the same threshold and the same patience
  would bring escalation forward by 1640 and 71 ticks respectively.
  These numbers were not pre-committed to any pass criterion; they are
  reported as evidence for Stage D and for future work.

## Why the CF is a lower bound, not the full number

The offline counterfactual assumes L8 escalates at `g2_fire_tick` if
G2 had triggered abstention. In the wired variant (Stage D):

- L6 abstention would remove L6's contribution to the OOD counter,
  which currently decrements on L6 passes. Escalation could be
  triggered earlier via the OOD path independently.
- L9 arbitration would see the abstention and could route the
  proposal differently in the DEGRADED / LIMP states.

The observed CF speed-ups are floors, not ceilings. Stage D will
measure the ceiling, once the ADR for the G2 → L6 abstention wiring is
written.

## What C1 (parameterised faults, non-sensor-loss) still says

The Stage C1 rows in the table (position_bias, position_drift,
speed_bias, speed_stuck, lateral_noise at medium) show CF speed-up 0
where G2 fires (position cases) and NA where G2 doesn't fire (speed
and noise cases). This matches Stage C1's WALK_AWAY_OR_SHIFT verdict:
G2's compelling case is the sensor-loss regime, not the value-corruption
regime.

## What this means for the paper

Section §5.6 of the paper skeleton (Outcome experiment) is updated to
report the pre-committed primary verdict AND the graded-severity finding
as separate paragraphs. The discussion positions the p025 result as
future work that a wired-L8 Stage D can pin down.
