"""Tests for the G2 monitor and its baselines.

Each monitor is checked against the specific behaviour Stage C2 depends on.
The tests do not stub the pipeline; they build synthetic ``DecisionRecord``-
shaped objects, because a monitor is a pure function of a stream of records
and testing it that way keeps the failure surface narrow -- a broken monitor
here fails a test, not a 70-minute Stage C3 experiment.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from astra.kernel.enums import StreamHealth
from benchmarks.g2_monitor import (
    ConformalMartingaleMonitor,
    GateBlindnessMonitor,
    KSConfMonitor,
    L1OnlyMonitor,
    OracleMonitor,
    _ks_two_sample_p,
    build_monitors,
    evaluate_run,
)


@dataclass
class _FakeGate:
    gate: str
    evidence: tuple[tuple[str, float], ...]


def _record(*, score: float | None, l1_healthy: bool = True) -> SimpleNamespace:
    """A minimal decision record with the two fields the monitors read."""
    if score is None:
        gate_verdicts: tuple[_FakeGate, ...] = ()
    else:
        gate_verdicts = (
            _FakeGate("GateId.STATISTICAL", (("non_conformity_score", score),)),
        )
    safety = SimpleNamespace(gate_verdicts=gate_verdicts)
    health = StreamHealth.HEALTHY if l1_healthy else StreamHealth.FAULTED
    return SimpleNamespace(
        safety_verdict=safety,
        frame_health=((SimpleNamespace(value="IMU"), health),),
    )


def test_gate_blindness_fires_when_l1_bad_and_gate_quiet_for_patience() -> None:
    """Ticks where L1 is unhealthy AND the gate is not alarming, held for
    `patience` ticks, is exactly the disagreement the monitor exists for.
    """
    mon = GateBlindnessMonitor(patience=5)
    # Ticks 0-9 clean: L1 healthy, no alarm.
    for tick in range(10):
        assert mon.observe(_record(score=1.0), tick=tick, fault_active=False) is False
    # Ticks 10-13: L1 bad, gate quiet -- disagreement, but only 4 ticks.
    for tick in range(10, 14):
        mon.observe(_record(score=1.0, l1_healthy=False), tick=tick, fault_active=True)
    assert mon.first_fire_tick is None
    # Tick 14: fifth consecutive disagreement -> fires.
    assert mon.observe(_record(score=1.0, l1_healthy=False), tick=14, fault_active=True) is True
    assert mon.first_fire_tick == 14


def test_gate_blindness_does_not_fire_when_gate_also_alarming() -> None:
    """If L6 is doing its job (alarming), it isn't blind -- no matter what L1 says."""
    mon = GateBlindnessMonitor(patience=3)
    for tick in range(20):
        # L1 bad AND L6 above threshold -> not blindness.
        fired = mon.observe(
            _record(score=100.0, l1_healthy=False),
            tick=tick,
            fault_active=True,
        )
        assert fired is False


def test_gate_blindness_resets_on_agreement() -> None:
    """A tick where L1 agrees with L6 (both healthy, both quiet) resets the counter."""
    mon = GateBlindnessMonitor(patience=5)
    # Four disagreement ticks.
    for tick in range(4):
        mon.observe(_record(score=1.0, l1_healthy=False), tick=tick, fault_active=True)
    # Then one agreement tick (L1 healthy).
    mon.observe(_record(score=1.0, l1_healthy=True), tick=4, fault_active=True)
    # Then four more disagreement ticks -- should not have fired yet.
    for tick in range(5, 9):
        mon.observe(_record(score=1.0, l1_healthy=False), tick=tick, fault_active=True)
    assert mon.first_fire_tick is None


def test_l1_only_matches_e21_health_behaviour_on_dropout() -> None:
    """L1OnlyMonitor with patience=5 should fire the fifth consecutive
    unhealthy tick. This is E21's `health` detector's shape.
    """
    mon = L1OnlyMonitor(patience=5)
    for tick in range(5):
        mon.observe(_record(score=1.0, l1_healthy=False), tick=tick, fault_active=True)
    assert mon.first_fire_tick == 4


def test_oracle_fires_immediately_when_fault_active_first_true() -> None:
    """Oracle is a ceiling: it fires on the exact tick the fault opens."""
    mon = OracleMonitor()
    # Clean run.
    for tick in range(200):
        mon.observe(_record(score=1.0), tick=tick, fault_active=False)
    assert mon.first_fire_tick is None
    # Fault opens tick 200.
    mon.observe(_record(score=1.0), tick=200, fault_active=True)
    assert mon.first_fire_tick == 200


