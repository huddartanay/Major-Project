# ASTRA — Research Playbook

**Written 13 September 2026.** Every step from now to submission, in order, for you to carry out.
Each step says what to do, how, what "done" looks like, and where the result goes.

Branch for all work: `3.0`. Commands are for **PowerShell** from `C:\Users\Dell\Documents\ASTRA`.

---

## What you are doing, in one paragraph

A runtime-assurance safety gate can be **alive, calibrated and confident — and blind** to a persistent
sensor fault. Prior work checks whether monitors are running (HALO), whether their outputs are confident
(conformal assurance monitors), and whether their assumptions hold (CoCo). **Nobody checks whether a
safety gate can still detect.** You will (1) prove the blindness happens and that existing monitor
checks miss it, and (2) build a **gate-blindness monitor** that detects it at runtime and stops the
system trusting the gate's silence.

**Working title:** *Alive, Calibrated, and Blind: Detecting Loss of Detection Capability in Runtime
Assurance for Learned Controllers*

## Documents you will use

| file | use it for |
|---|---|
| `docs/OBJECTIVES.md` | objectives and completion criteria |
| `docs/NOVELTY_CLAIMS.md` | what you may claim, and wording traps |
| `docs/NOVELTY_REVERIFICATION.md` | what the literature does and doesn't contain |
| `docs/MANUAL_NOVELTY_CHECK.md` | worksheet for Phase 1 |
| `docs/GAP_VERIFICATION.md` | evidence for the finding, with sources |
| `experiments/phase5_od8_h7/CLAIM_LEDGER.md` | the permanent record of what may be said |

## Rules that apply to every step

1. **Pre-register before you run.** Commit the design, metric and decision rule first. A result without
   a prior pre-registration commit is not evidence.
2. **The run is the unit.** Never treat ticks as independent samples.
3. **Tune on development seeds, evaluate on held-out seeds.** Development: `20260731 + i`, `i < 30`.
   Held-out: `20261201 + i`, `i < 30`. Freeze thresholds before touching held-out runs.
4. **Runtime code must not read ground truth** — no injected-fault identity, injector state, `truth_y`
   or `truth_speed`. Ground truth is for scoring only.
5. **Record failures in the claim ledger**, not just successes.
6. **Never tune a threshold after seeing the result it decides.**

---

# PHASE 0 — Housekeeping (day 1)

### 0.1 Push the branch

The evidence exists only on your machine. Nobody can verify it until this is done.

```powershell
git push origin 3.0
```

**Done when:** `git log origin/3.0 --oneline -1` shows the same commit as `git log --oneline -1`.

### 0.2 Independent reproduction

Ask Tanay (or anyone) to verify, in a **separate worktree** so the record is never overwritten:

```powershell
git fetch --all
git worktree add ..\astra-verify 3.0
cd ..\astra-verify
.venv\Scripts\python.exe -m pytest tests/ -q
.venv\Scripts\python.exe -m benchmarks.e21_baseline --seeds 5
```

They then check each element in `docs/GAP_VERIFICATION.md` against the files named there.

**Done when:** they confirm E1–E5, or report a mismatch. A mismatch is a finding — record it.

### 0.3 Make three decisions

| decision | options | notes |
|---|---|---|
| **Paper strategy** | one combined paper (finding + monitor) · or two papers | Combined is stronger; two is faster to a first submission |
| **Venue** | IEEE ITSC · IEEE ISSRE | Get deadlines from the **official call for papers** — do not trust any date written in this repo |
| **Preprint** | post on arXiv before submission · or not | **Recommended now that the patent application was rejected** — it timestamps the finding in a fast-moving area. Check the venue's preprint and anonymity policy in the call for papers first |
| **Code release** | release under an open licence with the paper · or not | The patent rejection removes the reason for withholding code, which `conference.md` and `research/PAPER_REJECTION_RISK.md` flag as a rejection risk. Choosing a licence needs agreement from all four authors in `pyproject.toml` and your guide |

