# ASTRA — handoff for Tanay (19 September 2026)

From: Sushanth. For: Tanay S. Huddar.
Branch: **`3.0`** on `origin` (`huddartanay/Major-Project`).

Your copy is out of date. GitHub's `3.0` stopped at **2 September** (`5142cc2`). This push adds
**77 commits** (2–19 September): new experiments, several fixes, and the full literature review that
decided the paper's direction. Read §1 to update, then §2–§5 to catch up (§5 lists every result so far). §6–§9 are the plan,
the gap each phase covers, and how we split the work.

---

## Contents

1. Update your copy
2. What changed since your version
3. Where the research stands, in plain terms
4. The numbers we rely on
5. Main research results, experiment by experiment
6. The plan and deadlines
7. Which gap each phase covers
8. Stage-by-stage: what to do and how
9. Proposed split of work
10. Rules for running experiments
11. Architecture notes you need before touching code
12. Literature: what is done and what is left
13. Collaboration and outreach
14. Housekeeping and open decisions
15. Your first-day checklist
16. Where everything lives

---

## 1 · Update your copy

Commands for **PowerShell** on Windows. Use `;`, not `&&` — Windows PowerShell 5.1 rejects `&&`.

### 1.1 If you have no local changes you care about

```powershell
cd C:\path\to\your\ASTRA
git fetch origin
git checkout 3.0
git reset --hard origin/3.0
```

`reset --hard` **throws away** anything uncommitted in your folder. Only use it if you are sure.

### 1.2 If you have local changes to keep

```powershell
cd C:\path\to\your\ASTRA
git status
git stash push -m "tanay-local-before-sync"
git fetch origin
git checkout 3.0
git pull --ff-only origin 3.0
git stash pop
```

If `stash pop` reports conflicts, stop and message me — do not force anything.

### 1.3 Install and check it works

The project uses **uv** (see `docs/INSTALL.md`). Python 3.12 or newer.

```powershell
uv sync --all-groups --all-extras
uv run pytest -q
```

Expected: about **3,067 tests passing**. If you do not use uv, the existing `.venv` works too:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

### 1.4 Quick sanity run (about 20 seconds)

This drives one faulted run and prints the vehicle's mode history summary:

```powershell
.venv\Scripts\python.exe experiments\phase5_od8_h7\EXPLORATORY_DEESCALATION\deesc_probe.py 3400 1 speed_bias out.json
```

You should see `"peak": "NOMINAL"` — under `speed_bias` the car never leaves normal mode. That is one of
the findings in §5.

### 1.5 The demo

```powershell
.venv\Scripts\python.exe -m demo.dashboard --port 8000
.venv\Scripts\python.exe -m demo.narrate --explain --every 20
```

Hosting notes are in `DEPLOY.md`. The dashboard also lives at
`github.com/Sushanth-1000/simulation_dashboard`.

---

## 2 · What changed since your version (2 → 18 September)

### 2.1 Experiments (all under `experiments/phase5_od8_h7/`)

| experiment | what it found |
|---|---|
| **E18-R3** | The earlier limitation was precision, not dynamics |
| **E18-R3b** | A short fault is invisible to the L6 gate *while it happens* |
| **E18-R3c** | A **sustained** `imu_dropout` is invisible too: gate alarm rate ≈0.2 %, **0/30** runs detected |
| **Phase 2 monitorability** | Monitorability is weak and blind to the fault that matters (identity-free ρ = 0.654, p = 0.011, n = 15; headline 0.895 was confounded) |
| **E21 baseline comparison** | **The old detectors win:** L1 stream health catches `imu_dropout` in **30/30** runs, **0/30** false alarms on clean runs, exactly **5 ticks** latency. The blind spot is architectural, not statistical. `speed_bias` and `speed_stuck` are missed by everything |
| **Exploratory de-escalation probe** (18 Sept, dev seeds, not pre-registered) | The failsafe **steps back down while a fault persists** (`position_drift`, 5/5 runs); speed faults keep the car in **NOMINAL for 100 %** of the faulted run |

### 2.2 Code fixes you should know about

| fix | file | why it matters |
|---|---|---|
| Drift scaled by the run length actually driven | `benchmarks/e18_evaluate.py` | R3b's `position_drift` arm was inflated to ~32 m before this |
| `on_assembled` can receive the plant | `training/closed_loop.py` | Needed by the dashboard |
| `FaultInjector.stand_down()` | `training/faults.py` | Clears faults mid-run (dashboard) |
| Two brittle single-draw tests replaced with measured properties | `tests/integration/test_closed_loop_faults.py` | They passed or failed by luck |
| Dashboard made honest and hostable; Streamlit entry point removed | `demo/` | Plots real truth/estimate with an adaptive axis |
| Terminal narrator | `demo/narrate.py` | Tick-by-tick explanation |

