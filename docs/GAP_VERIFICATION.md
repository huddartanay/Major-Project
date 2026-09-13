# Gap Verification

**Prepared 13 September 2026.** Every number below was read from a result file in this repository
while this document was written, not copied from another document. Each element names its source
file, the commit that recorded it, a way to reproduce it, and the result that would falsify it.

**How to use this.** A verifier — advisor, reviewer, co-author, or another model — should be able to
check each element independently and reach a verdict without trusting the author. If any element
fails, the gap statement in §1 must be narrowed or withdrawn; §5 says which.

---

## 1 · The gap

The gap has two halves, and they are verified separately because they fail differently.

### G-emp — what this stack does (empirical, verified internally)

> On a learned-controller runtime-assurance stack, a conformal monitor whose calibration is **valid**
> — and whose own score still **separates** faulted from clean runs — goes **quieter than its own
> healthy baseline** for as long as a sensor failure persists. Its apparent detection of that fault
> came from the **post-fault recovery transient**. Meanwhile the same fault is **detected within five
> ticks by a stream-health check two layers upstream**, at zero false positives. The evidence exists
> in the stack; the gate does not consult it.

### G-lit — what the literature has not shown (external, not yet fully verified)

> Closed-loop fault masking is known. What has not been shown, to the extent searched, is this
> conjunction on a **conformal runtime monitor of a learned controller**: alarm rate falling **below
> the monitor's clean baseline** under sustained fault, **while calibration remains valid**, and
> **while the fault is detectable elsewhere in the same stack.**

### In one sentence

**The layers disagree, and nothing in the architecture listens to the disagreement.** Runtime
assurance is evaluated on calibration and separability; neither guarantees detection, and the
failure is located in where the monitor sits and what it reads.

---

## 2 · The empirical elements

Scope throughout: **policy P1, `medium` severity, one synthetic plant, 30 seeds (`20260731 + i`),
frozen threshold 3.7024 (v3).** The unit of analysis is the run or the cell, never the tick.

### E1 — Calibration is valid

| | |
|---|---|
| Claim | On clean data at a 160 s window the monitor's false-alarm rate is inside its acceptance band on every run |
| Evidence | **30 / 30** P1 runs in band `[2.5 %, 10 %]` at n = 3,200. Per-run FAR median **5.84 %**, range **4.66 %–8.22 %** |
| Source | `experiments/phase5_od8_h7/E18_R3/raw_results/long_runs.json` (field `far_3200`) |
| Recorded | data commit `5142cc2`; decision `bd5f410` |
| Reproduce | `python -m benchmarks.e18r3_windows --out <scratch dir>` then `python -m benchmarks.e18r3_analyse` |
| Falsified if | fewer than 24 of 30 runs fall in band on a rerun |
| Why it matters | Without E1, the blind spot could be dismissed as a mis-set threshold. With it, the monitor is behaving *as specified* and still misses the fault |

### E2 — The evidence exists, and the monitor's own score still separates

| | |
|---|---|
| Claim | `imu_dropout` is near-perfectly separable at the sensor, and still separable at the monitor's score |
| Evidence | Discriminability `D_s` (AUC folded to [0.5, 1.0]; 0.5 = chance), P1, median of 30 seeds, BCa 95 % CI: **L1 0.998**, L2a 0.860, L2b 0.758, L3 0.860, **L6 0.737 [0.675, 0.777]**, L7 0.531, **L8 0.988** |
| Source | `results/E17_30SEED/tables/tableA_stage_profiles.md`, Policy P1 |
| Reproduce | `python -m benchmarks.e17_sweep` then `python -m benchmarks.e17_analyse` |
| Falsified if | the L6 confidence interval includes 0.5 |
| **Caveat** | E17 is a **400-tick transient** design (fault ticks 200–399). It establishes separability during the fault interval, not under sustained injection. It is supporting evidence for G-emp, not the sustained measurement itself |
| Note | L8 at 0.988 means the fail-safe *state* separates faulted from clean — another layer that sees the fault |

### E3 — The monitor goes silent, below its own baseline, while the fault persists

