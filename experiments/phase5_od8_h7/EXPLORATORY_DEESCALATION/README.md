# Exploratory probe — does L8 step down while a fault is still active? (18 September 2026)

**Exploratory, not pre-registered.** Dev seeds 20260731–20260735 only; held-out seeds untouched. 3,400
ticks, sustained faults opening at tick 200 (E21 injectors). Script `deesc_probe.py`, raw output
`results.json`. The demo speed hack in `training/closed_loop.py` was still active.

| fault | peak mode | de-escalations while fault active | share of post-onset time in NOMINAL | gate veto rate | L1 unhealthy share |
|---|---|---|---|---|---|
| clean | NOMINAL | — (one start-up transient, seed 34, tick 15) | 1.00 | 0.5–0.8 % | 0 |
| imu_dropout | LIMP (5/5) | 0 | 0.002 | 0.06–16 % | 1.00 |
| position_bias | HALT (5/5) | 0 | 0.004 | 16–99 % | ~0.96 |
| **position_drift** | **HALT (5/5)** | **2–10 per run, 5/5 runs** | **0.36–0.38** | 15–58 % | ~0.61 |
| lateral_noise | HALT (5/5) | 0–3 (LIMP→DEGRADED, OOD counter 28) | 0.01–0.04 | 78–99 % | 0 |
| speed_bias | **NOMINAL (5/5)** | 0 | **1.00** | 0.5–0.8 % | 0 |
| speed_stuck | **NOMINAL (5/5)** | 0 | **1.00** | 0.5–0.8 % | 0 |

**Findings**

1. **False de-escalation happens.** Under `position_drift`, all 5 runs escalate, then step back down —
   first event at ticks 1264–1387, DEGRADED→NOMINAL or LIMP→DEGRADED — while the drift is still
   present. At that tick the OOD counter is 0–2 (the gate is passing) **and L1 reports healthy**:
   both layers are quiet at once. The vehicle then spends ~36 % of the faulted period in NOMINAL before
   the growing drift drives it to HALT.
2. **Never escalating is the larger exposure.** Under `speed_bias` and `speed_stuck` the vehicle stays
   in NOMINAL for the entire faulted run: no layer sees the fault.
3. **L1 is what holds the vehicle under imu_dropout.** The gate is near-silent in 3/5 runs, but the
   integrity counter keeps the vehicle in LIMP with no de-escalation — consistent with G1 (gate silent)
   and with ADR-0024's design (L8 reads L1).

**What this does and does not show.** It shows mode recovery while a fault persists, driven by
simultaneous quiet in the gate and L1. It does not yet show harm at the moment of recovery (true
tracking error was not recorded), and 5 dev seeds are not a result. A pre-registered version needs
held-out seeds, the true state error at each transition, and the demo hack disabled.
