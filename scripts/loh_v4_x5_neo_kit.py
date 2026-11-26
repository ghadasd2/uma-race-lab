"""v4 extra X5: best Neo kit and stats WITHOUT Ignited Spirit WIT (user rule: no skills that risk losing position).
Others stay at the v4 champion. Excluded for Neo: Ignited Spirit WIT and Prudent Positioning (same opening lane-move
mechanism), stamina-drain skills (Neo runs 1000 stamina), Pedal to the Metal (X3: worse than an empty slot).
Nimble Navigator (lane +0.005 in the last spurt) may be kept or dropped; the best kit without it is reported too.
Constraints: <= 23 skills incl. unique, <= 3 inherited, one skill per tier group, ESP 4500-4600, stat box/cost as A7,
HP floor (Neo and team <= 3/175) in the final rounds.
Candidate pool = Neo's skill pool + the skills the user had tested in X3/X4.
Stages (paired, fresh seeds per stage; reference 'base' = current v4 champion WITH Ignited Spirit WIT):
  1 kits: enumerate removals of low-value held skills x adds of valued candidates, rank by prior value (X3/X4 slot
    values, X4/A6 holding values, A6 add values), keep top K + references; halving 2,000 -> 6,000 -> 17,500 races
    (seeds 198.0M / 198.1M / 198.2M)
  2 stats: winning kit x cost-neutral stat moves, 9,000 races (seeds 198.4M); keep a move only if its CI lower bound > 0
  3 validation: 17,500 unseen races (seeds 199M): current champion, champion minus IS WIT (nothing added),
    final kit, best kit without Nimble Navigator
Resumable per stage (stage files in the run dir). Usage: loh_v4_x5_neo_kit.py [RUN_DIR] [K]"""
import copy, itertools, json, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
from umasim import buildgen as G, catalog as C, esp, mock, opt

out = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].isdigit() else opt.run_dir("v4-x5-neo-kit")
K = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 48
SCALE = float(os.environ.get("X5_SCALE", "1"))   # smoke tests only
sz = lambda n: max(50, int(n * SCALE))
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()
RES = Path("data/loh/results/v4")
NEO = 2
champ = json.loads(Path("data/loh/my_team_v4_champion.json").read_text())
neo0 = champ[NEO]
EVOLVED = set(G.EVOLVED["Neo Universe"])
EXCLUDE = {"Ignited Spirit WIT", "Prudent Positioning", "Keep Going!", "Full Throttle", "Racing Spirit: Stamina",
           "Pedal to the Metal", "Mad Dash"}
EXTRA = ["Condor's Fury", "Latch On", "Break the Mold", "Triumphant Pulse", "Barcarole of Blessings",
         "Racing Spirit: Power", "Straightaway Acceleration"]
LANE = {"Nimble Navigator"}
BOX = [(1350, 1500), (950, 1300), (1100, 1250), (1000, 1250), (1100, 1250)]
STAT = ["spd", "sta", "pow", "guts", "wit"]

# ------------------------------------------------------------------ priors (team pp)
sv = pd.read_csv(RES / "A6" / "skill_values.csv")
sv = sv[sv.uma == "Neo Universe"]
HOLD = {r.skill: -r.d_team_top3 for r in sv[sv.test == "drop"].itertuples()}
ADDV = {r.skill: r.d_team_top3 for r in sv[sv.test == "add"].itertuples()}
HOLD.update({"Slick Surge": 0.26, "Into High Gear!": 0.73})                       # X3 / X4, 17,500 races
ADDV.update({"Condor's Fury": 0.55, "Latch On": 0.43, "Break the Mold": 0.40, "Triumphant Pulse": 0.36,
             "Barcarole of Blessings": 0.30, "Racing Spirit: Power": 0.25, "Straightaway Acceleration": 0.16})
pool = sorted({p["skill"] for p in G.candidates(neo0)} | set(EXTRA))
cand_add = [s for s in pool if s not in neo0["skills"] and s not in EXCLUDE and ADDV.get(s, 0) > 0.2]
held = [s for s in neo0["skills"] if s != "Ignited Spirit WIT"]
removable = [s for s in held if s not in EVOLVED and HOLD.get(s, 0) <= 0.3]
kind = lambda s: esp.kind(C.resolve_skill(s))
log("candidate adds (prior):", {s: round(ADDV[s], 2) for s in sorted(cand_add, key=lambda s: -ADDV[s])})
log("removable held (hold value):", {s: round(HOLD.get(s, 0), 2) for s in sorted(removable, key=lambda s: HOLD.get(s, 0))})


COST = {s: G.build_esp([s]) for s in set(pool) | set(neo0["skills"])}
GRP = {s: G._group(s) for s in COST}
INH = {s: kind(s) == "inherited" for s in COST}


FAMILY = {"Medium Straightaways ◎": "straight", "Medium Straightaways ○": "straight", "Late Surger Straightaways ○": "straight",
          "Straightaway Adept": "straight", "Straightaway Acceleration": "straight", "Professor of Curvature": "corner",
          "Corner Adept ○": "corner", "Late Surger Corners ◎": "corner"}
