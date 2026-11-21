"""v4 extra X1: why Ignited Spirit WIT helps Neo Universe (mechanism study on the v4 champion).

Ignited Spirit WIT (210052, white, wit-checked, random point in phase 0, 4 s base -> 9.6 s at 2400 m):
  type 28 lane move speed +0.015 and type 8 vision +5 m.
Engine (retail runtime used by the v77 profile: retail_physics.rs / retail lane movement; same rules in race_solver.rs): lateral speed = base 0.02*(0.3+0.001*P)*mod + sum(type-28 modifiers); and while any
type-28 skill is active, every tick after a tick with lane movement gets target speed + sqrt(0.0002*P).

Counterfactual clones of the skill keep its lottery, condition and duration and change only the effects, so a
race is identical in every variant until the skill fires (checked: the `clone` variant must equal `full`).
Neo's slot only; Kitasan and Ines keep the real skill.
  full        real skill
  clone       identical copy under a new id (validation)
  none        no effects
  vision      vision +5 m only
  lane        lane speed +0.015 only (with the moving-lane speed bonus)
  lane_bonus  lane speed +0.0001 only: the moving-lane speed bonus without faster lateral movement
  drop        skill removed (as in A6; the RNG stream then differs after initialization)
Part 1: outcomes, N races per variant (seeds 195M). Part 2: dense frames for Neo, M races (seeds 195.5M).
Usage: loh_v4_x1_ignited_wit.py N M"""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
from umasim import catalog as C, engine, mock, opt

N, M = int(sys.argv[1]), int(sys.argv[2])
out = opt.run_dir("v4-x1-ignited-wit")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()

SID, NEO = "210052", 2
T = C.skill_table()
base = T[SID]
def clone(new_id, lane=None, vision=None):
    e = copy.deepcopy(base)
    effs = []
    for f in e["alternatives"][0]["effects"]:
        if f["type"] == 28 and lane is not None:
            if lane == 0:
                continue
            f["modifier"] = lane
        if f["type"] == 8 and vision is not None:
            if vision == 0:
                continue
            f["modifier"] = vision
        effs.append(f)
    e["alternatives"][0]["effects"] = effs
    T[new_id] = e
    return new_id
IDS = {"full": SID, "clone": clone("299001"), "none": clone("299002", lane=0, vision=0),
       "vision": clone("299003", lane=0), "lane": clone("299004", vision=0),
       "lane_bonus": clone("299005", lane=1, vision=0)}
# a skill with no effects at all may be dropped by the engine; keep a zero-value vision effect instead
T["299002"]["alternatives"][0]["effects"] = [dict(base["alternatives"][0]["effects"][1], modifier=0)]
log("effects:", {k: [(f["type"], f["modifier"]) for f in T[v]["alternatives"][0]["effects"]] for k, v in IDS.items()})

champ = json.loads(Path("data/loh/my_team_v4_champion.json").read_text())
def team(var):
    t = copy.deepcopy(champ)
    sk = t[NEO]["skills"]; k = sk.index("Ignited Spirit WIT")
    if var == "drop":
        sk.pop(k)
    else:
        sk[k] = IDS[var]
    return t
VARS = ["full", "clone", "none", "vision", "lane", "lane_bonus", "drop"]

# ---------------------------------------------------------------- part 1: outcomes
t0 = time.time()
seeds = list(range(195_000_000, 195_000_000 + N))
df = mock.evaluate({v: team(v) for v in VARS}, seeds)
df.to_csv(out / "outcomes.csv.gz", index=False)
log(f"part 1: {len(df)} races {time.time() - t0:.0f}s")
w = df.pivot(index="seed", columns="variant", values="top3") * 100
neo = df.assign(neo=(df.p2 <= 3) * 100.0).pivot(index="seed", columns="variant", values="neo")
pts = df.pivot(index="seed", columns="variant", values="points")
def paired(x, a, b):
    d = x[a] - x[b]; se = d.std(ddof=1) / np.sqrt(len(d))
    return d.mean(), d.mean() - 1.96 * se, d.mean() + 1.96 * se
rows = []
for v in VARS:
    r = {"variant": v, "team_top3": w[v].mean(), "neo_top3": neo[v].mean(), "points": pts[v].mean()}
    for ref in ("none", "full"):
        if v != ref:
            for name, x in (("team", w), ("neo", neo)):
                m_, lo, hi = paired(x, v, ref)
                r.update({f"{name}_vs_{ref}": m_, f"{name}_vs_{ref}_lo": lo, f"{name}_vs_{ref}_hi": hi})
    r["identical_to_full_%"] = 100 * (df[df.variant == v].sort_values("seed")[["p0", "p1", "p2"]].values ==
                                      df[df.variant == "full"].sort_values("seed")[["p0", "p1", "p2"]].values).all(1).mean()
    rows.append(r)
