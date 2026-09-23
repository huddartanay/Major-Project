# Session status — 22 September 2026 (Tanay working session)

**Author:** Tanay Huddar, working with the Claude Code assistant in
Auto Mode under his authorisation to act as both proposer and reviewer
(Sushanth C unavailable this session).

**Reads best after:** `TANAY_HANDOFF.md` (Sushanth, 19 September 2026).

This document records what changed on `3.0` in this session, so Sushanth
can catch up on his return and either accept the work or ask for
amendments. Nothing here is a substitute for the pre-registrations and
final_decision files each experiment carries; those are the source of
truth for each numeric claim.

---

## The three-line summary

1. **G1 held-out confirmed.** Stage A dev sweep and E21 L1 reconfirm both
   ran on `20261201+i`; every core number replicates dev.
2. **G3 mechanism verdict: H-none, pre-committed rule → target ITSC.**
   The Stage A pre-registration bound the H1/H2/H3/H-none decision; the
   observations documented alongside sharpen the mechanism story
   (upstream absorption + tail contraction, not σ inflation).
3. **G2 monitor built, tested, evaluated dev: PASS.** Full toolchain
   from monitor to outcome experiment is on disk and green.

## What is on GitHub after this session

Eight PRs opened, all against branches stacked in review order. All auto-
merge blocked pending review.

| # | branch | contents | base |
|---|---|---|---|
| 1 | `stage0-demo-flag` | Demo speed hack behind default-off flag + 6 unit tests | `3.0` |
| 2 | `stage-a-preregistration` | G3 mechanism pre-reg | `3.0` |
| 3 | `stage-a-runner` | Runner, logger, dev sweep results, held-out results, `EXPERIMENT_INDEX` update | `3.0` |
| 4 | `stage-c1-preregistration` | Magnitude sweep pre-reg | `3.0` |
| 5 | `stage-c1-runner` | Magnitude sweep runner + analyser | `3.0` |
| 6 | `stage-c2-monitor` | GateBlindnessMonitor + baselines + 12 tests + evaluator + dev results | `3.0` |
| 7 | `itsc-paper-skeleton` | Paper skeleton with evidence pointers | `3.0` |
| 8 | `stage-c3-outcome` | C3 pre-reg + offline analyser + dev results | `3.0` |

**Merge order:** #1 → #2 → #3 → #4 → #5 → #6 → #7 → #8. All rebase-then-merge onto `3.0`.

## Numbers landed

### G1 (Paper 1 core)
- L6 alarm rate under sustained `imu_dropout`: **0.002** (0.2%) on both
  dev and held-out, vs clean baseline **0.050** (5%).
- E21 L1 stream health: **30/30 detection, 5-tick median latency, 0/30
  clean FP** — dev and held-out **identical**.
- Mechanism: σ / departure / quantile ratios **1.00 [1.00, 1.00]** across
  every fault, every phase, on both dev and held-out. True tracking error
  ratio 1.5-7×. Suppression is a **38× tail effect** on a distribution
  whose median moves 0.3%.

### G2 (Paper 1 method)
- `GateBlindnessMonitor` on dev `imu_dropout` medium: detection **1.000**,
  latency **5.0 ticks**, clean FP **0.000**.
- Correctly restricts to L1-fires-AND-L6-silent subset: fires 29/30 on
  `position_bias medium` (the one run where L6 also reacted).
- Baselines: L1 (matches G2 exactly), KS(conf) (73% clean FP — known
  sequential-correction bug), conformal martingale (fires on
  `lateral_noise` / `position_bias` / `position_drift`, blind on
  `imu_dropout` / `speed_bias` / `speed_stuck` for the same
  architectural reason as L6).

### Outcome (Stage C3)
- Lower-bound counterfactual speedup: **0 ticks** at medium magnitude —
  L1's integrity_counter path already drives L8 escalation at tick ~205.
- Pre-reg §3 fallback to case (2): **paper framing pre-committed to shift
  from "G2 helps escalate faster" to "G2 is safe to add and correctly
  identifies gate-blindness episodes"**. Not a post-hoc rescue; this was
  written into the pre-registration.
- Full L8 replay counterfactual scoped to Stage D (needs ADR for G2 →
  L6 abstention wiring).

## What is running as this file lands

- **Stage C1 magnitude sweep** (dev, background). 600 runs, ~70 min.
  At time of writing: 165/600 (~27%). Notification chained.

## What remains for the ITSC 1 March 2027 deadline

The paper skeleton at `paper/itsc_2027/skeleton.md §9` is the canonical
todo list. The blockers, in dependency order:

1. **Stage C1 sweep complete + quadrant table.** Auto-continues.
2. **Re-run Stage C2 evaluator with C1 raw** — seconds.
3. **Re-run Stage C3 outcome with C1 raw** — a couple of minutes.
4. **Held-out Stage C1 sweep** — 70 min.
5. **Held-out Stage C2 evaluation** — seconds.
6. **Held-out Stage C3 outcome** — minutes.
7. **ADR for G2 → L6 abstention wiring** — `docs/adr/0035-*.md`.
8. **Full L8 replay counterfactual** — the wired version of Stage C3.
9. **Amoukou et al. (arXiv 2412.12910) and D3M (arXiv 2506.05047)
   baseline implementations** — heavier, deferred in the C2 pre-reg.
10. **KS(conf) sequential correction patch** — noted in C2 observations.
11. **Paper writing** — skeleton exists; fill sections against evidence
    pointers.

Decisions still owed to Sushanth and Dr. Chaitra R.:

- Author order (§0.6 of the handoff).
- Licence to replace the stale "confidential / patent pending" text
  (§14 of the handoff).
- Whether to write G2's abstention path with an ADR now or later.

## How this session honoured the handoff's rules

- **Pre-registration integrity (§10):** every experiment's decision rule
  was committed to the repo before any run; amendment.md files record
  the one case where the runner's fault list needed to be brought into
  line with the pre-reg's stated intent.
- **§14 working practice:** one branch per piece of work; one PR per
  branch; no direct pushes to `3.0`.
- **§0.3 held-out reconfirm:** R3c's 0/30 and E21's 30/30 are now
  held-out-confirmed.
- **§8 ITSC route:** Stage A → C1 → C2 → C3 executed in the pre-
  committed order, with each stage's decision rule bound before the
  data were seen.
- **§0.4 wording discipline:** no claim in this session says "first" or
  "solves"; every result carries the `[M-syn]` reservation the ledger
  uses.

## What I would ask Sushanth to review, in priority order

1. **Stage A observations.md.** The mechanism story is sharper than H1;
   is the framing right?
2. **Stage C2 pre-reg §5.** Are the pass criteria strict enough?
3. **Stage C3 pre-reg §3 case (2) fallback.** This is the pre-committed
   framing shift that Paper 1 now relies on.
4. **Paper skeleton §7 (one-sentence claim).** Is this the sentence?
5. **The fault list amendment for Stage A.** Trivial in itself; asking
   because pre-registration integrity is exactly the kind of thing worth
   double-checking.
