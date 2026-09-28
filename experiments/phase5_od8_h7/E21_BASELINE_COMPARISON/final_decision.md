# E21 — Baseline comparison: final decision

**9 September 2026** · 210 runs × 3,400 ticks · 88.8 minutes · P1, `medium` severity
**Pre-registered at `ae997b3`; paired with E18-R3c on the same 30 seeds, faults and injection mode.**

---

# VERDICT: BASELINE WINS

**A stream-health check detects `imu_dropout` on 30 of 30 runs, with zero false positives on 30
clean runs. The conformal gate detects it on 0 of 30.**

**The fault evidence was available at L1, two layers before the gate that missed it.**

---

## 1 · The measurement

Clean false-positive rate, 30 clean runs:

| detector | clean FP | |
|---|--:|---|
| `health` | **0.000** | within the 0.10 bar |
| `innovation` | 0.000 | within the bar |
| `trust` | **0.767** | **breaches it** — fires on 77 % of healthy runs |

Run-level detection under sustained injection:

| fault | OD-8 | `health` | `innovation` | `trust` | detected by |
|---|--:|--:|--:|--:|---|
| `position_bias` | 1.00 | **1.00** | 0.00 | 0.63 | health |
| `position_drift` | 1.00 | **1.00** | 0.00 | 0.63 | health |
| **`imu_dropout`** | **0.00** | **1.00** | 0.00 | 0.63 | **health** |
| `lateral_noise` | **1.00** | 0.00 | 0.20 | 0.63 | — (OD-8 only) |
| `speed_bias` | 0.00 | 0.00 | 0.00 | 0.37 | **nobody** |
| `speed_stuck` | 0.37 | 0.00 | 0.00 | 0.20 | **nobody** |

Only `health` clears both bars. `trust` is disqualified by its clean rate, not by its detection.

## 2 · The honest reading of `health` on `imu_dropout`

**A dropout sets stream health to something other than `HEALTHY`. Detecting it with a health check
is close to definitional, and this result should not be reported as though a clever baseline
outsmarted a sophisticated monitor.**

That near-tautology *is* the finding. The architecture routes a trivially available signal past the
gate that needed it. L1 knows within 5 ticks — the median latency is exactly `PATIENCE`, meaning it
fires the first moment it is allowed to — and L6 never finds out. The gap is not statistical
sophistication; it is plumbing.

**`position_bias` and `position_drift` are the substantive part of the result.** Those faults do not
trivially set a health flag: they are injected by making two of three position channels lie, and
`health` catches them at 1.00 because the redundancy cross-check sees the channels disagree. That is
a genuine detection by a cheap mechanism, not a definition.

The latencies matter to the safety argument. `imu_dropout` is caught in **5 ticks (0.25 s)**;
`position_bias` in **13 ticks**; `position_drift` in **1,082 ticks (54 s)**, because a slow drift
takes that long to breach a cross-channel consistency bound. A slow drift is caught eventually and
far too late — a different failure from never.

## 3 · The two monitors are complementary, and neither is sufficient

`health` catches what OD-8 misses (`imu_dropout`); OD-8 catches what `health` misses
(`lateral_noise`, 1.00 against 0.00). The union covers **4 of 6** faults, against 3 for OD-8 alone.

**Neither catches `speed_bias` or `speed_stuck`, and nor does anything else tested.** Those two
defeat every detector in this experiment at every severity and in both injection modes. That is now
a well-supported negative: two of six fault classes are invisible to the entire monitoring surface
as built.

## 4 · `innovation` — the principled candidate — detects essentially nothing

`benchmarks/detectors.py` calls the innovation detector "the principled candidate", on the reasoning
that the innovation sequence is where a filter's disagreement with its measurements shows up.

Measured: **0.00 on five of six faults**, and 0.20 on `lateral_noise` at a median latency of 2,154
ticks. At its committed ceiling of 3.0 it is inert.

This is worth stating because it is the detector a control engineer would reach for first, and
because it was pre-registered as a fair comparator at a threshold set long before this experiment.
It fails here. Whether a *calibrated* innovation test would do better is a different question and
was explicitly excluded in §8 of the pre-registration.

## 5 · The prediction, scored

§9 of the pre-registration recorded: *"I expect BASELINE WINS, on `imu_dropout`, via `health` and
`trust` … I expect both speed faults to defeat every detector … `health` near zero false positives
and `trust` the risk: a Trust Index that dips below 0.80 on clean runs would breach the clean bar and
turn a win into trigger-happy."*

| prediction | outcome |
|---|---|
| BASELINE WINS on `imu_dropout` | **correct** |
| via `health` | **correct**, 1.00 at 0.000 FP |
| via `trust` | **wrong** — `trust` breached the clean bar, exactly as the same paragraph warned |
| both speed faults defeat everything | **correct** |
| `health` clean FP near zero | **correct**, 0.000 |
| `trust` is the one at risk on the clean bar | **correct**, 0.767 |

The one substantive miss — `innovation` detecting nothing at all — was not predicted in either
direction.

## 6 · What this changes

**The E18-R3c finding stands, and its interpretation changes.** "A persistent sensor failure is
invisible to the conformal monitor" remains exactly true and is unaffected by this experiment. What
changes is what follows from it:

- **Before E21:** a blind spot of conformal monitoring, cause unknown.
- **After E21:** an **architectural** failure. The evidence was present at L1, cheap to read, and
  the gate does not consult it. The monitor is blind because of where it sits and what it reads —
  not because the fault is hard to see.

This is a stronger and more actionable claim, and it is the one the paper should carry.

## 7 · What this does not license

- **No claim that conformal prediction is a poor method.** This compares one conformal monitor as
  configured here against three fixed thresholds on one plant. Nothing here generalises to conformal
  prediction as such.
- **No claim that `health` is a sufficient monitor.** It misses `lateral_noise` entirely and takes
  54 seconds on `position_drift`.
- **No claim about a calibrated baseline.** These thresholds are uncalibrated; a calibrated
  innovation test is untested.
- Nothing about P2 or P3; P1 only. Nothing about severities other than `medium`.
- `[M-syn]` throughout. `[M-ext]` remains **0 of 30**.
- The comparison is asymmetric by construction — OD-8 carries a conformal guarantee, the baselines do
  not — and §4 of the pre-registration states this. The clean-arm bar exists so that asymmetry cannot
  be exploited, and it is what disqualified `trust`.

## 8 · Next

1. **Literature review**, using `docs/LITERATURE_REVIEW_PROMPT.md`. E21 sharpens the claim into
   an architectural one, which changes what prior art matters — fault masking and sensor-attack
   detection are now the load-bearing searches.
2. **The paper reframes on this result.** The contribution is the separation of discriminability,
   calibration validity and operational detectability, plus a demonstrated case where a monitor is
   quieter than baseline during a hazard *and* the evidence was available upstream and unused.
3. **E19 / H7 becomes answerable.** It asks where a monitor should sit; E21 has just shown that
   where it sits is the problem. The two experiments now compose.
4. `speed_bias` and `speed_stuck` are undetected by everything tested. Either a detector that reads
   the speed channel is added, or the limitation is stated plainly in the paper. It should not be
   left implicit.
