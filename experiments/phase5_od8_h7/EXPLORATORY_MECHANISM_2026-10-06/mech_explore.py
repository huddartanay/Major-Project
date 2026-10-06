"""EXPLORATORY (dev seeds, not pre-registered).
Is the gate silent under IMU loss because of the sensor loss, or because L8 has already stopped the car?
Arms: clean | imu_dropout (governed) | imu_dropout with L8's integrity path neutralised (car keeps driving)."""
import json, math, sys, statistics as st
sys.path.insert(0, ".")
from astra.layers.l4_proposer.learned import LearnedPolicy
from benchmarks.e21_baseline import CHANNEL_SIGMAS, POLICY_PATH, _injector_sustained, _sensing_sustained
from benchmarks.mechanism_logger import _l6_evidence
from training.closed_loop import drive_closed_loop
from training.faults import FaultInjector

THR = 3.7024
BIG = 10**9

def neutralise_integrity(built, *_):
    m = getattr(built.pipeline, "_failsafe")
    s = m._settings
    m._settings = s.model_copy(update={"integrity_threshold_degraded": BIG,
                                       "integrity_threshold_limp": BIG,
                                       "integrity_threshold_halt": BIG})

def run(policy, seed, fault, neutral, ticks=3400):
    inj = _injector_sustained(fault, None, seed) if fault else FaultInjector((), seed=seed, sigmas=CHANNEL_SIGMAS)
    rows = []
    def obs(s):
        e = _l6_evidence(s)
        r = s.record
        rows.append((s.tick, s.speed_mps, abs(s.lane_deviation_m), r.failsafe.state.value if r.failsafe else None,
                     e["non_conformity_score"], e["departure"], e["sigma"],
                     float(r.fast_state.speed) if r.fast_state is not None else math.nan))
    drive_closed_loop(policy=policy, ticks=ticks, seed=seed, observer=obs, fault=inj,
                      redundant=_sensing_sustained(fault or "", None, seed, active=bool(fault)),
                      on_assembled=neutralise_integrity if neutral else None)
    return rows

def summ(rows, lo=400, hi=3400):
    w = [r for r in rows if lo <= r[0] < hi and not math.isnan(r[4])]
    sc = sorted(r[4] for r in w); n = len(sc)
    q = lambda p: sc[min(n - 1, int(p * n))]
    states = {}
    for r in w: states[r[3]] = states.get(r[3], 0) + 1
    return dict(n=n, alarm=round(sum(s > THR for s in sc) / n, 4), p50=round(q(.5), 3), p95=round(q(.95), 3),
                p99=round(q(.99), 3), score_sd=round(st.pstdev(sc), 3),
                dep_sd=round(st.pstdev([r[5] for r in w]), 4), sigma_med=round(st.median(r[6] for r in w), 4),
                true_speed=round(st.mean(r[1] for r in w), 2), est_speed=round(st.mean(r[7] for r in w), 2),
                est_speed_sd=round(st.pstdev([r[7] for r in w]), 5),
                max_abs_dev=round(max(r[2] for r in w), 2), states=states)

if __name__ == "__main__":
    policy = LearnedPolicy.load(POLICY_PATH)
    out = []
    for seed in range(20260731, 20260731 + int(sys.argv[1])):
        for label, fault, neutral in (("clean", None, False), ("clean_L8int_off", None, True),
                                      ("dropout_governed", "imu_dropout", False),
                                      ("dropout_L8int_off", "imu_dropout", True)):
            s = summ(run(policy, seed, fault, neutral)); s.update(seed=seed, arm=label)
            out.append(s); print(json.dumps(s), flush=True)
    json.dump(out, open(sys.argv[2], "w"), indent=1)
