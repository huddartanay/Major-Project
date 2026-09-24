# Stage C2 -- Final Decision (dev)

**Runs evaluated:** 300 faulted, 30 clean
**Sources:** experiments/phase5_od8_h7/STEP1_MECHANISM/raw_results_heldout, experiments/phase5_od8_h7/STEP5_SENSOR_LOSS_SWEEP/raw_results_heldout

## Primary result: **PASS**

gate_blindness detection=1.000 vs l1_only 1.000; gate_blindness latency=5.0 vs l1_only 5.0; gate_blindness clean_fp=0.000 (bar 0.1)

## Clean false-alarm rate per monitor

| monitor | clean FP |
|---|---:|
| `gate_blindness` | 0.000 |
| `l1_only` | 0.000 |
| `oracle` | 0.000 |
| `ks_conf` | 0.833 |
| `conformal_martingale` | 0.000 |

## Per-(fault, magnitude) detection

| monitor | fault | magnitude | n | detection | median latency | clean FP |
|---|---|---|---:|---:|---:|---:|
| `gate_blindness` | `imu_dropout` | medium | 30 | 1.000 | 5.0 | 0.000 |
| `l1_only` | `imu_dropout` | medium | 30 | 1.000 | 5.0 | 0.000 |
| `oracle` | `imu_dropout` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `imu_dropout` | medium | 30 | 1.000 | 203.0 | 0.833 |
| `conformal_martingale` | `imu_dropout` | medium | 30 | 0.033 | 11 | 0.000 |
| `gate_blindness` | `imu_dropout` | p025 | 30 | 1.000 | 220.5 | 0.000 |
| `l1_only` | `imu_dropout` | p025 | 30 | 1.000 | 220.5 | 0.000 |
| `oracle` | `imu_dropout` | p025 | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `imu_dropout` | p025 | 30 | 0.900 | 353 | 0.833 |
| `conformal_martingale` | `imu_dropout` | p025 | 30 | 0.033 | 1391 | 0.000 |
| `gate_blindness` | `imu_dropout` | p050 | 30 | 1.000 | 18.5 | 0.000 |
| `l1_only` | `imu_dropout` | p050 | 30 | 1.000 | 17.5 | 0.000 |
| `oracle` | `imu_dropout` | p050 | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `imu_dropout` | p050 | 30 | 1.000 | 370.0 | 0.833 |
| `conformal_martingale` | `imu_dropout` | p050 | 30 | 0.867 | 1108.0 | 0.000 |
| `gate_blindness` | `imu_dropout` | p075 | 30 | 1.000 | 8.0 | 0.000 |
| `l1_only` | `imu_dropout` | p075 | 30 | 1.000 | 8.0 | 0.000 |
| `oracle` | `imu_dropout` | p075 | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `imu_dropout` | p075 | 30 | 1.000 | 203.0 | 0.833 |
| `conformal_martingale` | `imu_dropout` | p075 | 30 | 1.000 | 112.0 | 0.000 |
| `gate_blindness` | `imu_dropout` | p100 | 30 | 1.000 | 5.0 | 0.000 |
| `l1_only` | `imu_dropout` | p100 | 30 | 1.000 | 5.0 | 0.000 |
| `oracle` | `imu_dropout` | p100 | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `imu_dropout` | p100 | 30 | 1.000 | 203.0 | 0.833 |
| `conformal_martingale` | `imu_dropout` | p100 | 30 | 0.033 | 11 | 0.000 |
| `gate_blindness` | `lateral_noise` | medium | 30 | 0.000 | -- | 0.000 |
| `l1_only` | `lateral_noise` | medium | 30 | 0.000 | -- | 0.000 |
| `oracle` | `lateral_noise` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `lateral_noise` | medium | 30 | 1.000 | 203.0 | 0.833 |
| `conformal_martingale` | `lateral_noise` | medium | 30 | 1.000 | 90.5 | 0.000 |
| `gate_blindness` | `position_bias` | medium | 30 | 1.000 | 13.0 | 0.000 |
| `l1_only` | `position_bias` | medium | 30 | 1.000 | 13.0 | 0.000 |
| `oracle` | `position_bias` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `position_bias` | medium | 30 | 1.000 | 203.0 | 0.833 |
| `conformal_martingale` | `position_bias` | medium | 30 | 1.000 | 30.0 | 0.000 |
| `gate_blindness` | `position_drift` | medium | 30 | 0.967 | 1119 | 0.000 |
| `l1_only` | `position_drift` | medium | 30 | 1.000 | 1011.0 | 0.000 |
| `oracle` | `position_drift` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `position_drift` | medium | 30 | 1.000 | 559.0 | 0.833 |
| `conformal_martingale` | `position_drift` | medium | 30 | 1.000 | 1226.0 | 0.000 |
| `gate_blindness` | `speed_bias` | medium | 30 | 0.000 | -- | 0.000 |
| `l1_only` | `speed_bias` | medium | 30 | 0.000 | -- | 0.000 |
| `oracle` | `speed_bias` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `speed_bias` | medium | 30 | 1.000 | 203.0 | 0.833 |
| `conformal_martingale` | `speed_bias` | medium | 30 | 0.067 | 7.0 | 0.000 |
| `gate_blindness` | `speed_stuck` | medium | 30 | 0.000 | -- | 0.000 |
| `l1_only` | `speed_stuck` | medium | 30 | 0.000 | -- | 0.000 |
| `oracle` | `speed_stuck` | medium | 30 | 1.000 | 0.0 | 0.000 |
| `ks_conf` | `speed_stuck` | medium | 30 | 0.633 | 203 | 0.833 |
| `conformal_martingale` | `speed_stuck` | medium | 30 | 0.033 | 10 | 0.000 |
