"""Stage 1: skill screening for my team (drop-one on kit skills, add-one on candidate pools)."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from umasim import loh, opt

INHERITED = ["Red Shift/LP1211-M", "Bring on the Banquet!", "Operation Cacao", "Moving Past, and Beyond", "Into High Gear!"]
EXTRA = ["Racing Spirit: Stamina", "Mad Dash", "In Body and Mind", "Firm Resolve", "Killer Tunes"]

out = opt.run_dir("stage1-skills")
log_f = open(out / "log.txt", "a")
def log(*a):
    msg = " ".join(str(x) for x in a); print(msg, flush=True); log_f.write(msg + "\n"); log_f.flush()

base = loh.my_baseline()
opt.save_team(out / "baseline_team.json", base)
log("baseline:", [(b["name"], b["stats"], sum(b["stats"]), len(b["skills"]) + 1) for b in base])

# --- drop-one (full precision, no elimination)
drops = {"base": base}
for i, b in enumerate(base):
    for s in b["skills"]:
        t = [dict(x) for x in base]; t[i] = opt.drop_skill(b, s)
        drops[f"{b['name']}: -{s}"] = t
n_drop = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
t0 = time.time()
df = opt.evaluate(drops, list(range(500_000, 500_000 + n_drop // 2)))
summ = opt.summarize(df); summ.to_csv(out / "drop_one.csv", index=False)
log(f"drop-one: {len(drops)} variants x {n_drop} races in {time.time() - t0:.0f}s")

# --- add-one (successive halving)
adds = {"base": base}
for i, b in enumerate(base):
    for s in opt.candidate_pool(b, EXTRA, INHERITED):
        t = [dict(x) for x in base]; t[i] = opt.add_skill(b, s)
        adds[f"{b['name']}: +{s}"] = t
log(f"add-one candidates: {len(adds) - 1}")
hist = opt.halving(adds, n0=150, keep=0.25, rounds=3, grow=3, log=log, out_dir=out)
hist.to_csv(out / "add_one_all_rounds.csv", index=False)
log("done", out)
