# Gaps in the existing literature — and the direction for ASTRA

> **Superseded in part by `docs/CLOSEST_WORK.md`.** A later adversarial pass searched for the papers
> closest to closing each gap. **No gap was closed, but L1 and L4 were narrowed** — navigation
> integrity monitoring already detects a wrong estimate held with false confidence, and runtime
> failure prediction exists for perception components. **Quote the restated gaps in
> `CLOSEST_WORK.md` §3, not the statements below.**

**Compiled 13 September 2026.** This document is about limitations of **other people's published
work** that ASTRA can contribute to. It is not a list of ASTRA's own limitations
(see `GAP_VERIFICATION.md` and `OBJECTIVES.md` for those).

## How to read the evidence

Every gap is supported by what the cited papers **say about themselves** — their stated assumptions,
out-of-scope declarations, or open-challenges sections — wherever possible, because a gap a paper
admits is far stronger than one inferred from outside.

Evidence levels:

| tag | meaning |
|---|---|
| `FULL-TEXT` | the paper's HTML full text was opened and the relevant section located |
| `ABSTRACT` | only the abstract or landing page was read |
| `SEARCH` | seen only in a search result; **not to be relied on** |

**Caveat that applies to every entry.** Full text was read through automated page extraction, not by a
person with the PDF. Paraphrases below are faithful to what was extracted, but **every assumption or
quotation must be confirmed in the PDF before it goes into a manuscript.** Section and assumption
numbers are given so that check is quick.

Findings are paraphrased, not quoted, except where a stated assumption is identified by number.

---

## The short version

Six significant gaps, in order of how strongly they are evidenced and how directly ASTRA's existing
results bear on them:

| # | The gap in existing work | Strongest evidence | ASTRA already has |
|---|---|---|---|
| **L1** | Runtime assurance assumes its safety monitor sees the true state | Synergistic Simplex (2026), **Assumption 8** | R3c, E21 — measured counter-example |
| **L2** | Recovery research assumes detection is already solved | SpecGuard (CCS 2024), threat-model section | R3c — the detector is blind exactly when recovery would be needed |
| **L3** | Combining monitors and checking their consistency is an open problem | ML safety-monitoring survey (2024), **§8 open challenges** | E21 — two monitors complementary; their disagreement unused |
| **L4** | Nothing tells a monitor it has stopped being able to see | Monitor-and-Recover agenda (2025); rational-monitor RV (2024) | the L1-degraded / L6-passes tick |
| **L5** | Conformal runtime guarantees bound false alarms, are derived open-loop, and assume perfect observations | Robust conformal STL verification (2024), assumptions section | R1–R3c — valid calibration, zero detection |
| **L6** | Closed-loop fault masking is studied for classical controllers and detectors, not learned controllers or runtime-assurance monitors | two 2025–26 Springer case studies, both PID-family | R3c — below-baseline alarms under a learned policy |

**They converge on one question existing runtime assurance does not ask: *can my monitor currently
see?*** That is the direction proposed for ASTRA in §3.

---

## 1 · The gaps in detail

### L1 — Runtime assurance assumes the safety monitor sees the true state

**The limitation.** Simplex-style runtime assurance — an unverified learned controller, a verified
fallback, and a monitor that switches between them — is built on the premise that the monitor's
inputs are correct. The most recent work from the group that originated Simplex states this
explicitly.

| paper | what it assumes | evidence |
|---|---|---|
| Bansal, Yeghiazaryan, Khachatryan, Zhu, Kim, Hovakimyan, Sha — *Synergistic Simplex: Cooperative Runtime Assurance for Safety-Critical Autonomous Systems*, arXiv 2605.08190, May 2026 | **Assumption 8 (No Sensor Failure):** all sensors are assumed to operate nominally; malfunctions such as LiDAR dropouts are assumed not to occur, are declared out of scope, and are delegated to "state-of-the-art approaches". The paper does not discuss the safety layer itself failing | `FULL-TEXT` |
| Zhao, Hoxha, Fainekos, Deshmukh, Lindemann — *Robust Conformal Prediction for STL Runtime Verification under Distribution Shift*, arXiv 2311.09482, 2024 | Assumes perfect state observations at runtime; sensor faults are not considered | `FULL-TEXT` |
| Ferrando & Malvone — *Runtime Verification via Rational Monitor with Imperfect Information*, arXiv 2408.11627, 2024 (ACM TOSEM 2025) | States that traditional runtime verification assumes perfect information — that the monitor perceives everything accurately — and that this often fails for autonomous systems with faulty sensors. **Its remedy is for LTL properties over discrete traces**, not continuous control or learned controllers | `ABSTRACT` |
| Phan et al. — *Neural Simplex Architecture*, NFM 2020 | Simplex over a neural controller; sensor faults not evaluated | `ABSTRACT` |

