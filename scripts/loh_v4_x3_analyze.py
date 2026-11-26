"""Analyse a loh_v4_x3_neo_skills.py run: paired value of each skill on Neo (added on top / swapped for Slick Surge),
Neo's own top-3, points, HP-out vs the floor, and where / how often each skill fired.
Usage: loh_v4_x3_analyze.py RUN_DIR"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
from umasim import catalog as C, esp, mock

run = Path(sys.argv[1])
X = pd.read_csv(run / "races.csv.gz")
X["neo_top3"] = (X.p2 <= 3) * 100.0
W = {c: X.pivot(index="seed", columns="variant", values=c) for c in ("team_top3", "neo_top3", "points")}
SID = {"Condor's Fury (inherited)": "910141", "Break the Mold": "202522", "Racing Spirit: Power": "210111",
       "Latch On": "202472", "Pedal to the Metal": "202452"}
SLICK = esp.esp(C.resolve_skill("Slick Surge"), True)

def ci(d):
    se = d.std(ddof=1) / np.sqrt(len(d)); return d.mean(), d.mean() - 1.96 * se, d.mean() + 1.96 * se
def fmt(t):
    return f"{t[0]:+.2f} [{t[1]:+.2f}, {t[2]:+.2f}]"

rows = []
for v in X.variant.unique():
    x = X[X.variant == v]
    r = {"variant": v, "races": len(x), "team_top3": x.team_top3.mean(), "neo_top3": x.neo_top3.mean(), "points": x.points.mean()}
    if v != "base":
        for c, nm in (("team_top3", "d_team"), ("neo_top3", "d_neo"), ("points", "d_points")):
            r[nm] = fmt(ci(W[c][v] - W[c]["base"]))
        r["_d_team"] = (W["team_top3"][v] - W["team_top3"]["base"]).mean()
    n = len(x); k = int(x.hp2.sum())
    r["neo_hp_out%"] = 100 * k / n; r["neo_hp_ub%"] = 100 * mock.wilson_ub(k, n)
    r["neo_floor"] = "ok" if r["neo_hp_ub%"] <= 100 * mock.HP_FLOOR else ("marginal" if r["neo_hp_out%"] <= 100 * mock.HP_FLOOR else "fail")
    r["team_hp_max%"] = 100 * max(x.hp0.mean(), x.hp1.mean(), x.hp2.mean())
    name = v.split(" ", 1)[1] if v.split(" ", 1)[0] in ("add", "swap") else None
    if name in SID:
        sp = esp.esp(SID[name], True)
        r["sp"] = sp if v.startswith("add") else sp - SLICK
        r["neo_esp"] = 4600 + r["sp"]
        r["pp_per_100sp"] = 100 * r["_d_team"] / r["sp"] if r["sp"] else None
        r["fired%"] = 100 * x.fired.mean()
        r["fire_m_median"] = x.fire_pos.median(); r["fire_m_p10"] = x.fire_pos.quantile(.1); r["fire_m_p90"] = x.fire_pos.quantile(.9)
        r["neo_top3_if_fired"] = x[x.fired].neo_top3.mean(); r["neo_top3_if_not"] = x[~x.fired].neo_top3.mean()
    rows.append(r)
R = pd.DataFrame(rows)
pd.set_option("display.width", 300); pd.set_option("display.max_columns", 40)
out = [f"{len(W['team_top3'])} paired races per variant (seeds 197M); v4 champion, only Neo's kit changes; "
       f"Slick Surge = {SLICK} SP; Neo ESP 4600 before changes", ""]
cols = ["variant", "team_top3", "d_team", "neo_top3", "d_neo", "d_points", "sp", "neo_esp", "pp_per_100sp",
        "neo_hp_out%", "neo_hp_ub%", "neo_floor", "team_hp_max%"]
out.append(R[[c for c in cols if c in R]].round(2).to_string(index=False))
out += ["", "activation (Neo):"]
out.append(R[R["fired%"].notna()][["variant", "fired%", "fire_m_p10", "fire_m_median", "fire_m_p90", "neo_top3_if_fired",
                                   "neo_top3_if_not"]].round(1).to_string(index=False))
# value of each skill in the Slick Surge slot = swap - drop
out += ["", "value in Neo's Slick Surge slot (swap vs drop Slick Surge, paired):"]
for name in SID:
    out.append(f"  {name}: team {fmt(ci(W['team_top3'][f'swap {name}'] - W['team_top3']['drop Slick Surge']))}, "
               f"Neo {fmt(ci(W['neo_top3'][f'swap {name}'] - W['neo_top3']['drop Slick Surge']))}")
# by gate band for the swaps (Neo top-3)
g = X[X.variant == "base"].set_index("seed").gate.reindex(W["neo_top3"].index)
band = pd.cut(g, [0, 3, 6, 9, 12], labels=["2-3", "4-6", "7-9", "10-12"])
out += ["", "Neo top-3 change by gate (swap vs base):"]
gb = pd.DataFrame({name: (W["neo_top3"][f"swap {name}"] - W["neo_top3"]["base"]).groupby(band, observed=True).mean() for name in SID})
out.append(gb.round(2).to_string())
txt = "\n".join(out); print(txt)
(run / "analysis.txt").write_text(txt + "\n"); R.drop(columns=["_d_team"], errors="ignore").to_csv(run / "summary.csv", index=False)