DISCOUNT = [1.0, 0.6, 0.4, 0.3]


def add_prior(A):
    """Sum of add values with diminishing returns inside a family (overlapping straight / corner skills)."""
    tot, seen = 0.0, {}
    for s in sorted(A, key=lambda x: -ADDV[x]):
        f = FAMILY.get(s)
        k = seen.get(f, 0) if f else 0
        tot += ADDV[s] * DISCOUNT[min(k, 3)]
        if f:
            seen[f] = k + 1
    return tot


def legal(sk):
    if len(sk) + 1 > G.MAX_SKILLS or any(s in EXCLUDE for s in sk):
        return False
    gr = [GRP[s] for s in sk]
    if len(gr) != len(set(gr)) or sum(INH[s] for s in sk) > G.MAX_INHERITED:
        return False
    return 4500 <= sum(COST[s] for s in sk) <= 4600


def team_with(skills, stats=None):
    t = copy.deepcopy(champ); t[NEO]["skills"] = list(skills)
    if stats:
        t[NEO]["stats"] = list(stats)
    return t


def name_of(sk):
    rem = [s for s in neo0["skills"] if s not in sk]; add = [s for s in sk if s not in neo0["skills"]]
    return "-" + "/".join(rem) + (" +" + "/".join(add) if add else "")


def evaluate(teams, seeds):
    df = mock.evaluate(teams, seeds)
    s = mock.summarize(df)
    w = df.assign(neo=(df.p2 <= 3) * 100.0).pivot(index="seed", columns="variant", values="neo")
    s["neo_top3"] = s.variant.map(w.mean())
    d = w.sub(w["base"], axis=0); se = d.std(ddof=1) / np.sqrt(len(d))
    s["d_neo"] = s.variant.map(d.mean()); s["d_neo_lo"] = s.variant.map(d.mean() - 1.96 * se)
    s["neo_hp_ub%"] = [100 * mock.wilson_ub(int(df[df.variant == v].hp2.sum()), int((df.variant == v).sum())) for v in s.variant]
    return df, s


