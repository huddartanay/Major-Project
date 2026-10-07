# Threat literature study — lying, hacked and semantically wrong sensors

**7 October 2026 · Sushanth.** 24 papers; every one was downloaded as a PDF and its text extracted and
read in the sections named below (abstract, threat model / assumptions, limitations, open problems).
None was read cover to cover. Quotes are short and from the extracted text. Nothing here is a result
of ours unless marked **[ASTRA evidence]**, and those point at a committed experiment.

This study does not replace `MANUAL_NOVELTY_CHECK.md`; it covers the threat side that the earlier
reviews (conformal gates, runtime monitors) left out.

---

## 1 · Definitions we should adopt

The literature does not use "lying sensor" or "hacked sensor" as terms. It uses the ones on the right.
We should use theirs in the paper and keep ours for talking among ourselves.

| our word | term to use | definition | intent | what makes it hard |
|---|---|---|---|---|
| broken sensor | **sensor loss / fail-silent fault** | readings stop or are flagged invalid | none | nothing, if it is flagged — the stack must degrade correctly |
| lying sensor | **fail-inconsistent (Byzantine) sensor fault** | a source reports well-formed, plausible, wrong values; the other sources are honest | none | the value passes range and freshness checks |
| hacked sensor | **sensor deception attack / false data injection (FDI)** | readings chosen by an adversary to cause harm *and* to stay under the detector | yes | the adversary adapts to the check: majority, slow drift, replay |
| semantic error | **semantic fault** | value is well-formed and self-consistent but its *meaning* is wrong: unit, sign, frame, timestamp, identity | either | every syntactic and statistical check passes |

Two boundaries worth stating in the paper:

- **Lying vs hacked** is not about the value, it is about whether the fault *adapts to the defence*. A
  constant 2 m bias on one of three position sources is a lie. The same bias on two of three, chosen
  because the fusion takes a majority, is an attack.
- **Semantic in the security literature means something else.** Shen et al.'s SoK defines "semantic AI
  security" as attacks on the AI component that change system-level driving behaviour (2203.05314). Our
  meaning — unit/sign/frame errors — is closer to software-engineering usage. If we keep the word we must
  define it in the first paragraph where it appears, or reviewers will read the other meaning.

---

## 2 · Hard limits — what no defence can do

These are theorems or structural arguments. Any claim of ours has to sit inside them.

| limit | source | consequence for us |
|---|---|---|
| The number of attacked sensors that can be corrected is bounded by a property of the system; in the standard setting, **fewer than half** | Fawzi, Tabuada & Diggavi (1205.5073) | With 3 position sources we can tolerate 1 liar. Two agreeing liars are, in principle, not correctable by redundancy alone |
| State can be recovered under `s` attacked sensors only if the system is **2s-sparse observable** | Shoukry et al. (1412.4324) | Speed and lateral acceleration have one source each in our simulator: **zero** attack tolerance on those channels by this criterion |
| An attacker who corrupts **all** inputs and outputs is undetectable; resilience needs periods where some I/O is uncorrupted | Griffioen, Krogh & Sinopoli (2205.00372) | "Resilient to hacked sensors" without a bound on the attacker is a false claim |
| A detector that compares against a model can be evaded by an attacker who keeps the deviation under the threshold; defences assume the attacker lacks internal state | Choi et al., RAID 2020 | Our gate has a fixed threshold; a stealthy attacker is out of scope unless we say what the attacker knows |
| Replay of recorded clean data defeats passive residual detectors; detecting it needs an **active** signal | Porter et al. (2001.09859) — dynamic watermarking | **[ASTRA evidence]** our frozen-sensor arm (STEP 6) is the unintentional version: L1 0/30, shipped gate ≈ 0 % |

**The sentence this forces:** ASTRA can be claimed resilient only against a *stated* fault and attacker
class. "All kinds of attacks" is not a claim any paper in this set makes, and the three limits above are
why.

---

## 3 · Paper by paper

Read level: **A** abstract + threat model + limitations/open problems read; **B** abstract + targeted
passages.

### 3.1 Hacked sensors — estimation-theoretic defences