def test_ks_conf_flags_when_score_distribution_shifts() -> None:
    """KSConfMonitor should fire when the recent window's scores are drawn
    from a clearly different distribution than the reference window's.
    """
    rng = random.Random(42)
    mon = KSConfMonitor(window=200, ref_window=200, alpha=0.05, patience=5)
    # Fill reference with N(3.7, 0.5) scores.
    for tick in range(200):
        mon.observe(_record(score=rng.gauss(3.7, 0.5)), tick=tick, fault_active=False)
    assert mon.first_fire_tick is None
    # Feed 200 recent ticks from same distribution -- expect no fire.
    for tick in range(200, 400):
        mon.observe(_record(score=rng.gauss(3.7, 0.5)), tick=tick, fault_active=False)
    baseline_first = mon.first_fire_tick
    # Now inject scores from N(2.0, 0.5) -- a clear shift down.
    for tick in range(400, 800):
        mon.observe(_record(score=rng.gauss(2.0, 0.5)), tick=tick, fault_active=True)
    assert mon.first_fire_tick is not None, "KS monitor should fire on a clear shift"
    assert mon.first_fire_tick != baseline_first  # either was None before, or moved


def test_ks_conf_does_not_fire_on_stationary_stream() -> None:
    """Alpha=0.05 with Bonferroni over many tests should keep the FP rate low
    on a stationary stream over a long horizon.
    """
    rng = random.Random(7)
    mon = KSConfMonitor(window=200, ref_window=200, alpha=0.05, patience=5)
    for tick in range(2000):
        mon.observe(_record(score=rng.gauss(3.7, 0.5)), tick=tick, fault_active=False)
    # With Bonferroni over ~1600 tests, no spurious fire expected.
    assert mon.first_fire_tick is None


def test_conformal_martingale_fires_on_a_persistent_upward_shift() -> None:
    """The p-value is computed as `rank_from_top / (n+1)`, so it is *small*
    when new scores are unusually HIGH. With theta=0.5 the betting function
    theta * p^{theta-1} rewards small p, so the martingale grows on upward
    shifts and this test exercises that direction. Downward shifts require
    a different (or symmetric) betting function; that variant is a Stage C2
    open item, not a shipped feature.
    """
    rng = random.Random(3)
    mon = ConformalMartingaleMonitor(ref_window=200, alpha=0.05, theta=0.5, patience=5)
    # Reference: N(3.7, 0.5).
    for tick in range(200):
        mon.observe(_record(score=rng.gauss(3.7, 0.5)), tick=tick, fault_active=False)
    assert mon.first_fire_tick is None
    # Shift UP (persistently higher scores than reference).
    for tick in range(200, 1000):
        mon.observe(_record(score=rng.gauss(6.0, 0.5)), tick=tick, fault_active=True)
    assert mon.first_fire_tick is not None


def test_evaluate_run_returns_all_monitors_and_measures_latency() -> None:
    """Full-run evaluation returns one entry per monitor with the fields the
    C3 outcome experiment reads (fired, first_fire_tick, latency, false_alarm).
    """
    records = []
    fault_active = []
    for tick in range(30):
        records.append(_record(score=1.0, l1_healthy=(tick < 10)))
        fault_active.append(tick >= 10)
    result = evaluate_run(records, fault_active=fault_active)
    assert "gate_blindness" in result
    assert "l1_only" in result
    assert "oracle" in result
    assert "ks_conf" in result
    assert "conformal_martingale" in result
    # Oracle should fire exactly at tick 10 (first True).
    assert result["oracle"]["fired"] is True
    assert result["oracle"]["first_fire_tick"] == 10
    assert result["oracle"]["latency_ticks"] == 0


def test_evaluate_run_rejects_mismatched_lengths() -> None:
    """A length mismatch between records and fault_active is a caller error
    and must raise, not silently truncate or repeat.
    """
    records = [_record(score=1.0)]
    with pytest.raises(ValueError, match="must match"):
        evaluate_run(records, fault_active=[True, False])


def test_ks_p_value_on_the_same_sample_is_one() -> None:
    """Regression pin: KS on a sample compared with itself yields p = 1.

    Two independent draws from the same distribution can still KS-reject at
    alpha = 0.05 by chance -- that is the whole point of a level test -- so
    testing the KS routine against "two normals" is a fragile assertion.
    Compare a sample with itself instead; this is the only case where the
    p-value is deterministic across seeds.
    """
    rng = random.Random(1)
    a = [rng.gauss(0, 1) for _ in range(500)]
    p = _ks_two_sample_p(a, a)
    assert p > 0.9, f"expected p ~ 1 for a self-comparison, got {p}"


def test_build_monitors_yields_fresh_instances() -> None:
    """A monitor keeps per-run state; reusing one across runs mixes them. The
    factory must not memoise.
    """
    a = build_monitors()
    b = build_monitors()
    assert a is not b
    # Same monitor names in same order.
    assert [m.name for m in a] == [m.name for m in b]
    # But different objects.
    for m_a, m_b in zip(a, b):
        assert m_a is not m_b
