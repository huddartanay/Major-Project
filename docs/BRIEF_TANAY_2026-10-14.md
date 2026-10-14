# Brief for Tanay — 14 October 2026

From Sushanth. Everything below is on branch `3.0`. Read in the order given; items 1–3 need your sign-off
before any Phase 2 run.

## What happened since your merge on 6 October

| date | what | where |
|---|---|---|
| 7 Oct | STEP 6 (pre-registered, held-out): the gate's silence is not caused by the car stopping; a frozen sensor silences it and L1 flags it in 0 of 30 runs | `experiments/phase5_od8_h7/STEP6_MECHANISM_FROZEN_ESTIMATE/final_decision.md` |
| 7 Oct | Finding: the twin predicts steer only (B = (0, 0, 120), plant uses 140), so 99.96 % of the L6 score is throttle and brake | `…/FINDING_TWIN_CHANNEL_MISMATCH_2026-10-07/README.md` |
| 7 Oct | STEP 7: a steering-only score is calibrated and catches a lying position source (11× dev, 17× held-out) but does not reliably catch sensor loss; no outcome confirmed | `…/STEP7_EFFECT_SPACE_GATE/final_decision.md`, `POST_HOC_NOTE_2026-10-07.md` |
| 7 Oct | Direction, phases P1–P10, task plan with owners | `docs/DIRECTION_2026-10-07.md`, `docs/TASK_PLAN_2026-10-07.md` |
| 7 Oct | Exploratory single runs per sensor defect, and with the cold path switched on (exploration never exits) | `…/EXPLORATORY_SENSOR_DEFECT_TRACES_2026-10-07/README.md` |
| 13 Oct | **ICDCN v21 audit:** `benchmarks/fault_study.py` injects position faults through `FaultInjector`, which cannot reach the position channel when redundancy is on. The paper's position rows, Table 5 and the position columns of Tables 4 and 6 measure a run with no fault in it. Camera-ready due 29 October | discussed with Sushanth; record to follow |
| 14 Oct | Phase 1 started: evaluation fault model, P2 audit pre-registration (draft), three classic papers read | below |

## Please read and sign off

1. `docs/FAULT_MODEL_EVALUATION.md` — fault classes F0–F5 for the experiments, mapped to your
   `docs/THREAT_MODEL.md` tiers (which is unchanged).
2. `experiments/phase5_od8_h7/P2_MONITOR_AUDIT/preregistration.md` — **DRAFT**. Section 9 lists the four open
   decisions. Disagree in writing before it is frozen; after that it cannot change.
3. `docs/THREAT_LITERATURE_STUDY.md` §9 — SAVIOR, control invariants, PID-Piper. Consequence for STEP 8: add a
   command-aware residual baseline, not only a frozen-value check.

## Proposed for you (from the task plan; say if you want different ones)

| task | what | phase |
|---|---|---|
| T1.4 | Search for prior work on unit / sign / frame errors as a runtime fault class; log what was searched | P1 |
| T2.4 | Code for monitor M4 and M4b in the audit (ridge-regression behaviour reference) | P2, after the freeze |
| T3.1 | Frozen-value check as benchmark code, unit-tested | P3 |

## Also

- PRs #2–#10 on GitHub are still open; please close them.
- Your PR #11 (web redesign) was viewed on 12 October, unchanged.
