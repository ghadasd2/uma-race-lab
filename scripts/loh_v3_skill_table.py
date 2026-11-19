"""Per-skill effect sizes (m/s, m/s^2, HP%, seconds at 2400 m) and measured value per 100 SP, from study 2."""
import glob, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import catalog as C, esp
DIST = 2.4
NAMES = {27: "target speed", 21: "current speed", 22: "current speed", 31: "accel", 9: "HP recovery", 28: "lane speed",
         1: "speed stat", 2: "stamina stat", 3: "power stat", 4: "guts stat", 5: "wit stat", 10: "start delay x", 14: "start delay"}
sv = pd.read_csv(sorted(glob.glob("runs/*v3-skill-values"))[-1] + "/skill_values.csv")
rows = []
for r in sv[sv.test != "front_test"].itertuples():
    sid = C.resolve_skill(r.skill); t = C.skill_table()[sid]
    a = t["alternatives"][0]; dur = a["baseDuration"] / 10000 * DIST if a["baseDuration"] > 0 else None
    eff = []; ms = acc = hp = 0.0
    for e in a["effects"]:
        v = e["modifier"] / 10000; tg = e.get("target", 1)
        nm = NAMES.get(e["type"], f"type{e['type']}")
        if e["type"] in (21, 22) and tg != 1:
            nm = "debuff (others' speed)"
        elif e["type"] in (27, 21, 22):
            ms += v
        if e["type"] == 31: acc += v
        if e["type"] == 9: hp += v * (1 if tg == 1 else 0)
        eff.append(f"{nm} {v:+.3g}" if e["type"] not in (1, 2, 3, 4, 5) else f"{nm} {e['modifier']:+d}")
    sp = abs(r.esp_delta) if r.test == "drop" else esp.esp(sid, True)
    rows.append({"uma": r.uma.split()[0], "test": r.test, "skill": r.skill, "kind": esp.kind(sid), "sp": sp,
                 "effect": "; ".join(eff), "dur_s": round(dur, 1) if dur else None,
                 "ms": ms or None, "ms_per_100sp": round(100 * ms / sp, 3) if ms and sp else None,
                 "ms_x_s": round(ms * dur, 2) if ms and dur else None,
                 "accel": acc or None, "hp_pct": round(100 * hp, 1) if hp else None,
                 "pp": round(-r.d_team_top3 if r.test == "drop" else r.d_team_top3, 2),
                 "lo": round(-r.hi if r.test == "drop" else r.lo, 2), "hi": round(-r.lo if r.test == "drop" else r.hi, 2),
                 "ind_pp": round(-r.d_ind_top3 if r.test == "drop" else r.d_ind_top3, 2),
                 "pp_per_100sp": round(100 * (-r.d_team_top3 if r.test == "drop" else r.d_team_top3) / sp, 2) if sp else None})
df = pd.DataFrame(rows)
df.to_csv("data/loh/results/v3_skill_table.csv", index=False)
pd.set_option("display.width", 300); pd.set_option("display.max_colwidth", 60)
print(df.to_string())
