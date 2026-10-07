# Direction — 7 October 2026

Record of what was decided and assessed on 7 October after the threat literature study
(`THREAT_LITERATURE_STUDY.md`). Author: Sushanth. Tanay has not yet read this.

**Status of everything below: plan and assessment. Nothing in §3, §5 or §6 has been built or run.**

---

## 1 · Focus: three claims

| | claim | role in the paper | evidence held | missing |
|---|---|---|---|---|
| **C1** | A calibrated monitor can be uninformative: calibration checks do not test whether the score depends on what it claims to monitor | headline | `FINDING_TWIN_CHANNEL_MISMATCH_2026-10-07`: shipped gate passes calibration with 99.96 % of its score from channels the twin does not model | A general test, not one anecdote |
| **C2** | Frozen values evade freshness checks, range checks and the conformal gate at once | sharpest evidence for C1 | STEP 6, dev + held-out: L1 0/30, shipped gate ≈ 0 %, speed gap ≈ 12 m/s | Why ≈ 20 % of runs stay quiet under the corrected score (STEP 7); a plain stuck-at baseline |
| **C3** | End-to-end response of a governed learned controller across a fault taxonomy | scope / map | Harness; two of eight rows run | Six rows |

Dropped for now: C4 (unit / sign / frame errors as a fault class) as a *novelty* claim — it stays as arms
inside C3. It needs a targeted literature search before it can be called a gap.

## 2 · Wording constraints

- Never "resilient to all attacks". Three results forbid it: fewer-than-half (Fawzi et al.), full-I/O
  attacker undetectable (Griffioen et al.), replay needs an active signal (Porter et al.).
- Not "conformal gates go silent under sensor loss" — STEP 7 rejected G1-SILENT on both splits.
- The claim is: *calibration does not reveal an uninformative score; here is a test that does.*
- Never "first". "Not found in what we read" only.
- Use the literature's terms: fail-inconsistent (Byzantine) sensor fault; sensor deception / false data
  injection; semantic fault (defined at first use, because AV-security uses "semantic" differently).

## 3 · Plan for C1–C3

1. **Threat model, one page.** Sources, how many may be faulty, attacker knowledge, out of scope
   (colluding majority; full-I/O attacker). No runs.
2. **C1 — sensitivity audit**, pre-registered. Two label-free checks:
   - *channel share*: fraction of the score from channels the model actually predicts;
   - *perturbation response*: does the score move when the monitored quantity is nudged by a known amount.
   Apply to the shipped score and the corrected lateral score. Expected: shipped fails, corrected passes.
   If not, C1 is weaker than believed.
   - **2b · generality:** run the audit on a second, independently built monitor (a different score, or a
     re-implemented published gate). This is the single item that most raises acceptance odds.
3. **STEP 8 — fault-taxonomy study**, pre-registered; covers C2 and C3 together.
   - Arms: loss, frozen, single lie (position, speed, lateral acceleration), two colluding sources, slow
     drift, unit and sign errors.
   - Detectors compared: L1, shipped L6, corrected lateral score, a plain stuck-at / variance check.
   - Outcome: **run-level** — share of runs detected at a fixed run-level false-alarm rate; which layer
     reacts first; lane kept or not. Replaces the median ratio that made STEP 7 unstable.
   - Seeds: fresh held-out block `20270301 + i`.
   - Log frozen values at onset per run (answers the 20 % question).
   - STEP 8 is the proper version of the exploratory threat probe whose run was declined.
     **Not to be run without Sushanth's explicit go-ahead.**
4. **Reading before writing:** SAVIOR (USENIX Sec 2020), control invariants (CCS 2018), PID-Piper
   (DSN 2021), Mo & Sinopoli on replay.

Accepted up front: C3 may be mostly negative (colluding sources and unit errors probably undetected); the
stuck-at baseline may beat our gate on frozen sensors. Both get reported as found.

## 4 · Venue assessment for the C1–C3 paper

Strengths: C1 is a checkable finding that matches a gap the literature states (Lu et al.: recovery and
monitoring modules assumed safe); method is pre-registered with single-use held-out seeds; evaluation is
end-to-end, which two SoK papers ask for.

| weakness | reviewer's wording | fixable by 1 March 2027 |
|---|---|---|
| One system, one controller, one twin | "A bug in your implementation, not a property" | Partly — step 2b |
| Own simulator only | "No real data, no standard benchmark" | Hard |
| Findings are negative | "What do you propose?" | Yes — the audit |
| Fix unproven (≈ 20 % quiet runs) | — | Unknown until STEP 8 |
| Stuck-at baseline may win | "A variance check solves C2" | Report it |

| venue | assessment |
|---|---|
| IEEE ITSC, 1 Mar 2027 | **Target.** Realistic with the audit, step 2b, and a complete C3 table. A fair chance, not a safe one |
| DSN, 2 Dec 2026 | Best topical fit; too soon. Not attempting |
| IROS / ICRA / IV main track | Unlikely without real-vehicle or standard-benchmark results |
| Workshop / Springer conference | Achievable with steps 1–3 |

