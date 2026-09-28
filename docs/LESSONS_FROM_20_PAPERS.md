# What the 20 new papers teach us (18 September 2026)

Nineteen PDFs read through **targeted full-text extraction** (abstract, method, assumptions, results,
limitations located and read; not every page), plus #15 via its journal page. List and IDs in
`NEW_PAPERS_AND_GAPS.md`. Note: #17's arXiv title is *Predictable by Design, Vulnerable by Nature:
Security Consequences of Learnability in UAV State Estimators* (framework REQUIEM).

## Verdict

**None closes G1 or G2.** Three narrow or sharpen them; several give ready-made tools, metrics and
citable limitations. One new must-read surfaced.

## Per paper — what to take away

| # | paper | key finding | lesson for ASTRA |
|---|---|---|---|
| 1 | **WATCH** (Prinster et al., weighted-conformal test martingales) | Online monitor that detects harmful shift, adapts to benign covariate shift, and **diagnoses the cause** (concept vs out-of-support shift). Explicitly treats **over-coverage (uninformative sets) as harmful** and bets on too-large p-values as well as too-small. **Needs labels Y_t online** | **Narrows G2 further:** detecting over-coverage with a conformal martingale exists — *with labels*. ASTRA's gate has no runtime labels, so WATCH cannot run as is. Use as a **label-oracle upper-bound baseline**. Its root-cause diagnosis idea (which shift?) is worth copying |
| 2 | **FAME** (Yang & Wang, IEEE Reliability Magazine) | STL monitors on perception outputs caught **29/31 silent failures (93.5 %)**, 0 false positives in 100 trials (95 % CI ≤ 3.6 %). Example: tracked pedestrian vanishes during glare. Single domain, one model (YOLOv4), one property family | Temporal-consistency rules catch silent DNN failures. **Good reporting template:** exact counts + Clopper–Pearson CI for zero-event rates. Monitors the DNN, not the monitor |
| 3 | **Unifying Evaluation of ML Safety Monitors** (Guerin et al.) | Three metrics: **Safety Gain**, **Residual Hazard**, **Availability Cost**; shows evaluation choices change a monitor's perceived quality | **Adopt these metrics** for G2's outcome experiment — they turn "does the blind flag help?" into three numbers a reviewer recognises |
| 4 | **Closing the Loop on Runtime Monitors with Fallback-Safe MPC** (Sinha, Schmerling & Pavone) | Conformal-calibrated monitor detects perception degradation beyond the MPC's tolerance; fallback plan kept feasible. **Adapts conformal to correlated observations within a trajectory** (standard exchangeable methods do not apply). Limitations: imperfect OOD heuristic fires on harmless shifts; **no switch back to nominal** | (i) Their trajectory-level calibration is the precedent for our **run-level calibration**. (ii) **Direct support for G4 (recovery):** a top group lists "switch back to nominal" as future work. (iii) Design G2's mitigation as a fallback that stays feasible |
| 5 | Runtime Safety Monitoring of DNNs for Perception: survey | Output-based monitors are limited because DNNs are **confidently wrong** in unfamiliar scenes; calls for combining monitoring strategies | Citable motivation for cross-layer (combined) monitoring |
| 6 | ARGUS | Runtime hazard monitor + mitigator for end-to-end driving stacks (TCP, UniAD, …) | Example of monitor-plus-takeover evaluation in CARLA-type setups |
| 7 | Detecting and Mitigating System-Level Anomalies of Vision-Based Controllers | Offline reachability mines system-level failures; classifier flags risky inputs online; fallback | Closed-loop failure mining — a way to generate faults the health monitor misses |
| 8 | Can We Detect Failures Without Failure Data? (TRI) | Failure detection trained only on successes | Our blindness monitor must also be calibrated without blindness examples — same setting |
| 9 | FIPER | OOD in embedding space + action-chunk uncertainty, conformal-calibrated on successful rollouts only; both indicators must agree | **Agreement of two indicators** to cut false alarms — relevant to G2's cross-layer rule |
| 10 | **ACoFi** (learned HJ safety filter + adaptive conformal) | Filter's switching threshold adapts via ACI; states that trajectory states/actions are **not exchangeable**; ACI needs the **true value observed with delay** | Confirms Gibbs & Candès lesson in a safety filter: ACI needs ground truth. ASTRA's gate lacks it |
| 11 | Output-feedback backup CBFs | Safety under estimation error **assuming a known bound** on it (Assumption 2) | Classic assumption ASTRA's faults violate: a dropout makes the error bound itself wrong |
| 12 | Conformal under Lévy–Prokhorov shifts | Robust conformal intervals if the shift size is **known in advance** | Robustness requires a shift budget — persistent sensor faults have none |
| 13 | Vision-based runtime monitoring, varying specs | One conformal calibration certifies a whole STL fragment | Tool for future semantic monitoring (G6) |
| 14 | Embedding Temporal Logic | Predicates as embedding distances, conformal-calibrated | Same — future G6 |
| 15 | **Quartararo & Langel 2022**, NAVIGATION (FIND) | Snapshot innovation tests miss slowly accumulating faults; banks of finite-window cumulative monitors catch them. **Undetected faults bias the estimate and the filter gradually adapts toward the faulty trajectory, reducing detection sensitivity** | **Supports H1-type estimator masking** from the navigation-integrity side: the estimator absorbs the fault. Cite in the mechanism section; the **bank-of-windows** design is a candidate for G2's statistic |
| 16 | Dual detection of faults vs integrity attacks | Two detectors (controller side and plant side) distinguish faults from attacks via closed-loop stealthiness conditions | Precedent for **two-sided placement** of detectors; useful for G5 |
| 17 | **REQUIEM** (UIUC/GWU/Boeing) | ML surrogate of the EKF lets a spoofer drive a UAV off-mission **while evading anomaly detectors** (incl. SAVIOR), real quadrotor + PX4 | **Adversarial version of G1:** detectors can be deliberately blinded. Strong motivation for G5 and for stating G2's attacker limit |
| 18 | Secure safety filter under sensor spoofing (Tan, Ong, Tabuada, Ames) | Secure state estimation + CBF; guarantee holds if the attacker controls **at most a bounded number of sensors** (sparse observability) | The formal limit to quote: beyond that bound no monitor can recover the state |
| 19 | Barrier-certificate control for LiDAR under faults/attacks | Cross-checks LiDAR scans against reconstructions from state estimates; drops inconsistent sectors | Cross-sensor consistency as defence — related to G2's cross-layer idea, at sensor level |
| 20 | STAnDS | Residual + time-based change detector for ToF sensor attacks, simulation only | Minor |

