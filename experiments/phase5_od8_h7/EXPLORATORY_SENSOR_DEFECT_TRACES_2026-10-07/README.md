# EXPLORATORY — one recorded run per sensor defect (7 October 2026)

**Not pre-registered. One dev seed (`20260731`), one run per arm. Not evidence for any claim.** Recorded to drive
the 3D replay in `mp_review_sim.html` and to choose arms for STEP 8.

2,400 ticks at 20 Hz (120 s); defect from tick 200 (10.0 s) to the end; policy `var/policy/synthetic.pt`;
default redundant sensing (position from IMU σ 0.10 m, GPS σ 0.20 m, LIDAR σ 0.06 m; speed and lateral
acceleration one source each). Code at `09dc6e3` plus this folder.

- `record_traces.py` — runs the arms, writes `traces.json` (every 4th tick).
- `build_sim.py` + `sim_template.html` — pack the traces into `mp_review_sim.html` at the repository root.

Unit and sign errors are injected by a small `FaultInjector` subclass in `record_traces.py`; that path is new
and untested beyond these runs.

## Result

| sensor | exact defect | L1 flags it | fail-safe leaves NOMINAL | final mode | real speed at end | worst speed belief error | worst distance from lane centre |
|---|---|---|---|---|---|---|---|
| — | none (healthy reference) | — | never | NOMINAL | 40 km/h | 0 km/h | 0.24 m |
| Position · IMU | reads 1.0 m to the side; GPS, LIDAR honest | IMU, after 0.45 s | 0.65 s | HALT at 2.40 s | 0 | 2 km/h | 0.47 m |
| Position · GPS | reads 1.0 m to the side; IMU, LIDAR honest | GPS, after 0.80 s | 1.00 s | HALT at 3.75 s | 0 | 2 km/h | 0.42 m |
| Position · LIDAR | reads 1.0 m to the side; IMU, GPS honest | LIDAR, after 0.45 s | 0.65 s | HALT at 2.40 s | 0 | 2 km/h | 0.57 m |
| Position · LIDAR | drifts sideways 4 cm/s | LIDAR, after 16.40 s (0.66 m of drift) | 16.60 s | HALT at 21.90 s | 0 | 2 km/h | 0.46 m |
| Position · IMU + GPS | both read 1.0 m to the side; only LIDAR honest | **LIDAR** (the honest one), after 0.45 s | 0.65 s | HALT at 2.40 s | 0 | 2 km/h | 0.95 m |
| Position · IMU + GPS | both drift sideways 4 cm/s | **LIDAR** (the honest one), after 15.65 s | 17.95 s | HALT at 22.40 s | 0 | 2 km/h | 0.48 m |
| Speed | freezes | never | **never** | NOMINAL | **53 km/h** | 15 km/h | 0.24 m |
| Speed | reads 3.0 m/s too high | never | **never** | NOMINAL | 29 km/h | 11 km/h | 0.23 m |
| Speed | reads 3.0 m/s too low | never | **never** | NOMINAL | **51 km/h** | 11 km/h | 0.30 m |
| Speed | drifts to 5.0 m/s too low | never | **never** | NOMINAL | **55 km/h** | 18 km/h | 0.26 m |
| Speed | reported in km/h instead of m/s | never | 0.45 s, then back to NOMINAL | NOMINAL | 4 km/h | 100 km/h | 0.56 m |
| Lateral acceleration | freezes | never | **never** | NOMINAL | 21 km/h | 0 | 0.50 m |
| Lateral acceleration | reads 1.0 m/s² too high | never | 0.65 s | HALT at 5.15 s | 0 | 2 km/h | **10.91 m — left the lane** |
| Lateral acceleration | sign flipped | never | **never** | NOMINAL | 4 km/h | 0 | 0.74 m |
| Speed + lateral acceleration | both freeze (STEP 6 arm) | never | **never** | NOMINAL | 0 km/h | 38 km/h | 0.38 m |
| IMU message stream | stops sending (STEP 6 arm) | IMU, after 0.05 s | 0.25 s | LIMP | 0 km/h | 38 km/h | 0.25 m |

Times are measured from the moment the defect starts (10.0 s into the run). Lane edge is 1.75 m from centre.

**What these single runs suggest — to be tested, not yet claimed:**

1. **Position defects are the well-covered case.** Any one of the three sources lying by 1.0 m is flagged within
   0.45–0.80 s and the car is stopped within 2.4–3.75 s. A slow drift is caught too, but only after 16 s.
2. **When two position sources agree on a lie, L1 blames the honest third one.** The car is still stopped, but for
   the wrong reason, and it moved 0.95 m off centre first.
3. **Every speed defect went unnoticed.** With a frozen or under-reading speed sensor the car ended 11–15 km/h
   *faster* than the healthy run while the fail-safe stayed in NOMINAL. Speed has a single source and nothing to
   cross-check it against.
4. **A lateral-acceleration reading 1.0 m/s² too high put the car 10.9 m off the lane centre** before the fail-safe
   stopped it at 5.15 s. L1 never flagged it. This is the most serious outcome in the set.
5. **A wrong unit was noticed and then forgotten.** The gates blocked at once and the fail-safe went to DEGRADED
   after 0.45 s, then returned to NOMINAL with the defect still present, the car crawling at 4 km/h.
6. **Freezing both speed and lateral acceleration stops the car without any layer knowing**; freezing speed alone
   speeds it up. The same kind of defect has opposite effects depending on which channels it hits.

## Limits

- One seed. STEP 6 / STEP 7 showed the frozen-sensor outcome varies by seed (about a third of 30 runs halted).
- "First gate to block" is in `traces.json` (`first`); the physical gate also blocks occasionally in the healthy
  run (first at tick 519), so a block is not by itself a detection.
- Purple "picture is wrong" states in the replay are computed against simulator ground truth, which ASTRA does
  not have.
