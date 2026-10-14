"""Pack recorded traces and the design-target scenarios into mp_review_sim.html.

Usage (this folder): python build_sim.py

Three kinds of scenario end up in the page:
  rec   -- recorded run of the code as configured for the paper experiments (traces.json)
  feat  -- recorded run with dormant features switched on (traces_features.json)
  design-- NOT a run. A hand-written illustration of the intended behaviour (TARGETS below).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
HZ = 20
MODE = {"NOMINAL": 0, "DEGRADED": 1, "LIMP": 2, "HALT": 3}
ORIG = {"PROPOSED": 0, "RATE_LIMITED": 1, "SPEED_CAPPED": 2, "FALLBACK_PID": 3, None: 4, "EXPLORATION_BOUNDED": 5}
ARB = {None: 0, "CONTINUE": 1, "SHADOW_EXECUTION": 2, "SWITCH_COMMITTED": 3, "ROLLBACK": 4, "SAFE_EXPLORATION": 5}
ENVC = {"road": 0, "tunnel": 1, "rain_night": 2}
ENVN = {"road": "open road", "tunnel": "a tunnel (no calibration covers it)", "rain_night": "rain at night"}
GATE = {"STATISTICAL": 1, "PHYSICAL": 2, "DETERMINISTIC": 4}
MOD = {"IMU": 1, "GPS": 2, "LIDAR": 4}
GNAME = {"STATISTICAL": "L6 statistical gate", "PHYSICAL": "L7 physical gate", "DETERMINISTIC": "L7 rule shield"}
MNAME = {"NOMINAL": "L8 fail-safe returns to NOMINAL", "DEGRADED": "L8 fail-safe enters DEGRADED (cap 40 km/h)",
         "LIMP": "L8 fail-safe enters LIMP (cap 20 km/h)", "HALT": "L8 fail-safe enters HALT (stop; needs a manual reset)"}
BAD = {"clean": [], "pos_imu_bias": ["imu"], "pos_gps_bias": ["gps"], "pos_lidar_bias": ["lidar"], "pos_lidar_drift": ["lidar"],
       "pos_two_bias": ["imu", "gps"], "pos_two_drift": ["imu", "gps"], "speed_frozen": ["speed"], "speed_bias": ["speed"],
       "speed_low": ["speed"], "speed_drift": ["speed"], "speed_unit": ["speed"], "lat_frozen": ["lat"], "lat_bias": ["lat"],
       "lat_sign": ["lat"], "both_frozen": ["speed", "lat"], "imu_dropout": ["stream"],
       "env_change": [], "road_only": [], "pos_gps_tol1": ["gps"], "pos_lidar_tol1": ["lidar"], "pos_two_tol1": ["imu", "gps"],
       "dropout_10s": ["stream"], "tunnel_dropout": ["stream"]}


def r2(x):
    return 0 if x is None else round(x, 2)


def pack(rows, extra=False):
    def col(i): return [r2(r[i]) for r in rows]
    def mask(i, table): return "".join(str(sum(table[x] for x in set(r[i]))) for r in rows)
    d = dict(vt=col(1), ve=col(2), dv=col(3), ye=col(4), sc=col(9), tr=col(11),
             m="".join(str(MODE[r[5]]) for r in rows), o="".join(str(ORIG[r[6]]) for r in rows),
             g=mask(7, GATE), h=mask(8, MOD), b="".join("1" if (r[13] or 0) > (r[12] or 0) else "0" for r in rows))
    if extra:
        names = sorted({r[16] for r in rows if r[16]})
        d.update(env="".join(str(ENVC[r[14]]) for r in rows), arb="".join(str(ARB[r[15]]) for r in rows),
                 pn=names, pf="".join(str(names.index(r[16])) if r[16] else "0" for r in rows))
    return d


# ------------------------------------------------------------------ recorded, as configured
d = json.load(open(HERE / "traces.json"))
clean_first = next(a for a in d["arms"] if a["id"] == "clean")["first"]
arms = []
for a in d["arms"]:
    ev = []
    for k, v in a["first"].items():
        if k == "l1":
            ev.append([v[0] / HZ, "L1 marks " + " + ".join(v[1]) + " position as unhealthy", 0])
        elif k.startswith("gate_"):
            same = clean_first.get(k) == v and a["id"] != "clean"
            ev.append([v / HZ, GNAME[k[5:]] + " first blocks a command", 1 if same else 0])
        else:
            ev.append([v / HZ, MNAME[k[5:]], 0])
    ev.sort()
    arms.append(dict(id=a["id"], kind="rec", sensor=a["sensor"], defect=a["defect"], desc=a["desc"], bad=BAD[a["id"]],
                     on=None if a["id"] == "clean" else d["onset"] / HZ, off=None, ev=ev, **pack(a["rows"])))

# ------------------------------------------------------------------ recorded, dormant features on
FEAT_NOTES = {
 "env_change": [["good", "Safe exploration engaged at the first calibration check after the tunnel began, and the car slowed."],
                ["bad", "It never ended. Back on the open road, and later in rain, the car was still in safe exploration at about 4 km/h."],
                ["bad", "Rain at night produced no calibration switch, because the car was still exploring."],
                ["warn", "Before the tunnel, L9 found a better calibration (urban_clear) and began testing it in shadow, but had not committed it after 20 s."]],
 "road_only": [["warn", "L9 found a better calibration (urban_clear, trust 0.71 to 0.74) and tested it in shadow for the whole 120 s. It never committed the switch and never rolled back."],
               ["good", "Driving was unaffected: NOMINAL throughout at about 40 km/h."]],
 "pos_gps_tol1": [["good", "With one bad source tolerated, the fail-safe did not stop the car: mode stayed NOMINAL."],
                  ["bad", "But one calibration check after L1 flagged GPS, L9 entered safe exploration and stayed there. The car ended at about 4 km/h."],
                  ["warn", "L1's flag on GPS flickered on and off for the whole run."]],
 "pos_lidar_tol1": [["good", "With one bad source tolerated, the fail-safe did not stop the car: mode stayed NOMINAL."],
                    ["bad", "But L9 entered safe exploration within a second and stayed there. The car ended at about 4 km/h."]],
 "pos_two_tol1": [["bad", "Two sources lied together and L1 blamed LIDAR, the honest one. One flagged source is within the tolerance, so the fail-safe stayed in NOMINAL."],
                  ["bad", "The car was never stopped. It only slowed because L9 entered safe exploration."],
                  ["warn", "Raising the tolerance to one hides a two-source lie from the fail-safe."]],
 "dropout_10s": [["good", "Graded response and recovery both worked: DEGRADED after 0.25 s, LIMP after 0.75 s, and back to NOMINAL 1.8 s after the messages returned."],
                 ["bad", "L9 entered safe exploration during the outage and never left it. The car was at 0 km/h at the end although the mode was NOMINAL."]],
 "tunnel_dropout": [["good", "Safe exploration engaged in the tunnel."],
                    ["bad", "When the IMU stream then stopped, the fail-safe escalated to HALT in 3 s. HALT is latched, so the car stayed stopped after the messages returned and after the tunnel ended."]],
}
FEAT_GROUP = {"env_change": "Environment changes", "road_only": "Environment changes", "pos_gps_tol1": "One bad source tolerated",
              "pos_lidar_tol1": "One bad source tolerated", "pos_two_tol1": "One bad source tolerated",
              "dropout_10s": "Defect that ends", "tunnel_dropout": "Defect that ends"}
FEAT_SHORT = {"env_change": "road, tunnel, road, rain", "road_only": "open road only", "pos_gps_tol1": "GPS reads 1.0 m off",
              "pos_lidar_tol1": "LIDAR reads 1.0 m off", "pos_two_tol1": "IMU + GPS read 1.0 m off", "dropout_10s": "IMU stream off for 10 s",
              "tunnel_dropout": "IMU stream off in a tunnel"}
f = json.load(open(HERE / "traces_features.json"))
for a in f["arms"]:
    ev, flags = [], 0
    for c in a["changes"]:
        t, kind = c[0] / HZ, c[1]
        if kind == "env" and c[0] > 0:
            ev.append([t, "Surroundings change to " + ENVN[c[2]], 0])
        elif kind == "mode" and c[0] > 0:
            ev.append([t, MNAME[c[2]], 0])
        elif kind == "arb":
            if c[2] == "SHADOW_EXECUTION":
                ev.append([t, f"L9 starts shadow execution: testing calibration '{c[3]}' (trust {c[4]})", 0])
            elif c[2] == "SAFE_EXPLORATION":
                ev.append([t, "L9 enters safe exploration: no calibration fits (half speed, steering within 15 degrees)", 0])
            elif c[2]:
                ev.append([t, "L9: " + c[2].replace("_", " ").lower(), 0])
        elif kind == "l1" and c[2]:
            flags += 1
            if flags == 1:
                ev.append([t, "L1 marks " + " + ".join(c[2]) + " as unhealthy", 0])
    if flags > 1:
        ev.append([a["changes"][-1][0] / HZ, f"(L1's flag switched on {flags} times in total)", 0])
    arms.append(dict(id="f_" + a["id"], kind="feat", group=FEAT_GROUP[a["id"]], short=FEAT_SHORT[a["id"]], sensor=a["sensor"], defect=a["defect"],
                     desc=a["desc"], bad=BAD[a["id"]], on=a["onset"] / HZ if a["onset"] else None, off=a["off"] / HZ if a["off"] else None,
                     ev=ev, notes=FEAT_NOTES[a["id"]], **pack(a["rows"], extra=True)))
    r = a["rows"]
    print(f"{a['id']:15s} speed at 15s {r[75][1]:5.1f}  40s {r[200][1]:5.1f}  70s {r[350][1]:5.1f}  100s {r[500][1]:5.1f}  end {r[-1][1]:5.1f}  max|dev| {max(abs(x[3]) for x in r):.2f}")

# ------------------------------------------------------------------ design targets (NOT runs)
C = arms[0]
N, DT = len(C["vt"]), d["every"] / HZ
V_CRUISE, V_RAIN, V_SLOW = 11.1, 8.3, 5.55   # 40, 30, 20 km/h


def seg(t, table, default):
    """table: [(t_from, value), ...] ascending; returns the value in force at t."""
    v = default
    for t0, val in table:
        if t >= t0:
            v = val
    return v


def design(id, group, short, sensor, defect, desc, bad, on, off, speed, mode, env=(), arb=(), prof=(), flag=(), belief=None,
           ye_off=(), orig=(), ev=(), notes=(), today=None, pn=("urban_clear", "rain_night"), sc=None, g=None):
    vt, v = [], V_CRUISE
    for i in range(N):
        t = i * DT
        v += (seg(t, speed, V_CRUISE) - v) * DT / 1.6
        vt.append(round(max(0.0, v + (C["vt"][i] - C["vt"][min(N - 1, 60)]) * (0.3 if v > 1 else 0)), 2))
    ve = [round(belief(i * DT, vt[i]) if belief else vt[i], 2) for i in range(N)]
    dv = [round(C["dv"][i] * (1.0 if vt[i] > 1 else 0.6), 2) for i in range(N)]
    ye = [round(C["ye"][i] + seg(i * DT, ye_off, 0.0), 2) for i in range(N)]
    m = "".join(str(seg(i * DT, mode, 0)) for i in range(N))
    return dict(id=id, kind="design", group=group, short=short, sensor=sensor, defect=defect, desc=desc, bad=list(bad), on=on, off=off,
                ev=[[t, s, 0] for t, s in ev], notes=[list(n) for n in notes], today=today,
                vt=vt, ve=ve, **({"ye": ye} if ye_off else {}), m=m,
                o="".join(str(seg(i * DT, orig, 0)) for i in range(N)), h="".join(str(seg(i * DT, flag, 0)) for i in range(N)),
                b="".join("1" if i and vt[i] < vt[i - 1] - 0.03 else "0" for i in range(N)),
                env="".join(str(seg(i * DT, env, 0)) for i in range(N)), arb="".join(str(seg(i * DT, arb, 1)) for i in range(N)),
                pn=list(pn), pf="".join(str(seg(i * DT, prof, 0)) for i in range(N)),
                # optional L6 score (sc(t, clean score)) and gate mask (g(t) -> 1 L6, 2 physics, 4 rules)
                **({"sc": [round(sc(i * DT, C["sc"][i]), 2) for i in range(N)]} if sc else {}),
                **({"g": "".join(str(int(g(i * DT))) for i in range(N))} if g else {}))


T = []
T.append(design("d_rain", "Environment", "rain at night", "Environment", "none",
    "No sensor defect. Rain at night begins at 20 s and ends at 70 s", [], None, None,
    speed=[(26, V_RAIN), (76, V_CRUISE)], mode=[], env=[(20, 2), (70, 0)],
    arb=[(21, 2), (26, 3), (27, 1), (71, 2), (76, 3), (77, 1)], prof=[(26, 1), (76, 0)],
    ev=[(20, "Rain at night begins"), (21, "L9 calibration search finds a better fit: 'rain_night'. Shadow execution starts: both calibrations run side by side, only the old one drives"),
        (26, "The two agreed for 5 s. Switch committed: 'rain_night' is now active, speed limit 30 km/h"),
        (70, "Rain ends"), (71, "L9 finds 'urban_clear' fits again. Shadow execution starts"), (76, "Switch committed back to 'urban_clear', 40 km/h")],
    notes=[("good", "Dynamic calibration: the thresholds and speed limit follow the surroundings, with no fault raised."),
           ("good", "A new calibration is never trusted at once. It runs in shadow first and is committed only if it agrees with the active one; otherwise it is rolled back."),
           ("good", "Mode stays NOMINAL: a change of weather is not a failure.")], today="f_env_change"))
T.append(design("d_tunnel", "Environment", "tunnel", "Environment", "none",
    "No sensor defect. The car is in a tunnel from 20 s to 60 s; no stored calibration covers a tunnel", [], None, None,
    speed=[(21, V_SLOW), (62, V_CRUISE)], mode=[], env=[(20, 1), (60, 0)], arb=[(21, 5), (62, 1)], orig=[(21, 5), (62, 0)],
    ev=[(20, "The car enters a tunnel"), (21, "L9 calibration search finds no calibration that fits. Bounded safe exploration starts: half speed (20 km/h), no lane change, steering within 15 degrees"),
        (60, "The car leaves the tunnel"), (62, "L9 finds 'urban_clear' fits again. Exploration ends, speed returns to 40 km/h")],
    notes=[("good", "Safe exploration: in surroundings nobody calibrated for, the car keeps moving inside a narrow, slow envelope instead of stopping."),
           ("good", "It ends by itself as soon as a certified calibration fits again."),
           ("good", "Mode stays NOMINAL: unfamiliar surroundings are not a sensor failure.")], today="f_env_change"))
T.append(design("d_pos_one", "Position (IMU / GPS / LIDAR)", "one source reads 1.0 m off", "Position: GPS", "constant offset, repaired at 60 s",
    "GPS position reads 1.0 m to the side from 10 s to 60 s; IMU and LIDAR are honest", ["gps"], 10, 60,
    speed=[], mode=[], flag=[(10.5, 2), (65, 0)],
    ev=[(10, "Defect starts"), (10.5, "L1 cross-check: GPS disagrees with IMU and LIDAR. GPS is excluded; the estimate uses the other two"),
        (10.5, "L8 stays in NOMINAL: one bad source out of three is within the declared tolerance. Redundancy is reported as reduced"),
        (60, "GPS reads correctly again"), (65, "GPS agreed with the others for 5 s and is re-admitted")],
    notes=[("good", "The car keeps driving at 40 km/h in its lane. Two honest sources are enough."),
           ("good", "The defect is reported, not hidden: an operator sees \"GPS excluded\"."),
           ("good", "The repaired sensor is taken back only after a probation period.")], today="pos_gps_bias"))
T.append(design("d_pos_two", "Position (IMU / GPS / LIDAR)", "two sources read 1.0 m off", "Position: IMU + GPS", "two sources agree on a lie",
    "IMU and GPS both read 1.0 m to the side from 10 s; only LIDAR is honest", ["imu", "gps"], 10, None,
    speed=[(10.6, V_SLOW), (16, 0.0)], mode=[(10.6, 2), (22, 3)], flag=[(10.5, 7)], orig=[(10.6, 3)], ye_off=[(10, 0.5), (10.6, 0.0)],
    ev=[(10, "Defect starts"), (10.5, "L1 cross-check: the position sources split two against one. No majority can be trusted, so all three are marked suspect"),
        (10.6, "L8 enters LIMP (cap 20 km/h); the fallback controller takes over and holds the lane on the last trusted estimate"),
        (16, "Controlled stop begins"), (22, "L8 enters HALT: stopped in lane, hazard lights on, human reset required")],
    notes=[("good", "A two-against-one split is treated as \"cannot tell who is right\", not as one bad sensor."),
           ("good", "The car stops in a controlled way inside its lane."),
           ("warn", "This is the limit of redundancy: with three sources, two that lie together cannot be outvoted. Stopping is the correct answer.")], today="pos_two_bias"))


def speed_case(id, short, defect, desc, wrong, today):
    return design(id, "Speed", short, "Speed", defect, desc, ["speed"], 10, None,
        speed=[(11, V_SLOW)], mode=[(11, 2)], orig=[(11, 2)], belief=lambda t, v: wrong(v) if 10 <= t < 11 else v,
        ev=[(10, "Defect starts"), (11, "L1 cross-check: the speed reading disagrees with the speed worked out from how fast the position changes. The speed sensor is excluded"),
            (11, "L2 switches to the position-derived speed, which is noisier but honest"),
            (11, "L8 enters LIMP (cap 20 km/h): speed is a single-source, safety-critical reading, so the car continues slowly rather than at full speed")],
        notes=[("good", "The defect is caught within about a second, by comparing against a quantity another sensor already provides."),
               ("good", "The car keeps driving, slowly, on a substitute speed. It neither speeds up nor stops in the lane."),
               ("warn", "Not built yet: today nothing cross-checks the speed reading.")], today=today)


T.append(speed_case("d_speed_frozen", "freezes", "frozen", "Speed reading holds its last value from 10 s", lambda v: V_CRUISE, "speed_frozen"))
T.append(speed_case("d_speed_bias", "reads 3 m/s low", "constant offset", "Speed reads 3.0 m/s too low from 10 s", lambda v: v - 3.0, "speed_low"))
T.append(speed_case("d_speed_unit", "km/h instead of m/s", "wrong unit", "Speed reported in km/h instead of m/s from 10 s", lambda v: v * 3.6, "speed_unit"))
T.append(design("d_lat", "Lateral acceleration", "reads 1 m/s² high or sign flipped", "Lateral acceleration", "constant offset or flipped sign",
    "Lateral acceleration reads wrongly from 10 s", ["lat"], 10, None,
    speed=[], mode=[(10.8, 1)], orig=[(10.8, 2)],
    ev=[(10, "Defect starts"), (10.8, "L1 cross-check: the reading disagrees with speed times turning rate. The lateral-acceleration sensor is excluded"),
        (10.8, "L2 uses the value worked out from speed and heading instead"),
        (10.8, "L8 enters DEGRADED (cap 40 km/h); L9 limits steering to gentle corrections")],
    notes=[("good", "The car stays in its lane. Today the same defect put it 10.9 m off the lane centre."),
           ("good", "It keeps driving at reduced authority instead of stopping."),
           ("warn", "Not built yet: today nothing cross-checks lateral acceleration.")], today="lat_bias"))
T.append(design("d_drop_short", "IMU message stream", "stops for 10 s", "IMU message stream", "stops for 10 s, then returns",
    "IMU messages stop arriving from 10 s to 20 s", ["stream"], 10, 20,
    speed=[(10.3, V_SLOW), (23, V_CRUISE)], mode=[(10.1, 1), (10.3, 2), (21.5, 1), (23, 0)], flag=[(10.05, 1), (20, 0)], orig=[(10.3, 3), (23, 0)],
    belief=lambda t, v: v,
    ev=[(10, "Defect starts"), (10.05, "L1 marks the IMU stream as stale"), (10.1, "L8 enters DEGRADED"), (10.3, "L8 enters LIMP (cap 20 km/h); fallback controller drives"),
        (20, "IMU messages return"), (21.5, "L8 steps back to DEGRADED after a clean period"), (23, "L8 returns to NOMINAL; the learned controller drives again at 40 km/h")],
    notes=[("good", "Graded response: slow down while the sensor is missing, do not stop."),
           ("good", "Recovery: back to normal driving within 3 s of the sensor returning, one step at a time."),
           ("good", "The fail-safe part of this already works in the code today.")], today="f_dropout_10s"))
T.append(design("d_drop_long", "IMU message stream", "stops and stays off", "IMU message stream", "stops permanently",
    "IMU messages stop arriving at 10 s and never return", ["stream"], 10, None,
    speed=[(10.3, V_SLOW), (40, 0.0)], mode=[(10.1, 1), (10.3, 2), (46, 3)], flag=[(10.05, 1)], orig=[(10.3, 3)],
    ev=[(10, "Defect starts"), (10.05, "L1 marks the IMU stream as stale"), (10.3, "L8 enters LIMP (cap 20 km/h); fallback controller drives"),
        (40, "30 s without the sensor: the outage is treated as permanent and a controlled stop begins"), (46, "L8 enters HALT: stopped in lane, hazard lights on, human reset required")],
    notes=[("good", "A short outage and a permanent one get different answers: the car first buys time at low speed, then stops."),
           ("good", "The stop is controlled and in lane.")], today="imu_dropout"))
T.append(design("d_tunnel_drop", "Environment + sensor defect", "tunnel, then IMU stream off for 10 s", "IMU message stream", "stops for 10 s inside a tunnel",
    "The car enters a tunnel at 15 s; IMU messages stop from 30 s to 40 s; the tunnel ends at 60 s", ["stream"], 30, 40,
    speed=[(16, V_SLOW), (62, V_CRUISE)], mode=[(30.1, 1), (30.3, 2), (41.5, 1), (43, 0)], env=[(15, 1), (60, 0)],
    arb=[(16, 5), (62, 1)], flag=[(30.05, 1), (40, 0)], orig=[(16, 5), (30.3, 3), (43, 5), (62, 0)],
    ev=[(15, "The car enters a tunnel"), (16, "L9 starts bounded safe exploration: 20 km/h, steering within 15 degrees"),
        (30, "Defect starts"), (30.05, "L1 marks the IMU stream as stale"), (30.3, "L8 enters LIMP and the fallback controller takes over, still at 20 km/h inside the exploration envelope"),
        (40, "IMU messages return"), (43, "L8 returns to NOMINAL; exploration continues at 20 km/h"), (60, "The car leaves the tunnel"),
        (62, "L9 finds 'urban_clear' fits again. Exploration ends, 40 km/h")],
    notes=[("good", "Two problems at once do not confuse the response: exploration handles the surroundings, the fail-safe handles the sensor."),
           ("good", "The car never stops and never leaves its lane, and it recovers fully."),
           ("warn", "Today this combination ends in a latched HALT.")], today="f_tunnel_dropout"))

# ------------------------------------------------------------------ runtime behaviour (sim/runtime-behaviour, NOT runs)
# Illustrations of the runtime behaviour in the team's ASTRA description: incident timeline, fault scenarios A-E,
# the L6 monitor failure and the channel-aligned repair, shields and fail-closed, hysteresis, recovery.
# Figures quoted as "reported" come from the team's separate build; nothing in this page measured them.
import random

REP = "Reported by the team's build, not measured by this page: "
THR = 3.70                       # about the 95th percentile of the healthy run's L6 score


def alarm(p, seed=0):
    """Deterministic pseudo-random alarm with probability p at time t."""
    return lambda t: random.Random(round(t * 1000) * 7919 + seed).random() < p


clean5 = alarm(0.05, 1)
T.append(design("d_incident", "End-to-end incident · frozen velocity", "freeze, detect, LIMP, repair, recover", "Speed", "frozen, repaired at 40 s",
    "Hypothetical timeline. The speed reading freezes at 10 s on a downhill stretch and is repaired at 40 s", ["speed"], 10, 40,
    speed=[(10, 13.0), (11, V_SLOW), (45, V_CRUISE)], mode=[(11, 2), (45, 1), (50, 0)], orig=[(11, 3), (45, 2), (50, 0)],
    belief=lambda t, v: V_CRUISE if 10 <= t < 11 else v, g=lambda t: 1 if 10.6 <= t < 11 else int(clean5(t)),
    sc=lambda t, s: s + (1.4 if 10.6 <= t < 11 else 0),
    ev=[(0, "NOMINAL at 40 km/h: every sensor fresh, the estimate matches, the learned controller's proposals pass every gate"),
        (10, "Speed reading freezes at 40 km/h. Timestamps keep advancing, so the freshness check in L1 still sees a live stream"),
        (10.2, "The road goes downhill. The car speeds up, but L2 still believes 40 km/h because the only speed source is frozen"),
        (10.6, "Channel-aligned lateral monitor (L6) alarms: lateral acceleration no longer matches speed times turning rate"),
        (11, "L1 cross-check: the speed reading has not changed for 1 s while position-derived speed and IMU acceleration say the car is speeding up. Speed sensor excluded"),
        (11, "L2 switches to position-derived speed (noisier, honest). L8 enters LIMP (cap 20 km/h). The fallback controller drives; the learned controller's proposals are only advisory"),
        (40, "Speed sensor repaired: readings change again and match position-derived speed"),
        (45, "5 s of agreement (probation). Speed sensor re-admitted. L8 steps back one level to DEGRADED (cap 40 km/h)"),
        (50, "5 s more without a fault. L8 returns to NOMINAL; the learned controller drives again")],
    notes=[("good", "Freshness alone misses a frozen value: the timestamps still advance. Comparing against other motion evidence (position change, IMU acceleration) is what catches it."),
           ("good", "Proposed vs authorized: from 11 s to 50 s the learned controller keeps proposing, but only commands inside the mode's limits reach the actuators."),
           ("good", "Recovery is one level at a time, each step after a clean period, so a sensor that comes back briefly does not bounce the car between modes."),
           ("warn", "All times and speeds here are hypothetical. Today's recorded run of this defect stays in NOMINAL and ends at 53 km/h.")], today="speed_frozen"))

# --- L6 statistical monitor: failure and repair
agg = dict(group="Statistical monitor (L6)", sensor="Statistical monitor")
T.append(design("d_mon_clean", agg["group"], "no defect: ~5% alarms", agg["sensor"], "none",
    "No defect. Both monitors alarm on about 5% of healthy ticks, as calibrated", [], None, None,
    speed=[], mode=[], g=clean5,
    ev=[(0, "Healthy driving. The L6 gate alarms on about 1 tick in 20, as its calibration intends")],
    notes=[("good", "A calibrated alarm rate of about 5% on healthy data is what the conformal calibration promises, and it holds."),
           ("good", REP + "clean alarm rate 5.02% on development data and 4.88% on held-out data."),
           ("warn", "Key finding: a correct healthy alarm rate says nothing about whether the monitor reacts to faults. The next scenarios show it does not.")]))
T.append(design("d_mon_agg_imu", agg["group"], "aggregate score: IMU loss", agg["sensor"], "score contracts under IMU loss",
    "IMU messages stop from 10 s to 20 s. L6 uses today's aggregate score over all control channels", ["stream"], 10, 20,
    speed=[(10.75, V_SLOW), (21.8, V_CRUISE)], mode=[(10.25, 1), (10.75, 2), (21, 1), (21.8, 0)], flag=[(10.05, 1), (20, 0)], orig=[(10.75, 3), (21.8, 0)],
    sc=lambda t, s: s - 1.5 if 10 <= t < 20 else s, g=lambda t: 0 if 10 <= t < 20 else int(clean5(t)),
    ev=[(10, "Defect starts"), (10.05, "L1 marks the IMU stream as stale (freshness check)"),
        (10.1, "L6 aggregate score DROPS instead of rising: with no IMU updates the throttle and brake channels look calmer than usual"),
        (10.25, "L8 enters DEGRADED, driven by L1, not by L6"), (10.75, "L8 enters LIMP"),
        (20, "IMU messages return"), (21.8, "L8 back to NOMINAL")],
    notes=[("bad", "L6 stays silent for the whole outage: no alarm in 10 s. Its score contracts below its healthy level."),
           ("bad", "The aggregate score is dominated by throttle and brake. Steering, where the IMU loss matters, contributes almost nothing."),
           ("good", "The car is still handled safely here, but only because L1's freshness check catches a stream that stops. L6 adds nothing.")], today="imu_dropout"))
T.append(design("d_mon_agg_frozen", agg["group"], "aggregate score: frozen velocity", agg["sensor"], "score contracts under frozen speed",
    "Speed reading freezes at 10 s. L6 uses today's aggregate score", ["speed"], 10, None,
    speed=[(10, 12.5), (40, 14.7)], mode=[], belief=lambda t, v: V_CRUISE if t >= 10 else v,
    sc=lambda t, s: s - 1.2 if t >= 10 else s, g=lambda t: 0 if t >= 10 else int(clean5(t)),
    ev=[(10, "Speed reading freezes"), (10.2, "L6 aggregate score drops: a constant speed makes throttle and brake look unusually steady"),
        (30, "Real speed passes 50 km/h. L2 still believes 40 km/h. No layer objects")],
    notes=[("bad", "Silent failure: L6 never alarms, L8 stays NOMINAL, the car ends far faster than it believes."),
           ("bad", "Freshness does not help: timestamps keep advancing on a frozen value."),
           ("warn", "This matches today's recorded run (NOMINAL throughout, 53 km/h at the end).")], today="speed_frozen"))


def aligned(id, short, defect, desc, bad, on, off, speed, mode, orig, flag, belief, t_al, ev, today):
    return design(id, agg["group"], short, agg["sensor"], defect, desc, bad, on, off, speed=speed, mode=mode, orig=orig, flag=flag, belief=belief,
        sc=lambda t, s: s + 2.2 if t_al <= t < (off or 1e9) else s,
        g=lambda t: int(t < t_al + 0.6 or alarm(0.75, 2)(t)) if t_al <= t < (off or 1e9) else int(clean5(t)), ev=ev,
        notes=[("good", "Channel-aligned conformal tracking: the lateral channel gets its own calibrated score, so steering-related faults are no longer drowned out by throttle and brake."),
               ("good", "Healthy behaviour is unchanged: about 5% alarms before the defect, as in the aggregate monitor."),
               ("good", REP + "alarms amplified 11.0x to 17.2x under the evaluated offsets, with clean alarm rates 5.02% (development) and 4.88% (held-out)."),
               ("warn", "Why it can work (explanation, not a reported finding): a fault that removes or freezes motion evidence makes lateral acceleration disagree with speed times turning rate, which only a lateral-only score sees clearly."),
               ("warn", "The alarm says something is wrong, not which sensor. The fail-safe restricts the car; it does not identify the culprit.")], today=today)


T.append(aligned("d_mon_al_imu", "channel-aligned: IMU loss", "lateral score rises under IMU loss",
    "IMU messages stop from 10 s to 20 s. L6 adds a channel-aligned lateral tracker", ["stream"], 10, 20,
    speed=[(10.75, V_SLOW), (21.8, V_CRUISE)], mode=[(10.25, 1), (10.75, 2), (21, 1), (21.8, 0)], orig=[(10.3, 3), (21.8, 0)], flag=[(10.05, 1), (20, 0)],
    belief=None, t_al=10.3,
    ev=[(10, "Defect starts"), (10.05, "L1 marks the IMU stream as stale"), (10.25, "L8 enters DEGRADED"),
        (10.3, "L6 lateral tracker alarms: the lateral score rises above its calibrated threshold and stays there"),
        (10.75, "L8 enters LIMP; L6 and L1 now agree"), (20, "IMU messages return; the lateral score falls back"), (21.8, "L8 back to NOMINAL")], today="imu_dropout"))
T.append(aligned("d_mon_al_frozen", "channel-aligned: frozen velocity", "lateral score rises under frozen speed",
    "Speed reading freezes at 10 s. L6 adds a channel-aligned lateral tracker", ["speed"], 10, None,
    speed=[(10, 12.5), (11.2, V_SLOW)], mode=[(10.8, 1), (11.8, 2)], orig=[(10.8, 2), (11.8, 3)], flag=[],
    belief=lambda t, v: V_CRUISE if 10 <= t < 11.8 else v, t_al=10.5,
    ev=[(10, "Speed reading freezes"), (10.5, "L6 lateral tracker alarms: on the next curve, lateral acceleration does not match the frozen speed times turning rate"),
        (10.8, "Out-of-envelope counter reaches its limit: L8 enters DEGRADED (cap 40 km/h)"),
        (11.8, "Alarm persists: L8 enters LIMP (cap 20 km/h); the fallback controller drives on position-derived speed")], today="speed_frozen"))

# --- shields and fail-closed
SH = "Shields and fail-closed"
T.append(design("d_shield", SH, "monitor silent, physics rejects", "Proposed command", "unsafe steering proposal",
    "No sensor defect. At 30 s the learned controller proposes a sharp steering input at 40 km/h", [], None, None,
    speed=[], mode=[], orig=[(30, 1), (31, 0)], g=lambda t: 2 if 30 <= t < 30.6 else 0, sc=lambda t, s: s,
    ev=[(30, "L4 proposes a sharp steer. L6 score is normal: the statistical monitor raises no alarm"),
        (30, "L5 twin predicts the outcome: lateral acceleration and lateral jerk above the vehicle limits. L7 physics gate rejects the proposal"),
        (30, "L9 issues a rate-limited command instead: same direction, within the steering, lateral-acceleration and jerk limits"),
        (31, "Proposals are back inside the limits; they pass unchanged")],
    notes=[("good", "A proposal can be rejected with no statistical alarm. The deterministic checks do not wait for L6."),
           ("good", "Proposed is not authorized: only the limited command reaches the actuators."),
           ("warn", "Which constraints are enforced in code (lateral acceleration, jerk, slip, stopping distance, speed) is listed in the architecture document; this scene does not prove any of them.")]))
T.append(design("d_failclosed", SH, "twin evidence missing: fail closed", "Digital twin (L5)", "no prediction for 3 s",
    "No sensor defect. The L5 twin returns no prediction from 30 s to 33 s", [], 30, 33,
    speed=[(31, V_SLOW), (38, V_CRUISE)], mode=[(31, 1), (36, 0)], orig=[(30, 3), (36, 0)], g=lambda t: 2 if 30 <= t < 33 else 0,
    ev=[(30, "L5 produces no prediction. Without it the physics gate cannot confirm the proposal is safe"),
        (30, "Fail-closed: L9 does not forward the learned controller's proposal. The fallback controller drives"),
        (31, "Evidence still missing after 1 s: L8 enters DEGRADED"), (33, "Twin predictions return"),
        (36, "3 s of valid evidence: L8 returns to NOMINAL; the learned controller drives again")],
    notes=[("good", "Missing safety evidence is treated as a reason to refuse, never as a pass."),
           ("good", "The car keeps moving under the conservative fallback instead of stopping, because the state estimate is still trusted.")]))

# --- fault scenarios A-E (C is the incident timeline above)
FS = "Fault scenarios A to E"
T.append(design("d_A_outlier", FS, "A: GPS 25 m outlier", "Position: GPS", "extreme outlier",
    "GPS position reads 25 m to the side from 10 s to 30 s; IMU and LIDAR are honest", ["gps"], 10, 30,
    speed=[], mode=[], flag=[(10.05, 2), (35, 0)],
    ev=[(10, "Defect starts"), (10.05, "L1 coordinate-wise median of IMU, GPS and LIDAR: the median ignores the 25 m value. GPS is flagged"),
        (10.05, "L2 UKF updates from the median; its uncertainty barely changes. L8 stays NOMINAL"),
        (30, "GPS reads correctly again"), (35, "5 s of agreement: GPS re-admitted")],
    notes=[("good", "With one outlier among three, the median is unaffected however large the outlier."),
           ("good", "If the UKF uncertainty had grown past its limit, L8 would restrict the car; here it does not need to."),
           ("good", "Matches today's recorded behaviour for a single lying position source, except that today the car is stopped.")], today="pos_gps_bias"))
T.append(design("d_B_imu", FS, "B: IMU loss, 1.8 s recovery", "IMU message stream", "stops for 10 s",
    "IMU messages stop from 10 s to 20 s", ["stream"], 10, 20,
    speed=[(10.75, V_SLOW), (21.8, V_CRUISE)], mode=[(10.25, 1), (10.75, 2), (21, 1), (21.8, 0)], flag=[(10.05, 1), (20, 0)], orig=[(10.75, 3), (21.8, 0)],
    ev=[(10, "Defect starts"), (10.05, "L1 freshness check: no IMU message within its deadline. IMU marked stale"),
        (10.1, "L2 UKF continues on prediction and the other sensors; its uncertainty grows each tick without IMU updates"),
        (10.25, "L8 enters DEGRADED (sensor-integrity counter)"), (10.75, "Uncertainty past the limit: L8 enters LIMP (cap 20 km/h), fallback controller drives"),
        (20, "IMU messages return"), (21, "L8 steps back to DEGRADED"), (21.8, "L8 returns to NOMINAL, 1.8 s after the sensor returned")],
    notes=[("good", "The UKF bridges a gap, not an outage: it cannot reconstruct missing IMU data indefinitely, so restrictions tighten as uncertainty grows."),
           ("good", REP + "recovery 1.8 s after a temporary IMU loss. Today's recorded run shows the same 1.8 s."),
           ("good", "Safe exploration is not entered by a sensor outage, so the car returns to 40 km/h (today it stays crawling).")], today="f_dropout_10s"))
T.append(design("d_D_stale", FS, "D: GPS data 600 ms late", "Position: GPS", "stale messages",
    "GPS messages arrive 600 ms late from 10 s to 30 s", ["gps"], 10, 30,
    speed=[], mode=[], flag=[(10.6, 2), (32, 0)],
    ev=[(10, "GPS messages start arriving late"), (10.6, "L1 freshness check: GPS timestamps are older than the allowed age. GPS is excluded, not fused late"),
        (10.6, "L2 continues on IMU and LIDAR. This is a data-quality problem, not a vehicle-state anomaly: L8 stays NOMINAL"),
        (30, "GPS messages on time again"), (32, "2 s of fresh data: GPS re-admitted")],
    notes=[("good", "Stale data is dropped at L1 before it can distort the estimate."),
           ("good", "A data-quality fault in one redundant source is reported, but does not change the operating mode.")]))
T.append(design("d_D_implausible", FS, "D: LIDAR jumps implausibly", "Position: LIDAR", "physically implausible jumps",
    "LIDAR position jumps by metres between ticks from 10 s to 25 s", ["lidar"], 10, 25,
    speed=[], mode=[], flag=[(10.05, 4), (30, 0)],
    ev=[(10, "LIDAR starts jumping"), (10.05, "L1 plausibility check: a jump of several metres in 50 ms would need impossible acceleration. LIDAR rejected"),
        (25, "LIDAR plausible again"), (30, "5 s of agreement: LIDAR re-admitted")],
    notes=[("good", "A reading that breaks physics is rejected as a sensor fault, not believed as the car's motion."),
           ("good", "The estimate, and therefore the controller, never sees the jumps.")]))
T.append(design("d_E_multi", FS, "E: IMU + GPS + speed together", "Several sensors", "three faults at once",
    "At 10 s the IMU stream stops, GPS goes stale and the speed reading freezes", ["stream", "gps", "speed"], 10, None,
    speed=[(10.75, V_SLOW), (14, 0.0)], mode=[(10.25, 1), (10.75, 2), (18, 3)], flag=[(10.05, 1), (10.6, 3)], orig=[(10.75, 3)],
    belief=lambda t, v: V_CRUISE if 10 <= t < 10.75 else v,
    ev=[(10, "Three sensors fail at once"), (10.05, "L1 marks the IMU stale"), (10.25, "L8 enters DEGRADED"),
        (10.6, "L1 marks GPS stale. Only LIDAR is left for position: the median of one source is no protection"),
        (10.75, "L2 uncertainty past its limit and the speed reading cannot be cross-checked. L8 enters LIMP, fallback controller drives"),
        (14, "State can no longer be trusted enough to keep driving: controlled stop begins in lane"),
        (18, "L8 enters HALT: stopped, latched, human reset required")],
    notes=[("good", "When too few independent sources remain, the answer is a controlled stop, not continued driving on a guess."),
           ("warn", "Median fusion needs a majority of honest sources. Correlated faults (shared power, shared clock, shared mounting) can defeat it silently."),
           ("warn", "HALT is latched on purpose: it is not left automatically even if sensors come back.")]))
T.append(design("d_pos_two_fixed", "Position (IMU / GPS / LIDAR)", "two lie, motion check finds them", "Position: IMU + GPS", "two sources agree on a lie",
    "IMU and GPS both read 1.0 m to the side from 10 s; only LIDAR is honest", ["imu", "gps"], 10, None,
    speed=[(10.6, V_RAIN)], mode=[(10.6, 1)], flag=[(10.6, 3)], orig=[(10.6, 2)], ye_off=[(10, 0.3), (10.6, 0.0)],
    ev=[(10, "Defect starts"), (10.4, "L1 median would follow the two liars. A motion cross-check (speed and heading integrated over the last second) shows the 1.0 m jump never happened"),
        (10.6, "IMU and GPS flagged; LIDAR, which agrees with the motion check, is kept. L8 enters DEGRADED (cap 40 km/h) because only one position source is left")],
    notes=[("good", "Voting alone blames the honest sensor when two lie together (today's recorded run). An independent physical check breaks the tie."),
           ("good", "The car keeps driving at reduced authority instead of stopping."),
           ("warn", "If the motion check itself is unavailable, a two-against-one split must still end in LIMP and a stop.")], today="pos_two_bias"))

# --- hysteresis, calibration switching, exploration exit
RC = "Recovery and calibration"
flick = [(10 + 0.4 * k, (2 if k % 3 else 0)) for k in range(75)] + [(40, 0)]
T.append(design("d_hyst", RC, "flickering GPS: hysteresis", "Position: GPS", "quality flickers around the threshold",
    "GPS freshness hovers around its limit from 10 s to 40 s, so the flag switches on and off", ["gps"], 10, 40,
    speed=[(11.2, V_CRUISE)], mode=[(11.2, 1), (45, 0)], flag=flick, orig=[(11.2, 2), (45, 0)],
    ev=[(10, "GPS quality starts hovering around its limit"), (10.4, "L1 flag switches on and off every few hundred milliseconds"),
        (11.2, "Sensor-integrity counter reaches its limit: L8 enters DEGRADED. Counter decays slower than it rises, so one good tick does not undo it"),
        (40, "GPS steady again"), (45, "5 s with no flag: L8 returns to NOMINAL")],
    notes=[("good", "Hysteresis: one mode change in, one out, although the flag toggled dozens of times."),
           ("good", "Separate counters for out-of-envelope commands and sensor integrity, so a noisy sensor does not reset the other evidence."),
           ("warn", "Without hysteresis the mode would flip with every toggle, and so would the speed cap.")]))
T.append(design("d_rain_fast", RC, "rain: switch in 20 ticks", "Environment", "none",
    "No sensor defect. Rain at night from 20 s to 70 s. Shadow test lasts 20 ticks (1 s)", [], None, None,
    speed=[(22, V_RAIN), (72, V_CRUISE)], mode=[], env=[(20, 2), (70, 0)],
    arb=[(21, 2), (22, 3), (23, 1), (71, 2), (72, 3), (73, 1)], prof=[(22, 1), (72, 0)],
    ev=[(20, "Rain at night begins"), (21, "L9 shadow search: 'rain_night' fits better. Shadow execution: both calibrations run, only the active one drives"),
        (22, "20 ticks of agreement: 'rain_night' committed, speed limit 30 km/h"), (70, "Rain ends"),
        (71, "Shadow test of 'urban_clear'"), (72, "Committed back to 'urban_clear', 40 km/h")],
    notes=[("good", REP + "calibration switching in 20 ticks, one second at 20 Hz."),
           ("good", "A calibration switch changes thresholds and the speed limit only. It cannot lift a mode cap or override L7.")], today="f_env_change"))
T.append(design("d_explore_exit", RC, "exploration ends after IMU outage", "IMU message stream", "stops for 10 s",
    "IMU messages stop from 10 s to 20 s. No calibration fits during the outage, so L9 explores", ["stream"], 10, 20,
    speed=[(10.75, V_SLOW), (23, V_CRUISE)], mode=[(10.25, 1), (10.75, 2), (21, 1), (21.8, 0)], flag=[(10.05, 1), (20, 0)],
    arb=[(11, 5), (23, 1)], orig=[(10.75, 3), (21.8, 5), (23, 0)],
    ev=[(10, "Defect starts"), (10.75, "L8 enters LIMP"), (11, "L9 calibration search finds no fit: bounded safe exploration (half speed, steering within 15 degrees)"),
        (20, "IMU messages return"), (21.8, "L8 back to NOMINAL; still inside the exploration envelope"),
        (23, "L9 matches 'urban_clear' on the sensor-health and road part of the context, ignoring the car's own reduced speed. Exploration ends, 40 km/h")],
    notes=[("good", "Exploration is no longer a one-way door: it ends when a calibration fits again."),
           ("good", "The car's own speed is left out of the context match, so slowing down for exploration cannot keep it exploring."),
           ("warn", "Today's recorded run of this outage ends crawling at 0 to 4 km/h in NOMINAL.")], today="f_dropout_10s"))

arms += T
data =dict(seed=d["seed"], hz=HZ, step=d["every"], arms=arms)
html = (HERE / "sim_template.html").read_text(encoding="utf-8").replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
(ROOT / "mp_review_sim.html").write_text(html, encoding="utf-8", newline="\n")
print("wrote", ROOT / "mp_review_sim.html", len(html) // 1024, "KB;", len(arms), "scenarios")
