# STEP 6 -- decision (heldout)

Runs: 150 (30 seeds x 5 arms). Code at `c2b1d39`.
Seeds excluded from ratios (clean alarm rate 0): 0.

## Verdicts (preregistration §5)

- **H-indep: SUPPORTED**
- **H-freeze: SUPPORTED**
- **H-noise: REFUTED**

## Paired alarm-rate ratio to clean (median over seeds, 95 % bootstrap interval)

| arm | median | 95 % interval | n |
|---|---:|---|---:|
| dropout | 0.000 | [0.000, 0.022] | 30 |
| dropout_noL8 | 0.003 | [0.000, 0.013] | 30 |
| stuck | 0.000 | [0.000, 0.002] | 30 |
| stuck_noise | 0.000 | [0.000, 0.000] | 30 |

## Per-arm medians (descriptive)

| arm | alarm rate | score p50 | score p95 | score sd | est. speed sd | mean abs speed gap (m/s) | L1 unhealthy (runs) |
|---|---:|---:|---:|---:|---:|---:|---:|
| clean | 0.0570 | 3.6890 | 3.7030 | 0.0095 | 0.18763 | 0.01 | 0/30 |
| dropout | 0.0000 | 3.6778 | 3.6919 | 0.0085 | 0.00000 | 12.22 | 30/30 |
| dropout_noL8 | 0.0002 | 3.6707 | 3.6888 | 0.0090 | 0.00000 | 11.91 | 30/30 |
| stuck | 0.0000 | 3.6759 | 3.6897 | 0.0072 | 0.00000 | 11.95 | 0/30 |
| stuck_noise | 0.0000 | 3.6758 | 3.6891 | 0.0075 | 0.00864 | 11.95 | 0/30 |
