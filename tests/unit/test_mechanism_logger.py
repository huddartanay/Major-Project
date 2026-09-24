"""Tests for the Stage A per-tick logger.

Why the logger has its own tests
--------------------------------
The Stage A pre-registration binds to the fields this logger writes. A silent
bug -- a field renamed to a typo, a NaN written as 0.0, the header omitted --
propagates through the whole downstream analysis: the ratios, the H1/H2/H3
verdict, and the IV-vs-ITSC decision are all functions of what these rows
say. A regression here does not produce a wrong number in a test suite; it
produces a wrong number in the paper.

So each test is about a property the analyser reads back:

- the header row is the first line of the file, distinguishable from ticks,
- every per-tick row carries all 15 expected fields,
- a missing L6 evidence field is NaN, not 0.0 (an average of "silent tick"
  values must not be confused with an average of "gate reported zero"),
- the failsafe schema verification fires the FIRST tick a snapshot is present
  and refuses to write further rows if a field disappears.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest

from benchmarks.mechanism_logger import (
    FAILSAFE_FIELDS,
    L6_EVIDENCE_FIELDS,
    TickLogger,
    _failsafe_fields,
    _l6_evidence,
)


@dataclass
class _FakeGateVerdict:
    """Mimics enough of GateVerdict for the logger to walk it."""

    gate: str
    evidence: tuple[tuple[str, float], ...]


@dataclass
class _FakeSafetyVerdict:
    gate_verdicts: tuple[_FakeGateVerdict, ...]


def _fake_sample(
    *,
    tick: int = 0,
    l6_evidence: tuple[tuple[str, float], ...] | None = None,
    failsafe: object | None = None,
    lane_deviation_m: float = 0.42,
    speed_mps: float = 12.5,
    lateral_acceleration_mps2: float = -0.1,
    fault_active: bool = False,
    was_issued: bool = True,
) -> SimpleNamespace:
    """Build a stand-in TickSample. Only the attributes the logger reads."""
    evidence = l6_evidence if l6_evidence is not None else tuple(
        (name, float(i + 1)) for i, name in enumerate(L6_EVIDENCE_FIELDS)
    )
    gv = _FakeGateVerdict(gate="GateId.STATISTICAL", evidence=evidence)
    record = SimpleNamespace(
        safety_verdict=_FakeSafetyVerdict(gate_verdicts=(gv,)),
        failsafe=failsafe if failsafe is not None else SimpleNamespace(
            state=SimpleNamespace(value="NOMINAL"),
            ood_counter=3,
            integrity_counter=1,
        ),
    )
    return SimpleNamespace(
        tick=tick,
        record=record,
        lane_deviation_m=lane_deviation_m,
        speed_mps=speed_mps,
        lateral_acceleration_mps2=lateral_acceleration_mps2,
        fault_active=fault_active,
        was_issued=was_issued,
    )


def test_l6_evidence_reads_every_field_the_pre_reg_names() -> None:
    """All seven fields end up in the returned dict with float values.

    The pre-registration's ratio computation (§4) uses these exact keys; a
    typo here would silently drop one from the analysis.
    """
    values = _l6_evidence(_fake_sample())
    assert set(values.keys()) == set(L6_EVIDENCE_FIELDS)
    for i, name in enumerate(L6_EVIDENCE_FIELDS):
        assert values[name] == pytest.approx(float(i + 1))


def test_l6_evidence_missing_field_becomes_nan_not_zero() -> None:
    """If the gate reports evidence without one of the pre-reg fields, the
    logger writes NaN. An analysis averaging "missing" and "reported zero"
    would be a mistake -- H2 (departure collapses) reads a low departure as
    evidence, and 0.0 from a tick where the gate did not report would satisfy
    the H2 fingerprint spuriously.
    """
    incomplete = (("non_conformity_score", 4.0), ("sigma", 0.2))  # departure omitted
    values = _l6_evidence(_fake_sample(l6_evidence=incomplete))
    assert values["non_conformity_score"] == pytest.approx(4.0)
    assert values["sigma"] == pytest.approx(0.2)
    assert math.isnan(values["departure"])
    for other in ("conformal_quantile", "effective_epsilon", "mmd_discrepancy", "calibration_samples"):
        assert math.isnan(values[other])


def test_l6_evidence_no_statistical_gate_returns_all_nan() -> None:
    """A tick where the STATISTICAL gate did not vote (e.g. abstained during
    setup) yields NaN for every field, not zero.
    """
    other = _FakeGateVerdict(gate="GateId.DETERMINISTIC", evidence=(("something", 1.0),))
    record = SimpleNamespace(safety_verdict=_FakeSafetyVerdict((other,)),
                             failsafe=SimpleNamespace(
                                 state=SimpleNamespace(value="NOMINAL"),
                                 ood_counter=0, integrity_counter=0))
    sample = SimpleNamespace(tick=0, record=record,
                             lane_deviation_m=0.0, speed_mps=0.0,
                             lateral_acceleration_mps2=0.0,
                             fault_active=False, was_issued=True)
    values = _l6_evidence(sample)
    assert all(math.isnan(v) for v in values.values())


def test_failsafe_fields_coerce_state_to_plain_string() -> None:
    """The JSONL file has no enum reprs, so downstream analysis has no import
    dependency on the astra package.
    """
    out = _failsafe_fields(_fake_sample())
    assert out == {"failsafe_state": "NOMINAL", "ood_counter": 3, "integrity_counter": 1}


def test_failsafe_fields_when_absent_are_none() -> None:
    """The failsafe machine may not have observed anything on the very first
    tick of a fresh run. The logger should not crash; it should write
    ``None`` and continue.
    """
    sample = _fake_sample(failsafe=SimpleNamespace())  # no attributes set
    # We stub the guard rather than skipping it -- setting failsafe=None to
    # exercise the "no snapshot yet" branch.
    sample.record.failsafe = None
    out = _failsafe_fields(sample)
    assert out == {"failsafe_state": None, "ood_counter": None, "integrity_counter": None}


def test_logger_writes_header_first_then_one_row_per_call(tmp_path: Path) -> None:
    """A written file has exactly ``1 + n_ticks`` lines: the header is line 0,
    each tick is line 1..n. This is the shape the analyser assumes.
    """
    output = tmp_path / "run.jsonl"
    logger = TickLogger(output_path=output, header={"seed": 20260731, "fault": "imu_dropout"})
    for tick in range(5):
        logger(_fake_sample(tick=tick))
    written = logger.close()

    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 6
    header = json.loads(lines[0])
    assert header["schema_version"] == 1
    assert header["kind"] == "stage_a_mechanism_tick"
    assert header["seed"] == 20260731
    assert header["fault"] == "imu_dropout"
    assert written == 5

    for i, line in enumerate(lines[1:]):
        row = json.loads(line)
        assert row["tick"] == i
        # Every pre-registered field present.
        for field in ("lane_deviation_m", "speed_mps", "lateral_acceleration_mps2",
                      "fault_active", "was_issued", "failsafe_state",
                      "ood_counter", "integrity_counter", *L6_EVIDENCE_FIELDS):
            assert field in row, f"row {i} missing field {field!r}"


def test_logger_refuses_to_write_when_failsafe_field_is_missing(tmp_path: Path) -> None:
    """If the FailSafeSnapshot renames one of the fields the logger needs, a
    silent zero every tick would produce a data file that looks intact and
    is not. The logger raises on the first tick where the snapshot lacks a
    field, forcing the reviewer to update the logger before the sweep runs.
    """
    output = tmp_path / "broken.jsonl"
    logger = TickLogger(output_path=output, header={"seed": 1})

    class _MissingCounter:
        state = SimpleNamespace(value="NOMINAL")
        ood_counter = 0
        # integrity_counter deliberately omitted -- simulates a rename

    sample = _fake_sample(failsafe=_MissingCounter())
    with pytest.raises(RuntimeError, match="missing fields"):
        logger(sample)

    # Verify the exception names the field the reviewer needs to fix.
    with pytest.raises(RuntimeError) as excinfo:
        logger(sample)
    assert "integrity_counter" in str(excinfo.value)
    logger.close()


def test_failsafe_field_names_match_what_l8_actually_exposes() -> None:
    """Guard against a rename under ``src/astra/layers/l8_failsafe/``.

    The three names live in one place -- ``FAILSAFE_FIELDS`` -- so a rename
    in L8 fails this test before it fails a running sweep. We import the
    real snapshot class here (not a fake) and assert each name exists.
    """
    from astra.layers.l8_failsafe.machine import FailSafeSnapshot  # noqa: PLC0415

    hints = FailSafeSnapshot.__annotations__ if hasattr(FailSafeSnapshot, "__annotations__") else {}
    # FailSafeSnapshot may be a dataclass; either way, __init__ signature or
    # dataclass fields expose the parameter names. Use both routes so a shape
    # change in one still catches the miss.
    signature_names = set(hints.keys())
    try:
        import dataclasses  # noqa: PLC0415
        if dataclasses.is_dataclass(FailSafeSnapshot):
            signature_names |= {f.name for f in dataclasses.fields(FailSafeSnapshot)}
    except Exception:  # pragma: no cover - defensive
        pass
    for name in FAILSAFE_FIELDS:
        assert name in signature_names, (
            f"benchmarks/mechanism_logger.py names {name!r} but "
            f"FailSafeSnapshot does not expose it. Rename in L8?"
        )
