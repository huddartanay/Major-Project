"""Stage C1 analyser -- L1-vs-gate quadrant table for the magnitude sweep.

Reads the C1 runner's per-run detector summary and, for each (fault,
magnitude) cell, the paired Stage A clean-run raw JSONL to compute the gate
alarm rate over ticks 400-3399 at the frozen threshold. Places every cell in
one of A / B / C / D per §4 of ``preregistration.md`` and applies the
pre-committed rule in §5.

Nothing here is tuned to the data. All thresholds are constants imported
from the pre-registration.
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
CLEAN_BASELINE_ALARM_RATE = 0.05
SUPPRESSION_FACTOR = 0.5
L1_DETECT_MAJORITY = 15
N_SEEDS_EXPECTED = 30


def _reconstruct_detector_summary(raw_dir: Path) -> list[dict[str, Any]]:
    """Rebuild the runner's detector_summary.json from JSONL when it is missing.

    Proxy for L1 detection: the earliest tick at or after the fault onset
    where ``integrity_counter`` first exceeds 0. This is what the C2 evaluator
    also uses; the runner's live detector call is more precise (E21's
    `health` uses stream-freshness metadata not in the JSONL) but the proxy
    matches on the sustained-fault runs where L1 stays engaged.
    """
    out: list[dict[str, Any]] = []
    for path in sorted(raw_dir.glob("*.jsonl")):
        try:
            with path.open("r", encoding="utf-8") as fh:
                lines = [line.strip() for line in fh if line.strip()]
            if len(lines) < 2:
                continue
            header = json.loads(lines[0])
            first_fire: int | None = None
            for line in lines[1:]:
                row = json.loads(line)
                integrity = row.get("integrity_counter")
                if integrity is not None and int(integrity) > 0:
                    first_fire = int(row.get("tick", 0))
                    break
            fault = header.get("fault", "")
            arm = header.get("arm", "faulted")
            onset = header.get("fault_onset_tick", FAULT_ONSET)
            l1_detected = (
                arm == "faulted"
                and first_fire is not None
                and first_fire >= onset
            )
            out.append({
                "fault": fault,
                "magnitude_label": header.get("magnitude_label", "medium"),
                "magnitude_value": header.get("magnitude_value"),
                "seed": header.get("seed"),
                "l1_detected": bool(l1_detected),
                "l1_first_fire_tick": first_fire,
                "l1_latency_ticks": (
                    first_fire - onset if l1_detected and first_fire is not None else None
                ),
                "l1_false_alarm": bool(
                    first_fire is not None and (arm == "clean" or first_fire < onset)
                ),
                "n_ticks": len(lines) - 1,
            })
        except (OSError, json.JSONDecodeError):
            continue
    return out


def _tick_score_alarm_rate(jsonl_path: Path, thr: float, lo: int, hi: int) -> float:
    """Alarm rate `score > thr` over ticks [lo, hi] for a run JSONL file."""
    if not jsonl_path.exists():
        return math.nan
    hits = 0
    total = 0
    with jsonl_path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh):
            if line_no == 0:  # header
                continue
            row = json.loads(line)
            if not lo <= row["tick"] <= hi:
                continue
            score = row.get("non_conformity_score")
            if score is None or not isinstance(score, (int, float)) or not math.isfinite(score):
                continue
            total += 1
            if score > thr:
                hits += 1
    return hits / total if total else math.nan


def _quadrant(
    l1_detected_count: int,
    n_seeds: int,
    faulted_alarm_median: float,
    clean_alarm_median: float,
) -> str:
    """Return the cell label per §4 of the pre-reg."""
    l1_hits = l1_detected_count >= L1_DETECT_MAJORITY
    gate_quiet = (
        math.isfinite(faulted_alarm_median)
        and math.isfinite(clean_alarm_median)
        and faulted_alarm_median <= SUPPRESSION_FACTOR * clean_alarm_median
    )
    if l1_hits and gate_quiet:
        return "A"
    if l1_hits and not gate_quiet:
        return "B"
    if not l1_hits and gate_quiet:
        return "C"
    return "D"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw",
        type=Path,
        default=Path("experiments/phase5_od8_h7/STEP2_MAGNITUDE_SWEEP/raw_results"),
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
        default=Path("experiments/phase5_od8_h7/STEP2_MAGNITUDE_SWEEP/processed_results"),
    )
    parser.add_argument("--suffix", default="dev")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    detector_summary_path = args.raw / "detector_summary.json"
    if detector_summary_path.exists():
        runs: list[dict[str, Any]] = json.loads(detector_summary_path.read_text(encoding="utf-8"))
    else:
        # Salvage path: if the runner crashed before writing the summary,
        # reconstruct L1's per-run answer from the JSONL directly. The proxy
        # is the failsafe integrity_counter: >0 means L1 has been flagging
        # something. First tick with integrity_counter > 0 is L1's first-fire
        # tick. Same approximation the C2 evaluator uses; documented in
        # experiments/phase5_od8_h7/STEP3_G2_MONITOR/stage_c2_evaluate.py.
        print(
            f"note: {detector_summary_path} missing; reconstructing L1 "
            f"detection from integrity_counter in raw JSONL",
            file=sys.stderr,
        )
        runs = _reconstruct_detector_summary(args.raw)
        if not runs:
            print(f"no raw JSONL files under {args.raw}", file=sys.stderr)
            return 1

    # Group by (fault, magnitude_label) -> list of runs.
    cells: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for run in runs:
        key = (run["fault"], run["magnitude_label"])
        cells.setdefault(key, []).append(run)

    # Also collect clean-arm alarm rates once per seed for the paired comparison.
    clean_alarm_by_seed: dict[int, float] = {}
    for run in runs:
        seed = run["seed"]
        if seed in clean_alarm_by_seed:
            continue
        clean_path = args.stage_a_raw / f"clean_{seed}.jsonl"
        clean_alarm_by_seed[seed] = _tick_score_alarm_rate(
            clean_path, FROZEN_V3_P1, ANALYSIS_LO, ANALYSIS_HI
        )

    rows: list[dict[str, Any]] = []
    for (fault, mag_label), group in sorted(cells.items()):
        l1_hits = sum(1 for r in group if r["l1_detected"])
        # Compute faulted alarm rate per run from the raw JSONL.
        faulted_rates = []
        clean_rates = []
        for r in group:
            faulted_path = args.raw / f"{fault}_{mag_label}_{r['seed']}.jsonl"
            faulted_rates.append(
                _tick_score_alarm_rate(faulted_path, FROZEN_V3_P1, ANALYSIS_LO, ANALYSIS_HI)
            )
            clean_rates.append(clean_alarm_by_seed.get(r["seed"], math.nan))
        finite_f = [x for x in faulted_rates if math.isfinite(x)]
        finite_c = [x for x in clean_rates if math.isfinite(x)]
        f_med = statistics.median(finite_f) if finite_f else math.nan
        c_med = statistics.median(finite_c) if finite_c else math.nan
        cell = _quadrant(l1_hits, len(group), f_med, c_med)
        rows.append({
            "fault": fault,
            "magnitude_label": mag_label,
            "magnitude_value": group[0]["magnitude_value"],
            "n_seeds": len(group),
            "l1_detected_count": l1_hits,
            "faulted_alarm_median": f_med,
            "clean_alarm_median": c_med,
            "cell": cell,
        })

    cell_counts = Counter(r["cell"] for r in rows)
    cell_a_rows = [r for r in rows if r["cell"] == "A"]
    cell_a_by_fault: dict[str, int] = {}
    for r in cell_a_rows:
        cell_a_by_fault[r["fault"]] = cell_a_by_fault.get(r["fault"], 0) + 1

    n_faults_with_cell_a = len(cell_a_by_fault)
    if n_faults_with_cell_a >= 2:
        overall = "PROCEED_TO_STAGE_C2"
        message = (
            f"Cell A non-empty for {n_faults_with_cell_a} faults "
            f"({sorted(cell_a_by_fault.keys())}); Stage C2 proceeds with those pairs."
        )
    else:
        overall = "WALK_AWAY_OR_SHIFT"
        message = (
            "Cell A empty or single-fault; ITSC contribution has to shift, "
            "or Paper 1 walks away. See preregistration.md §5."
        )

    report = {
        "cell_counts": dict(cell_counts),
        "cell_a_by_fault": cell_a_by_fault,
        "overall": overall,
        "message": message,
        "rows": rows,
    }
    (args.out / f"quadrant_table_{args.suffix}.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8",
    )

    md_lines = [f"# Stage C1 -- Final Decision ({args.suffix})", "", f"**{overall}** -- {message}", ""]
    md_lines.append("## Quadrant counts\n")
    for cell in ("A", "B", "C", "D"):
        md_lines.append(f"- **{cell}**: {cell_counts.get(cell, 0)}")
    md_lines.append("\n## Per-cell detail\n")
    md_lines.append("| fault | magnitude | value | L1 (of 30) | gate faulted | gate clean | cell |")
    md_lines.append("|---|---|---|---|---|---|---|")
    for r in rows:
        md_lines.append(
            f"| `{r['fault']}` | {r['magnitude_label']} | {r['magnitude_value']:.3f} | "
            f"{r['l1_detected_count']} | {r['faulted_alarm_median']:.4f} | "
            f"{r['clean_alarm_median']:.4f} | **{r['cell']}** |"
        )
    (args.out / f"final_decision_{args.suffix}.md").write_text(
        "\n".join(md_lines) + "\n", encoding="utf-8",
    )

    print(f"overall: {overall}")
    print(f"message: {message}")
    print(f"cell counts: {dict(cell_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
