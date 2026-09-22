# Stage C2 -- Final Decision (dev)

**Runs evaluated:** 257 faulted, 30 clean
**Sources:** experiments/phase5_od8_h7/STEP1_MECHANISM/raw_results, experiments/phase5_od8_h7/STEP2_MAGNITUDE_SWEEP/raw_results

## Primary result: **PASS**

gate_blindness detection=1.000 vs l1_only 1.000; gate_blindness latency=5.0 vs l1_only 5.0; gate_blindness clean_fp=0.000 (bar 0.1)

## Clean false-alarm rate per monitor

| monitor | clean FP |
|---|---:|
| `gate_blindness` | 0.000 |
| `l1_only` | 0.000 |
| `oracle` | 0.000 |
| `ks_conf` | 0.733 |
| `conformal_martingale` | 0.000 |

## Per-(fault, magnitude) detection

| monitor | fault | magnitude | n | detection | median latency | clean FP |
|---|---|---|---:|---:|---:|---:|
| `gate_blindness` | `imu_dropout` | medium | 30 | 1.000 | 5.0 | 0.000 |
| `l1_only` | `imu_dropout` | medium | 30 | 1.000 | 5.0 | 0.000 |
| `oracle` | `imu_dropout` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `imu_dropout` | medium | 30 | 1.000 | 203.0 | 0.733 |
| `conformal_martingale` | `imu_dropout` | medium | 30 | 0.033 | 8 | 0.000 |
| `gate_blindness` | `lateral_noise` | medium | 30 | 0.000 | -- | 0.000 |
| `l1_only` | `lateral_noise` | medium | 30 | 0.000 | -- | 0.000 |
| `oracle` | `lateral_noise` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `lateral_noise` | medium | 30 | 1.000 | 203.0 | 0.733 |
| `conformal_martingale` | `lateral_noise` | medium | 30 | 1.000 | 80.0 | 0.000 |
| `gate_blindness` | `position_bias` | low | 30 | 0.000 | -- | 0.000 |
| `l1_only` | `position_bias` | low | 30 | 0.000 | -- | 0.000 |
| `oracle` | `position_bias` | low | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `position_bias` | low | 30 | 1.000 | 520.0 | 0.733 |
| `conformal_martingale` | `position_bias` | low | 30 | 0.633 | 1574 | 0.000 |
| `gate_blindness` | `position_bias` | medium | 30 | 0.967 | 13 | 0.000 |
| `l1_only` | `position_bias` | medium | 30 | 1.000 | 13.0 | 0.000 |
| `oracle` | `position_bias` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `position_bias` | medium | 30 | 1.000 | 203.0 | 0.733 |
| `conformal_martingale` | `position_bias` | medium | 30 | 1.000 | 30.0 | 0.000 |
| `gate_blindness` | `position_bias` | mid_low | 17 | 0.000 | -- | 0.000 |
| `l1_only` | `position_bias` | mid_low | 17 | 0.059 | 2490 | 0.000 |
| `oracle` | `position_bias` | mid_low | 17 | 1.000 | 0 | 0.000 |
| `ks_conf` | `position_bias` | mid_low | 17 | 1.000 | 203 | 0.733 |
| `conformal_martingale` | `position_bias` | mid_low | 17 | 0.941 | 649.0 | 0.000 |
| `gate_blindness` | `position_bias` | subthreshold | 30 | 0.000 | -- | 0.000 |
| `l1_only` | `position_bias` | subthreshold | 30 | 0.000 | -- | 0.000 |
| `oracle` | `position_bias` | subthreshold | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `position_bias` | subthreshold | 30 | 0.700 | 203 | 0.733 |
| `conformal_martingale` | `position_bias` | subthreshold | 30 | 0.000 | -- | 0.000 |
| `gate_blindness` | `position_drift` | medium | 30 | 0.767 | 1101 | 0.000 |
| `l1_only` | `position_drift` | medium | 30 | 1.000 | 1037.0 | 0.000 |
| `oracle` | `position_drift` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `position_drift` | medium | 30 | 1.000 | 590.5 | 0.733 |
| `conformal_martingale` | `position_drift` | medium | 30 | 1.000 | 1278.5 | 0.000 |
| `gate_blindness` | `speed_bias` | medium | 30 | 0.000 | -- | 0.000 |
| `l1_only` | `speed_bias` | medium | 30 | 0.000 | -- | 0.000 |
| `oracle` | `speed_bias` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `speed_bias` | medium | 30 | 1.000 | 203.0 | 0.733 |
| `conformal_martingale` | `speed_bias` | medium | 30 | 0.033 | 6 | 0.000 |
| `gate_blindness` | `speed_stuck` | medium | 30 | 0.000 | -- | 0.000 |
| `l1_only` | `speed_stuck` | medium | 30 | 0.000 | -- | 0.000 |
| `oracle` | `speed_stuck` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `speed_stuck` | medium | 30 | 0.533 | 203.0 | 0.733 |
| `conformal_martingale` | `speed_stuck` | medium | 30 | 0.000 | -- | 0.000 |
