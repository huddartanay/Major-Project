# Manual novelty check — worksheet

**For a person to work through by hand.** The novelty estimates in `NOVELTY_REVERIFICATION.md` were
built mostly from automated extraction of web pages and some abstracts. This sheet tells you exactly
what to open, where to look, what yes/no question to answer, and what each answer does to the claims.

Work top to bottom — items are ordered by how much they can change the verdict. Record answers in the
table in §5.

---

## 0 · Before you start

**Access.** Use the BMSCE library for IEEE Xplore, ACM Digital Library and Springer. Most items below also
have a free arXiv version — use it where given.

**Tools.**
- **Google Scholar** — search the title, click **Cited by**, then tick **Search within citing articles**.
- **Semantic Scholar** — same, with better filtering by year.
- **Connected Papers** (connectedpapers.com) — paste a title to see nearby work you might not find by
  keyword.

**Rule while reading.** Answer only from what the paper says. If it is ambiguous, mark it ambiguous —
do not resolve it in ASTRA's favour.

**Known weak spots in the automated reading** (check these especially):
- Zhao et al.: "no guarantee on detection power" is **my reading** of the guarantee's form, not a
  sentence in the paper.
- CoCo, HALO, DeLorean, Orf et al.: read through automated HTML extraction, not by a person.
- Antonante et al., Boursinos & Koutsoukos, Tsai & Hariri's scope, Rober et al.: abstract level only.
- Both closed-loop masking papers: abstract only.

---

## 1 · Decisive — can change the core finding

### 1.1 CoCo — the biggest threat

**Ruchkin, Cleaveland, Ivanov, Lu, Carpenter, Sokolsky & Lee, *Confidence Composition for Monitors of
Verification Assumptions*, ICCPS 2022** — https://arxiv.org/abs/2111.03782

| look at | question | if YES | if NO |
|---|---|---|---|
| §4.2 (assumptions) | Is any monitored assumption about **sensor observations / state estimation** being correct? | N1 must cite CoCo as monitoring observation assumptions (already planned) | N1 strengthens |
| §5 case studies | Does any case study inject a **sensor fault** (dropout, bias, stuck value) during operation? | Read how the composed confidence responds — go to next row | CoCo does not test the regime ASTRA measures; core finding strengthens |
| §5 results | When that fault occurs, does CoCo's confidence **drop** — i.e. would it have flagged that the safety guarantee no longer holds? | **Core finding narrows sharply**: an assumption monitor catches the case. ASTRA's distinction must move to faults assumption monitors *miss* (speed faults) | Core finding holds for that fault |
| §4.3 / discussion | Does it consider a monitor becoming **uninformative** — alive but unable to detect? | **B1 (Paper 2) threatened directly** | B1's distinction holds |

### 1.2 Papers citing CoCo — the most likely place the gap was closed since 2022

Google Scholar → CoCo → **Cited by** → **Search within citing articles**, one search at a time:

`sensor fault` · `monitor failure` · `detection capability` · `blind` · `silent` ·
`runtime assurance` · `observation model` · `conformal`

| for each hit, ask | if YES |
|---|---|
| Does it detect at runtime that a **safety monitor or gate can no longer detect** faults (not just that it is offline or unconfident)? | **Core finding and B1 at risk.** Record the paper; this is the paper to position against |
| Does it evaluate assumption monitors under **persistent sensor faults** in closed loop? | N1 and N3 narrow |

**Expected effort:** 2–4 hours. **This item alone decides most of the novelty estimate.**

### 1.3 Synergistic Simplex — Assumption 8

**Bansal, Yeghiazaryan, Khachatryan, Zhu, Kim, Hovakimyan & Sha, arXiv 2605.08190 (2026)** —
https://arxiv.org/abs/2605.08190

| look at | question |
|---|---|
| Assumptions list | Does **Assumption 8** state that sensors operate nominally and sensor failure is out of scope? Record the page number |
| Anywhere | Does it cite a specific method it relies on for sensor failures? If so, open that paper — it may close N1 |