| | |
|---|---|
| Claim | Under sustained `imu_dropout` the monitor never detects the fault, and alarms less than on healthy runs |
| Evidence | Run-level detection **0 / 30 at every window** (200, 400, 800, 1,600, 3,200 ticks). Per-phase alarm rate: **0.38 %** (200–399), **0.18 %** (400–999), **0.20 %** (1,000–1,999), **0.21 %** (2,000–3,399), against a clean median of **5.84 %** (E1) |
| Source | `experiments/phase5_od8_h7/E18_R3c/raw_results/faulted_sustained.json` (`detected_*`); `E18_R3c/processed_results/phase_comparison.json` (`r3c_alarm`) |
| Recorded | runs at code state `87561cd`; decision `0bb5381`, ledger `1b09738` |
| Reproduce | `python -m benchmarks.e18r3c_sustained` then `python -m benchmarks.e18r3c_analyse --out <scratch dir>` |
| Falsified if | any post-onset phase alarm rate reaches the clean median, or run-level detection reaches 27 / 30 |

### E4 — The apparent detection was the recovery transient

| | |
|---|---|
| Claim | Earlier evidence of detection came from after the fault ended, not during it |
| Evidence | Same seeds, same threshold, same fault; the only difference is whether it ends. Alarm rate 400–999: **99.06 %** when the fault ends at 399 (R3b) against **0.18 %** when it never ends (R3c). 1,000–1,999: 69.15 % vs 0.20 %. 2,000–3,399: 59.58 % vs 0.21 %. Identical 200–399: 0.38 % vs 0.38 % |
| Source | `E18_R3c/processed_results/phase_comparison.json` (`r3b_alarm`, `r3c_alarm`) |
| Recorded | R3b `87561cd`; R3c `0bb5381` |
| Falsified if | R3c's post-onset alarm rates approach R3b's |
| **Caveat** | R3b's `position_drift` arm was inflated by a drift-scaling defect (~32 m instead of 2 m). **`imu_dropout` is unaffected** — dropout has no magnitude parameter. The defect is fixed at `0a3ea56` |

### E5 — The fault was detectable, cheaply, upstream

| | |
|---|---|
| Claim | A trivial detector reading L1 catches what the conformal gate misses, without false alarms |
| Evidence | `health` detector: `imu_dropout` **30 / 30**, clean false positives **0 / 30**, median latency **5 ticks** (0.25 s). Conformal gate: **0 / 30**. Also: `position_bias` 30/30 at 13 ticks; `position_drift` 30/30 at 1,082.5 ticks |
| Source | `experiments/phase5_od8_h7/E21_BASELINE_COMPARISON/processed_results/summary.json`; raw `raw_results/detections.json` |
| Recorded | pre-registration `ae997b3` (before any run); runner `edd7acd`; decision `4615cdc` |
| Reproduce | `python -m benchmarks.e21_baseline` (~90 min) |
| Falsified if | `health` clean FP exceeds 0.10, or its `imu_dropout` detection falls below 0.90 |
| **Caveat — read before quoting** | Detecting a dropout by stream health is **near-definitional**. The claim is not that the baseline is clever; it is that a trivially available signal never reaches the gate. The **position faults are the non-trivial part**: they do not set a health flag directly, and are caught because the redundancy cross-check sees two of three channels disagree |
| Also measured | `trust` fires on **23 / 30 clean** runs — unusable. `innovation` detects **0.00 on five of six faults**. `speed_bias` and `speed_stuck` are detected by **no** monitor tested |

### E6 — Separability does not predict detection

| | |
|---|---|
| Claim | Offline discriminability is not a usable proxy for operational detection |
| Evidence | Sensor-level `D_L1` vs detection: **ρ = −0.480, p = 0.0088, n = 28 cells** (E18, 400-tick design) — negative. Per-fault `D_s` vs phase-resolved alarm rate: **ρ = 0.077, p = 0.7192, n = 24 cells** (Phase 2, sustained) |
| Source | `experiments/phase5_od8_h7/E18_OD8_CALIBRATION/final_decision.md`; `PHASE2_MONITORABILITY/processed_results/monitorability.json` (`incumbent_d_s`) |
| Recorded | Phase 2 pre-registration `db090f2`, result `236330e` |
| Falsified if | a rerun with confidence intervals gives a significant positive correlation |
| **Open** | Cells are **not independent** (shared seeds; four phases per fault). No confidence interval or per-fault breakdown has been computed for ρ = −0.480. **This element is the weakest and must be strengthened before submission** |

