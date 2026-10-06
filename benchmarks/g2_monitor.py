"""GateBlindnessMonitor and its label-free baselines.

The design in one sentence
--------------------------
When L1's sensor-health layer fires (fault visible at the sensor boundary) but
the L6 conformal gate stays silent (fault invisible at the assurance boundary),
that gap is the evidence that the L6 gate has gone blind. Stage A's mechanism
observations show why: the L6 gate's inputs are held within ~1% of the clean
baseline for the whole duration of a sustained sensor fault, so no signal
internal to the L6 gate can be trusted to reveal blindness. The comparison
has to be between L1 and L6, not within L6.

Where each monitor sits
-----------------------
- `GateBlindnessMonitor` is the Stage C2 contribution. Cheap, label-free,
  online: one boolean state and one counter per tick.
- `L1OnlyMonitor` is the strongest existing baseline. E21 established it
  catches sustained `imu_dropout` at 30/30 with 0/30 clean false alarms and
  ~5-tick latency on dev seeds; held-out replicates exactly (§0.3). Any G2
  monitor that does not measurably beat L1 on some (fault, magnitude) cell
  in the Stage C1 sweep is not worth the wiring.
- `OracleMonitor` reads ground-truth `fault_active` from the sample. Only
  meaningful in benchmarks; a deployed vehicle has no such signal. Serves
  as the upper bound.
- `KSConfMonitor` runs a two-sample Kolmogorov-Smirnov test on a sliding
  window of L6 non-conformity scores against a reference clean window.
  From Sun & Lampert (arXiv 1804.04171). Sequentiality via Bonferroni over
  the number of tests performed so far, so alpha stays honest.
- `ConformalMartingaleMonitor` is Volkhonskiy et al.'s exchangeability
  martingale (arXiv 1706.03415) on the same score sequence. Fires when the
  running product of transformed p-values exceeds 1/alpha.

Each monitor exposes the same shape as ``benchmarks.detectors.Detector``:
name, description, and a method that consumes a ``DecisionRecord`` per tick
and returns whether it has fired. That symmetry is deliberate -- the Stage
C3 outcome experiment (§8) rotates monitors under the same driver, so the
harness reads one method regardless of what is behind it.

All state is per-instance. Reuse across runs is a programming error; the
factory functions build a fresh monitor per run.
"""

from __future__ import annotations

import math
import statistics
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from astra.contracts.audit import DecisionRecord
from astra.kernel.enums import StreamHealth
from benchmarks.detectors import DETECTORS

FROZEN_V3_P1 = 3.7024
"""The L6 threshold, quoted from the pre-registration; never recomputed here."""

DEFAULT_PATIENCE = 5
"""Ticks the disagreement must persist before the monitor fires.

The choice matches E21's L1 latency (5 ticks) so the two are on the same
temporal footing. A monitor with patience = 1 would be trivially reactive to
transient noise; higher patience trades off latency for false-alarm rate.
"""


def _health_is_degraded(record: DecisionRecord) -> bool:
    """True iff any sensor modality reports worse than HEALTHY.

    Mirrors ``benchmarks.detectors._health_is_degraded``; kept as a local
    function so this module has no import cycle with detectors.py.
    """
    return any(health is not StreamHealth.HEALTHY for _, health in record.frame_health)


def _l6_alarmed(record: DecisionRecord, threshold: float = FROZEN_V3_P1) -> bool:
    """True iff the L6 STATISTICAL gate's score exceeded ``threshold`` this tick.

    Reads the same evidence tuple the Stage A logger walks. A tick where the
    gate did not vote (setup, abstain) counts as not-alarmed here.
    """
    verdict = getattr(record, "safety_verdict", None)
    if verdict is None:
        return False
    for gate_verdict in getattr(verdict, "gate_verdicts", ()):
        if not str(getattr(gate_verdict, "gate", "")).endswith("STATISTICAL"):
            continue
        for key, value in getattr(gate_verdict, "evidence", ()):
            if key == "non_conformity_score":
                try:
                    return float(value) > threshold
                except (TypeError, ValueError):
                    return False
        return False
    return False


