"""Exploratory probe (dev seeds only, not a pre-registered experiment):
does L8 step DOWN to a less severe mode while a sustained fault is still active,
and if so, which counter allowed it?
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")
from astra.kernel.enums import StreamHealth
from astra.layers.l4_proposer.learned import LearnedPolicy
from benchmarks.e21_baseline import (
    CHANNEL_SIGMAS,
    FAULT_FIRST,
    POLICY_PATH,
    _injector_sustained,
    _sensing_sustained,
    _severity,
)
from training.closed_loop import drive_closed_loop
from training.faults import FaultInjector

RANK = {"NOMINAL": 0, "DEGRADED": 1, "LIMP": 2, "HALT": 3}


def run(policy, fault, seed, ticks):
    active = fault is not None
    mag = None if fault is None else _severity(fault)
    inj = (
        _injector_sustained(fault, mag, seed)
        if active
        else FaultInjector((), seed=seed, sigmas=CHANNEL_SIGMAS)
    )
    rows = []

    def obs(s):
        r = s.record
        fs = r.failsafe
        v = r.safety_verdict
        rows.append(
            (
                s.tick,
                fs.state.value if fs else None,
                fs.ood_counter if fs else None,
                fs.integrity_counter if fs else None,
                bool(v.is_blocking) if v is not None else None,
                any(h is not StreamHealth.HEALTHY for _, h in r.frame_health),
            )
        )

    drive_closed_loop(
        policy=policy,
        ticks=ticks,
        seed=seed,
        observer=obs,
        fault=inj,
        redundant=_sensing_sustained(fault or "", mag, seed, active=active),
    )
    return rows


def analyse(rows, active):
    peak = 0
    events = []
    for i in range(1, len(rows)):
        t, st, ood, integ, _blk, unhealthy = rows[i]
        prev = rows[i - 1][1]
        if st is None or prev is None:
            continue
        if t >= FAULT_FIRST:
            peak = max(peak, RANK[st])
        if RANK[st] < RANK[prev] and (not active or t >= FAULT_FIRST):
            events.append(
                {
                    "tick": t,
                    "from": prev,
                    "to": st,
                    "ood": ood,
                    "integrity": integ,
                    "l1_unhealthy": unhealthy,
                }
            )
    after = [r for r in rows if r[0] >= FAULT_FIRST]
    nominal_frac = sum(r[1] == "NOMINAL" for r in after) / max(len(after), 1)
    veto_frac = sum(bool(r[4]) for r in after) / max(len(after), 1)
    unhealthy_frac = sum(r[5] for r in after) / max(len(after), 1)
    return {
        "peak": next(k for k, v in RANK.items() if v == peak),
        "final": rows[-1][1],
        "n_deescalations": len(events),
        "first_deesc": events[:3],
        "nominal_frac_after_onset": round(nominal_frac, 3),
        "veto_frac_after_onset": round(veto_frac, 4),
        "l1_unhealthy_frac_after_onset": round(unhealthy_frac, 3),
    }


if __name__ == "__main__":
    ticks = int(sys.argv[1])
    seeds = int(sys.argv[2])
    faults = sys.argv[3].split(",")
    out = Path(sys.argv[4])
    policy = LearnedPolicy.load(POLICY_PATH) if hasattr(LearnedPolicy, "load") else None
    res = []
    for f in faults:
        fault = None if f == "clean" else f
        for i in range(seeds):
            seed = 20260731 + i
            t0 = time.time()
            rows = run(policy, fault, seed, ticks)
            a = analyse(rows, fault is not None)
            a.update(fault=f, seed=seed, secs=round(time.time() - t0, 1))
            res.append(a)
            print(json.dumps(a), flush=True)
    out.write_text(json.dumps(res, indent=1))
