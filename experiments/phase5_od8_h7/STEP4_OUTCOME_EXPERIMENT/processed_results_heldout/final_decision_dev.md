# Stage C3 -- Outcome (observed; counterfactual = lower bound)

**Runs analysed:** 330

| fault | magnitude | arm | n | median nom-frac | escalation tick | never-esc | G2 fires | G2 tick | CF speed-up (lb) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `clean` | medium | clean | 30 | 1.000 | 17 | 0.90 | 0.00 | -- | -- |
| `imu_dropout` | medium | faulted | 30 | 0.002 | 205.0 | 0.00 | 1.00 | 205.0 | 0.0 |
| `imu_dropout` | p025 | faulted | 30 | 1.000 | 1602.0 | 0.53 | 1.00 | 420.5 | 1181.0 |
| `imu_dropout` | p050 | faulted | 30 | 0.950 | 299.5 | 0.00 | 1.00 | 218.5 | 47.5 |
| `imu_dropout` | p075 | faulted | 30 | 0.009 | 210.0 | 0.00 | 1.00 | 208.0 | 0.0 |
| `imu_dropout` | p100 | faulted | 30 | 0.002 | 205.0 | 0.00 | 1.00 | 205.0 | 0.0 |
| `lateral_noise` | medium | faulted | 30 | 0.020 | 246.0 | 0.00 | 0.00 | -- | -- |
| `position_bias` | medium | faulted | 30 | 0.004 | 213.0 | 0.00 | 1.00 | 213.0 | 0.0 |
| `position_drift` | medium | faulted | 30 | 0.373 | 1249.5 | 0.00 | 0.97 | 1319 | 0 |
| `speed_bias` | medium | faulted | 30 | 1.000 | -- | 1.00 | 0.00 | -- | -- |
| `speed_stuck` | medium | faulted | 30 | 1.000 | -- | 1.00 | 0.00 | -- | -- |

**CF speed-up** = lower bound on the ticks the G2 monitor would have brought escalation forward by, if L6 were forced to abstain from the G2 fire tick. Full L8 counterfactual requires the abstention wiring landed by Stage D.
