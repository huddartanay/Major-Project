# Stage C2 observations (dev; C1 in flight) — not a verdict amendment

`final_decision_dev.md` records the primary verdict — **PASS** per
`preregistration.md` §5. This file records what the per-(monitor, fault,
magnitude) table shows *beyond* the primary rule, and known issues in the
baseline implementations. It does not amend the primary result.

## 1 · G2 is upper-bounded by L1 on detection rate

`GateBlindnessMonitor` requires L1 to fire before it can fire — its condition
is "L1 fires AND L6 stays silent". So on any cell where L1 misses, G2 misses
too. That is not a bug: the paper's claim is not that G2 catches more faults
than L1, but that G2 correctly *identifies gate-blindness episodes* -- the
subset of L1-detected cases where L6 fails to react.

On the Stage A dev raw for `imu_dropout` at medium: G2 detected 30/30 with
5-tick latency, same as L1. That is the pattern the whole story rests on --
L1 fires, L6 doesn't, so G2 correctly flags a blind gate on every run.

Where L6 responds to a fault L1 also sees (e.g. `position_bias medium`, one
of 30 runs), G2 correctly does not flag: 29/30 vs L1's 30/30. This is the
one-run difference between "L1 detected the fault" and "the gate was blind
to it".

## 2 · KS(conf) clean false-alarm rate is 0.733 — an implementation issue

The KS baseline's Bonferroni correction divides alpha by `tests_run` at each
call. On a 3,400-tick run with ref_window=200 that yields ~3,000 tests, so
the first few tests use a loose alpha (0.05, 0.025, ...) and can fire on a
clean stream. A correct sequential correction would fix alpha_effective for
a bounded family of tests, e.g. alpha / expected_tests, or use a step-down
procedure such as Bonferroni-Holm keyed on the a-priori test count.

The pre-registration does not name a specific correction scheme, so this is
a fixable engineering defect, not a design change. Noting rather than
patching now because (a) KS is not the paper's contribution and (b) even a
patched KS is expected to fire on lateral_noise / position_drift (real
distributional shifts) and correctly report the gate is behaving — that
is the "beats the field on gate-blindness cases specifically" story.

Follow-up: replace `corrected_alpha = alpha / tests_run` with a fixed
`alpha_effective = alpha / expected_tests` computed at construction from
`ticks - ref_window`, or switch to an alpha-spending function.

## 3 · Conformal martingale detects `lateral_noise` and `position_bias` but
    misses `imu_dropout`

Martingale detection rate on dev-medium: `lateral_noise` 1.000,
`position_bias medium` 1.000, `position_drift medium` 1.000, `imu_dropout`
0.033, `speed_bias` 0.033, `speed_stuck` 0.000.

This is consistent with the Stage A observation that `imu_dropout`,
`speed_bias` and `speed_stuck` do not shift the L6 score distribution --
the input to the martingale is the exchangeable stream, and the stream
does not become non-exchangeable under those faults. The martingale is a
valid detector of the shifts it can see; on the faults where L6 is
architecturally blind, it is architecturally blind too.

## 4 · What this means for the ITSC framing

The paper's contribution is:

> On the subset of faults for which the L6 gate is silent while an
> independent layer detects them, G2 flags blindness with zero clean
> false alarms and matches L1's latency. Existing label-free
> baselines (KS(conf), conformal test martingale) either false-alarm
> heavily on clean runs or share L6's blindness for the same reason.

That subset is where G2 delivers value; the paper is honest about the
cases where it does not. This shape survives whatever Stage C1 produces
at smaller magnitudes -- the primary result already stands on Stage A's
committed evidence.
