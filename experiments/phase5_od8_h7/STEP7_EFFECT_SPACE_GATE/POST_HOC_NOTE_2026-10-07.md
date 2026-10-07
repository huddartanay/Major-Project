# Post-hoc note on STEP 6 and STEP 7 — L8 reaches HALT in some frozen-sensor runs

**7 October 2026. Descriptive, from the committed `per_run_*.json`; no new run. Does not change any
pre-registered verdict.**

## Observation

Runs (of 30) in which L8 was in HALT for essentially the whole evaluation window (ticks 400–3399):

| study | split | `stuck` | `dropout_noL8` | `clean` |
|---|---|---:|---:|---:|
| STEP 6 | dev | 10 | 8 | 0 |
| STEP 6 | held-out | 8 | 7 | 0 |
| STEP 7 | dev | 10 | 8 | 0 |
| STEP 7 | held-out | 10 | 8 | 0 |

In those runs the HALT share of ticks is 0.94–1.00, so the stop happens before tick 400. In the remaining
runs the state is NOMINAL throughout. L1 reported unhealthy in 0 of 30 `stuck` runs, so the stop did not
come from frame health; `dropout_noL8` has the integrity thresholds neutralised. The cause is therefore a
gate verdict (out-of-distribution counter), and which gate is **not identified**.

## Consequences

1. The sentence "nothing in the stack notices a frozen sensor" was too strong. Correct statement: L1
   never flags it; the shipped L6 score is suppressed; in about two thirds of runs the stack stays NOMINAL
   while true speed is 0–2 m/s and estimated speed is about 11.5 m/s; in about one third L8 halts.
2. STEP 7's pre-registration called `stuck` and `dropout_noL8` "the two arms where L8's stop does not
   confound". **That assumption does not hold for these runs.** In STEP 7 held-out `stuck`, the 10 HALT
   runs have a corrected-score alarm rate of exactly 1.0 (7 runs) or ≈ 0.0 (3 runs); the per-seed
   bimodality reported in `final_decision.md` is partly this. Among the 20 non-HALT runs the alarm rate
   ranges 0.007–0.56 against a clean median of 0.049, so the spread is not only the HALT runs.
3. STEP 8 must record the L8 state and the first blocking gate per tick, and analyse HALT and non-HALT runs
   separately (or censor at the first HALT tick).

## Not known

Which gate vetoes in the HALT runs; why those seeds and not the others; whether the same seeds halt in
both arms.
