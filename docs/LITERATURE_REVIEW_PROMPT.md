# Literature review prompt — ASTRA novelty check

Paste everything below the line into Claude (or another capable model) **with web search
enabled**. It is written to be self-contained: the reviewer has none of this project's context.

The prompt is deliberately adversarial. It asks the reviewer to *destroy* the novelty claim, not to
support it, because a literature review that sets out to confirm novelty will always find a way.

---

# TASK

You are a systematic literature reviewer with access to web search. Your job is **to find prior work
that invalidates the novelty claims below.** You are not writing a related-work section and you are
not helping anyone publish. Assume each claim has already been made by somebody, and go find them.

A claim survives only if you searched hard and failed. Report "novel" only with the searches you ran
listed, so a reader can judge whether you looked in the right places.

If a claim is already in the literature, **say so plainly and give the citation.** That outcome is
more useful than a false all-clear, because it saves a rejected submission.

---

# THE SYSTEM UNDER REVIEW

A runtime governance architecture for a vehicle controlled by a **learned (reinforcement-learning)
policy**. The design separates two domains with a one-way trust boundary:

- **Core-A (untrusted):** the learned policy. It only ever *proposes* a control action.
- **Core-B (trusted):** conventional, inspectable layers that can veto the proposal and decide what
  is actually sent to the actuator. The learned policy never commands directly.

Nine layers, in the order a control tick passes through them:

| layer | function |
|---|---|
| L1 | Sensing. Redundant multi-modal sensor bus with per-modality stream health |
| L2 | State estimation. Dual-rate Unscented Kalman Filter; sole state source |
| L3 | Trust. A "Trust Index" from a Mondrian conformal context over the filter innovation |
| L4 | Learned proposer. PPO under a PID-Lagrangian constrained MDP |
| L5 | Digital twin. A physics-informed neural network producing a one-step reference action |
| L6 | Statistical gate. **Split/inductive conformal prediction.** Non-conformity score is the Euclidean distance between the proposal (L4) and the twin's prediction (L5), normalised by the square root of the filter's control-dimension variance, thresholded against a Mondrian-conditional calibration quantile |
| L7 | Shield. Deterministic hard bounds plus a physical admissibility check |
| L8 | Fail-safe. A state machine (NOMINAL → DEGRADED → LIMP → HALT) driven by two separate counters: an out-of-distribution counter and a sensor-integrity counter |
| L9 | Arbitration. Runtime calibration management; selects a certified profile per operating context, and engages a deliberately narrowed "bounded safe exploration" envelope when no certified profile matches |

**Empirical findings obtained with this system** (synthetic plant, 30 seeds, pre-registered,
frozen thresholds):

- Under a **sustained** sensor failure (IMU dropout persisting 160 seconds), the conformal gate's
  alarm rate is **0.2%**, which is *below* its ~5% alarm rate on a healthy vehicle. The monitor is
  **quieter during the fault than during normal operation.**
- Apparent detection of that fault came almost entirely from the **post-fault recovery transient**.
  Where the fault never ends, detection never happens.
- Of six injected fault classes, only **three** are detected under sustained injection.
- **Statistical discriminability does not predict operational detection.** Faulted and clean runs
  separate at AUC ≈ 0.998 for a fault the monitor never alarms on. Across cells, sensor-level
  discriminability is *anti-correlated* with detection (Spearman ρ = −0.480, p = 0.0088).
- Conformal validity failed because the calibration set was not exchangeable with live scores
  (a calibration-provenance failure, not a bad threshold value).

---

# CLAIMS TO CHECK

Check each **independently**. For each, give a verdict: **ALREADY EXISTS / PARTIALLY EXISTS /
NOT FOUND**, with citations and one sentence on how close the prior work is.

**C1 — Architecture.** A runtime-assurance architecture for a learned controller in which a
*conformal-prediction* gate compares the learned proposal against a *learned physics-twin*
prediction, inside a Simplex-style one-way trust boundary.

**C2 — The alarm-suppression finding.** That a residual/conformal runtime monitor becomes
**quieter than its own healthy baseline** during a sustained sensor fault, so that monitor silence
becomes positive evidence for a compromised system.

**C3 — Aftermath-only detection.** That such a monitor's apparent detection is dominated by the
**post-fault recovery transient** rather than the fault interval, so detection rates measured on
faults that end are not transferable to faults that persist.

**C4 — Discriminability ≠ detectability.** That offline separability (AUC/discriminability) of
faulted vs clean data fails to predict, and can be anti-correlated with, a deployed monitor's
operational detection rate.

**C5 — Monitorability metric.** A pre-deployment metric predicting whether a monitor's decision
statistic has the dynamic range and stability to support a reliable threshold.

