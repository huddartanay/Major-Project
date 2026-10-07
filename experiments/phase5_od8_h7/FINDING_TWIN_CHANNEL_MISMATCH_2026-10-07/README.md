# Finding — the L6 score is dominated by channels the twin does not model (7 October 2026)

Read from the code and from exploratory dev-seed runs. **Not a pre-registered result.**

## What the code does

- The twin (L5) is trained in `training/train_twin.py` to predict the command that explains the observed
  **lateral** acceleration: target = `(0, 0, a_lat / 120)` over the actuation space
  `(throttle, brake, steer)`. Its throttle and brake targets are **always zero**
  (`CONTROL_EFFECTIVENESS = (0.0, 0.0, 120.0)`; `config/environments/development.toml:54`).
- The gate (L6) scores `‖proposed − predicted‖ / σ` as a **Euclidean distance over all three channels**
  (`src/astra/layers/l6_statistical_gate/gate.py:131`).
- The proposer (L4) commands roughly `(0.65, 0.24, 0.00)`.

## Consequence, measured on clean dev runs

| channel | proposer | twin | share of departure² |
|---|---:|---:|---:|
| throttle | 0.647 | 0.000 | **87.2 %** |
| brake | 0.242 | −0.006 | **12.8 %** |
| steer | 0.000 | 0.013 | **0.04 %** |

The score is therefore `≈ sqrt(throttle² + brake²) / σ` — the size of the longitudinal command, which
the twin was never trained to predict. The one channel the twin does model contributes 0.04 %.
(Matches the measured correlation 0.98–0.999 between departure and ‖proposal‖.)

## What this means

1. **The gate is not testing the proposer against physics.** It thresholds the size of the longitudinal
   command at the 95th percentile of a band 0.25 % wide (3.689 ± 0.009).
2. **Every result built on the L6 score inherits this**: E17 separation, E18 calibration (threshold
   3.7024), R3b/R3c, Stage A, C1/C1b, C2/C3, STEP 6. The numbers are correct; what they measure is the
   longitudinal-command size, not proposer–twin physical disagreement.
3. **G1 as "conformal safety gates go silent under sensor loss" is not supported in general.** What is
   supported is narrower: *this* score falls slightly when a fault moves the closed loop to a different
   operating point.
4. **A different, defensible finding emerges:** the gate passed every calibration check (30/30 runs in
   band on held-out seeds, stable false-alarm rate) while 99.96 % of its score came from channels its
   reference model does not predict. **Calibration validity did not reveal an uninformative score.**

## Not yet known

- Whether a correctly specified gate (steer channel only, or a twin that also models longitudinal
  dynamics) goes silent under sensor loss. **This is the experiment that decides whether G1 is general.**
- Whether the mismatch is known and intended; no ADR or docstring found states it.
