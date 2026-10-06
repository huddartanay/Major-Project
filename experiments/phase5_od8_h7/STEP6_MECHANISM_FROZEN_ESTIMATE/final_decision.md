# STEP 6 — final decision (7 October 2026)

Pre-registration `preregistration.md` (commit `d1f6144`). Dev run at `d1f6144`, verdict committed at
`c2b1d39`; held-out run once at `c2b1d39` on seeds `20270101 + i`. No amendment was needed.

## Verdicts

| hypothesis | dev | held-out | status |
|---|---|---|---|
| **H-indep** — silence does not depend on L8 stopping the vehicle | SUPPORTED | SUPPORTED | **CONFIRMED** |
| **H-freeze** — silence follows from the estimator receiving no new information, not from missing messages | SUPPORTED | SUPPORTED | **CONFIRMED** |
| **H-noise** — the score shift is the absence of measurement noise | REFUTED | REFUTED | **REFUTED** |

## Paired alarm-rate ratio to clean (median, 95 % interval, 30 seeds)

| arm | dev | held-out |
|---|---|---|
| dropout | 0.002 [0.000, 0.013] | 0.000 [0.000, 0.022] |
| dropout, L8 integrity path off | 0.000 [0.000, 0.016] | 0.003 [0.000, 0.013] |
| stuck (values frozen, still delivered) | 0.000 [0.000, 0.008] | 0.000 [0.000, 0.002] |
| stuck + noise | 0.000 [0.000, 0.006] | 0.000 [0.000, 0.000] |

Clean alarm rate (median): 5.80 % dev, 5.70 % held-out.

## Descriptive (held-out medians)

| arm | est. speed sd | mean abs(est − true speed) | L1 unhealthy |
|---|---:|---:|---:|
| clean | 0.188 | 0.01 m/s | 0/30 |
| dropout | 0.000 | 12.22 m/s | 30/30 |
| dropout, L8 integrity path off | 0.000 | 11.91 m/s | 30/30 |
| stuck | 0.000 | 11.95 m/s | **0/30** |
| stuck + noise | 0.009 | 11.95 m/s | **0/30** |

## What is established

1. **G1 is not an artefact of the stop.** The gate is silent under IMU loss whether or not L8 reacts.
2. **The cause is loss of information to the estimator, not loss of messages.** A sensor that keeps
   publishing a frozen value silences the gate equally.
3. **Measurement noise is not what drives the gate's clean alarms.** Restoring noise at the declared
   level restores nothing.
4. **A frozen sensor is seen by no layer:** L1 0/30, gate ≈0 %, while the speed estimate is wrong by
   about 12 m/s.

## What is not established

- Why the score moves *down* rather than up. The data are consistent with the clean alarms tracking
  real variation of the vehicle's state (estimated-speed sd 0.19 clean vs 0.000 frozen), but this was
  not a registered hypothesis and is an observation only.
- Whether this holds for another controller, another gate, or another sensor (Phase 2).
- 7–8 of 30 runs in the arms that stay otherwise NOMINAL end in HALT; the path was not traced.

## Consequences

- G3 can now be stated: *the gate compares two quantities computed from the same state estimate; when
  the estimate stops receiving information it stops moving, and so does the gate.*
- G2 as built cannot help in the frozen-sensor case — it needs L1 to fire first.
- The alarm-rate figures must be shown with the score distribution (3.689 ± 0.009 clean).