Write the decisions at the top of `docs/OBJECTIVES.md` and commit.

---

# PHASE 1 — Verify the gap is really open (days 1–5)

**This phase decides whether the monitor is novel. Do not start Phase 3 until it is done.**

### 1.1 Manual check of the decisive papers

Work through `docs/MANUAL_NOVELTY_CHECK.md` **§1 first**:

1. **CoCo** (Ruchkin et al., ICCPS 2022, arXiv 2111.03782) — §4.2 assumptions; §5 case studies: is a
   sensor fault injected, and does CoCo's confidence drop on it?
2. **Papers citing CoCo** — Google Scholar → *Cited by* → *Search within citing articles*, one term at
   a time: `sensor fault`, `monitor failure`, `detection capability`, `blind`, `silent`,
   `runtime assurance`, `observation model`, `conformal`.
3. **Synergistic Simplex** — record the page of Assumption 8.

Then §2 and §3 of the worksheet. Fill the record table in §5.

**Done when:** every row in the worksheet's record table has an answer and a page number.

### 1.2 Systematic, logged search

This becomes **Appendix A** of the paper. Reviewers trust a documented search; they do not trust "we
found nothing".

**Step 1 — Fix the protocol before searching.** Create `docs/SEARCH_PROTOCOL.md` containing:

| item | value |
|---|---|
| Databases | IEEE Xplore · ACM Digital Library · Google Scholar · Semantic Scholar · arXiv · Scopus if the library provides it |
| Date range | January 2019 – date of search |
| Language | English |
| Inclusion | Runtime monitoring, runtime assurance, safety filtering or fault detection for autonomous or learning-enabled cyber-physical systems, **and** addresses at least one of: monitor reliability, monitor failure, sensor faults reaching a safety monitor, combining monitors |
| Exclusion | Offline testing only with no runtime monitor; perception accuracy only with no safety decision; hardware bit-flip studies with no monitor |
| The one question | *Does this work detect, at runtime, that a safety monitor or gate has lost its ability to detect faults?* |

**Commit the protocol before running any query.**

**Step 2 — Run the queries.** Each in every database. Use both vocabularies — control theory and
machine learning name the same idea differently.

```
Q1  "runtime assurance" AND ("sensor fault" OR "sensor failure")
Q2  ("safety monitor" OR "runtime monitor") AND ("monitor failure" OR "blind" OR "silent failure")
Q3  ("detection capability" OR "detectability") AND ("runtime" OR "online") AND monitor
Q4  ("monitor of monitors" OR "meta-monitor" OR "monitoring the monitor")
Q5  "closed-loop" AND "fault masking" AND ("neural" OR "learned" OR "reinforcement learning")
Q6  "integrity monitoring" AND ("safety filter" OR "runtime assurance" OR "controller")
Q7  "conformal" AND ("runtime monitor" OR "assurance monitor") AND ("missed detection" OR "false negative")
Q8  ("assumption monitoring" OR "verification assumptions") AND ("sensor" OR "observation")
Q9  ("persistent" OR "long-duration") AND ("sensor attack" OR "sensor fault") AND recovery
Q10 ("cross-layer" OR "inconsistency" OR "disagreement") AND ("safety monitors" OR "fault diagnosis") AND autonomous
```

**Step 3 — Screen in three passes and count.** Keep a spreadsheet `docs/search_log.xlsx` (or `.csv`):

| column | content |
|---|---|
| query | Q1–Q10 |
| database | |
| date run | |
| hits | total returned |
| title screened | kept after reading titles |
| abstract screened | kept after abstracts |
| full text read | kept after full text |
| answers the one question? | yes / no / partly |
| notes | citation and page |

**Step 4 — Snowball citations.** From these seed papers, list every reference (backward) and every
citing paper (forward), and screen them the same way:
CoCo · HALO · PID-Piper · DeLorean · Synergistic Simplex · Ferreira et al. survey (arXiv 2412.06869) ·
Yang et al. 2021 (introspective false-negative prediction).

