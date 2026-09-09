# Phase 2 — Monitorability: final decision

**9 September 2026** · 24 (fault × phase) cells · 180 recorded runs × 3,400 ticks · zero new compute
**Pre-registered in `preregistration.md`, committed at `db090f2` before any value of M was computed.**

---

# VERDICT: M IS WEAK — and it is blind in the one case that matters

**The pre-registered primary test passed, and the pre-registered primary test was wrong.**
**The identity-free reading puts M in the "weak" band, and M mispredicts `imu_dropout` — the
sustained blind spot the whole programme is about.**

---

## 1 · What was measured

| test | ρ | p | n |
|---|--:|--:|--:|
| **PRIMARY** — M vs alarm rate, as pre-registered | **0.895** | <0.0001 | 24 |
| incumbent — `D_s` vs alarm rate | 0.077 | 0.7192 | 24 |
| conservative — per-fault medians | 1.000 | 0.0023 | 6 |
| **identity-free** — within below-threshold cells | **0.654** | 0.0113 | 15 |
| identity-free — within above-threshold cells | 0.554 | 0.1354 | 9 |

Clean baseline: μ = 3.5357, σ_between = 0.1542, over 60 runs. Threshold 3.7024 (v3, frozen).

## 2 · Why the primary test is withdrawn as the headline

M is a monotone transform of the cell median. The alarm rate is `P(score > threshold)`. Therefore

    median > threshold   ⟺   alarm rate > 0.5

is an **identity**, not a finding. The threshold sits at M = 1.081, and all 24 cells obey the
identity exactly: the 9 cells above it all have alarm > 0.5, the 15 below all have alarm < 0.5. That
split alone forces a large rank correlation before any evidence is considered.

**This is a defect in the frozen definition, not in the data.** It was mine, it was pre-registered,
and it survives into the record. The correction runs the same correlation *within* each side, where
the identity constrains nothing. That is the part of ρ = 0.895 which is actually empirical, and it
is **ρ = 0.654 (p = 0.0113)** on the 15 below-threshold cells — the "weak" band under the frozen
rule, and close to the ρ ≈ 0.5–0.75 recorded as the prediction in §8 of the pre-registration.

The above-threshold side is uninformative in either direction: n = 9, and 6 of those cells are
saturated at alarm = 1.000, so there is a ceiling and nothing to order.

**The correction moves the result from "passes" to "weak". It is reported because it goes that
direction, not despite it.**

## 3 · The finding that actually matters

M is a **location** statistic. It measures how far the score's centre has moved from the clean
baseline. It has no dispersion term, and `imu_dropout` is a dispersion failure:

| phase | M | alarm rate | clean baseline FAR | |
|---|--:|--:|--:|---|
| P-early | 0.94 | 0.004 | ~0.05 | 13× quieter than clean |
| P-mid | 0.93 | 0.002 | ~0.05 | **28× quieter than clean** |
| P-late | 0.93 | 0.002 | ~0.05 | 25× quieter than clean |
| P-tail | 0.93 | 0.002 | ~0.05 | 24× quieter than clean |

M reports `imu_dropout` as **mildly elevated above the clean mean** in every phase. The monitor's
actual behaviour is to fall **almost silent** — a factor of 25 below its own clean false-alarm rate,
sustained for 160 seconds on all 30 seeds.

**M gets the direction right and the consequence exactly backwards.** A sustained IMU failure does
not shift the score much; it *tightens* it, and a tighter distribution crosses a fixed threshold
less often even when its centre has moved slightly toward it. A location-only metric cannot see
that, and `imu_dropout` is precisely the fault E18-R3c identified as the safety case.

So M would have predicted "this fault is marginally more visible than clean" for the one fault that
is, operationally, invisible.

## 4 · The incumbent is confirmed dead

`D_s` against alarm rate: **ρ = 0.077, p = 0.7192**. No predictive power whatsoever.

This is not subject to the identity confound — `D_s` is computed on whole runs from an independent
experiment (E17) and has no algebraic relationship to the alarm rate. It reinforces E18's finding
from an additional direction: `D_s` was measured there as *anti*-correlated with detection
(ρ = −0.480, p = 0.0088); here it is simply uncorrelated. Either way, **discriminability does not
tell you whether a fault will be detected.**

`D_s` also cannot represent phase at all — it is one number per fault, so the four phases of
`position_drift` (alarm 0.068 → 0.182 → 0.780 → 1.000) all carry the same `D_s` of 0.997. That
alone disqualifies it as an operational predictor, independent of the correlation.

## 5 · What this licenses

- **M in its current form must not be claimed as a design justification for ASTRA 2.0.** It is weak,
  and it is wrong on the safety case. E18-R3 anticipated that Phase 2 might "delete a large part of
  the ASTRA 2.0 proposal"; it deletes the location-only formulation.
- **The phase-aware framing survives and is vindicated.** `position_drift` moves 0.068 → 1.000 across
  phases at a constant `D_s`; any per-fault metric is structurally incapable of representing that.
- **A dispersion term is the named next step**, not a speculative improvement. The failure is
  specific and diagnosed: M needs to represent the *width* of the score distribution, not only its
  centre, because suppression is a width effect.

## 6 · What this does not license

- Nothing about P2 or P3; every run is P1.
- Nothing about severities other than `medium`.
- Nothing causal. Correlation across cells says M is a usable-but-weak predictor on this plant, not
  that low monitorability causes missed detection.
- No claim that a dispersion-augmented M *would* work. That is a hypothesis this experiment
  generated and did not test. Testing it requires a new pre-registration, because the definition
  would be chosen after seeing these results.
- `[M-syn]` throughout. `[M-ext]` remains 0 of 30.
- The 24 cells are not independent — four phases share a fault and the same 30 seeds appear in every
  cell — so the primary p-value is optimistic. The conservative per-fault check (ρ = 1.000, n = 6)
  is badly underpowered and is a direction, not a test.

## 7 · The prediction, scored

§8 of the pre-registration recorded: *"Expectation: M passes at the 'weak' level, ρ ≈ 0.5–0.75. I
expect it to beat `D_s` … and to fall short of 0.9 because score level and threshold-crossing rate
come apart whenever the baseline drifts."*

**Identity-free ρ = 0.654 — inside the predicted band.** It did beat `D_s` (0.077). The stated reason
for falling short of 0.9 was right in mechanism but understated in consequence: score level and
crossing rate do not merely "come apart", they invert for `imu_dropout`.

The pre-registration did not anticipate the identity confound. That is the substantive miss.

## 8 · Next

1. **E19 / H7 monitor placement** is now the next new-compute experiment, and Phase 2 has given it a
   yardstick: any placement is scored on detection, with M reported as a weak covariate and never as
   the outcome.
2. **A dispersion-augmented monitorability metric**, pre-registered fresh before it is computed.
3. **E18-R4 (P3)** remains optional, wanted only if E19 needs a second policy.