def _l6_score(record: DecisionRecord) -> float:
    """Return the L6 non-conformity score, or NaN if the gate did not report."""
    verdict = getattr(record, "safety_verdict", None)
    if verdict is None:
        return math.nan
    for gate_verdict in getattr(verdict, "gate_verdicts", ()):
        if not str(getattr(gate_verdict, "gate", "")).endswith("STATISTICAL"):
            continue
        for key, value in getattr(gate_verdict, "evidence", ()):
            if key == "non_conformity_score":
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return math.nan
    return math.nan


class Monitor(ABC):
    """Shared surface for the G2 monitor and its baselines.

    Kept minimal on purpose. A monitor is not a detector in the
    ``benchmarks.detectors`` sense (it may not be a pure function of a single
    tick) but exposes the same read-only relationship to the pipeline: it
    observes, it does not steer.
    """

    name: str

    @abstractmethod
    def observe(self, record: DecisionRecord, *, tick: int, fault_active: bool) -> bool:
        """Feed one tick. Return True iff the monitor is currently firing.

        ``fault_active`` is ground truth. Only ``OracleMonitor`` reads it; the
        others accept it in the signature so the outer loop is uniform.
        """


@dataclass
class GateBlindnessMonitor(Monitor):
    """The C2 contribution: flag blindness when L1 fires and L6 stays silent.

    Rationale (Stage A): the L6 gate's own inputs do not move under sustained
    faults, so no L6-internal statistic can detect blindness. L1's stream
    health does move (E21: 30/30 on `imu_dropout`, 5-tick latency), so the
    principled signal is the L1-vs-L6 disagreement.
    """

    name: str = "gate_blindness"
    patience: int = DEFAULT_PATIENCE
    threshold: float = FROZEN_V3_P1
    _consecutive_disagreement: int = field(default=0, init=False)
    _fired: bool = field(default=False, init=False)
    _first_fire_tick: int | None = field(default=None, init=False)

    def observe(self, record: DecisionRecord, *, tick: int, fault_active: bool) -> bool:
        l1_bad = _health_is_degraded(record)
        l6_alarmed = _l6_alarmed(record, self.threshold)
        # The disagreement of interest: L1 says something is wrong AND the
        # gate is not flagging it. The reverse (L6 fires alone) is the gate
        # doing its job; not blindness.
        if l1_bad and not l6_alarmed:
            self._consecutive_disagreement += 1
        else:
            self._consecutive_disagreement = 0
        if self._consecutive_disagreement >= self.patience and not self._fired:
            self._fired = True
            self._first_fire_tick = tick
        return self._fired

    @property
    def first_fire_tick(self) -> int | None:
        """Tick the monitor first fired, or ``None`` if it never did."""
        return self._first_fire_tick


@dataclass
class L1OnlyMonitor(Monitor):
    """Baseline: fire when L1 stream health has been unhealthy for ``patience``
    ticks. This is E21's `health` detector, reused verbatim so the C3 outcome
    experiment compares against exactly what E21 measured.
    """

    name: str = "l1_only"
    patience: int = DEFAULT_PATIENCE
    _run_length: int = field(default=0, init=False)
    _fired: bool = field(default=False, init=False)
    _first_fire_tick: int | None = field(default=None, init=False)

    def observe(self, record: DecisionRecord, *, tick: int, fault_active: bool) -> bool:
        if _health_is_degraded(record):
            self._run_length += 1
            if self._run_length >= self.patience and not self._fired:
                self._fired = True
                self._first_fire_tick = tick
        else:
            self._run_length = 0
        return self._fired

    @property
    def first_fire_tick(self) -> int | None:
        return self._first_fire_tick


@dataclass
class OracleMonitor(Monitor):
    """Upper bound: fires the first tick ``fault_active`` becomes True.

    Only meaningful in benchmarks; no deployed vehicle sees this signal. Its
    presence in the comparison gives a ceiling every practical monitor is
    measured against.
    """

    name: str = "oracle"
    _fired: bool = field(default=False, init=False)
    _first_fire_tick: int | None = field(default=None, init=False)

    def observe(self, record: DecisionRecord, *, tick: int, fault_active: bool) -> bool:
        if fault_active and not self._fired:
            self._fired = True
            self._first_fire_tick = tick
        return self._fired

    @property
    def first_fire_tick(self) -> int | None:
        return self._first_fire_tick


