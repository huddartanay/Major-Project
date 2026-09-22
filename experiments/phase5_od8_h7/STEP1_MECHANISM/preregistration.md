# STEP 1 · Mechanism — Pre-Registration (Stage A of the 19 Sep 2026 handoff)

**Written 22 September 2026, before any run of this experiment.** Nothing below may be revised after
inspecting any tick of the output. Any change requires a dated `amendment.md` alongside this file and
a fresh commit; existing raw results become historical evidence and are not re-analysed under the
amended rule.

Owner (drafting): Tanay. Reviewer (must approve before any run): Sushanth.

---

## 1 · Why this experiment exists

E18-R3c established the fact of G1: under a sustained `imu_dropout`, the L6 conformal gate alarms on
~0.2 % of ticks (0/30 runs detected) — quieter than the ~5 % clean baseline (E18-R3, 30/30 in band).
E21 established that an independent layer (L1 sensor health) catches the same fault in 5 ticks on
30/30 runs with 0/30 clean false alarms. The gate's blind spot is therefore not a calibration issue,
not a shortage of information (L1 sees it at once), and not a threshold error.

**What none of those experiments answered: why does the gate go silent?** The score is
`log(score) = log(|departure|) − log(σ)` where σ is the estimator's control-dimension variance and
`departure` is the projected proposal–prediction gap. Three mutually exclusive mechanisms could hold
the alarm rate below the clean baseline:

- **H1 · σ inflates.** After onset the estimator becomes less certain (the IMU is delivering
  nothing), so σ grows, the ratio shrinks, and the score drops below the frozen quantile even when
  the proposal has genuinely diverged from the prediction.
- **H2 · departure collapses.** The estimator's prediction chases the (still passing) proposals, so
  their difference shrinks and the score drops directly. A common-mode failure of the estimator and
  the proposer.
- **H3 · threshold moves.** The context classifier drifts under the fault, or the shift detector
  lowers the threshold (`gate.py:203`), making the quantile close over the score from above.

Stage A produces the evidence that distinguishes these. Its verdict decides whether we submit to IV
2027 (H1 confirmed → Stage B → 15 Nov deadline) or skip IV and target ITSC alone (any other outcome
→ G1 stands; the mechanism remains an open thread).

## 2 · Design at a glance

**Scope.** Same six faults, seeds and window as R3c; the only additions are the per-tick logger and
a matched **clean arm**. No architecture change, no threshold recomputation. Frozen v3 threshold
`P1 = 3.7024` as in R3, R3b, R3c.

