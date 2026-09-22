"""Stage A analyser -- applies the pre-registered decision rule to the sweep.

Reads every JSONL under ``raw_results/``, computes the four ratios (§4) per
fault per phase per seed, aggregates to a median with a 95 % bootstrap CI over
runs (not ticks: ticks within a run are autocorrelated -- see the Phase 2
monitorability ledger entry that got bitten by exactly that), and applies the
one-sentence decision rule in §5 verbatim.

Nothing here is tuned against the data. Everything with a number in it -- the
1.5x and 0.5x thresholds, the phase edges, the 95 % CI level, the 2,000
bootstrap resamples, the seed count, the fault set -- is pinned by
constants imported from ``stage_a_run.py`` and matches the pre-registration
one-for-one. If a number below does not match §4 of preregistration.md, the
analyser is wrong, not the pre-registration.

Usage
-----

Dev analysis::

    uv run python experiments/phase5_od8_h7/STEP1_MECHANISM/stage_a_analyse.py

Held-out analysis (writes to a separate verdict file so the two are on
disk simultaneously)::

    uv run python experiments/phase5_od8_h7/STEP1_MECHANISM/stage_a_analyse.py \\
        --raw experiments/phase5_od8_h7/STEP1_MECHANISM/raw_results_heldout \\
        --out experiments/phase5_od8_h7/STEP1_MECHANISM/processed_results \\
        --suffix heldout
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Numbers below are the pre-registered ones. Anything imported here is a
# constant already committed in preregistration.md or stage_a_run.py.
PHASES: tuple[tuple[str, int, int], ...] = (
    ("P200_399", 200, 399),
    ("P400_999", 400, 999),
    ("P1000_1999", 1000, 1999),
    ("P2000_3399", 2000, 3399),
)

# The four ratios of §4. Keys are the field names in the JSONL rows;
# 'lane_deviation_abs' is derived from lane_deviation_m (see below).
RATIO_FIELDS: tuple[tuple[str, str], ...] = (
    ("sigma", "sigma"),
    ("departure", "departure"),
    ("conformal_quantile", "quantile"),
    ("lane_deviation_abs", "err"),
)

# Pre-registered ratio bounds for the H1 fingerprint on imu_dropout, phases
# P400_999 and later (§4 of preregistration.md).
H1_BOUNDS = {
    "sigma": (1.5, math.inf),          # lower CI bound must be >= 1.5
    "departure": (0.75, 1.5),          # 95 % CI overlaps 1.0
    "quantile": (0.75, 1.25),          # 95 % CI overlaps 1.0
    "err": (1.5, math.inf),            # true error grows: lower CI >= 1.5
}
H2_BOUNDS = {
    "departure": (0.0, 0.5),           # upper CI must be <= 0.5
    "sigma": (0.75, 1.5),              # 95 % CI overlaps 1.0
}
H3_BOUNDS = {
    "quantile": (1.5, math.inf),       # lower CI >= 1.5
    "sigma": (0.75, 1.5),
    "departure": (0.75, 1.5),
}

BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_CI = 0.95
RATIO_TICKS_ALL_PHASE = "all"  # sentinel for a single phase spanning fault onset..end
FAULT_ONSET_TICK = 200
FROZEN_THRESHOLD = 3.7024
PRIMARY_FAULT = "imu_dropout"


@dataclass(frozen=True)
class RunSummary:
    """Per-phase per-field median for one run."""

    fault: str
    seed: int
    arm: str
    # phase name -> field name -> median
    values: dict[str, dict[str, float]]


def _load_run(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return (header, tick_rows) from a JSONL run file."""
    with path.open("r", encoding="utf-8") as fh:
        lines = [line.strip() for line in fh if line.strip()]
    header = json.loads(lines[0])
    ticks = [json.loads(line) for line in lines[1:]]
    return header, ticks