---

## 2 · Important — can narrow individual claims

### 2.1 PID-Piper — §II-E threat model (N3)

**Dash, Li, Chen, Karimibiuki & Pattabiraman, DSN 2021** —
https://people.ece.ubc.ca/zitaoc/files/Pid-Piper-DSN21.pdf

- §II-E: confirm it **excludes attacks causing persistent drastic sensor manipulation** and **attacks on
  all sensors simultaneously**. Record the exact page.
- §IV-B: confirm the feed-forward controller takes current state and sensor-derived features as input.

### 2.2 DeLorean — duration and detector (N3)

**Dash, Li, Karimibiuki & Pattabiraman, ASIA CCS 2024** — https://arxiv.org/abs/2209.04554

| look at | question | if YES |
|---|---|---|
| §2.3 threat model | Does it say anything about **attack duration**? | Record it |
| §6 evaluation | Does any attack **persist for the rest of the mission**? | **N3 narrows** — "not evaluated" becomes false |
| §5.4 | Does it rely on PID-Piper's detector without measuring its misses? | Supports L2 |

Then: **papers citing DeLorean** — search within citing articles for `persistent`, `long-duration`,
`entire mission`, `continuous attack`.

### 2.3 Closed-loop fault masking — full texts (N4)

- **Gómez-González, Fischer et al.**, *Anomaly Detection Under Closed-Loop Fault Masking … Two-Tank*,
  Springer, doi 10.1007/978-3-032-29254-4_6 — **needs library access or an email to the authors**.
- **Zhang, Yang, Dandago & Li**, *The negative impact of closed-loop control on fault detection*,
  Springer 2026 — https://research.manchester.ac.uk/en/publications/the-negative-impact-of-closed-loop-control-on-fault-detection/

| question | if YES |
|---|---|
| Does either report a detector's alarm rate falling **below its healthy / fault-free rate** during a fault? | **N4 becomes a replication** — reframe as extending a known result |
| Does either use a **learned (RL / neural) controller**? | **N4 dies** |
| Confirm the Gómez-González venue and year (SOCO 2025 or 2026?) | Fix the citation |

### 2.4 Conformal assurance monitors (N2)

- **Boursinos & Koutsoukos**, arXiv 2001.05014 and arXiv 2110.03120 (AI EDAM 2021).
- ***Fault-Adaptive Autonomy in Systems with Learning-Enabled Components***, Sensors 21(18):6089, 2021 —
  https://pmc.ncbi.nlm.nih.gov/articles/PMC8470782/

| question | if YES |
|---|---|
| Is a conformal monitor evaluated for **missed detections / false negatives** under faults? | N2 narrows |
| Are **sensor** faults (not only thruster/actuator degradation) injected? | N2 narrows |
| Is the monitored system closed-loop, with faults persisting? | N2 narrows further |

### 2.5 Cross-layer monitors (N5)

- **Orf et al.**, *Modular Fault Diagnosis Framework for Complex Autonomous Driving Systems*, arXiv 2411.09643 —
  https://arxiv.org/abs/2411.09643
- **Antonante, Nilsen & Carlone**, *Monitoring of Perception Systems*, arXiv 2205.10906 —
  https://arxiv.org/abs/2205.10906
- **Harder, Kulkarni & Behl**, *HALO*, arXiv 2503.10341 — https://arxiv.org/abs/2503.10341

| paper | question | if YES |
|---|---|---|
| Orf et al. §IV–VI | Is **disagreement** between modules used as fault evidence (not only dependency propagation)? Any quantitative results? | N5 narrows or dies |
| Antonante et al. | Do the diagnostic graphs include **localization / state estimation**? Any closed-loop evaluation? | N5 narrows |
| HALO §10 | Any mechanism acting on disagreement between data-health and behavioural monitors? Confirm §10.2 heartbeat watchdog | N5 narrows |

