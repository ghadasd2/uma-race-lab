"""Analyse a loh_v4_x6_angling.py run: paired effects of Angling and Scheming on the fronts — placings, dueling (rate,
partner, length), Kitasan-Ines gap and speed difference at the final corner / straight, and what happens in races where
it fired. Usage: loh_v4_x6_analyze.py RUN_DIR"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

run = Path(sys.argv[1])
X = pd.read_csv(run / "races.csv.gz")
X["k_top3"] = (X.p0 <= 3) * 100.0; X["i_top3"] = (X.p1 <= 3) * 100.0; X["n_top3"] = (X.p2 <= 3) * 100.0
X["k_win"] = (X.p0 == 1) * 100.0; X["i_win"] = (X.p1 == 1) * 100.0
X["front_win"] = ((X.p0 == 1) | (X.p1 == 1)) * 100.0
X["gap_le3_1875"] = (X.gap_1875 <= 3) * 100.0; X["gap_le3_1625"] = (X.gap_1625 <= 3) * 100.0
for c in ("duel_k", "duel_i", "fronts_duel_each_other", "duel_k_with_opp", "duel_i_with_opp", "duel_k_with_npc",
          "duel_i_with_npc", "fronts_1_2", "as_k", "as_i"):
    X[c] = X[c].astype(float) * 100
X["any_front_duel"] = ((X.duel_k > 0) | (X.duel_i > 0)) * 100.0
lines = []
def say(*a):
    m = " ".join(str(x) for x in a); print(m); lines.append(m)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
V = list(X.variant.unique())
def ci(d):
    d = d.dropna(); se = d.std(ddof=1) / np.sqrt(len(d)); return d.mean(), d.mean() - 1.96 * se, d.mean() + 1.96 * se
def fmt(t, nd=2):
    return f"{t[0]:+.{nd}f} [{t[1]:+.{nd}f}, {t[2]:+.{nd}f}]"
W = {c: X.pivot(index="seed", columns="variant", values=c) for c in X.columns if c not in ("variant", "seed")}
say(f"{len(W['team_top3'])} paired races per variant (seeds 200M). Kitasan/Ines = v4 champion, Neo = X5 build.")

measures = [("team_top3", "team top-3 %"), ("points", "team points / race"), ("k_top3", "Kitasan top-3 %"),
            ("i_top3", "Ines top-3 %"), ("n_top3", "Neo top-3 %"), ("k_win", "Kitasan win %"), ("i_win", "Ines win %"),
            ("front_win", "a front wins %"), ("fronts_1_2", "fronts finish 1-2 %"),
            ("as_k", "A&S fired: Kitasan %"), ("as_i", "A&S fired: Ines %"),
            ("duel_k", "Kitasan duels %"), ("duel_i", "Ines duels %"), ("any_front_duel", "either front duels %"),
            ("fronts_duel_each_other", "Kitasan and Ines duel EACH OTHER %"),
            ("duel_k_with_opp", "Kitasan duels a mock opponent %"), ("duel_i_with_opp", "Ines duels a mock opponent %"),
            ("duel_k_len", "Kitasan duel seconds / race"), ("duel_i_len", "Ines duel seconds / race"),
            ("gap_1625", "Kitasan-Ines gap at 1625 m (m)"), ("gap_1875", "Kitasan-Ines gap at 1875 m (m)"),
            ("gap_le3_1875", "fronts within 3 m at 1875 m %"), ("dspeed_1875", "speed difference at 1875 m (m/s)"),
            ("finish_gap_s", "Kitasan-Ines finish gap (s)")]
rows = []
for c, nm in measures:
    r = {"measure": nm}
    for v in V:
        r[v] = W[c][v].mean()
    for v in V[1:]:
        r[f"{v} vs base"] = fmt(ci(W[c][v] - W[c]["base"]))
    rows.append(r)
say(pd.DataFrame(rows).round(2).to_string(index=False))

say("\nhp-out % (Kitasan, Ines, Neo):")
for v in V:
    x = X[X.variant == v]; say(f"  {v}: {100 * x.hp0.mean():.2f} / {100 * x.hp1.mean():.2f} / {100 * x.hp2.mean():.2f}")

say("\nwhere it fires (m): " + "; ".join(
    f"{v} {nm}: median {X[X.variant == v][f'as_{c}_pos'].median():.0f}, p90 {X[X.variant == v][f'as_{c}_pos'].quantile(.9):.0f}"
    for v in V[1:] for c, nm in (("k", "Kitasan"), ("i", "Ines")) if X[X.variant == v][f"as_{c}"].mean() > 0))

# races where it fired vs the same races in base (selection by firing is identical in base up to 1600 m)
say("\nraces where A&S fired, same races in base (paired):")
rows = []
for v, c in (("Kitasan +A&S", "k"), ("Ines +A&S", "i"), ("both +A&S", "k"), ("both +A&S", "i")):
    x = X[X.variant == v].set_index("seed"); b = X[X.variant == "base"].set_index("seed").loc[x.index]
    m = x[f"as_{c}"] > 0
    r = {"variant": v, "fired for": {"k": "Kitasan", "i": "Ines"}[c], "races %": 100 * m.mean()}
    for col, nm in (("gap_1875", "gap 1875 m"), ("gap_le3_1875", "within 3 m %"), ("fronts_duel_each_other", "duel each other %"),
                    ("any_front_duel", "either duels %"), ("team_top3", "team top-3"), (f"{c}_top3", "own top-3"),
                    ("fronts_1_2", "fronts 1-2 %")):
        r[f"{nm}: with"] = x[m][col].mean(); r[f"{nm}: diff"] = fmt(ci(x[m][col] - b[m][col]))
    rows.append(r)
R = pd.DataFrame(rows).set_index(["variant", "fired for"]).T
say(R.round(2).to_string())

# duel value check in base: top-3 when dueling vs not (descriptive)
b = X[X.variant == "base"]
say("\nbase, descriptive: Kitasan top-3 when she duels {:.1f} % vs not {:.1f} %; Ines {:.1f} % vs {:.1f} %; "
    "team top-3 when the fronts duel each other {:.2f} % vs not {:.2f} %".format(
        b[b.duel_k > 0].k_top3.mean(), b[b.duel_k == 0].k_top3.mean(), b[b.duel_i > 0].i_top3.mean(), b[b.duel_i == 0].i_top3.mean(),
        b[b.fronts_duel_each_other > 0].team_top3.mean(), b[b.fronts_duel_each_other == 0].team_top3.mean()))
(run / "analysis.txt").write_text("\n".join(lines) + "\n")

# ------------------------------------------------------------- clean causal comparison: real A&S vs no-effect clone
if "both +null" in V:
    say("\n== CLEAN: real A&S vs its no-effect twin (identical race until the skill fires)")
    rows = []
    for real, null in (("Kitasan +A&S", "Kitasan +null"), ("Ines +A&S", "Ines +null"), ("both +A&S", "both +null")):
        r = {"pair": real}
        fk, fi = W["as_k"][real] > 0, W["as_i"][real] > 0
        same_fire = ((W["as_k"][real] == W["as_k"][null]) & (W["as_i"][real] == W["as_i"][null])).mean()
        nofire = ~(fk | fi)
        ident = (W["finish_gap_s"][real][nofire] - W["finish_gap_s"][null][nofire]).abs().max()
        r["fires same races %"] = 100 * same_fire; r["no-fire races max diff"] = ident
        for c, nm in (("team_top3", "team top-3"), ("points", "points"), ("k_top3", "Kitasan top-3"), ("i_top3", "Ines top-3"),
                      ("front_win", "a front wins"), ("fronts_1_2", "fronts 1-2"), ("any_front_duel", "either front duels"),
                      ("fronts_duel_each_other", "duel each other"), ("duel_k_len", "Kitasan duel s"), ("duel_i_len", "Ines duel s"),
                      ("gap_1875", "gap 1875 m"), ("gap_le3_1875", "within 3 m at 1875")):
            r[nm] = fmt(ci(W[c][real] - W[c][null]))
        rows.append(r)
    say(pd.DataFrame(rows).set_index("pair").T.to_string())
    say("\nnull vs base (RNG reshuffle only, should be ~0):")
    for null in ("Kitasan +null", "Ines +null", "both +null"):
        say(f"  {null}: team {fmt(ci(W['team_top3'][null] - W['team_top3']['base']))}, either front duels "
            f"{fmt(ci(W['any_front_duel'][null] - W['any_front_duel']['base']))}")
    say("\nraces where it fired (clean, vs the identical-until-then null race):")
    rows = []
    for real, null, c in (("Kitasan +A&S", "Kitasan +null", "k"), ("Ines +A&S", "Ines +null", "i"),
                          ("both +A&S", "both +null", "k"), ("both +A&S", "both +null", "i")):
        m = W[f"as_{c}"][real] > 0
        r = {"pair": real, "fired for": {"k": "Kitasan", "i": "Ines"}[c], "races %": 100 * m.mean()}
        for col, nm in (("gap_1875", "gap 1875 m"), ("gap_le3_1875", "within 3 m %"), ("fronts_duel_each_other", "duel each other %"),
                        ("any_front_duel", "either duels %"), ("team_top3", "team top-3"), (f"{c}_top3", "own top-3"),
                        ({"k": "i", "i": "k"}[c] + "_top3", "other front top-3"), (f"{c}_win", "own win %"), ("fronts_1_2", "fronts 1-2 %")):
            r[f"{nm} (null)"] = W[col][null][m].mean(); r[f"{nm} diff"] = fmt(ci(W[col][real][m] - W[col][null][m]))
        rows.append(r)
    say(pd.DataFrame(rows).set_index(["pair", "fired for"]).T.round(2).to_string())
    (run / "analysis.txt").write_text("\n".join(lines) + "\n")
