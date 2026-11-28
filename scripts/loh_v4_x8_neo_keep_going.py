"""v4 extra X8: stamina requirement for Keep Going! (gold Full Throttle, 202151: +0.45 m/s for 5.76 s and -2 % HP, random
point in the middle phase) on Neo's current build (X5 kit, 1450/1000/1250/1200/1200). Kitasan/Ines = v4 champion.
Stamina changes are cost-neutral (speed pays, 2 cost per speed point above 1200).
Variants: ref (X5 build, no Keep Going!); KG added on top (cap/ESP ignored) at stamina 1050..1200; KG swapped in for
Slick Surge + Tail Held High (23-skill cap, ESP 4580) at 1100..1150. 17,500 paired races each (seeds 201M).
Floor: Neo HP-out <= 3/175 (1.714 %); 'ok' also needs the Wilson 95 % upper bound under it.
Usage: loh_v4_x8_neo_keep_going.py N [RUN_DIR]"""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
from umasim import buildgen as G, mock, opt

N = int(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else opt.run_dir("v4-x8-neo-keep-going")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()
champ = json.loads(Path("data/loh/my_team_v4_champion.json").read_text())
champ[2] = json.loads(Path("data/loh/my_team_v4_neo_no_isw.json").read_text())[2]
neo = champ[2]; KG = "Keep Going!"


def neutral(stats, sta):
    s = list(stats); before = mock.stat_cost(s); s[1] = sta
    diff = mock.stat_cost(s) - before
    s[0] -= -(-diff // 2) if s[0] > 1200 else diff
    return s


def team(skills, sta):
    t = copy.deepcopy(champ); t[2]["skills"] = skills; t[2]["stats"] = neutral(neo["stats"], sta); return t
swap = [s for s in neo["skills"] if s not in ("Slick Surge", "Tail Held High")] + [KG]
V = {"base": copy.deepcopy(champ)}
for sta in (1050, 1075, 1100, 1125, 1150, 1200):
    V[f"on top @ {sta}"] = team(neo["skills"] + [KG], sta)
for sta in (1100, 1125, 1150):
    V[f"swap @ {sta}"] = team(swap, sta)
log("swap kit ESP", G.build_esp(swap), "skills", len(swap) + 1)
for k, t in V.items():
    log(f"{k}: Neo {t[2]['stats']} cost {mock.stat_cost(t[2]['stats'])}")
t0 = time.time()
df = mock.evaluate(V, list(range(201_000_000, 201_000_000 + N)))
df.to_csv(out / "races.csv.gz", index=False)
s = mock.summarize(df)
w = df.assign(neo=(df.p2 <= 3) * 100.0).pivot(index="seed", columns="variant", values="neo")
d = w.sub(w["base"], axis=0); se = d.std(ddof=1) / np.sqrt(len(d))
s["neo_top3"] = s.variant.map(w.mean()); s["d_neo"] = s.variant.map(d.mean())
s["d_neo_lo"] = s.variant.map(d.mean() - 1.96 * se); s["d_neo_hi"] = s.variant.map(d.mean() + 1.96 * se)
s["neo_hp_ub%"] = [100 * mock.wilson_ub(int(df[df.variant == v].hp2.sum()), int((df.variant == v).sum())) for v in s.variant]
fl = 100 * mock.HP_FLOOR
s["neo_floor"] = ["ok" if u <= fl else ("marginal" if h <= fl else "fail") for h, u in zip(s["hp2%"], s["neo_hp_ub%"])]
hb = df.sort_values("seed").assign(batch=lambda x: x.groupby("variant").cumcount() // 175)
s["neo_batches_gt3%"] = s.variant.map(hb.groupby(["variant", "batch"]).hp2.sum().gt(3).groupby("variant").mean() * 100)
s["neo_stats"] = s.variant.map(lambda v: V[v][2]["stats"])
s.to_csv(out / "summary.csv", index=False)
pd.set_option("display.width", 250)
log(s[["variant", "neo_stats", "top3", "d_top3", "d_top3_lo", "d_top3_hi", "points", "d_points", "neo_top3", "d_neo", "d_neo_lo",
       "d_neo_hi", "hp0%", "hp1%", "hp2%", "neo_hp_ub%", "neo_floor", "neo_batches_gt3%"]].round(2).to_string(index=False))
log(f"{len(df)} races {time.time() - t0:.0f}s\ndone {out}")