### 2.3 Documents added (all in `docs/` unless stated)

The literature review and gap work — see §12 and §16 for the full map. Most important:
`GAPS_CONFIRMED.md`, `LITERATURE_SYNTHESIS.md`, `LESSONS_FROM_20_PAPERS.md`, `NEW_PAPERS_AND_GAPS.md`,
and `research.md` (root) — the step-by-step playbook.

### 2.4 Decisions made

- **The patent application was rejected.** No disclosure limits now: preprints and open code are fine.
  (The LICENSE / NOTICE / README still carry old "confidential" text — see §14.)
- **Paper direction** changed from "ASTRA the architecture" to **one sharp problem**: safety gates that
  fail silently. §3 explains; §5 lists every result.

---

## 3 · Where the research stands, in plain terms

### The setup

The car has an AI driver (the PPO proposer, L4) and a **safety guard** (the L6 conformal gate) whose job
is to raise an alarm when the AI's command looks wrong.

### The gaps we are solving in Paper 1

| gap | plain meaning | status |
|---|---|---|
| **G1 · The guard fails silently** | When a sensor breaks mid-drive and **stays** broken, the guard does not crash or complain — it just **stops raising alarms**. Like a smoke detector clogged with dust: light on, never beeps | ✅ **Verified** in literature (≈39 papers read in depth, none shows it) and in our data |
| **G1's harm** | Because the guard is silent, the car **stays in normal mode at full speed** through the fault | ✅ Measured (18 Sept probe) |
| **G3 · Why it goes silent** | The gate's score is `departure ÷ √P_f` (filter uncertainty). A dead sensor makes the filter **less certain**, √P_f grows, the score shrinks — the guard relaxes exactly when it should tighten | ⚠️ **Hypothesis (H1).** Supported by the code and by navigation literature; **not tested yet** — this is Stage A |
| **G2 · Catching the blind guard without labels** | A "watchdog for the watchdog": if an independent layer (L1 sensor health) says "fault" while the guard stays silent, flag the guard as blind and stop trusting its approvals | ✅ Open **as a problem** for vehicle safety gates. ⚠️ The **method** is narrowed: label-free harmful-shift detection exists in other fields (Amoukou et al., NeurIPS 2024; D3M, NeurIPS 2025). **Not built yet** |

**Paper 1 in one sentence:**
> Safety gates in autonomous vehicles can silently stop working when a sensor fails (G1), because the
> car's growing uncertainty makes every command look acceptable (G3); we detect this without labels by
> comparing the gate against an independent sensing layer, and fall back to safer behaviour (G2).

### Saved for later papers — do not put these in Paper 1

| gap | plain meaning | status |
|---|---|---|
| **G4 · Silence mistaken for recovery** | The car steps back down to normal because every alarm went quiet, not because the fault went away | ✅ Seen in 5/5 `position_drift` runs (exploratory). Competition to read first: arXiv 2608.07061, 2401.09678. **Paper 2** |
| **G5 · Attackers blinding the guard** | Spoofing designed to stay under every threshold | Candidate (REQUIEM, arXiv 2407.15003). **Paper 3** |
| **G6 · Semantic errors** | Sensors agree on something wrong (stale map, wrong frame) | Weak evidence. Later |

One paper, one gap: reviewers reward depth. G1 is the gap; G3 and G2 are its explanation and its fix.

### Never claim these

| claim | why not |
|---|---|
| "First monitor of a monitor" | HALO (liveness), CoCo (assumption confidence), Lukina (precision), Antonante (unreliable tests) |
| "A new statistical test" | KS(conf), conformal martingales, ACI, Amoukou already exist |
| "The problem is surely unsolved" / "the first to…" | Say **"to our knowledge, no prior work…"** |
| "Solves adversarial sensors" | We inject faults only |
| "Hands over to a human" | Only a flag (`human_intervention_requested`) exists |

---

## 4 · The numbers we rely on

All from result files on this branch. Seeds: **dev** `20260731 + i`, **held-out** `20261201 + i`.
Frozen gate threshold **3.7024** (v3).