oc = pd.DataFrame(rows); oc.to_csv(out / "outcome_summary.csv", index=False)
pd.set_option("display.width", 250)
log(oc.round(2).to_string())

# ---------------------------------------------------------------- part 2: dense frames, Neo only
mm = mock.MockMatchup(champ)
DT = 1 / 15
MARKS = (400, 1000, 1600, 2000)
def features(rep, var, seed, req):
    fr = rep["frames"]; res = rep["results"]
    t = np.array([f["t"] for f in fr])
    H = [f["horses"] for f in fr]
    pos = np.array([h[NEO]["pos"] for h in H]); lane = np.array([h[NEO]["lane"] for h in H])
    spd = np.array([h[NEO]["speed"] for h in H]); blk = np.array([h[NEO]["blockFrontHorseIndex"] >= 0 for h in H])
    allpos = np.array([[x["pos"] for x in h] for h in H])
    ev = [e for e in rep.get("skillEvents", []) if e["horseIndex"] == NEO and str(e["skillId"]) == str(IDS.get(var, SID))]
    r = {"variant": var, "seed": seed, "gate": req["horses"][NEO]["gateIndex"] + 1, "place": res[NEO]["finishOrder"] + 1,
         "finish_t": res[NEO]["finishTimeRaw"], "fired": bool(ev), "rushed": res[NEO].get("rushingStartCount", 0) > 0,
         "late_start": res[NEO].get("startDelayTime", 0) > 0.08}
    if ev:
        ta, du = ev[0]["t"], ev[0]["duration"]
        k0 = int(np.searchsorted(t, ta)); k1 = int(np.searchsorted(t, ta + du))
        win = slice(k0, k1)
        dl = np.abs(np.diff(lane[max(k0 - 1, 0):k1]))
        r.update({"act_t": ta, "act_pos": float(np.interp(ta, t, pos)), "act_lane": float(np.interp(ta, t, lane)),
                  "act_blocked": bool(blk[min(k0, len(blk) - 1)]),
                  "win_moving_s": float((dl > 1e-7).sum() * DT), "win_lateral": float(dl.sum()),
                  "win_blocked_s": float(blk[win].sum() * DT), "win_mean_speed": float(spd[win].mean()),
                  "pos_end_win": float(np.interp(ta + du, t, pos)), "pos_end_win_plus10": float(np.interp(ta + du + 10, t, pos)),
                  "rank_end_win": int((allpos[min(k1, len(t) - 1)] > pos[min(k1, len(t) - 1)]).sum() + 1)})
    for a, b, nm in ((0, 400, "p0"), (400, 1600, "p1"), (1600, 2000, "p2"), (2000, 2400, "p3")):
        m_ = (pos >= a) & (pos < b)
        r[f"blocked_s_{nm}"] = float(blk[m_].sum() * DT)
    for x in MARKS:
        k = int(np.searchsorted(pos, x))
        k = min(k, len(t) - 1)
        r[f"t_{x}"] = float(np.interp(x, pos[max(k - 1, 0):k + 1], t[max(k - 1, 0):k + 1])) if k > 0 else float(t[k])
        r[f"rank_{x}"] = int((allpos[k] > pos[k]).sum() + 1)
        r[f"lane_{x}"] = float(lane[k])
    return r

t0 = time.time()
mseeds = list(range(195_500_000, 195_500_000 + M))
MV = ["full", "none", "vision", "lane", "lane_bonus"]
feats = []
for v in MV:
    mmv = mock.MockMatchup(team(v))
    for k in range(0, M, 40):
        part = mseeds[k:k + 40]
        reqs = []
        for s in part:
            q = mmv.request(s); q["omitFrames"] = False; q["retainAllFrames"] = True; reqs.append(q)
        reps = engine.run_requests(reqs)
        for s, q, rp in zip(part, reqs, reps):
            if "error" in rp:
                raise engine.EngineError(rp["error"])
            feats.append(features(rp, v, s, q))
        del reps
    log(f"part 2 {v}: {M} races {time.time() - t0:.0f}s")
F = pd.DataFrame(feats); F.to_csv(out / "neo_frames_features.csv.gz", index=False)
log("done", out)
