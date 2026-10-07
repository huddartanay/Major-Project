"""EXPLORATORY (dev seeds): what does the gate's score track, and why is it lower under a frozen estimate?"""
import importlib.util, json, math, statistics as st, sys
sys.path.insert(0, ".")
spec = importlib.util.spec_from_file_location("s6", "experiments/phase5_od8_h7/STEP6_MECHANISM_FROZEN_ESTIMATE/step6_run.py")
s6 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s6)
from astra.layers.l4_proposer.learned import LearnedPolicy
from benchmarks.mechanism_logger import _l6_evidence
from training.closed_loop import DEFAULT_CHANNEL_SIGMAS, RedundantSensing, drive_closed_loop

def run(policy, arm, seed):
    rows = []
    def obs(s):
        if not (400 <= s.tick < 3400): return
        r = s.record; e = _l6_evidence(s)
        if math.isnan(e["departure"]) or r.fast_state is None: return
        rows.append(dict(dep=e["departure"], est=tuple(float(x) for x in r.fast_state.mean),
                         prop=tuple(r.proposal.command.values), pred=tuple(r.prediction.command.values),
                         v_true=s.speed_mps, a_true=s.lateral_acceleration_mps2, y_true=s.lane_deviation_m))
    drive_closed_loop(policy=policy, ticks=3400, seed=seed, observer=obs, fault=s6._injector(arm, seed),
                      redundant=RedundantSensing.build(sigmas=DEFAULT_CHANNEL_SIGMAS, seed=seed))
    return rows

def corr(a, b):
    ma, mb = st.fmean(a), st.fmean(b)
    sa, sb = st.pstdev(a), st.pstdev(b)
    if sa == 0 or sb == 0: return float("nan")
    return st.fmean((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)

if __name__ == "__main__":
    policy = LearnedPolicy.load(s6.POLICY_PATH)
    print("fast_state fields:", [f for f in dir(__import__("astra.contracts.estimation", fromlist=["x"]).FastStateEstimate) if not f.startswith("_")][:25])
    for seed in (20260731, 20260733, 20260735):
        data = {arm: run(policy, arm, seed) for arm in ("clean", "stuck")}
        for arm, rows in data.items():
            dep = [r["dep"] for r in rows]
            print(f"\n== seed {seed} {arm}: n={len(rows)} dep mean={st.fmean(dep):.5f} sd={st.pstdev(dep):.5f} p95={sorted(dep)[int(.95*len(dep))]:.5f}")
            for i in range(len(rows[0]["est"])):
                x = [r["est"][i] for r in rows]
                print(f"   est[{i}] mean={st.fmean(x):9.4f} sd={st.pstdev(x):8.5f} corr(dep)={corr(dep, x):+.3f} corr(dep,|x|)={corr(dep, [abs(v) for v in x]):+.3f}")
            for i in range(3):
                p = [r["prop"][i] for r in rows]; q = [r["pred"][i] for r in rows]
                print(f"   prop[{i}] mean={st.fmean(p):+.5f} sd={st.pstdev(p):.5f} corr(dep)={corr(dep, p):+.3f} | pred[{i}] mean={st.fmean(q):+.5f} sd={st.pstdev(q):.5f} corr(dep)={corr(dep, q):+.3f}")
            pn = [math.sqrt(sum(c * c for c in r["prop"])) for r in rows]
            print(f"   |prop| mean={st.fmean(pn):.5f} sd={st.pstdev(pn):.5f} corr(dep)={corr(dep, pn):+.3f}; true v mean={st.fmean(r['v_true'] for r in rows):.2f}")
