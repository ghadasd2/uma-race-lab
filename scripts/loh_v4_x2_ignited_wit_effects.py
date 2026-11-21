"""v4 extra X2: side effects of Ignited Spirit WIT on Neo — position keep (pace down etc.), blocking, and races
where the skill hurts. Needs the engine built with the posKeepLog observation (data/globalsim-observation.patch).

Variants (Neo's slot only, same activation lottery/condition/duration as the real skill, see X1):
  full     real skill (210052)
  none     no-effect clone (vision +0)
  placebo  HP +0.01 % clone: a near-zero change that only shows how often races flip by knock-on divergence
Part A: N races per variant, no frames (seeds 195M, same races as X1 part 1): outcomes + Neo position-keep log.
Part B: M races, dense frames, full and none (seeds 195.5M; the first 2,500 are the X1 frame races): blocking.
Usage: loh_v4_x2_ignited_wit_effects.py N M"""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
from umasim import catalog as C, engine, loh, mock, opt

N, M = int(sys.argv[1]), int(sys.argv[2])
out = opt.run_dir("v4-x2-ignited-wit-effects")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()

SID, NEO, DT = "210052", 2, 1 / 15
T = C.skill_table(); base = T[SID]
def clone(new_id, effects):
    e = copy.deepcopy(base); e["alternatives"][0]["effects"] = effects; T[new_id] = e; return new_id
vis = base["alternatives"][0]["effects"][1]
IDS = {"full": SID, "none": clone("299002", [dict(vis, modifier=0)]),
       "placebo": clone("299006", [dict(vis, type=9, modifier=1)])}
log("effects:", {k: [(f["type"], f["modifier"]) for f in T[v]["alternatives"][0]["effects"]] for k, v in IDS.items()})
champ = json.loads(Path("data/loh/my_team_v4_champion.json").read_text())
def team(var):
    t = copy.deepcopy(champ); sk = t[NEO]["skills"]; sk[sk.index("Ignited Spirit WIT")] = IDS[var]; return t
MODES = {1: "pace_down", 2: "pace_up", 3: "pace_up_ex", 4: "speed_up", 5: "overtake"}


def poskeep(rep, act_t, gate_idx):
    """Neo's position-keep intervals -> per-mode count / seconds / metres, pace-down split by race window.
    posKeepLog is indexed by solver = gate order (like duelLog/spotLog); intervals still open when position keep
    stops being evaluated are counted but add no time."""
    ev = sorted((e for e in rep.get("posKeepLog", []) if e["horseIndex"] == gate_idx), key=lambda e: e["t"])
    r = {f"{m}_{k}": 0.0 for m in MODES.values() for k in ("n", "s", "m")}
    r.update({"pd_s_before": 0.0, "pd_s_window": 0.0, "pd_s_after20": 0.0, "pd_s_later": 0.0,
              "pd_first_pos": np.nan, "pd_first_gap": np.nan, "pd_n_window_or_after20": 0})
    cur, t0, p0 = 0, None, None
    def close(t1, p1):
        if cur == 0 or t0 is None:
            return
        nm = MODES[cur]; r[f"{nm}_s"] += t1 - t0; r[f"{nm}_m"] += p1 - p0
        if cur == 1 and act_t is not None:
            a, b = act_t, act_t + 9.6
            for lo, hi, key in ((-1e9, a, "pd_s_before"), (a, b, "pd_s_window"), (b, b + 20, "pd_s_after20"), (b + 20, 1e9, "pd_s_later")):
                r[key] += max(0.0, min(t1, hi) - max(t0, lo))
    for e in ev:
        close(e["t"], e["pos"])
        cur, t0, p0 = int(e["mode"]), e["t"], e["pos"]
        if cur:
            r[f"{MODES[cur]}_n"] += 1
            if cur == 1:
                if np.isnan(r["pd_first_pos"]):
                    r["pd_first_pos"], r["pd_first_gap"] = e["pos"], e["gap"]
                if act_t is not None and act_t <= e["t"] < act_t + 29.6:
                    r["pd_n_window_or_after20"] += 1
    r["open_at_end"] = MODES.get(cur, "")
    return r


