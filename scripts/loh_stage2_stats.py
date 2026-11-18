"""Stage 2: stat allocation search. Usage: loh_stage2_stats.py TEAM.json
For each of my umas (others held at TEAM): every legal spread on a 50-pt grid (ranges + total 6100),
paired successive halving vs TEAM in both worlds; then 25-pt refinement around each uma's top spreads;
then the per-uma winners are combined and checked jointly."""
import itertools, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from umasim import loh, opt

team = json.loads(Path(sys.argv[1]).read_text())
out = opt.run_dir("stage2-stats")
log_f = open(out / "log.txt", "a")
def log(*a):
    msg = " ".join(str(x) for x in a); print(msg, flush=True); log_f.write(msg + "\n"); log_f.flush()

ranges, total = loh.stat_box()
def grid(step, center=None, radius=None):
    g = []
    for lo, hi in ranges:
        g.append(range(lo, hi + 1, step))
    for c in itertools.product(*g):
        if sum(c) != total:
            continue
        if center and max(abs(a - b) for a, b in zip(c, center)) > radius:
            continue
        yield list(c)

def variants_for(spreads_by_uma):
    v = {"base": team}
    for i, spreads in spreads_by_uma.items():
        for s in spreads:
            if s == team[i]["stats"]:
                continue
            t = [dict(x) for x in team]; t[i] = dict(team[i], stats=s)
            v[f"{team[i]['name']}: {s}"] = t
    return v

opt.save_team(out / "input_team.json", team)
coarse = variants_for({i: list(grid(50)) for i in range(3)})
log("coarse variants", len(coarse) - 1)
hist = opt.halving(coarse, n0=200, keep=0.2, rounds=3, grow=3, log=log, out_dir=out, seed_base=2_000_000)
hist.to_csv(out / "coarse_all_rounds.csv", index=False)

last = hist[hist["round"] == hist["round"].max()]
best = {}
for i, u in enumerate(team):
    rows = last[last.variant.str.startswith(u["name"] + ":")]
    best[i] = [json.loads(v.split(": ", 1)[1]) for v in rows.head(2).variant]
log("coarse winners", best)

fine_spreads = {i: [s for c in best[i] for s in grid(25, c, 25)] for i in best}
fine = variants_for(fine_spreads)
log("fine variants", len(fine) - 1)
hist2 = opt.halving(fine, n0=600, keep=0.3, rounds=2, grow=3, log=log, out_dir=out, seed_base=3_000_000)
hist2.to_csv(out / "fine_all_rounds.csv", index=False)
last2 = hist2[hist2["round"] == hist2["round"].max()]
final = [dict(x) for x in team]
for i, u in enumerate(team):
    rows = last2[last2.variant.str.startswith(u["name"] + ":")]
    if len(rows) and rows.iloc[0].get("d_top3", 0) > 0:
        final[i] = dict(u, stats=json.loads(rows.iloc[0].variant.split(": ", 1)[1]))
opt.save_team(out / "best_team.json", final)
df = opt.evaluate({"base": team, "best": final}, list(range(4_000_000, 4_003_000)))
s = opt.summarize(df); s.to_csv(out / "combined_check.csv", index=False)
log(s.round(3).to_string()); log("done", out)
