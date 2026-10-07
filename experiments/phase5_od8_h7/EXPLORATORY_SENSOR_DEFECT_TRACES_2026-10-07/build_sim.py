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
           ye_off=(), orig=(), ev=(), notes=(), today=None, pn=("urban_clear", "rain_night")):
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
                pn=list(pn), pf="".join(str(seg(i * DT, prof, 0)) for i in range(N)))


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

arms += T
data = dict(seed=d["seed"], hz=HZ, step=d["every"], arms=arms)
html = (HERE / "sim_template.html").read_text(encoding="utf-8").replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
(ROOT / "mp_review_sim.html").write_text(html, encoding="utf-8", newline="\n")
print("wrote", ROOT / "mp_review_sim.html", len(html) // 1024, "KB;", len(arms), "scenarios")