**Why it is significant.** The switching decision is only as good as the monitor's view of the
world. If that view is corrupted, the architecture that exists to catch an untrusted controller can
itself be fooled, and the assumption that prevents this is declared out of scope rather than
addressed.

**What ASTRA has.** A measured instance of the assumption failing: under sustained IMU dropout the
conformal gate detects 0 of 30 runs while a stream-health check at L1 detects 30 of 30 (E18-R3c,
E21).

---

### L2 — Recovery research assumes detection is already solved

**The limitation.** Work on recovering a vehicle after a sensor fault or attack takes a working
detector as given.

| paper | what it assumes | evidence |
|---|---|---|
| Dash, Chan, Pattabiraman — *SpecGuard: Specification Aware Recovery for Robotic Autonomous Vehicles from Physical Attacks*, ACM CCS 2024, arXiv 2408.15200 | Declares attack detection and diagnosis **out of scope**; uses the detector from the authors' prior work (PID-Piper); **does not measure that detector's true or false positives** in this paper. Recovers via a Deep-RL policy across GPS, gyroscope, accelerometer, magnetometer, optical-flow and barometer attacks | `FULL-TEXT` |
| Bansal et al. — *Synergistic Simplex*, 2026 | Delegates sensor failure to existing approaches (see L1) | `FULL-TEXT` |
| Lin & Lee — *Monitor and Recover: A Paradigm for Future Research on Distribution Shift in Learning-Enabled Cyber-Physical Systems*, arXiv 2504.13484, 2025 | Argues for recovery instead of abstention, and states that the monitoring method must itself stay reliable under distribution shift — without supplying a way to establish that | `FULL-TEXT` |

**Why it is significant.** A detect-then-recover pipeline is a chain, and its weakest link is
unmeasured. If the detector is silent during a persistent fault, recovery is never triggered, however
good it is.

**What ASTRA has.** Direct evidence that the link fails in the specific way that would defeat
recovery: the conformal monitor is quieter than its clean baseline for as long as the fault persists
(0.2 % against 5.84 %), and its apparent detection came from after the fault ended (E18-R3b vs R3c).

---

### L3 — Combining monitors and checking their consistency is an open problem

**The limitation.** Safety monitors are designed and evaluated one at a time. The field's own survey
names combining them as unsolved.

| paper | what it says is open | evidence |
|---|---|---|
| Ferreira, Guérin, Delmas, Guiochet, Waeselynck — *Safety Monitoring of Machine Learning Perception Functions: A Survey*, arXiv 2412.06869 (Computational Intelligence, 2025) | **§8 lists as an important open challenge** how to combine several safety monitors and verify the consistency of their outputs. Also: monitors must be evaluated within the integrated system, since not all errors have the same consequences; and there is no unified benchmark | `FULL-TEXT` |
| Guérin, Ferreira, Delmas, Guiochet — *Unifying Evaluation of Machine Learning Safety Monitors*, arXiv 2208.14660, 2022 | Unifies metrics for a single monitor; does not evaluate in closed loop or measure detections lost to the system's own feedback | `ABSTRACT` |
| Hua et al. — *Combining Cost-Constrained Runtime Monitors for AI Safety*, arXiv 2507.15886, 2025 | Combines monitors to maximise recall under a cost budget, in an AI code-review setting. Does not treat disagreement between monitors as a signal, and does not address a monitor that has failed | `ABSTRACT` |

**Why it is significant.** Real stacks run several monitors. Without a principled way to reconcile
them, a system either trusts one and inherits its blind spots, or votes and lets a confidently wrong
majority win.

