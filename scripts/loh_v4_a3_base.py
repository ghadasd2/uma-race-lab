"""v4 step A3: the v4 base team = the v3 champion made legal under v4 rules.
  * front start-accel rule (buildgen.valid)
  * HP-out floor: any uma over 3/175 gets +50 stamina, paid by speed (cost-neutral), until all pass on N races
Writes data/loh/my_team_v4_base.json.
Usage: loh_v4_a3_base.py N"""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import buildgen as G, mock, opt

N = int(sys.argv[1])
out = opt.run_dir("v4-a3-base")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()


def neutral(stats, k, val):
    """Set stat k to val; speed pays/refunds the in-game cost difference (2 per speed point above 1200)."""
    s = list(stats); before = mock.stat_cost(s); s[k] = val
    diff = mock.stat_cost(s) - before
    s[0] -= -(-diff // 2) if s[0] > 1200 else diff
    return s


team = json.loads(Path("data/loh/my_team_v3_champion.json").read_text())
for b in team:
    ok, why = G.valid(b, b["skills"])
    log(f"{b['name']}: valid={ok} ({why}) stats {b['stats']} cost {mock.stat_cost(b['stats'])}")
    assert ok, why
seeds = list(range(101_000_000, 101_000_000 + N))
hist = []
for it in range(8):
    df = mock.evaluate({"base": team}, seeds)
    rates = mock.hp_rates(df)
    sm = mock.summarize(df, base="__none__").iloc[0]
    hist.append({"iter": it, "top3": sm.top3, "points": sm.points, **{f"hp{k}%": 100 * r for k, r in enumerate(rates)},
                 **{f"stats{k}": "/".join(map(str, b["stats"])) for k, b in enumerate(team)}})
    log(f"iter {it}: team top3 {sm.top3:.2f}  HP-out % " + " ".join(f"{100 * r:.2f}" for r in rates) +
        f"  status {mock.hp_status(df)}")
    bad = [k for k, r in enumerate(rates) if r > mock.HP_FLOOR]
    if not bad:
        break
    for k in bad:
        b = team[k]
        b["stats"] = neutral(b["stats"], 1, b["stats"][1] + 50)
        log(f"   {b['name']}: stamina +50 -> {b['stats']} cost {mock.stat_cost(b['stats'])}")
pd.DataFrame(hist).to_csv(out / "history.csv", index=False)
opt.save_team(out / "v4_base.json", team)
Path("data/loh/my_team_v4_base.json").write_text(json.dumps(team, indent=1, ensure_ascii=False))
for b in team:
    log(f"FINAL {b['name']}: {b['stats']} cost {mock.stat_cost(b['stats'])}")
log("done", out)
