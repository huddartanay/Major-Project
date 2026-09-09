"""E21 -- OD-8 against the detectors that were already in the repository.

Implements the design frozen in
``experiments/phase5_od8_h7/E21_BASELINE_COMPARISON/preregistration.md``.

Paired with E18-R3c: the same 30 seeds, the same six faults, sustained injection
opening at tick 200 and never closing, 3,400 ticks. A clean arm of the same 30
seeds supplies the false-positive rate, without which a detection number means
nothing -- a detector that fires constantly detects everything.

Nothing in ``benchmarks.detectors`` is modified. Its three thresholds were set
during P2.7 and are used as committed.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import TYPE_CHECKING

from astra.kernel.enums import SensorModality
from astra.layers.l4_proposer.learned import LearnedPolicy
from benchmarks.detectors import DETECTORS, evaluate
from benchmarks.e18_evaluate import SEVERITIES
from training.closed_loop import (
    CHANNEL_SIGMAS,
    DEFAULT_CHANNEL_SIGMAS,
    RedundantSensing,
    drive_closed_loop,
)
from training.faults import (
    FaultChannel,
    FaultInjector,
    bias,
    dropout,
    noise_burst,
    stuck_at,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ["FAULTS", "main", "run_one"]

BASE_SEED, N_SEEDS, TICKS, FAULT_FIRST = 20260731, 30, 3400, 200
POLICY_PATH = Path("var/policy/synthetic.pt")
_OUT = Path("experiments/phase5_od8_h7/E21_BASELINE_COMPARISON")

FAULTS = (
    "position_bias",
    "position_drift",
    "imu_dropout",
    "lateral_noise",
    "speed_bias",
    "speed_stuck",
)

#: E18-R3c's run-level detection under sustained injection, as recorded. Quoted,
#: never recomputed here -- this experiment measures the baselines, not OD-8.
OD8_SUSTAINED: dict[str, float] = {
    "position_bias": 1.00,
    "position_drift": 1.00,
    "lateral_noise": 1.00,
    "speed_stuck": 0.37,
    "speed_bias": 0.00,
    "imu_dropout": 0.00,
}

DETECTION_BAR = 0.90
CLEAN_BAR = 0.10


def _severity(fault: str) -> float | None:
    """Return the medium severity for a fault, or ``None`` where it has none.

    ``speed_stuck`` and ``imu_dropout`` take no magnitude parameter -- STUCK_AT
    holds the last value and DROPOUT suppresses the publish -- so their severity
    is ``None`` by design rather than by omission.

    Args:
        fault: The fault name.

    Returns:
        The magnitude, or ``None``.
    """
    value = SEVERITIES[fault]["levels"]["medium"]
    return None if value is None else float(value)


def _injector_sustained(fault: str, magnitude: float | None, seed: int) -> FaultInjector:
    """Injector whose fault opens at tick 200 and never closes.

    Written here rather than imported: ``e18_evaluate._build_injector`` binds
    ``last_tick`` to its own ``TICKS = 400`` constant, and importing it into a
    3,400-tick run is exactly the defect that inflated E18-R3b.

    Args:
        fault: The fault name.
        magnitude: Severity, or ``None`` for the parameterless faults.
        seed: Run seed.

    Returns:
        The armed injector.
    """
    last = TICKS - 1
    if fault == "speed_bias":
        specs = (bias(FaultChannel.SPEED, first_tick=FAULT_FIRST, last_tick=last,
                      offset=float(magnitude)),)
    elif fault == "speed_stuck":
        specs = (stuck_at(FaultChannel.SPEED, first_tick=FAULT_FIRST, last_tick=last),)
    elif fault == "lateral_noise":
        specs = (noise_burst(FaultChannel.LATERAL_ACCELERATION, first_tick=FAULT_FIRST,
                             last_tick=last, sigma_multiplier=float(magnitude)),)
    elif fault == "imu_dropout":
        specs = (dropout(first_tick=FAULT_FIRST, last_tick=last),)
    else:
        specs = ()
    return FaultInjector(specs, seed=seed, sigmas=CHANNEL_SIGMAS)


def _sensing_sustained(
    fault: str, magnitude: float | None, seed: int, *, active: bool
) -> RedundantSensing:
    """Redundant spec for a sustained position fault.

    Sustained means no closing tick, so the drift rate is scaled over the whole
    run rather than over a 400-tick window -- the defect that inflated R3b's
    ``position_drift`` arm to roughly 32 m.

    Args:
        fault: The fault name.
        magnitude: Severity value.
        seed: Run seed.
        active: Whether to arm it at all.

    Returns:
        The sensing specification.
    """
    if not active or fault not in {"position_bias", "position_drift"}:
        return RedundantSensing.build(sigmas=DEFAULT_CHANNEL_SIGMAS, seed=seed)
    span = TICKS - 1 - FAULT_FIRST
    return RedundantSensing.build(
        sigmas=DEFAULT_CHANNEL_SIGMAS,
        seed=seed,
        faulted=SensorModality.IMU,
        also_faulted=(SensorModality.GPS,),
        opens_at=FAULT_FIRST,
        bias=float(magnitude or 0.0) if fault == "position_bias" else 0.0,
        drift_per_tick=0.0 if fault == "position_bias" else float(magnitude or 0.0) / span,
    )


def run_one(policy: object, fault: str | None, seed: int) -> list[dict[str, object]]:
    """Drive one run and score every detector on it.

    Args:
        policy: The loaded proposer.
        fault: The fault name, or ``None`` for a clean run.
        seed: Run seed.

    Returns:
        One record per detector.
    """
    active = fault is not None
    magnitude = None if fault is None else _severity(fault)
    injector = (
        _injector_sustained(fault, magnitude, seed)
        if active
        else FaultInjector((), seed=seed, sigmas=CHANNEL_SIGMAS)
    )

    records = []
    drive_closed_loop(
        policy=policy,
        ticks=TICKS,
        seed=seed,
        observer=lambda s: records.append(s.record),
        fault=injector,
        redundant=_sensing_sustained(fault or "", magnitude, seed, active=active),
    )

    truth = [active and index >= FAULT_FIRST for index in range(len(records))]
    detections = evaluate(records, fault_active=truth, opened_at=FAULT_FIRST if active else None)
    return [
        {
            "fault": fault or "clean",
            "seed": seed,
            "detector": d.detector,
            "fired_at": d.fired_at,
            "latency_ticks": d.latency_ticks,
            "fired_ticks": d.fired_ticks,
            "false_alarm": d.false_alarm,
            # A clean run has no fault window, so "fired at all" is the
            # false-positive event; a faulted run needs firing after onset.
            "detected": bool(d.fired_at is not None and (not active or d.fired_at >= FAULT_FIRST)),
        }
        for d in detections
    ]


def main(argv: Sequence[str] | None = None) -> int:
    """Run E21 and write the results.

    Args:
        argv: Command-line arguments.

    Returns:
        Process exit status.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, default=N_SEEDS)
    arguments = parser.parse_args(argv)

    policy = LearnedPolicy.load(POLICY_PATH)
    seeds = [BASE_SEED + i for i in range(arguments.seeds)]
    rows: list[dict[str, object]] = []
    started = time.time()

    arms: list[str | None] = [None, *FAULTS]
    for arm in arms:
        for seed in seeds:
            rows.extend(run_one(policy, arm, seed))
        done = time.time() - started
        print(f"  {arm or 'clean':<16} {len(seeds)} runs   elapsed {done / 60:.1f} min", flush=True)

    _OUT.joinpath("raw_results").mkdir(parents=True, exist_ok=True)
    _OUT.joinpath("raw_results", "detections.json").write_text(json.dumps(rows, indent=1))

    # ---- summarise -------------------------------------------------------
    names = [d.name for d in DETECTORS]
    clean_fp = {
        n: sum(1 for r in rows if r["fault"] == "clean" and r["detector"] == n and r["detected"])
        / len(seeds)
        for n in names
    }

    summary: list[dict[str, object]] = []
    for fault in FAULTS:
        for n in names:
            sub = [r for r in rows if r["fault"] == fault and r["detector"] == n]
            hits = [r for r in sub if r["detected"]]
            lat = [int(r["latency_ticks"]) for r in hits if r["latency_ticks"] is not None]
            rate = len(hits) / len(sub) if sub else 0.0
            summary.append(
                {
                    "fault": fault,
                    "detector": n,
                    "detection_rate": rate,
                    "clean_fp": clean_fp[n],
                    "median_latency_ticks": statistics.median(lat) if lat else None,
                    "detects": bool(rate >= DETECTION_BAR and clean_fp[n] <= CLEAN_BAR),
                }
            )

    print(f"\nclean false-positive rate over {len(seeds)} clean runs:")
    for n in names:
        flag = "OK" if clean_fp[n] <= CLEAN_BAR else "BREACHES the 0.10 clean bar"
        print(f"  {n:<12}{clean_fp[n]:>7.3f}   {flag}")

    print(f"\n{'fault':<16}{'OD-8':>7}", end="")
    for n in names:
        print(f"{n:>12}", end="")
    print("   detected by")
    print("-" * 78)
    for fault in FAULTS:
        print(f"{fault:<16}{OD8_SUSTAINED[fault]:>7.2f}", end="")
        winners = []
        for n in names:
            row = next(s for s in summary if s["fault"] == fault and s["detector"] == n)
            mark = "*" if row["detects"] else " "
            print(f"{row['detection_rate']:>11.2f}{mark}", end="")
            if row["detects"]:
                winners.append(n)
        print(f"   {', '.join(winners) if winners else '--'}")
    print("  * meets both the 0.90 detection bar and the 0.10 clean bar")

    missed = [f for f in FAULTS if OD8_SUSTAINED[f] < DETECTION_BAR]
    rescued = {
        f: [s["detector"] for s in summary if s["fault"] == f and s["detects"]] for f in missed
    }
    any_rescued = any(v for v in rescued.values())
    breaches = [n for n in names if clean_fp[n] > CLEAN_BAR]

    if any_rescued:
        verdict = "BASELINE WINS"
    elif breaches and any(
        s["detection_rate"] >= DETECTION_BAR for s in summary if s["fault"] in missed
    ):
        verdict = "BASELINE IS TRIGGER-HAPPY"
    else:
        verdict = "OD-8 HOLDS"

    print(f"\nfaults OD-8 misses: {', '.join(missed)}")
    for fault, who in rescued.items():
        print(f"  {fault:<16} rescued by: {', '.join(who) if who else 'nobody'}")
    print(f"\nVERDICT (frozen rule): {verdict}")

    _OUT.joinpath("processed_results").mkdir(parents=True, exist_ok=True)
    _OUT.joinpath("processed_results", "summary.json").write_text(
        json.dumps(
            {
                "experiment_id": "E21-BASELINE",
                "seeds": len(seeds),
                "ticks": TICKS,
                "fault_first": FAULT_FIRST,
                "detection_bar": DETECTION_BAR,
                "clean_bar": CLEAN_BAR,
                "od8_sustained": OD8_SUSTAINED,
                "clean_false_positive": clean_fp,
                "cells": summary,
                "rescued": rescued,
                "verdict": verdict,
            },
            indent=2,
        )
    )
    print(f"elapsed {(time.time() - started) / 60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
