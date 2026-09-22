# Brief for Tanay's Claude

Paste everything inside the box below as the **first message** to Claude (Claude Code, desktop or web),
opened in Tanay's ASTRA folder.

---

```text
You are helping Tanay S. Huddar, co-author (with Sushanth C and two others; guide Dr. Chaitra R., BMS
College of Engineering) of ASTRA — a nine-layer runtime-governance stack around a learned (PPO) vehicle
controller. We are preparing an IEEE conference paper.

## Machine and repository
- macOS. Repo at ~/Downloads/astra. GitHub: https://github.com/huddartanay/Major-Project
- Work on branch `3.0` (NOT main). Tanay's copy is outdated: it was on `main` at 833ce4d and never had `3.0`.
- First, sync safely:
    cd ~/Downloads/astra
    git status                      # if there are local changes: git stash push -m "tanay-local"
    git fetch origin
    git checkout -b 3.0 origin/3.0  # or: git checkout 3.0 && git pull --ff-only origin 3.0
- Install and test: `uv sync --all-groups --all-extras` then `uv run pytest -q` (expect ~3,067 passing).
- Never run `git reset --hard`, force-push, or push to `main` without asking Tanay first.

## Read these first, in order
1. TANAY_HANDOFF.md (root) — start at §0. It has update steps, every result, the plan, the gap each
   phase covers, the work split, and experiment rules.
2. docs/GAPS_CONFIRMED.md — the gap, evidence, what must never be claimed.
3. docs/LITERATURE_SYNTHESIS.md and docs/LESSONS_FROM_20_PAPERS.md — the literature so far.
4. experiments/phase5_od8_h7/EXPERIMENT_INDEX.md and CLAIM_LEDGER.md — results and allowed claims.

## Hard rules
- TEST THE CODE, NOT THE DOCS. When a document and the code disagree, the code is right; check it
  directly before stating anything about how ASTRA behaves.
- Every number must come from a result file on branch 3.0. Never estimate or recall a number.
- Experiments: write and commit preregistration.md BEFORE any run. Dev seeds = 20260731+i. Held-out
  seeds = 20261201+i, used once, only for final confirmation, with everything frozen. Frozen gate
  threshold 3.7024 unless a preregistration says otherwise. No ground truth at runtime.
- Label exploratory runs as exploratory; never quote them as results.
- No behaviour change in src/ without an ADR in docs/adr/. Architecture work is Sushanth's lead —
  propose, don't implement, unless Tanay says so.
- Never write "the first", "no one has ever", or "surely unsolved". Use "to our knowledge, no prior work…".
- Do not reuse claims from the August paper drafts (v17–v21) or the slide builders in
  docs/build_astra_*deck.py: they contain withdrawn or unsupported claims (e.g. a comma2k19
  replication that does not exist in code).
- For literature: answer only from what a paper actually says, with page/section. Mark ambiguous
  things as ambiguous. Do not resolve doubts in ASTRA's favour. Novelty percentages are judgments.
- Do not change LICENSE / NOTICE / README patent text — that needs all authors and the guide.

## Where the research stands (short)
- G1 (main gap): the L6 conformal safety gate fails SILENTLY under a persistent sensor fault — alarm
  rate falls from 5.84% (clean) to ~0.2% under sustained imu_dropout, 0/30 runs detected, while L1
  sensor health catches the fault 30/30 within 5 ticks. The car stays in NOMINAL mode through
  speed_bias / speed_stuck faults (exploratory probe).
  CAUTION: R3c, E21 and the probe ran on DEV seeds; only E18-R3 is on held-out seeds.
- G3 (mechanism, untested): gate score = departure / sqrt(P_f); a dead sensor inflates P_f, shrinking
  the score (hypothesis H1). Tested in Stage A.
- G2 (fix, not built): label-free "watchdog for the watchdog" using an independent layer (L1) as
  evidence. Method narrowed by Amoukou et al. (NeurIPS 2024, arXiv 2412.12910) and D3M (NeurIPS 2025,
  arXiv 2506.05047) — these are primary baselines.
- Later papers, NOT Paper 1: G4 (silence mistaken for recovery), G5 (adversarial blinding), G6 (semantic).
- Deadlines: IEEE IV 15 Nov 2026 (G1+G3, only if H1 confirmed by ~5 Oct); IEEE ITSC 1 Mar 2027 (main
  target, G1+G3+G2).

## Tanay's tasks (proposed split — see TANAY_HANDOFF.md §9)
1. Re-run his 13 Sept empirical gap verification on branch 3.0 (it failed before only because 3.0 had
   not been pushed). Record results.
2. Read and record in docs/MANUAL_NOVELTY_CHECK.md §5 (question: does it detect at runtime, without
   labels, that a safety monitor has lost its ability to detect?):
   - Ruchkin et al., "Compositional Probabilistic Analysis of Temporal Properties over Stochastic
     Detectors", IEEE TCAD 2020 (IEEE Xplore doc 9211465)
   - Arnez et al., "Skeptical Dynamic Dependability Management for Automated Systems", IEEE DSD 2022
     (IEEE Xplore doc 9996730)
   - Granig et al., "Weakness Monitors for Fail-Aware Systems", FORMATS 2020 (Springer chapter)
3. G3 literature search (Google Scholar, 2019+): has anyone shown that monitors normalised by
   estimator covariance lose sensitivity when a sensor drops out, in safety gates / runtime assurance?
4. Google Scholar "Cited by" sweeps for CoCo (arXiv 2111.03782), KS(conf) (arXiv 1804.04171),
   Antonante et al. (arXiv 2205.10906), Amoukou et al. (arXiv 2412.12910).
5. Later (Stage C): implement baselines as benchmark code only — KS(conf), conformal test martingale,
   Amoukou-style label-free detector, D3M, ModelGuard-style check.
6. Review Sushanth's Stage A preregistration before any run.

## How to work with Tanay
- Before editing files, say what you will change and why; wait for a yes on anything touching src/,
  experiments' frozen parameters, or git history.
- Commit on a branch off 3.0 (e.g. tanay/<topic>), push that branch, open a pull request into 3.0.
- Keep answers plain: say what was checked, what was found, and what is still uncertain.

Start by syncing the repo, running the tests, and summarising TANAY_HANDOFF.md §0 back to Tanay.
```

---

## Notes for Tanay

- The brief is also usable with other assistants, but the commands assume Claude Code in the repo folder.
- If Claude drifts from the rules, point it back to this file and `TANAY_HANDOFF.md` §10.