### E7 — Mechanism (supporting, not load-bearing)

| | |
|---|---|
| Claim | Separation without exceedance arises because the fault tightens the score rather than shifting it |
| Evidence | Under sustained `imu_dropout` the L6 score median sits **above** the clean mean (M ≈ 0.93 between-run SDs), yet the alarm rate is ~25× **below** clean. A location shift toward the threshold paired with narrower spread produces fewer exceedances |
| Source | `PHASE2_MONITORABILITY/processed_results/monitorability.json` |
| Status | Consistent with E2 and E3. A 3-seed pilot suggested the twin's prediction barely moves under this fault; **that pilot is unregistered and is not evidence** |

---

## 3 · What the gap does not claim

A verifier should treat any of these appearing in a manuscript as an overclaim.

- **Not** that conformal prediction is flawed as a method. One conformal monitor, as configured here.
- **Not** that closed-loop fault masking is newly discovered. It is known — see §4.
- **Not** a general property of runtime assurance. One plant, one policy, one severity.
- **Not** that the `health` detector is sufficient. It misses `lateral_noise` entirely (the gate
  catches it at 1.00) and takes 54 s on `position_drift`.
- **Not** that the architecture (Simplex + conformal gate + twin) is novel. It is not — see §4.
- **Not** resilience to adversarial sensors, semantic errors, or recovery to a better state. None is
  built.
- **Not** external validity. `[M-ext]` is **0 of 30**.

---

## 4 · The literature half (G-lit)

### Verified — these exist and must be cited

Each was opened and checked on 13 September 2026.

| work | what it establishes | what it does not do |
|---|---|---|
| Gómez-González, Fischer et al., *Anomaly Detection Under Closed-Loop Fault Masking: A Case Study … Two-Tank Level Control System*, SOCO 2026 (Springer, doi 10.1007/978-3-032-29254-4_6) | **Closed-loop fault masking of data-driven detectors is a recognised problem**, on a real plant (SVDD, autoencoder, MLP; adaptive PID/RLS) | Abstract does not report alarm rates **below** baseline; no conformal monitor; no learned controller. **Full text not read — paywalled** |
| Phan, Grosu, Jansen, Paoletti, Smolka, Stoller, *Neural Simplex Architecture*, NFM 2020 (arXiv 1908.00528) | Simplex-style runtime assurance over neural controllers | No conformal gate, no twin, no sensor faults |
| Strawn, Ayanian, Lindemann, *Conformal Predictive Safety Filter for RL Controllers in Dynamic Environments*, IEEE RA-L 2023 (arXiv 2306.02551) | Conformal prediction as a safety filter over RL | Guarantees coverage of **trajectory-prediction** uncertainty; **no sensor faults, no detection rates** |
| Rashidi, *Benchmark AUC Is Not Deployable Reliability*, arXiv 2606.29506 (2026) | AUC does not predict deployed reliability | **Cross-dataset** shift in video; no runtime monitor, no closed loop, no faults |

**Consequence for the claim:** masking cannot be presented as a finding, the architecture cannot be
presented as a contribution, and "AUC isn't deployment" is a commonplace. What the verified papers do
*not* contain is the G-lit conjunction.

### Cited by the 11 September review — not yet verified

These must be opened and checked before they are cited or relied upon.

- Fawzi, Tabuada, Diggavi, secure estimation under adversarial attack, IEEE TAC 2014
- Pasqualetti, Dörfler, Bullo, undetectable attacks in cyber-physical systems
- Mo & Sinopoli, replay attacks
- Gibbs & Candès, adaptive conformal inference (arXiv 2106.00170)
- Barber, Candès, Ramdas, Tibshirani, conformal prediction beyond exchangeability, *Annals of Statistics* 2023
- *Unifying Evaluation of Machine Learning Safety Monitors*, arXiv 2208.14660
- Tatbul et al., range-based precision and recall; TaPR (CIKM 2019)

### Searches still required to close G-lit

Run each in control-theory **and** machine-learning vocabulary. Record the queries.

