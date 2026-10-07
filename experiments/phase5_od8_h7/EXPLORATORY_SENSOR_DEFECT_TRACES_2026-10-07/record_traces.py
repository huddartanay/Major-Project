"""EXPLORATORY: record one closed-loop run per sensor defect for the 3D replay.
One dev seed, not pre-registered, not evidence for any claim."""
import json, math, sys, time
sys.path.insert(0, ".")
from astra.kernel.enums import SensorModality, StreamHealth
from astra.layers.l4_proposer.learned import LearnedPolicy
from benchmarks.e21_baseline import CHANNEL_SIGMAS, POLICY_PATH
from benchmarks.mechanism_logger import _l6_evidence
from training.closed_loop import DEFAULT_CHANNEL_SIGMAS, RedundantSensing, drive_closed_loop
from training.faults import FaultChannel, FaultInjector, bias, drift, dropout, stuck_at

SEED, ONSET, TICKS, EVERY = 20260731, 200, 2400, 4
LAST = TICKS - 1
IMU, GPS, LIDAR = SensorModality.IMU, SensorModality.GPS, SensorModality.LIDAR
V, A = FaultChannel.SPEED, FaultChannel.LATERAL_ACCELERATION


class Transform(FaultInjector):
    def __init__(self, key, k):
        super().__init__((), seed=SEED, sigmas=CHANNEL_SIGMAS)
        self._key, self._k = key, k
    def is_active(self, tick): return tick >= ONSET
    def drops_reading(self, tick): return False
    def corrupt(self, payload, *, tick):
        out = dict(payload)
        if tick >= ONSET: out[self._key] = out[self._key] * self._k
        return out


def inj(*specs): return FaultInjector(tuple(specs), seed=SEED, sigmas=CHANNEL_SIGMAS)
def pos(liars=(), b=0.0, d=0.0):
    if not liars: return RedundantSensing.build(sigmas=DEFAULT_CHANNEL_SIGMAS, seed=SEED)
    return RedundantSensing.build(sigmas=DEFAULT_CHANNEL_SIGMAS, seed=SEED, faulted=liars[0],
                                  also_faulted=tuple(liars[1:]), opens_at=ONSET, bias=b, drift_per_tick=d)
W = dict(first_tick=ONSET, last_tick=LAST)

# id: (sensor, defect, exact description, injector, sensing)
ARMS = {
 "clean":        ("none", "none", "No defect", lambda: inj(), lambda: pos()),
 "pos_imu_bias": ("Position: IMU", "constant offset", "IMU position reads +1.0 m to the side; GPS and LIDAR honest", lambda: inj(), lambda: pos((IMU,), b=1.0)),
 "pos_gps_bias": ("Position: GPS", "constant offset", "GPS position reads +1.0 m to the side; IMU and LIDAR honest", lambda: inj(), lambda: pos((GPS,), b=1.0)),
 "pos_lidar_bias": ("Position: LIDAR", "constant offset", "LIDAR position reads +1.0 m to the side; IMU and GPS honest", lambda: inj(), lambda: pos((LIDAR,), b=1.0)),
 "pos_lidar_drift": ("Position: LIDAR", "slow drift", "LIDAR position drifts sideways by 2 mm per tick (4 cm/s)", lambda: inj(), lambda: pos((LIDAR,), d=0.002)),
 "pos_two_bias": ("Position: IMU + GPS", "two sources agree on a lie", "IMU and GPS both read +1.0 m to the side; only LIDAR honest", lambda: inj(), lambda: pos((IMU, GPS), b=1.0)),
 "pos_two_drift": ("Position: IMU + GPS", "two sources drift together", "IMU and GPS both drift sideways by 2 mm per tick", lambda: inj(), lambda: pos((IMU, GPS), d=0.002)),
 "speed_frozen": ("Speed", "frozen", "Speed reading holds its last value", lambda: inj(stuck_at(V, **W)), lambda: pos()),
 "speed_bias":   ("Speed", "constant offset", "Speed reads 3.0 m/s too high", lambda: inj(bias(V, offset=3.0, **W)), lambda: pos()),
 "speed_low":    ("Speed", "constant offset", "Speed reads 3.0 m/s too low", lambda: inj(bias(V, offset=-3.0, **W)), lambda: pos()),
 "speed_drift":  ("Speed", "slow drift", "Speed reading drifts to 5.0 m/s too low over the run", lambda: inj(drift(V, final=-5.0, **W)), lambda: pos()),
 "speed_unit":   ("Speed", "wrong unit", "Speed reported in km/h instead of m/s (x3.6)", lambda: Transform("v", 3.6), lambda: pos()),
 "lat_frozen":   ("Lateral acceleration", "frozen", "Lateral-acceleration reading holds its last value", lambda: inj(stuck_at(A, **W)), lambda: pos()),
 "lat_bias":     ("Lateral acceleration", "constant offset", "Lateral acceleration reads 1.0 m/s2 too high", lambda: inj(bias(A, offset=1.0, **W)), lambda: pos()),
 "lat_sign":     ("Lateral acceleration", "sign flipped", "Lateral acceleration reported with the opposite sign", lambda: Transform("a", -1.0), lambda: pos()),
 "both_frozen":  ("Speed + lateral acceleration", "frozen", "Both readings hold their last values (the STEP 6 arm)", lambda: inj(stuck_at(V, **W), stuck_at(A, **W)), lambda: pos()),
 "imu_dropout":  ("IMU message stream", "stops sending", "IMU messages stop arriving (the STEP 6 dropout arm)", lambda: inj(dropout(**W)), lambda: pos()),
}


