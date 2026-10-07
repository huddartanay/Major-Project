# STEP 7 -- decision (heldout)

Runs: 150. Code at `7f2c35b`. Threshold tau = 9.189672.

## Outcome: **MIXED / INCONCLUSIVE**

## Preconditions

- P-cal: 30/30 clean runs with alarm rate in [0.025, 0.10] -> **PASS** (clean median 0.0488, min 0.0403, max 0.0603)
- P-sens: position_bias is DETECTS -> **PASS**
- Seeds excluded from ratios (clean alarm rate 0): 0

## Paired alarm-rate ratio to clean

| arm | median | 95 % interval | n | class |
|---|---:|---|---:|---|
| dropout | 0.685 | [0.109, 6.151] | 30 | **INCONCLUSIVE** |
| dropout_noL8 | 2.155 | [0.611, 9.242] | 30 | **INCONCLUSIVE** |
| stuck | 5.198 | [0.919, 9.061] | 30 | **INCONCLUSIVE** |
| position_bias | 17.223 | [11.545, 18.293] | 30 | **DETECTS** |

## Per-arm medians (descriptive)

| arm | alarm rate | s_lat p50 | s_lat p95 | s_lat sd | steer proposal sd | steer twin sd | mean abs speed gap | L1 unhealthy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0.0488 | 8.4682 | 9.1854 | 0.5126 | 0.00177 | 0.00150 | 0.01 | 0/30 |
| dropout | 0.0285 | 8.5781 | 9.1014 | 0.7378 | 0.00117 | 0.00011 | 11.58 | 30/30 |
| dropout_noL8 | 0.1028 | 8.6304 | 9.4022 | 0.7473 | 0.00122 | 0.00011 | 11.43 | 30/30 |
| stuck | 0.2655 | 8.8506 | 9.6070 | 0.6362 | 0.00094 | 0.00009 | 11.43 | 0/30 |
| position_bias | 0.8003 | 20.6524 | 23.1295 | 5.3873 | 0.00826 | 0.00593 | 0.01 | 30/30 |
