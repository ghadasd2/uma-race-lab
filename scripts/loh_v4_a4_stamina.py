"""v4 step A4: stamina requirement study under the HP-out floor (each uma <= 3/175 races out of HP).
Per uma, others at the v4 base; stamina changes are cost-neutral (speed pays / refunds, 2 per speed point > 1200):
  fronts : stamina 950..1350 x {none, RS:Stamina, Mad Dash, RS:Stamina + Mad Dash}
  Neo    : stamina 950..1350 x {none, RS:Stamina, Full Throttle, Keep Going!, RS + Full Throttle, RS + Keep Going!}
  all    : guts 1000 / 1100 / 1200 / 1250 at base skills
Drain skills are added on top of the base kit (the skill cap / ESP are ignored, as in v3, to measure raw value).
Full telemetry per variant; resumable (rows appended to stamina.csv; finished variants are skipped).
Usage: loh_v4_a4_stamina.py N_SEEDS [RUN_DIR_TO_RESUME]"""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import mock, opt

N = int(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else opt.run_dir("v4-a4-stamina")
team = json.loads(Path("data/loh/my_team_v4_base.json").read_text())
seeds = list(range(102_000_000, 102_000_000 + N))
RS, MD, FT, KG = "Racing Spirit: Stamina", "Mad Dash", "Full Throttle", "Keep Going!"
DRAIN = {RS, MD, FT, KG}
SETS = {"Front Runner": [("none", []), ("RS", [RS]), ("MD", [MD]), ("RS+MD", [RS, MD])],
        "Late Surger": [("none", []), ("RS", [RS]), ("FT", [FT]), ("KG", [KG]), ("RS+FT", [RS, FT]), ("RS+KG", [RS, KG])]}
STAMINA = list(range(950, 1351, 50))


def neutral(stats, k, val):
    s = list(stats); before = mock.stat_cost(s); s[k] = val
    diff = mock.stat_cost(s) - before
    s[0] -= -(-diff // 2) if s[0] > 1200 else diff
    return s


variants = []
for i, b in enumerate(team):
    core = [x for x in b["skills"] if x not in DRAIN]
    for sta in STAMINA:
        for tag, add in SETS[b["strategy"]]:
            variants.append((b["name"], i, "stamina", sta, tag, neutral(b["stats"], 1, sta), core + add))
    for g in (1000, 1100, 1200, 1250):
        variants.append((b["name"], i, "guts", g, "base", neutral(b["stats"], 3, g), list(b["skills"])))

csv = out / "stamina.csv"
done = set()
if csv.exists():
    prev = pd.read_csv(csv)
    done = set(zip(prev.uma, prev.study, prev.level, prev.skills))
print(f"{len(variants)} variants, {len(done)} already done -> {out}", flush=True)
t0 = time.time()
for k, (uma, i, study, level, tag, stats, skills) in enumerate(variants):
    if (uma, study, level, tag) in done:
        continue
    t = copy.deepcopy(team); t[i]["stats"] = stats; t[i]["skills"] = skills
    df, _ = mock.MockMatchup(t).simulate(seeds)
    me = df[df.side == "mine"]
    x = me[me.idx == i]
    d = x[x.dueled]
    n_hp = int(x.hp_empty.sum())
    row = {"uma": uma, "study": study, "level": level, "skills": tag, "spd": stats[0], "sta": stats[1], "guts": stats[3],
           "cost": mock.stat_cost(stats), "n": len(x),
           "team_top3": 100 * me.groupby("seed").top3.mean().mean(), "team_pts": me.groupby("seed").points.sum().mean(),
           "ind_top3": 100 * x.top3.mean(), "ind_1st": 100 * x.p1.mean(),
           "hp_empty%": 100 * n_hp / len(x), "hp_empty_ub%": 100 * mock.wilson_ub(n_hp, len(x)),
           "hp_ok": n_hp / len(x) <= mock.HP_FLOOR,
           "team_hp_max%": 100 * me.groupby("idx").hp_empty.mean().max(),
           "full_spurt%": 100 * x.full_spurt.mean(), "duel%": 100 * x.dueled.mean(),
           "duel_len_s": d.duel_time.mean(), "duel_start_m": d.duel_start_pos.median(),
           "top3_if_duel": 100 * d.top3.mean() if len(d) else None, "top3_if_no_duel": 100 * x[~x.dueled].top3.mean(),
           "spot%": 100 * x.spot.mean(), "spot_len_s": x[x.spot].spot_time.mean(),
           "late_start%": 100 * x.late_start.mean()}
    pd.DataFrame([row]).to_csv(csv, mode="a", header=not csv.exists(), index=False)
    print(f"[{k + 1}/{len(variants)} {time.time() - t0:.0f}s] " +
          json.dumps({kk: (round(vv, 2) if isinstance(vv, float) else vv) for kk, vv in row.items()}), flush=True)

# requirement table: lowest stamina meeting the floor per skill set, and the best feasible stamina
res = pd.read_csv(csv)
st = res[res.study == "stamina"]
req = []
for (uma, tag), x in st.groupby(["uma", "skills"]):
    x = x.sort_values("level")
    feas = x[x.hp_ok]
    none = st[(st.uma == uma) & (st.skills == "none") & st.hp_ok]
    none_best = none.loc[none.team_top3.idxmax()] if len(none) else None
    r = {"uma": uma, "skills": tag, "min_stamina_floor": feas.level.min() if len(feas) else None}
    if len(feas):
        m = feas.iloc[0]
        b = feas.loc[feas.team_top3.idxmax()]
        same = none[none.level == m.level]
        r.update({"team_top3_at_min": m.team_top3, "ind_top3_at_min": m.ind_top3, "hp%_at_min": m["hp_empty%"],
                  "vs_none_same_stamina_pp": m.team_top3 - same.team_top3.iloc[0] if len(same) else None,
                  "best_feasible_stamina": b.level, "best_team_top3": b.team_top3, "best_ind_top3": b.ind_top3,
                  "best_spd": b.spd, "vs_best_none_pp": b.team_top3 - none_best.team_top3 if none_best is not None else None,
                  "best_none_stamina": none_best.level if none_best is not None else None})
    req.append(r)
pd.DataFrame(req).to_csv(out / "requirements.csv", index=False)
pd.set_option("display.width", 250)
print(pd.DataFrame(req).round(2).to_string())
print("done", out)
