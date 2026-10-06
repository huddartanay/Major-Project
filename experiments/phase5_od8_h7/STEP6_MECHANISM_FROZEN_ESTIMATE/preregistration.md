# STEP 6 — Mechanism of the silent gate: the frozen estimate (pre-registration)

**Written 6 October 2026, before any run of this study.** Author: Sushanth. Second reader required
before the dev run: Tanay.

## 1 · Background (what is already known, and how)

- Stage A (pre-registered, held-out): under sustained `imu_dropout` the L6 score, σ and quantile medians
  equal their clean values while the alarm rate falls from ≈6 % to ≈0 %. Its three hypotheses were all
  rejected (H-none).
- **Exploratory** probe of 6 October (`EXPLORATORY_MECHANISM_2026-10-06/`, dev seeds 20260731–35): the
  silence persists with L8's integrity path neutralised; the estimated speed has zero within-run variance
  after onset; the score is 3.689 ± 0.009 clean and shifts down by ≈0.01 under the fault.

**Disclosure:** five dev seeds have been seen for the arms `clean`, `dropout`, `dropout_noL8`. The arms
`stuck` and `stuck_noise` have never been run on any seed.

## 2 · Hypotheses

| id | statement | prediction |
|---|---|---|
| **H-indep** | The silence does not depend on L8 stopping the vehicle | `dropout_noL8` alarm rate is suppressed like `dropout` |
| **H-freeze** | The silence follows from the estimator receiving no new information on the lost channels — not from messages being absent | `stuck` (values frozen but still delivered, L1 healthy) is suppressed like `dropout` |
| **H-noise** | The downward score shift is the absence of measurement noise on those channels | `stuck_noise` (frozen value + fresh noise at the declared σ) restores the alarm rate to the clean level, although the estimate is still wrong |

## 3 · Design

| arm | fault from tick 200 to end | L8 integrity path |
|---|---|---|
| `clean` | none | normal |
| `dropout` | `imu_dropout` (as E21) | normal |
| `dropout_noL8` | `imu_dropout` | thresholds raised to 10⁹ via the `on_assembled` benchmark hook |
| `stuck` | `STUCK_AT` on speed **and** lateral acceleration | normal |
| `stuck_noise` | as `stuck`, plus fresh Gaussian noise each tick at the declared channel σ (benchmark-level injector subclass) | normal |

- 30 runs per arm, 3,400 ticks, policy `var/policy/synthetic.pt`, `demo_speed_assist` off.
- **Dev seeds** `20260731 + i`, i = 0…29. **Held-out seeds** `20270101 + i`, i = 0…29 — a new block,
  because `20261201 + i` has been used by Stages A and C1b.
- Evaluation window: ticks 400–3399. Threshold: frozen v3 P1 = 3.7024.
- No change under `src/`. Runner refuses to start on a dirty working tree.

## 4 · Measurements

Per run: alarm rate `P(score > 3.7024)`; score p50, p95, p99 and standard deviation; within-run standard
deviation of the estimated speed; mean `|estimated speed − true speed|`; share of ticks per L8 state.

Per arm: **paired ratio** `alarm(arm, seed) / alarm(clean, seed)`, summarised as the median over seeds
with a 95 % bootstrap interval (2,000 resamples of seeds). A clean alarm rate of 0 for a seed excludes
that seed from ratios and is reported.

## 5 · Decision rules (fixed now)

"Suppressed" means: median ratio ≤ 0.25 **and** upper interval bound < 0.50.
"Restored" means: median ratio within [0.50, 2.00] **and** lower interval bound > 0.25.

| hypothesis | supported if | refuted if |
|---|---|---|
| H-indep | `dropout_noL8` suppressed | its median ratio > 0.50 |
| H-freeze | `stuck` suppressed | its median ratio > 0.50 |
| H-noise | `stuck` suppressed **and** `stuck_noise` restored | `stuck_noise` suppressed |

Anything else is **inconclusive** and reported as such. A hypothesis counts as **confirmed** only if
supported on dev **and** on held-out. Held-out is run once, after the dev verdict is committed, with no
change to code or rules.

## 6 · Descriptive outputs (no pass rule)

- Score histogram per arm (the alarm-rate figure is never to be shown without it).
- Mean `|estimated − true speed|` per arm.
- L1 detection per arm (E21 `health` rule), to place `stuck` in the L1-vs-gate table.

## 7 · What each outcome means for the paper

| outcome | consequence |
|---|---|
| H-indep + H-freeze + H-noise confirmed | Mechanism: the gate's clean alarms are driven by measurement noise passing through the shared estimate; remove the information and the gate goes quiet whether or not messages arrive. General statement about estimate-fed gates |
| H-freeze confirmed, H-noise refuted | Silence is tied to the frozen estimate but not to noise; report the freeze, leave the direction of the shift open |
| H-freeze refuted | Silence is specific to missing messages; the structural claim is withdrawn |
| H-indep refuted | G1 is an artefact of L8's stop and is withdrawn as a finding |

## 8 · Deviations

Any deviation is recorded in `amendment.md` with its reason before the affected run.