**Step 5 — Stop** when two consecutive snowballing rounds add no new relevant paper.

**Step 6 — Write the flow counts** for the appendix: records found → after duplicates removed → titles
screened → abstracts screened → full texts read → included → answering the one question.

**Done when:** the log is complete and the flow counts are written.

### 1.3 Ask the experts

Researchers do this routinely. Send one short email to the CoCo authors and one to the Simplex group.

> Subject: Question about runtime detection of monitor blindness
>
> Dear Dr. [surname],
>
> I am an undergraduate researcher at BMS College of Engineering working on runtime assurance for
> learned controllers. We have found that a calibrated conformal safety gate can remain silent throughout
> a persistent sensor failure while another layer of the same stack detects it.
>
> Your work on [CoCo / Synergistic Simplex] is the closest we have found. Are you aware of any work that
> detects at runtime that a safety monitor has lost its ability to detect faults — as distinct from
> monitoring its liveness, confidence, or assumptions? We want to position our work correctly.
>
> Thank you for your time.
> [Name], BMS College of Engineering (guide: Dr. Chaitra R.)

Keep the first email short. If they reply with interest, a preprint link is the easiest thing to share.

### 1.4 Decision gate

| outcome | action |
|---|---|
| No work detects gate blindness | **Proceed** with the gate-blindness monitor (Phases 2–3) |
| CoCo's confidence drops on sensor faults like dropout | Proceed, but the monitor must win on faults CoCo-style monitors **miss**; Experiment 2.4 becomes essential |
| A paper already detects gate blindness | **Stop Phase 3.** Reposition against that paper. Fallback: cross-layer disagreement + no-silence routing in the persistent-fault regime |

Record the outcome in `docs/NOVELTY_CLAIMS.md` and commit.

---

# PHASE 2 — Complete the evidence for the finding (week 2)

### 2.1 How to pre-register any experiment

Create `experiments/phase5_od8_h7/<EXPERIMENT>/preregistration.md` with these sections, then commit it
**before** writing or running any analysis:

```
1. Question            — one sentence
2. Why it matters      — which claim it supports or could kill
3. Design              — policy, faults, severity, injection mode, ticks, seeds, arms
4. Metrics             — exact definitions; the unit of analysis
5. Decision rule       — thresholds that decide the verdict, fixed now
6. What would invalidate it
7. What it cannot establish
8. Prediction          — what you expect, stated so it can be wrong
```

Use `experiments/phase5_od8_h7/E21_BASELINE_COMPARISON/preregistration.md` as the model.

After running, add `final_decision.md`, update `CLAIM_LEDGER.md` and `CURRENT_STATUS.md`, and commit.

### 2.2 Recovery-trigger analysis (A5) — zero compute

**Question:** would a detect-then-recover pipeline gated on the conformal gate ever trigger?

**How:** from `experiments/phase5_od8_h7/E21_BASELINE_COMPARISON/raw_results/detections.json` and the
R3c records, compute for each fault the fraction of runs where the gate fires, and the latency
distribution. Compare with the `health` detector.

**Done when:** a table of trigger rate and latency per fault, per detector, is written up.

### 2.3 Confidence intervals on the correlations (A2b) — zero compute

**How:** bootstrap the Spearman correlations (discriminability vs detection) by resampling **runs**,
not ticks; report 95 % intervals and a per-fault breakdown. Use `benchmarks/e17_stats.py` (it has
`spearman` and a BCa bootstrap).

**Done when:** each correlation quoted anywhere has an interval next to it.

### 2.4 Experiment — do existing monitor checks catch the blind gate? (the key experiment)

**This tests the paper's central boundary.** Pre-register first (2.1).

**Monitors to implement as baselines** on the E21 protocol:

