"""Stage C3 outcome analysis (offline; wired variant follows in Stage D).

Reads every committed raw JSONL under Stage A and Stage C1, then reports the
observed outcome metrics from `preregistration.md §2` on the RECORDED runs
(no counterfactual) and estimates the earliest tick a G2-triggered L6
abstention would have brought escalation forward to.

The full counterfactual requires an L8 state-machine replay driven by the
per-tick OOD / integrity counters. Because the L8 rules include hysteresis,
speed caps, capability withdrawal and manual-only HALT recovery
(`src/astra/layers/l8_failsafe/machine.py`), a faithful reconstruction is
its own module -- landed with the ADR that wires G2 -> L6 abstention in
Stage D. This module ships the honest first half: the actual
`ticks_in_nominal_faulted` and `escalation_tick` numbers, plus the
G2 fire ticks that Stage D will act on.

Usage
-----

::

    uv run python experiments/phase5_od8_h7/STEP4_OUTCOME_EXPERIMENT/stage_c3_outcome.py
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from astra.kernel.enums import StreamHealth  # noqa: E402
from benchmarks.g2_monitor import build_monitors  # noqa: E402

FAULT_ONSET = 200
STAGE_A_DIR = Path("experiments/phase5_od8_h7/STEP1_MECHANISM/raw_results")
STAGE_C1_DIR = Path("experiments/phase5_od8_h7/STEP2_MAGNITUDE_SWEEP/raw_results")


def _load_jsonl(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as fh:
        lines = [line.strip() for line in fh if line.strip()]
    return json.loads(lines[0]), [json.loads(line) for line in lines[1:]]


def _replay_record(row: dict[str, Any]) -> SimpleNamespace:
    """Same shape as the C2 evaluator's replay -- share the pattern."""
    score = row.get("non_conformity_score")
    gate_verdicts: tuple[SimpleNamespace, ...] = ()
    if score is not None:
        gate_verdicts = (
            SimpleNamespace(
                gate="GateId.STATISTICAL",
                evidence=(("non_conformity_score", float(score)),),
            ),
        )
    integrity = row.get("integrity_counter")
    health = StreamHealth.FAULTED if (integrity and int(integrity) > 0) else StreamHealth.HEALTHY
    return SimpleNamespace(
        safety_verdict=SimpleNamespace(gate_verdicts=gate_verdicts),
        frame_health=((SimpleNamespace(value="IMU"), health),),
    )


def _analyse_run(path: Path) -> dict[str, Any]:
    header, rows = _load_jsonl(path)
    arm = header.get("arm") or "faulted"
    fault = header.get("fault") or ""
    mag = header.get("magnitude_label") or "medium"
    onset = header.get("fault_onset_tick", FAULT_ONSET)

    # Observed L8 trajectory.
    faulted_rows = [r for r in rows if r["tick"] >= onset] if arm == "faulted" else rows
    nominal_ticks_faulted = sum(1 for r in faulted_rows if r.get("failsafe_state") == "NOMINAL")
    # First tick after onset where the state moved away from NOMINAL.
    escalation_tick: int | None = None
    for r in faulted_rows:
        state = r.get("failsafe_state")
        if state is not None and state != "NOMINAL":
            escalation_tick = int(r["tick"])
            break

    # G2 fire tick, replayed offline.
    monitors = build_monitors()
    fault_active = [r["tick"] >= onset for r in rows] if arm == "faulted" else [False] * len(rows)
    for i, r in enumerate(rows):
        record = _replay_record(r)
        for m in monitors:
            m.observe(record, tick=int(r["tick"]), fault_active=fault_active[i])
    g2 = next((m for m in monitors if m.name == "gate_blindness"), None)
    g2_fire_tick = g2.first_fire_tick if g2 is not None else None

    # Rough counterfactual estimate: if G2 fired T ticks after onset, and the
    # actual escalation happened at ET ticks after onset, the counterfactual
    # can bring escalation forward by max(0, ET - T) at best. The full L8
    # replay (Stage D) can bring it further via the integrity counter's own
    # dynamics; this is a lower-bound estimate.
    if arm == "faulted" and g2_fire_tick is not None and escalation_tick is not None:
        cf_earliest_escalation = max(g2_fire_tick, onset)
        cf_speedup_ticks = max(0, escalation_tick - cf_earliest_escalation)
    else:
        cf_earliest_escalation = None
        cf_speedup_ticks = None

    return {
        "fault": fault,
        "arm": arm,
        "seed": header.get("seed"),
        "magnitude_label": mag,
        "magnitude_value": header.get("magnitude_value"),
        "ticks_faulted": len(faulted_rows),
        "nominal_ticks_faulted": nominal_ticks_faulted,
        "nominal_fraction_faulted": (
            nominal_ticks_faulted / len(faulted_rows) if faulted_rows else 0.0
        ),
        "escalation_tick": escalation_tick,
        "g2_fire_tick": g2_fire_tick,
        "counterfactual_earliest_escalation": cf_earliest_escalation,
        "counterfactual_speedup_ticks": cf_speedup_ticks,
    }