| quantity | value | source |
|---|---|---|
| Gate false-alarm rate, clean runs (median) | **5.84 %** (range 4.66–8.22 %), 30/30 in band | E18-R3 P1 |
| Gate alarm rate, sustained `imu_dropout` | **≈0.2 %** (0.38 / 0.18 / 0.20 / 0.21 %) | E18-R3c |
| Gate run-level detection, sustained `imu_dropout` | **0/30** | E18-R3c |
| Ticks 400–999 alarm rate, R3b vs R3c | 99.06 % vs 0.18 % | E18-R3b/c |
| L1 health, `imu_dropout` | **30/30**, 0/30 clean false alarms, latency exactly **5 ticks** | E21 |
| Score separation `imu_dropout` (D_s) | L1 0.998, **L6 0.737 [0.675, 0.777]**, L8 0.988 | E17 P1 |
| `position_bias` detection latency | 13–19 ticks | E21 |
| `position_drift` detection latency | 957–1153 ticks | E21 |
| `speed_bias`, `speed_stuck` | **Undetected by every layer** | E21 |
| Time in NOMINAL after onset, speed faults | **100 %** (5/5 dev seeds) | exploratory probe |
| De-escalation while `position_drift` persists | **5/5** runs, first at ticks 1264–1387 | exploratory probe |

**Important wording:** E17 shows the L6 *score* still separates `imu_dropout` (0.737). So the gate is
**alarm-blind at its calibrated threshold**, not "information-free". Do not write that the score carries
no information.

---

## 5 · Main research results, experiment by experiment

What each experiment asked, what it found, and what it means for the paper. Folders are under
`experiments/phase5_od8_h7/`; the running summary is `EXPERIMENT_INDEX.md` and the claims ledger is
`CLAIM_LEDGER.md`. "OD-8" is the L6 conformal gate's detector.

| # | experiment | question | result | decision | what it means for us |
|---|---|---|---|---|---|
| 1 | **E17** | How observable is each fault at each layer? | Heterogeneous. Separation D_s for `imu_dropout`: L1 0.998, **L6 0.737 [0.675, 0.777]**, L8 0.988. Only 1 of 6 faults showed well-posed absorption | Baseline | L1 sees `imu_dropout` far better than the gate: first hint of G1 |
| 2 | **E17-Position** | Does absorption survive correct injection? | Absorbed in **0 of 12** cells | **Claim withdrawn** | We do not claim estimator absorption of position faults |
| 3 | **E18** | Can OD-8 be validly calibrated? | Failure was **calibration-set provenance**, not threshold value. Frozen v1 thresholds P1 3.7095, P2 5.9024, P3 3.4000. **D_s does not predict detection** (17/28 cells disagree; rho = -0.480). **Fault-induced alarm suppression in 11/28 cells** (all p < 0.05): `imu_dropout` makes the gate **55x less likely** to alarm than clean driving. `speed_stuck` and `imu_dropout` undetectable at any severity. P2 invalid (score drifts upward in 30/30 runs) | PARTIAL; P1 verdict later withdrawn | **Earliest evidence of G1**: the gate goes quieter under a fault |
| 4 | **E18-R1** | Does run-local calibration help? | P3 9/30 in band; mechanism removed but estimator too noisy. **Found E18's window defect** (false alarms measured on ticks 0-399, detection on 200-399) | FAIL-P3 | E18's "P1 VALID" withdrawn |
| 5 | **E18-R2** | Does matched-window pooled calibration work? | P1 13/30 (best of 3); the obstacle is the score process, not the threshold | PARTIAL-R2 | Calibration must be judged per run, on the matched window |
| 6 | **E18-R3** | Precision-limited or dynamics-limited? | **P1 30/30 in band** at n = 3,200 (160 s); false-alarm median **5.84 %** (4.66-8.22 %); frozen threshold **3.7024** (v3) | **PASS-R3** | The gate *can* be calibrated, so its later silence is not a calibration failure |
| 7 | **E18-R3b** | Does it detect faults at the long window? | 4/6 faults at 100 %, but the detection comes from the **post-fault transient** when the fault ends, not from the fault itself | PASS, mechanism refuted | "Detection while it happens" was an illusion |
| 8 | **E18-R3c** | Is detection the aftermath, or the sustained fault? | Sustained `imu_dropout`: alarm rate **~0.2 %**, **below the clean baseline**, **0/30** runs. Ticks 400-999: 99.06 % (R3b) vs 0.18 % (R3c). Only 3/6 faults detected under sustained injection | **H-AFTERMATH SUPPORTED** | **The core G1 result** |
| 9 | **Phase 2 monitorability** | Can we predict where the gate will be blind? | Identity-free rho = 0.654 (p = 0.011, n = 15); headline 0.895 was confounded; D_s rho = 0.077 (p = 0.72) | Weak | Blindness is not predictable from simple observability, so a runtime check (G2) is needed |
| 10 | **E21 baseline comparison** | Do existing detectors beat the gate? | **Yes.** L1 stream health: `imu_dropout` **30/30**, **0/30** clean false alarms, latency exactly **5 ticks**. `position_bias` 13-19 ticks; `position_drift` 957-1153 ticks. `speed_bias`, `speed_stuck`: **undetected by every layer**. Trust clean false-positive 0.767; innovation monitor ~0 | **BASELINE WINS** | The blind spot is **architectural**: an independent layer sees what the gate cannot. This is the basis of G2 |
| 11 | **Exploratory de-escalation probe** (18 Sep) | Does the failsafe step down while a fault persists? | `position_drift`: steps down in **5/5** runs (ticks 1264-1387) while the gate passes and L1 is momentarily healthy; ~36 % of the faulted period spent in NOMINAL. `speed_bias` / `speed_stuck`: **100 % in NOMINAL** | Exploratory only (dev seeds, not pre-registered) | G1's harm (the car stays in normal mode) and first evidence for G4 (Paper 2) |
| - | **E19** (monitor placement), **E20** (lying sensor) | - | **Not run**: the folders exist but are empty | - | E20 becomes relevant for G5 later |

