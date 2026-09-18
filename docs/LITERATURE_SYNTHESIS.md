# Literature synthesis — what the reading so far says (18 September 2026)

Built from `NOVELTY_REVERIFICATION.md` §5–§12 and `MANUAL_NOVELTY_CHECK.md`. Scope: published literature
only. Novelty judgments are judgments, not measurements.

## 1 · What was read

| level | papers |
|---|---|
| **PDF, in full (12)** | CoCo (Ruchkin et al. 2022); Lindemann et al. (conformal STL RV); Cleaveland et al. 2023 (conservative safety monitors); Peper et al. 2025; Mao et al. 2025 (pp. 1–25); Cleaveland et al. 2025 (conservative perception models); ModelGuard; Luo et al. (conformal warning systems); Henzinger & Saraç (monitorability under assumptions); Volkhonskiy et al. (conformal martingales); Gibbs & Candès (ACI); Barber et al. (§1–4, §7) |
| **Abstract only, cleared (8)** | Lu et al. ×3; Geng et al.; Mao et al. 2023, 2024 ×2; Silva et al. review |
| **Not yet read** | Tier 1: Ruchkin TCAD 2020, Lukina RV 2021, Arnez DSD 2022, Granig FORMATS 2020. Tier 2: Gómez-González, Zhang et al., DeLorean, Cairoli, Synergistic Simplex, Antonante, Kempa, Boursinos |

**No paper read does what ASTRA claims.** Every one narrows the wording somewhere.

## 2 · The pattern across all twelve

Every guarantee in these papers is **conditional on an assumption about the monitor's inputs**, and the
papers fall into four groups by what they do about it:

| group | what they do | papers | what they leave open |
|---|---|---|---|
| **A · Assume, never check** | Guarantee holds if inputs are calibrated / exchangeable / memoryless | Lindemann (Assumption 1), Cleaveland 2023 (Thm 1: calibrated estimator), Cleaveland 2025 (Eq. 7: memoryless perception), Mao 2025 (exchangeable calibration), Henzinger & Saraç (assumption given) | When the assumption breaks at runtime, the guarantee lapses **silently** |
| **B · Check, but offline or with ground truth** | Validate the perception / dynamics model against data | Peper 2025 (offline, true states, one verdict per environment); ModelGuard (per trace, online only sketched) | Detection **within a run, at fault onset, without ground truth** |
| **C · Check the controller's assumptions at runtime** | Compose monitors of verification assumptions | CoCo | Assumes the **monitors themselves** stay accurate; monitoring monitors listed as future work |
| **D · Statistical tools that could detect it** | Change detection on conformal p-values; adaptive thresholds; coverage-gap bounds | Volkhonskiy, Gibbs & Candès, Barber, Luo | Not applied to a safety gate; ACI needs labels; Barber lists adaptive detection of coverage failure as an **open question** (p. 18) |

**Shared-path observation.** In all six monitor papers (A–C) the monitor reads the same state estimate the
controller acts on. None discusses this. ASTRA's L6 gate has the same structure (proposer and twin both
read L2). **Caution:** our own common-mode pilot *refuted* shared-path as the mechanism of ASTRA's blindness,
so it may be named as a structural property, **not** as the proven cause.

## 3 · Claims after the reading

| claim | status | correct wording |
|---|---|---|
| **Core finding** — a calibrated conformal gate goes silent under a persistent sensor fault | **Holds; strengthened.** No counterexample in 12 full reads | "…detected online, within a run, at fault onset, without ground truth, for persistent faults outside the calibrated model." Say **alarm-blind at its calibrated threshold** — E17 shows the score still separates (D_s 0.737) |
| **B1** — detect that the gate has lost detection capability | **Problem holds; method is not new.** Conformal martingales (Volkhonskiy), few-sample bounds (Luo) and coverage-gap theory (Barber) exist | "A runtime detector of a safety gate's loss of detection capability in closed loop, for which no prior work was found." Never "the first" |
| **N1** — integrity not consumed by the safety gate | Narrowed earlier (CoCo monitors observation assumptions) | Cite CoCo as monitoring *assumptions*, not *detection capability* |
| **N2** — coverage met, detection zero | **Supported** — Lindemann, Mao, Luo never measure misses under sensor faults | Unchanged |
| **N3** — persistent-fault regime | **Narrowed and supported.** Cleaveland 2023 handles modelled transient glitches; Peper studies persistent bias as a whole environment; Cleaveland 2025 is memoryless by construction | "Persistent, out-of-model, arriving mid-run" |
| **N4, N5, N6** | **Not tested by this reading** — their threats (Gómez-González, Zhang, Antonante, Kempa, Bench2Drive) are unread | — |

