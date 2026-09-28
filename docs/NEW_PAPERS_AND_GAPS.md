# 20 new papers and candidate gaps (18 September 2026)

Found by web search, **not yet read**. Titles and arXiv IDs are taken from search results; check each
before citing. Priority: **H** = could narrow G1/G2, **M** = informs design, **L** = future gaps.

## A · Could narrow G2 (monitor reliability, silent failure)

| # | paper | why | prio |
|---|---|---|---|
| 1 | *WATCH: Adaptive Monitoring for AI Deployments via Weighted-Conformal Martingales*, arXiv 2505.04608 | Conformal-martingale deployment monitoring — closest tool to a score-based blindness detector | **H** |
| 2 | *Taming Silent Failures: A Framework for Verifiable AI Reliability* (FAME), arXiv 2510.22224 | "Silent failures" of AV perception; offline synthesis + runtime monitors | **H** |
| 3 | *Unifying Evaluation of Machine Learning Safety Monitors*, arXiv 2208.14660 | Metrics for evaluating monitors — may define monitor "blindness" | **H** |
| 4 | *Closing the Loop on Runtime Monitors with Fallback-Safe MPC*, arXiv 2309.08603 | Acting on a monitor's output — design for G2's outcome step | M |
| 5 | *Runtime Safety Monitoring of Deep Neural Networks for Perception: A Survey*, arXiv 2511.05982 | Notes output-based monitors are fooled by confident wrong outputs | M |
| 6 | *Argus: Resilience-Oriented Safety Assurance Framework for End-to-End ADSs*, arXiv 2511.09032 | Resilience of end-to-end driving safety assurance | M |
| 7 | *Detecting and Mitigating System-Level Anomalies of Vision-Based Controllers*, arXiv 2309.13475 | Closed-loop anomaly monitor + mitigation | M |
| 8 | *Can We Detect Failures Without Failure Data? Uncertainty-Aware Runtime Failure Detection for Imitation Learning Policies*, arXiv 2503.08558 | Runtime failure detection, conformal calibration | M |
| 9 | *FIPER: Failure Prediction at Runtime for Generative Robot Policies*, arXiv 2510.09459 | OOD + action uncertainty, conformal-calibrated | M |

## B · Conformal and safety filters under shift or estimation error

| # | paper | why | prio |
|---|---|---|---|
| 10 | *Safe Control using Learned Safety Filters and Adaptive Conformal Inference*, arXiv 2604.18482 | ACI inside a safety filter — the "why not ACI?" question again | **H** |
| 11 | *Output Feedback Backup Control Barrier Functions: Safety Guarantees Under Input Bounds and State Estimation Error*, arXiv 2604.19893 | Safety filter robust to bounded estimation error | M |
| 12 | *Conformal Prediction under Lévy-Prokhorov Distribution Shifts*, arXiv 2502.14105 | Robust conformal under bounded shift | M |
| 13 | *Vision-Based Runtime Monitoring under Varying Specifications using Semantic Latent Representations*, arXiv 2605.13923 | Certified ptSTL monitoring from images under partial observability | M |
| 14 | *Runtime Monitoring of Perception-Based Autonomous Systems via Embedding Temporal Logic*, arXiv 2605.12651 | Monitoring in embedding space | L |

## C · Estimator-driven masking (mechanism H1)

| # | paper | why | prio |
|---|---|---|---|
| 15 | *Detecting Slowly Accumulating Faults Using a Bank of Cumulative Innovations Monitors in Kalman Filters*, NAVIGATION (ION) 69(1), navi.507 | Innovation monitors and their sensitivity to model/covariance mismatch | **H** |
| 16 | *Dual Detection Framework for Faults and Integrity Attacks in Cyber-Physical Control Systems*, arXiv 2510.14052 | Separating faults from attacks | M |

## D · Adversarial and lying sensors (future gaps)

| # | paper | why | prio |
|---|---|---|---|
| 17 | *Requiem for a drone: a machine-learning based framework for stealthy attacks against unmanned autonomous vehicles*, arXiv 2407.15003 | Stealthy spoofing that evades EKF-based anomaly detectors — adversarial gate blinding | L |
| 18 | *Secure Safety Filter Design for Sampled-data Nonlinear Systems under Sensor Spoofing Attacks*, arXiv 2505.06842 | Safety filter under spoofing | L |
| 19 | *Barrier Certificate based Safe Control for LiDAR-based Systems under Sensor Faults and Attacks*, arXiv 2208.05944 | Safety under sensor faults and attacks | L |
| 20 | *Spatial-Temporal Anomaly Detection for Sensor Attacks in Autonomous Vehicles*, arXiv 2212.07757 | Attack detection across sensors and time | L |

Extras: *Peak Bounds for the Estimation Error under Sensor Attacks* (arXiv 2602.04568); *Formalizing and
Evaluating Requirements of Perception Systems … Spatio-Temporal Perception Logic* (arXiv 2206.14372).

## Candidate new gaps aligned with the goals (hypotheses — not yet verified)

| gap | goal served | why it looks open | status |
|---|---|---|---|
| **G3 · Uncertainty-normalised gates lose sensitivity when sensors fail** — a gate that divides by filter covariance becomes *less* sensitive exactly when a sensor drops out, because the covariance inflates | Detect | Code shows the L6 score divides by √P_f; navigation literature knows χ² tests fail under covariance inconsistency, but not for learned-controller safety gates | **Fold into this paper** if experiment 2.6 confirms H1 |
| **G4 · Recovery after the safety stack itself degrades** — returning from fail-safe to nominal with evidence, when the monitor's reliability is in doubt | React / recover | L8 has no automatic exit from HALT; RTA work covers switching *to* the fallback, rarely switching *back* | Needs a search on Simplex reverse switching |
| **G5 · Adversarial blinding of conformal safety gates** — can an attacker drive the gate into its silent regime, and does cross-layer G2 resist? | Hacked / adversarial sensors | Stealthy attacks target residual/EKF detectors (#17); none found targeting conformal gates of learned controllers | Next paper; bounded by secure-estimation limits |
| **G6 · Semantic consistency between layers feeding a safety gate** | Semantic errors | Perception logics exist (#13, #14, STPL) but are not linked to control-level safety gates | Weakest evidence; later |
