# STEP 6 -- decision (dev)

Runs: 150 (30 seeds x 5 arms). Code at `d1f6144`.
Seeds excluded from ratios (clean alarm rate 0): 0.

## Verdicts (preregistration §5)

- **H-indep: SUPPORTED**
- **H-freeze: SUPPORTED**
- **H-noise: REFUTED**

## Paired alarm-rate ratio to clean (median over seeds, 95 % bootstrap interval)

| arm | median | 95 % interval | n |
|---|---:|---|---:|
| dropout | 0.002 | [0.000, 0.013] | 30 |
| dropout_noL8 | 0.000 | [0.000, 0.016] | 30 |
| stuck | 0.000 | [0.000, 0.008] | 30 |
| stuck_noise | 0.000 | [0.000, 0.006] | 30 |

## Per-arm medians (descriptive)

| arm | alarm rate | score p50 | score p95 | score sd | est. speed sd | mean abs speed gap (m/s) | L1 unhealthy (runs) |
|---|---:|---:|---:|---:|---:|---:|---:|
| clean | 0.0580 | 3.6893 | 3.7031 | 0.0093 | 0.12966 | 0.01 | 0/30 |
| dropout | 0.0002 | 3.6795 | 3.6927 | 0.0089 | 0.00000 | 11.32 | 30/30 |
| dropout_noL8 | 0.0000 | 3.6767 | 3.6912 | 0.0094 | 0.00000 | 11.03 | 30/30 |
| stuck | 0.0000 | 3.6747 | 3.6892 | 0.0075 | 0.00000 | 11.03 | 0/30 |
| stuck_noise | 0.0000 | 3.6744 | 3.6882 | 0.0074 | 0.00863 | 11.04 | 0/30 |
