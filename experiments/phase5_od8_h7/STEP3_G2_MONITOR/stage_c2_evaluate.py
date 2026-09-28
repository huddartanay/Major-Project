"""Stage C2 evaluator -- replays committed raw runs through every monitor.

Fast because it does not re-drive the pipeline. Reads the JSONL rows the
Stage A / Stage C1 runners emitted and reconstructs the minimum
``DecisionRecord``-shaped input each monitor needs. If Amoukou/D3M land
later, they slot into ``benchmarks.g2_monitor.ALL_MONITORS`` and the
analyser picks them up with no change here.

Usage
-----

::

    uv run python experiments/phase5_od8_h7/STEP3_G2_MONITOR/stage_c2_evaluate.py

Reads from Stage A's raw_results and Stage C1's raw_results (if present),
runs every monitor over each run, aggregates per (monitor, fault, magnitude)
across seeds, and writes a summary + a final_decision.md that applies
`preregistration.md` §5 verbatim.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from astra.kernel.enums import StreamHealth  # noqa: E402
from benchmarks.g2_monitor import ALL_MONITORS, build_monitors  # noqa: E402

STAGE_A_DIR = Path("experiments/phase5_od8_h7/STEP1_MECHANISM/raw_results")
STAGE_C1_DIR = Path("experiments/phase5_od8_h7/STEP2_MAGNITUDE_SWEEP/raw_results")
FAULT_ONSET = 200
CLEAN_BAR = 0.10  # from E21; matches pre-reg §5


@dataclass
class ReplayRecord:
    """A subset of ``DecisionRecord`` shape sufficient for every monitor."""

    safety_verdict: Any
    frame_health: Any


def _replay_from_row(row: dict[str, Any]) -> ReplayRecord:
    """Build a monitor-compatible record from a tick's JSONL row.

    Only three fields are needed: the L6 non-conformity score (as the
    STATISTICAL gate's evidence), and the L1 stream health boolean coded
    into a single-modality frame.
    """
    # L6 gate verdict, carrying the non-conformity score in evidence.
    score = row.get("non_conformity_score")
    if score is None:
        gate_verdicts = ()
    else:
        gate_verdicts = (
            SimpleNamespace(
                gate="GateId.STATISTICAL",
                evidence=(("non_conformity_score", float(score)),),
            ),
        )
    safety = SimpleNamespace(gate_verdicts=gate_verdicts)
    # L1 health: rely on integrity_counter movement rather than parsing a
    # per-modality health field, since the logger writes an integer counter
    # and not a StreamHealth enum. A non-zero integrity_counter reflects L1
    # having flagged something -- correlated with StreamHealth.FAULTED for
    # the purposes of this replay. If a run has integrity_counter == 0 the
    # tick is treated as healthy.
    integrity = row.get("integrity_counter")
    if integrity is not None and int(integrity) > 0:
        health = StreamHealth.FAULTED
    else:
        health = StreamHealth.HEALTHY
    return ReplayRecord(
        safety_verdict=safety,
        frame_health=((SimpleNamespace(value="IMU"), health),),
    )


def _load_run(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as fh:
        lines = [line.strip() for line in fh if line.strip()]
    return json.loads(lines[0]), [json.loads(line) for line in lines[1:]]


def _replay_one_run(path: Path) -> dict[str, dict[str, Any]] | None:
    header, ticks = _load_run(path)
    fault = header.get("fault") or ""
    arm = header.get("arm") or "faulted"
    n = len(ticks)
    if arm == "clean":
        fault_active = [False] * n
    else:
        onset = header.get("fault_onset_tick", FAULT_ONSET)
        fault_active = [t.get("tick", i) >= onset for i, t in enumerate(ticks)]
    monitors = build_monitors()
    for i, row in enumerate(ticks):
        record = _replay_from_row(row)
        for m in monitors:
            m.observe(record, tick=int(row.get("tick", i)), fault_active=fault_active[i])
    opened_at = next((i for i, v in enumerate(fault_active) if v), None)
    per_monitor: dict[str, dict[str, Any]] = {}
    for m in monitors:
        fire_tick = m.first_fire_tick
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
        per_monitor[m.name] = {
            "fired": fire_tick is not None,
            "first_fire_tick": fire_tick,
            "latency_ticks": latency,
            "false_alarm": false_alarm,
        }
    return {
        "fault": fault,
        "arm": arm,
        "seed": header.get("seed"),
        "magnitude_label": header.get("magnitude_label"),
        "magnitude_value": header.get("magnitude_value"),
        "n_ticks": n,
        "monitors": per_monitor,
    }


def _iter_runs(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob("*.jsonl"))


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Per (monitor, fault, magnitude_label): detection rate, median latency,
    clean false-alarm rate.
    """
    monitor_names = [cls().name for cls in ALL_MONITORS]
    clean_rows = [r for r in rows if r["arm"] == "clean"]
    faulted_rows = [r for r in rows if r["arm"] != "clean"]
    cells: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for r in faulted_rows:
        key = (r["fault"], r.get("magnitude_label") or "medium")
        cells.setdefault(key, []).append(r)

    per_monitor_clean_fp: dict[str, float] = {}
    for name in monitor_names:
        if not clean_rows:
            per_monitor_clean_fp[name] = 0.0
            continue
        fired = sum(1 for r in clean_rows if r["monitors"].get(name, {}).get("fired"))
        per_monitor_clean_fp[name] = fired / len(clean_rows)

    per_cell: list[dict[str, Any]] = []
    for (fault, mag_label), group in sorted(cells.items()):
        for name in monitor_names:
            entries = [r["monitors"].get(name, {}) for r in group]
            fired = [e for e in entries if e.get("fired") and not e.get("false_alarm")]
            latencies = [
                int(e["latency_ticks"]) for e in fired
                if e.get("latency_ticks") is not None
            ]
            per_cell.append({
                "monitor": name,
                "fault": fault,
                "magnitude_label": mag_label,
                "n_runs": len(group),
                "detection_rate": len(fired) / len(group) if group else 0.0,
                "median_latency_ticks": statistics.median(latencies) if latencies else None,
                "clean_fp_rate": per_monitor_clean_fp[name],
            })
    return {
        "clean_fp_by_monitor": per_monitor_clean_fp,
        "per_cell": per_cell,
    }


def _apply_pass_rule(agg: dict[str, Any]) -> dict[str, Any]:
    """Apply preregistration.md §5 verbatim to `imu_dropout` at medium."""
    l1 = _lookup(agg, "l1_only", "imu_dropout", "medium")
    g2 = _lookup(agg, "gate_blindness", "imu_dropout", "medium")
    if l1 is None or g2 is None:
        return {
            "primary_result": "MISSING_DATA",
            "message": "Stage A raw_results not present or imu_dropout / medium missing.",
        }
    l1_latency = l1.get("median_latency_ticks") or float("inf")
    g2_latency = g2.get("median_latency_ticks") or float("inf")
    passes = (
        g2["detection_rate"] >= l1["detection_rate"]
        and g2_latency <= 2.0 * l1_latency
        and g2["clean_fp_rate"] <= CLEAN_BAR
    )
    result = "PASS" if passes else "FAIL"
    return {
        "primary_result": result,
        "gate_blindness": g2,
        "l1_only": l1,
        "detail": (
            f"gate_blindness detection={g2['detection_rate']:.3f} vs l1_only {l1['detection_rate']:.3f}; "
            f"gate_blindness latency={g2_latency} vs l1_only {l1_latency}; "
            f"gate_blindness clean_fp={g2['clean_fp_rate']:.3f} (bar {CLEAN_BAR})"
        ),
    }


def _lookup(agg: dict[str, Any], monitor: str, fault: str, mag: str) -> dict[str, Any] | None:
    for row in agg["per_cell"]:
        if row["monitor"] == monitor and row["fault"] == fault and row["magnitude_label"] == mag:
            return row
    return None


def _render_md(agg: dict[str, Any], decision: dict[str, Any], header: dict[str, Any]) -> str:
    lines = ["# Stage C2 -- Final Decision (dev)", ""]
    lines.append(f"**Runs evaluated:** {header['n_runs_faulted']} faulted, "
                 f"{header['n_runs_clean']} clean")
    lines.append(f"**Sources:** {header['sources']}")
    lines.append("")
    lines.append(f"## Primary result: **{decision['primary_result']}**")
    lines.append("")
    lines.append(decision.get("detail", ""))
    lines.append("")
    lines.append("## Clean false-alarm rate per monitor")
    lines.append("")
    lines.append("| monitor | clean FP |")
    lines.append("|---|---:|")
    for m, fp in agg["clean_fp_by_monitor"].items():
        lines.append(f"| `{m}` | {fp:.3f} |")
    lines.append("")
    lines.append("## Per-(fault, magnitude) detection")
    lines.append("")
    lines.append("| monitor | fault | magnitude | n | detection | median latency | clean FP |")
    lines.append("|---|---|---|---:|---:|---:|---:|")
    for row in agg["per_cell"]:
        lat = "--" if row["median_latency_ticks"] is None else str(row["median_latency_ticks"])
        lines.append(
            f"| `{row['monitor']}` | `{row['fault']}` | {row['magnitude_label']} | "
            f"{row['n_runs']} | {row['detection_rate']:.3f} | {lat} | "
            f"{row['clean_fp_rate']:.3f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/phase5_od8_h7/STEP3_G2_MONITOR/processed_results"),
    )
    parser.add_argument("--stage-a", type=Path, default=STAGE_A_DIR)
    parser.add_argument("--stage-c1", type=Path, default=STAGE_C1_DIR)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    sources: list[str] = []
    for source in (args.stage_a, args.stage_c1):
        run_paths = _iter_runs(source)
        if not run_paths:
            continue
        sources.append(str(source))
        for path in run_paths:
            run_result = _replay_one_run(path)
            if run_result is not None:
                rows.append(run_result)

    if not rows:
        print("no runs found in any source directory", file=sys.stderr)
        return 1

    agg = _aggregate(rows)
    decision = _apply_pass_rule(agg)
    header = {
        "sources": ", ".join(sources) or "(none)",
        "n_runs_faulted": sum(1 for r in rows if r["arm"] != "clean"),
        "n_runs_clean": sum(1 for r in rows if r["arm"] == "clean"),
    }

    (args.out / "monitor_evaluation.json").write_text(
        json.dumps({"header": header, "decision": decision, "aggregate": agg},
                   indent=2),
        encoding="utf-8",
    )
    (args.out / "final_decision_dev.md").write_text(
        _render_md(agg, decision, header), encoding="utf-8",
    )
    print(f"primary_result: {decision['primary_result']}")
    print(decision.get("detail", ""))
    print(f"wrote {args.out / 'monitor_evaluation.json'}")
    print(f"      {args.out / 'final_decision_dev.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
