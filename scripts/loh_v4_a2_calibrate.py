"""v4 step A2: weaken the mock field until the CN team scores 95-97 % team top-3 (target 96).
Mock logic is unchanged; two knobs: MOCK_STAT_SHIFT (every stat range bound lowered; stamina optionally kept)
and EXTRA_DROP (more non-gold skills dropped).
  coarse grid : shift 0..300 step 50 x {stamina shifted, stamina kept} x extra drop 0/1/2, N_COARSE races each
  confirm     : the 3 settings closest to 96 % (smallest change on ties) on N_CONFIRM fresh races, plus my v3 base and
                v3 champion under each (team top-3, per-uma HP-out)
Usage: loh_v4_a2_calibrate.py N_COARSE N_CONFIRM"""
import itertools, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import loh, mock, opt

NC, NF = int(sys.argv[1]), int(sys.argv[2])
out = opt.run_dir("v4-a2-calibrate")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()

CN = loh.opponent_team("cn")
TARGET = 96.0


def setting(shift, keep_sta, extra):
    mock.MOCK_STAT_SHIFT, mock.SHIFT_STAMINA, mock.EXTRA_DROP = shift, not keep_sta, extra
    mock._DRAWS.clear()


def run(teams, seeds):
    df = mock.evaluate(teams, seeds)
    return df, mock.summarize(df, base="__none__")


grid = [(s, k, e) for s, k, e in itertools.product(range(0, 301, 50), (False, True), (0, 1, 2)) if not (s == 0 and k)]
seeds = list(range(100_000_000, 100_000_000 + NC))
rows = []
t0 = time.time()
for s, k, e in grid:
    setting(s, k, e)
    df, sm = run({"cn": CN}, seeds)
    r = sm.iloc[0]
    rows.append({"shift": s, "stamina_kept": k, "extra_drop": e, "cn_top3": r.top3, "cn_points": r.points,
                 "n": len(df), "change": s + 60 * e})
    log(f"[{len(rows)}/{len(grid)} {time.time() - t0:.0f}s] shift {s} stamina_kept {k} extra_drop {e}: CN {r.top3:.2f}%")
g = pd.DataFrame(rows)
g.to_csv(out / "grid.csv", index=False)
log(g.round(2).to_string())

# confirm: closest to target; ties broken by the smallest change, then stamina kept
g["dist"] = (g.cn_top3 - TARGET).abs()
cand = g[(g.cn_top3 >= 94.5) & (g.cn_top3 <= 97.5)].sort_values(["dist", "change", "stamina_kept"], ascending=[True, True, False])
if len(cand) < 3:
    cand = g.sort_values(["dist", "change"])
cand = cand.head(3)
v3_base = json.loads(Path("data/loh/my_team_v3_base.json").read_text())
v3_champ = json.loads(Path("data/loh/my_team_v3_champion.json").read_text())
seeds_f = list(range(100_500_000, 100_500_000 + NF))
conf = []
for _, c in cand.iterrows():
    setting(int(c["shift"]), bool(c.stamina_kept), int(c.extra_drop))
    df, sm = run({"cn": CN, "v3_base": v3_base, "v3_champion": v3_champ}, seeds_f)
    for _, r in sm.iterrows():
        x = df[df.variant == r.variant]
        bt = mock.batches(x)
        conf.append({"shift": int(c["shift"]), "stamina_kept": bool(c.stamina_kept), "extra_drop": int(c.extra_drop),
                     "variant": r.variant, "top3": r.top3, "points": r.points, "batch_p10": bt.team_top3.quantile(.1),
                     "batch_p90": bt.team_top3.quantile(.9), "P_batch>=95": 100 * (bt.team_top3 >= 95).mean(),
                     "P_batch>=97.1": 100 * (bt.team_top3 >= 97.1).mean(), "pts_per_batch": bt.points.mean(),
                     "ind0": r.ind0, "ind1": r.ind1, "ind2": r.ind2,
                     "hp0%": r["hp0%"], "hp1%": r["hp1%"], "hp2%": r["hp2%"], "hp_ok": r.hp_ok, "hp_status": mock.hp_status(x)})
    log(f"confirm shift {int(c['shift'])} stamina_kept {bool(c.stamina_kept)} extra {int(c.extra_drop)}:\n" +
        pd.DataFrame(conf[-3:]).drop(columns=["shift", "stamina_kept", "extra_drop"]).round(2).to_string())
pd.DataFrame(conf).to_csv(out / "confirm.csv", index=False)
log("done", out)