| paper | read | what it does | assumes | does not do |
|---|---|---|---|---|
| Fawzi, Tabuada, Diggavi — *Secure estimation and control for CPS under adversarial attacks* (1205.5073) | A | Characterises how many attacked sensors can be corrected; decoder by optimisation | Linear, known model; sparse attack | Learned controller; what to do once the bound is exceeded |
| Shoukry et al. — *Secure state estimation … SMT approach* (1412.4324) | A | SMT search for the attacked set | Linear; 2s-sparse observability | Same |
| Yang & Lv — *Secure sensor fusion framework for CAVs* (2103.00883) | A | Fuses redundant sensors, isolates attacked ones | Fewer than half of redundant sensors compromised | No degraded-mode policy; no learned controller |
| Niazi et al. — *Secure set-based state estimation* (2309.05075) | B | Set-valued estimate guaranteed to contain the true state | Sensor redundancy; bounded noise | Sets grow; no link to a mode decision |
| Griffioen, Krogh, Sinopoli — *Ensuring resilience against stealthy attacks* (2205.00372) | A | Tool to analyse mechanisms against stealthy attacks | Some uncorrupted I/O at some times | — (it is the limit result) |
| Andersson & Dán — *Active Bayesian inference … under sensor FDI* (2604.11410) | A | Bayesian network over which sensors are compromised; **active probing**; says it bridges detection and recovery | Known linear model; attack hypotheses enumerable | Learned controller; staged degradation |

### 3.2 Hacked sensors — autonomous vehicles specifically

| paper | read | finding we can cite |
|---|---|---|
| Porter et al. — *LTV dynamic watermarking* (2001.09859) | B | A private excitation signal in the actuation detects replay and deception on an AV. Active, not passive |
| Choi et al. — *Software-based realtime recovery from sensor attacks* (RAID 2020) | A | Software sensors stand in for attacked ones. Recovery is short-horizon; assumes attacker cannot track internal state |
| Shen et al. — *Lateral-direction localization attack* (2307.14540) | A | GPS spoofing alone defeats multi-sensor-fusion localization; lane detection as an independent check. Says recovery methods "assume an effective attack detection in place, which does not yet exist" |
| Zhang et al. — *SoK: How sensor attacks disrupt AVs* (2509.11120) | A | End-to-end view: fusion is under-analysed; attacks must be sustained across frames to matter; **localization errors propagate downstream**; calls for end-to-end rather than per-module evaluation; lists 12 overlooked vectors |
| Khan et al. — *SoK: perception attacks and multi-sensor fusion* (2604.20621) | A | Gaps: limited real-world testing, short-term evaluation bias, and the "absence of defenses that account for inter-sensor consistency" |
| Tsai, Abrar, Hariri — *Security and resilience in AVs: a proactive design approach* (2604.12408) | B | Layered resilient architecture (redundancy, diversity, reconfiguration), anomaly + hash-based detection, shown on a Quanser QCar against camera blinding and software tampering. **Closest architecture paper in this set** |

### 3.3 Recovery and degradation

| paper | read | finding we can cite |
|---|---|---|
| Lu et al. — *Recovery from adversarial attacks in CPS: shallow, deep and exploratory* (2404.04472) | A | Survey. Most recovery is "shallow" (restore the estimate); recovery works assume the recovery module itself is safe and do not consider its own vulnerability |
| Chu et al. — *Integrating graceful degradation and recovery through requirement-driven adaptation* (2401.09678) | B | Degradation = weakening a requirement, recovery = strengthening it; one mechanism for both. Notes the two are "typically developed independently" with ad-hoc coordination. Evaluated on a UUV, STL + MILP |
| Fu et al. — *A formally verified fail-operational safety concept for AD* (2011.00892) | B | Four-mode degradation policy over redundant channels, model-checked in mCRL2. Hardware/channel faults, not sensor lies; no learned component |
| Kröger & Brettin — *Challenging transition from minimal risk condition* (2608.07061) | B | What happens *after* the vehicle stops is unspecified in regulation; cites ISO 23793-1:2024: resuming after MRC "shall always require human interaction" |
| Segovia-Ferreira et al. — *Survey on cyber-resilience approaches for CPS* (2302.05402) | B | Open challenge: techniques protect network, software or physical layer "in an independent manner"; calls for cross-layer integration |