**What ASTRA has.** Evidence that combination matters and that consistency carries information: the
health check and the conformal gate are **complementary** — health catches `imu_dropout` (gate 0.00),
the gate catches `lateral_noise` (health 0.00) — and their union covers 4 of 6 faults against 3 for
the gate alone (E21).

---

### L4 — Nothing tells a monitor it has stopped being able to see

**The limitation.** Related to L1 and L3, but distinct: even where monitor reliability is recognised
as a requirement, there is no runtime mechanism for detecting that a particular monitor has become
blind.

| paper | what it says | evidence |
|---|---|---|
| Lin & Lee, 2025 | The monitoring method must itself maintain performance under distribution shift — stated as a requirement, not solved | `FULL-TEXT` |
| Ferrando & Malvone, 2024 | Traditional monitors are passive and cannot interpret incomplete data; the fix is formal and discrete (LTL) | `ABSTRACT` |
| Bansal et al., 2026 | Does not discuss the safety layer itself failing | `FULL-TEXT` |

**Why it is significant.** A blind monitor and a healthy system produce the same output: silence.
Unless something distinguishes the two, silence is read as safety. This is the precise hazard
E18-R3c measured.

**What ASTRA has.** A concrete, observable signature of blindness: on the same tick, L1 reports the
IMU degraded and L3's Trust Index collapses to 0.06, while L6 passes. The disagreement exists in the
stack today and nothing consumes it.

---

### L5 — Conformal runtime guarantees bound false alarms, are derived open-loop, and assume perfect observations

**The limitation.** Conformal methods for runtime verification and safety filtering give guarantees on
coverage — equivalently, on how often the monitor raises a false alarm — under assumptions that
closed-loop fault conditions break.

