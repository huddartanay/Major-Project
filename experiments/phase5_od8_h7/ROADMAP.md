# ASTRA Roadmap - Phase 5 and beyond

**Updated 1 September 2026.** Stages are gated. A stage is not entered because it exists here.

## Current position

    E17  fault observability            COMPLETE - heterogeneous; 1 of 6 well-posed absorption
    E17-Position  corrected injection   COMPLETE - absorption withdrawn, 0 of 12 cells
    E18  OD-8 calibration               COMPLETE - verdict revised; P1 withdrawn
    E18-R1  run-local calibration       COMPLETE - FAIL-P3; found E18 window defect
    E18-R2  matched-window calibration  COMPLETE - PARTIAL-R2; obstacle is the score process
    E18-R3  longer evaluation windows   COMPLETE - PASS. P1 30/30 at 160 s
    E18-R3b detection at the long window <-- NEXT, and blocking
    E19  H7 monitor placement           UNBLOCKED for P1, pending R3b
    E20  lying sensor                   FUTURE
    comma2k19 / highD / CARLA           NOT STARTED, correctly

## The blocking chain

    a calibrated monitor
        -> operational detection that means something
            -> monitor placement (H7 / E19)
                -> external validation (comma2k19, highD)
                    -> adversarial extension (E20)
                        -> closed-loop validation (CARLA)

**Nothing below the first line can proceed until it is satisfied.** E18-R1 established that it is
not currently satisfied for any policy on the evaluation window.

## E18-R2 - the immediate next experiment

**Question:** does pooled calibration on the *matched* window (ticks 200-399) produce per-run-stable
false-alarm behaviour?

**Why this and not something else:** R1 failed on estimator variance, not on window matching. E18
failed on window mismatch, not on sample size. E18-R2 is the only untested combination - large
sample, correct window. One experiment, no search, about four minutes of compute since the runs
already exist.

**Frozen criterion:** >= 24/30 runs in band for P1, the positive control, reported for P3.

**If E18-R2 fails**, the honest conclusion is that the current OD-8 formulation cannot support a
per-run-stable operational monitor at this eps on this plant, and the contribution reframes around
that demonstrated limitation rather than around monitor placement.

## What is not on the roadmap

Additional fault families, additional datasets, and any adversarial work, until the calibration
question is closed. More datasets do not increase novelty and cannot substitute for a working
measurement instrument.


## Update, 1 September 2026 - the E18 calibration series is closed

Three calibration schemes have been tried and the obstacle is now identified:

| scheme | P1 runs in band | P3 runs in band |
|---|:--:|:--:|
| v1 pooled, whole run | 4/30 | 5/30 |
| v2 run-local windowed | 3/30 | 9/30 |
| v3 pooled, matched window | **13/30** | 2/30 |
| *ideal independent monitor* | *29.2/30* | *29.2/30* |

**The limit is the score process, not the threshold.** P1's alarms cluster within runs (lag-1
autocorrelation +0.359, ~11 effective ticks of 200); P3's baseline varies between runs (~2 effective
ticks). Each scheme that addresses one mechanism aggravates the other. **No further calibration
variant is warranted.**

### E18-R3 - longer evaluation windows

A pure compute change: extend runs so the evaluation window carries the independent information a
200-tick window does not. At ~11 effective ticks per 200, matching an independent 200-tick monitor
implies roughly 3,600 ticks. This separates "not enough samples" from "wrong monitor" for both
policies at once, and needs no new rule pre-registered.

If R3 recovers P1, the finding is a precision limit and E19 becomes possible. If it does not, the
contribution reframes around the demonstrated limitation:

> A conformal score that separates faulted from clean runs at high AUC can still fail to support a
> per-run-stable operational monitor, because its alarm process is temporally clustered and its
> baseline varies between runs. Statistical discriminability, calibration validity and operational
> stability are three distinct properties.


## Update, 3 September 2026 — E18-R3 passed

**The evaluation window was the binding variable all along.**

| policy | n=200 | n=800 | n=3200 (160 s) |
|---|:--:|:--:|:--:|
| P1 | 12/30 | 21/30 | **30/30** |
| P3 | 2/30 | 6/30 | 5/30 (bias, not variance) |

The E18-R2 conclusion is **superseded**. "OD-8 cannot deliver per-run-stable false alarms" was true
only on 200-tick windows, and that qualifier was load-bearing. At 160 seconds of driving — an
ordinary engineering requirement — P1 has a valid operational monitor.

### E18-R3b is now the gate

R3 measured **clean data only**. A monitor with perfect false-alarm control and no detection is
still useless, and E18 found `speed_stuck` and `imu_dropout` undetectable at any severity on the
short window. **R3b re-runs the faulted evaluation at n = 3200 against the frozen threshold.** It
decides whether the PASS is worth anything.

Only after R3b does E19 become genuinely worth running.


## Update, 9 September 2026 — the E18 series is closed and Phase 2 has cut a claim

    E18-R3b  detection at the long window     COMPLETE - superseded by R3c
    E18-R3c  duration-matched control         COMPLETE - H-AFTERMATH SUPPORTED, terminal for E18
    Phase 2  monitorability re-analysis       COMPLETE - M IS WEAK; location-only form withdrawn
    E21      baseline comparison              <-- RUNNING, and now the gate on E19
    E19      H7 monitor placement             pre-register only after E21
    E20      lying sensor                     FUTURE

**Phase 2 did the job it was kept on the roadmap for.** It was retained because it was "still able
to delete a large part of the ASTRA 2.0 proposal", and it deleted the location-only monitorability
metric: M reads sustained `imu_dropout` as mildly elevated while the monitor runs 25x quieter than
its own clean baseline. The phase-aware framing survives and is vindicated; the location-only
statistic does not.

### Why E21 now gates E19

E19 asks **where to place a monitor**. E18-R3c says the monitor we have is blind to sustained sensor
failure, and a live observation showed L1 reporting `IMU=DEGRADED` and L3's Trust Index at 0.06 on a
tick where L6 returned `PASS`.

If a one-line health check detects what the conformal gate misses, then the placement question
changes shape entirely — and designing E19 first would mean measuring placement for a monitor that
should not be the one being placed. E21 is paired with R3c, uses detectors that have been committed
since P2.7 with untouched thresholds, and costs about an hour.

**Nothing new is added to the roadmap by this update.** E21 was always implied by the negative
result; it had simply never been run.
