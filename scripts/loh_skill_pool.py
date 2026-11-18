"""Build the realistic Front/Late skill pool for Tokyo 2400 from the CN/JP builds (+ user extras),
with ESP costs, sources and stage-1 sim values. Writes data/loh/skill_pool.{json,csv} and prints ESP stats."""
import collections, glob, json, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import catalog as C, esp, opt

L = Path("data/loh")
cn = json.loads((L / "cn_team.json").read_text()); jp = json.loads((L / "jp_team.json").read_text())
K, I, N = cn["team"]; B = cn["reference"][0]; JK, JB = jp["team"][0], jp["team"][1]
VODKA = ["Red Shift/LP1211-M", "Moving Past, and Beyond", "Standard Distance ○", "Spring Runner ○", "Straightaway Adept",
         "In Body and Mind", "Medium Straightaways ◎", "Medium Corners ○", "Late Surger Straightaways ○", "Late Surger Corners ◎"]
EXTRAS = ["Racing Spirit: Stamina", "Mad Dash", "In Body and Mind", "Firm Resolve", "Killer Tunes"]
LOCKED = {"Introducing the Victor!": "Kitasan", "Leap Ahead to the Future": "Kitasan", "Perfect ♪ Order Up!": "Ines",
          "Slick Serving": "Ines", "Beyond the Stars with You": "Neo", "Cross the Sea of Stars": "Neo"}

builds = [("CN Kitasan", K), ("CN Ines", I), ("CN Bourbon", B), ("JP Bourbon", JB), ("CN Neo", N)]
src = collections.defaultdict(set)
for tag, u in builds:
    for s in u["skills"]: src[s].add(tag)
for s in VODKA: src[s].add("JP Vodka (screenshot)")
for s in EXTRAS: src[s].add("your extras")

print("ESP per build (listed = base costs, ◎ incl. ○, evolved = base gold; full = also white under each gold):")
rows = []
for tag, u in builds:
    rows.append((tag, u["strategy"], len(u["skills"]) + 1, esp.build_esp(u["skills"], False), esp.build_esp(u["skills"], True)))
    print(f"  {tag:11} {u['strategy']:12} skills={rows[-1][2]}  listed={rows[-1][3]}  full={rows[-1][4]}")
fr = [r for r in rows if r[1] == "Front Runner"]
print(f"  FRONT mean listed={st.mean(r[3] for r in fr):.0f} (range {min(r[3] for r in fr)}-{max(r[3] for r in fr)}), "
      f"full={st.mean(r[4] for r in fr):.0f} (range {min(r[4] for r in fr)}-{max(r[4] for r in fr)})")
print(f"  ALL   mean listed={st.mean(r[3] for r in rows):.0f}, full={st.mean(r[4] for r in rows):.0f}")

val = {}
runs = sorted(glob.glob("runs/*stage1-skills"))
if runs:
    dr = pd.read_csv(runs[-1] + "/drop_one.csv")
    for _, r in dr[dr.variant != "base"].iterrows():
        u, s = r.variant.split(": -"); val[(u, s)] = round(-r.d_top3, 1)
pool = []
for n, tags in src.items():
    i = C.resolve_skill(n); k = esp.kind(i)
    if k == "evolved" and n not in LOCKED:
        continue
    front, late = opt.can_fire(i, "Front Runner"), opt.can_fire(i, "Late Surger")
    if not (front or late):
        continue
    pool.append({"skill": n, "id": i, "type": k, "inherited": k == "inherited", "locked_to": LOCKED.get(n),
                 "front": front, "late": late, "cost": esp.cost(i), "esp_listed": esp.esp(i, False), "esp_full": esp.esp(i, True),
                 "verified_legacy": C.is_approximated(i), "used_by": sorted(tags),
                 "sim_value_pp": {u: val[(u, n)] for u in ["Kitasan Black", "Ines Fujin", "Neo Universe"] if (u, n) in val}})
pool.sort(key=lambda p: (p["type"], p["skill"]))
(L / "skill_pool.json").write_text(json.dumps(pool, indent=1, ensure_ascii=False))
pd.DataFrame(pool).to_csv(L / "skill_pool.csv", index=False)
print(len(pool), "skills in pool")