### 2.6 Integrity used in decisions (N1)

- **Lee, Seo & Kassas**, *Integrity-Based Path Planning Strategy…*, ION GNSS+ 2020 —
  https://ece.osu.edu/sites/default/files/2022-09/Integrity_Based_Path_Planning_Strategy_for_Urban_Autonomous_Vehicular_Navigation_Using_GPS_and_Cellular_Signals.pdf
- **Nayak & Barth**, arXiv 2502.04874 — follow its references for any work using **protection levels
  inside a controller, safety filter or runtime monitor** online.

| question | if YES |
|---|---|
| Does any work consume protection levels **online** in a safety gate or controller of an autonomous vehicle? | **N1 narrows sharply** |

---

## 3 · Confirmatory — quick checks of statements already relied on

| paper | check |
|---|---|
| **Rober, Jia & How**, arXiv 2608.20467 | Abstract says most safety filters assume perfect state information — confirm wording |
| **Zhao, Hoxha, Fainekos, Deshmukh & Lindemann**, arXiv 2311.09482 | Assumptions: known f-divergence bound, calibration from training distribution. Does it say anything about detection power? (My reading, not a quote) |
| **Strawn, Ayanian & Lindemann**, RA-L 2023, arXiv 2306.02551 | Guarantee is coverage of trajectory prediction; no sensor faults |
| **Tsai & Hariri**, arXiv 2606.06996 | Table II varies duration; faults are mission-command, not sensor |
| **Yang, Chen, Chen & Su**, Sensors 2021 | Introspection predicts object-detector false negatives; camera only |
| **Zudaire et al.**, ICRA 2021 | Assumption monitoring for task plans; "silent mission failure" term |
| **Aslam et al.**, arXiv 2604.27728 | Two monitors, sequential, qualitative evaluation only |
| **Martinez Gil et al.**, arXiv 2604.20122 | False-alarm control only; no closed loop or sensor faults |
| **Volkhonskiy et al.**, arXiv 1706.03415 | Conformal martingales for change-point detection |
| **Or**, arXiv 2606.00090 | §9.5 open questions include evaluating silent failures beyond task completion |

---

## 4 · Independent searches — to catch what I missed

Run each in **Google Scholar** and **Semantic Scholar**, filter **2022 onward**, and scan the first two
pages. The same idea goes by different names in control theory and in machine learning, so run both
columns.

| control / dependability vocabulary | machine-learning vocabulary |
|---|---|
| `runtime assurance monitor detectability loss` | `safety monitor failure detection at runtime` |
| `fault detection capability degradation online` | `monitor blind spot runtime` |
| `monitor of monitors cyber-physical` | `meta-monitoring learning-enabled` |
| `closed-loop fault masking neural controller` | `anomaly detector silent failure closed loop` |
| `integrity monitoring safety filter` | `conformal monitor missed detection sensor fault` |
| `persistent sensor fault runtime assurance` | `OOD detector fails under sensor degradation` |
| `watchdog monitor detection coverage` | `assumption monitoring neural network controller sensor fault` |

For any hit that looks close: read the abstract, then ask the §1.1 question — *does it detect that a
monitor can no longer detect?*

---

## 5 · Record

Copy this table and fill one row per paper checked.

