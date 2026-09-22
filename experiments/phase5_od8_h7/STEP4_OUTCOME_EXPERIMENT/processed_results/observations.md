# Stage C3 observations (dev, lower-bound counterfactual)

## Primary finding

At medium fault magnitude, the L8 failsafe **already escalates via the
integrity counter** (L1-driven) at roughly tick 205 -- five ticks after
fault onset, matching E21 L1's 5-tick latency. G2 fires at the same tick.
The lower-bound counterfactual speedup is therefore **0 ticks**: forcing
L6 to abstain when G2 fires cannot bring escalation forward, because L1
is already driving it there.

Applying pre-registration §3 verbatim:

- (1) ticks_in_nominal_faulted already at 0.002 (99.8% out of NOMINAL);
      a further ≥ 50% drop is not measurable from this floor.
- (2) escalation_tick already 205 median for imu_dropout at medium; CF
      speedup of 0 ticks fails the ≥ 20-tick criterion.
- (3) needless_escalation_on_clean: G2 does not fire on any of the 30
      clean runs, so **G2's clean-FP contribution is 0**. (Aggregate
      "clean escalation" of 0.17 in the table is the setup transient,
      not the monitor.)

Per the pre-committed §3 fallback: **paper framing shifts from "G2 helps
escalate faster" to "G2 is safe to add (zero clean false alarms) and
correctly identifies gate-blindness episodes; the outcome benefit at
medium magnitudes is null because L1's own escalation path already
handles them, and G2's value at smaller magnitudes is bounded by the L1
detection floor observed in Stage C1."**

## The lower-bound is genuinely a lower bound

Under a full L8 replay (Stage D), forcing L6 abstention when G2 fires
does two things the offline analysis cannot capture:

1. Removes L6's contribution to the OOD counter. In the current wiring
   L6 vetoes push the counter up, L6 passes push it down. Abstention
   contributes neither. If L6 was silently passing while L1 was
   unhealthy, abstention removes a downward force on the OOD counter,
   which can bring escalation forward through the OD-8 path even when
   integrity was already driving it.
2. Removes the L6 verdict's participation in the L9/RCM arbitration,
   which changes the trajectory in DEGRADED / LIMP states.

Neither is knowable without wiring the change into the live pipeline
and rerunning. The lower-bound of 0 is the least generous reading of
the counterfactual; Stage D's real-driven counterfactual can only make
it larger.

## Where G2's value would show up if the setting exposed it

- Faults where L1 misses but the gate still changes behaviour (Stage C1
  cell A). The Stage A dev raw shows this cell is empty for imu_dropout,
  speed_bias, speed_stuck at every magnitude tested so far; Stage C1's
  in-flight sweep is characterising it for the parameterised faults.
- Downstream classification: if L8 or a policy layer wants to
  distinguish "L1 unhealthy" from "L6 blind while L1 unhealthy",
  the two events carry different information about what to do next.
  This is not a Paper 1 experiment; it is future work.

## What this means for the ITSC paper

Section §5.6 of the paper skeleton now reads: "Outcome experiment
(pre-registered lower-bound counterfactual): G2 fires on 100% of
`imu_dropout` runs at 5-tick latency with zero clean false alarms;
observed L8 escalation is already at 5 ticks via the integrity path, so
the offline counterfactual speedup is 0 ticks. Stage D's full L8 replay
under G2-driven L6 abstention is required to measure the with-monitor
outcome; that measurement is scoped in `docs/adr/` (to be written) and
runs against the same held-out seeds as Stage D's C1/C2 replication."

That is exactly the honesty the pre-registration §3 case (2) was
written to secure.
