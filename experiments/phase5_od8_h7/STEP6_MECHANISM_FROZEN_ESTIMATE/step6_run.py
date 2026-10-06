"""STEP 6 runner -- mechanism of the silent gate (see preregistration.md).

Usage (from the repository root):
    python experiments/phase5_od8_h7/STEP6_MECHANISM_FROZEN_ESTIMATE/step6_run.py dev
    python experiments/phase5_od8_h7/STEP6_MECHANISM_FROZEN_ESTIMATE/step6_run.py heldout

Writes one summary row per run to ``processed_results/per_run_<split>.json``. No raw tick logs are kept:
every statistic the pre-registration names is computed in the observer.
"""

from __future__ import annotations

import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")

from astra.kernel.enums import StreamHealth  # noqa: E402
from astra.layers.l4_proposer.learned import LearnedPolicy  # noqa: E402
from benchmarks.e21_baseline import CHANNEL_SIGMAS, POLICY_PATH  # noqa: E402
from benchmarks.mechanism_logger import _l6_evidence  # noqa: E402
from training.closed_loop import DEFAULT_CHANNEL_SIGMAS, RedundantSensing, drive_closed_loop  # noqa: E402
from training.faults import (  # noqa: E402
    FaultChannel,
    FaultInjector,
    FaultKind,
    dropout,
    stuck_at,
)

HERE = Path(__file__).parent
SEEDS = {"dev": 20260731, "heldout": 20270101}
N_SEEDS, TICKS, FAULT_FIRST = 30, 3400, 200
WINDOW = (400, 3400)
THRESHOLD = 3.7024
ARMS = ("clean", "dropout", "dropout_noL8", "stuck", "stuck_noise")
_BIG = 10**9


class NoisyStuckInjector(FaultInjector):
    """STUCK_AT whose held value is re-noised each tick at the declared channel sigma."""

    def _apply(self, spec, index, *, tick, channel, clean):  # type: ignore[no-untyped-def]
        if spec.kind is FaultKind.STUCK_AT:
            held = self._frozen.setdefault(index, clean)
            return held + self._random.gauss(0.0, self._sigmas[channel])
        return super()._apply(spec, index, tick=tick, channel=channel, clean=clean)


def _injector(arm: str, seed: int) -> FaultInjector:
    last = TICKS - 1
    if arm == "clean":
        return FaultInjector((), seed=seed, sigmas=CHANNEL_SIGMAS)
    if arm in {"dropout", "dropout_noL8"}:
        return FaultInjector(
            (dropout(first_tick=FAULT_FIRST, last_tick=last),), seed=seed, sigmas=CHANNEL_SIGMAS
        )
    specs = (
        stuck_at(FaultChannel.SPEED, first_tick=FAULT_FIRST, last_tick=last),
        stuck_at(FaultChannel.LATERAL_ACCELERATION, first_tick=FAULT_FIRST, last_tick=last),
    )
    cls = NoisyStuckInjector if arm == "stuck_noise" else FaultInjector
    return cls(specs, seed=seed, sigmas=CHANNEL_SIGMAS)


def _neutralise_integrity(built, *_):  # type: ignore[no-untyped-def]
    machine = built.pipeline._failsafe
    machine._settings = machine._settings.model_copy(
        update={
            "integrity_threshold_degraded": _BIG,
            "integrity_threshold_limp": _BIG,
            "integrity_threshold_halt": _BIG,
        }
    )


def run_one(policy: object, arm: str, seed: int) -> dict[str, object]:
    scores: list[float] = []
    est_speed: list[float] = []
    gap: list[float] = []
    states: dict[str, int] = {}
    l1_first: list[int] = []

    def observer(sample) -> None:  # type: ignore[no-untyped-def]
        record = sample.record
        if sample.tick >= FAULT_FIRST and not l1_first:
            if any(h is not StreamHealth.HEALTHY for _, h in record.frame_health):
                l1_first.append(int(sample.tick))
        if not (WINDOW[0] <= sample.tick < WINDOW[1]):
            return
        score = _l6_evidence(sample)["non_conformity_score"]
        if not math.isnan(score):
            scores.append(score)
        if record.fast_state is not None:
            v_est = float(record.fast_state.speed)
            est_speed.append(v_est)
            gap.append(abs(v_est - float(sample.speed_mps)))
        if record.failsafe is not None:
            name = record.failsafe.state.value
            states[name] = states.get(name, 0) + 1

    drive_closed_loop(
        policy=policy,
        ticks=TICKS,
        seed=seed,
        observer=observer,
        fault=_injector(arm, seed),
        redundant=RedundantSensing.build(sigmas=DEFAULT_CHANNEL_SIGMAS, seed=seed),
        on_assembled=_neutralise_integrity if arm == "dropout_noL8" else None,
    )
    ordered = sorted(scores)
    n = len(ordered)

    def q(p: float) -> float:
        return ordered[min(n - 1, int(p * n))]

    return {
        "arm": arm,
        "seed": seed,
        "n_scored": n,
        "alarm_rate": sum(s > THRESHOLD for s in ordered) / n,
        "score_p50": q(0.50),
        "score_p95": q(0.95),
        "score_p99": q(0.99),
        "score_sd": statistics.pstdev(ordered),
        "est_speed_sd": statistics.pstdev(est_speed),
        "mean_abs_speed_gap": statistics.fmean(gap),
        "l1_first_unhealthy_tick": l1_first[0] if l1_first else None,
        "states": states,
    }


def main() -> int:
    split = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else N_SEEDS
    if subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip():
        print("refusing to run: working tree is dirty", file=sys.stderr)
        return 2
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    policy = LearnedPolicy.load(POLICY_PATH)
    rows: list[dict[str, object]] = []
    started = time.time()
    for i in range(limit):
        seed = SEEDS[split] + i
        for arm in ARMS:
            rows.append(run_one(policy, arm, seed))
            print(f"[{time.time() - started:6.0f}s] {split} seed={seed} {arm:13s} "
                  f"alarm={rows[-1]['alarm_rate']:.4f}", flush=True)
    out = HERE / "processed_results" / f"per_run_{split}.json"
    out.write_text(json.dumps({"split": split, "git_head": head, "n_seeds": limit, "runs": rows}, indent=1))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