| baseline | represents | how |
|---|---|---|
| Liveness | HALO | does the gate produce a verdict every tick? (it always does — record it) |
| Confidence | conformal assurance monitors | the gate's own conformal p-value / credibility on each decision |
| Assumption validity | CoCo | calibrated monitors of observation-model assumptions: innovation consistency, sensor staleness, redundancy cross-check; combined into a confidence |

**Protocol:** P1, six faults, sustained from tick 200, 3,400 ticks, 30 development seeds plus a 30-run
clean arm. Metric: for each baseline, does it flag **the gate as untrustworthy** during the fault, at a
clean false-flag rate ≤ 0.10?

**Run:** write `benchmarks/e22_monitor_checks.py` modelled on `benchmarks/e21_baseline.py`, then

```powershell
.venv\Scripts\python.exe -m benchmarks.e22_monitor_checks --seeds 30
```

**Done when:** a verdict for each baseline and fault. **Most important cell:** does the CoCo-style
monitor flag the gate during `imu_dropout`, and during `speed_bias`?

### 2.5 Adaptive conformal comparison (A2c)

**Question:** is the blindness specific to split conformal, or does adaptive conformal also miss it?
Pre-register. Implement adaptive conformal inference, and the weighted conformal detector of Martinez Gil
et al. (arXiv 2604.20122), as alternative gates. Same protocol. About 90 minutes of compute each.

**Done when:** recorded either way. If adaptive conformal catches sustained dropout, narrow the claim to
split conformal.

### 2.6 Blindness signature across seeds (A4)

**Question:** is the disagreement between the gate and the sensor layer systematic, or a one-tick
observation? Pre-register. Measure, per fault, the fraction of post-onset ticks where a sensor-layer
check reports degradation **while** the gate is quiet, against the same fraction on clean runs, with
intervals across 30 seeds.

### 2.7 Matched classical controller (A3) — optional, decide first

**Question:** is the masking caused by the learned policy? Build a classical lateral-and-speed
feedback controller that reads the same estimated state the learned policy reads (note:
`KinematicPlaceholderPolicy` is **not** suitable — it ignores lateral position). Run the E21 protocol
with it.

Skip if time is short; then write "under a learned controller", never "caused by".

---

# PHASE 3 — Build the gate-blindness monitor (weeks 3–5)

**Only if Phase 1 said proceed.**

### 3.1 Write the specification first

Create `docs/GATE_BLINDNESS_MONITOR_SPEC.md` answering:

| question | constraint |
|---|---|
| **Inputs** | The gate's verdict and score (L6), plus evidence from other layers: L1 stream health, the redundancy cross-check, L2 innovation, L3 Trust Index |
| **Independence** | At least one evidence source must **not** pass through the fused estimate the gate reads. State which, and why — the method depends on it |
| **Decision** | Over a sliding window (not per tick): flag "blind" when other-layer evidence indicates a fault persistently while the gate stays within its clean band |
| **Calibration** | Threshold set by conformal calibration on **clean development runs**, at **window or run level** — this is what gives the provable bound on false "blind" flags |
| **Output** | `TRUSTWORTHY` / `BLIND`, plus a confidence, every tick |
| **Action** | When `BLIND`, L8 and L9 stop treating the gate's PASS as evidence of safety |
| **Forbidden inputs** | fault identity, injector state, `truth_y`, `truth_speed` |
| **Stated limit** | Can only flag blindness where some layer still sees the fault. Today nothing sees `speed_bias` / `speed_stuck` |

### 3.2 Write down the guarantee you will prove

State it precisely in the spec, for example:

> Under exchangeability of clean evaluation windows with clean calibration windows, the probability that
> the monitor flags a healthy gate as blind in a window is at most ε.

Then write the short proof (it follows from the standard split-conformal argument applied at window
level). **Do not claim a guarantee on catching blindness** — that half is empirical.

### 3.3 Implement

Suggested location: a new module alongside the Core-B layers, for example
`src/astra/layers/l6b_gate_capability/`. Keep the existing layers unchanged.

For every function: unit tests under `tests/unit/`. Run the full suite after each change:

