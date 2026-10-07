"""STEP 7 analyser -- applies preregistration.md §5-§7 verbatim.

Usage: python experiments/phase5_od8_h7/STEP7_EFFECT_SPACE_GATE/step7_analyse.py dev
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).parent
FAULT_ARMS = ("dropout", "dropout_noL8", "stuck", "position_bias")
RESAMPLES = 2000


def _summary(ratios: list[float]) -> dict[str, float]:
    rng = random.Random(20261007)
    meds = sorted(statistics.median(rng.choices(ratios, k=len(ratios))) for _ in range(RESAMPLES))
    return {
        "median": statistics.median(ratios),
        "lo": meds[int(0.025 * RESAMPLES)],
        "hi": meds[int(0.975 * RESAMPLES) - 1],
        "n": len(ratios),
    }


def classify(s: dict[str, float]) -> str:
    if s["median"] <= 0.25 and s["hi"] < 0.50:
        return "SUPPRESSED"
    if s["median"] >= 2.0 and s["lo"] > 1.0:
        return "DETECTS"
    if 0.5 <= s["median"] <= 2.0 and s["lo"] >= 0.25 and s["hi"] <= 4.0:
        return "UNCHANGED"
    return "INCONCLUSIVE"


def main() -> int:
    split = sys.argv[1]
    data = json.loads((HERE / "processed_results" / f"per_run_{split}.json").read_text())
    by = {(r["arm"], r["seed"]): r for r in data["runs"]}
    seeds = sorted({r["seed"] for r in data["runs"]})
    clean_rates = [by[("clean", s)]["alarm_rate"] for s in seeds]
    in_band = sum(0.025 <= r <= 0.10 for r in clean_rates)
    excluded = [s for s in seeds if by[("clean", s)]["alarm_rate"] == 0]
    used = [s for s in seeds if s not in excluded]

    ratios = {
        arm: _summary([by[(arm, s)]["alarm_rate"] / by[("clean", s)]["alarm_rate"] for s in used])
        for arm in FAULT_ARMS
    }
    classes = {arm: classify(ratios[arm]) for arm in FAULT_ARMS}

    p_cal = in_band >= 24
    p_sens = classes["position_bias"] == "DETECTS"
    pair = {classes["dropout_noL8"], classes["stuck"]}
    if not (p_cal and p_sens):
        outcome = "NO-VALID-GATE"
    elif "DETECTS" in pair:
        outcome = "G1-ARTEFACT"
    elif pair == {"SUPPRESSED"}:
        outcome = "G1-SILENT"
    elif pair <= {"UNCHANGED", "SUPPRESSED"} and "UNCHANGED" in pair:
        outcome = "G1-BLIND"
    else:
        outcome = "MIXED / INCONCLUSIVE"

    def med(arm: str, key: str) -> float:
        return statistics.median(by[(arm, s)][key] for s in seeds)

    arms = ("clean", *FAULT_ARMS)
    lines = [
        f"# STEP 7 -- decision ({split})",
        "",
        f"Runs: {len(data['runs'])}. Code at `{data['git_head'][:7]}`. Threshold tau = {data['tau']:.6f}.",
        "",
        f"## Outcome: **{outcome}**",
        "",
        "## Preconditions",
        "",
        f"- P-cal: {in_band}/30 clean runs with alarm rate in [0.025, 0.10] -> **{'PASS' if p_cal else 'FAIL'}** "
        f"(clean median {statistics.median(clean_rates):.4f}, min {min(clean_rates):.4f}, max {max(clean_rates):.4f})",
        f"- P-sens: position_bias is {classes['position_bias']} -> **{'PASS' if p_sens else 'FAIL'}**",
        f"- Seeds excluded from ratios (clean alarm rate 0): {len(excluded)}",
        "",
        "## Paired alarm-rate ratio to clean",
        "",
        "| arm | median | 95 % interval | n | class |",
        "|---|---:|---|---:|---|",
        *[
            f"| {a} | {ratios[a]['median']:.3f} | [{ratios[a]['lo']:.3f}, {ratios[a]['hi']:.3f}] | {ratios[a]['n']} | **{classes[a]}** |"
            for a in FAULT_ARMS
        ],
        "",
        "## Per-arm medians (descriptive)",
        "",
        "| arm | alarm rate | s_lat p50 | s_lat p95 | s_lat sd | steer proposal sd | steer twin sd | mean abs speed gap | L1 unhealthy |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        *[
            f"| {a} | {med(a, 'alarm_rate'):.4f} | {med(a, 'score_p50'):.4f} | {med(a, 'score_p95'):.4f} | "
            f"{med(a, 'score_sd'):.4f} | {med(a, 'steer_prop_sd'):.5f} | {med(a, 'steer_twin_sd'):.5f} | "
            f"{med(a, 'mean_abs_speed_gap'):.2f} | "
            f"{sum(by[(a, s)]['l1_first_unhealthy_tick'] is not None for s in seeds)}/{len(seeds)} |"
            for a in arms
        ],
        "",
    ]
    (HERE / "processed_results" / f"final_decision_{split}.md").write_text("\n".join(lines), encoding="utf-8")
    (HERE / "processed_results" / f"verdict_{split}.json").write_text(
        json.dumps(
            {"outcome": outcome, "classes": classes, "ratios": ratios, "p_cal_in_band": in_band, "p_sens": p_sens},
            indent=1,
        )
    )
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
