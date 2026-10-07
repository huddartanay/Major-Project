# STEP 7 -- decision (dev)

Runs: 150. Code at `109beea`. Threshold tau = 9.189672.

## Outcome: **G1-ARTEFACT**

## Preconditions

- P-cal: 30/30 clean runs with alarm rate in [0.025, 0.10] -> **PASS** (clean median 0.0502, min 0.0423, max 0.0610)
- P-sens: position_bias is DETECTS -> **PASS**
- Seeds excluded from ratios (clean alarm rate 0): 0

## Paired alarm-rate ratio to clean

| arm | median | 95 % interval | n | class |
|---|---:|---|---:|---|
| dropout | 1.758 | [0.502, 3.387] | 30 | **UNCHANGED** |
| dropout_noL8 | 2.867 | [1.480, 7.843] | 30 | **DETECTS** |
| stuck | 5.235 | [2.173, 9.904] | 30 | **DETECTS** |
| position_bias | 11.002 | [7.569, 17.569] | 30 | **DETECTS** |

## Per-arm medians (descriptive)

| arm | alarm rate | s_lat p50 | s_lat p95 | s_lat sd | steer proposal sd | steer twin sd | mean abs speed gap | L1 unhealthy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean | 0.0502 | 8.4707 | 9.1899 | 0.5153 | 0.00173 | 0.00148 | 0.01 | 0/30 |
| dropout | 0.0837 | 8.4906 | 9.2824 | 0.7332 | 0.00114 | 0.00011 | 11.32 | 30/30 |
| dropout_noL8 | 0.1465 | 8.5891 | 9.4443 | 0.7664 | 0.00126 | 0.00011 | 11.03 | 30/30 |
| stuck | 0.2392 | 8.8898 | 9.5938 | 0.6082 | 0.00092 | 0.00009 | 11.03 | 0/30 |
| position_bias | 0.5827 | 18.0475 | 22.8802 | 5.1004 | 0.00800 | 0.00469 | 0.01 | 30/30 |
