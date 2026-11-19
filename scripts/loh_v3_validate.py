"""LoH v3 final check: champion vs start team vs CN team on unseen seeds, in 175-race LoH batches,
plus full telemetry for the champion (placements, mood/gate/ground breakdowns, duels, late starts).
Usage: loh_v3_validate.py N_SEEDS"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import loh, mock, opt

N = int(sys.argv[1])
out = opt.run_dir("v3-validate")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()
seeds = list(range(90_000_000, 90_000_000 + N))
champ = json.loads(Path("data/loh/my_team_v3_champion.json").read_text())
v = {"base": json.loads(Path("data/loh/my_team_v3_base.json").read_text()), "champion": champ,
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
    for x in (80, 85, 90, 97.1):
        r[f"P>={x}"] = 100 * (bt.team_top3 >= x).mean()
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
