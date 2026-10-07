"""EXPLORATORY: record runs with features that every paper experiment leaves off --
the L9 cold path (calibration search, shadow execution, safe exploration), a
changing environment, a tolerance of one bad position source, and defects that end.
One dev seed, not pre-registered, not evidence for any claim.

Usage (repository root): python <this file> <out.json> [arm,arm,...]
"""
import json, math, sys, time
sys.path.insert(0, ".")
from astra.kernel.enums import SensorModality, StreamHealth
from astra.layers.l4_proposer.learned import LearnedPolicy
from benchmarks.e21_baseline import CHANNEL_SIGMAS, POLICY_PATH
from benchmarks.mechanism_logger import _l6_evidence
from demo.dashboard import CERTIFIED, TUNNEL, cold_path
from training.closed_loop import DEFAULT_CHANNEL_SIGMAS, RedundantSensing, drive_closed_loop
from training.faults import FaultInjector, dropout

SEED, TICKS, EVERY = 20260731, 2400, 4
IMU, GPS, LIDAR = SensorModality.IMU, SensorModality.GPS, SensorModality.LIDAR
RAIN_NIGHT = (0.35, 0.5, 0.5)   # near the seeded rain_night profile's centroid
ENV = {"road": CERTIFIED, "tunnel": TUNNEL, "rain_night": RAIN_NIGHT}


def inj(*specs): return FaultInjector(tuple(specs), seed=SEED, sigmas=CHANNEL_SIGMAS)
def pos(liars=(), b=0.0, at=200):
    if not liars: return RedundantSensing.build(sigmas=DEFAULT_CHANNEL_SIGMAS, seed=SEED)
    return RedundantSensing.build(sigmas=DEFAULT_CHANNEL_SIGMAS, seed=SEED, faulted=liars[0],
                                  also_faulted=tuple(liars[1:]), opens_at=at, bias=b)

# id: dict(sensor, defect, desc, onset tick or None, off tick or None, env schedule [(tick, name)], injector, sensing, tolerated)
ARMS = {
 "env_change": dict(sensor="Environment", defect="none", desc="No sensor defect. The surroundings change: open road, then a tunnel no calibration covers, then road, then rain at night",
                    onset=None, off=None, env=[(0, "road"), (400, "tunnel"), (1000, "road"), (1500, "rain_night"), (2100, "road")], inj=lambda: inj(), pos=lambda: pos(), tol=0),
 "road_only":  dict(sensor="Environment", defect="none", desc="No sensor defect, open road throughout, with calibration search switched on",
                    onset=None, off=None, env=[(0, "road")], inj=lambda: inj(), pos=lambda: pos(), tol=0),
 "pos_gps_tol1": dict(sensor="Position: GPS", defect="constant offset", desc="GPS position reads +1.0 m to the side; the fail-safe is allowed to absorb one bad position source",
                    onset=200, off=None, env=[(0, "road")], inj=lambda: inj(), pos=lambda: pos((GPS,), b=1.0), tol=1),
 "pos_lidar_tol1": dict(sensor="Position: LIDAR", defect="constant offset", desc="LIDAR position reads +1.0 m to the side; the fail-safe is allowed to absorb one bad position source",
                    onset=200, off=None, env=[(0, "road")], inj=lambda: inj(), pos=lambda: pos((LIDAR,), b=1.0), tol=1),
 "pos_two_tol1": dict(sensor="Position: IMU + GPS", defect="two sources agree on a lie", desc="IMU and GPS both read +1.0 m to the side; tolerance is one, so two is still too many",
                    onset=200, off=None, env=[(0, "road")], inj=lambda: inj(), pos=lambda: pos((IMU, GPS), b=1.0), tol=1),
 "dropout_10s": dict(sensor="IMU message stream", defect="stops for 10 s, then returns", desc="IMU messages stop arriving for 10 s and then come back",
                    onset=200, off=400, env=[(0, "road")], inj=lambda: inj(dropout(first_tick=200, last_tick=399)), pos=lambda: pos(), tol=0),
 "tunnel_dropout": dict(sensor="IMU message stream", defect="stops for 10 s inside a tunnel", desc="The car is exploring inside a tunnel when IMU messages stop for 10 s",
                    onset=700, off=900, env=[(0, "road"), (300, "tunnel"), (1300, "road")], inj=lambda: inj(dropout(first_tick=700, last_tick=899)), pos=lambda: pos(), tol=0),
}