## 4 · The strongest idea the reading produced

**Loud versus silent failure.** Luo et al. (Fig. 13d) show that under exchangeability an uninformative
detector fails **loudly** — it alarms almost always. Barber et al. (p. 16) show that when exchangeability
breaks the error can go **either way**, and which way cannot be known in advance. ASTRA's data shows which
way it went: the gate **over-covers** — alarms fall from 5.84 % to ≈0.2 % under sustained `imu_dropout`.

This gives the paper a precise, citable framing: *conformal gates are safe against uninformative scores
under exchangeability, but a persistent sensor fault breaks exchangeability in the over-coverage direction,
where no existing guarantee or monitor raises a signal.* The **mechanism** of that direction in ASTRA is
still unexplained and needs experiment 2.6.

## 5 · Gap statements available to cite

| source | statement (paraphrased) | where |
|---|---|---|
| CoCo | Assumes monitors well-calibrated and accurate; monitoring other monitors is future work | §6 pp. 9–10 |
| Barber et al. | Open question: determine adaptively whether coverage will hold | p. 18 |
| Peper et al. | A gap remains between verification and validity of its assumptions once deployed | §1 p. 2 |
| Lindemann et al. | Guarantee is marginal over the calibration distribution | Remark 2 p. 8 |
| Cleaveland et al. 2023 | Conservatism assumes a well-calibrated state estimator | Thm 1 p. 10 |
| Mao et al. 2025 | Asserts, without testing, that OOD inputs widen intervals and alert the controller | p. 15 |
| Henzinger & Saraç | Networks of monitors and assume-guarantee monitoring are future work | §6 p. 15 |

## 6 · Consequences for the Phase 3 monitor and experiments

1. **One-sided test** for too-large p-values (under-alarming); a two-sided test cannot tell a blind gate from
   a correctly alarming one.
2. **Calibrate on whole clean runs** — closed-loop tick scores are temporally correlated.
3. **Baselines:** ModelGuard (expect it to catch dropout, possibly miss bias); two-sided conformal martingale;
   ACI on alarms (restores the rate, destroys the meaning); the L1 health monitor; an **oracle gate fed
   ground truth** (Cleaveland 2023's true-state monitor) to measure blindness directly.
4. **Magnitude sweep including small shifts** — Peper excluded 0–2.45 as inconclusive; that band is where
   gates are hardest to judge.
5. **Show the blind flag changes an outcome** — still the biggest open risk, because the health monitor
   already catches `imu_dropout` in 5 ticks.

## 7 · Rough novelty after this reading (judgment)

| item | before | now | why |
|---|---|---|---|
| Core finding | ~60–70 % | **~65–75 %** | 12 full reads, no counterexample; wording now precise |
| B1 as a problem | ~45–60 % | **~55–65 %** | Barber names it open; CoCo lists it as future work |
| B1 as a method — score-only | — | **low (~10–15 %)** | ≈ KS(conf) (Sun & Lampert 2018) / conformal martingale on the gate's scores |
| B1 as a method — cross-layer disagreement | — | **moderate (~35–50 %)** | Needed when the gate's scores do not change; not found in 14 full reads |

**Update 18 Sept:** Lukina et al. (self-assessing monitor sees false alarms, not silence) and KS(conf) read — see `NOVELTY_REVERIFICATION.md` §13–14.
