"""Consistency checks on the scenarios packed into mp_review_sim.html.

Usage (this folder): python check_sim.py

Checks that every scenario's data agrees with itself and with the rules the page describes:
speed caps per mode, HALT latched, safe-exploration envelope and exit, shadow-before-commit
calibration switching, events that match the mode / flags at their time, recovery after a defect ends.
Recorded runs are checked too, but there a failed rule is a finding about the code, not a page bug.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
html = (HERE.parents[2] / "mp_review_sim.html").read_text(encoding="utf-8")
DATA, _ = json.JSONDecoder().raw_decode(html[html.index('{"seed":'):])
DT = DATA["step"] / DATA["hz"]
CAP = {1: 40 / 3.6, 2: 20 / 3.6}
SETTLE = 6.0                     # s allowed for the car to slow down to a new cap
MODES = ["NOMINAL", "DEGRADED", "LIMP", "HALT"]
SENS = {"imu", "gps", "lidar", "speed", "lat", "stream"}
BITS = {"IMU": 1, "GPS": 2, "LIDAR": 4}


def held(s, i, v):
    """Seconds value v has been held at tick i in sequence s."""
    j = i
    while j > 0 and s[j - 1] == v:
        j -= 1
    return (i - j) * DT


def tick(t, n):
    return min(n - 1, -int(-t // DT))    # first tick at or after t


def check(a):
    P, W = [], []                        # problems, notes
    n = len(a["vt"])
    m = [int(c) for c in a["m"]]
    o = [int(c) for c in a["o"]]
    h = [int(c) for c in a["h"]]
    arb = [int(c) for c in a.get("arb", "1" * n)]
    for k in ("ve", "m", "o", "h", "b", "dv", "ye", "sc", "g", "env", "arb", "pf"):
        if k in a and len(a[k]) != n:
            P.append(f"field {k} has {len(a[k])} ticks, expected {n}")
    if set(a["bad"]) - SENS:
        P.append(f"unknown sensor in bad: {set(a['bad']) - SENS}")
    if a["bad"] and a["on"] is None:
        P.append("defective sensors listed but no defect start time")
    if min(a["vt"]) < 0:
        P.append("negative speed")

    for i in range(n):
        t, v = i * DT, a["vt"][i]
        if m[i] in CAP and held(m, i, m[i]) >= SETTLE and v > CAP[m[i]] + 0.3:
            P.append(f"{t:.1f} s: {v * 3.6:.0f} km/h above the {MODES[m[i]]} cap"); break
    for i in range(n):
        if m[i] == 3 and held(m, i, 3) >= 8 and a["vt"][i] > 0.3:
            P.append(f"{i * DT:.1f} s: still moving {a['vt'][i] * 3.6:.0f} km/h 8 s into HALT"); break
    if 3 in m and any(x != 3 for x in m[m.index(3):]):
        P.append("left HALT: HALT must be latched")

    # safe exploration: half speed, inside the envelope, and it should end
    if 5 in arb:
        for i in range(n):
            if arb[i] == 5 and held(arb, i, 5) >= SETTLE and a["vt"][i] > 20 / 3.6 + 0.3:
                j = next((k for k in range(i, n) if arb[k] != 5 or a["vt"][k] <= 20 / 3.6 + 0.3), n)
                (P if a["kind"] == "design" else W).append(f"{i * DT:.1f} s: exploring at {a['vt'][i] * 3.6:.0f} km/h; reaches half speed only {(j - arb.index(5)) * DT:.1f} s after exploration starts"); break
        if any(arb[i] == 5 and arb[i - 1] == 5 and o[i] == 0 for i in range(1, n)):
            P.append("exploring while the learned controller drives unrestricted")
        if arb[-1] == 5:
            (P if a["kind"] == "design" else W).append("safe exploration never ends (one-way door)")
        else:
            W.append(f"exploration from {arb.index(5) * DT:.1f} s to {(n - 1 - arb[::-1].index(5)) * DT + DT:.1f} s")
    if any(o[i] == 5 and arb[i] != 5 for i in range(n)) and a["kind"] == "design":
        P.append("command marked 'inside exploration envelope' while L9 is not exploring")

    # calibration: shadow first, profile changes only at a commit
    if "pf" in a:
        for i in range(1, n):
            if arb[i] == 3 and arb[i - 1] != 3 and 2 not in arb[max(0, i - 50):i]:
                P.append(f"{i * DT:.1f} s: switch committed without a shadow test before it")
            if a["pf"][i] != a["pf"][i - 1]:
                if 3 not in arb[max(0, i - 2):i + 2]:
                    (P if a["kind"] == "design" else W).append(f"{i * DT:.1f} s: calibration changed without a commit")
                else:
                    s = i - 1
                    while s > 0 and arb[s] in (2, 3):
                        s -= 1
                    W.append(f"{i * DT:.1f} s: switched to '{a['pn'][int(a['pf'][i])]}' after {(i - 1 - s) * DT:.1f} s of shadow")
        env = a.get("env", "0" * n)
        for i in range(1, n):
            if env[i] != env[i - 1] and a["kind"] == "design":
                if not any(arb[j] in (2, 5) or (arb[j] == 1 and arb[j - 1] == 5) for j in range(i, min(n, i + 15))):
                    P.append(f"{i * DT:.1f} s: surroundings changed but L9 did not react within 3 s")

    # recovery after a defect that ends
    if a["off"] is not None and a["kind"] == "design" and 3 not in m:
        if m[-1] != 0:
            P.append(f"defect ended at {a['off']} s but the mode ends in {MODES[m[-1]]}")
        if h[-1]:
            P.append("defect ended but a sensor is still flagged at the end")
        if a["vt"][-1] < 10:
            P.append(f"defect ended but the car ends at {a['vt'][-1] * 3.6:.0f} km/h")
    # LIMP should not be driven by the unrestricted learned controller
    if a["kind"] == "design" and any(m[i] == 2 and o[i] == 0 for i in range(n)):
        P.append("learned controller drives unrestricted in LIMP")

    # events must agree with the data at their time
    for t, text, *_ in a["ev"]:
        i = tick(t, n)
        mm = re.search(r"L8 (?:enters|returns to|steps back(?: one level)? to|back to) (NOMINAL|DEGRADED|LIMP|HALT)", text)
        if mm and m[i] != MODES.index(mm.group(1)):
            P.append(f"event at {t} s says {mm.group(1)} but the mode is {MODES[m[i]]}")
        mm = re.search(r"L1 marks (?:the )?([A-Z +]+?)(?: stream| position| as)", text)
        if mm and a["kind"] != "rec":
            for s in re.findall(r"IMU|GPS|LIDAR", mm.group(1)):
                if not h[i] & BITS[s]:
                    P.append(f"event at {t} s says L1 flags {s} but the flag is off")
        if a["kind"] == "design" and re.search(r"(?:L6|lateral tracker|monitor \(L6\)) alarms", text) and a.get("g") and not int(a["g"][i]) & 1:
            P.append(f"event at {t} s says L6 alarms but the gate is quiet")
        if a["kind"] == "design" and "Exploration ends" in text and arb[i] == 5:
            P.append(f"event at {t} s says exploration ends but L9 is still exploring")
    return P, W


bad = 0
for kind in ("design", "feat", "rec"):
    print(f"\n== {kind}")
    for a in DATA["arms"]:
        if a["kind"] != kind:
            continue
        P, W = check(a)
        bad += bool(P) and kind == "design"
        print(f"{'FAIL' if P else ' ok '}  {a['id']:18s} {'; '.join(P)}")
        for w in W:
            print(f"      {'':18s} . {w}")
print(f"\n{bad} design scenario(s) with problems")
