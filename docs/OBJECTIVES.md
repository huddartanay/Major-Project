# ASTRA — Objectives

**Finalised 13 September 2026.** Supersedes objectives stated in earlier plans where they conflict.
Every objective has a measurable completion condition. An objective is not done because work was
done on it; it is done when its condition is met and recorded in the claim ledger.

Evidence referred to below is on branch `3.0`; see `docs/GAP_VERIFICATION.md`.

---

## 0 · Two corrections that change decisions

1. **SAFECOMP is not an IEEE venue.** It is published by Springer (LNCS). Earlier advice recommended
   "ITSC or SAFECOMP"; for an IEEE submission the candidates are **IEEE ITSC**, **IEEE ISSRE**, and
   **IEEE/IFIP DSN**. See §3.
2. **comma2k19 is logged data, so replaying it is open-loop.** The recorded vehicle's trajectory does
   not respond to ASTRA's commands, which means **closed-loop fault masking — the mechanism behind the
   central finding — cannot occur in a replay.** External validation on comma2k19 can test the
   sensor- and estimator-level parts of the claim on real noise; it cannot reproduce the blind spot
   itself. O4 is scoped accordingly, and a reviewer must be told this rather than left to discover it.

---

## 1 · The north star

> **A runtime governance system for a learned controller that detects faults — including ones that
> persist — without going quiet; knows which sensor is at fault; responds to *that* fault by restoring
> the best functional state available rather than only degrading toward a stop; and stays safe when a
> sensor is compromised or a reading is semantically wrong.**

What the literature review established about this goal, and must shape it:

- Fault-tolerant reconfiguration, secure estimation under sensor attack, and semantic anomaly
  detection **each already exist as fields**. ASTRA will not be novel for having any of them.
- ASTRA's differentiator has to be what the evidence uncovered: **a governance stack whose layers can
  disagree, and which treats that disagreement — especially a monitor that has gone blind — as a
  first-class signal.** Every capability is organised around that.

The north star is reached in two stages. Stage 1 proves the problem exists and locates it. Stage 2
builds against it.

---

## 2 · Stage 1 — Paper 1: establish and locate the gap

**Thesis.** Calibration validity, statistical separability and operational detectability are three
different properties of a runtime monitor. A conformal monitor of a learned controller can have the
first two and lack the third — going quieter than its own healthy baseline while a sensor failure
persists — and the failure is architectural: the evidence is present elsewhere in the stack and the
gate does not consult it.

**Gate.** Nothing is submitted with an open P0 (`conference.md`).

| # | Objective | Done when | Status |
|---|---|---|---|
| **O1** | **Make the empirical gap verifiable by someone else** | `3.0` pushed to the team remote; an independent verifier resolves E1–E5 against it; E6 has a bootstrap CI on ρ and a per-fault breakdown | **Blocked on push.** Evidence exists locally; E6 lacks CIs |
| **O2** | **Confirm the gap is not already published** | Full text of the closed-loop fault-masking paper read; the eight searches in `GAP_VERIFICATION.md` §4 run and logged; the seven unverified citations read first-hand; verdict recorded for the conjunction | **Open.** Four works verified; none contains the conjunction |
| **O3** | **Show the blind spot is architectural, not a calibration choice** | Pre-registered experiment: adaptive conformal inference on the E21 protocol. If ACI also misses sustained `imu_dropout`, recorded as supporting the architectural reading; if it catches it, the thesis narrows to "vanilla split-conformal" | **Not started** |
| **O4** | **External validation of what replay can test** | comma2k19 acquired and split frozen; the sensor-level cross-check and L1 evidence of E2/E5 reproduced on real sensor noise with injected faults; **first `[M-ext]` row**; the open-loop limitation stated in the paper | **Not started.** The long pole |
| **O5** | **Indicative remedy** *(decision required — §5)* | A cross-layer disagreement signal evaluated on the E21 protocol, reported as indicative: expected to cover at most 4 of 6 faults, with `speed_bias` and `speed_stuck` stated as unsolved | **Not started** |
| **O6** | **Paper rewritten on the corrected thesis** | Every claim maps to a ledger row and a table; every number re-measured from `3.0`; architecture presented as the instrument, not the contribution; fault masking, Simplex and conformal safety filters cited as prior art; zero open P0 | **Not started** |
| **O7** | **Submit** | Compliance checklist in `conference.md` Step 20 complete; submitted to the venue chosen in §3 | — |

### Already achieved toward Stage 1

