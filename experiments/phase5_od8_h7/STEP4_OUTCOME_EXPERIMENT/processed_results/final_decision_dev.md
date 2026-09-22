# Stage C3 -- Outcome (observed; counterfactual = lower bound)

**Runs analysed:** 349

| fault | magnitude | arm | n | median nom-frac | escalation tick | never-esc | G2 fires | G2 tick | CF speed-up (lb) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `clean` | medium | clean | 30 | 1.000 | 9 | 0.83 | 0.00 | -- | -- |
| `imu_dropout` | medium | faulted | 30 | 0.002 | 205.0 | 0.00 | 1.00 | 205.0 | 0.0 |
| `lateral_noise` | medium | faulted | 30 | 0.017 | 233.0 | 0.00 | 0.00 | -- | -- |
| `position_bias` | high | faulted | 19 | 0.003 | 209 | 0.00 | 1.00 | 213 | 0 |
| `position_bias` | low | faulted | 30 | 1.000 | -- | 1.00 | 0.00 | -- | -- |
| `position_bias` | medium | faulted | 60 | 0.004 | 213.0 | 0.00 | 0.97 | 213.0 | 0.0 |
| `position_bias` | mid_low | faulted | 30 | 1.000 | 1690 | 0.83 | 0.00 | -- | -- |
| `position_bias` | subthreshold | faulted | 30 | 1.000 | -- | 1.00 | 0.00 | -- | -- |
| `position_drift` | medium | faulted | 30 | 0.365 | 1278.0 | 0.00 | 0.77 | 1301 | 0 |
| `speed_bias` | medium | faulted | 30 | 1.000 | -- | 1.00 | 0.00 | -- | -- |
| `speed_stuck` | medium | faulted | 30 | 1.000 | -- | 1.00 | 0.00 | -- | -- |

**CF speed-up** = lower bound on the ticks the G2 monitor would have brought escalation forward by, if L6 were forced to abstain from the G2 fire tick. Full L8 counterfactual requires the abstention wiring landed by Stage D.
