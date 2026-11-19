"""LoH v3 study 3: stamina x stamina-draining skills, and guts, with full telemetry (HP, full spurt, duels).
Stat changes are cost-neutral: the in-game cost difference is paid by / refunded to speed (2 cost per speed pt > 1200).
Per uma (others at base):
  stamina 950..1250 x skill sets {none, Racing Spirit: Stamina, Mad Dash, both}  (skills added/removed on top of base)
  guts 1000/1100/1200/1250 (base skills)
Usage: loh_v3_stamina_duel.py N_SEEDS"""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import mock, opt

N = int(sys.argv[1])
team = json.loads(Path("data/loh/my_team_v3_base.json").read_text())
out = opt.run_dir("v3-stamina-duel")
seeds = list(range(53_000_000, 53_000_000 + N))
RS, MD = "Racing Spirit: Stamina", "Mad Dash"


def neutral(stats, k, val):
    """Set stat k to val and move speed so the in-game cost is unchanged."""
    s = list(stats); before = mock.stat_cost(s); s[k] = val
    diff = mock.stat_cost(s) - before
    s[0] -= diff // 2 if s[0] > 1200 else diff
    return s


variants = []
for i, b in enumerate(team):
    core = [x for x in b["skills"] if x not in (RS, MD)]
    for sta in (950, 1000, 1050, 1100, 1150, 1200, 1250):
        for tag, add in (("none", []), ("RS", [RS]), ("MD", [MD]), ("RS+MD", [RS, MD])):
            variants.append((b["name"], i, "stamina", sta, tag, neutral(b["stats"], 1, sta), core + add))
    for g in (1000, 1100, 1250):
        variants.append((b["name"], i, "guts", g, "base", neutral(b["stats"], 3, g), list(b["skills"])))
    variants.append((b["name"], i, "guts", 1200, "base", list(b["stats"]), list(b["skills"])))

rows = []
t0 = time.time()
for k, (uma, i, study, level, tag, stats, skills) in enumerate(variants):
    t = copy.deepcopy(team); t[i]["stats"] = stats; t[i]["skills"] = skills
    df, _ = mock.MockMatchup(t).simulate(seeds)
    me = df[df.side == "mine"]
    x = me[me.idx == i]
    per_race = me.groupby("seed").top3.mean()
    d = x[x.dueled]
    rows.append({"uma": uma, "study": study, "level": level, "skills": tag, "spd": stats[0], "sta": stats[1], "guts": stats[3],
                 "team_top3": 100 * per_race.mean(), "team_pts": me.groupby("seed").points.sum().mean(),
                 "ind_top3": 100 * x.top3.mean(), "ind_1st": 100 * x.p1.mean(), "hp_empty%": 100 * x.hp_empty.mean(),
                 "full_spurt%": 100 * x.full_spurt.mean(), "duel%": 100 * x.dueled.mean(),
                 "duel_len_s": d.duel_time.mean(), "duel_start_m": d.duel_start_pos.median(),
                 "duel_to_finish%": 100 * d.duel_to_finish.mean() if len(d) else None,
                 "top3_if_duel": 100 * d.top3.mean() if len(d) else None, "spot%": 100 * x.spot.mean(),
                 "spot_len_s": x[x.spot].spot_time.mean()})
    print(f"[{k + 1}/{len(variants)} {time.time() - t0:.0f}s] " + json.dumps({kk: (round(vv, 2) if isinstance(vv, float) else vv) for kk, vv in rows[-1].items()}), flush=True)
    df[df.side == "mine"].to_csv(out / f"races_{k:03d}.csv.gz", index=False)
res = pd.DataFrame(rows)
res.to_csv(out / "stamina_duel.csv", index=False)
pd.set_option("display.width", 250)
print(res.round(2).to_string()); print("done", out)