### 3.4 Lying (faulty, non-adversarial) sensors

| paper | read | finding we can cite |
|---|---|---|
| Buerkle et al. — *Fault-tolerant perception: a lightweight monitoring approach* (2111.12360) | A | Plausibility checks on perception output; states it detects only a subset of errors |
| Park et al. — *Resilient sensor fusion under adverse sensor failures (MoME)* (2503.19776) | B | Fusion that keeps working when a modality fails. Perception level; no claim about the controller downstream |
| Aslam et al. — *Runtime validation of AI-based environment perception* (2412.16762) | B | "Dependability cage": redundant perception channels checked for consistency at run time |
| Rahman, Corke, Dayoub — *Run-time monitoring of ML for robotic perception: survey* (2101.01364) | B | Taxonomy; inconsistency between redundant outputs is a growing monitoring signal |

### 3.5 Semantic errors

| paper | read | finding we can cite |
|---|---|---|
| Shen et al. — *SoK: On the semantic AI security in AD* (2203.05314) | A | Defines the semantic gap between component-level error and system-level effect. Scientific gaps include **lack of system-level evaluation**, most attacks having no defence, and downstream components under-explored |
| Hekmatnejad et al. — *Spatio-Temporal Perception Logic (STPL)* (2206.14372) | A | Formal sanity checks on perception streams **without ground truth**. Offline |
| Yu, Feng, Elbaum — *Runtime monitoring of VLA reasoning–trajectory consistency* (2608.29583) | B | Monitors whether what the model says it will do matches the trajectory it emits. Nearest to "meaning vs value" at the decision level |

**Not found in this search:** a paper treating unit / sign / reference-frame errors in a sensor stream as a
runtime fault class for a learned vehicle controller. That is an absence in 24 papers from six searches,
not evidence that none exists. Needs a targeted search (data-validation, schema and units-of-measure
literature) before it is written down as a gap.

---

## 4 · What the field says is missing — in its own words

| statement | source | status for us |
|---|---|---|
| Recovery assumes detection exists; detection "does not yet exist" | Shen et al. 2307.14540 | Supports motivating detection *and* response in one stack |
| Recovery works assume the recovery module is itself safe | Lu et al. 2404.04472 | **Matches our own finding** — see §5 |
| No defences accounting for inter-sensor consistency | Khan et al. 2604.20621 | L3 trust is exactly this in intent; untested against attacks |
| Evaluation is per-module, not end-to-end; errors propagate downstream | Zhang et al. 2509.11120; Shen et al. 2203.05314 | Our closed-loop harness is end-to-end. A real strength if the experiments are run |
| Degradation and recovery are built separately and glued ad hoc | Chu et al. 2401.09678 | L8 escalation and de-escalation are one state machine. Chu et al. already unify them a different way — cite, do not claim first |
| Layers are protected independently | Segovia-Ferreira et al. 2302.05402 | Motivation for a layered stack with a shared evidence path |
| What happens after the stop is unspecified | Kröger & Brettin 2608.07061 | Our HALT exits only by `reset()`; consistent with ISO 23793-1. Say so; do not claim autonomous resumption |

---

## 5 · Where ASTRA stands, category by category

Only what committed experiments show. The exploratory threat probe was written and **not run**, so most
cells are empty on purpose.

| category | case | evidence | result |
|---|---|---|---|
| sensor loss | IMU dropout | Tanay's STEP 1–5; STEP 6 | L1 flags it; L8 escalates and stops. Shipped L6 gate goes quiet (G1) |
| frozen sensor (replay-like) | speed and lateral acceleration stuck | STEP 6, dev + held-out | **L1 0/30. Shipped gate ≈ 0 %. Estimated vs true speed ≈ 12 m/s apart.** Nothing in the stack notices |
| frozen sensor, corrected score | same | STEP 7 | Not suppressed (median ≈ 5.2× clean), but ≈ 20 % of runs stay quiet. Detection **not established** |
| lying, one of three position sources | `position_bias` | STEP 7 positive control | Corrected score detects it (11× dev, 17× held-out). Shipped-score behaviour on this arm not re-measured in STEP 7 |
| lying, speed / lateral-acceleration bias | — | none | **untested** |
| hacked, two of three sources colluding | — | none | **untested**; §2 says redundancy alone cannot correct it |
| hacked, slow drift under threshold | — | none | **untested** |
| semantic: unit, sign | — | none | **untested** |

