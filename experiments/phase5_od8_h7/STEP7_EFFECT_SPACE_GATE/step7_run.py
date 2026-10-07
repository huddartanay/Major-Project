"""STEP 7 runner -- effect-space (lateral) gate score. See preregistration.md.

Usage (repository root):
    python experiments/phase5_od8_h7/STEP7_EFFECT_SPACE_GATE/step7_run.py calibrate
    python experiments/phase5_od8_h7/STEP7_EFFECT_SPACE_GATE/step7_run.py dev
    python experiments/phase5_od8_h7/STEP7_EFFECT_SPACE_GATE/step7_run.py heldout
"""

from __future__ import annotations

import importlib.util
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
from benchmarks.e21_baseline import (  # noqa: E402
    CHANNEL_SIGMAS,
    POLICY_PATH,
    _sensing_sustained,
    _severity,
)
from benchmarks.mechanism_logger import _l6_evidence  # noqa: E402
from training.closed_loop import DEFAULT_CHANNEL_SIGMAS, RedundantSensing, drive_closed_loop  # noqa: E402
from training.faults import FaultInjector  # noqa: E402

HERE = Path(__file__).parent
_s6_spec = importlib.util.spec_from_file_location(
    "step6_run", HERE.parent / "STEP6_MECHANISM_FROZEN_ESTIMATE" / "step6_run.py"
)
step6 = importlib.util.module_from_spec(_s6_spec)
_s6_spec.loader.exec_module(step6)  # type: ignore[union-attr]

SEEDS = {"calibrate": 20260901, "dev": 20260731, "heldout": 20270201}
N_SEEDS, TICKS, FAULT_FIRST = 30, 3400, 200
WINDOW = (400, 3400)
EFFECTIVENESS = (0.0, 0.0, 120.0)  # twin.control_effectiveness, development.toml
STEER = 2
ARMS = ("clean", "dropout", "dropout_noL8", "stuck", "position_bias")
THRESHOLD_FILE = HERE / "processed_results" / "threshold.json"


def lateral_score(proposed: tuple[float, ...], predicted: tuple[float, ...], sigma: float) -> float:
    implied = sum(b * p for b, p in zip(EFFECTIVENESS, proposed, strict=True))
    expected = sum(b * p for b, p in zip(EFFECTIVENESS, predicted, strict=True))
    return abs(implied - expected) / sigma


def drive(policy: object, arm: str, seed: int) -> dict[str, list[float] | dict[str, int] | int | None]:
    scores: list[float] = []
    steer_prop: list[float] = []
    steer_twin: list[float] = []
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
        sigma = _l6_evidence(sample)["sigma"]
        if math.isnan(sigma) or record.proposal is None or record.prediction is None:
            return
        proposed = tuple(float(v) for v in record.proposal.command.values)
        predicted = tuple(float(v) for v in record.prediction.command.values)
        scores.append(lateral_score(proposed, predicted, sigma))
        steer_prop.append(proposed[STEER])
        steer_twin.append(predicted[STEER])
        if record.fast_state is not None:
            gap.append(abs(float(record.fast_state.speed) - float(sample.speed_mps)))
        if record.failsafe is not None:
            name = record.failsafe.state.value
            states[name] = states.get(name, 0) + 1

    if arm == "position_bias":
        injector = FaultInjector((), seed=seed, sigmas=CHANNEL_SIGMAS)
        sensing = _sensing_sustained("position_bias", _severity("position_bias"), seed, active=True)
    else:
        injector = step6._injector(arm, seed)
        sensing = RedundantSensing.build(sigmas=DEFAULT_CHANNEL_SIGMAS, seed=seed)

    drive_closed_loop(
        policy=policy,
        ticks=TICKS,
        seed=seed,
        observer=observer,
        fault=injector,
        redundant=sensing,
        on_assembled=step6._neutralise_integrity if arm == "dropout_noL8" else None,
    )
    return {
        "scores": scores,
        "steer_prop": steer_prop,
        "steer_twin": steer_twin,
        "gap": gap,
        "states": states,
        "l1_first": l1_first[0] if l1_first else None,
    }


def _clean_tree() -> str | None:
    if subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip():
        return None
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def calibrate(policy: object, head: str) -> int:
    pooled: list[float] = []
    for i in range(N_SEEDS):
        seed = SEEDS["calibrate"] + i
        pooled.extend(drive(policy, "clean", seed)["scores"])  # type: ignore[arg-type]
        print(f"calibrate seed={seed} pooled={len(pooled)}", flush=True)
    pooled.sort()
    tau = pooled[min(len(pooled) - 1, int(0.95 * len(pooled)))]
    THRESHOLD_FILE.write_text(
        json.dumps(
            {
                "tau": tau,
                "quantile": 0.95,
                "n_scores": len(pooled),
                "seeds": f"{SEEDS['calibrate']}+i, i<{N_SEEDS}",
                "git_head": head,
                "pooled_p50": pooled[len(pooled) // 2],
                "pooled_sd": statistics.pstdev(pooled),
            },
            indent=1,
        )
    )
    print(f"tau = {tau}")
    return 0


def evaluate(policy: object, head: str, split: str) -> int:
    tau = float(json.loads(THRESHOLD_FILE.read_text())["tau"])
    rows: list[dict[str, object]] = []
    started = time.time()
    for i in range(N_SEEDS):
        seed = SEEDS[split] + i
        for arm in ARMS:
            d = drive(policy, arm, seed)
            s = sorted(d["scores"])  # type: ignore[arg-type]
            n = len(s)
            row = {
                "arm": arm,
                "seed": seed,
                "n_scored": n,
                "alarm_rate": sum(v > tau for v in s) / n,
                "score_p50": s[n // 2],
                "score_p95": s[min(n - 1, int(0.95 * n))],
                "score_sd": statistics.pstdev(s),
                "steer_prop_mean": statistics.fmean(d["steer_prop"]),  # type: ignore[arg-type]
                "steer_prop_sd": statistics.pstdev(d["steer_prop"]),  # type: ignore[arg-type]
                "steer_twin_mean": statistics.fmean(d["steer_twin"]),  # type: ignore[arg-type]
                "steer_twin_sd": statistics.pstdev(d["steer_twin"]),  # type: ignore[arg-type]
                "mean_abs_speed_gap": statistics.fmean(d["gap"]),  # type: ignore[arg-type]
                "l1_first_unhealthy_tick": d["l1_first"],
                "states": d["states"],
            }
            rows.append(row)
            print(f"[{time.time() - started:6.0f}s] {split} seed={seed} {arm:13s} alarm={row['alarm_rate']:.4f}", flush=True)
    out = HERE / "processed_results" / f"per_run_{split}.json"
    out.write_text(json.dumps({"split": split, "git_head": head, "tau": tau, "runs": rows}, indent=1))
    print(f"wrote {out}")
    return 0


def main() -> int:
    mode = sys.argv[1]
    head = _clean_tree()
    if head is None:
        print("refusing to run: working tree is dirty", file=sys.stderr)
        return 2
    policy = LearnedPolicy.load(POLICY_PATH)
    return calibrate(policy, head) if mode == "calibrate" else evaluate(policy, head, mode)


if __name__ == "__main__":
    raise SystemExit(main())