@dataclass
class KSConfMonitor(Monitor):
    """Two-sample KS test on L6 non-conformity scores.

    Sun & Lampert (arXiv 1804.04171) test whether the recent window of
    conformal scores is drawn from the same distribution as a reference
    clean window. This monitor fires when the two-sample KS test's
    p-value drops below ``alpha`` for ``patience`` consecutive ticks. A
    Bonferroni correction over the number of tests performed keeps
    family-wise error at ``alpha`` even under repeated testing.
    """

    name: str = "ks_conf"
    window: int = 200
    ref_window: int = 200
    alpha: float = 0.05
    patience: int = DEFAULT_PATIENCE
    _ref: list[float] = field(default_factory=list, init=False)
    _recent: deque[float] = field(default_factory=deque, init=False)
    _tests_run: int = field(default=0, init=False)
    _consecutive: int = field(default=0, init=False)
    _fired: bool = field(default=False, init=False)
    _first_fire_tick: int | None = field(default=None, init=False)

    def observe(self, record: DecisionRecord, *, tick: int, fault_active: bool) -> bool:
        score = _l6_score(record)
        if not math.isfinite(score):
            return self._fired
        # Reference window: the first `ref_window` ticks (before any fault
        # onset in the pre-registered design at tick 200 -- ref_window=200 by
        # default). After that, `_recent` slides.
        if len(self._ref) < self.ref_window:
            self._ref.append(score)
            return self._fired
        self._recent.append(score)
        if len(self._recent) > self.window:
            self._recent.popleft()
        if len(self._recent) < self.window:
            return self._fired
        # Compute a KS p-value on the two samples. Statistic is the max
        # empirical-CDF gap; asymptotic p-value from Kolmogorov's
        # distribution. Bonferroni corrects over number of tests.
        self._tests_run += 1
        p = _ks_two_sample_p(list(self._ref), list(self._recent))
        corrected_alpha = self.alpha / self._tests_run
        if p < corrected_alpha:
            self._consecutive += 1
            if self._consecutive >= self.patience and not self._fired:
                self._fired = True
                self._first_fire_tick = tick
        else:
            self._consecutive = 0
        return self._fired

    @property
    def first_fire_tick(self) -> int | None:
        return self._first_fire_tick


def _ks_two_sample_p(a: Sequence[float], b: Sequence[float]) -> float:
    """Approximate two-sample KS p-value using Kolmogorov's asymptotic form.

    Standalone implementation so the monitor has no scipy dependency
    (scipy was removed alongside FilterPy, per the repo's own note in
    demo/dashboard.py). Accuracy is fine for n >= 100.
    """
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        return 1.0
    # Empirical CDF gap.
    combined = sorted(set(a) | set(b))
    a_sorted = sorted(a)
    b_sorted = sorted(b)
    max_gap = 0.0
    i = j = 0
    for value in combined:
        while i < n1 and a_sorted[i] <= value:
            i += 1
        while j < n2 and b_sorted[j] <= value:
            j += 1
        gap = abs(i / n1 - j / n2)
        if gap > max_gap:
            max_gap = gap
    # Kolmogorov's asymptotic p-value.
    en = math.sqrt(n1 * n2 / (n1 + n2))
    lam = (en + 0.12 + 0.11 / en) * max_gap
    if lam <= 0.0:
        return 1.0
    # Alternating series expansion, converges quickly.
    p = 0.0
    for k in range(1, 101):
        term = 2.0 * ((-1) ** (k - 1)) * math.exp(-2.0 * lam * lam * k * k)
        p += term
        if abs(term) < 1e-12:
            break
    return min(max(p, 0.0), 1.0)


