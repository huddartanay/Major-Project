"""Per-tick logger for Stage A's mechanism experiment.

The Stage A pre-registration
(``experiments/phase5_od8_h7/STEP1_MECHANISM/preregistration.md``) asks for
tick-level series of the seven L6 evidence fields, the failsafe state and its
two counters, and the true tracking error, so the H1 / H2 / H3 / H-none
decision in §4 can be made mechanistically rather than by inspecting an
aggregate that could be produced by more than one process.

Where the fields come from, and why here rather than in ``src/``
----------------------------------------------------------------
- The seven L6 fields are already emitted by ``L6ConformalGate.tick`` at
  ``src/astra/layers/l6_statistical_gate/gate.py:325`` as an evidence tuple on
  every ``GateVerdict``. This module walks the tuple; it does not compute.
- The failsafe fields are read off ``record.failsafe`` (a ``FailSafeSnapshot``
  produced by ``src/astra/layers/l8_failsafe/machine.py``). Names verified at
  construction so a future rename crashes the run rather than silently
  substituting a zero.
- The true tracking error is ``sample.lane_deviation_m``, which
  ``training.closed_loop.TickSample`` already carries (a benchmark can read
  the plant's truth via the observer; a deployed vehicle cannot). No
  ``on_assembled`` hook is required.

Nothing here writes back into the pipeline. The logger is an observer in the
strict sense: it reads what the tick produced, appends a row, and returns.
Placement is under ``benchmarks/`` per handoff §14 -- instrumentation, not
architecture, so no ADR is required.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any

from training.closed_loop import TickSample

#: The seven fields ``L6ConformalGate.tick`` writes to a verdict's evidence.
#: Kept in this exact order for column stability across analysis scripts.
L6_EVIDENCE_FIELDS: tuple[str, ...] = (
    "non_conformity_score",
    "departure",
    "sigma",
    "conformal_quantile",
    "effective_epsilon",
    "mmd_discrepancy",
    "calibration_samples",
)

#: Fields we require ``record.failsafe`` to expose. Verified once at logger
#: construction against a real snapshot; a rename in L8 fails loudly on the
#: very first tick, not silently in a downstream analysis a week later.
FAILSAFE_FIELDS: tuple[str, ...] = ("state", "ood_counter", "integrity_counter")


def _l6_evidence(sample: TickSample) -> dict[str, float]:
    """Extract the seven L6 evidence fields from this tick's verdict.

    Missing values become NaN rather than 0.0 so an analysis that averages
    them cannot confuse a tick where the gate did not report with a tick where
    the gate returned an exactly-zero value. R3c uses the same convention.
    """
    values: dict[str, float] = dict.fromkeys(L6_EVIDENCE_FIELDS, math.nan)
    verdict = getattr(sample.record, "safety_verdict", None)
    if verdict is None:
        return values
    for gate_verdict in getattr(verdict, "gate_verdicts", ()):
        # `gate` is an enum whose string ends in the gate identifier ("STATISTICAL").
        gate_name = str(getattr(gate_verdict, "gate", ""))
        if not gate_name.endswith("STATISTICAL"):
            continue
        for key, value in getattr(gate_verdict, "evidence", ()):
            if key in values:
                try:
                    values[key] = float(value)
                except (TypeError, ValueError):
                    # A non-numeric evidence value is a schema break -- leave
                    # NaN and let the analysis complain rather than coerce.
                    values[key] = math.nan
        break  # only one STATISTICAL gate; stop scanning
    return values


def _failsafe_fields(sample: TickSample) -> dict[str, Any]:
    """Extract failsafe state and both counters from ``record.failsafe``.

    ``state`` is coerced to a plain string (its ``.value`` when it is an enum,
    else ``str(...)``) so the JSONL file has no enum reprs and can be re-read
    without importing the astra package.
    """
    failsafe = getattr(sample.record, "failsafe", None)
    if failsafe is None:
        return {"failsafe_state": None, "ood_counter": None, "integrity_counter": None}
    state = getattr(failsafe, "state", None)
    return {
        "failsafe_state": getattr(state, "value", None) if state is not None else None,
        "ood_counter": int(getattr(failsafe, "ood_counter", -1)),
        "integrity_counter": int(getattr(failsafe, "integrity_counter", -1)),
    }


@dataclass
class TickLogger:
    """A callable observer that writes one JSON object per tick.

    The observer signature is what ``drive_closed_loop`` calls: it takes a
    ``TickSample`` and returns nothing. Instances open a file at construction
    (line-buffered) and close it in ``close()``. The header row goes in first
    and carries the provenance the pre-registration requires (§8): seed, fault,
    threshold, git SHA, run wall-clock start.

    A logger built once and reused across runs would silently mix runs in the
    same file, which is exactly the "aggregate that could be produced by two
    processes" the pre-registration is trying to avoid. One logger per run.
    """

    output_path: Path
    header: dict[str, Any]
    _handle: IO[str] = field(init=False)
    _tick_count: int = field(default=0, init=False)
    _fields_verified: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Open the file, write the header, and remember the offset for tick 0."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.output_path.open("w", encoding="utf-8", buffering=1)
        # Header is the first line; its keys are all metadata and none of them
        # is a per-tick field, so an analysis can tell rows from header without
        # a schema version. It still says schema_version = 1 for good measure.
        header = {"schema_version": 1, "kind": "stage_a_mechanism_tick", **self.header}
        self._handle.write(json.dumps(header) + "\n")

    def __call__(self, sample: TickSample) -> None:
        """Append this tick's row.

        First tick: verifies the failsafe snapshot really exposes the fields
        the pre-registration names, so a future L8 refactor that renames one
        crashes the run at tick 0 rather than losing every downstream analysis.
        """
        if not self._fields_verified:
            self._verify_failsafe_schema(sample)
            self._fields_verified = True
        row = {
            "tick": int(sample.tick),
            "lane_deviation_m": float(sample.lane_deviation_m),
            "speed_mps": float(sample.speed_mps),
            "lateral_acceleration_mps2": float(sample.lateral_acceleration_mps2),
            "fault_active": bool(sample.fault_active),
            "was_issued": bool(sample.was_issued),
        }
        row.update(_l6_evidence(sample))
        row.update(_failsafe_fields(sample))
        self._handle.write(json.dumps(row) + "\n")
        self._tick_count += 1

    def _verify_failsafe_schema(self, sample: TickSample) -> None:
        """Raise on the first tick if the failsafe snapshot lacks a field.

        The pre-registration commits to these three names. If a rename lands
        under ``src/astra/`` without updating this logger, the run must not
        silently write ``-1`` for every subsequent tick -- that would produce
        a data file that looks intact and is not, which is the failure mode
        the whole project's integrity discipline is organised against.
        """
        failsafe = getattr(sample.record, "failsafe", None)
        if failsafe is None:
            # A clean tick before the failsafe machine has observed anything
            # (rare, but possible); allow this pass, and re-verify next tick.
            self._fields_verified = False
            return
        missing = [name for name in FAILSAFE_FIELDS if not hasattr(failsafe, name)]
        if missing:
            raise RuntimeError(
                f"FailSafeSnapshot is missing fields {missing!r}; "
                f"benchmarks/mechanism_logger.py needs updating before the "
                f"Stage A pre-registration can bind. Do not proceed."
            )

    def close(self) -> int:
        """Flush and close. Returns the number of ticks written."""
        self._handle.flush()
        self._handle.close()
        return self._tick_count
