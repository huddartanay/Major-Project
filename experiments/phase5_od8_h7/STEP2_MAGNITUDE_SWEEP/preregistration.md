# STEP 2 · Magnitude sweep — Pre-Registration (Stage C1 of the 19 Sep 2026 handoff)

**Written 22 September 2026, before any run of this experiment.** Any change
requires a dated `amendment.md`; existing raw results are not re-analysed
under the amended rule.

Owner (drafting): Tanay Huddar. Reviewer note: Sushanth C is unavailable
this session; the primary author is proceeding under Tanay's authorization.
Sushanth may request an amendment on return.

---

## 1 · Why this experiment exists

The Stage A dev sweep landed at H-none on the pre-registered mechanism
question (`processed_results/final_decision_dev.md`, dev, 30 seeds), which
sends Paper 1 to ITSC. The ITSC contribution is **G2 · a label-free monitor
for gate blindness** (handoff §7 Stage C).

E21 already shows that L1's stream-health detector catches the sustained
`imu_dropout` in 30/30 dev runs with 5-tick latency and 0/30 clean false
alarms. The obvious reviewer question is therefore: *"L1 solves the case
you presented; what does G2 add?"* Stage C1 answers this by characterising,
across a range of fault magnitudes, when L1 misses and what the L6 gate does
in those cases. G2's design in Stage C2 targets exactly the region this
sweep uncovers.

Stage C1 does not design G2. It measures the space in which G2 would live.

## 2 · Design at a glance

**Scope.** For each parameterised fault kind (`position_bias`,
`position_drift`, `speed_bias`, `lateral_noise`) run five magnitudes on the
same 30 dev seeds and same sustained-injection window (tick 200 through the
end of the run) as Stage A. Parameterless faults (`imu_dropout`,
`speed_stuck`) are not part of this sweep — they have no magnitude to vary.

**Magnitudes.** For each parameterised fault, five points:

- **subthreshold** (0.1 × `low`)
- **low** (unchanged from `SEVERITIES`)
- **mid-low** (0.5 × `medium`)
- **medium** (unchanged from `SEVERITIES`)
- **high** (unchanged from `SEVERITIES`)

The 0.1× point is deliberately far below `low`: the sweep should include
magnitudes small enough that L1 could plausibly miss them, otherwise we
cannot distinguish "L1 catches everything" from "the sweep did not test the
boundary".

**Ticks per run:** 3,400. **Seeds:** dev `20260731 + i` for `i ∈ [0, 30)`,
paired with the clean arm from Stage A (already run; the clean-arm runs are
seed-deterministic and can be reused, not re-executed).

**Cost.** 4 faults × 5 magnitudes × 30 seeds = 600 faulted runs. At the
~7 s/run Stage A observed, ~70 min wall time.

## 3 · Fields recorded, and where they come from

Reuses `benchmarks/mechanism_logger.py`. The same 15 per-tick fields feed
both Stage A's ratio analysis and this experiment's L1-vs-gate table.
Additionally, per run:

- `l1_detected`: whether the L1 stream-health detector fired at any tick
  ≥ 200 (from the E21 pipeline, `benchmarks.detectors`, unchanged).
- `l1_first_fire_tick`: first tick where L1 fired, or ``None``.
- `gate_alarm_rate_400_3399`: alarm rate over ticks 400–3399 at the frozen
  threshold `3.7024` (this is the R3c-equivalent number).

## 4 · The four quadrants — the primary outcome table

For each (fault kind, magnitude) the run is placed in one of four cells by
two binary axes, both applied on the dev-median run:

| axis | boundary |
|---|---|
| L1 detects | any L1 fire tick ≥ 200 in ≥ 15 of 30 runs |
| Gate is quieter than baseline | median gate alarm rate over ticks 400–3399 ≤ 50 % of the clean-baseline median (0.05 in Stage A) |

Result:

| | **L1 detects** | **L1 misses** |
|---|---|---|
| **Gate quieter than baseline** | **A** (G2's target: L1 flags, gate stays silent) | **C** (both blind; needs a different detector) |
| **Gate at baseline or louder** | **B** (nominal detection) | **D** (no fault effect) |

Stage C1's finding is the counts of A, B, C, D per fault kind. Cell A is
where G2 delivers value; cell C is where it does not, and Paper 1 must be
honest about the size of cell C.

## 5 · Pre-committed decisions this experiment supports

- **If cell A is non-empty for at least two of the four parameterised
  faults** across the five magnitudes → Stage C2 (G2 design) proceeds with
  those (fault, magnitude) pairs as its primary benchmark.
- **If cell A is empty across the sweep** → Paper 1's G2 story is that no
  gate blindness beyond what L1 catches exists in the tested regime, and
  the ITSC contribution has to shift (options: focus on the mechanism
  observations from Stage A alone; broaden the fault library; drop the
  paper). This is the pre-committed "walk away" call so it cannot be
  waved off later.

## 6 · Analysis, in one script

`stage_c1_analyse.py` reads the sweep's raw JSONL, computes the two axes
per run, aggregates to a per-(fault, magnitude) 4-cell count, and writes
`processed_results/quadrant_table.json` plus a `final_decision.md` naming
the cell A candidates or the walk-away outcome. Rule 5 above is coded
literally; no threshold in the analyser is decided after seeing the data.

## 7 · What this experiment cannot establish

- Whether G2 beats its label-free baselines (Amoukou, D3M, KS(conf)) —
  that is Stage C2's outcome experiment.
- Whether the cell A regime survives on held-out seeds — the held-out
  version of this sweep runs after C2's design lands, in Stage D.
- Anything about adversarial faults (G5) or semantic errors (G6).

## 8 · Integrity checklist

- Frozen threshold `3.7024`, hard-coded, not recomputed here.
- Stage 0's `demo_speed_assist=False` (default) enforced by `stage_a_run.py`'s
  integrity check, which the C1 runner delegates to.
- Git working tree clean at run start.
- Same seed set as Stage A dev (`20260731 + i`); clean baseline reused, not
  re-executed, so this sweep contributes no new source of clean-arm variance.
- Per-tick JSONL under `raw_results/` (git-ignored, same pattern as Stage A);
  per-run summary under `processed_results/` is what enters the repo.
- Runner script committed **before** the first run and its git SHA in the
  header of every JSONL.

## 9 · Cost cap

70 minutes wall time on dev seeds, one machine. If the sweep is still
running after 90 minutes, kill it, diagnose, and either resume from the
manifest or restart clean. No amendment needed for a resume from a
crash-time state.