@dataclass
class ConformalMartingaleMonitor(Monitor):
    """Volkhonskiy et al. (arXiv 1706.03415) exchangeability martingale.

    On each tick a p-value is computed from the score against a reference
    window (rank of new score among reference + 1) / (len(ref) + 1). Each
    p-value is transformed by a betting function ``f_theta(p) = theta *
    p^{theta - 1}`` and the running product is a martingale under
    exchangeability. Fires when the product exceeds ``1 / alpha``, giving
    a valid sequential test at level ``alpha``.

    Two small implementation choices: (1) theta = 0.5 (a mild power betting
    function, standard for anomaly detection); (2) an integer log-scale so
    the product does not underflow.
    """

    name: str = "conformal_martingale"
    ref_window: int = 200
    alpha: float = 0.05
    theta: float = 0.5
    patience: int = DEFAULT_PATIENCE
    _ref: list[float] = field(default_factory=list, init=False)
    _log_martingale: float = field(default=0.0, init=False)
    _consecutive: int = field(default=0, init=False)
    _fired: bool = field(default=False, init=False)
    _first_fire_tick: int | None = field(default=None, init=False)

    def observe(self, record: DecisionRecord, *, tick: int, fault_active: bool) -> bool:
        score = _l6_score(record)
        if not math.isfinite(score):
            return self._fired
        if len(self._ref) < self.ref_window:
            self._ref.append(score)
            return self._fired
        # Rank-based p-value; ties broken by adding one to numerator, standard.
        rank = sum(1 for r in self._ref if r >= score) + 1
        p = rank / (len(self._ref) + 1.0)
        # Betting function f_theta(p) = theta * p^{theta - 1}; log for stability.
        log_bet = math.log(max(self.theta, 1e-12)) + (self.theta - 1.0) * math.log(max(p, 1e-12))
        self._log_martingale += log_bet
        # Fire when martingale > 1 / alpha, i.e. log > -log(alpha).
        if self._log_martingale > -math.log(self.alpha):
            self._consecutive += 1
            if self._consecutive >= self.patience and not self._fired:
                self._fired = True
                self._first_fire_tick = tick
        else:
            self._consecutive = 0
        return self._fired

    @property
    def first_fire_tick(self) -> int | None:
        return self._first_fire_tick


ALL_MONITORS: tuple[type[Monitor], ...] = (
    GateBlindnessMonitor,
    L1OnlyMonitor,
    OracleMonitor,
    KSConfMonitor,
    ConformalMartingaleMonitor,
)
"""Every monitor implementation this module ships. The C3 outcome experiment
iterates this tuple; adding a new monitor here is enough to include it in
the comparison table, no further wiring required.
"""


def build_monitors() -> tuple[Monitor, ...]:
    """Fresh instances of every monitor. One tuple, one run.

    A monitor keeps per-run state; reusing an instance across runs mixes
    two histories in one output. The factory exists so a caller cannot
    accidentally do that.
    """
    return tuple(cls() for cls in ALL_MONITORS)


def evaluate_run(
    records: Sequence[DecisionRecord],
    *,
    fault_active: Sequence[bool],
    monitors: tuple[Monitor, ...] | None = None,
) -> dict[str, dict[str, Any]]:
    """Feed a whole run through every monitor and return their outcomes.

    Args:
        records: Tick-ordered decision records.
        fault_active: Ground truth, same length as records.
        monitors: Optional pre-built monitors (typically from :func:`build_monitors`).
            Reusing already-observed monitors is a caller error.

    Returns:
        Mapping monitor name -> ``{"fired": bool, "first_fire_tick": int | None,
        "latency_ticks": int | None, "false_alarm": bool}``. Latency is
        measured from the first True in ``fault_active`` and is None on
        clean runs; false_alarm is True iff the monitor fired on a run
        with no true fault.
    """
    if monitors is None:
        monitors = build_monitors()
    if len(records) != len(fault_active):
        raise ValueError(
            f"records ({len(records)}) and fault_active ({len(fault_active)}) must match"
        )
    fault_active = list(fault_active)
    opened_at = next((i for i, x in enumerate(fault_active) if x), None)

    for tick, (record, active) in enumerate(zip(records, fault_active)):
        for monitor in monitors:
            monitor.observe(record, tick=tick, fault_active=active)

    out: dict[str, dict[str, Any]] = {}
    for monitor in monitors:
        fire_tick = monitor.first_fire_tick
        if fire_tick is None:
            latency: int | None = None
            false_alarm = False
        elif opened_at is None:
            latency = None
            false_alarm = True
        elif fire_tick >= opened_at:
            latency = fire_tick - opened_at
            false_alarm = False
        else:
            latency = None
            false_alarm = True
        out[monitor.name] = {
            "fired": monitor.first_fire_tick is not None,
            "first_fire_tick": fire_tick,
            "latency_ticks": latency,
            "false_alarm": false_alarm,
        }
    return out