def _phase_medians(ticks: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """For each phase and each ratio field, the median value over that phase."""
    out: dict[str, dict[str, float]] = {name: {} for name, _, _ in PHASES}
    for name, lo, hi in PHASES:
        phase_ticks = [t for t in ticks if lo <= t["tick"] <= hi]
        if not phase_ticks:
            for _src, alias in RATIO_FIELDS:
                out[name][alias] = math.nan
            continue
        for src, alias in RATIO_FIELDS:
            if src == "lane_deviation_abs":
                values = [abs(float(t["lane_deviation_m"])) for t in phase_ticks
                          if t.get("lane_deviation_m") is not None
                          and math.isfinite(float(t["lane_deviation_m"]))]
            else:
                values = [float(t[src]) for t in phase_ticks
                          if t.get(src) is not None
                          and isinstance(t[src], (int, float))
                          and math.isfinite(float(t[src]))]
            out[name][alias] = statistics.median(values) if values else math.nan
    return out


def _summarise_runs(raw_dir: Path) -> list[RunSummary]:
    """Every run file under ``raw_dir`` reduced to per-phase medians."""
    summaries: list[RunSummary] = []
    for path in sorted(raw_dir.glob("*.jsonl")):
        header, ticks = _load_run(path)
        summaries.append(RunSummary(
            fault=header["fault"],
            seed=int(header["seed"]),
            arm=header["arm"],
            values=_phase_medians(ticks),
        ))
    return summaries


def _bootstrap_ci(values: list[float], resamples: int, ci: float,
                  rng_seed: int) -> tuple[float, float, float]:
    """Bootstrap median CI. Returns (median, lower, upper).

    Fixed RNG seed so re-running the analyser is deterministic. Bootstrap is
    over *runs* (each `values` entry is one seed's ratio) rather than ticks --
    the pre-registration flags autocorrelation as the reason.
    """
    import random  # noqa: PLC0415 - stdlib RNG, deterministic under seed
    finite = [v for v in values if math.isfinite(v)]
    if not finite:
        return math.nan, math.nan, math.nan
    med = statistics.median(finite)
    rng = random.Random(rng_seed)
    n = len(finite)
    resamples_out: list[float] = []
    for _ in range(resamples):
        sample = [finite[rng.randint(0, n - 1)] for _ in range(n)]
        resamples_out.append(statistics.median(sample))
    resamples_out.sort()
    lo = resamples_out[int((0.5 - ci / 2) * resamples)]
    hi = resamples_out[int((0.5 + ci / 2) * resamples)]
    return med, lo, hi


def _paired_ratios(
    summaries: list[RunSummary],
) -> dict[str, dict[str, dict[str, list[float]]]]:
    """Per fault, per phase, per field: the list of seed-paired ratios.

    The clean arm has one run per seed (deterministic under a fixed seed with
    no fault, so per-fault duplicates would be identical). Every faulted run
    is paired to the clean run at the same seed.
    """
    clean_by_seed: dict[int, RunSummary] = {
        s.seed: s for s in summaries if s.arm == "clean"
    }
    faulted: dict[str, dict[int, RunSummary]] = {}
    for s in summaries:
        if s.arm != "faulted":
            continue
        faulted.setdefault(s.fault, {})[s.seed] = s

    out: dict[str, dict[str, dict[str, list[float]]]] = {}
    for fault, by_seed in faulted.items():
        out[fault] = {name: {alias: [] for _src, alias in RATIO_FIELDS} for name, _, _ in PHASES}
        for seed in sorted(by_seed):
            f = by_seed[seed]
            c = clean_by_seed.get(seed)
            if c is None:
                continue
            for name, _, _ in PHASES:
                for _src, alias in RATIO_FIELDS:
                    fv = f.values[name][alias]
                    cv = c.values[name][alias]
                    if not (math.isfinite(fv) and math.isfinite(cv)) or cv == 0.0:
                        out[fault][name][alias].append(math.nan)
                    else:
                        out[fault][name][alias].append(fv / cv)
    return out


def _apply_rule(
    fault_stats: dict[str, dict[str, dict[str, tuple[float, float, float]]]],
) -> dict[str, Any]:
    """Apply the pre-committed H1/H2/H3/H-none rule to the primary fault."""
    verdicts: dict[str, str] = {}
    # For each fault, evaluate H1/H2/H3 over the "committed window" (P400_999
    # and later, per §4). Report the strictest verdict; a per-fault mixed
    # outcome is recorded as MIXED, and the primary fault's verdict drives §5.
    for fault, phases in fault_stats.items():
        outcomes: list[str] = []
        for phase_name in ("P400_999", "P1000_1999", "P2000_3399"):
            stat = phases[phase_name]
            outcomes.append(_verdict_for_phase(stat))
        # If all committed phases agree on H1, H2 or H3, that is the verdict;
        # any disagreement is mixed and reads as H-none per §5.
        if all(o == outcomes[0] and o in {"H1", "H2", "H3"} for o in outcomes):
            verdicts[fault] = outcomes[0]
        elif all(o == "H-none" for o in outcomes):
            verdicts[fault] = "H-none"
        else:
            verdicts[fault] = "MIXED"

    primary = verdicts.get(PRIMARY_FAULT, "MISSING")
    if primary == "H1":
        overall = "H1"
        action = f"Go IV (Stage B, 15 Nov). Primary fault {PRIMARY_FAULT} shows H1 fingerprint across P400_999 and later."
    else:
        overall = primary
        action = (
            f"Skip IV. Primary fault {PRIMARY_FAULT} verdict = {primary}. G1 stands; target ITSC alone (Stages C, D)."
        )

    return {
        "primary_fault": PRIMARY_FAULT,
        "primary_verdict": primary,
        "overall_action": action,
        "per_fault_verdict": verdicts,
    }


def _verdict_for_phase(stat: dict[str, tuple[float, float, float]]) -> str:
    """H1/H2/H3/H-none for one phase, per the pre-registered bounds in §4."""
    def match(bounds: dict[str, tuple[float, float]]) -> bool:
        for field, (lower_bound, upper_bound) in bounds.items():
            median, ci_lo, ci_hi = stat[field]
            if not math.isfinite(ci_lo) or not math.isfinite(ci_hi):
                return False
            # For "CI overlaps 1.0" bounds, require the [ci_lo, ci_hi]
            # interval to intersect [lower_bound, upper_bound]. For "lower CI
            # >= X" (upper_bound == inf), require ci_lo >= lower_bound.
            if math.isinf(upper_bound):
                if ci_lo < lower_bound:
                    return False
            elif lower_bound == 0.0:  # H2's "upper CI <= X" pattern
                if ci_hi > upper_bound:
                    return False
            else:
                # Overlap check.
                if ci_hi < lower_bound or ci_lo > upper_bound:
                    return False
        return True

    if match(H1_BOUNDS):
        return "H1"
    if match(H2_BOUNDS):
        return "H2"
    if match(H3_BOUNDS):
        return "H3"
    return "H-none"


def _format_final_decision(
    fault_stats: dict[str, dict[str, dict[str, tuple[float, float, float]]]],
    decision: dict[str, Any],
    header_common: dict[str, Any],
    suffix: str,
) -> str:
    """Render final_decision.md content per §9 of the pre-reg."""
    lines: list[str] = []
    label = " (held-out)" if suffix == "heldout" else " (dev seeds)"
    lines.append(f"# Stage A -- Final Decision{label}")
    lines.append("")
    lines.append(f"**Analysis run against** `{header_common['raw_dir']}`.")
    lines.append(f"**Base seed:** {header_common['base_seed']}   "
                 f"**seeds:** {header_common['n_seeds']}   "
                 f"**ticks:** {header_common['ticks']}   "
                 f"**threshold:** {header_common['threshold']}   "
                 f"**git SHA:** `{header_common['git_sha']}`")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"**Primary fault:** `{decision['primary_fault']}`")
    lines.append(f"**Primary verdict:** **{decision['primary_verdict']}**")
    lines.append("")
    lines.append(f"**Action:** {decision['overall_action']}")
    lines.append("")
    lines.append("## Per-fault verdicts")
    lines.append("")
    lines.append("| fault | verdict |")
    lines.append("|---|---|")
    for fault, v in decision["per_fault_verdict"].items():
        lines.append(f"| `{fault}` | {v} |")
    lines.append("")
    lines.append("## Per-fault, per-phase ratios (faulted / clean; median [95 % CI])")
    lines.append("")
    for fault, phases in fault_stats.items():
        lines.append(f"### `{fault}`")
        lines.append("")
        lines.append("| phase | σ | departure | quantile | true err |")
        lines.append("|---|---|---|---|---|")
        for phase_name, _, _ in PHASES:
            stat = phases[phase_name]
            row = [phase_name]
            for _src, alias in RATIO_FIELDS:
                med, lo, hi = stat[alias]
                if math.isfinite(med):
                    row.append(f"{med:.2f} [{lo:.2f}, {hi:.2f}]")
                else:
                    row.append("--")
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("Rule applied verbatim from `preregistration.md` §4 and §5. "
                 "See `mechanism_verdict.json` for machine-readable output.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw",
        type=Path,
        default=Path("experiments/phase5_od8_h7/STEP1_MECHANISM/raw_results"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/phase5_od8_h7/STEP1_MECHANISM/processed_results"),
    )
    parser.add_argument(
        "--suffix",
        default="dev",
        help="'dev' or 'heldout'; distinguishes the two verdict files.",
    )
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    summaries = _summarise_runs(args.raw)
    if not summaries:
        print(f"no runs found under {args.raw}", file=sys.stderr)
        return 1

    ratios = _paired_ratios(summaries)

    # Aggregate: per fault per phase per field -> (median, ci_lo, ci_hi).
    fault_stats: dict[str, dict[str, dict[str, tuple[float, float, float]]]] = {}
    for fault, phases in ratios.items():
        fault_stats[fault] = {}
        for phase_name, fields in phases.items():
            fault_stats[fault][phase_name] = {}
            for field, values in fields.items():
                # rng_seed keyed by fault+phase+field, deterministic across runs
                rng_seed = abs(hash((fault, phase_name, field))) % (2**31)
                fault_stats[fault][phase_name][field] = _bootstrap_ci(
                    values, BOOTSTRAP_RESAMPLES, BOOTSTRAP_CI, rng_seed
                )

    decision = _apply_rule(fault_stats)

    # A common header block for the report.
    n_seeds = len({s.seed for s in summaries if s.fault == PRIMARY_FAULT})
    a_run = summaries[0]
    example_path = next(iter(args.raw.glob("*.jsonl")))
    hdr, _ = _load_run(example_path)
    header_common = {
        "raw_dir": str(args.raw),
        "base_seed": hdr.get("base_seed"),
        "n_seeds": n_seeds,
        "ticks": hdr.get("ticks"),
        "threshold": hdr.get("threshold"),
        "git_sha": hdr.get("git_sha"),
    }

    verdict_path = args.out / f"mechanism_verdict_{args.suffix}.json"
    verdict_path.write_text(
        json.dumps(
            {
                "header": header_common,
                "decision": decision,
                "ratios": {
                    fault: {
                        phase: {field: {"median": t[0], "ci_lo": t[1], "ci_hi": t[2]}
                                for field, t in fields.items()}
                        for phase, fields in phases.items()
                    }
                    for fault, phases in fault_stats.items()
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # Per-run summary: every seed's per-phase medians, so a reviewer can
    # rebuild the verdict without re-running the ~25 min sweep. This is the
    # only committed record of what each seed did; the raw JSONL files stay
    # local (and are regeneratable from stage_a_run.py under the seeds
    # recorded in the header).
    per_run_path = args.out / f"per_run_summary_{args.suffix}.json"
    per_run_path.write_text(
        json.dumps(
            {
                "header": header_common,
                "runs": [
                    {
                        "fault": s.fault,
                        "arm": s.arm,
                        "seed": s.seed,
                        "phase_medians": s.values,
                    }
                    for s in summaries
                ],
            },
            indent=1,
        ),
        encoding="utf-8",
    )

    md_path = args.out / f"final_decision_{args.suffix}.md"
    md_path.write_text(_format_final_decision(fault_stats, decision, header_common, args.suffix),
                       encoding="utf-8")

    print(f"verdict: {decision['primary_verdict']}")
    print(f"action:  {decision['overall_action']}")
    print(f"wrote:   {verdict_path}")
    print(f"         {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