Two things this table makes plain:

1. **The monitor is itself the weak component.** The shipped gate passed its calibration checks while
   99.96 % of its score came from channels the twin does not model
   (`FINDING_TWIN_CHANNEL_MISMATCH_2026-10-07`). Lu et al. say recovery work assumes the recovery module
   is safe. We have a measured instance of a safety monitor that was calibrated and uninformative. This
   is the best-supported thing we have.
2. **The frozen-sensor result is our clearest attack-relevant finding**, and it is a failure, not a
   strength. A value that stops changing defeats L1 (still fresh, in range) and the shipped L6. The
   literature's answer to replay is an active signal (watermarking, probing). ASTRA has none.

---

## 6 · What this means for novelty

**Not novel, do not claim:**

- Tolerating a minority of bad redundant sensors (Fawzi 2012; Shoukry; Yang & Lv).
- A layered resilient AV architecture with detection and fallback (Tsai et al. 2604.12408; Fu et al.).
- Unifying degradation and recovery (Chu et al.).
- Bridging detection and recovery under FDI (Andersson & Dán).
- "Resilient to adversarial sensors" without a bounded attacker.

**Open in these 24 papers, and we have or can get evidence:**

| candidate | why it looks open | what we hold |
|---|---|---|
| **C1 · A calibrated monitor can be uninformative** — calibration checks do not test whether the score depends on the thing it claims to monitor | Recovery/monitor safety is assumed, not tested (Lu et al.); conformal papers reviewed earlier validate coverage, not sensitivity | Measured, dev + held-out. Strongest |
| **C2 · Frozen-value faults evade freshness, range and a conformal gate at once** | Replay is treated as an attack needing watermarking; as a *fault* class against learned-controller gates it is not evaluated in this set | Measured (STEP 6). Corrected-score detection inconclusive (STEP 7) |
| **C3 · End-to-end response of a governed learned controller across a fault taxonomy** (loss → lie → collusion → semantic), reporting where each layer first reacts | SoKs call for end-to-end evaluation; most defences are per-module | Harness exists; only the first two rows are run |
| **C4 · Unit / sign / frame errors as a runtime fault class** | Not found (weak evidence — see §3.5) | Nothing yet |

C1 and C2 are findings about a failure. C3 is the "system" contribution, and it only becomes a claim
after the experiments exist. So the honest answer to "can we call it a novel system resilient to all of
these" is: **not today.** What we can defend today is C1, with C2 as supporting evidence.

---

## 7 · What to do next (recommendation)

1. **Write the threat model first**, one page, using §1's terms and §2's limits: which sources, how many
   may be faulty, what the attacker knows, what is out of scope (full-I/O attacker; colluding majority).
2. **Pre-register and run the fault-taxonomy study (C3)** — the scratchpad probe turned into a proper
   study with a run-level detection metric, new held-out block. This fills the empty rows of §5.
3. **Frozen-value check at L1** — a cheap, well-known remedy (variance / stuck-at test). Adding it is
   engineering, not novelty; it should be reported as a baseline the gate is compared against.
4. **Targeted search for C4** before any claim: units-of-measure checking, data validation for ML
   pipelines, frame/timestamp consistency in ROS.
5. Still owed from STEP 7: why ≈ 20 % of runs stay quiet.

## 8 · Limits of this study

- 24 papers from six web searches; arXiv-heavy; no IEEE Xplore or ACM full-text sweep, no "cited by" pass.
- Partial reads. A limitation stated on a page I did not read would be missed.
- Classic works known but **not** read here: SAVIOR (USENIX Sec 2020), control invariants (CCS 2018),
  PID-Piper (DSN 2021), DeLorean, Mo & Sinopoli on replay. They should be read before submission.
- "Not found" in §3.5 and §6 means not found here.