### The story the results tell, in order

1. The gate **can** be calibrated (R3), so what follows is not a tuning problem.
2. Under a sustained sensor fault it goes **quieter than when healthy** (E18, R3c): **G1**.
3. What looked like detection was the fault *ending* (R3b), so it truly misses faults while they last.
4. An **independent layer (L1) sees the fault at once** (E21). The blind spot is architectural, which is
   exactly what **G2** exploits.
5. Because the gate is silent, the car **stays in normal mode**, and can even **step back down** while a
   fault persists (probe): the practical harm, and G4 for later.
6. **Why** it goes silent is still open. That is **G3**, Stage A.

---

## 6 · The plan and deadlines

Deadlines checked on 18 September 2026 against the official calls.

| venue | deadline | pages | fit | plan |
|---|---|---|---|---|
| **IEEE IV 2027** (Perth, 15–18 Jun 2027) | **15 Nov 2026** | 6 | Strong | **G1 + G3 only**, *if* Stage A confirms H1 by ~5 Oct |
| IEEE/IFIP DSN 2027 (Berlin) | abstract 25 Nov, paper **2 Dec 2026** | 11 | Strong, top tier | Too early for us — skip |
| **IEEE ITSC 2027** (Boston, 21–24 Sep 2027) | **1 Mar 2027** | ~6–8 | Strong | **Main target: G1 + G3 + G2** |
| IEEE/RSJ IROS 2027 (Florence) | 1 Mar 2027 (tracker sites; verify) | ~6–8 | Good | Alternative to ITSC |
| ICCPS 2027 | not announced; historically early–mid Oct | — | Strong, top tier | Probably too soon |
| ICRA 2027 | closed 16 Sep | — | — | Missed |
| ICDCN 2027 | closed 13 Aug; networking topic | — | Poor | No |

Official pages: IV `ieee-iv.org/2027/contributions/call-for-papers/`, DSN
`dsn2027-berlin.github.io/call-for-contributions/`, ITSC `ieee-itsc.org/2027/contributions/call-for-papers/`.

### Timeline

| phase | dates | goal | output |
|---|---|---|---|
| **A · Mechanism** | 19 Sep – 5 Oct | Test G3 (why the gate goes silent) | Go / no-go for IV |
| **B · IV paper** | 6 Oct – 15 Nov | Write G1 + G3 | IV submission |
| **C · Breadth + G2** | Oct – Jan | Build and test the blindness monitor | ITSC core results |
| **D · Confirm + write** | Jan – 1 Mar | Held-out runs, second setting, paper | ITSC submission |
| Parallel | throughout | Last literature, preprint, outreach | — |

**Two papers must not overlap.** IV = G1 + G3. ITSC = G2 (cites IV for G1/G3). Never submit the same
results twice.

---

## 7 · Which gap each phase covers

