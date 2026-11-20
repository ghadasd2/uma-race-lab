"""v4 step A5: stat exchange rates at the v4 base (each uma x each stat +-50 / +-100, others at base).
Reports pp team top-3 per 100 in-game cost points (cut vs add) and flags variants that break the HP-out floor.
Usage: loh_v4_a5_exchange.py N_SEEDS"""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import mock, opt

N = int(sys.argv[1])
out = opt.run_dir("v4-a5-exchange")
team = json.loads(Path("data/loh/my_team_v4_base.json").read_text())
STAT = ["spd", "sta", "pow", "guts", "wit"]
v, meta = {"base": team}, {}
for i, b in enumerate(team):
    for k in range(5):
        for d in (-100, -50, 50, 100):
            st = list(b["stats"]); st[k] += d
            t = copy.deepcopy(team); t[i]["stats"] = st
            name = f"{b['name']}: {STAT[k]}{d:+d}"
            v[name] = t
            meta[name] = {"uma": b["name"], "slot": i, "stat": STAT[k], "delta": d, "from": b["stats"][k], "to": st[k],
                          "cost_delta": mock.stat_cost(st) - mock.stat_cost(b["stats"])}
t0 = time.time()
df = mock.evaluate(v, list(range(103_000_000, 103_000_000 + N)))
df.to_csv(out / "races.csv.gz", index=False)
s = mock.summarize(df)
base_ind = {i: 100 * (df[df.variant == "base"][f"p{i}"] <= 3).mean() for i in range(3)}
rows = []
for _, r in s.iterrows():
    if r.variant == "base":
        continue
    m = meta[r.variant]; x = df[df.variant == r.variant]
    rows.append({**m, "d_team_top3": r.d_top3, "lo": r.d_top3_lo, "hi": r.d_top3_hi, "d_points": r.d_points,
                 "d_ind_top3": r[f"ind{m['slot']}"] - base_ind[m["slot"]],
                 "hp_own%": r[f"hp{m['slot']}%"], "hp_status": mock.hp_status(x),
                 "pp_per_100_cost": 100 * r.d_top3 / m["cost_delta"] if m["cost_delta"] else None})
ex = pd.DataFrame(rows).sort_values(["uma", "stat", "delta"])
ex.to_csv(out / "exchange_rates.csv", index=False)
b = s[s.variant == "base"].iloc[0]
pd.set_option("display.width", 250)
print(f"base: team top3 {b.top3:.2f}, HP-out % {b['hp0%']:.2f} {b['hp1%']:.2f} {b['hp2%']:.2f}")
print(ex.drop(columns=["slot"]).round(2).to_string())
print(f"{len(df)} races {time.time() - t0:.0f}s\ndone {out}")
