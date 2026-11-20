"""LoH v4 step A8: v4 champion vs v4 base vs v3 champion vs CN team on unseen seeds (190M block), in 175-race batches,
with the HP-out floor checked per uma (overall rate, 95 % upper bound, and the share of 175-race batches in which an uma
ran out of HP more than 3 times), plus full telemetry for the champion.
Usage: loh_v4_a8_validate.py N_SEEDS [CHAMPION.json]"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import loh, mock, opt

N = int(sys.argv[1])
out = opt.run_dir("v4-a8-validate")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()
seeds = list(range(190_000_000, 190_000_000 + N))
champ = json.loads(Path(sys.argv[2] if len(sys.argv) > 2 else "data/loh/my_team_v4_champion.json").read_text())
v = {"base": json.loads(Path("data/loh/my_team_v4_base.json").read_text()), "champion": champ,
     "v3_champion": json.loads(Path("data/loh/my_team_v3_champion.json").read_text()),
     "cn_team": loh.opponent_team("cn")}
t0 = time.time()
df = mock.evaluate(v, seeds); df.to_csv(out / "races.csv.gz", index=False)
s = mock.summarize(df); s.to_csv(out / "summary.csv", index=False)
pd.set_option("display.width", 250)
log(s.round(2).to_string()); log(f"{len(df)} races {time.time() - t0:.0f}s")
rows = []
for name in v:
    bt = mock.batches(df[df.variant == name]); bt.to_csv(out / f"batches_{name}.csv", index=False)
    r = {"variant": name, "batches": len(bt), "mean": bt.team_top3.mean(), "p10": bt.team_top3.quantile(.1),
         "p50": bt.team_top3.median(), "p90": bt.team_top3.quantile(.9), "max": bt.team_top3.max(),
         "pts_mean": bt.points.mean(), "pts_p10": bt.points.quantile(.1), "pts_p90": bt.points.quantile(.9)}
    for x in (80, 85, 90, 95, 97.1):
        r[f"P>={x}"] = 100 * (bt.team_top3 >= x).mean()
    xv = df[df.variant == name].sort_values("seed").reset_index(drop=True)
    xv["batch"] = xv.index // 175
    hb = xv[xv.groupby("batch").seed.transform("size") == 175].groupby("batch")[["hp0", "hp1", "hp2"]].sum()
    for k in range(3):
        r[f"hp{k}%"] = 100 * xv[f"hp{k}"].mean()
        r[f"hp{k}_ub%"] = 100 * mock.wilson_ub(xv[f"hp{k}"].sum(), len(xv))
        r[f"batches_hp{k}>3%"] = 100 * (hb[f"hp{k}"] > 3).mean()
    r["hp_status"] = mock.hp_status(xv)
    rows.append(r)
log(pd.DataFrame(rows).round(2).to_string())
pd.DataFrame(rows).to_csv(out / "batch_dist.csv", index=False)

# champion telemetry
tel, _ = mock.MockMatchup(champ).simulate(seeds)
tel.to_csv(out / "champion_telemetry.csv.gz", index=False)
me = tel[tel.side == "mine"]
per = me.groupby("runner").agg(top3=("top3", "mean"), win=("p1", "mean"), second=("p2", "mean"), third=("p3", "mean"),
                               pts=("points", "mean"), late=("late_start", "mean"), hp_empty=("hp_empty", "mean"),
                               full_spurt=("full_spurt", "mean"), duel=("dueled", "mean"), spot=("spot", "mean"))
log((100 * per.drop(columns="pts")).round(1).assign(pts=per.pts.round(1)).to_string())
for col in ("mood", "ground", "weather", "late_start", "dueled"):
    t = me.groupby(["runner", col]).top3.mean().unstack() * 100
    log(f"\ntop3% by {col}\n" + t.round(1).to_string())
me = me.assign(gate_band=pd.cut(me.gate, [0, 3, 6, 9, 12], labels=["2-3", "4-6", "7-9", "10-12"]))
log("\ntop3% by gate\n" + (me.groupby(["runner", "gate_band"], observed=True).top3.mean().unstack() * 100).round(1).to_string())
log("done", out)