def _iter_runs(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob("*.jsonl"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/phase5_od8_h7/STEP4_OUTCOME_EXPERIMENT/processed_results"),
    )
    parser.add_argument("--stage-a", type=Path, default=STAGE_A_DIR)
    parser.add_argument("--stage-c1", type=Path, default=STAGE_C1_DIR)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for source in (args.stage_a, args.stage_c1):
        for path in _iter_runs(source):
            rows.append(_analyse_run(path))

    if not rows:
        print("no runs found", file=sys.stderr)
        return 1

    # Aggregate per (fault, magnitude, arm).
    cells: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        cells[(r["fault"], r["magnitude_label"], r["arm"])].append(r)

    summary: list[dict[str, Any]] = []
    for (fault, mag, arm), group in sorted(cells.items()):
        nominal_fracs = [r["nominal_fraction_faulted"] for r in group]
        escalations = [r["escalation_tick"] for r in group if r["escalation_tick"] is not None]
        g2_fires = [r["g2_fire_tick"] for r in group if r["g2_fire_tick"] is not None]
        cf_speedups = [r["counterfactual_speedup_ticks"] for r in group
                       if r["counterfactual_speedup_ticks"] is not None]
        summary.append({
            "fault": fault,
            "magnitude_label": mag,
            "arm": arm,
            "n": len(group),
            "median_nominal_fraction_faulted": statistics.median(nominal_fracs),
            "median_escalation_tick": statistics.median(escalations) if escalations else None,
            "fraction_never_escalated": (
                sum(1 for r in group if r["escalation_tick"] is None) / len(group)
            ),
            "fraction_g2_fired": (
                sum(1 for r in group if r["g2_fire_tick"] is not None) / len(group)
            ),
            "median_g2_fire_tick": statistics.median(g2_fires) if g2_fires else None,
            "median_cf_speedup_ticks": statistics.median(cf_speedups) if cf_speedups else None,
        })

    out_json = args.out / "outcome_dev.json"
    out_json.write_text(
        json.dumps({"n_runs": len(rows), "per_cell": summary, "rows": rows}, indent=2),
        encoding="utf-8",
    )

    # Render a readable markdown summary.
    md = ["# Stage C3 -- Outcome (observed; counterfactual = lower bound)", ""]
    md.append(f"**Runs analysed:** {len(rows)}")
    md.append("")
    md.append("| fault | magnitude | arm | n | median nom-frac | escalation tick | never-esc | G2 fires | G2 tick | CF speed-up (lb) |")
    md.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for row in summary:
        esc = "--" if row["median_escalation_tick"] is None else str(row["median_escalation_tick"])
        g2t = "--" if row["median_g2_fire_tick"] is None else str(row["median_g2_fire_tick"])
        cfs = "--" if row["median_cf_speedup_ticks"] is None else str(row["median_cf_speedup_ticks"])
        md.append(
            f"| `{row['fault']}` | {row['magnitude_label']} | {row['arm']} | {row['n']} | "
            f"{row['median_nominal_fraction_faulted']:.3f} | {esc} | "
            f"{row['fraction_never_escalated']:.2f} | {row['fraction_g2_fired']:.2f} | "
            f"{g2t} | {cfs} |"
        )
    md.append("")
    md.append("**CF speed-up** = lower bound on the ticks the G2 monitor "
              "would have brought escalation forward by, if L6 were forced "
              "to abstain from the G2 fire tick. Full L8 counterfactual "
              "requires the abstention wiring landed by Stage D.")

    out_md = args.out / "final_decision_dev.md"
    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"wrote {out_json}")
    print(f"      {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
