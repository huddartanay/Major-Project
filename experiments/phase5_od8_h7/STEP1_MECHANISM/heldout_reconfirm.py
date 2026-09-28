"""Held-out re-confirmation of the two headline G1 numbers.

Why this exists
---------------
Handoff §0.3: R3c's 0/30 (the gate goes silent under sustained ``imu_dropout``)
and E21's L1 30/30 (stream health catches the same fault in ~5 ticks with
zero clean false alarms) were both established on dev seeds
(``BASE_SEED = 20260731``). Paper 1 cannot cite either as a held-out number
until the same procedure is repeated on the held-out set
(``BASE_SEED = 20261201``) with nothing else changed.

Stage A's held-out sweep already produces the per-tick scores needed to
recover R3c's number, so the R3c side of §0.3 is folded into
``stage_a_run.py --base-seed 20261201``. This script covers the E21 side --
it invokes the exact detectors E21 wrote (unchanged) against 30 held-out
clean runs and 30 held-out ``imu_dropout`` runs, then reports the L1
detection rate, median latency, and clean false-alarm rate.

Wall time: about 7 min for 60 runs of 3,400 ticks.

Usage::

    uv run python experiments/phase5_od8_h7/STEP1_MECHANISM/heldout_reconfirm.py
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from astra.layers.l4_proposer.learned import LearnedPolicy  # noqa: E402
from benchmarks.detectors import DETECTORS  # noqa: E402
from benchmarks.e21_baseline import run_one  # noqa: E402

HELD_OUT_BASE_SEED = 20261201
N_SEEDS = 30
POLICY_PATH = Path("var/policy/synthetic.pt")
FAULT = "imu_dropout"

# The dev numbers we are trying to reproduce. Held-out numbers within tight
# margins of these confirm §0.3 -- Paper 1 can then cite either as
# held-out-confirmed. Widely different numbers -- e.g. L1 detection dropping
# below 0.90 -- would say the dev result did not generalise, and Paper 1
# would need to soften the claim.
DEV_L1_DETECTION_RATE = 30 / 30
DEV_L1_MEDIAN_LATENCY_TICKS = 5
DEV_L1_CLEAN_FP_RATE = 0 / 30

DETECTION_BAR = 0.90
CLEAN_BAR = 0.10


def _l1_name() -> str:
    """Look up whatever L1's detector is called in this build.

    E21's L1 is the stream-health detector; the string identifier lives in
    ``benchmarks.detectors``. Hard-coding the name here would drift; asking
    the module keeps this script correct across renames.
    """
    for detector in DETECTORS:
        if "stream" in detector.name.lower() or "l1" in detector.name.lower():
            return detector.name
    # Fall back to first detector rather than crashing -- lets a diagnostic
    # run still complete, and the return value is inspected in the report.
    return DETECTORS[0].name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/phase5_od8_h7/STEP1_MECHANISM/processed_results"),
    )
    parser.add_argument("--base-seed", type=int, default=HELD_OUT_BASE_SEED)
    parser.add_argument("--seeds", type=int, default=N_SEEDS)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    if args.base_seed == 20260731:
        print(
            "warning: base-seed 20260731 IS the dev set. Re-running here is a "
            "regression test, not a held-out confirmation.",
            file=sys.stderr,
        )

    seeds = [args.base_seed + i for i in range(args.seeds)]
    policy = LearnedPolicy.load(POLICY_PATH)
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()

    print(f"held-out reconfirmation: {args.seeds} clean + {args.seeds} {FAULT} runs")
    print(f"base seed: {args.base_seed}, threshold set by benchmarks/detectors.py\n")

    rows: list[dict[str, Any]] = []
    t0 = time.time()
    for arm in ("clean", FAULT):
        arm_start = time.time()
        for seed in seeds:
            arm_kind = None if arm == "clean" else arm
            rows.extend(run_one(policy, arm_kind, seed))
        print(f"  {arm:<16} {args.seeds} runs   elapsed {(time.time() - arm_start) / 60:.1f} min",
              flush=True)

    l1_name = _l1_name()

    # L1 numbers on the faulted arm.
    l1_faulted = [r for r in rows if r["fault"] == FAULT and r["detector"] == l1_name]
    l1_detected = [r for r in l1_faulted if r["detected"]]
    l1_lat = [int(r["latency_ticks"]) for r in l1_detected if r["latency_ticks"] is not None]
    detection_rate = len(l1_detected) / len(l1_faulted) if l1_faulted else float("nan")
    median_lat = statistics.median(l1_lat) if l1_lat else None

    # L1 clean false alarms.
    l1_clean = [r for r in rows if r["fault"] == "clean" and r["detector"] == l1_name]
    clean_fp_rate = sum(1 for r in l1_clean if r["detected"]) / len(l1_clean) if l1_clean else float("nan")

    passed = (
        detection_rate >= DETECTION_BAR
        and clean_fp_rate <= CLEAN_BAR
        and (median_lat is None or median_lat <= DEV_L1_MEDIAN_LATENCY_TICKS * 2)
    )
    verdict = "CONFIRMED" if passed else "NOT CONFIRMED"

    report = {
        "base_seed": args.base_seed,
        "n_seeds": args.seeds,
        "detector": l1_name,
        "detection_rate": detection_rate,
        "median_latency_ticks": median_lat,
        "clean_fp_rate": clean_fp_rate,
        "dev_detection_rate": DEV_L1_DETECTION_RATE,
        "dev_median_latency_ticks": DEV_L1_MEDIAN_LATENCY_TICKS,
        "dev_clean_fp_rate": DEV_L1_CLEAN_FP_RATE,
        "verdict": verdict,
        "git_sha": git_sha,
        "wall_secs": round(time.time() - t0, 2),
    }
    out_path = args.out / "e21_l1_heldout.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\ndetector: {l1_name}")
    print(f"  detection rate on held-out {FAULT}: {detection_rate:.3f}  "
          f"(dev = {DEV_L1_DETECTION_RATE:.3f})")
    print(f"  median latency (ticks):            {median_lat}  "
          f"(dev = {DEV_L1_MEDIAN_LATENCY_TICKS})")
    print(f"  clean false-alarm rate:            {clean_fp_rate:.3f}  "
          f"(dev = {DEV_L1_CLEAN_FP_RATE:.3f})")
    print(f"\n=> {verdict}")
    print(f"wrote {out_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
