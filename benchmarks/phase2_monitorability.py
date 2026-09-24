"""Phase 2 -- does monitorability predict the alarm rate that was observed?

Implements the frozen definition in
``experiments/phase5_od8_h7/PHASE2_MONITORABILITY/preregistration.md`` and nothing
else. No new runs: every number comes from data E18-R3 and E18-R3c already wrote.

The unit of analysis is the **(fault, phase) cell**. Ticks are never treated as
samples -- they are autocorrelated, which is the property that made a 200-tick
window insufficient in the first place. Within a cell the per-tick scores are
pooled across the 30 seeds to form one median, and the alarm rate is likewise one
number per cell.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from benchmarks.e17_stats import spearman

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ["PHASES", "cells", "main"]

_ROOT = Path("experiments/phase5_od8_h7")
_CLEAN = _ROOT / "E18_R3" / "raw_results" / "long_runs.json"
_FAULTED = _ROOT / "E18_R3c" / "raw_results" / "faulted_sustained.json"
_SERIES = _ROOT / "E18_R3c" / "raw_results" / "tick_series.json"
_OUT = _ROOT / "PHASE2_MONITORABILITY" / "processed_results"

#: Frozen threshold, v3, from E18_R2/processed_results/verdict.json. Not recomputed.
THRESHOLD = 3.7024

#: Phase edges exactly as E18-R3c used them, so M and the alarm rate it is scored
#: against are measured over identical tick ranges.
PHASES: tuple[tuple[str, int, int], ...] = (
    ("P-early", 200, 400),
    ("P-mid", 400, 1000),
    ("P-late", 1000, 2000),
    ("P-tail", 2000, 3400),
)

FAULTS = (
    "position_bias",
    "position_drift",
    "imu_dropout",
    "lateral_noise",
    "speed_bias",
    "speed_stuck",
)

#: E17's per-fault discriminability at the delivered signal, the incumbent
#: predictor M has to beat. Folded to [0.5, 1.0]; 0.5 is chance level.
#: Source: research/E17_30SEED_RESULTS.md, medium severity.
D_S_INCUMBENT: dict[str, float] = {
    "position_bias": 0.998,
    "position_drift": 0.997,
    "imu_dropout": 0.998,
    "lateral_noise": 0.995,
    "speed_bias": 0.881,
    "speed_stuck": 0.526,
}


def clean_baseline() -> tuple[float, float, int]:
    """Return the clean baseline M is standardised against.

    Returns:
        ``(mu_clean, sigma_between_clean, n_runs)`` -- the mean of the per-run
        clean means, and the spread *between* those run means. The between-run
        spread is the denominator because per-run baseline level, not within-run
        noise, is what a threshold frozen across runs has to survive.
    """
    runs = json.loads(_CLEAN.read_text())
    means = np.array([r["mean_3200"] for r in runs], dtype=np.float64)
    return float(means.mean()), float(means.std(ddof=1)), int(means.size)


def cells(mu: float, sigma: float) -> list[dict[str, object]]:
    """Compute M and the observed alarm rate for every (fault, phase) cell.

    Args:
        mu: Clean baseline mean.
        sigma: Between-run clean standard deviation.

    Returns:
        One record per cell, in a fixed order.
    """
    series = json.loads(_SERIES.read_text())
    records = json.loads(_FAULTED.read_text())

    by_fault: dict[str, list[str]] = {}
    for record in records:
        by_fault.setdefault(str(record["fault"]), []).append(str(record["tick_series_key"]))

    out: list[dict[str, object]] = []
    for fault in FAULTS:
        keys = by_fault.get(fault, [])
        for name, lo, hi in PHASES:
            pooled: list[float] = []
            for key in keys:
                values = np.asarray(series[key], dtype=np.float64)[lo:hi]
                pooled.append(values[np.isfinite(values)])
            stacked = np.concatenate(pooled) if pooled else np.array([])
            if stacked.size == 0:
                continue
            out.append(
                {
                    "fault": fault,
                    "phase": name,
                    "ticks": f"{lo}-{hi - 1}",
                    "n_runs": len(keys),
                    "median_score": float(np.median(stacked)),
                    # The frozen definition, verbatim.
                    "M": float((np.median(stacked) - mu) / sigma),
                    "alarm_rate": float(np.mean(stacked > THRESHOLD)),
                    "d_s": D_S_INCUMBENT[fault],
                }
            )
    return out


def _verdict(rho: float, p: float) -> str:
    """Apply the frozen decision rule.

    Args:
        rho: Spearman correlation.
        p: Its permutation p-value.

    Returns:
        The pre-registered verdict label.
    """
    if p >= 0.05:
        return "M FAILS"
    if rho >= 0.70:
        return "M PREDICTS"
    if rho >= 0.40:
        return "M IS WEAK"
    return "M FAILS"


def main() -> int:
    """Run the analysis and write the results.

    Returns:
        Process exit status.
    """
    mu, sigma, n_clean = clean_baseline()
    rows = cells(mu, sigma)

    print(f"clean baseline: mu = {mu:.4f}, sigma_between = {sigma:.4f}, over {n_clean} runs")
    print(f"threshold {THRESHOLD} (v3 frozen)   {len(rows)} cells\n")

    print(f"{'fault':<16}{'phase':<9}{'ticks':>11}{'median':>9}{'M':>9}{'alarm':>9}{'D_s':>7}")
    print("-" * 70)
    for r in rows:
        print(
            f"{r['fault']:<16}{r['phase']:<9}{r['ticks']:>11}"
            f"{r['median_score']:>9.3f}{r['M']:>9.2f}{r['alarm_rate']:>9.3f}{r['d_s']:>7.3f}"
        )

    m = np.array([r["M"] for r in rows], dtype=np.float64)
    alarm = np.array([r["alarm_rate"] for r in rows], dtype=np.float64)
    d_s = np.array([r["d_s"] for r in rows], dtype=np.float64)

    primary = spearman(m, alarm)
    incumbent = spearman(d_s, alarm)

    # Conservative check: 24 cells are not independent -- four phases share a
    # fault and the same 30 seeds appear throughout. Underpowered by design, and
    # reported as a direction rather than as an alternative test to choose from.
    per_fault_m, per_fault_a = [], []
    for fault in FAULTS:
        sub = [r for r in rows if r["fault"] == fault]
        per_fault_m.append(float(np.median([r["M"] for r in sub])))
        per_fault_a.append(float(np.median([r["alarm_rate"] for r in sub])))
    conservative = spearman(np.array(per_fault_m), np.array(per_fault_a))

    # The pre-registered primary test is confounded, and the confound was in the
    # frozen definition rather than in the data. M is a monotone transform of the
    # median, and the alarm rate is P(score > threshold), so
    #     median > threshold  <=>  alarm rate > 0.5
    # is an identity. Every cell obeys it, which forces a large rank correlation
    # before any evidence is considered. The identity constrains nothing *within*
    # a side, so re-running the correlation inside each side is the part of the
    # primary result that is actually empirical.
    m_threshold = (THRESHOLD - mu) / sigma
    above = [r for r in rows if r["M"] > m_threshold]
    below = [r for r in rows if r["M"] <= m_threshold]
    identity_holds = all(r["alarm_rate"] > 0.5 for r in above) and all(
        r["alarm_rate"] < 0.5 for r in below
    )

    def _within(group: Sequence[dict[str, object]]) -> dict[str, float] | None:
        if len(group) < 4:
            return None
        return spearman(
            np.array([r["M"] for r in group], dtype=np.float64),
            np.array([r["alarm_rate"] for r in group], dtype=np.float64),
        )

    within_below = _within(below)
    within_above = _within(above)

    verdict = _verdict(primary["rho"], primary["p"])
    # The honest verdict is the identity-free one; the frozen rule is applied to
    # it and reported alongside, never instead of, the pre-registered result.
    corrected = (
        _verdict(within_below["rho"], within_below["p"]) if within_below else "INSUFFICIENT"
    )

    print()
    print(f"{'test':<34}{'rho':>8}{'p':>10}   n")
    print("-" * 62)
    print(f"{'PRIMARY  M vs alarm rate':<34}{primary['rho']:>8.3f}{primary['p']:>10.4f}   {len(rows)}")
    print(f"{'incumbent  D_s vs alarm rate':<34}{incumbent['rho']:>8.3f}{incumbent['p']:>10.4f}   {len(rows)}")
    print(f"{'conservative  per-fault medians':<34}{conservative['rho']:>8.3f}{conservative['p']:>10.4f}   {len(per_fault_m)}")
    print()
    print(f"threshold in M units = {m_threshold:.3f}")
    print(f"identity median>threshold <=> alarm>0.5 holds in every cell: {identity_holds}")
    print(f"  cells above {len(above)}, below {len(below)} -- that split is forced, not evidence")
    for label, res in (("within below-threshold", within_below), ("within above-threshold", within_above)):
        if res is None:
            continue
        n = len(below) if "below" in label else len(above)
        print(f"  {label:<24} rho={res['rho']:+.3f}  p={res['p']:.4f}  n={n}")
    print()
    print(f"VERDICT, pre-registered primary: {verdict}")
    print(f"VERDICT, identity-free (below-threshold cells): {corrected}")

    _OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "experiment_id": "PHASE2-MONITORABILITY",
        "threshold": THRESHOLD,
        "clean": {"mu": mu, "sigma_between": sigma, "n_runs": n_clean},
        "cells": rows,
        "primary": primary,
        "incumbent_d_s": incumbent,
        "conservative_per_fault": conservative,
        "identity": {
            "m_at_threshold": m_threshold,
            "holds_in_every_cell": identity_holds,
            "n_above": len(above),
            "n_below": len(below),
            "within_below": within_below,
            "within_above": within_above,
        },
        "verdict_preregistered": verdict,
        "verdict_identity_free": corrected,
    }
    (_OUT / "monitorability.json").write_text(json.dumps(payload, indent=2))
    print(f"\nwrote {_OUT / 'monitorability.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
