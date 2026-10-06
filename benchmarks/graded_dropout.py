"""Graded IMU dropout injector for Stage C1b (sensor-loss magnitude sweep).

The shipped ``training.faults.dropout`` is all-or-nothing over its window.
Stage C1's WALK_AWAY_OR_SHIFT verdict on parameterised faults left the
sensor-loss regime -- where G2's compelling case lives -- untested at
sub-100 % magnitudes. This module extends the fault library, in
``benchmarks/`` per handoff §14, with a factory that produces a
``FaultInjector`` whose IMU dropout probability is a knob.

Design
------
The all-or-nothing DROPOUT spec covers a tick range. To vary the
probability without touching ``src/astra/`` or the shipped ``FaultSpec``
contract, we generate a *set* of single-tick DROPOUT specs by
Bernoulli-sampling under a seeded RNG. The resulting ``FaultInjector``
reports the same interface -- ``corrupt()`` returns ``None`` on dropped
ticks -- and every existing consumer (the pipeline, the C2 evaluator, the
mechanism logger) works unchanged.

Ground truth ("was a tick dropped?") is captured in the returned
`FaultInjector.episodes` after the run; the runner records per-run
dropout fraction from that so an analysis can distinguish an intended
50 % rate from an achieved 47 %.
"""

from __future__ import annotations

import random

from training.faults import FaultInjector, FaultSpec, FaultKind


def graded_dropout_injector(
    *,
    first_tick: int,
    last_tick: int,
    probability: float,
    seed: int,
    sigmas: dict,
) -> FaultInjector:
    """Return a FaultInjector whose IMU dropout fires with the given probability.

    ``probability = 1.0`` reproduces the shipped ``dropout()`` behaviour;
    ``probability = 0.0`` returns an empty injector (all-clean run). Every
    intermediate value samples each tick i.i.d. under a stream keyed off
    ``seed`` xor ``first_tick``, so re-runs at the same (seed, first_tick,
    probability) triple are bit-identical.

    Args:
        first_tick: First tick of the window, inclusive.
        last_tick: Last tick of the window, inclusive.
        probability: Per-tick dropout probability, in [0.0, 1.0].
        seed: The run's seed; the RNG stream is derived deterministically.
        sigmas: The channel sigmas the injector will pass through.

    Returns:
        A ``FaultInjector`` armed with single-tick DROPOUT specs on the
        ticks the RNG selected.
    """
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"probability must be in [0, 1], got {probability!r}")
    if first_tick > last_tick:
        raise ValueError(f"first_tick {first_tick} must be <= last_tick {last_tick}")
    # RNG derived from seed + first_tick so two calls with different windows
    # do not draw the same stream. Standard-library random for stdlib-only
    # determinism (no numpy dependency in the injector path).
    rng = random.Random(seed ^ (first_tick * 0x9E3779B1))
    specs: list[FaultSpec] = []
    for tick in range(first_tick, last_tick + 1):
        if rng.random() < probability:
            specs.append(
                FaultSpec(
                    kind=FaultKind.DROPOUT,
                    first_tick=tick,
                    last_tick=tick,
                )
            )
    return FaultInjector(tuple(specs), seed=seed, sigmas=sigmas)