| phase | dates | gap(s) | question answered | evidence produced | success criterion | paper |
|---|---|---|---|---|---|---|
| Done (E17-E21) | Aug - Sep | **G1** | Does the gate fail silently? | R3c, E18 suppression, E21 | Met: 0/30 detected, alarms below clean | Paper 1 |
| Done (probe) | 18 Sep | **G1's harm**, G4 hint | Does the car stay in normal mode? | Exploratory probe | Seen; needs a pre-registered replication | Paper 1 (harm), Paper 2 (G4) |
| **Stage 0** | this week | validity | Are paper runs free of demo code? | Demo hack behind a flag | Flag off by default, tests pass | - |
| **Stage A** | 19 Sep - 5 Oct | **G3** | Why does the gate go silent? | sigma vs departure per tick; mode and true error | Pre-registered rule picks H1/H2/H3 on dev seeds, confirmed on held-out | Paper 1 (IV) |
| **Stage B** | 6 Oct - 15 Nov | **G1 + G3** | Can we state it generally? | Proposition plus at least 3 faults with CIs | Proposition matches the data; IV submitted | **IV 2027** |
| **Stage C1** | Oct - Nov | **G1 breadth**; G2's "so what?" | Which faults does L1 miss while the gate still reacts? | Magnitude sweep incl. small faults | At least one such fault class, or an honest report that none exists | ITSC |
| **Stage C2** | Nov - Jan | **G2** | Can we detect the blind gate without labels? | `GateBlindnessMonitor` plus 8 baselines | Beats Amoukou, D3M and KS(conf) on time-in-NOMINAL-while-faulted; false-flag rate within bound | ITSC |
| **Stage C3** | Dec - Jan | **G2 outcome** | Does acting on the flag help? | With/without the monitor; Safety Gain, Residual Hazard, Availability Cost | Less time in NOMINAL under fault; bounded extra escalation on clean runs | ITSC |
| **Stage D** | Jan - 1 Mar | **G1-G3 generality** | Does it hold beyond one setup? | Held-out confirmation plus comma2k19 replay **or** a classical controller | All pre-registered criteria hold on held-out seeds | **ITSC 2027** |
| Paper 2 | after ITSC | **G4** | Is silence mistaken for recovery? How to re-certify a monitor before recovering? | Pre-registered de-escalation study plus re-certification probe | - | Paper 2 |
| Paper 3 | later | **G5** (+ G6) | Can an attacker blind the gate? | Stealthy-lie experiments (E20) | - | Paper 3 |

---

## 8 · Stage-by-stage: what to do and how

### Stage 0 · Housekeeping (this week)

1. **Put the demo speed hack behind a flag, default off.** In `training/closed_loop.py` (around line 864)
   the plant's speed is reset to the reference while the failsafe is NOMINAL and speed < 1 m/s. It was
   measured as inert, but paper runs must not contain demo code paths.
2. Keep pushing `3.0` after every session so nothing lives on one laptop.

### Stage A · Mechanism (G3) — 19 Sep to 5 Oct

**Question:** why does the L6 gate go silent under a sustained sensor fault?

The score splits into two parts: `log(score) = log(departure) − log(σ)`. The gate **already records**
`departure`, `sigma`, `non_conformity_score`, `conformal_quantile` and `effective_epsilon` in its
evidence every tick (`src/astra/layers/l6_statistical_gate/gate.py:325`). No architecture change needed.

| hypothesis | what the data would show |
|---|---|
| **H1 · σ inflates** | σ rises after onset; departure roughly flat |
| H2 · departure collapses | departure falls (our earlier common-mode pilot argued against this) |
| H3 · threshold moves | quantile changes — unlikely: FB3 is unwired, shift detector only lowers the threshold |

**Steps**

1. Write `experiments/phase5_od8_h7/STEP1_MECHANISM/preregistration.md` **before running anything**:
   hypotheses, metrics, decision rule, seeds.
2. Logger (benchmark code only): per tick record departure, σ, score, quantile, ε, failsafe state,
   OOD and integrity counters, **and the true tracking error** from the plant.
3. Run on **dev seeds** (`20260731 + i`), sustained faults from tick 200, 3,400 ticks, clean arm too.
   Reuse `benchmarks/e21_baseline.py`'s injectors.
4. Decide per the pre-registered rule. Then confirm on **held-out seeds** with nothing changed.
5. Write `final_decision.md`, update `CLAIM_LEDGER.md`.

**Decision on ~5 Oct:** H1 confirmed → Stage B (IV). Not confirmed → skip IV, investigate H2, all effort
to ITSC. G1 stands either way.

### Stage B · IV paper (only if H1 holds) — 6 Oct to 15 Nov

- **Formal proposition:** for a gate scored as departure/σ, if σ grows by factor k after a fault, the
  alarm probability for a fixed departure distribution falls accordingly. Prove it; check it against data.
- **Figures:** alarm rate before/after onset; σ and departure over time; time in NOMINAL under fault.
- **Faults:** `imu_dropout` plus at least two others, with confidence intervals (Clopper–Pearson for
  zero-event rates).
- **Keep G2 out.**

### Stage C · Breadth and G2 — October to January

1. **Fault sweep across magnitudes, including small ones.** Find faults that **L1 misses but that still
   change the gate's behaviour** — this is the answer to the reviewer question "L1 already catches
   `imu_dropout` in 5 ticks, so what?".
