"""LoH v3 study 2: value of every skill vs random mock teams (others held at base).
  drop-one : each held non-evolved skill removed
  add-one  : each legal pool skill not held, added (if it shares a tier group with a held skill it replaces it,
             e.g. Groundwork -> Solid Preparation); ignores the 23-skill / ESP caps so the raw value is measured
  front test: Ines without Taking the Lead / Solid Preparation / both, Solid Preparation -> Groundwork
Values are paired team top-3 deltas and the uma's own top-3 delta; ESP of the skill given for pp per 100 ESP.
Usage: loh_v3_skill_values.py N_SEEDS [TEAM.json]"""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import buildgen as G, catalog as C, esp, mock, opt

N = int(sys.argv[1])
team = json.loads(Path(sys.argv[2] if len(sys.argv) > 2 else "data/loh/my_team_v3_base.json").read_text())
out = opt.run_dir("v3-skill-values")
opt.save_team(out / "base_team.json", team)
v, meta = {"base": team}, {}


def put(name, i, skills, kind, skill, esp_delta):
    t = copy.deepcopy(team); t[i]["skills"] = skills
    v[name] = t
    meta[name] = {"uma": team[i]["name"], "slot": i, "test": kind, "skill": skill, "esp_delta": esp_delta}


for i, b in enumerate(team):
    fixed = set(G.EVOLVED.get(b["name"], []))
    held = list(b["skills"])
    for s in held:
        if s not in fixed:
            put(f"{b['name']}: -{s}", i, [x for x in held if x != s], "drop", s, -esp.esp(C.resolve_skill(s), True))
    groups = {G._group(s): s for s in held}
    for p in G.candidates(b):
        s = p["skill"]
        if s in held:
            continue
        g = G._group(s)
        rep = groups.get(g)
        if rep in fixed:
            continue
        new = [x for x in held if x != rep] + [s]
        d = p["esp_full"] - (esp.esp(C.resolve_skill(rep), True) if rep else 0)
        put(f"{b['name']}: +{s}" + (f" (for {rep})" if rep else ""), i, new, "add" if not rep else "swap", s, d)
# front test on Ines
i = 1; held = team[i]["skills"]
put("Ines Fujin: -Taking the Lead -Solid Preparation", i, [x for x in held if x not in ("Taking the Lead", "Solid Preparation")],
    "front_test", "TtL+SP", -sum(esp.esp(C.resolve_skill(x), True) for x in ("Taking the Lead", "Solid Preparation")))
put("Ines Fujin: Groundwork for Solid Preparation", i, [x for x in held if x != "Solid Preparation"] + ["Groundwork"],
    "front_test", "SP->Groundwork", esp.esp(C.resolve_skill("Groundwork"), True) - esp.esp(C.resolve_skill("Solid Preparation"), True))
print(len(v) - 1, "variants", flush=True)

t0 = time.time()
df = mock.evaluate(v, list(range(52_000_000, 52_000_000 + N)))
df.to_csv(out / "races.csv.gz", index=False)
s = mock.summarize(df)
base_ind = {k: 100 * (df[df.variant == "base"][f"p{k}"] <= 3).mean() for k in range(3)}
rows = []
for _, r in s.iterrows():
    if r.variant == "base":
        continue
    m = meta[r.variant]
    rows.append({"variant": r.variant, **m, "d_team_top3": r.d_top3, "lo": r.d_top3_lo, "hi": r.d_top3_hi,
                 "d_points": r.d_points, "d_ind_top3": r[f"ind{m['slot']}"] - base_ind[m["slot"]],
                 "pp_per_100esp": 100 * r.d_top3 / m["esp_delta"] if m["esp_delta"] else None})
res = pd.DataFrame(rows).sort_values(["uma", "test", "d_team_top3"], ascending=[True, True, False])
res.to_csv(out / "skill_values.csv", index=False)
pd.set_option("display.width", 250)
print(res.drop(columns=["variant", "slot"]).round(2).to_string())
print(f"{len(df)} races {time.time() - t0:.0f}s\ndone {out}")