# ------------------------------------------------------------------ stage 1: kits
f1 = out / "stage1_final.csv"
if not f1.exists():
    kits = {}
    e0 = sum(COST[s] for s in held)
    adds_by_n = {a: [(A, sum(COST[x] for x in A)) for A in itertools.combinations(cand_add, a)
                     if len({GRP[x] for x in A}) == a] for a in range(1, 5)}
    for r in range(0, 4):
        for R in itertools.combinations(removable, r):
            base = [s for s in held if s not in R]; eb = e0 - sum(COST[x] for x in R)
            for a in range(1, r + 2):
                for A, ca in adds_by_n[a]:
                    if not 4500 <= eb + ca <= 4600:
                        continue
                    sk = base + list(A)
                    if legal(sk):
                        prior = add_prior(A) - sum(HOLD.get(s, 0) for s in R)
                        if prior > kits.get(frozenset(A), (None, -9))[1]:      # best removal set per add set
                            kits[frozenset(A)] = (tuple(sk), prior)
    kits = dict(kits.values())
    log(f"{len(kits)} legal kits (best removal set per add set)")
    ranked = sorted(kits.items(), key=lambda kv: -kv[1])
    chosen, uses = [], {}
    for k, _ in ranked:                                   # diversity: no added skill in more than half the kits
        A = [s for s in k if s not in held]
        if any(uses.get(a, 0) >= K // 2 for a in A):
            continue
        chosen.append(k)
        for a in A:
            uses[a] = uses.get(a, 0) + 1
        if len(chosen) == K:
            break
    no_nn = [k for k, _ in ranked if "Nimble Navigator" not in k and k not in chosen][:6]
    refs = [tuple(held + ["Latch On"]), tuple(held + ["Break the Mold"])]
    for k in no_nn + refs:
        if k not in chosen and k in kits:
            chosen.append(k)
    teams = {"base": champ}
    meta = {}
    for k in chosen:
        nm = name_of(k); teams[nm] = team_with(k); meta[nm] = {"skills": list(k), "prior": kits[k], "esp": G.build_esp(list(k)),
                                                                 "no_nn": "Nimble Navigator" not in k}
    json.dump(meta, open(out / "stage1_kits.json", "w"), ensure_ascii=False, indent=1)
    keep = list(teams)
    for rnd, (n, top, seed0) in enumerate(((2000, 12, 198_000_000), (6000, 5, 198_100_000), (17500, None, 198_200_000))):
        t0 = time.time()
        df, s = evaluate({k: teams[k] for k in keep}, list(range(seed0, seed0 + sz(n))))
        s["prior"] = s.variant.map(lambda v: meta.get(v, {}).get("prior")); s["no_nn"] = s.variant.map(lambda v: meta.get(v, {}).get("no_nn"))
        s = s.sort_values("top3", ascending=False); s.to_csv(out / f"stage1_round{rnd}.csv", index=False)
        log(f"stage 1 round {rnd}: {len(keep)} x {n} races {time.time() - t0:.0f}s")
        log(s[["variant", "top3", "d_top3", "d_top3_lo", "d_top3_hi", "neo_top3", "d_neo", "hp2%", "neo_hp_ub%", "prior"]].head(15).round(2).to_string(index=False))
        if top is None:
            break
        lenient = s[(s["hp2%"] <= 2.5) & (s.variant != "base")]
        nxt = list(lenient.variant[:top])
        best_nn = lenient[lenient.no_nn == True].variant[:2].tolist()
        keep = ["base"] + nxt + [v for v in best_nn if v not in nxt]
    s.to_csv(f1, index=False)
s1 = pd.read_csv(f1)
meta = json.load(open(out / "stage1_kits.json"))
ok = s1[(s1.variant != "base") & (s1["hp2%"] <= 100 * mock.HP_FLOOR)]
win = ok.iloc[0].variant
win_nn = ok[ok.no_nn == True].iloc[0].variant if (ok.no_nn == True).any() else None
log("stage 1 winner:", win, "| best without Nimble Navigator:", win_nn)

# ------------------------------------------------------------------ stage 2: stats for the winning kit
f2 = out / "stage2.csv"
if not f2.exists():
    sk = meta[win]["skills"]; st0 = list(neo0["stats"])
    def move(frm, to, step):
        st = list(st0); before = mock.stat_cost(st); st[frm] -= step
        freed = before - mock.stat_cost(st)
        while True:
            t = list(st); t[to] += 5
            if mock.stat_cost(t) - mock.stat_cost(st) > freed or t[to] > BOX[to][1]:
                break
            freed -= mock.stat_cost(t) - mock.stat_cost(st); st = t
        return st
    variants = {"kit, base stats": team_with(sk, st0)}
    for frm, to, step in ((3, 4, 50), (3, 4, 100), (3, 0, 50), (3, 0, 100), (0, 1, 50), (0, 4, 50), (3, 1, 50), (0, 3, 50)):
        st = move(frm, to, step)
        ok_box = all(lo <= v <= hi for v, (lo, hi) in zip(st, BOX)) and mock.stat_cost(st) <= mock.COST_BUDGET
        if ok_box and st != st0:
            variants[f"kit, {STAT[frm]}-{step}->{STAT[to]} {st}"] = team_with(sk, st)
    teams = {"base": variants.pop("kit, base stats")}
    teams.update(variants)
    t0 = time.time()
    df, s = evaluate(teams, list(range(198_400_000, 198_400_000 + sz(9000))))
    s = s.sort_values("top3", ascending=False); s.to_csv(f2, index=False)
    log(f"stage 2 (stats, reference = winning kit with base stats): {len(teams)} x 9000 races {time.time() - t0:.0f}s")
    log(s[["variant", "top3", "d_top3", "d_top3_lo", "d_top3_hi", "neo_top3", "d_neo", "hp2%", "neo_hp_ub%"]].round(2).to_string(index=False))
s2 = pd.read_csv(f2)
cand = s2[(s2.variant != "base") & (s2.d_top3_lo > 0) & (s2["neo_hp_ub%"] <= 100 * mock.HP_FLOOR + 0.3) & (s2["hp2%"] <= 100 * mock.HP_FLOOR)]
final_stats = list(neo0["stats"])
if len(cand):
    final_stats = json.loads(cand.iloc[0].variant.split(" ", 2)[2])
log("final stats:", final_stats)

# ------------------------------------------------------------------ stage 3: validation
f3 = out / "stage3.csv"
if not f3.exists():
    teams = {"base": champ, "minus IS WIT, nothing added": team_with(held),
             "final": team_with(meta[win]["skills"], final_stats)}
    if win_nn and win_nn != win:
        teams["best without Nimble Navigator"] = team_with(meta[win_nn]["skills"], final_stats)
    t0 = time.time()
    df, s = evaluate(teams, list(range(199_000_000, 199_000_000 + sz(17500))))
    df.to_csv(out / "stage3_races.csv.gz", index=False); s.to_csv(f3, index=False)
    rows = []
    for v in teams:
        bt = mock.batches(df[df.variant == v])
        rows.append({"variant": v, "P>=95": 100 * (bt.team_top3 >= 95).mean(), "P>=97.1": 100 * (bt.team_top3 >= 97.1).mean()})
    pd.DataFrame(rows).to_csv(out / "stage3_batches.csv", index=False)
    log(f"stage 3 validation: {len(teams)} x 17500 races {time.time() - t0:.0f}s")
    log(s[["variant", "top3", "d_top3", "d_top3_lo", "d_top3_hi", "points", "neo_top3", "d_neo", "hp0%", "hp1%", "hp2%", "neo_hp_ub%"]].round(2).to_string(index=False))
    log(pd.DataFrame(rows).to_string(index=False))
final = team_with(meta[win]["skills"], final_stats)
opt.save_team(out / "neo_final_team.json", final)
if win_nn:
    opt.save_team(out / "neo_no_nn_team.json", team_with(meta[win_nn]["skills"], final_stats))
log("FINAL Neo:", final_stats, "ESP", G.build_esp(meta[win]["skills"]), meta[win]["skills"])
log("done", out)
