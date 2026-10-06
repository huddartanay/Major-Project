"""STEP 6 analyser -- applies preregistration.md §5 verbatim.

Usage: python experiments/phase5_od8_h7/STEP6_MECHANISM_FROZEN_ESTIMATE/step6_analyse.py dev
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).parent
FAULT_ARMS = ("dropout", "dropout_noL8", "stuck", "stuck_noise")
RESAMPLES = 2000


def _ratio_summary(ratios: list[float]) -> dict[str, float]:
    rng = random.Random(20261006)
    meds = sorted(
        statistics.median(rng.choices(ratios, k=len(ratios))) for _ in range(RESAMPLES)
    )
    return {
        "median": statistics.median(ratios),
        "lo": meds[int(0.025 * RESAMPLES)],
        "hi": meds[int(0.975 * RESAMPLES) - 1],
        "n": len(ratios),
    }


def _suppressed(s: dict[str, float]) -> bool:
    return s["median"] <= 0.25 and s["hi"] < 0.50


def _restored(s: dict[str, float]) -> bool:
    return 0.50 <= s["median"] <= 2.00 and s["lo"] > 0.25


def main() -> int:
    split = sys.argv[1]
    data = json.loads((HERE / "processed_results" / f"per_run_{split}.json").read_text())
    by = {(r["arm"], r["seed"]): r for r in data["runs"]}
    seeds = sorted({r["seed"] for r in data["runs"]})
    excluded = [s for s in seeds if by[("clean", s)]["alarm_rate"] == 0]
    used = [s for s in seeds if s not in excluded]

    summary: dict[str, dict[str, float]] = {}
    for arm in FAULT_ARMS:
        summary[arm] = _ratio_summary(
            [by[(arm, s)]["alarm_rate"] / by[("clean", s)]["alarm_rate"] for s in used]
        )

    def verdict(supported: bool, refuted: bool) -> str:
        return "SUPPORTED" if supported else "REFUTED" if refuted else "INCONCLUSIVE"

    verdicts = {
        "H-indep": verdict(_suppressed(summary["dropout_noL8"]), summary["dropout_noL8"]["median"] > 0.50),
        "H-freeze": verdict(_suppressed(summary["stuck"]), summary["stuck"]["median"] > 0.50),
        "H-noise": verdict(
            _suppressed(summary["stuck"]) and _restored(summary["stuck_noise"]),
            _suppressed(summary["stuck_noise"]),
        ),
    }

    def med(arm: str, key: str) -> float:
        return statistics.median(by[(arm, s)][key] for s in seeds)

    arms = ("clean", *FAULT_ARMS)
    lines = [
        f"# STEP 6 -- decision ({split})",
        "",
        f"Runs: {len(data['runs'])} ({len(seeds)} seeds x {len(arms)} arms). Code at `{data['git_head'][:7]}`.",
        f"Seeds excluded from ratios (clean alarm rate 0): {len(excluded)}.",
        "",
        "## Verdicts (preregistration §5)",
        "",
        *[f"- **{k}: {v}**" for k, v in verdicts.items()],
        "",
        "## Paired alarm-rate ratio to clean (median over seeds, 95 % bootstrap interval)",
        "",
        "| arm | median | 95 % interval | n |",
        "|---|---:|---|---:|",
        *[
            f"| {a} | {summary[a]['median']:.3f} | [{summary[a]['lo']:.3f}, {summary[a]['hi']:.3f}] | {summary[a]['n']} |"
            for a in FAULT_ARMS
        ],
        "",
        "## Per-arm medians (descriptive)",
        "",
        "| arm | alarm rate | score p50 | score p95 | score sd | est. speed sd | mean abs speed gap (m/s) | L1 unhealthy (runs) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        *[
            f"| {a} | {med(a, 'alarm_rate'):.4f} | {med(a, 'score_p50'):.4f} | {med(a, 'score_p95'):.4f} | "
            f"{med(a, 'score_sd'):.4f} | {med(a, 'est_speed_sd'):.5f} | {med(a, 'mean_abs_speed_gap'):.2f} | "
            f"{sum(by[(a, s)]['l1_first_unhealthy_tick'] is not None for s in seeds)}/{len(seeds)} |"
            for a in arms
        ],
        "",
    ]
    (HERE / "processed_results" / f"final_decision_{split}.md").write_text("\n".join(lines), encoding="utf-8")
    (HERE / "processed_results" / f"verdict_{split}.json").write_text(
        json.dumps({"verdicts": verdicts, "ratios": summary, "excluded_seeds": excluded}, indent=1)
    )
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
