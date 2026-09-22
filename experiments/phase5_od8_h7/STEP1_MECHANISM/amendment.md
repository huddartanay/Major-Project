# Amendment 1 — fault list brought into line with the pre-reg's definition

**Written 22 September 2026, before any run whose output survives to the analysis.**

## The change

`stage_a_run.py`'s `FAULTS` tuple originally read:

```python
FAULTS = ("imu_dropout", "imu_bias", "lateral_noise",
          "position_bias", "position_drift", "speed_bias")
```

It now reads:

```python
FAULTS = ("imu_dropout", "lateral_noise", "position_bias",
          "position_drift", "speed_bias", "speed_stuck")
```

## Why this is not a change to the pre-registration

`preregistration.md` §2 defines the fault set by reference: *"matches R3c's
set"*. R3c's set — read from `benchmarks/e18r3c_sustained.py`'s iteration over
`SEVERITIES` — is the second tuple, not the first. The original runner
constant was a mistranscription: `imu_bias` has no entry in `SEVERITIES` at
all and was skipped with a warning; `speed_stuck` (which R3c does run) was
missing.

The pre-registered *definition* of the fault set has not moved. Bringing the
runner into line with it is the same kind of change as fixing a typo in a
variable name.

## What survives from the aborted pre-amendment run

Nothing. The first sweep was killed after four runs (`imu_dropout` seeds
20260731 and 20260732, both arms) so no partial JSONL from it may enter the
analysis. `raw_results/` starts empty for the amended sweep.

## Everything else in the pre-registration stands

- Frozen v3 threshold `P1 = 3.7024`. Unchanged.
- Dev seeds `20260731 + i` for `i ∈ [0, 30)`; held-out seeds `20261201 + i`.
  Unchanged.
- Three hypotheses, the pre-committed ratio bounds, the one-sentence decision
  rule in §5. Unchanged.
- The tick logger's schema. Unchanged.

## Authorised by

Tanay Huddar, primary author, 22 September 2026, in the same session that
drafted the pre-registration. Sushanth C unavailable at time of write;
review will follow when he is back.