def race_row(rep, var, seed, req):
    res = rep["results"]
    ev = [e for e in rep.get("skillEvents", []) if e["horseIndex"] == NEO and str(e["skillId"]) == IDS[var]]
    act_t = ev[0]["t"] if ev else None
    pl = [res[k]["finishOrder"] + 1 for k in range(3)]
    row = {"variant": var, "seed": seed, "fired": bool(ev), "act_t": act_t, "place": pl[2], "finish_t": res[NEO]["finishTimeRaw"],
           "team_top3": 100 * sum(p <= 3 for p in pl) / 3, "points": sum(loh.points(p) for p in pl),
           "rushed": res[NEO].get("rushingStartCount", 0) > 0, "hp_empty": bool(res[NEO].get("hpEmptyOnRace")),
           "spurt_start": res[NEO].get("lastSpurtStartDistance", -1)}
    row["gate"] = req["horses"][NEO]["gateIndex"] + 1
    row.update(poskeep(rep, act_t, req["horses"][NEO]["gateIndex"]))
    return row


def run(var, seeds, frames):
    mm = mock.MockMatchup(team(var)); rows = []
    step = 40 if frames else 1000
    for k in range(0, len(seeds), step):
        part = seeds[k:k + step]; reqs = []
        for s in part:
            q = mm.request(s)
            if frames:
                q["omitFrames"] = False; q["retainAllFrames"] = True
            reqs.append(q)
        for s, q, rp in zip(part, reqs, engine.run_requests(reqs)):
            if "error" in rp:
                raise engine.EngineError(rp["error"])
            r = race_row(rp, var, s, q)
            if frames:
                r.update(blocking(rp, r["act_t"]))
            rows.append(r)
    return rows


def blocking(rep, act_t):
    fr = rep["frames"]; t = np.array([f["t"] for f in fr])
    pos = np.array([f["horses"][NEO]["pos"] for f in fr]); blk = np.array([f["horses"][NEO]["blockFrontHorseIndex"] >= 0 for f in fr])
    lane = np.array([f["horses"][NEO]["lane"] for f in fr])
    r = {}
    for a, b, nm in ((0, 400, "p0"), (400, 1600, "p1"), (1600, 2000, "p2"), (2000, 2400, "p3"), (0, 2400, "all")):
        m_ = (pos >= a) & (pos < b); x = blk & m_
        r[f"blk_s_{nm}"] = float(x.sum() * DT)
        r[f"blk_ep_{nm}"] = int(((x[1:]) & (~x[:-1])).sum() + (1 if len(x) and x[0] else 0))
        r[f"blk_any_{nm}"] = bool(x.any())
    if act_t is not None:
        w = (t >= act_t) & (t < act_t + 9.6)
        r["blk_s_window"] = float((blk & w).sum() * DT); r["blk_any_window"] = bool((blk & w).any())
        r["pos_end_win"] = float(np.interp(act_t + 9.6, t, pos))
        r["moving_s_window"] = float((np.abs(np.diff(lane)) > 1e-7)[w[1:]].sum() * DT)
    k = min(int(np.searchsorted(pos, 1600)), len(pos) - 1)
    r["rank_1600"] = int((np.array([h["pos"] for h in fr[k]["horses"]]) > pos[k]).sum() + 1)
    return r


t0 = time.time()
seeds = list(range(195_000_000, 195_000_000 + N))
A = []
for v in ("full", "none", "placebo"):
    A += run(v, seeds, False); log(f"part A {v}: {N} races {time.time() - t0:.0f}s")
A = pd.DataFrame(A); A.to_csv(out / "partA_races.csv.gz", index=False)
mseeds = list(range(195_500_000, 195_500_000 + M))
B = []
for v in ("full", "none"):
    B += run(v, mseeds, True); log(f"part B {v}: {M} races {time.time() - t0:.0f}s")
B = pd.DataFrame(B); B.to_csv(out / "partB_races.csv.gz", index=False)
log("done", out)
