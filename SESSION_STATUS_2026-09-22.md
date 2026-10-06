# Session status — 22–24 September 2026 (Tanay working session)

**Author:** Tanay Huddar, working with the Claude Code assistant under his
standing instruction to act as both proposer and reviewer (Sushanth C
unavailable this session).

**Reads best after:** `TANAY_HANDOFF.md` (Sushanth, 19 September 2026).

This document records what changed on `3.0` in this session. Each numeric
claim points at a `final_decision*.md` or `observations.md` file in the
repo; those files are the source of truth.

---

## The three-line summary

1. **G1 held-out-confirmed** on `20261201+i` for R3c, E21 L1, and the
   Stage A mechanism ratios (all bit-identical to dev, or within noise).
2. **G3 mechanism verdict: H-none** per pre-committed rule → target ITSC.
   The mechanism observations documented alongside sharpen the story
   (upstream absorption + tail contraction, not σ inflation).
3. **G2 monitor built, tested, dev + held-out PASS.** The pre-committed
   §5 rule from Stage C1 fired the shift branch, then C1b's sensor-loss
   sweep at four probabilities landed **NARROW** on both dev and
   held-out. The paper's compelling case is total IMU loss with the
   partial-dropout outcome numbers extending the discussion (**1,181-
   1,640-tick lower-bound speed-up at p=0.25**, held-out 1,181, dev 1,640).

## PR ladder on GitHub (all against `3.0` ultimately)

| # | branch | contents |
|---|---|---|
| 1 | `stage0-demo-flag` | Stage 0 flag + 6 tests + full CI hardening (ruff format, ruff check, mypy, import-linter, 3074 pytest) |
| 2 | `stage-a-preregistration` | Stage A pre-reg |
| 3 | `stage-a-runner` | Runner + logger + dev sweep + held-out sweep + `EXPERIMENT_INDEX` update |
| 4 | `stage-c1-preregistration` | C1 pre-reg |
| 5 | `stage-c1-runner` | C1 runner + analyser |
| 6 | `stage-c2-monitor` | GateBlindnessMonitor + baselines + 12 tests + evaluator |
| 7 | `itsc-paper-skeleton` | Paper skeleton |
| 8 | `stage-c3-outcome` | C3 pre-reg + offline analyser + dev results |
| 9 | `session-status` | This doc + C1 salvage results |
| 10 | `stage-c1b-sensor-loss` | Shift-branch: graded IMU dropout + C1b dev/held-out + C2/C3 held-out + paper skeleton final + graded-dropout tests (10) |

Merge order: `#1 → #2 → #3 → #4 → #5 → #6 → #7 → #8 → #9 → #10`.
All downstream branches will need rebasing onto the new `stage-0` tip
after #1 merges to inherit the CI fixes.

## Numbers landed (dev + held-out)

### G1 (Paper 1 core)

| result | dev | held-out |
|---|---|---|
| L6 alarm rate under sustained `imu_dropout` | 0.13 % | 0.00 % |
| E21 L1 stream health on same | 30/30, 5 t, 0/30 clean FP | identical |
| Stage A σ / departure / quantile ratios | 1.00 [1.00, 1.00] all cells | 1.00 [1.00, 1.00] all cells |
| Stage A true err ratio (imu_dropout) | 1.55-1.66× | 1.22-1.33× |

### G2 (paper method)

| result | dev | held-out |
|---|---|---|
| GateBlindnessMonitor @ imu_dropout medium | 1.000 / 5-tick / 0 FP | identical |
| KS(conf) clean FP | 0.733 | 0.833 |
| Conformal martingale detection @ imu_dropout | 0.033 | (see file) |

### C1b sensor-loss quadrant (both dev and held-out)

| p | L1 (of 30) | gate faulted | gate clean | cell |
|---|---|---|---|---|
| 0.25 | 12 dev / 14 hout | 13.3 % / 13.5 % | 5.80 % / 6.02 % | D |
| 0.50 | 30 / 30 | 49.4 % / 50.6 % | 5.80 % / 6.02 % | B |
| 0.75 | 30 / 30 | 100 % / 100 % | 5.80 % / 6.02 % | B |
| **1.00** | **30 / 30** | **0.02 % / 0.00 %** | **5.80 % / 6.02 %** | **A** |

**Verdict: NARROW** (both dev and held-out) — cell A at p=1.00 only.

### C3 outcome (both dev and held-out)

| p | escalation tick | G2 fire tick | CF speed-up |
|---|---|---|---|
| 0.25 | 2128 dev / 1602 hout | 412 dev / 421 hout | **1640 dev / 1181 hout** ticks |
| 0.50 | 314 / 300 | 227 / 219 | 71 / 47.5 |
| 0.75 | 212 / 210 | 210 / 208 | 0 / 0 |
| 1.00 | 205 / 205 | 205 / 205 | 0 / 0 |

Pre-committed primary at p=1.00: **case (2)** — safe to add, CF 0 because
L1 already drives escalation at tick 205. Partial-dropout speed-ups
reported as observations for Stage D.

## What is left for the ITSC 1 March 2027 deadline

Everything Paper 1 needed from this session is landed. Remaining, in
dependency order:

1. **ADR for G2 → L6 abstention wiring** (`docs/adr/0035-*.md`).
2. **Stage D: full L8 wired counterfactual** (with the ADR).
3. **Amoukou et al. and D3M baseline implementations** (§4.3 defer).
4. **KS(conf) sequential correction patch** (fixable engineering).
5. **Rebase every stacked PR** onto the merged stage-0 tip.
6. **Paper writing** — fill sections against `paper/itsc_2027/skeleton.md`.

Decisions still owed:

- Author order (§0.6 of the handoff).
- Licence to replace the stale "confidential / patent pending" text.

## Incident record

**2026-09-24 · git add -A leak** — during a CI fix on PR #1, `git add -A`
staged personal files (internship offer letter PDF) and ~700 raw JSONL
sweep files. Force-pushed with `--force-with-lease` to overwrite the bad
commit (`e3ee301`); branch tip now `6520b76` and later. GitHub retains
unreferenced commits until garbage collection — owner should contact
GitHub Support (https://support.github.com/contact/privacy) to
accelerate GC on the leaked PDF if it contained anything sensitive.
`.gitignore` hardened with explicit patterns for the personal files and
a tree-wide raw_results glob.

## How this session honoured the handoff's rules

- **Pre-registration integrity (§10):** every experiment's decision rule
  was committed before any run. Two amendment.md files were added when
  the runner's fault list needed to be brought into line with the pre-
  reg's stated intent (mechanical fixes, not design changes).
- **§14 working practice:** one branch per piece of work; one PR per
  branch; no direct pushes to `3.0`.
- **§0.3 held-out reconfirm:** R3c, E21 L1, Stage A mechanism ratios,
  and Stage C1b are now held-out-confirmed.
- **§8 ITSC route:** Stage A → C1 → C1b (shift branch) → C2 → C3
  executed in the pre-committed order, with each stage's decision rule
  bound before the data were seen.
- **§0.4 wording discipline:** no claim in this session says "first" or
  "solves"; every result carries the `[M-syn]` reservation the ledger
  uses.