```powershell
.venv\Scripts\python.exe -m pytest tests/ -q
```

### 3.4 Develop and freeze

1. Tune window length and calibration level on **development seeds only**.
2. **Freeze** every threshold. Commit with a message stating they are frozen.
3. Only then continue.

### 3.5 Pre-register the evaluation

Pre-registration (2.1) must fix: held-out seeds `20261201 + i`; the success criteria below; the baselines
from 2.4; leave-one-fault-out.

**Success criteria** (from `docs/OBJECTIVES.md`, B1 and B3):

| criterion | bar |
|---|---|
| Flags gate blindness under sustained `imu_dropout` | ≥ 27 / 30 held-out runs, within 20 ticks (1 s) |
| False "blind" flags on clean runs | ≤ 3 / 30, **and** within the proved bound ε |
| Leave-one-fault-out | ≥ 0.80 flag rate on each held-out fault class that some layer can see |
| Against baselines from 2.4 | flags blindness they miss |
| With routing on vs off | stack never quieter than its clean baseline with routing on; sustained silence returns with routing off |

### 3.6 Run, then report honestly

Run on held-out seeds. Write `final_decision.md`. Update the claim ledger — **including every criterion
that failed**.

### 3.7 Optional — speed-channel coverage

If you want the monitor to cover `speed_bias` and `speed_stuck`, add a monitor that observes the speed
channel directly. Otherwise state the limit in the paper.

---

# PHASE 4 — External validation on comma2k19 (start in week 1, runs in parallel)

This is the longest task. **Start early.**

1. **Acquire.** Download one or two chunks from the official comma2k19 source (the full set is ~100 GB
   in ~10 GB chunks). Check the licence (MIT) and record it.
2. **Hash.** Record a SHA-256 of every file you use in `docs/COMMA2K19_MANIFEST.md`.
3. **Freeze the split** before looking at results: which segments are for development and which are
   held out. Commit.
4. **Build a replay harness** that feeds logged IMU, CAN speed and GNSS into L1 and L2.
5. **Inject the same fault classes** into the logged streams.
6. **Measure sensor-level evidence only**: stream health, redundancy cross-check, innovation. Does the
   evidence the gate-blindness monitor relies on exist on real sensor noise?
7. **State the limitation in the paper:** replay is open-loop — the logged vehicle does not respond to
   ASTRA — so closed-loop masking cannot occur and the blindness itself cannot be reproduced there.

**Done when:** a first `[M-ext]` row exists in the claim ledger.

---

# PHASE 5 — Write the paper (weeks 5–7)

### 5.1 Structure (IEEE conference, ~6–8 pages)

| section | content | source |
|---|---|---|
| Abstract | Problem, finding, monitor, key numbers | — |
| I. Introduction | Runtime assurance checks liveness, confidence, assumptions — not detection capability. Contributions list | `NOVELTY_CLAIMS.md` §8 |
| II. Related work | Runtime assurance & Simplex · safety filters under estimation error · integrity monitoring · detect-and-recover · monitor assurance (HALO, conformal assurance, CoCo) · closed-loop fault masking | `NOVELTY_REVERIFICATION.md` |
| III. Problem | Definitions: gate, detection capability, blindness | spec |
| IV. The finding | Alive, calibrated, blind; existing checks miss it | E18-R3, R3c, E21, experiment 2.4 |
| V. Gate-blindness monitor | Design, independence condition, calibration, guarantee and proof | Phase 3 |
| VI. Evaluation | Protocol, held-out results, baselines, ablation, leave-one-fault-out, comma2k19 | Phases 3–4 |
| VII. Limitations | One plant, P1, `medium`, speed faults, open-loop replay | ledger |
| VIII. Conclusion | | |
| Appendix A | Systematic search protocol and flow counts | Phase 1.2 |

### 5.2 Figures and tables to produce