## Lessons that change what we do

1. **G2 must be label-free.** WATCH and ACoFi both detect coverage failure *with labels*. The defensible
   novelty of G2 is doing it **without ground truth**, from another layer's evidence. Say this explicitly.
2. **New must-read:** Amoukou, Bewley, Mishra, Lecue, Magazzeni & Veloso, *Sequential Harmful Shift
   Detection Without Labels*, NeurIPS 2024 (cited by WATCH). **This is the most likely paper to narrow
   label-free G2** — read before building.
3. **Mechanism (H1) has literature support:** Quartararo & Langel show filters adapt toward faults and lose
   sensitivity. Our experiment 2.6 tests whether the same happens through √P_f in the gate.
4. **Evaluation:** adopt Safety Gain / Residual Hazard / Availability Cost (Guerin et al.) and exact
   counts with Clopper–Pearson CIs (FAME).
5. **Calibration over trajectories:** Sinha et al. adapt conformal to within-trajectory correlation — cite
   as precedent for run-level calibration.
6. **Recovery (G4) is confirmed open by a top group:** Sinha et al. — no switch back to nominal.
7. **Adversarial (G5):** REQUIEM shows real detector evasion; Tan et al. give the formal sensor-budget
   limit. G2 should state: it detects blindness while at least one layer still sees the fault.
