"""Stage C1b analyser -- L1-vs-gate quadrants across dropout probabilities.

Same quadrant machinery as Stage C1's analyser, specialised to the four
probabilities defined in ``stage_c1b_run.py``. The pre-committed decision
in ``preregistration.md §5`` is applied verbatim:

  - Cell A non-empty for >= 2 probabilities -> PROCEED (paper G2 story complete).
  - Cell A non-empty for exactly 1 probability -> NARROW (G2's compelling case
    is total loss; the paper says so and Stage D still runs).
  - Cell A empty across all 4 -> WALK_AWAY (strictest off-ramp; committed
    up front so a marginal result cannot rescue the deadline).

Reads the runner's ``detector_summary.json`` for L1 answers and the raw
JSONL for gate alarm rates. Clean baseline is reused from Stage A
(seed-deterministic).
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

FROZEN_V3_P1 = 3.7024
FAULT_ONSET = 200
ANALYSIS_LO = 400
ANALYSIS_HI = 3399
SUPPRESSION_FACTOR = 0.5
L1_DETECT_MAJORITY = 15
N_SEEDS_EXPECTED = 30


def _alarm_rate(jsonl_path: Path, thr: float, lo: int, hi: int) -> float:
    if not jsonl_path.exists():
        return math.nan
    hits = 0
    total = 0
    with jsonl_path.open("r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i == 0:
                continue
            row = json.loads(line)
            if not lo <= row.get("tick", 0) <= hi:
                continue
            score = row.get("non_conformity_score")
            if not isinstance(score, (int, float)) or not math.isfinite(score):
                continue
            total += 1
            if score > thr:
                hits += 1
    return hits / total if total else math.nan


def _quadrant(l1_hits: int, faulted_median: float, clean_median: float) -> str:
    l1_yes = l1_hits >= L1_DETECT_MAJORITY
    gate_quiet = (
        math.isfinite(faulted_median)
        and math.isfinite(clean_median)
        and faulted_median <= SUPPRESSION_FACTOR * clean_median
    )
    if l1_yes and gate_quiet:
        return "A"
    if l1_yes and not gate_quiet:
        return "B"
    if not l1_yes and gate_quiet:
        return "C"
    return "D"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw",
        type=Path,
        default=Path("experiments/phase5_od8_h7/STEP5_SENSOR_LOSS_SWEEP/raw_results"),
    )
    parser.add_argument(
        "--stage-a-raw",
        type=Path,
        default=Path("experiments/phase5_od8_h7/STEP1_MECHANISM/raw_results"),
        help="Where clean-arm JSONL files live (deterministic, reused).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/phase5_od8_h7/STEP5_SENSOR_LOSS_SWEEP/processed_results"),
    )
    parser.add_argument("--suffix", default="dev")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    # If the caller asked for the held-out suffix but left the default
    # stage-a-raw path (dev), redirect to the held-out clean baseline. The
    # dev clean baseline has different seeds (20260731+i vs 20261201+i) so
    # the pairing would silently produce NaN and mis-classify every cell.
    stage_a_default = Path("experiments/phase5_od8_h7/STEP1_MECHANISM/raw_results")
    if args.suffix == "heldout" and args.stage_a_raw == stage_a_default:
        args.stage_a_raw = Path("experiments/phase5_od8_h7/STEP1_MECHANISM/raw_results_heldout")
        print(
            f"note: --suffix heldout with default --stage-a-raw; using "
            f"{args.stage_a_raw} for clean baseline instead.",
            file=sys.stderr,
        )

    detector_summary_path = args.raw / "detector_summary.json"
    if not detector_summary_path.exists():
        print(f"missing detector summary: {detector_summary_path}", file=sys.stderr)
        return 1
    runs: list[dict[str, Any]] = json.loads(detector_summary_path.read_text(encoding="utf-8"))

    # Group by probability label.
    by_prob: dict[str, list[dict[str, Any]]] = {}
    for r in runs:
        by_prob.setdefault(r["magnitude_label"], []).append(r)

    # Clean alarm rates per seed (paired baseline from Stage A).
    clean_by_seed: dict[int, float] = {}
    for r in runs:
        s = r["seed"]
        if s in clean_by_seed:
            continue
        clean_by_seed[s] = _alarm_rate(
            args.stage_a_raw / f"clean_{s}.jsonl", FROZEN_V3_P1, ANALYSIS_LO, ANALYSIS_HI
        )

    rows: list[dict[str, Any]] = []
    for prob_label, group in sorted(by_prob.items()):
        l1_hits = sum(1 for r in group if r["l1_detected"])
        faulted_rates = []
        clean_rates = []
        for r in group:
            f_path = args.raw / f"imu_dropout_{prob_label}_{r['seed']}.jsonl"
            faulted_rates.append(_alarm_rate(f_path, FROZEN_V3_P1, ANALYSIS_LO, ANALYSIS_HI))
            clean_rates.append(clean_by_seed.get(r["seed"], math.nan))
        finite_f = [x for x in faulted_rates if math.isfinite(x)]
        finite_c = [x for x in clean_rates if math.isfinite(x)]
        f_med = statistics.median(finite_f) if finite_f else math.nan
        c_med = statistics.median(finite_c) if finite_c else math.nan
        cell = _quadrant(l1_hits, f_med, c_med)
        rows.append({
            "magnitude_label": prob_label,
            "magnitude_value": group[0]["magnitude_value"],
            "n_seeds": len(group),
            "l1_detected_count": l1_hits,
            "faulted_alarm_median": f_med,
            "clean_alarm_median": c_med,
            "cell": cell,
        })

    cell_counts = Counter(r["cell"] for r in rows)
    n_cell_a = cell_counts.get("A", 0)
    if n_cell_a >= 2:
        overall = "PROCEED"
        message = (
            f"Cell A non-empty for {n_cell_a} of {len(rows)} probabilities "
            f"({[r['magnitude_label'] for r in rows if r['cell'] == 'A']}); "
            "the paper's G2 story is complete. Stage D proceeds."
        )
    elif n_cell_a == 1:
        prob = next(r["magnitude_label"] for r in rows if r["cell"] == "A")
        overall = "NARROW"
        message = (
            f"Cell A populated only at {prob}. Paper narrows the G2 story "
            f"to that probability; the framing states 'total IMU loss is "
            f"the compelling case, partial loss is out of scope for this paper'. "
            "Stage D still proceeds."
        )
    else:
        overall = "WALK_AWAY"
        message = (
            "Cell A empty across all four probabilities -- even the p=1.0 rerun "
            "did not reproduce the earlier committed evidence. Paper does not ship; "
            "Sushanth and Dr. Chaitra R. are notified on his return."
        )

    report = {
        "cell_counts": dict(cell_counts),
        "overall": overall,
        "message": message,
        "rows": rows,
    }
    (args.out / f"quadrant_table_{args.suffix}.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8",
    )

    md = [f"# Stage C1b -- Final Decision ({args.suffix})", "",
          f"**{overall}** -- {message}", "", "## Quadrant counts", ""]
    for cell in ("A", "B", "C", "D"):
        md.append(f"- **{cell}**: {cell_counts.get(cell, 0)}")
    md.append("")
    md.append("## Per-probability detail")
    md.append("")
    md.append("| probability | value | L1 (of 30) | gate faulted | gate clean | cell |")
    md.append("|---|---|---:|---:|---:|---:|")
    for r in rows:
        md.append(
            f"| {r['magnitude_label']} | {r['magnitude_value']:.2f} | "
            f"{r['l1_detected_count']} | {r['faulted_alarm_median']:.4f} | "
            f"{r['clean_alarm_median']:.4f} | **{r['cell']}** |"
        )
    (args.out / f"final_decision_{args.suffix}.md").write_text(
        "\n".join(md) + "\n", encoding="utf-8",
    )
    print(f"overall: {overall}")
    print(f"message: {message}")
    print(f"cells: {dict(cell_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
