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

---

## 9 · Phases

Goal: a system that detects faults, reacts to them, and returns to a better functional state, with
stated limits against lying, manipulated and semantically wrong sensors.

Each phase has an exit test. A phase is not done until its exit test is met or its failure is written up.

### Paper 1 — "Calibration is not validity" (ITSC, 1 March 2027)

| phase | dates | work | exit test |
|---|---|---|---|
| **P1 · Define** | 8–18 Oct 2026 | Threat model (one page). Pre-registration of the C1 sensitivity audit. Read SAVIOR, control invariants, PID-Piper, Mo & Sinopoli. Brief Tanay on STEP 6/7 and the twin mismatch | Threat model and audit pre-registration committed; Tanay has read both |
| **P2 · Prove the monitor problem (C1)** | 19 Oct – 8 Nov | Run the audit on the shipped and corrected scores. Step 2b: audit a second, independently built monitor | Audit separates informative from uninformative scores on dev and held-out, on at least two monitors |
| **P3 · Map the faults (C2, C3)** | 9 Nov – 13 Dec | Add the L1 frozen-value check as baseline. Pre-register and run STEP 8 (eight fault arms, four detectors, run-level metric, seeds `20270301+i`). Explain the ≈ 20 % quiet runs | Complete taxonomy table, dev and held-out, every cell filled including the negative ones |
| **P4 · Repair the monitor** | 14 Dec – 10 Jan 2027 | Retrain the twin in effect space (a_long, a_lat) with an ADR; gate on the audit. Optional: safe-exploration check with the cold path on | Retrained gate passes the audit and detects frozen sensors in a pre-registered share of runs — or the failure is reported |
| **P5 · Write and submit** | 11 Jan – 1 Mar | Paper, figures, artefact, internal review by all four authors and the guide. College report from the same material | Submitted to ITSC |

### Paper 2 — the self-adapting system (journal, after March 2027)

| phase | work | exit test |
|---|---|---|
| **P6 · Guarded learning** | Health guard (no learning while L1/L3 unhealthy or the audit fails). Wire FB2 estimator behind it | Learning improves the twin on clean runs and does not weaken the gate under any STEP 8 fault |
| **P7 · Exploration and recovery** | Wire the L9 cold path: shadow execution, switch / rollback, bounded safe exploration. Test exploration as an active probe for frozen / replayed sensors | Exploration engages, keeps the car in lane, and raises frozen-sensor detection over the passive gate |
| **P8 · Adaptive thresholds** | FB3, committed only through shadow execution | No slow-drift arm can move the threshold enough to hide itself |
| **P9 · Generality and baselines** | Second controller or platform; CARLA or real data; SAVIOR / PID-Piper comparison | Main results hold on the second setting |
| **P10 · Write and submit** | Journal paper (T-ITS / T-IV / TDSC) | Submitted |

### Rules across all phases

- Pre-registration is committed before any study seed is run; a held-out block is used once.
- No learning loop is wired before P3 ends, so the system under test does not change midway.
- STEP 8 and any other run needs Sushanth's go-ahead; pushes need a yes each time.
- If P2 fails (the audit does not generalise), paper 1 becomes a case study and the venue drops to a
  workshop; decide at the end of P2, not later.

---

## 10 · Component status, layer by layer (read from code, 7 October)

Source: `src/astra/runtime/pipeline.py::GovernancePipeline.tick` and the layer modules; behaviour column
from STEP 6 / STEP 7 and the twin-mismatch finding. "Wired" = its output changes what the vehicle does.

| layer | wired | status | what is wrong or missing |
|---|---|---|---|
| L1 sensing | yes | works for what it checks | Freshness only. No frozen-value check: stuck sensor 0/30 detected |
| L1 integrity (`ResidualMonitor`) | yes, when redundant sensing is supplied | works for position | Merged worst-of with L1. Speed and lateral acceleration have one source each, so nothing to compare |
| L2 UKF | yes | works | Trusts a frozen speed: estimate ≈ 12 m/s from truth, no flag raised |
| FB1 re-anchor | yes | works | — |
| L3 trust | **partly** | computed every tick | Trust index is only an input to the proposer's observation and picks the twin head / quantile. `arbiter.issue` discards it (`del trust`); L8 never reads it. A low trust score triggers nothing |
| L4 proposer (PPO) | yes | works | — |
| L5 twin | yes | **mis-specified** | Trained on `(0, 0, a_lat/120)`; plant effectiveness is 140. Predicts ≈ 0 for throttle and brake |
| L6 statistical gate | yes | **mis-specified** | Distance over (throttle, brake, steer) against a twin that models steer only: 99.96 % of the score is unmodelled channels |
| L6 MMD shift detector | yes | untested by us | Fed from innovation, adjusts effective epsilon; never isolated in an experiment |
| L7a shield | yes | works | — |
| L7b physical gate | yes | works, **inherits twin error** | Compares proposal with the twin's lateral acceleration; uses the same 120 |
| L8 failsafe | yes | works | Escalation, de-escalation, HALT-until-reset all exercised. Only reacts to gate verdicts and frame health |
| L9 arbiter (issue, fallback, speed caps) | yes | works | Speed caps act on *estimated* speed, so a frozen speed sensor defeats them |
| L9 cold path (knowledge base, shadow execution, switch / rollback) | **no** | coded, dormant | Harness passes `cold_path=None` |
| L9 safe exploration | **no** | coded, unreachable | Needs the cold path |
| FB2 control-effectiveness estimator | **no** | shadow only | Would correct 120 → 140 |
| FB3 trust recalibration | **no** | shadow only | `TrustModule.recalibrate` exists, never called live |
| FB4 simulator sync | no | enum only | Prototype-only |

### Three groups

- **Correct and wired:** L1 freshness, position integrity, L2, FB1, L4, L7a, L8, L9 hot path.
- **Wired but wrong (fix, don't wire):** L5 twin target, L6 score, L7b's dependence on the twin,
  twin 120 vs plant 140.
- **Built but not connected:** L3 trust has no authority; L9 cold path and safe exploration; FB2; FB3.
- **Not built:** frozen-value check; any cross-check for speed and lateral acceleration; active probe.

### Common root

Every safety layer downstream of L2 reads the same state estimate. A fault that L1 does not flag
(frozen, lying single-source channel) is therefore invisible to L6, L7b, L8 and L9's speed cap at once.
