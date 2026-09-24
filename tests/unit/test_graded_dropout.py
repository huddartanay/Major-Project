"""Tests for benchmarks.graded_dropout.

The factory returns a ``FaultInjector`` armed with per-tick DROPOUT specs
sampled at the target probability. Stage C1b's whole verdict rests on
these draws being (a) close to the target rate, (b) deterministic under
seed, and (c) confined to the requested window. This file pins those
three properties.
"""

from __future__ import annotations

import pytest

from benchmarks.discriminability import CHANNEL_SIGMAS
from benchmarks.graded_dropout import graded_dropout_injector


def _fraction_dropped(injector, lo: int, hi: int) -> float:
    n = hi - lo + 1
    return sum(1 for t in range(lo, hi + 1) if injector.drops_reading(t)) / n


def test_p_zero_yields_no_dropouts() -> None:
    """probability=0 must produce an all-clean injector (no drops)."""
    inj = graded_dropout_injector(
        first_tick=200, last_tick=3399, probability=0.0, seed=20260731,
        sigmas=CHANNEL_SIGMAS,
    )
    assert _fraction_dropped(inj, 200, 3399) == 0.0


def test_p_one_yields_full_dropouts() -> None:
    """probability=1 must produce a drop on every tick in the window."""
    inj = graded_dropout_injector(
        first_tick=200, last_tick=3399, probability=1.0, seed=20260731,
        sigmas=CHANNEL_SIGMAS,
    )
    assert _fraction_dropped(inj, 200, 3399) == 1.0


@pytest.mark.parametrize("p", [0.25, 0.50, 0.75])
def test_intermediate_probabilities_hit_target_within_noise(p: float) -> None:
    """3,200 Bernoulli draws should hit ``p`` within ~0.02 (2 %) by CLT."""
    inj = graded_dropout_injector(
        first_tick=200, last_tick=3399, probability=p, seed=20260731,
        sigmas=CHANNEL_SIGMAS,
    )
    achieved = _fraction_dropped(inj, 200, 3399)
    assert abs(achieved - p) < 0.02, (
        f"probability {p} should produce ~{p:.2f} drops; got {achieved:.3f}"
    )


def test_no_dropouts_outside_the_window() -> None:
    """The injector must not fire on ticks outside [first_tick, last_tick]."""
    inj = graded_dropout_injector(
        first_tick=200, last_tick=3399, probability=1.0, seed=20260731,
        sigmas=CHANNEL_SIGMAS,
    )
    # Before window.
    for t in range(0, 200):
        assert not inj.drops_reading(t), f"tick {t} < first_tick fired"
    # After window.
    for t in range(3400, 3450):
        assert not inj.drops_reading(t), f"tick {t} > last_tick fired"


def test_same_inputs_yield_bit_identical_draws() -> None:
    """Two calls with the same (seed, first_tick, probability) must draw
    identical tick sets. Pre-registration integrity depends on this.
    """
    inj_a = graded_dropout_injector(
        first_tick=200, last_tick=3399, probability=0.5, seed=20260731,
        sigmas=CHANNEL_SIGMAS,
    )
    inj_b = graded_dropout_injector(
        first_tick=200, last_tick=3399, probability=0.5, seed=20260731,
        sigmas=CHANNEL_SIGMAS,
    )
    for t in range(200, 3400):
        assert inj_a.drops_reading(t) == inj_b.drops_reading(t), (
            f"tick {t} differs between two calls with identical inputs"
        )


def test_different_seeds_produce_different_draws() -> None:
    """Two different seeds at the same probability should not produce
    identical draws (or the seeding is broken)."""
    inj_a = graded_dropout_injector(
        first_tick=200, last_tick=3399, probability=0.5, seed=20260731,
        sigmas=CHANNEL_SIGMAS,
    )
    inj_b = graded_dropout_injector(
        first_tick=200, last_tick=3399, probability=0.5, seed=20260732,
        sigmas=CHANNEL_SIGMAS,
    )
    diffs = sum(
        1 for t in range(200, 3400)
        if inj_a.drops_reading(t) != inj_b.drops_reading(t)
    )
    # For two independent Bernoulli(0.5) streams the expected fraction of
    # disagreements is 0.5. Anything under 0.4 or over 0.6 is suspicious.
    assert 0.4 * 3200 < diffs < 0.6 * 3200, (
        f"expected ~50% disagreements between seeds, got {diffs} of 3200"
    )


def test_probability_out_of_range_raises() -> None:
    for bad in (-0.1, 1.5, float("nan")):
        with pytest.raises(ValueError, match="probability"):
            graded_dropout_injector(
                first_tick=200, last_tick=3399, probability=bad,
                seed=20260731, sigmas=CHANNEL_SIGMAS,
            )


def test_inverted_window_raises() -> None:
    with pytest.raises(ValueError, match="first_tick"):
        graded_dropout_injector(
            first_tick=300, last_tick=200, probability=0.5,
            seed=20260731, sigmas=CHANNEL_SIGMAS,
        )
