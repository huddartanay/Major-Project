# Stage C3 -- Outcome (observed; counterfactual = lower bound)

**Runs analysed:** 330

| fault | magnitude | arm | n | median nom-frac | escalation tick | never-esc | G2 fires | G2 tick | CF speed-up (lb) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `clean` | medium | clean | 30 | 1.000 | 9 | 0.83 | 0.00 | -- | -- |
| `imu_dropout` | medium | faulted | 30 | 0.002 | 205.0 | 0.00 | 1.00 | 205.0 | 0.0 |
| `imu_dropout` | p025 | faulted | 30 | 1.000 | 2128.5 | 0.60 | 1.00 | 412.5 | 1640.0 |
| `imu_dropout` | p050 | faulted | 30 | 0.954 | 314.0 | 0.00 | 1.00 | 227.0 | 71.0 |
| `imu_dropout` | p075 | faulted | 30 | 0.014 | 212.0 | 0.00 | 1.00 | 210.5 | 0.0 |
| `imu_dropout` | p100 | faulted | 30 | 0.002 | 205.0 | 0.00 | 1.00 | 205.0 | 0.0 |
| `lateral_noise` | medium | faulted | 30 | 0.017 | 233.0 | 0.00 | 0.00 | -- | -- |
| `position_bias` | medium | faulted | 30 | 0.004 | 213.0 | 0.00 | 0.97 | 213 | 0 |
| `position_drift` | medium | faulted | 30 | 0.365 | 1278.0 | 0.00 | 0.77 | 1301 | 0 |
| `speed_bias` | medium | faulted | 30 | 1.000 | -- | 1.00 | 0.00 | -- | -- |
| `speed_stuck` | medium | faulted | 30 | 1.000 | -- | 1.00 | 0.00 | -- | -- |

**CF speed-up** = lower bound on the ticks the G2 monitor would have brought escalation forward by, if L6 were forced to abstain from the G2 fire tick. Full L8 counterfactual requires the abstention wiring landed by Stage D.