def f(x, n=3):
    try:
        x = float(x)
        return None if math.isnan(x) or math.isinf(x) else round(x, n)
    except Exception:
        return None


def run(policy, name):
    a = ARMS[name]
    rows, changes, box = [], [], {}
    sched = dict(a["env"])
    def assembled(built, *_):
        box["p"] = built.pipeline
        if a["tol"]:
            fs = built.pipeline._failsafe
            fs._settings = fs._settings.model_copy(update={"integrity_tolerated_faults": a["tol"]})
    last = {"mode": None, "out": None, "prof": None, "env": "road", "l1": ()}
    def obs(s):
        r = s.record
        if s.tick + 1 in sched:                       # takes effect on the next tick
            box["p"].enter_context(cold_path(ENV[sched[s.tick + 1]]))
        if s.tick in sched: last["env"] = sched[s.tick]; changes.append([s.tick, "env", sched[s.tick]])
        bad = tuple(m.value for m, h in r.frame_health if h is not StreamHealth.HEALTHY)
        gates = [g.gate.value for g in r.safety_verdict.gate_verdicts if g.verdict.value != "PASS"] if r.safety_verdict else []
        mode = r.failsafe.state.value if r.failsafe else None
        arb = r.arbitration
        out = arb.outcome.value if arb else None
        prof = arb.active_profile.name if arb else None
        if mode != last["mode"]: changes.append([s.tick, "mode", mode]); last["mode"] = mode
        if out != last["out"]: changes.append([s.tick, "arb", out, arb.candidate_profile.name if arb and arb.candidate_profile else None, f(arb.trust_score) if arb else None]); last["out"] = out
        if prof != last["prof"]: changes.append([s.tick, "profile", prof]); last["prof"] = prof
        if bad != last["l1"]: changes.append([s.tick, "l1", list(bad)]); last["l1"] = bad
        if s.tick % EVERY: return
        e = _l6_evidence(s)
        rows.append([s.tick, f(s.speed_mps), f(r.fast_state.speed) if r.fast_state else None, f(s.lane_deviation_m),
                     f(r.fast_state.position_y) if r.fast_state else None, mode,
                     r.issued.origin.value if r.issued else None, gates, list(bad), f(e["non_conformity_score"]),
                     f(r.issued.command.values[2], 4) if r.issued else None, f(r.trust.trust_index) if r.trust else None,
                     f(r.issued.command.values[0]) if r.issued else None, f(r.issued.command.values[1]) if r.issued else None,
                     last["env"], out, prof, f(arb.trust_score) if arb else None,
                     f(arb.calibration_divergence_index) if arb and arb.calibration_divergence_index is not None else None])
    drive_closed_loop(policy=policy, ticks=TICKS, seed=SEED, observer=obs, fault=a["inj"](), redundant=a["pos"](),
                      cold_path=cold_path(ENV[a["env"][0][1]]), on_assembled=assembled)
    return dict(id=name, sensor=a["sensor"], defect=a["defect"], desc=a["desc"], onset=a["onset"], off=a["off"], tol=a["tol"], changes=changes, rows=rows)


if __name__ == "__main__":
    out = sys.argv[1]
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(ARMS)
    policy = LearnedPolicy.load(POLICY_PATH)
    res, t0 = [], time.time()
    for n in names:
        try:
            r = run(policy, n)
        except Exception as exc:  # noqa: BLE001
            import traceback; traceback.print_exc()
            r = dict(id=n, error=f"{type(exc).__name__}: {exc}"[:300])
        res.append(r)
        print(f"[{time.time()-t0:5.0f}s] {n}", r.get("error", ""), flush=True)
        for c in r.get("changes", [])[:60]: print("     ", c)
        if r.get("rows"): print("      end:", r["rows"][-1][1:7], r["rows"][-1][14:])
    json.dump(dict(seed=SEED, ticks=TICKS, every=EVERY, hz=20, arms=res), open(out, "w"))