| paper | assumption or scope | evidence |
|---|---|---|
| Zhao et al., 2024 | Calibration trajectories from the training distribution; a distribution-shift bound (an f-divergence) known or estimated **in advance**; open-loop trajectory prediction; policy-induced and closed-loop shift not addressed; perfect state observation. The guarantee is coverage; the paper provides no guarantee on detection power *(the last point is our reading of the guarantee's form)* | `FULL-TEXT` |
| Strawn, Ayanian, Lindemann — *Conformal Predictive Safety Filter for RL Controllers in Dynamic Environments*, IEEE RA-L 2023, arXiv 2306.02551 | Coverage of trajectory-prediction uncertainty for other agents; no sensor faults; no detection rates | `ABSTRACT` |

**Why it is significant.** A false-alarm guarantee is routinely read as a safety guarantee. It is
not: a monitor that never fires satisfies it perfectly. Under closed-loop operation with a faulted
sensor, the exchangeability and perfect-observation assumptions the guarantee rests on do not hold.

**What ASTRA has.** A monitor that satisfies its false-alarm specification — 30 of 30 runs in band
(E18-R3) — and detects nothing under sustained fault (E18-R3c). The guarantee held; the safety did
not.

---

### L6 — Closed-loop fault masking is studied for classical controllers, not learned controllers or runtime-assurance monitors

**The limitation.** That feedback control hides faults from detectors is established. What has been
studied is conventional control with conventional detectors.

| paper | scope | evidence |
|---|---|---|
| Zhang, Yang, Dandago, Li — *The negative impact of closed-loop control on fault detection*, Springer (4th Int. Conf. on Advanced Engineering, Technology and Applications on Power Systems), January 2026 | Shows a faulted closed-loop system can behave like a healthy one, reducing or delaying detection. **PID control**, 2-DOF aircraft, six propeller faults | `ABSTRACT` |
| Gómez-González, Fischer et al. — *Anomaly Detection Under Closed-Loop Fault Masking … Two-Tank Level Control System*, Springer, doi 10.1007/978-3-032-29254-4_6 (venue and year unconfirmed: 2025 or 2026) | Adaptive **PID/RLS** control on a real two-tank plant; SVDD, autoencoder and MLP detectors | `ABSTRACT` |

**Why it is significant.** A learned policy compensates in ways no designer specified, and a
runtime-assurance monitor carries a formal guarantee that practitioners trust. Whether masking
behaves differently there — in particular, whether it can drive a calibrated monitor **below** its
healthy alarm rate — is not addressed by these works.

**What ASTRA has.** Exactly that measurement, under a PPO policy (E18-R3c).

**Confidence.** Lower than L1–L5. "Not studied for learned controllers" rests on the searches run so
far, not an exhaustive survey, and both masking papers were read only at abstract level. **The full
text of the Gómez-González paper must be read before L6 is claimed.**

---

## 2 · Gaps deliberately not targeted

| area | why ASTRA should not compete here | representative work |
|---|---|---|
| Recovery policies as such | Mature and well-performing; ASTRA's contribution is making recovery trigger reliably (L2), not a better recovery policy | SpecGuard (CCS 2024) |
| Secure state estimation theory | A deep control-theoretic literature on estimation under sparse sensor attacks | nonlinear secure estimation (arXiv 2008.12697, `SEARCH`); Fawzi/Tabuada; Pasqualetti (unverified) |
| Semantic anomaly detection as such | Active and fast-moving, built on foundation models. Its monitors report anomalies without a demonstrated link to control response — but that integration point is **not yet verified** as a gap | Elhafsi, Sinha, Agia, Schmerling, Nesnas, Pavone, 2023, arXiv 2305.11307 (`ABSTRACT`) |
| Open-loop vs closed-loop metrics for planners | Adjacent; supports L3/L5 indirectly but is about planners, not monitors | Wang et al., arXiv 2605.00066, 2026 (`FULL-TEXT`): ADE/FDE shows no significant correlation with closed-loop score (ρ = −0.36, n = 8); a safety-aware aggregate correlates strongly but non-monotonically |

The rule: **integrate these, don't compete with them.** ASTRA's value is the layer that decides when
their outputs can be trusted.

---

## 3 · The direction for ASTRA

### The unasked question

Existing runtime assurance asks: *is the controller's action safe?* It assumes the monitor answering
that question can see (L1), that someone upstream has detected any fault (L2), and that each monitor
stands alone (L3). **None of it asks: can this monitor currently see?** (L4) — and its formal
guarantees would not notice if it couldn't (L5).

### What ASTRA should become

> **Monitor-aware runtime assurance: an architecture that does not assume its monitors see the truth.
> It measures, at runtime, whether each monitor is currently able to detect faults — using
> consistency between layers as the evidence — routes decisions away from monitors that have gone
> blind, and triggers fault-specific recovery only on detections it has reason to trust.**

### How each gap maps to the work

| gap | Paper 1 — establish the problem | Paper 2 — ASTRA 2.0 builds against it |
|---|---|---|
| **L1** | Measured counter-example to the "monitor sees the truth" assumption | Monitors never read only the fused estimate; L1 evidence reaches the decision (S1) |
| **L2** | Detection fails exactly when recovery would be needed | Recovery gated on trusted detection; fault isolation first (S5) |
| **L3** | Complementary monitors; unused disagreement | Principled cross-layer consistency checking (S1, S2) |
| **L4** | The blindness signature, observed | **Runtime blind-monitor detection — the core contribution** (S2) |
| **L5** | A calibrated monitor with zero detection | Detection-aware evaluation alongside coverage (S4) |
| **L6** | Masking below baseline under a learned policy | Detectors sensitive to persistence and spread (S4) |

**L4 is the centre.** It is where the evidence is most distinctive — a calibrated monitor going
silent while another layer sees the fault — and where the literature's own statements show a stated
requirement with no mechanism behind it.

---

## 4 · Before any of this is claimed

1. **Confirm every assumption and statement above in the PDFs**, starting with Synergistic Simplex
   Assumption 8, SpecGuard's threat model, and the survey's §8.
2. **Read the full text of both masking papers** (L6).
3. **Run targeted searches for L4 and L3 specifically**, since they carry the direction:
   runtime detection of monitor blindness or degradation; cross-monitor consistency checking;
   detector health monitoring; monitor self-assessment. The survey calls combining monitors open as of
   2024 — work since then must be checked.
4. **Check citing papers** of Synergistic Simplex, SpecGuard and the Ferreira survey for anyone who
   has already relaxed Assumption 8, measured the detector SpecGuard relies on, or built consistency
   checking.

Until step 3 is done, **L3 and L4 are well-evidenced open problems, not confirmed-unclaimed ones.**
