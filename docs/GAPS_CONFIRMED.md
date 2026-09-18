# The gap ASTRA closes — reconfirmed (18 September 2026)

Based on 18 papers read in full (`NOVELTY_REVERIFICATION.md` §5–§15, `LITERATURE_SYNTHESIS.md`).
Novelty figures are judgments.

## The gap, in one sentence

> Runtime safety gates carry guarantees that hold only while their inputs stay calibrated. When a
> **persistent sensor or state-estimation fault** arrives **mid-run** in **closed loop**, a gate can fail
> **silently** — it stays alive, confident and calibrated but stops alarming — and **no existing method
> detects this at runtime without ground truth**.

## Evidence that it is open

| source | what it says or shows | where |
|---|---|---|
| CoCo (ICCPS 2022) | Assumes monitors stay well-calibrated and accurate; monitoring other monitors is future work | §6 pp. 9–10 |
| Barber et al. (Ann. Stat. 2023) | Detecting adaptively whether conformal coverage will hold is an **open question**; errors can go either way | pp. 16, 18 |
| Lindemann et al. | Guarantee is marginal over the calibration distribution; lapses silently outside it | Remark 2 p. 8 |
| Cleaveland et al. 2023 | Conservatism assumes a well-calibrated state estimator | Thm 1 p. 10 |
| Mao et al. 2025 | Asserts, without testing, that OOD inputs widen intervals | p. 15 |
| Peper et al. 2025 | Detects a broken perception assumption — **offline, with ground truth, per environment** | §4.3, Table 2 |
| Lukina et al. 2021 | Self-assessing monitor measures precision only — **cannot see its own silence** | §3 p. 5 |
| Antonante et al. 2022 | Models diagnostic tests that pass under common-mode failure — **assumed a priori, not detected**; state estimation is future work | Def. 7 p. 15; §8 |
| KS(conf) 2018 | Two-sided score test on a classifier; flags any shift, cannot tell blind from working; misses faults that leave scores unchanged | §2 p. 4; §3.5 |

## What we close — two parts

| part | claim | status |
|---|---|---|
| **G1 · Finding** | A calibrated conformal safety gate goes **alarm-blind at its calibrated threshold** under a persistent sensor fault in closed loop: alarms fall from 5.84 % (clean) to ≈0.2 % (sustained `imu_dropout`), 0/30 runs detected, while the fault is real (L1 detects 30/30). This is the **silent (over-coverage) direction** that Luo et al. show cannot occur under exchangeability | **Evidence exists** (R3/R3c, E17, E21). Missing: mechanism (exp. 2.6), CIs (2.3), magnitude sweep incl. small faults |
| **G2 · Method** | A runtime **gate-blindness monitor** that treats the safety gate as a diagnosable component and flags it from **cross-layer disagreement** (independent layer reports a fault, gate stays silent), with a bound on false "blind" flags — and **acting on the flag improves outcomes** | **Not built.** Must beat KS(conf), conformal martingale, ModelGuard, L1 health alone; oracle gate on ground truth as reference |

Supporting claims kept, with tightened wording: **N2** coverage met, detection zero (no paper measures
misses under sensor faults); **N3** persistent, out-of-model, arriving mid-run.

## What is *not* the gap — never claim these

| not ours | already done by |
|---|---|
| "First monitor of a monitor" | HALO (liveness), CoCo (assumption confidence), Lukina (precision), Antonante (unreliable tests) |
| A new statistical test for shift | KS(conf), conformal martingales (Volkhonskiy), ACI (Gibbs & Candès) |
| Detecting a broken perception assumption offline | Peper et al. |
| Sensor voting / redundancy | Kempa et al. and classical FDI |
| Few-sample bounds on a warning system's miss rate | Luo et al. |

## Scope relative to the original goal

| goal element | covered by this paper? |
|---|---|
| Detect faults | Yes — and detect when the detector itself goes blind |
| React and recover to a better state | Partly — only if G2's flag triggers a mitigation that improves outcomes (must be shown) |
| Hacked / adversarial sensors | **No** — injected faults only; state as future work |
| Semantic errors | **No** — future work |

## Novelty (judgment)

| item | estimate |
|---|---|
| G1 finding | ~65–75 % |
| G2 as a problem | ~55–65 % |
| G2 method (cross-layer) | ~30–45 % |
| G2 method (score-only) | ~10–15 % — do not build it this way |

## Still unchecked

Ruchkin et al. TCAD 2020, Arnez et al. DSD 2022, Granig et al. FORMATS 2020; Google Scholar sweep incl.
"Cited by" for CoCo, KS(conf) and Antonante.
