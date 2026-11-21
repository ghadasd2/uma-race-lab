"""Analyse a loh_v4_x2_ignited_wit_effects.py run: (1) position keep / pace down, (2) blocking, (3) races where
Ignited Spirit WIT hurts Neo, with a mechanism split for the hurt and helped races. Paired full vs none.
Usage: loh_v4_x2_analyze.py RUN_DIR"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

run = Path(sys.argv[1])
lines = []
def say(*a):
    m = " ".join(str(x) for x in a); print(m); lines.append(m)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
def ci(d):
    d = pd.Series(d, dtype=float).dropna(); se = d.std(ddof=1) / np.sqrt(len(d)) if len(d) > 1 else np.nan
    return d.mean(), d.mean() - 1.96 * se, d.mean() + 1.96 * se
def f(t, nd=3):
    return f"{t[0]:+.{nd}f} [{t[1]:+.{nd}f}, {t[2]:+.{nd}f}]"
def pair(df, a="full", b="none"):
    x = df[df.variant == a].set_index("seed").sort_index(); y = df[df.variant == b].set_index("seed").sort_index()
    return x, y.loc[x.index]

A = pd.read_csv(run / "partA_races.csv.gz", keep_default_na=False, na_values=[""])
B = pd.read_csv(run / "partB_races.csv.gz", keep_default_na=False, na_values=[""])
fa, na = pair(A); fb, nb = pair(B)
fired = fa.fired.astype(bool)
say(f"part A: {len(fa)} paired races (fired in {100 * fired.mean():.1f} %); part B: {len(fb)} paired races with dense frames")
pa, pp = pair(A, "placebo", "none")
say(f"placebo (HP +0.01 %): Neo place identical to none in {100 * (pa.place == pp.place).mean():.2f} % of races, "
    f"finish time identical in {100 * ((pa.finish_t - pp.finish_t).abs() < 1e-9).mean():.2f} %")

# ------------------------------------------------------------- 1 position keep
say("\n== 1. Position keep (Neo, 0-1000 m), per race; paired full - none on all races")
rows = []
for c, nm in (("pace_down_n", "pace-down entries"), ("pace_down_s", "pace-down seconds"), ("pace_down_m", "pace-down metres"),
              ("pd_s_before", "pace-down s before skill"), ("pd_s_window", "pace-down s during 9.6 s window"),
              ("pd_s_after20", "pace-down s in 20 s after window"), ("pd_s_later", "pace-down s later"),
              ("pace_up_n", "pace-up entries"), ("pace_up_s", "pace-up seconds"), ("pace_up_ex_n", "pace-up-ex entries"),
              ("speed_up_n", "speed-up entries"), ("overtake_n", "overtake entries")):
    rows.append({"measure": nm, "with": fa[c].mean(), "without": na[c].mean(), "diff [95% CI]": f(ci(fa[c] - na[c]))})
for nm, x, y in (("races with any pace down %", fa.pace_down_n > 0, na.pace_down_n > 0),
                 ("races with pace down during/after window %", fa.pd_n_window_or_after20 > 0, na.pd_n_window_or_after20 > 0)):
    rows.append({"measure": nm, "with": 100 * x.mean(), "without": 100 * y.mean(),
                 "diff [95% CI]": f(ci(100 * (x.astype(float) - y.astype(float))), 2)})
say(pd.DataFrame(rows).round(3).to_string(index=False))
more = (fa.pace_down_s - na.pace_down_s)
say(f"pace-down time longer with the skill in {100 * (more > 1e-6).mean():.1f} % of races, shorter in "
    f"{100 * (more < -1e-6).mean():.1f} %, same in {100 * (more.abs() <= 1e-6).mean():.1f} %")
say(f"gap to pacemaker at first pace-down entry (m): with {fa.pd_first_gap.mean():.2f}, without {na.pd_first_gap.mean():.2f}; "
    f"first entry at {fa.pd_first_pos.median():.0f} m vs {na.pd_first_pos.median():.0f} m (median)")
say(f"open at end of position keep (not timed): with {(fa.open_at_end.fillna('') != '').mean() * 100:.2f} %, without {(na.open_at_end.fillna('') != '').mean() * 100:.2f} %")
# does extra pace down give the gain back? split races by pace-down change
d_t = fa.finish_t - na.finish_t; d_top = 100 * ((fa.place <= 3).astype(float) - (na.place <= 3).astype(float))
grp = pd.cut(more, [-1e9, -0.5, -1e-6, 1e-6, 0.5, 1e9], labels=["<= -0.5 s", "-0.5..0 s", "0", "0..0.5 s", ">= 0.5 s"])
say("\nby change in pace-down seconds (with - without):")
say(pd.DataFrame({"races": grp.value_counts().sort_index(), "finish_dt_s": d_t.groupby(grp, observed=True).mean(),
                  "neo_top3_diff_pp": d_top.groupby(grp, observed=True).mean()}).round(3).to_string())

# ------------------------------------------------------------- 2 blocking
say("\n== 2. Front blocking (Neo, dense frames), per race; paired full - none")
rows = []
for ph, nm in (("window", "during the 9.6 s window"), ("p0", "opening 0-400 m"), ("p1", "middle 400-1600 m"),
               ("p2", "late 1600-2000 m"), ("p3", "final 2000-2400 m"), ("all", "whole race")):
    s_ = f"blk_s_{ph}"; a_ = f"blk_any_{ph}"
    r = {"phase": nm, "blocked s with": fb[s_].mean(), "blocked s without": nb[s_].mean(), "diff s": f(ci(fb[s_] - nb[s_]))}
    r["% races blocked with"] = 100 * fb[a_].astype(bool).mean(); r["without"] = 100 * nb[a_].astype(bool).mean()
    r["diff pp"] = f(ci(100 * (fb[a_].astype(float) - nb[a_].astype(float))), 2)
    if f"blk_ep_{ph}" in fb:
        r["episodes with"] = fb[f"blk_ep_{ph}"].mean(); r["episodes without"] = nb[f"blk_ep_{ph}"].mean()
    rows.append(r)
say(pd.DataFrame(rows).round(3).to_string(index=False))
dl = (fb.blk_s_p1 + fb.blk_s_p2 + fb.blk_s_p3) - (nb.blk_s_p1 + nb.blk_s_p2 + nb.blk_s_p3)
say(f"blocked time after 400 m: more with the skill in {100 * (dl > 1e-6).mean():.1f} % of races, less in "
    f"{100 * (dl < -1e-6).mean():.1f} %, same in {100 * (dl.abs() <= 1e-6).mean():.1f} %")

# ------------------------------------------------------------- 3 hurt
say("\n== 3. Races where the skill hurts (part A, all paired races)")
dp = fa.place - na.place
nt = (na.place <= 3); ft = (fa.place <= 3)
rows = [{"outcome": "Neo finishes higher", "% races": 100 * (dp < 0).mean()},
        {"outcome": "Neo same place", "% races": 100 * (dp == 0).mean()},
        {"outcome": "Neo finishes lower", "% races": 100 * (dp > 0).mean()},
        {"outcome": "Neo gains top 3 (out -> in)", "% races": 100 * (~nt & ft).mean()},
        {"outcome": "Neo loses top 3 (in -> out)", "% races": 100 * (nt & ~ft).mean()},
        {"outcome": "Neo faster finish", "% races": 100 * (d_t < -1e-9).mean()},
        {"outcome": "Neo slower finish", "% races": 100 * (d_t > 1e-9).mean()}]
dt3 = fa.team_top3 - na.team_top3; dpt = fa.points - na.points
rows += [{"outcome": "team top-3 count up", "% races": 100 * (dt3 > 0).mean()},
         {"outcome": "team top-3 count down", "% races": 100 * (dt3 < 0).mean()},
         {"outcome": "team points up", "% races": 100 * (dpt > 0).mean()},
         {"outcome": "team points down", "% races": 100 * (dpt < 0).mean()}]
say(pd.DataFrame(rows).round(2).to_string(index=False))
say(f"net: Neo top-3 {f(ci(100 * (ft.astype(float) - nt.astype(float))), 2)} pp, team top-3 {f(ci(dt3), 2)} pp, "
    f"points {f(ci(dpt), 2)} per race")
say(f"when Neo finishes lower: mean places lost {dp[dp > 0].mean():.2f}; when higher: mean places gained {-dp[dp < 0].mean():.2f}")
# where the place changes happen
chg = dp != 0
say(f"place changes happen in {100 * chg.mean():.1f} % of races; skill did not fire in {100 * (~fired & chg).sum() / max(chg.sum(), 1):.1f} % of those")

say("\n== 3b. Why: mechanism split (part B races where the skill fired)")
m_ = fb.fired.astype(bool)
x = pd.DataFrame({"dplace": fb.place - nb.place, "gain_m": fb.pos_end_win - nb.pos_end_win,
                  "d_pd_s": fb.pace_down_s - nb.pace_down_s,
                  "d_blk_late": (fb.blk_s_p1 + fb.blk_s_p2 + fb.blk_s_p3) - (nb.blk_s_p1 + nb.blk_s_p2 + nb.blk_s_p3),
                  "d_blk_win": fb.blk_s_window - nb.blk_s_window.fillna(0),
                  "d_rank1600": fb.rank_1600 - nb.rank_1600, "d_t": fb.finish_t - nb.finish_t,
                  "moving_s": fb.moving_s_window})[m_]
def cause(r):
    if r.gain_m < -0.05: return "behind at end of window"
    if r.d_blk_late > 0.5: return "more blocked after 400 m (+0.5 s or more)"
    if r.d_pd_s > 0.5: return "more pace down (+0.5 s or more)"
    if r.d_rank1600 > 0: return "worse position at 1600 m"
    return "ahead at 1600 m, lost it later"
def cause_good(r):
    if r.gain_m > 0.05 and r.d_rank1600 < 0: return "ahead at window end and at 1600 m"
    if r.gain_m > 0.05: return "ahead at window end"
    if r.d_blk_late < -0.5: return "less blocked after 400 m"
    if r.d_pd_s < -0.5: return "less pace down"
    return "other"
hurt = x[x.dplace > 0]; helped = x[x.dplace < 0]
say(f"part B: Neo lower in {len(hurt)} races ({100 * len(hurt) / len(x):.1f} %), higher in {len(helped)} ({100 * len(helped) / len(x):.1f} %)")
say("hurt races by first matching cause:")
say((hurt.apply(cause, axis=1).value_counts(normalize=True) * 100).round(1).to_string())
say("helped races by first matching cause:")
say((helped.apply(cause_good, axis=1).value_counts(normalize=True) * 100).round(1).to_string())
say("\nmean of each measure (hurt vs helped vs no change):")
say(pd.DataFrame({"hurt": hurt.mean(), "helped": helped.mean(), "same": x[x.dplace == 0].mean()}).round(3).to_string())
say(f"share of fired races ending the window behind (<-0.05 m): {100 * (x.gain_m < -0.05).mean():.2f} %; "
    f"of those, Neo lower {100 * (x[x.gain_m < -0.05].dplace > 0).mean():.1f} %, higher {100 * (x[x.gain_m < -0.05].dplace < 0).mean():.1f} %")
# hurt rate by gate (part A)
g = pd.cut(fa.gate, [0, 3, 6, 9, 12], labels=["2-3", "4-6", "7-9", "10-12"])
say("\nby gate (part A): % races Neo lower / higher, top-3 lost / gained")
say(pd.DataFrame({"races": g.value_counts().sort_index(), "lower%": (dp > 0).groupby(g, observed=True).mean() * 100,
                  "higher%": (dp < 0).groupby(g, observed=True).mean() * 100,
                  "top3_lost%": (nt & ~ft).groupby(g, observed=True).mean() * 100,
                  "top3_gained%": (~nt & ft).groupby(g, observed=True).mean() * 100}).round(2).to_string())
(run / "analysis.txt").write_text("\n".join(lines) + "\n")
print("wrote", run / "analysis.txt")

# opening pace down that is still running when the skill fires
ov = na.pd_s_window > 0
d = fa.pace_down_s - na.pace_down_s
say(f"\nopening pace down still running when the skill fires: {100 * ov.mean():.1f} % of races; in those, pace down lasts "
    f"{f(ci(d[ov]))} s longer with the skill; in the others {f(ci(d[~ov]))} s")
extra = (fa.pace_down_n - na.pace_down_n)
say(f"extra pace-down entries: +1 in {100 * (extra > 0).mean():.2f} % of races, -1 in {100 * (extra < 0).mean():.2f} %")
loss = (fa.pace_down_s - na.pace_down_s) * 17.5 * (1 - 0.915) - (fa.pace_up_s - na.pace_up_s) * 19 * 0.04
say(f"rough give-back from position keep: {loss.mean():.3f} m per race (pace down at x0.915 of ~17.5 m/s, pace up x1.04 of ~19 m/s)")
(run / "analysis.txt").write_text("\n".join(lines) + "\n")
