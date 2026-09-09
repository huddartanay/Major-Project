# Phase 2 — Monitorability M(f, p): pre-registration

**Written 9 September 2026. Committed before any value of M was computed.**
**Zero new compute. Runs entirely on data already recorded by E18-R3 and E18-R3c.**

---

## 1 · The question

ASTRA 2.0 proposes a **monitorability metric** whose stated job is to

> predict whether a stage's decision statistic has the dynamic range and stability to support a
> reliable threshold, before deployment.

That proposal is currently unsupported. This experiment asks one falsifiable question:

> **Does M(f, p) predict the operational alarm rate that was actually observed in cell (f, p)?**

It is designed so that a negative answer is informative and publishable. E18 already established
that discriminability does **not** predict operational detection — `D_L1` against detection gave
ρ = −0.480, p = 0.0088, i.e. anti-correlated. If M does no better, then the monitorability metric
is not carrying its weight and **that part of the ASTRA 2.0 proposal should be deleted rather than
defended.** E18-R3 recorded this explicitly as the point of Phase 2: it is "still able to delete a
large part of the ASTRA 2.0 proposal".

## 2 · Why the definition has to be phase-aware

E18-R3c established that detection is **time-dependent**: `imu_dropout` alarms at 99.1 % in R3b's
late window and 0.2 % in R3c's, on the same seeds and the same threshold, the only difference being
whether the fault ever ends. A metric that returns one number per fault cannot distinguish those two
situations and would therefore be scored against an outcome it has no way to represent.

So M is defined per **(fault, phase)** cell, on the phase boundaries R3c already used, so that the
two are directly comparable and no boundary is chosen after seeing a result.

## 3 · Frozen definition

For fault `f` and phase `p` (a tick interval measured from fault onset):

```
                median_{runs, ticks in p} ( score_f )  −  mu_clean
    M(f, p)  =  ─────────────────────────────────────────────────
                                 sigma_between_clean
```

where

- `score_f` is the per-tick non-conformity score from
  `E18_R3c/raw_results/tick_series.json`, the same series the alarm rates were computed from;
- `mu_clean` is the mean of the per-run clean means (`mean_3200`) over the 60 clean runs in
  `E18_R3/raw_results/long_runs.json`;
- `sigma_between_clean` is the **standard deviation across those 60 per-run clean means**.

**The denominator is between-run, not within-run, and that is the whole point.** E18-R1, R2 and R3
established that the binding obstacle was never within-run noise — it was that each run's baseline
sits at its own level, so a threshold frozen across runs must survive between-run drift. A
monitorability metric that divided by within-run spread would be measuring a quantity that was
already known not to be the constraint. Using the median inside the cell rather than the mean is for
robustness: the score series contains recovery transients with large excursions, and a mean would
let a handful of ticks speak for a phase.

**Phases**, exactly as in E18-R3c, ticks from fault onset at tick 200:

| phase | ticks |
|---|---|
| P-early | 200–399 |
| P-mid | 400–999 |
| P-late | 1000–1999 |
| P-tail | 2000–3399 |

**Faults**: the six E18 classes at `medium` severity — `position_bias`, `position_drift`,
`imu_dropout`, `lateral_noise`, `speed_bias`, `speed_stuck`.

This gives **6 × 4 = 24 cells**.

## 4 · The outcome M is scored against

The observed **per-tick alarm rate** in the same cell, computed from the same series against the
frozen threshold **3.7024** (v3, from `E18_R2/processed_results/verdict.json`, not recomputed here).

M is computed from the score *level*; the outcome is computed from *threshold crossings*. These are
related but not identical, and the point of the test is whether the first predicts the second across
cells that differ in fault mechanism and phase.

## 5 · Frozen decision rule

Primary test: **Spearman ρ between M(f, p) and the observed alarm rate, over the 24 cells**, with a
permutation p-value from `benchmarks.e17_stats.spearman`.

| ρ | p | verdict |
|---|---|---|
| ≥ 0.70 | < 0.05 | **M PREDICTS** — the metric earns its place in ASTRA 2.0 |
| 0.40 – 0.70 | < 0.05 | **M IS WEAK** — reported as partial; not claimed as a design justification |
| < 0.40, or p ≥ 0.05 | — | **M FAILS** — the monitorability metric is withdrawn from the ASTRA 2.0 proposal |

Secondary, reported whatever the primary says:

1. **Against the incumbent.** The same ρ computed for `D_s` on the same cells where E17 supplies it.
   M is only worth having if it beats a number we already had. If M fails *and* `D_s` fails, the
   honest statement is that neither predicts detection.
2. **A conservative independence check.** The 24 cells are **not independent** — four phases share a
   fault, and the same 30 seeds appear in every cell. So ρ is recomputed on the 6 per-fault medians
   (n = 6). This is badly underpowered and is reported as a robustness direction, **not** as a second
   test to pick from. Ticks are never treated as samples anywhere in this analysis.

## 6 · What would make this analysis invalid

Declared in advance, so that finding one of them later is a withdrawal and not a judgement call:

- Using any detection outcome while choosing the form of M, its denominator, or the phase edges.
  The definition above is frozen by this commit and will not be amended after a value is seen.
- Reporting only the cells or the phase split that happen to correlate.
- Treating the 24 cells as independent when quoting the primary p-value. §5.2 exists for this.
- Quoting M as a property of a *fault* rather than of a *(fault, phase)* cell.

## 7 · What this cannot establish either way

- Nothing about P2 or P3; every run here is P1.
- Nothing about severities other than `medium`.
- Nothing causal. A correlation between M and alarm rate across cells would say M is a usable
  predictor on this plant, not that low monitorability *causes* missed detection.
- Nothing external. `[M-syn]` throughout; `[M-ext]` remains 0 of 30.
- Nothing about *why* the estimator behaves as it does. This is a re-analysis of recorded monitor
  output, and adds no instrumentation to L2.

## 8 · Prediction, recorded before running

Stated so that it can be wrong in public. Given that R3c showed `imu_dropout` sitting *below* its
clean baseline while faulted, its M should be near zero or negative in every phase, and its alarm
rate is ~0.002 — those agree. The risk to M is `position_drift`, whose alarm rate climbs across
phases as drift accumulates; if M tracks that climb, M is doing real work, and if it does not, M is
mostly re-describing `position_bias`'s large constant offset.

**Expectation: M passes at the "weak" level, ρ ≈ 0.5–0.75.** I expect it to beat `D_s`, because
`D_s` is computed on whole runs and cannot represent phase at all, and to fall short of 0.9 because
score level and threshold-crossing rate come apart whenever the baseline drifts.