def f(x, n=3):
    try:
        x = float(x)
        return None if math.isnan(x) or math.isinf(x) else round(x, n)
    except Exception:
        return None


def run(policy, name):
    sensor, defect, desc, mk_inj, mk_pos = ARMS[name]
    rows, first = [], {}
    def obs(s):
        r = s.record
        bad = [m.value for m, h in r.frame_health if h is not StreamHealth.HEALTHY]
        gates = [g.gate.value for g in r.safety_verdict.gate_verdicts if g.verdict.value != "PASS"] if r.safety_verdict else []
        state = r.failsafe.state.value if r.failsafe else None
        if s.tick >= ONSET:
            if bad and "l1" not in first: first["l1"] = [s.tick, bad]
            for g in gates: first.setdefault("gate_" + g, s.tick)
            if state and state != "NOMINAL": first.setdefault("mode_" + state, s.tick)
        if s.tick % EVERY: return
        e = _l6_evidence(s)
        rows.append([s.tick, f(s.speed_mps), f(r.fast_state.speed) if r.fast_state else None, f(s.lane_deviation_m),
                     f(r.fast_state.position_y) if r.fast_state else None, state,
                     r.issued.origin.value if r.issued else None, gates, bad, f(e["non_conformity_score"]),
                     f(r.issued.command.values[2], 4) if r.issued else None, f(r.trust.trust_index) if r.trust else None,
                     f(r.issued.command.values[0]) if r.issued else None, f(r.issued.command.values[1]) if r.issued else None])
    drive_closed_loop(policy=policy, ticks=TICKS, seed=SEED, observer=obs, fault=mk_inj(), redundant=mk_pos())
    return dict(id=name, sensor=sensor, defect=defect, desc=desc, first=first, rows=rows)


if __name__ == "__main__":
    out = sys.argv[1]
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(ARMS)
    policy = LearnedPolicy.load(POLICY_PATH)
    res, t0 = [], time.time()
    for n in names:
        try:
            r = run(policy, n)
        except Exception as exc:  # noqa: BLE001
            r = dict(id=n, error=f"{type(exc).__name__}: {exc}"[:300])
        res.append(r)
        last = r.get("rows", [[None] * 6])[-1]
        print(f"[{time.time()-t0:5.0f}s] {n:16s} first={r.get('first')} end: v={last[1]} est={last[2]} dev={last[3]} mode={last[5]} {r.get('error','')}", flush=True)
    json.dump(dict(seed=SEED, onset=ONSET, ticks=TICKS, every=EVERY, hz=20,
                   cols=["tick", "v_true", "v_est", "dev_true", "y_est", "mode", "origin", "gates", "unhealthy", "score", "steer", "trust", "throttle", "brake"],
                   arms=res), open(out, "w"))
