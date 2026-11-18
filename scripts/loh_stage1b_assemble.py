"""Assemble skill-optimized team from a stage-1 run dir, then verify vs baseline.
Usage: loh_stage1b_assemble.py RUN_DIR [MAX_NORMAL_SKILLS=22] [VERIFY_N_PER_WORLD=3000]
Value of a held skill = loss when dropped; value of a candidate = gain when added (final halving round).
Greedy: add candidates with positive, credible gains (swapping same-group skills), then trim the
lowest-value skills down to the cap (unique not counted in MAX_NORMAL_SKILLS)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import loh, opt, catalog as C

d = Path(sys.argv[1]); cap = int(sys.argv[2]) if len(sys.argv) > 2 else 22
nv = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
mode = sys.argv[4] if len(sys.argv) > 4 else "global"   # global: skip legacy-only candidates; all: allow them
suffix = "" if mode == "global" else "_" + mode
base = json.loads((d / "baseline_team.json").read_text())
drop = pd.read_csv(d / "drop_one.csv")
rounds = sorted(d.glob("round*.csv"))
add = pd.read_csv(rounds[-1])
report = {}
team = [dict(b, skills=list(b["skills"])) for b in base]
for i, b in enumerate(base):
    nm = b["name"]
    val = {}
    for _, r in drop[drop.variant.str.startswith(nm + ": -")].iterrows():
        val[r.variant.split(": -", 1)[1]] = -r.d_top3
    cands = []
    for _, r in add[add.variant.str.startswith(nm + ": +")].iterrows():
        sk = r.variant.split(": +", 1)[1]
        if mode == "global" and C.is_approximated(C.resolve_skill(sk)):
            continue
        if r.d_top3 > 0 and r.d_top3_lo > -0.25:      # positive and not clearly noise
            cands.append((r.d_top3, sk, r.d_top3_lo))
    cands.sort(reverse=True)
    b2 = team[i]
    added = []
    for g, sk, lo in cands:
        before = set(b2["skills"])
        b2 = opt.add_skill(b2, sk)
        swapped = before - set(b2["skills"])
        val[sk] = g + sum(val.get(x, 0) for x in swapped)
        added.append({"skill": sk, "gain_pp": round(g, 2), "ci_lo": round(lo, 2), "replaced": sorted(swapped)})
    trimmed = []
    while len(b2["skills"]) > cap:
        worst = min(b2["skills"], key=lambda s: val.get(s, 0))
        trimmed.append({"skill": worst, "value_pp": round(val.get(worst, 0), 2)})
        b2 = opt.drop_skill(b2, worst)
    team[i] = b2
    report[nm] = {"added": added, "trimmed": trimmed,
                  "kit_values_pp": dict(sorted(((k, round(v, 2)) for k, v in val.items()), key=lambda kv: -kv[1])),
                  "final_skills": b2["skills"], "count_incl_unique": len(b2["skills"]) + 1}
(d / f"assembled_team{suffix}.json").write_text(json.dumps(team, indent=1, ensure_ascii=False))
(d / f"assembly_report{suffix}.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
print(json.dumps({k: {"added": [a["skill"] for a in v["added"]], "trimmed": [t["skill"] for t in v["trimmed"]],
                      "count": v["count_incl_unique"]} for k, v in report.items()}, indent=1, ensure_ascii=False))
df = opt.evaluate({"base": base, "assembled": team}, list(range(5_000_000, 5_000_000 + nv)))
s = opt.summarize(df); s.to_csv(d / "assembled_check.csv", index=False)
print(s.round(3).to_string())