2. **Build `GateBlindnessMonitor`** (new component, Core-B side):
   - Inputs: L6 evidence (score, σ, departure, alarm) and L1 frame health.
   - Output: blindness snapshot (flag, statistic, confidence).
   - One-sided test (too **few** alarms), calibrated on **whole clean runs** (tick scores are correlated).
   - Bound on false "blind" flags.
3. **Reaction:** when flagged, **L6 abstains**, reusing the ADR-0016 path the gate already uses when it has
   no finite threshold; the verdict falls to L7a/L7b. Write an **ADR**. This keeps L8 gate-agnostic, which
   SI-3 requires (`src/astra/layers/l8_failsafe/machine.py:212`).
4. **Baselines** (benchmark code only):

   | baseline | role |
   |---|---|
   | KS(conf) (Sun & Lampert, arXiv 1804.04171) | score-distribution test |
   | Conformal test martingale (Volkhonskiy et al., arXiv 1706.03415) | sequential p-value test |
   | **Amoukou et al.** (arXiv 2412.12910) | label-free harmful shift — **primary baseline** |
   | **D3M** (arXiv 2506.05047) | label-free disagreement |
   | ModelGuard-style (arXiv 2104.15006) | model invalidation; may catch dropout, miss bias |
   | L1 health alone | what exists today |
   | WATCH (arXiv 2505.04608) | **upper bound** — given labels |
   | Gate fed ground truth | oracle reference |

5. **Outcome experiment** — with vs without the monitor:
   - time in NOMINAL while faulted (headline);
   - time to reach DEGRADED / LIMP;
   - needless escalation on clean runs;
   - Safety Gain / Residual Hazard / Availability Cost (Guerin et al., arXiv 2208.14660).

   Pre-registered pass rule: G2 beats the label-free baselines on time-in-NOMINAL-while-faulted, with its
   false-flag rate inside the bound, on held-out seeds.

### Stage D · Confirm and write — January to 1 March

- Held-out confirmation, thresholds frozen.
- **One** generality addition:
  - **comma2k19 open-loop replay** — note: **no loader exists in the code yet**; it is only mentioned in
    slide scripts. Needs a loader, a mapping to L1/L2, and fault injection on replayed streams. Useful
    for the false-flag rate on real sensor noise; **cannot** show closed-loop behaviour or outcomes; **or**
  - a **classical controller** (PID/MPC) alongside PPO.
- Write ITSC paper; G2 is the main contribution, cite IV.

### Risks

| risk | fallback |
|---|---|
| H1 refuted | G1 still stands; skip IV; investigate H2; target ITSC |
| G2 does not beat Amoukou | Publish the characterisation: where each method fails and why an independent layer is needed |
| No time for comma2k19 | Second controller instead; state real data as a limitation |

---

## 9 · Proposed split of work

A proposal — change it as you like.

| area | Tanay | Sushanth |
|---|---|---|
| Remaining literature (§12) — needs IEEE Xplore / Springer via college | **Lead** | review |
| G3 literature search (covariance-normalised monitors) | **Lead** | review |
| Stage 0 housekeeping, Stage A pre-registration and logger | review | **Lead** |
| Stage A analysis and the formal proposition | **joint** | **joint** |
| Baseline implementations (KS(conf), martingale, Amoukou, D3M, ModelGuard-style) | **Lead** | review |
| `GateBlindnessMonitor` + ADR | review | **Lead** |
| Outcome experiment | **joint** | **joint** |
| comma2k19 loader (if chosen) | **Lead** | review |
| IV paper writing | related work + experiments section | intro, mechanism, results |
| Preprint and outreach | **joint** | **joint** |

Rule: whoever leads an experiment writes its pre-registration; the other person reads it **before** any
run.

---

## 10 · Rules for running experiments

These are what make the results defensible. They are not optional.

1. **Pre-register first.** `preregistration.md` is committed **before** the first run: hypotheses,
   metrics, decision rule, seeds, thresholds.
2. **Dev seeds for development** (`20260731 + i`). **Held-out seeds** (`20261201 + i`) only for the
   final confirmation, **once**, with everything frozen.
3. **Frozen threshold** 3.7024 unless a pre-registration says otherwise.
4. **No ground truth at runtime.** Anything the monitor reads must be available on a real car.
5. **Raw results committed** under `raw_results/`, analysis under `processed_results/`, decision in
   `final_decision.md`, and a line in `CLAIM_LEDGER.md`.
6. **Report failures.** A refuted hypothesis is written up the same way as a confirmed one.
7. **Test the code, not the docs.** When a doc and the code disagree, the code is right — check it.
8. **Exploratory runs are labelled exploratory** (like the de-escalation probe) and never quoted as
   results.

---