**C6 — Self-trust.** A runtime mechanism by which a monitoring system **measures whether each of its
own monitors can currently be trusted** and routes decisions accordingly ("a monitor for the
monitors").

**C7 — Phase-aware detection.** A detection rule that explicitly distinguishes fault-interval
activity from post-fault recovery, so that silence during a fault is not scored as safety.

**C8 — Adversarial extension.** Resilience of such an architecture to **compromised or adversarial
sensors** — a sensor that lies strategically rather than failing stochastically.

**C9 — Semantic errors.** Detection of **semantic** faults (the reading is physically valid and
statistically unremarkable but means the wrong thing) as distinct from numerical sensor faults.

**C10 — Reactive recovery.** Fault-*specific* reconfiguration that returns the system to a **better
functional state**, as opposed to graduated degradation toward a safe stop.

---

# WHERE THE PRIOR ART MOST LIKELY LIVES

Search these deliberately. Several are strong candidates to kill a claim outright, and missing them
would make the review worthless.

**Highest risk — check first:**

1. **Fault masking by feedback control.** Classical FDI has long known that a closed-loop controller
   compensates for a fault, shrinking the residual and hiding it. If C2 is an instance of this, say
   so. Search: *fault masking closed loop*, *detectability degradation feedback control*,
   *closed-loop fault detection residual attenuation*.
2. **Stealthy / covert / zero-dynamics attacks on CPS.** There is a mature literature on attacks
   *constructed* to be invisible to residual-based detectors — covert attacks, zero-dynamics
   attacks, replay attacks. If a sustained sensor fault is a naturally-occurring stealthy attack,
   C2 and C8 are both weakened. Search: *stealthy attack undetectable residual*, *covert attack CPS*,
   *zero dynamics attack*, *replay attack Mo Sinopoli*.
3. **Secure state estimation under sensor attack.** Fawzi/Tabuada, Pasqualetti, Shoukry, SMT-based
   detection. Directly relevant to C8.
4. **Conformal prediction under distribution shift / exchangeability violation.** Weighted and
   adaptive conformal prediction (Tibshirani, Gibbs & Candès, Barber et al.). The calibration
   finding may be a known instance.

**Also required:**

5. Simplex architecture and runtime assurance (Sha; Seto; NASA/AFRL run-time assurance).
6. Shielded reinforcement learning (Alshiekh et al.), safe RL, constrained MDPs.
7. Runtime verification and runtime monitoring of neural network controllers.
8. Out-of-distribution and anomaly detection for autonomous driving; OOD detection blind spots.
9. Digital-twin-based fault detection and residual generation.
10. Conformal anomaly detection and conformal martingales for change detection.
11. Assurance cases, ISO 26262, and SOTIF (ISO/PAS 21448) for the "insufficiency of specification"
    framing.
12. Semantic anomaly detection in autonomous systems; "semantic" failures in perception.
13. Meta-monitoring, monitor evaluation, "who watches the watchmen" in safety-critical software.
14. Detectability/observability of faults — control-theoretic definitions that may already formalise
    C5 (e.g. fault detectability indices, structural detectability).

**Venues to search directly:** IEEE TAC, TCST, T-ITS, TDSC, TR (Reliability); ICCPS, HSCC, ITSC, IV,
ICRA, IROS; CAV, RV (Runtime Verification), EMSOFT, DSN, SAFECOMP; NeurIPS/ICML/ICLR for conformal
and safe-RL work; ACM CCS / IEEE S&P / NDSS for sensor-attack work. Also check arXiv preprints from
the last 24 months, which is where this area moves fastest.

---

# METHOD

1. For each claim, run **at least four distinct search phrasings**, including at least one using the
   control-theory vocabulary (*residual*, *detectability*, *fault masking*) and one using the
   machine-learning vocabulary (*OOD*, *conformal*, *anomaly*). The same idea has different names in
   the two communities, and searching only one is the most common way a review misses prior art.
2. Prefer peer-reviewed venues; include arXiv but mark it.
3. When you find something close, **read the abstract and state precisely what it does and does not
   cover.** "Related" is not a verdict.
4. Do not pad. Ten decisive citations beat sixty adjacent ones.

---

# OUTPUT

**A. Verdict table** — one row per claim C1–C10: verdict, closest prior work, citation, one-sentence
distinction (or "none — subsumed").

**B. The three most dangerous papers.** The work most likely to be cited by a reviewer as
"this has been done". For each, say exactly which claim it threatens and how a rebuttal might go, or
state honestly that there is no rebuttal.

**C. The surviving claim.** Write the single strongest **defensible** novelty sentence the evidence
supports, in the form: *"To our knowledge, no prior work has ___."* If nothing survives, say that,
and say what adjacent claim *would* be defensible instead.

**D. Reframing options.** If the primary framing is dead, give two alternative framings the same
experimental results would support.

**E. Gaps that must be closed before submission.** Specifically: what a reviewer would demand that
this work does not yet have. Note that the current results are on a **single synthetic plant**, one
policy, one severity level, with **no real-world or external dataset validation**.

**F. Search log.** Queries run, per claim, so the review can be audited and repeated.