## 5 · Parts that exist but are not wired (checked in code, 7 October)

| part | what it would add | where | risk if switched on as is |
|---|---|---|---|
| **FB2 — control-effectiveness estimator** | Learns steering effectiveness `B` from measured response | `ControlEffectivenessEstimator`, `src/astra/runtime/assembly.py`; shadow only (`shadow_fb2`); the live twin never reads it | Learns from measured lateral acceleration — a lying or frozen sensor teaches it a wrong `B` |
| **FB3 — online trust recalibration** | Thresholds adapt to recent conditions | Shadow only; pipeline computes the quantile it "would have used" | Adapts to the fault and normalises it; slow drift poisons it |
| **L9 cold path** — candidate search, shadow execution, switch / rollback | Tries a better calibration table in parallel; commits only on agreement | `layers/l9_rcm/shadow.py`, `arbiter.py`; `drive_closed_loop(cold_path=None)` so it never runs | Low (rollback built in); untested |
| **L9 bounded safe exploration** | Keeps moving slowly in a narrowed envelope instead of stopping | `engage_exploration`; unreachable without the cold path | Untested in closed loop |

FB4 (simulator sync) is prototype-only.

Two links to our findings:

- FB2 is the natural fix for the twin's 120 vs plant's 140 steering effectiveness — candidate cause of the
  constant offset (≈ 8.5) in the STEP 7 score.
- The code records that the original network-update FB2 collapsed the non-conformity score by 40 % with
  nothing changed ("the statistical gate disarming itself"), which is why ADR-0020 redefined it. That is
  C1 found earlier; cite it.

Does not exist yet:

- A frozen-value check at L1.
- An active probe. *Idea, not in code:* bounded safe exploration already makes small limited steering
  moves; it could double as the known signal that the replay literature uses to test sensors.

### Wiring order

1. Frozen-value check at L1 — inside STEP 8, as the baseline.
2. Health guard for learning — no loop learns while L1 / L3 report a problem or the gate fails the C1 audit.
3. FB2 estimator, guarded.
4. Cold path with shadow execution and safe exploration.
5. FB3 last, committed only through shadow execution.

**Decision:** nothing from 2–5 is wired before STEP 8, so the system under test does not change midway.
Optional for paper 1: item 4 as a separate small pre-registered check (does exploration engage and keep
the car in lane). Awaiting Sushanth's answer on that.

## 6 · The "self-learning, exploring, resilient system" claim

### Today

| word | shown | verdict |
|---|---|---|
| self-learning | Nothing; FB2 / FB3 shadow only | not shown |
| exploring | Nothing; cold path off in every experiment | not shown |
| resilient | Flagged sensor loss handled; frozen sensor missed; corrected score quiet in ≈ 20 % of runs; rest untested | partly, with a measured failure |
| clean | Pre-registration, held-out seeds, refuted guesses reported | shown — describes the process, not the system |

**The claim cannot be made today.**

### If it were proven

Having learning, exploration and resilience together is not novel; each is published (Tsai et al.;
Fu et al.; Chu et al.; Gibbs & Candès; Andersson & Dán). What was not found in the ~95 papers reviewed:

1. a test of whether a safety monitor is informative (the C1 audit),
2. used to decide **when the system is allowed to learn**, so a bad sensor cannot teach it wrongly,
3. with evidence across a full fault taxonomy.

"Prove" must include all six:

| requirement | have it |
|---|---|
| Learning improves the system and does not weaken the gate under faults | no |
| Exploration engages and keeps the car safe instead of stopping | no |
| Detection and safe response across the taxonomy, with a stated attacker bound | 2 of 8 rows |
| Comparison with published baselines (SAVIOR, PID-Piper, plain stuck-at) | no |
| A second controller or platform, and CARLA or real data | no |
| Stated limits (colluding majority; full-I/O attacker out of scope) | in the study, not in a paper |

If all six hold: Q1 journal (IEEE T-ITS, T-IV, TDSC) realistic; DSN achievable; ICRA / IROS possible,
stronger with hardware; ITSC comfortable. If only the first three hold, on our simulator alone: an ITSC
paper and a weak journal submission. Estimated effort for all six: 6–9 months for four people.

## 7 · Two-paper path

1. **Paper 1 — ITSC, 1 March 2027.** "Calibration is not validity": the sensitivity audit (C1), frozen
   sensors (C2), fault-taxonomy table (C3). Does not carry the self-learning claim.
2. **Paper 2 — journal.** The self-adapting system, with paper 1's audit as the guard for learning; loops
   wired; second platform; published baselines.

Reason for the split: putting unproven parts beside the solid finding would let the weak parts sink it.

## 8 · Awaiting Sushanth

- Go-ahead for step 1 (threat model) and step 2 (audit pre-registration) — writing only.
- Whether the safe-exploration check (wiring item 4) goes into paper 1.
- Go-ahead before any STEP 8 run.
- Push of local commits (`a34a482` onward).
