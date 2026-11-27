"""v4 extra X6: does Angling and Scheming (inherited, 900201: +0.2 m/s^2 for 5.76 s when 1st on a corner in the final leg)
on the front runners reduce dueling? Team = v4 champion fronts + Neo's X5 build (no Ignited Spirit WIT).
Variants (added on top, cap/ESP ignored as asked): base, Kitasan +A&S, Ines +A&S, both +A&S, and the same three with a
no-effect clone of the skill ("+null": same activation lottery, so each race is identical to its +A&S twin until the
skill fires; real - null is the clean causal effect). Paired seeds 200M.
Per race (downsampled frames, ~1 s): place/top-3/points/HP for my umas; per front: A&S fired / where, duel count, start,
length, and duel PARTNER (both runners of a duel share its start time); Kitasan-Ines gap and speed difference when the
leading one of the two reaches 1625 m (final corner) and 1875 m (final straight), and who leads.
Usage: loh_v4_x6_angling.py N [RUN_DIR]"""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
from umasim import engine, loh, mock, opt

N = int(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else opt.run_dir("v4-x6-angling")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()
AS = "900201"
# no-effect clone (same lottery/condition/duration, accel 0): races are identical to the real-skill variant until it fires
from umasim import catalog as C
T = C.skill_table(); NULL = "299101"
T[NULL] = copy.deepcopy(T[AS])
for a in T[NULL]["alternatives"]:
    for f in a["effects"]:
        f["modifier"] = 0
champ = json.loads(Path("data/loh/my_team_v4_champion.json").read_text())
champ[2] = json.loads(Path("data/loh/my_team_v4_neo_no_isw.json").read_text())[2]
def team(kit=False, ines=False, sid=AS):
    t = copy.deepcopy(champ)
    if kit:
        t[0]["skills"].append(sid)
    if ines:
        t[1]["skills"].append(sid)
    return t
V = {"base": team(), "Kitasan +A&S": team(kit=True), "Ines +A&S": team(ines=True), "both +A&S": team(True, True),
     "Kitasan +null": team(kit=True, sid=NULL), "Ines +null": team(ines=True, sid=NULL), "both +null": team(True, True, sid=NULL)}
MARKS = (1625, 1875)


def at_time(t, x, tt):
    return float(np.interp(tt, t, x))


def race(rep, req, var, seed):
    res = rep["results"]; gates = [h["gateIndex"] for h in req["horses"]]; g2i = {g: i for i, g in enumerate(gates)}
    fr = rep["frames"]; t = np.array([f["t"] for f in fr])
    P = np.array([[h["pos"] for h in f["horses"]] for f in fr]); S = np.array([[h["speed"] for h in f["horses"]] for f in fr])
    duels = {}
    for e in rep.get("duelLog", []):
        duels.setdefault(g2i[e["horseIndex"]], []).append(e)
    starts = {}
    for i, ds in duels.items():
        for e in ds:
            starts.setdefault(round(e["t0"], 4), []).append(i)
    pl = [res[i]["finishOrder"] + 1 for i in range(12)]
    row = {"variant": var, "seed": seed, **{f"p{i}": pl[i] for i in range(3)},
           "team_top3": 100 * sum(p <= 3 for p in pl[:3]) / 3, "points": sum(loh.points(p) for p in pl[:3]),
           **{f"hp{i}": bool(res[i].get("hpEmptyOnRace")) for i in range(3)},
           "gate_k": gates[0] + 1, "gate_i": gates[1] + 1}
    for i, nm in ((0, "k"), (1, "i")):
        ev = [e for e in rep.get("skillEvents", []) if e["horseIndex"] == i and str(e["skillId"]) in (AS, NULL)]
        ds = duels.get(i, [])
        partners = set()
        for e in ds:
            partners |= {j for j in starts.get(round(e["t0"], 4), []) if j != i}
        row.update({f"as_{nm}": bool(ev), f"as_{nm}_pos": at_time(t, P[:, i], ev[0]["t"]) if ev else None,
                    f"duel_{nm}": bool(ds), f"duels_{nm}": len(ds),
                    f"duel_{nm}_start": ds[0]["pos0"] if ds else None,
                    f"duel_{nm}_len": sum(((e["t1"] if e["t1"] >= 0 else res[i]["finishTimeRaw"]) - e["t0"]) for e in ds),
                    f"duel_{nm}_with_front": (1 - i) in partners,
                    f"duel_{nm}_with_opp": any(3 <= j < 6 for j in partners),
                    f"duel_{nm}_with_npc": any(j >= 6 for j in partners),
                    f"duel_{nm}_with_neo": 2 in partners})
    row["fronts_duel_each_other"] = row["duel_k_with_front"]
    for m in MARKS:
        lead = np.maximum(P[:, 0], P[:, 1]); k = int(np.searchsorted(lead, m)); k = min(max(k, 1), len(t) - 1)
        tt = float(np.interp(m, lead[k - 1:k + 1], t[k - 1:k + 1]))
        pk, pi = at_time(t, P[:, 0], tt), at_time(t, P[:, 1], tt)
        row[f"gap_{m}"] = abs(pk - pi); row[f"kit_ahead_{m}"] = pk > pi
        row[f"dspeed_{m}"] = abs(at_time(t, S[:, 0], tt) - at_time(t, S[:, 1], tt))
        allp = np.array([at_time(t, P[:, j], tt) for j in range(12)])
        row[f"front_leads_race_{m}"] = int(np.argmax(allp)) in (0, 1)
    row["finish_gap_s"] = abs(res[0]["finishTimeRaw"] - res[1]["finishTimeRaw"])
    row["fronts_1_2"] = sorted(pl[:2]) == [1, 2]
    return row


seeds = list(range(200_000_000, 200_000_000 + N))
csv = out / "races.csv.gz"
done = set(pd.read_csv(csv).variant.unique()) if csv.exists() else set()
t0 = time.time()
for var, tm in V.items():
    if var in done:
        continue
    mm = mock.MockMatchup(tm); rows = []
    for k in range(0, N, 200):
        part = seeds[k:k + 200]; reqs = []
        for s in part:
            q = mm.request(s); q["omitFrames"] = False; reqs.append(q)
        for s, q, rp in zip(part, reqs, engine.run_requests(reqs)):
            if "error" in rp:
                raise engine.EngineError(rp["error"])
            rows.append(race(rp, q, var, s))
    pd.DataFrame(rows).to_csv(csv, mode="a", header=not csv.exists(), index=False)
    log(f"{var}: {N} races {time.time() - t0:.0f}s")
log("done", out)
