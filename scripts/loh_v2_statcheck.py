"""Joint check of stage-2 stat winners on fresh seeds. Usage: loh_v2_statcheck.py TEAM.json N"""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from umasim import opt
team = json.loads(Path(sys.argv[1]).read_text()); n = int(sys.argv[2])
NEW = {"Kitasan Black": [1500, 1000, 1250, 1150, 1200], "Ines Fujin": [1500, 1000, 1225, 1175, 1200]}
def with_(names):
    t = copy.deepcopy(team)
    for b in t:
        if b["name"] in names: b["stats"] = NEW[b["name"]]
    return t
v = {"base": team, "kita_stats": with_(["Kitasan Black"]), "ines_stats": with_(["Ines Fujin"]), "both": with_(NEW)}
df = opt.evaluate(v, list(range(30_000_000, 30_000_000 + n)))
s = opt.summarize(df); print(s.round(3).to_string())
out = opt.run_dir("v2-statcheck"); s.to_csv(out / "summary.csv", index=False); opt.save_team(out / "both_team.json", v["both"])
print("done", out)