| | evidence |
|---|---|
| Calibration valid on P1 at 160 s — 30/30 in band | E18-R3 |
| Monitor below its own baseline under sustained fault — 0/30 detected, ~0.2 % vs 5.84 % | E18-R3c |
| Apparent detection was the recovery transient — 99.06 % vs 0.18 % | E18-R3b vs R3c |
| Evidence caught upstream — `health` 30/30, 0 false positives, 5 ticks | E21 |
| Separability is not detection — sensor 0.998, monitor score 0.737, alarms below baseline | E17, R3c |
| Two previously assumed detectors are unusable (`trust`, `innovation`) | E21 |
| Monitorability (location-only) withdrawn; `D_s` confirmed not predictive | Phase 2 |
| Test suite green, brittle claims withdrawn with measured n | `1848dd6` |

### Explicitly out of scope for Paper 1

Architectural novelty · adversarial sensors · semantic errors · reactive recovery · CARLA · policies
P2 and P3 · severities other than `medium`. Each is either not built or already in the literature,
and including any of them invites an overclaim rejection.

---

## 3 · Venue

Deadlines are not stated here; they must be taken from each official call for papers.

| venue | publisher | fit | risk |
|---|---|---|---|
| **IEEE ITSC** | IEEE ITSS | Vehicle framing; most tolerant of simulation-based evaluation among IEEE AV venues | Broad scope; the negative result must be framed as a safety finding, not a methods critique |
| **IEEE ISSRE** | IEEE | Software reliability; runtime-monitor failure analysis and measurement methodology are in scope | Fewer autonomy reviewers; the control-loop mechanism needs more explanation |
| **IEEE/IFIP DSN** | IEEE / IFIP | Dependability; values rigorous measurement and negative results | Highly competitive; weakest fit for a single synthetic plant |

**Recommendation: IEEE ITSC first, ISSRE as the alternative.** Hold DSN until external validation is
stronger than replay-only.

---

## 4 · Stage 2 — ASTRA 2.0: close the gap

Every objective below is scored on the **same protocol Stage 1 used** — the E21 design: P1, 30 seeds,
sustained injection opening at tick 200, 3,400 ticks, a 30-run clean arm, detection ≥ 0.90 at clean
false-positive ≤ 0.10. That is what makes Stage 2 measurable rather than aspirational.

| # | Objective | Done when | Depends on |
|---|---|---|---|
| **S1** | **Cross-layer evidence fusion** — evidence from every layer reaches the veto decision | `imu_dropout`, `position_bias`, `position_drift`, `lateral_noise` all ≥ 0.90 at clean FP ≤ 0.10 under sustained injection | Paper 1 |
| **S2** | **Self-trust** — detect that a monitor has gone blind, and never score silence as safety | The blind condition (e.g. L1 degraded while L6 is quiet) flagged on `imu_dropout` 30/30 at clean FP ≤ 0.10; decisions routed away from the blind monitor | S1 |
| **S3** | **Channel coverage** — the speed channel is observed | `speed_bias` and `speed_stuck` ≥ 0.90 at clean FP ≤ 0.10. Neither is detected by anything today | S1 |
| **S4** | **Detectors that respond to persistence and spread** | A dispersion-augmented monitorability metric, pre-registered fresh, predicts detection at ρ ≥ 0.70 identity-free; a persistence-accumulating rule outperforms per-tick crossings on sustained faults | Phase 2 |
| **S5** | **Fault isolation and fault-specific response** | The faulty channel is identified; it is excluded and the state re-estimated; the vehicle returns to NOMINAL, or holds a better state than graduated fallback, with lower lateral deviation — compared against a published attack-recovery baseline | S1, S2 |
| **S6** | **Adversarial sensors** | A strategic attacker that deliberately exploits the masking channel is detected or tolerated; compared against secure-estimation baselines; prior art conceded explicitly | S1–S5 |
| **S7** | **Semantic errors** | Scoped only after S1–S5. Semantic anomaly detection is an established field; ASTRA's contribution, if any, is routing semantic evidence through the same self-trust mechanism | S2 |

Stage 2 is **Paper 2**, not an extension of Paper 1.

---

## 5 · Decisions that are yours to make

1. **Venue** — ITSC or ISSRE (§3).
2. **Whether O5 goes in Paper 1.** Including an indicative remedy makes the paper more useful and more
   exposed: it must be reported as partial, since two of six faults would remain undetected.
3. **Push `3.0` to the team remote.** O1 cannot complete until this happens.
4. **Whether Paper 1 needs a second policy.** P1 only is honest but narrow; E18-R4 (recovering P3) is
   the route to two policies and is currently optional.

---

## 6 · Order of work

```
push 3.0 ──► O1 ──┐
                  ├──► O6 ──► O7   (Paper 1)
O2 ───────────────┤
O3 ───────────────┤
O4 ───────────────┤        (long pole — start early)
O5 (if chosen) ───┘

Paper 1 ──► S1 ──► S2, S3 ──► S5 ──► S6
            S4 (can run alongside S1)
            S7 (after S2)
```

**O2 goes before O6.** If the full text of the fault-masking paper already reports below-baseline
alarms, the thesis becomes an extension of a known result, and rewriting the paper first would be
wasted work.
