"""Analyse a loh_v4_x1_ignited_wit.py run: paired effects of Ignited Spirit WIT on Neo (frames) and on outcomes,
by gate and by activation position, plus one example race with a per-second timeline.
Usage: loh_v4_x1_analyze.py RUN_DIR"""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
from umasim import mock

run = Path(sys.argv[1])
lines = []
def say(*a):
    m = " ".join(str(x) for x in a); print(m); lines.append(m)
pd.set_option("display.width", 250)

def ci(d):
    d = pd.Series(d).dropna(); se = d.std(ddof=1) / np.sqrt(len(d))
    return d.mean(), d.mean() - 1.96 * se, d.mean() + 1.96 * se, len(d)
def fmt(t, nd=2):
    return f"{t[0]:+.{nd}f} [{t[1]:+.{nd}f}, {t[2]:+.{nd}f}] (n={t[3]})"

# ---------------------------------------------------------------- frames
F = pd.read_csv(run / "neo_frames_features.csv.gz", keep_default_na=False, na_values=[""])
V = {v: F[F.variant == v].set_index("seed").sort_index() for v in F.variant.unique()}
full, none = V["full"], V["none"]
say("== activation (full variant, frames sample)")
say(f"fired {100 * full.fired.mean():.1f} % of races; position m: mean {full.act_pos.mean():.0f}, "
    f"quartiles {full.act_pos.quantile(.25):.0f} / {full.act_pos.median():.0f} / {full.act_pos.quantile(.75):.0f}, "
    f"min {full.act_pos.min():.0f}, max {full.act_pos.max():.0f}; blocked at activation {100 * full.act_blocked.astype(float).mean():.1f} %")
same = (full.fired == none.fired).mean()
pre = full[~full.fired.astype(bool)]
ident = (pre.finish_t - none.loc[pre.index].finish_t).abs().max() if len(pre) else float("nan")
say(f"full and none fire in the same races: {100 * same:.1f} %; races where it did not fire: max |finish time diff| = {ident:.6f} s")

say("\n== inside the 9.6 s window (per variant, races where it fired)")
cols = ["win_moving_s", "win_lateral", "win_blocked_s", "win_mean_speed", "pos_end_win", "pos_end_win_plus10", "rank_end_win"]
tab = pd.DataFrame({v: V[v][V[v].fired.astype(bool)][cols].astype(float).mean() for v in V}).T
tab["win_lateral_horse_widths"] = tab.win_lateral / (1 / 18)
say(tab.round(3).to_string())

say("\n== paired differences vs none (same race until activation; races where it fired)")
rows = []
for v in [x for x in V if x != "none"]:
    a = V[v]; m_ = a.fired.astype(bool) & none.fired.astype(bool)
    a, b = a[m_], none[m_]
    r = {"variant": v}
    for c in ["win_moving_s", "win_blocked_s", "win_mean_speed", "pos_end_win", "pos_end_win_plus10", "rank_end_win",
              "t_400", "t_1000", "t_1600", "t_2000", "finish_t", "rank_1000", "rank_1600", "rank_2000",
              "blocked_s_p0", "blocked_s_p1", "blocked_s_p2", "blocked_s_p3", "lane_2000", "place"]:
        r[c] = fmt(ci(a[c].astype(float) - b[c].astype(float)), 3)
    r["top3"] = fmt(ci(100 * ((a.place <= 3).astype(float) - (b.place <= 3).astype(float))), 2)
    rows.append(r)
P = pd.DataFrame(rows).set_index("variant").T
say(P.to_string())

# ---------------------------------------------------------------- outcomes
O = pd.read_csv(run / "outcome_summary.csv", keep_default_na=False, na_values=[""])
say("\n== outcomes (part 1, paired on the same seeds)")
show = ["variant", "team_top3", "neo_top3", "points", "team_vs_none", "team_vs_none_lo", "team_vs_none_hi",
        "neo_vs_none", "neo_vs_none_lo", "neo_vs_none_hi", "identical_to_full_%"]
say(O[show].round(2).to_string(index=False))

D = pd.read_csv(run / "outcomes.csv.gz", keep_default_na=False, na_values=[""])
gates = {int(s): mock.draw(int(s))["gates"][2] + 1 for s in D.seed.unique()}
D["gate"] = D.seed.map(gates)
D["neo"] = (D.p2 <= 3) * 100.0
w = D.pivot(index="seed", columns="variant", values="neo"); tw = D.pivot(index="seed", columns="variant", values="top3") * 100
g = pd.Series(gates).reindex(w.index)
band = pd.cut(g, [0, 3, 6, 9, 12], labels=["2-3", "4-6", "7-9", "10-12"])
say("\n== Neo top-3 by gate: full vs none (part 1)")
rows = []
for bnd in ["2-3", "4-6", "7-9", "10-12"]:
    m_ = band == bnd
    rows.append({"gate": bnd, "races": int(m_.sum()), "neo_top3_full": w.full[m_].mean(), "neo_top3_none": w.none[m_].mean(),
                 "neo_diff": fmt(ci(w.full[m_] - w.none[m_])), "team_diff": fmt(ci(tw.full[m_] - tw.none[m_]))})
say(pd.DataFrame(rows).round(2).to_string(index=False))

say("\n== by activation position (frames sample): paired finish-time and top-3 change, full - none")
m_ = full.fired.astype(bool)
bins = pd.cut(full.act_pos[m_], [0, 100, 200, 300, 400])
rows = []
for b_, idx in full[m_].groupby(bins, observed=True).groups.items():
    rows.append({"activation_m": str(b_), "races": len(idx),
                 "moving_s": full.loc[idx].win_moving_s.mean(),
                 "metres_ahead_end_win": (full.loc[idx].pos_end_win - none.loc[idx].pos_end_win).mean(),
                 "finish_t_diff": fmt(ci(full.loc[idx].finish_t - none.loc[idx].finish_t), 3),
                 "top3_diff": fmt(ci(100 * ((full.loc[idx].place <= 3).astype(float) - (none.loc[idx].place <= 3).astype(float))))})
say(pd.DataFrame(rows).round(2).to_string(index=False))

say("\n== moving vs not moving lanes in the window")
x = full[m_].copy(); x["gain"] = full[m_].pos_end_win - none.loc[x.index].pos_end_win
x["mv"] = pd.cut(x.win_moving_s, [-0.01, 0.5, 2, 4, 9.7], labels=["<0.5 s", "0.5-2 s", "2-4 s", ">4 s"])
say(x.groupby("mv", observed=True).agg(races=("gain", "size"), metres_ahead=("gain", "mean"),
                                       finish_dt=("finish_t", lambda s: (s - none.loc[s.index].finish_t).mean())).round(3).to_string())
corr = np.corrcoef(x.win_moving_s, x.gain)[0, 1]
say(f"corr(moving seconds, metres gained by window end) = {corr:.2f}; metres per moving second (OLS slope) = "
    f"{np.polyfit(x.win_moving_s, x.gain, 1)[0]:.3f}")

(run / "analysis.txt").write_text("\n".join(lines) + "\n")
print("wrote", run / "analysis.txt")