1. **Read the full text of the SOCO 2026 paper.** It is the single most likely place for the
   below-baseline effect to already appear. Obtain through institutional access or by writing to the
   authors. *G-lit cannot be declared verified until this is done.*
2. Papers citing the SOCO 2026 paper, and the classical works it builds on.
3. `conformal` + `sensor fault` + `missed detection` / `false negative` / `detection rate` — does any
   conformal runtime monitor report missed-detection behaviour under sustained faults?
4. `alarm rate below baseline` / `alarm suppression` / `quieter than nominal` + `fault` + `monitor`.
5. `runtime monitor` + `learned controller` + `sustained fault` / `persistent fault`.
6. Whether arXiv 2208.14660's evaluation framework measures missed detection under closed-loop
   compensation.
7. Adaptive and weighted conformal papers — do any evaluate on sensor-fault injection?
8. `cross-layer` / `inconsistency between monitors` / `monitor disagreement as a fault signal` —
   the architectural half of the gap.

---

## 5 · Falsification summary

| if this happens | then |
|---|---|
| E1 fails (calibration invalid on rerun) | The blind spot may be a threshold artefact. **Withdraw G-emp**; revert to the E18 calibration story |
| E2's L6 CI includes 0.5 | Drop "the monitor's own score separates"; G-emp survives in narrower form |
| E3 fails (alarm ≥ baseline, or detection ≥ 27/30) | **Withdraw G-emp entirely** — there is no blind spot |
| E4 fails | Drop the aftermath clause; the silence claim may still stand |
| E5 fails (`health` false-alarms or misses) | Drop "detectable upstream"; the gap reverts from architectural to statistical |
| E6 fails with CIs | Drop the discriminability clause; G-emp survives without it |
| SOCO 2026 full text reports below-baseline alarms | **G-lit collapses to a replication.** Reframe as extending a known result to conformal monitors of learned controllers |
| Any paper reports the full conjunction | **G-lit is dead.** The paper becomes a replication plus the architectural diagnosis |

---

## 6 · Reproducing without disturbing the record

The analysis scripts write into `experiments/` and `results/`. **Run reproductions in a separate
worktree** so recorded results are never overwritten:

```bash
git worktree add ../astra-verify 4615cdc
cd ../astra-verify
python -m benchmarks.e21_baseline
git diff --stat
```

Compare the regenerated files against the committed ones. A run that reproduces should change only
timestamps and commit fields.

---

## 7 · Status

| half | status |
|---|---|
| **G-emp** | **Verified internally.** E1, E3, E4, E5 are pre-registered or duration-controlled, 30 seeds, frozen threshold, and reproducible from committed code. E2 is supporting and from a different design. **E6 is the weak element** and needs confidence intervals |
| **G-lit** | **Partially verified.** Four works checked, none contains the conjunction. **Not verified until the SOCO 2026 full text is read** and the §4 searches are run |
| External validity | **Absent.** One synthetic plant. This does not affect whether the gap exists on this stack; it limits what can be claimed beyond it |

### Open before submission

1. Read the SOCO 2026 full text.
2. Run and log the §4 searches.
3. Confidence intervals and per-fault breakdown for E6.
4. Adaptive conformal comparison — does ACI also miss sustained `imu_dropout`? If yes, strong evidence
   the failure is architectural rather than a calibration choice.
5. External replication (comma2k19 replay).

---

## 8 · Corrections recorded while preparing this document

- **The 0.998 is at L1, not L6.** Earlier summaries described the monitor as separating faulted from
  clean at AUC ≈ 0.998. That figure is sensor-level discriminability. The monitor's own score is
  **0.737 [0.675, 0.777]** on P1. The gap survives the correction — a monitor whose score still
  separates, yet never alarms, is the sharper statement — but 0.998 must not be quoted for L6.
- **The clean baseline is 5.84 % (median), not "~5 %".** Range 4.66–8.22 %.
- **The conformal safety filter** attributed to "Lindemann et al." is Strawn, Ayanian and Lindemann,
  RA-L 2023.
- The 11 September review's recommended root cause, "calibration-provenance failure", is
  **contradicted by E1**: the blind spot occurs with valid calibration. It explains the earlier OD-8
  false-alarm problem, not this gap.
