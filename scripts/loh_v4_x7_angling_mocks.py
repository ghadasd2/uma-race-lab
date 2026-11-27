"""v4 extra X7: Angling and Scheming (inherited, 900201) on the MOCK opponents instead of my fronts.
Team = v4 champion fronts + Neo X5 build (as X6). The skill (or its no-effect clone, same lottery/condition) is
appended to every mock's kit; it only fires for a runner that is 1st on a corner in the final leg.
Variants: base; mocks +A&S / mocks +null; all +A&S / all +null (my two fronts hold it too). Real vs null twins give
the clean causal effect (identical races until the skill fires). Paired seeds 200M (base = X6 base).
Per race (downsampled frames): my placings/points/HP, mock placings, who fired it and where, my fronts' duels and
partners (Kitasan-Ines / mock / NPC), Kitasan-Ines gap at 1875 m, race leader at 1600 / 1875 m (mine / mock / NPC)
and the gap from the leader to my nearest front at 1875 m.
Usage: loh_v4_x7_angling_mocks.py N [RUN_DIR]"""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
from umasim import catalog as C, engine, loh, mock, opt

N = int(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else opt.run_dir("v4-x7-angling-mocks")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()
AS, NULL = "900201", "299101"
T = C.skill_table(); T[NULL] = copy.deepcopy(T[AS])
for a in T[NULL]["alternatives"]:
    for f in a["effects"]:
        f["modifier"] = 0
champ = json.loads(Path("data/loh/my_team_v4_champion.json").read_text())
champ[2] = json.loads(Path("data/loh/my_team_v4_neo_no_isw.json").read_text())[2]


class Matchup(mock.MockMatchup):
    def __init__(self, mine, opp_sid=None):
        super().__init__(mine); self.opp_sid = opp_sid

    def request(self, seed, d=None):
        d = copy.deepcopy(d or mock.draw(seed))
        if self.opp_sid:
            for o in d["opp"]:
                o["skills"] = list(o["skills"]) + [self.opp_sid]
        return super().request(seed, d)


def mine(sid=None):
    t = copy.deepcopy(champ)
    if sid:
        t[0]["skills"].append(sid); t[1]["skills"].append(sid)
    return t
V = {"base": (mine(), None), "mocks +A&S": (mine(), AS), "mocks +null": (mine(), NULL),
     "all +A&S": (mine(AS), AS), "all +null": (mine(NULL), NULL)}


def race(rep, req, var, seed, opp):
    res = rep["results"]; gates = [h["gateIndex"] for h in req["horses"]]; g2i = {g: i for i, g in enumerate(gates)}
    fr = rep["frames"]; t = np.array([f["t"] for f in fr]); P = np.array([[h["pos"] for h in f["horses"]] for f in fr])
    duels, starts = {}, {}
    for e in rep.get("duelLog", []):
        i = g2i[e["horseIndex"]]; duels.setdefault(i, []).append(e); starts.setdefault(round(e["t0"], 4), []).append(i)
    pl = [res[i]["finishOrder"] + 1 for i in range(12)]
    row = {"variant": var, "seed": seed, **{f"p{i}": pl[i] for i in range(6)},
           "team_top3": 100 * sum(p <= 3 for p in pl[:3]) / 3, "points": sum(loh.points(p) for p in pl[:3]),
           "opp_top3": 100 * sum(p <= 3 for p in pl[3:6]) / 3, "winner": "mine" if 1 in pl[:3] else ("mock" if 1 in pl[3:6] else "npc"),
           **{f"hp{i}": bool(res[i].get("hpEmptyOnRace")) for i in range(3)},
           "mock_fronts": sum(o["strategy"] == "Front Runner" for o in opp)}
    fired = {}
    for e in rep.get("skillEvents", []):
        if str(e["skillId"]) in (AS, NULL):
            fired.setdefault(e["horseIndex"], at(t, P[:, e["horseIndex"]], e["t"]))
    row["as_mine"] = any(i in fired for i in (0, 1)); row["as_mock"] = any(3 <= i < 6 for i in fired)
    row["as_mock_pos"] = min((p for i, p in fired.items() if 3 <= i < 6), default=None)
    row["as_mock_strategy"] = next((opp[i - 3]["strategy"] for i in fired if 3 <= i < 6), None)
    for i, nm in ((0, "k"), (1, "i")):
        ds = duels.get(i, []); partners = set()
        for e in ds:
            partners |= {j for j in starts.get(round(e["t0"], 4), []) if j != i}
        row.update({f"duel_{nm}": bool(ds), f"duel_{nm}_len": sum(((e["t1"] if e["t1"] >= 0 else res[i]["finishTimeRaw"]) - e["t0"]) for e in ds),
                    f"duel_{nm}_with_front": (1 - i) in partners, f"duel_{nm}_with_mock": any(3 <= j < 6 for j in partners),
                    f"duel_{nm}_with_npc": any(j >= 6 for j in partners)})
    for m in (1600, 1875):
        lead = P.max(axis=1); k = min(max(int(np.searchsorted(lead, m)), 1), len(t) - 1)
        tt = float(np.interp(m, lead[k - 1:k + 1], t[k - 1:k + 1]))
        allp = np.array([at(t, P[:, j], tt) for j in range(12)]); ld = int(np.argmax(allp))
        row[f"leader_{m}"] = "mine" if ld < 3 else ("mock" if ld < 6 else "npc")
        if m == 1875:
            row["gap_k_i_1875"] = abs(allp[0] - allp[1])
            row["leader_to_my_front_1875"] = allp[ld] - max(allp[0], allp[1])
    return row


def at(t, x, tt):
    return float(np.interp(tt, t, x))


seeds = list(range(200_000_000, 200_000_000 + N))
csv = out / "races.csv.gz"
done = set(pd.read_csv(csv).variant.unique()) if csv.exists() else set()
t0 = time.time()
for var, (tm, sid) in V.items():
    if var in done:
        continue
    mm = Matchup(tm, sid); rows = []
    for k in range(0, N, 200):
        part = seeds[k:k + 200]; reqs, opps = [], []
        for s in part:
            q = mm.request(s); q["omitFrames"] = False; reqs.append(q); opps.append(list(mm.opp))
        for s, q, o, rp in zip(part, reqs, opps, engine.run_requests(reqs)):
            if "error" in rp:
                raise engine.EngineError(rp["error"])
            rows.append(race(rp, q, var, s, o))
    pd.DataFrame(rows).to_csv(csv, mode="a", header=not csv.exists(), index=False)
    log(f"{var}: {N} races {time.time() - t0:.0f}s")
log("done", out)
