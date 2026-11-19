"""LoH v3 study 1 (vs random mock teams).
 1. calibration: CN team and my team vs mocks, in 175-race batches
 2. Ines: pick the Nimble Navigator replacement (paired)
 3. stat exchange rates: each uma, each stat +-50 / +-100 around the target spread, value per in-game cost point
Usage: loh_v3_stats_study.py N_SEEDS"""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import buildgen as G, loh, mock, opt

N = int(sys.argv[1])
out = opt.run_dir("v3-stats-study")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()
TARGET = [1430, 1100, 1200, 1200, 1200]
STAT = ["spd", "sta", "pow", "guts", "wit"]

team = json.loads(Path("data/loh/my_team_v2_stats.json").read_text())
for b in team:
    b["stats"] = list(TARGET)
log("target cost", mock.stat_cost(TARGET), "budget", mock.COST_BUDGET)

# 1+2: calibration and the Nimble Navigator replacement
ines = team[1]; base_sk = [s for s in ines["skills"] if s != "Nimble Navigator"]
opts = ["Standard Distance ○", "Mad Dash", "Straightaway Adept", "Ramp Up", "Playtime's Over!"]
v = {"cn_team": loh.opponent_team("cn")}
for o in opts:
    t = copy.deepcopy(team); t[1]["skills"] = base_sk + [o]
    assert G.valid(t[1], t[1]["skills"])[0], o
    v[f"ines+{o}"] = t
v["base"] = v["ines+Standard Distance ○"]
t0 = time.time()
df = mock.evaluate(v, list(range(50_000_000, 50_000_000 + N)))
s = mock.summarize(df); s.to_csv(out / "calib_ines.csv", index=False)
log(s.round(2).to_string()); log(f"{len(df)} races {time.time() - t0:.0f}s")
for name in ("cn_team", "base"):
    bt = mock.batches(df[df.variant == name])
    log(f"{name}: 175-race batches team top3 mean {bt.team_top3.mean():.1f} p10 {bt.team_top3.quantile(.1):.1f} "
        f"p90 {bt.team_top3.quantile(.9):.1f}; points/batch mean {bt.points.mean():.0f}")
mine = s[s.variant.str.startswith("ines+")].sort_values("ind1", ascending=False)
best_opt = mine.iloc[0].variant
team = v[best_opt]
log("Ines replacement chosen (individual top3):", best_opt)
opt.save_team(out / "base_team.json", team)

# 3: exchange rates
v = {"base": team}
meta = {}
for i, b in enumerate(team):
    for k in range(5):
        for d in (-100, -50, 50, 100):
            st = list(TARGET); st[k] += d
            t = copy.deepcopy(team); t[i]["stats"] = st
            name = f"{b['name']}: {STAT[k]}{d:+d}"
            v[name] = t
            meta[name] = {"uma": b["name"], "slot": i, "stat": STAT[k], "delta": d, "stats": st,
                          "cost_delta": mock.stat_cost(st) - mock.stat_cost(TARGET)}
t0 = time.time()
df = mock.evaluate(v, list(range(51_000_000, 51_000_000 + N)))
df.to_csv(out / "exchange_races.csv.gz", index=False)
s = mock.summarize(df)
rows = []
base_ind = {i: 100 * (df[df.variant == "base"][f"p{i}"] <= 3).mean() for i in range(3)}
for _, r in s.iterrows():
    if r.variant == "base":
        continue
    m = meta[r.variant]
    rows.append({**m, "d_team_top3": r.d_top3, "lo": r.d_top3_lo, "hi": r.d_top3_hi, "d_points": r.d_points,
                 "d_ind_top3": r[f"ind{m['slot']}"] - base_ind[m["slot"]], "hp_empty_per_race": r.hp_empty_per_race,
                 "pp_per_100_cost": 100 * r.d_top3 / m["cost_delta"] if m["cost_delta"] else None})
ex = pd.DataFrame(rows).sort_values(["uma", "stat", "delta"])
ex.to_csv(out / "exchange_rates.csv", index=False)
log(ex.drop(columns=["stats", "slot"]).round(2).to_string())
log(f"{len(df)} races {time.time() - t0:.0f}s"); log("done", out)