- Faults: `imu_dropout` (primary), `imu_bias`, `imu_noise_burst`, `position_bias`, `position_drift`,
  `speed_bias` — matches R3c's set. Severity `medium`. Fault active from tick 200 through the last
  tick of the run (sustained; identical to R3c's injector).
- Ticks per run: 3,400 (as R3c). 20 Hz plant.
- Dev seeds: `20260731 + i` for `i` in `range(30)` — used for the primary analysis and the H1/H2/H3
  decision.
- Held-out seeds: `20261201 + i` for `i` in `range(30)` — run **once**, after the dev analysis is
  frozen in `final_decision.md`, with **zero source or configuration changes**. In the same run,
  R3c's headline (`imu_dropout` sustained alarm rate ≤ clean baseline, 0/30 runs detected) and
  E21's headline (L1 catches `imu_dropout` on 30/30 runs, latency ≈ 5 ticks) are re-computed on the
  held-out seeds so the G1 core numbers become held-out-confirmed as well (handoff §0.3).
- Clean arm: 30 runs at the same dev seeds, no fault. Provides the baseline distributions of σ,
  `departure`, `score`, and `quantile` that H1/H2/H3 are compared against.
- Cost: 30 dev + 30 clean = 60 runs × 3,400 ticks per fault × 6 faults + 30 held-out × 6 faults =
  approximately 630 runs. R3c cost ~50 min for 180 runs; expect ~3–4 h wall time.

## 3 · The one addition to the pipeline

A tick-level logger, `benchmarks/mechanism_logger.py`, is added under `benchmarks/` — that is,
outside `src/astra/` per handoff §14 ("Anything in `src/` that changes behaviour needs an ADR").
It records, per tick, from the `DecisionRecord` and the plant:

1. From the L6 gate `GateVerdict.evidence` (source of truth: `gate.py:325`):
   `non_conformity_score`, `departure`, `sigma`, `conformal_quantile`, `effective_epsilon`,
   `mmd_discrepancy`, `calibration_samples`.
2. From `record.failsafe`: `state.value`, `ood_counter`, `integrity_counter` (names verified against
   `l8_failsafe/machine.py` at run time; the logger is written to fail loudly if a field disappears
   rather than silently emit zeros).
3. From the plant (via `on_assembled`, already wired for the dashboard): the true lateral position,
   true speed, and true lateral acceleration — the ground-truth tracking error the L6 gate cannot
   see at runtime, needed to distinguish H1 (σ inflates while true error grows) from H2 (true error
   itself shrinks because the estimator has captured the proposer).
4. Provenance: seed, fault kind, fault onset tick, threshold, git SHA of the run.

The logger writes one JSON-lines file per run under
`experiments/phase5_od8_h7/STEP1_MECHANISM/raw_results/<seed>_<fault>.jsonl`. This puts none of the
Stage 0 machinery at risk: the logger observes, it does not steer.

## 4 · Hypotheses — mutually exclusive, direction genuinely unknown

Let `t0 = 200` be the fault onset tick. Define, per run, per fault, for each of R3c's four phases
`P200-399, P400-999, P1000-1999, P2000-3399`:

- `σ_ratio(P) = median_{tick ∈ P} σ / median_{tick ∈ clean-run [200,3399]} σ` (matched seed)
- `dep_ratio(P) = median |departure| under fault / median |departure| clean` (matched seed)
- `q_ratio(P) = median conformal_quantile under fault / median clean` (matched seed)
- `err_ratio(P) = median true tracking error under fault / median clean` (matched seed)

Ratios are computed per run, then aggregated across the 30 dev seeds as the median and a 95 %
Clopper–Pearson-adjacent bootstrap CI (2,000 resamples of runs, not of ticks; ticks within a run are
autocorrelated and a tick-level bootstrap would understate variance — an error the ledger already
records in Phase 2 monitorability).

**H1 · σ inflates** is supported if, for `imu_dropout`, in phases `P400-999` and later:
- `σ_ratio` ≥ **1.5×** (lower CI bound above 1.5), and
- `dep_ratio` ∈ **[0.75, 1.5]** (95 % CI overlaps 1.0), and
- `q_ratio` ∈ **[0.75, 1.25]** (95 % CI overlaps 1.0), and
- `err_ratio` ≥ **1.5×** (the true error grows even though `departure` does not — the specific
  fingerprint of the estimator absorbing the fault while the proposer continues correctly).

**H2 · departure collapses** is supported if, in the same phases:
- `dep_ratio` ≤ **0.5×** (upper CI bound below 0.5), and
- `σ_ratio` ∈ **[0.75, 1.5]** (95 % CI overlaps 1.0).

**H3 · threshold moves** is supported if, in the same phases:
- `q_ratio` ≥ **1.5×** (lower CI bound above 1.5), and
- `σ_ratio` and `dep_ratio` both in `[0.75, 1.5]`.

**H-none.** Any other pattern — including mixed evidence (e.g. σ grows *and* departure shrinks; a
combination of two mechanisms; H1 for one fault but not another) — reads as **no single mechanism
supported**. In that case G1 stands, but the IV paper is not written on this evidence: we skip IV,
investigate further under Stage C, and target ITSC alone. This is the pre-committed conservative
call, made now so a post-hoc pattern-match cannot rescue the deadline.

Rationale for the 1.5× / 0.5× / [0.75, 1.5] thresholds: `log(score) = log(|dep|) − log(σ)`, so a
score halving corresponds to `σ` doubling or `|dep|` halving; 1.5× shifts the score by ≈0.4 nats,
which is comparable to the frozen v3 threshold's headroom over the median clean score in E18-R3.
These are not tuned against the eventual data — the numerics are pinned to R3's already-committed
distributions.

## 5 · Primary decision, in one sentence

**H1 confirmed on the dev seeds and reproduced on the held-out seeds → go IV (Stage B).**

**Any other outcome → skip IV, keep G1, investigate in Stage C, target ITSC (Stage D).**

## 6 · Falsifiability, and what would refute this design

The pre-registration is falsifiable in two directions: (a) any one of the four ratio bounds for H1
fails on `imu_dropout`, or (b) the held-out replication contradicts the dev outcome (the pre-reg
holds itself to the same held-out standard it demands of Paper 1). It is falsifiable **regardless**
of R3c's result — R3c said the gate goes silent; this experiment says nothing about whether we can
say **why** unless the fingerprint above matches.

## 7 · What Stage A cannot establish

The proposition in §8 of the handoff — a formal statement that "if σ grows by factor k, the alarm
probability at a fixed departure distribution falls accordingly" — is a **theorem**, not a
measurement. Stage A produces evidence consistent (or not) with that theorem's premise; the theorem
itself is proved and stated in Stage B. Stage A also cannot address adversarial faults (G5), semantic
errors (G6), or the label-free detection method (G2). Those are ITSC-side (Stage C) and later.

## 8 · Integrity checklist (identical to R3c, extended for the logger)

- Frozen threshold `3.7024` hard-coded; **no quantile is recomputed** in this module.
- Delivered-signal check on every run: the injector must actually change the reading it targets
  (per `test_fault_injection.py`).
- Per-tick series stored raw; analysis lives only in `processed_results/` and reads the raw files.
- Seed, policy weights hash, and `git rev-parse HEAD` recorded in every JSONL header.
- Logger asserts every evidence field it names exists in the record at construction; if a field is
  renamed under `src/astra/`, the logger fails fast rather than emit a silent zero.
- Stage 0's `demo_speed_assist=False` (default) is asserted at the top of the runner; a future
  regression that reintroduces the demo hack surfaces here as a loud failure, not a silent drift.
- The runner script is committed **before** the first run and its git SHA is one of the recorded
  provenance fields.

## 9 · What lands in `final_decision.md`

- The per-fault, per-phase tables of the four ratios with medians and 95 % CIs.
- The H1 / H2 / H3 / H-none verdict, quoting the pre-committed rule verbatim from this file.
- The held-out replication table (same ratios, same tests, held-out seeds).
- The held-out re-confirmation of R3c's alarm rate and E21's L1 detection (per §0.3).
- A single sentence pointing to Stage B (IV) or Stage C (ITSC) per §5.

## 10 · Reviewer notes for Sushanth

Please read this before any run. Specifically flag:
1. The 1.5× / 0.5× / [0.75, 1.5] thresholds in §4 — do these carry the shift you expect from
   `log(score) = log(|dep|) − log(σ)`?
2. The clean-arm construction in §2 (matched seeds, no fault). Is a paired-seed comparison what you
   want, or an unpaired one?
3. The held-out plan in §2. R3c's 0/30 and E21's 30/30 fold into the same held-out sweep so we
   spend one held-out budget on both.
4. Whether `imu_bias`, `imu_noise_burst`, `speed_bias` add anything given only `imu_dropout`,
   `position_bias`, `position_drift` are the ones the paper's proposition addresses.

Approval to run: reply on the PR that opens this file with "approved for run". No run happens until
that appears in the PR history — the pre-registration is otherwise not pre.