1. Architecture diagram with the new monitor marked.
2. Alarm rate by phase: faulted vs clean baseline (shows "quieter than healthy").
3. Detection matrix: fault × monitor (gate, health, liveness, confidence, CoCo-style, blindness monitor).
4. False "blind" flag rate vs the proved bound ε.
5. Routing on vs off.
6. Search flow counts.

### 5.3 Every claim must map to evidence

Before writing a sentence that states a result, find its row in `CLAIM_LEDGER.md`. **No row, no
sentence.**

### 5.4 Wording traps — check every draft against these

From `docs/NOVELTY_CLAIMS.md` §9. The most important:

- Not "novel architecture" — the architecture is the instrument.
- Not "first" — "to our knowledge", with Appendix A behind it.
- 0.998 is the **sensor** discriminability; the gate's is **0.737**.
- The clean baseline is **5.84 %** (median), not "about 5 %".
- The low alarm rate is a **miss**, never "fewer false alarms".
- A conformal guarantee is **marginal** — not "holds on every run".
- "Silent failure" and "hazardously misleading information" are **existing terms** — cite them.
- "Under a learned controller", not "caused by", unless 2.7 was done.

---

# PHASE 6 — Before submission (week 8)

| # | check | how |
|---|---|---|
| 1 | Every citation real and correct | Open each; confirm authors, year, venue, and that it says what you cite it for |
| 2 | Every number re-measured from `3.0` | Re-run or re-read each figure's source file; no number copied from an old document |
| 3 | Test suite green | `.venv\Scripts\python.exe -m pytest tests/ -q` |
| 4 | Red-team | Give the draft to someone unfamiliar with it; ask them to find the weakest claim |
| 5 | Zero open P0 | `conference.md` gate |
| 6 | Venue compliance | Page limit, template, anonymisation rules, author list, no concurrent submission |
| 7 | Guide sign-off | Dr. Chaitra R. — including the licence chosen for code release |
| 9 | Stale confidentiality text removed | `README.md`, `NOTICE`, `LICENSE`, `docs/ASSUMPTIONS.md` (A-7), ADR-0014 and `conference.md` still describe a pending patent. A reviewer who finds "withheld pending patent" next to a public repository will ask why |
| 8 | Reproducibility | Code and protocol ready to release, or a stated reason why not |

---

# PHASE 7 — Submit, then

1. Submit before the official deadline.
2. Tag the commit: `git tag submission-<venue>-<year>` and push the tag.
3. Record the submission in `CURRENT_STATUS.md`.
4. While under review: start **fault-specific recovery gated on trusted detection** (objective B4), then
   adversarial sensors (B6).

---

## Rough timeline

| week | work |
|---|---|
| 1 | Phase 0 · Phase 1 · start Phase 4 |
| 2 | Phase 2 |
| 3–5 | Phase 3 · Phase 4 continues |
| 5–7 | Phase 5 |
| 8 | Phase 6 · submit |

Adjust to the real deadline once you have it.

## Decision gates in one place

| gate | when | if it fails |
|---|---|---|
| Push and reproduction | end of Phase 0 | Nothing can be verified — fix before continuing |
| Gap still open | end of Phase 1 | Stop Phase 3; reposition; fallback direction |
| Existing checks miss the blind gate | after 2.4 | Narrow to the faults they miss |
| Adaptive conformal also blind | after 2.5 | Narrow claim to split conformal |
| Held-out success criteria | end of Phase 3 | Report honestly; submit the finding alone |

## Command cheat sheet

```powershell
# tests
.venv\Scripts\python.exe -m pytest tests/ -q

# existing experiments
.venv\Scripts\python.exe -m benchmarks.e21_baseline --seeds 30
.venv\Scripts\python.exe -m benchmarks.phase2_monitorability

# live views
.venv\Scripts\python.exe -m demo.dashboard
.venv\Scripts\python.exe -m demo.narrate --fault dropout --at 200 --explain --every 10 --pause 0.05 --ticks 400

# safe reproduction
git worktree add ..\astra-verify 3.0
```
