# Review of Tanay's Stage 0 – C3 work (6 October 2026)

Reviewer: Sushanth (with Claude). Branches reviewed: `tanay/stage0-demo-flag` (`f920019`) and
`tanay/stage-c1b-sensor-loss` (`ba73d0a`), which together contain all ten PRs.

## Verdict

**Merge the code and data. Do not accept the claims as written.**
The engineering is sound and isolated; three statements in `PROTOTYPE_STATE.md` and the paper skeleton
overstate what the data show and must be corrected in the same merge.

## What was checked

| check | result |
|---|---|
| `src/astra/` changed? | **No** — zero files on either branch |
| Trial merge `3.0` ← stage0 ← c1b | **Clean, no conflicts** |
| Full suite on the merged result | **3,075 passed**, 3 xfailed, 1 skipped (1 failure is a path artefact of the review worktree, not a defect) |
| Tanay's 36 new tests | All pass |
| Stage 0 change | Correct: demo speed reset behind `demo_speed_assist=False`; only the two demo entry points pass `True`; an AST test enforces it |
| Held-out result files vs the numbers quoted | Match (G1 0.00 %; L1 30/30, 5 ticks; C1b NARROW; C2 1.000 / 5 / 0.000; C3 0 and 1,181) |
| Stage 0 CI changes | Formatting only in my benchmark files; lint/mypy relaxed for research folders, `src/` still strict |

## Findings

### Must fix before the claims are used

1. **G2 never outperforms L1-only — by construction.** `GateBlindnessMonitor` fires on
   "L1 unhealthy AND gate silent" for 5 ticks; `L1OnlyMonitor` fires on "L1 unhealthy" for 5 ticks. On
   held-out data they are identical or G2 is slower: 5.0/5.0 (p=1.00), 8.0/8.0 (0.75), **18.5 vs 17.5**
   (0.50), 220.5/220.5 (0.25); detection 1.000 for both everywhere. "Beats label-free baselines" is true
   only against KS(conf) and the martingale.
2. **The KS(conf) comparison is not valid.** Its 0.73–0.83 clean false-alarm rate comes from an
   implementation defect (acknowledged in `observations.md`). It cannot be cited as a baseline G2 beats
   until fixed. Amoukou and D3M are not implemented.
3. **The 1,181–1,640-tick speed-up is against L8's integrity counter, not against L1-only**, and it is a
   median over only the runs that escalated: at p=0.25 held-out, **53 % of runs never escalate at all**.
   Report it as censored, and add the L1-only counterfactual beside it.
4. **G2 also fires where the gate is working** (p=0.50 and 0.75, cell B), so it does not separate
   "gate blind" from "gate reacting".

### Pre-registration integrity

5. **Stage C2:** pre-registration and results are in the **same commit** (`a42c1a7`). **Stage C3:** the
   pre-registration precedes results by **one minute**, on data already on disk. Neither is a credible
   prior commitment. Label C2 and C3 **exploratory**, or re-register and confirm on fresh seeds.
6. **C2 ran before C1's verdict** (22 Sept 20:16 vs 23 Sept 10:05) although C1's rule decided whether C2
   should proceed.
7. **No second human read any pre-registration** before its run (handoff §9 required it).
8. Stage A, C1 and C1b pre-registrations do precede their results. Good.

### Smaller

9. Two L1 definitions disagree at p=0.25: 12–14/30 (E21 `health` rule in C1b) vs 30/30 (`L1OnlyMonitor`
   in C2). It does not change the NARROW verdict but must be reconciled.
10. C1: `lateral_noise` never ran (crash); L1 detection reconstructed from `integrity_counter > 0`.
11. Stage A's "tail effect / absorption" explanation is an untested observation — keep it labelled so.
12. PR #10 targets `main`; it must target `3.0`.

### Urgent, not about the science

13. **The leaked commit `e3ee301` is still publicly reachable** (HTTP 200 on a public repository). It
    contains Tanay's internship offer letter and other private files. Tanay should contact GitHub Support
    today to purge it, and treat the letter's contents as exposed.

## How to merge

1. Retarget PR #10 to `3.0`.
2. Merge **#1** (`stage0-demo-flag`), then **#10** (`stage-c1b-sensor-loss`). Verified clean.
3. Close #2–#9 as superseded (their commits are contained in #10).
4. In the same merge or immediately after, correct:
   - `PROTOTYPE_STATE.md` §1 item 2 and the skeleton's one-sentence claim: G2 **matches** L1-only;
   - item 3: add the censoring and the L1-only comparison;
   - mark C2 and C3 exploratory.

## What this means for the paper

- **G1 stands**, held-out, scoped to **total** sensor loss.
- **G3:** H1 refuted; no confirmed mechanism.
- **G2:** not yet a contribution. Stage D must compare **no monitor / act on L1 / act on G2**; G2 counts
  only if it beats "act on L1" on a pre-registered outcome.
