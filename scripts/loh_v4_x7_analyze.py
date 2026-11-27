"""Analyse a loh_v4_x7_angling_mocks.py run: clean effects (real vs no-effect twin) of Angling and Scheming on the mocks,
and on mocks + my fronts; plus what happens in races where a mock fired it. Usage: loh_v4_x7_analyze.py RUN_DIR"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

run = Path(sys.argv[1])
X = pd.read_csv(run / "races.csv.gz", low_memory=False)
X["k_top3"] = (X.p0 <= 3) * 100.0; X["i_top3"] = (X.p1 <= 3) * 100.0; X["n_top3"] = (X.p2 <= 3) * 100.0
X["mine_win"] = (X.winner == "mine") * 100.0; X["mock_win"] = (X.winner == "mock") * 100.0
X["mock_leads_1600"] = (X.leader_1600 == "mock") * 100.0; X["mock_leads_1875"] = (X.leader_1875 == "mock") * 100.0
X["fronts_1_2"] = ((X.p0 <= 2) & (X.p1 <= 2)) * 100.0
for c in ("duel_k", "duel_i", "duel_k_with_front", "duel_k_with_mock", "duel_i_with_mock", "as_mine", "as_mock"):
    X[c] = X[c].astype(float) * 100
X["either_duels"] = ((X.duel_k > 0) | (X.duel_i > 0)) * 100.0
X["front_duels_mock"] = ((X.duel_k_with_mock > 0) | (X.duel_i_with_mock > 0)) * 100.0
W = {c: X.pivot(index="seed", columns="variant", values=c) for c in X.columns if c not in ("variant", "seed", "winner", "leader_1600",
                                                                                             "leader_1875", "as_mock_strategy")}
lines = []
def say(*a):
    m = " ".join(str(x) for x in a); print(m); lines.append(m)
def ci(d):
    d = d.dropna(); se = d.std(ddof=1) / np.sqrt(len(d)) if len(d) > 1 else np.nan; return d.mean(), d.mean() - 1.96 * se, d.mean() + 1.96 * se
def fmt(t, nd=2):
    return f"{t[0]:+.{nd}f} [{t[1]:+.{nd}f}, {t[2]:+.{nd}f}]"
pd.set_option("display.width", 250)
say(f"{len(W['team_top3'])} paired races per variant (seeds 200M). Fronts = v4 champion, Neo = X5 build, mocks as calibrated (CN 96 %).")
M = [("team_top3", "team top-3 %"), ("points", "team points / race"), ("k_top3", "Kitasan top-3 %"), ("i_top3", "Ines top-3 %"),
     ("n_top3", "Neo top-3 %"), ("opp_top3", "mock top-3 %"), ("mine_win", "my team wins %"), ("mock_win", "a mock wins %"),
     ("fronts_1_2", "my fronts 1-2 %"), ("as_mock", "A&S fired by a mock %"), ("as_mine", "A&S fired by my front %"),
     ("mock_leads_1600", "mock leads at 1600 m %"), ("mock_leads_1875", "mock leads at 1875 m %"),
     ("either_duels", "either of my fronts duels %"), ("duel_k_with_front", "my fronts duel each other %"),
     ("front_duels_mock", "my front duels a mock %"), ("gap_k_i_1875", "Kitasan-Ines gap at 1875 m"),
     ("leader_to_my_front_1875", "leader ahead of my best front at 1875 m (m)")]
rows = []
for c, nm in M:
    r = {"measure": nm, "base": W[c]["base"].mean(), "mocks +A&S": W[c]["mocks +A&S"].mean(), "all +A&S": W[c]["all +A&S"].mean(),
         "mocks: A&S vs twin": fmt(ci(W[c]["mocks +A&S"] - W[c]["mocks +null"])),
         "all: A&S vs twin": fmt(ci(W[c]["all +A&S"] - W[c]["all +null"])),
         "all vs mocks-only (A&S)": fmt(ci(W[c]["all +A&S"] - W[c]["mocks +A&S"]))}
    rows.append(r)
say(pd.DataFrame(rows).round(2).to_string(index=False))
for v in ("mocks +null", "all +null"):
    say(f"RNG reshuffle check {v} vs base: team {fmt(ci(W['team_top3'][v] - W['team_top3']['base']))}")
x = X[X.variant == "mocks +A&S"]
say(f"\nmock firings by strategy: {x.as_mock_strategy.value_counts().to_dict()}; position median {x.as_mock_pos.median():.0f} m")
say(f"races with 0/1/2/3 mock front runners: {X[X.variant == 'base'].mock_fronts.value_counts().sort_index().to_dict()}")

say("\nraces where a mock fired it (clean: vs the identical-until-then twin):")
rows = []
for real, null in (("mocks +A&S", "mocks +null"), ("all +A&S", "all +null")):
    m = W["as_mock"][real] > 0
    r = {"pair": real, "races %": 100 * m.mean()}
    for c, nm in (("team_top3", "team top-3"), ("k_top3", "Kitasan top-3"), ("i_top3", "Ines top-3"), ("mock_win", "mock wins %"),
                  ("mine_win", "my team wins %"), ("either_duels", "my fronts duel %"), ("front_duels_mock", "my front duels a mock %"),
                  ("leader_to_my_front_1875", "leader lead at 1875 m"), ("points", "points")):
        r[f"{nm} (twin)"] = W[c][null][m].mean(); r[f"{nm} diff"] = fmt(ci(W[c][real][m] - W[c][null][m]))
    rows.append(r)
say(pd.DataFrame(rows).set_index("pair").T.round(2).to_string())
by = X[X.variant == "base"].groupby("mock_fronts")
say("\nbase by number of mock front runners: " + "; ".join(f"{k}: team {g.team_top3.mean():.2f} %, mock leads at 1600 m "
                                                           f"{100 * (g.leader_1600 == 'mock').mean():.1f} %" for k, g in by))
(run / "analysis.txt").write_text("\n".join(lines) + "\n")