## 11 · Architecture notes you need before touching code

### Layers

L1 sensing → L2 estimation (UKF) → L3 trust → L4 proposer (PPO) → L5 twin → L6 conformal gate →
L7a shield / L7b physical → L8 failsafe → L9 arbitration (RCM).

### What is and is not wired

| part | status | where |
|---|---|---|
| FB1 · UKF re-anchor | ✅ wired | `src/astra/runtime/pipeline.py:492` |
| Shift detector → ε | ✅ wired; only **lowers** the threshold | `pipeline.py:547`, `gate.py:203` |
| FB2 · twin adaptation | ❌ not wired; shadow only | `pipeline.py:348`, `:720` |
| FB3 · online requantilisation | ❌ unwired **on purpose** (self-referential threshold) | `gate.py:242` |
| FB4 · simulator sync | ❌ enum only; prototype-only | `kernel/enums.py:472` |
| HALT recovery | ❌ only `reset()`, called only by the demo | `l8_failsafe/machine.py:756` |
| Handover to human | ❌ a flag only | `observability/explain.py:183` |

Paper wording: *the twin is frozen and the threshold static during evaluation.*

### Failsafe modes (L8)

| mode | behaviour | dev-config cap | leaves by |
|---|---|---|---|
| NOMINAL | AI drives | — | — |
| DEGRADED | fallback PID drives | 40 km/h | automatic, with hysteresis |
| LIMP | no lane changes | 20 km/h | automatic |
| HALT | full braking to 0 | 0 | **manual `reset()` only** |

Escalation takes the **worse** of two counters: the OOD counter (gate vetoes up, passes down) and the
integrity counter (L1 health). De-escalation needs **both** below threshold minus hysteresis. This is why
a silent gate plus a momentarily healthy L1 lets the car step down (G4).

### Invariant to respect

**SI-3:** L8 must not weight gates differently. G2's reaction therefore makes L6 **abstain** (same as
ADR-0016) instead of teaching L8 to distrust one gate.

---

## 12 · Literature: what is done and what is left

About **65–70 papers** reviewed; **~39** at full-text depth.

### Read closely (19)
CoCo; Lindemann et al.; Cleaveland 2023; Peper 2025; Mao 2025; Cleaveland 2025; ModelGuard; Luo et al.;
Henzinger & Saraç; Volkhonskiy et al.; Gibbs & Candès; Barber et al.; Lukina et al.; KS(conf);
NeuroStrata; Antonante et al.; Orf et al.; Kempa et al.; HALO. Details: `docs/NOVELTY_REVERIFICATION.md`
§5–§15 and `docs/MANUAL_NOVELTY_CHECK.md`.

### Targeted full-text (22)
The 20 in `docs/LESSONS_FROM_20_PAPERS.md`, plus Amoukou et al. and D3M (`docs/GAPS_CONFIRMED.md`).

### Still to read — please take these

| paper | why | access |
|---|---|---|
| **Ruchkin, Sokolsky, Weimer, Hedaoo & Lee**, *Compositional Probabilistic Analysis of Temporal Properties over Stochastic Detectors*, IEEE TCAD 2020 | Error rates of monitors — could narrow G2 | IEEE Xplore doc 9211465 (the UF author link returns a server error); or ResearchGate / email Ruchkin |
| **Arnez et al.**, *Skeptical Dynamic Dependability Management for Automated Systems*, IEEE DSD 2022 | Runtime dependability decisions with doubtful monitors — G2 and G4 | IEEE Xplore doc 9996730 |
| **Granig et al.**, *Weakness Monitors for Fail-Aware Systems*, FORMATS 2020 | A monitor reporting its own weakness | Springer chapter (the book front matter we have is not the chapter) |
| **G3 search** | Has anyone shown covariance-normalised monitors lose sensitivity under sensor loss in safety gates? Queries: `innovation normalized monitor covariance inflation sensitivity`; `Mahalanobis anomaly detector sensor dropout missed detection`; `uncertainty-aware safety filter conservative estimation` | Google Scholar, 2019+ |
| **Google Scholar "Cited by"** for CoCo, KS(conf), Antonante, Amoukou | Anything newer that closes G1/G2 | Search within citing articles for `safety monitor`, `sensor fault`, `runtime assurance` |
| For G4 later: arXiv 2608.07061, arXiv 2401.09678 | Recovery from minimal-risk condition | arXiv |

Record every paper in `docs/MANUAL_NOVELTY_CHECK.md` §5 with: read level, question, answer, page,
effect on claim. **Answer only from what the paper says; mark ambiguous as ambiguous.**

