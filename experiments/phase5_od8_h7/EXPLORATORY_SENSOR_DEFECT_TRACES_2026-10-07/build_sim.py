"""Pack traces.json into mp_review_sim.html. Usage: python build_sim.py <traces.json>"""
import json, sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
d = json.load(open(sys.argv[1]))
MODE = {"NOMINAL": 0, "DEGRADED": 1, "LIMP": 2, "HALT": 3}
ORIG = {"PROPOSED": 0, "RATE_LIMITED": 1, "SPEED_CAPPED": 2, "FALLBACK_PID": 3, None: 4}
GATE = {"STATISTICAL": 1, "PHYSICAL": 2, "DETERMINISTIC": 4}
MOD = {"IMU": 1, "GPS": 2, "LIDAR": 4}
BAD = {"clean": [], "pos_imu_bias": ["imu"], "pos_gps_bias": ["gps"], "pos_lidar_bias": ["lidar"], "pos_lidar_drift": ["lidar"],
       "pos_two_bias": ["imu", "gps"], "pos_two_drift": ["imu", "gps"], "speed_frozen": ["speed"], "speed_bias": ["speed"],
       "speed_low": ["speed"], "speed_drift": ["speed"], "speed_unit": ["speed"], "lat_frozen": ["lat"], "lat_bias": ["lat"],
       "lat_sign": ["lat"], "both_frozen": ["speed", "lat"], "imu_dropout": ["stream"]}
GNAME = {"STATISTICAL": "L6 statistical gate", "PHYSICAL": "L7 physical gate", "DETERMINISTIC": "L7 rule shield"}
MNAME = {"DEGRADED": "L8 fail-safe enters DEGRADED (cap 40 km/h)", "LIMP": "L8 fail-safe enters LIMP (cap 20 km/h)",
         "HALT": "L8 fail-safe enters HALT (stop; needs a manual reset)"}
clean_first = next(a for a in d["arms"] if a["id"] == "clean")["first"]


def r2(x):
    return 0 if x is None else round(x, 2)


arms = []
for a in d["arms"]:
    rows, out = a["rows"], []
    ev = []
    for k, v in a["first"].items():
        if k == "l1":
            ev.append([v[0], "L1 marks " + " + ".join(v[1]) + " position as unhealthy", 0])
        elif k.startswith("gate_"):
            same = clean_first.get(k) == v and a["id"] != "clean"
            ev.append([v, GNAME[k[5:]] + " first blocks a command", 1 if same else 0])
        else:
            ev.append([v, MNAME[k[5:]], 0])
    ev.sort()
    keep = range(len(rows))
    def col(i): return [r2(rows[j][i]) for j in keep]
    def ormask(i, table):
        res = []
        for j in keep:
            m = 0
            for r in rows[j:j + 1]:
                for x in r[i]: m |= table[x]
            res.append(m)
        return res
    arms.append(dict(id=a["id"], sensor=a["sensor"], defect=a["defect"], desc=a["desc"], bad=BAD[a["id"]], ev=ev,
                     vt=col(1), ve=col(2), dv=col(3), ye=col(4), sc=col(9), tr=col(11),
                     m="".join(str(MODE[rows[j][5]]) for j in keep), o="".join(str(ORIG[rows[j][6]]) for j in keep),
                     g=ormask(7, GATE), h=ormask(8, MOD),
                     b="".join("1" if (rows[j][13] or 0) > (rows[j][12] or 0) else "0" for j in keep)))
data = dict(seed=d["seed"], onset=d["onset"], ticks=d["ticks"], hz=d["hz"], step=d["every"], arms=arms)
html = (HERE / "sim_template.html").read_text(encoding="utf-8").replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
(ROOT / "mp_review_sim.html").write_text(html, encoding="utf-8", newline="\n")
print("wrote", ROOT / "mp_review_sim.html", len(html) // 1024, "KB")
c = arms[0]
print("clean dev vs y_est sample:", list(zip(c["dv"][60:66], c["ye"][60:66])))
