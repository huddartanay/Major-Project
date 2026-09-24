# E21 — Baseline comparison: does OD-8 beat the detectors we already had?

**Written 9 September 2026. Committed before any run.**
**Paired with E18-R3c: same seeds, same faults, same sustained injection, same 3,400 ticks.**

---

## 1 · The question

E18-R3c established that under sustained injection the conformal monitor detects **3 of 6** faults,
and is *quieter than its own clean baseline* during `imu_dropout` for 160 continuous seconds.

That result has never been compared against anything. `benchmarks/detectors.py` has held three
simple detectors since P2.7, one of which its own docstring calls **"the principled candidate"**, and
no recorded experiment has ever run them against OD-8.

> **Do the pre-existing simple detectors detect the faults OD-8 misses, at an acceptable
> false-alarm rate?**

This is the first question a reviewer asks about a negative monitoring result, and it is currently
unanswered. It is also the question most able to change what this work is about.

## 2 · Why it might reframe the contribution

A live 300-tick observation recorded during demo work showed, on a single tick under `imu_dropout`:

    L1 sensing      IMU=DEGRADED
    L3 trust        Trust Index +0.06
    L6 conformal    PASS

If that generalises, **the evidence for the fault was already present in the pipeline, two layers
before the gate that missed it.** The finding would then not be "conformal monitoring is blind" but
"the fault evidence was available upstream and the gate does not consult it" — a claim about
architecture rather than about conformal prediction, and a stronger one.

Pre-registering this reading so it cannot be invented after the numbers arrive.

## 3 · Design

| | |
|---|---|
| Policy | P1 (`synthetic.pt`) — the only policy R3c covers |
| Faults | the six E18 classes at `medium` severity |
| Injection | **sustained** — opens at tick 200, never closes, exactly as R3c |
| Ticks | 3,400 |
| Seeds | 30, `BASE_SEED = 20260731`, the same seeds R3c used |
| Clean arm | 30 clean runs, same seeds, same length |
| Total | 180 faulted + 30 clean = 210 runs |

## 4 · The detectors, and why they are fair comparators

From `benchmarks/detectors.py`, unmodified:

| detector | condition | threshold |
|---|---|---|
| `health` | any modality worse than `HEALTHY` | — |
| `innovation` | fast innovation above ceiling | `_INNOVATION_CEILING = 3.0` |
| `trust` | Trust Index below floor | `_TRUST_FLOOR = 0.80` |

All three fire only after **`PATIENCE = 5` consecutive** qualifying ticks.

**These thresholds are pre-existing.** They were set during P2.7, are committed, and are **not
tuned for this experiment**. No threshold will be adjusted after seeing a result; if a baseline
performs badly at its existing threshold, that is the reported outcome.

**The comparison is not symmetric, and the asymmetry is stated up front.** OD-8 carries a conformal
calibration guarantee; these three are fixed thresholds with none. A fixed threshold can win on
detection simply by firing constantly, which is why detection is only counted when the clean-arm
false-positive requirement is also met (§6). Conversely OD-8's run-level rule from R3c and the
`PATIENCE = 5` rule here are **different rules**, and no claim will merge them: each is reported
against its own criterion, and the comparison is between *outcomes*, not between rule mechanics.

## 5 · Metrics

Per (detector × fault), over the 30 seeds:

- **Run-level detection rate** — the fraction of runs where the detector fired at any point after the
  fault opened. The run is the unit; ticks are never treated as samples.
- **Median latency**, in ticks from fault onset to first firing.
- **Clean false-positive rate** — the fraction of the 30 *clean* runs where the detector fired at all.

OD-8's comparator numbers are taken from E18-R3c as recorded and are **not recomputed**:

| fault | OD-8 run-level detection, sustained |
|---|--:|
| `position_bias` | 100 % |
| `position_drift` | 100 % |
| `lateral_noise` | 100 % |
| `speed_stuck` | 37 % |
| `speed_bias` | 0 % |
| `imu_dropout` | 0 % |

## 6 · Frozen decision rule

A detector **detects** fault `f` when, on that fault:

    run-level detection rate  >= 0.90     AND     clean false-positive rate <= 0.10

The 0.90 bar is R3c's, reused so the two experiments are read on the same scale. The 0.10 clean bar
exists so that a detector cannot win by firing all the time.

**Primary outcome.** Does any baseline detect at least one of the three faults OD-8 misses —
`imu_dropout`, `speed_bias`, `speed_stuck`?

| result | verdict |
|---|---|
| a baseline detects ≥ 1 of the three, within the clean bar | **BASELINE WINS** — the contribution reframes around architecture: the evidence was upstream and unused |
| no baseline detects any of the three | **OD-8 HOLDS** — the blind spot is a property of the fault class, not of the gate, and OD-8's negative result stands on its own |
| a baseline detects some, but breaches the clean bar | **BASELINE IS TRIGGER-HAPPY** — reported as a false-alarm/detection trade, no reframing claimed |

**Secondary, reported regardless:** total faults detected by each detector, out of 6, against OD-8's
3; and latency, because a detector that fires eventually but far too late is a different failure from
one that never fires.

## 7 · What would invalidate this

- Adjusting any detector threshold after seeing a result. The three thresholds are frozen by this
  commit at their committed values.
- Using a different seed set, fault set, or run length from R3c's, which would break the pairing that
  makes the comparison meaningful.
- Reporting detection without the paired clean false-positive rate.
- Concluding anything about conformal prediction *as a method*. This compares one conformal monitor
  as configured in this repository against three fixed thresholds on one plant.

## 8 · What it cannot establish

- Nothing about P2 or P3; P1 only.
- Nothing about severities other than `medium`.
- Nothing external. `[M-syn]` throughout; `[M-ext]` remains 0 of 30.
- Nothing about whether a *calibrated* version of these baselines would do better. That is a
  different experiment.
- No causal claim. A baseline that detects a fault OD-8 misses shows the evidence was present and
  usable, not that any particular redesign will work.

## 9 · Prediction, recorded before running

**I expect BASELINE WINS, on `imu_dropout`, via `health` and `trust`.**

The reasoning is mechanical rather than hopeful: `imu_dropout` sets a modality to something other
than `HEALTHY`, which is `health`'s condition almost by definition, and the observed Trust Index of
0.06 is far below the 0.80 floor. Both should fire within `PATIENCE` ticks and stay fired, giving
detection near 100 % and latency near 5 ticks.

I expect **both speed faults to defeat every detector**, because neither disturbs stream health, and
a pilot measurement showed the twin barely moves under them — so there is little reason for the
innovation to move either.

I expect `health` to have a **clean false-positive rate near zero** and `trust` to be the risk: a
Trust Index that dips below 0.80 transiently on clean runs for 5 consecutive ticks would breach the
clean bar and turn a win into "trigger-happy".

**If this prediction is right, the honest headline becomes: the conformal gate missed a fault that a
one-line health check catches, because the gate reads the estimate rather than the sensors.**