### Access tips
Most papers are on arXiv. For paywalled ones: Google Scholar → "All versions"; author homepage; college
library (IEEE Xplore, Springer); email the corresponding author. ACM is fully open access since January
2026, but only for ACM-published papers (DOI `10.1145`). No Sci-Hub.

---

## 13 · Collaboration and outreach

**Why industry cares:** ISO/PAS 8800:2024 (AI in road vehicles) and UL 4600 call for runtime monitoring
and diagnostic coverage. G1 shows such monitors can fail silently; G2 is field evidence that they still
work. Tool vendors themselves note teams cannot show whether runtime monitors are field-verified.

| who | what they would want | what we can realistically get |
|---|---|---|
| Ruchkin (UF), Carlone (MIT), Pavone group (Stanford) | A new result in their own line of work | Feedback, possible co-authorship |
| KPIT, Tata Elxsi, Bosch (India) | Standards-mapped evidence; an open tool | Data, internship, mentor — not funding |

**When:** after Stage A confirms G3 **and** an arXiv preprint exists. Not before.
**Pitch:** *"Your runtime monitor can go silent under persistent sensor faults — here is the data, and a
label-free check that it still works."*

---

## 14 · Housekeeping and open decisions

| item | status | needs |
|---|---|---|
| LICENSE, NOTICE, README, `docs/ASSUMPTIONS.md` A-7, ADR-0014, `conference.md`, `docs/ENGINEERING_HANDOFF.md`, `docs/COMMERCIAL_ASSESSMENT.md` still say "confidential / patent pending" | Stale since the rejection | Agreement of **all four authors and Dr. Chaitra R.** on a licence (MIT or Apache-2.0) before editing |
| Demo speed hack in `training/closed_loop.py` | Present | Flag, default off (Stage 0) |
| Docker images (`Dockerfile`, `Dockerfile.narrate`) | Built, never run (daemon was off) | A quick check on a machine with Docker |
| Target venue confirmation | IV (conditional) + ITSC | Agreement with the guide |
| Novelty percentages in docs | Judgments, not measurements | Keep them out of the paper |

---

## 15 · Your first-day checklist

- [ ] Update your copy (§1.1 or §1.2) and run the tests (§1.3)
- [ ] Run the sanity probe (§1.4) and confirm `speed_bias` stays NOMINAL
- [ ] Read §3–§5 and §7 of this file, then `docs/GAPS_CONFIRMED.md`
- [ ] Skim `docs/LITERATURE_SYNTHESIS.md` and `docs/LESSONS_FROM_20_PAPERS.md`
- [ ] Download Ruchkin TCAD 2020 and Arnez DSD 2022 from IEEE Xplore on the college network
- [ ] Start the G3 literature search (§12)
- [ ] Read the Stage A pre-registration when it lands and comment **before** anything runs
- [ ] Reply with any changes to the work split (§9)

---

## 16 · Where everything lives

| file | what it is |
|---|---|
| `TANAY_HANDOFF.md` (this file) | Start here |
| `research.md` | Step-by-step playbook to submission |
| `docs/GAPS_CONFIRMED.md` | The gap, evidence, what not to claim, G2 update |
| `docs/LITERATURE_SYNTHESIS.md` | Pattern across the papers, gap statements to cite |
| `docs/LESSONS_FROM_20_PAPERS.md` | What each of the 20 new papers teaches us |
| `docs/NEW_PAPERS_AND_GAPS.md` | The 20 papers + candidate gaps G3–G6 |
| `docs/NOVELTY_REVERIFICATION.md` | Paper-by-paper verification, §5–§15 |
| `docs/MANUAL_NOVELTY_CHECK.md` | Worksheet — record every paper here |
| `docs/NOVELTY_CLAIMS.md`, `docs/CLOSEST_WORK.md`, `docs/OBJECTIVES.md` | Earlier claim and objective drafts (13 Sept) |
| `docs/GAP_VERIFICATION.md` | The gap-verification brief you answered on 13 Sept |
| `experiments/phase5_od8_h7/` | Every experiment: pre-registration, raw, processed, decision |
| `experiments/phase5_od8_h7/CLAIM_LEDGER.md` | What we may and may not claim, with evidence |
| `experiments/phase5_od8_h7/EXPLORATORY_DEESCALATION/` | The 18 Sept mode-change probe |
| `benchmarks/e21_baseline.py` | Reusable sustained-fault injectors and runner |
| `src/astra/layers/l6_statistical_gate/gate.py` | The gate; score and evidence |
| `src/astra/layers/l8_failsafe/machine.py` | The failsafe modes |
| `DEPLOY.md` | Hosting the dashboard |

Questions: message me before changing anything in `src/` — architecture changes need an ADR.