| # | paper | read level (PDF / abstract) | question | answer (yes / no / ambiguous) | page / section | effect on claim |
|---|---|---|---|---|---|---|
| 0 | CoCo | PDF (all 13 pp.) | observation assumptions monitored? | **yes** — observation models capturing sensor uncertainty; noise-parameter bounds | §4.2, pp. 4–5; §5.1–5.2 | N1 must cite CoCo |
| 1 | CoCo | PDF | sensor fault injected? | **no** — steeper hill (dynamics), initial states outside verified set, stuck fin (actuator, UUV) | §5.1–5.2, pp. 8–9 | Core finding strengthens: CoCo not tested in this regime |
| 2 | CoCo | PDF | confidence drops on it? | **n/a** — no sensor fault; results are episode-aggregate calibration and AUC only | Tables 1–2, p. 8 | — |
| 3 | CoCo | PDF | uninformative monitor considered? | **no** — assumes monitors carry the relevant information (§4.4) and are "well-calibrated and accurate" (§6); lists monitoring the assumptions of other monitors as **future work** citing Henzinger & Saraç 2020 | §4.4 p. 5; §6 pp. 9–10 | B1 distinction holds; new lead added |
| 3a | Henzinger & Saraç, *Monitorability Under Assumptions*, RV 2020 | | does it detect that a monitor cannot detect? | *to check* | | Could close B1 |
| 3b | Carpenter et al., *ModelGuard*, ADHS 2021 | | would model invalidation flag sensor dropout / bias? | *to check* | | Must be a baseline in experiment 2.4 |
| 4 | CoCo citing papers | Semantic Scholar list (16) | gate blindness detected? | *in progress* — 16 listed 15 Sept; Google Scholar "Cited by" still to cross-check | — | — |
| 4a | Lindemann, Qin, Deshmukh & Pappas, *Conformal Prediction for STL Runtime Verification*, arXiv 2211.01539v2 (Allerton per Semantic Scholar; venue to confirm) | PDF (all 24 pp.) | observation assumptions monitored? | **no** — assumes calibration and test trajectories are i.i.d. draws from one distribution; nothing checks this at runtime | Assumption 1 p. 4; Remark 2 p. 8 | Core finding strengthens |
| 4b | Lindemann et al. | PDF | sensor fault injected? | **no** — observed prefix treated as the true state; randomness is initial conditions (F-16) and Gaussian control noise (CARLA) | §2.3 p. 6; §4.1 p. 11; §4.2 p. 13 | Not tested in ASTRA's regime |
| 4c | Lindemann et al. | PDF | per-tick detection reported? | **no** — one fixed evaluation time per case study; results are counts over 100 test trajectories (e.g. 96/100, 99/100) | §4.1 pp. 11–12; §4.2 p. 15 | — |
| 4d | Lindemann et al. | PDF | uninformative monitor considered? | **no** — guarantee is marginal over the calibration distribution; a faulted trajectory falls outside it and the guarantee silently lapses, unaddressed | Remark 2 p. 8; §5 p. 16 | B1 distinction holds; the lapse is the gap stated in their own terms |
| 4e | Luo, Zhao, Kuck, Ivanovic, Savarese, Schmerling & Pavone, *Sample-Efficient Safety Assurances using Conformal Prediction*, arXiv 2109.14082 | | does it bound a monitor's **miss rate** at runtime, and under sensor faults? | *to check* — cited by Lindemann as conformal guarantees on an online monitor's false-negative rate | | **Could narrow B1's provable half** — must read |
| 4f | Cairoli, Bortolussi & Paoletti, *Neural Predictive Monitoring under Partial Observability*, RV 2021 | | are noisy / corrupted observations part of the guarantee? | *to check* | | Could narrow the core finding for sensor noise |
| 4g | Lukina, Schilling & Henzinger, *Into the Unknown: Active Monitoring of Neural Networks*, RV 2021 | | does the monitor detect its own loss of detection power? | *to check* | | Could narrow B1 |
| 4h | Cleaveland, Sokolsky, Lee & Ruchkin, *Conservative Safety Monitors of Stochastic Dynamical Systems*, arXiv 2301.11330v2 (NFM 2023 per Semantic Scholar; venue to confirm) | PDF (all 17 pp.) | observation assumptions monitored? | **no** — the conservatism theorem *assumes* a well-calibrated state estimator; calibration is checked once, offline (ECE 0.00656), never at runtime | Theorem 1 p. 10; §7.2 p. 15 | Core finding strengthens; A1 gains a theorem-level citation |
| 4i | Cleaveland et al. | PDF | sensor fault injected? | **ambiguous (partial)** — water-tank sensors have Gaussian noise and, with constant probability each step, read 0 or full scale. This is transient, i.i.d. and folded into the design-time perception model — in-distribution, not a persistent fault | §7.1 p. 11; §5.1 p. 7 | Must cite as handling *modelled* spurious readings; ASTRA's distinction is persistence and being outside the calibrated model |
| 4j | Cleaveland et al. | PDF | per-tick detection reported? | **no** — per-step safety estimates plotted for two trials only; results pooled into calibration bins, ECE/Brier and ROC-AUC over 500 trials | Fig. 2 p. 13; Table 1 p. 15 | — |
| 4k | Cleaveland et al. | PDF | uninformative monitor considered? | **no** — admits perception/state-estimation conservatism cannot be proved and lists conservative perception abstractions as future work; nothing signals when the calibration assumption stops holding | §6 pp. 9–10; §8 p. 15 | B1 distinction holds |
| 4l | Granig, Jakšić, Lewitschnig, Mateis & Ničković, *Weakness Monitors for Fail-Aware Systems*, FORMATS 2020 | | does a monitor report its own weakness / loss of detection? | *to check* — found in Cleaveland et al.'s references | | Could narrow B1 |
| 4m | CoCo citing papers — triage by abstract (15 Sept) | abstract | overlap with gate blindness? | **15 unique** (Semantic Scholar lists arXiv 2503.18077 twice). **Read in full, no overlap (2):** Lindemann et al.; Cleaveland et al. 2023. **Cleared at abstract level (8):** Lu et al. ×3 (controller repair); Geng et al. (reachability for high-dimensional controllers); Mao et al. 2024 (physically interpretable world models); Mao et al. 2024 (CLIP-based OOD detection on camera inputs); Mao et al. 2023 (conformal safety-chance prediction, prediction-induced shift only); Silva et al. 2022 (systematic review — abstract lists no monitor-blindness theme). **Skipped (1):** Ruchkin research statement (not peer-reviewed). **Still to read (4):** Arnez et al. 2022; Peper et al. 2025; Cleaveland et al. 2025; Mao et al. 2025 | abstracts via Semantic Scholar | Abstract-level clearance is not proof; re-open any if a later paper points back to it |
| 4n | Peper, Miao, Mitra & Ruchkin, *Towards Unified Probabilistic Verification and Validation of Vision-Based Autonomy*, ATVA 2025, arXiv 2508.14181v1 | PDF (all 31 pp.) | does the guarantee **detect or adapt** when test-time conditions leave the calibrated distribution? | **yes, but offline and with ground truth** — a Bayesian check of whether new-environment data still fits the perception model degrades the guarantee (confidence γ). Needs **state/estimate pairs** (true state alongside estimate) from **1000 i.i.d. trajectories** of the new environment; stated as design-time validation | Problem 3 p. 5; §4.3 p. 11; Alg. 3 p. 13; Thm 2 p. 14 | **Closest analogue found so far** — must be cited and positioned against |
| 4n-i | Peper et al. | PDF | sensor fault injected? | **yes, as a whole-environment shift** — state-estimate noise biased by a scalar offset (synthetic waypoint task). Shifts ≥ 2.45 give confidence 0.0000 vs 0.65–0.78 in-distribution; **shifts 0–2.45 excluded as inconclusive**. Mountain car: Gaussian image noise, in-distribution tradeoff only | §5.1 p. 17; Table 2 p. 18; §5.2 pp. 18–19 | N3 wording: persistent bias *as a separate deployment environment* is studied offline; ASTRA's regime is **onset within a run, detected online without ground truth** |
| 4n-ii | Peper et al. | PDF | per-tick detection reported? | **no** — one confidence per environment dataset | Table 2 p. 18 | — |
| 4n-iii | Peper et al. | PDF | uninformative monitor considered? | **no** — validates the perception *model*, not a runtime monitor's detection capability. States that a fundamental gap remains between assume-guarantee verification and the validity of its assumptions once deployed, and that no prior perception-contract approach has been investigated under visual distribution change | §1 p. 2; §2 p. 4 | B1 distinction holds; both statements usable as gap citations |
| 4n-iv | leads from Peper et al. | | | *to check* — Ruchkin, Sokolsky, Weimer, Hedaoo & Lee, *Compositional Probabilistic Analysis of Temporal Properties over Stochastic Detectors*, IEEE TCAD 2020 (cited for **runtime confidence monitoring of model validity**; IEEE — Xplore); Waite, Geng, Turnquist, Ruchkin & Ivanov, *State-Dependent Conformal Perception Bounds*, arXiv 2502.21308; Dutta et al., *Distributionally Robust Statistical Verification with Imprecise Neural Networks*, HSCC 2025 | ref. [77], [91], [29] | TCAD 2020 could narrow B1 |
| 4o | Cleaveland et al., *Conservative Perception Models for Probabilistic Verification*, arXiv 2503.18077 (2025) | | are the conservative perception models checked at runtime, or under sensor faults? | *to check* — abstract: provably conservative IMDP perception models with user-specified probability; offline; YOLO11 in CARLA | | Answers 4k's future work; likely offline only |
| 4p | Mao, Umasudhan & Ruchkin, *How Safe Will I Be Given What I Saw? Calibrated Safety Prediction for Image-Controlled Autonomy*, arXiv 2508.09346v3 (journal extension of the L4DC 2023 paper) | PDF (pp. 1–25 read; references skimmed) | is miscalibration under shift **detected** at runtime, and is shift caused by sensor faults? | **no** — test-time adaptation (MEMO entropy minimisation) is applied to every sample; no detection step is specified in the method, although the introduction describes the module as detecting shifts (**ambiguous**). Shift is prediction-induced (decoder artifacts) plus a manually labelled 500-image OOD subset; sensor noise named as a possible source but **not injected** | §1 p. 3; §4.3 pp. 13–15; Tables 3–4 pp. 22–23 | Core finding strengthens |
| 4p-i | Mao et al. 2025 | PDF | observation / calibration assumptions monitored? | **no** — calibration and test samples deliberately drawn from independent trajectories to satisfy exchangeability; for trajectory-level OOD the paper **asserts** the predicted chance will show higher uncertainty and wider intervals that alert the controller — **not evaluated** | §3.2 p. 10; §4.3 p. 15; Thm 1 p. 17 | **Usable citation of the assumption ASTRA tests:** that a monitor's uncertainty rises when its inputs go out of distribution |
| 4p-ii | Mao et al. 2025 | PDF | per-tick detection reported? | **no** — pooled F1, FPR, ECE, Brier and conformal coverage per test set | Tables 1–4; Fig. 6 p. 24 | — |
| 4p-iii | Mao et al. 2025 | PDF | uninformative monitor considered? | **no** — limitations cover unobservable safety, labelling cost, simple predicates | §6 pp. 24–25 | B1 distinction holds |
| … | | | | | | |

---

## 6 · How to turn answers into a verdict

| finding | effect |
|---|---|
| Any paper detects at runtime that a safety monitor **can no longer detect** faults | **Core finding and B1 at risk** — reposition against that paper before anything else |
| CoCo-style confidence drops for sensor faults like `imu_dropout` | Core finding narrows to faults assumption monitors miss (e.g. speed faults); the planned monitor-comparison experiment becomes essential |
| A masking paper reports **below-baseline** alarms | N4 becomes "extends a known result" |
| A detect-and-recover paper evaluates **whole-mission** persistent faults | N3 narrows |
| Nothing found on §1.1 or §1.2 after the searches | Core finding's estimate rises — record the searches run as evidence |

**Bring the filled table back** and the claims, estimates and objectives can be updated from your
reading rather than the automated one.
