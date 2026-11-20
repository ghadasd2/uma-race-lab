"""Per-skill effect sizes (m/s, m/s^2, HP %, seconds at 2400 m) and measured value per 100 SP (v4).
For swaps, SP is the cost difference and pp per 100 SP uses it. Adds own HP-out %, floor status and the v4-new flag.
Usage: loh_v4_skill_table.py SKILL_VALUES.csv OUT.csv"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import catalog as C, esp

DIST = 2.4
NAMES = {27: "target speed", 21: "current speed", 22: "current speed", 31: "accel", 9: "HP recovery", 28: "lane speed",
         1: "speed stat", 2: "stamina stat", 3: "power stat", 4: "guts stat", 5: "wit stat"}
sv = pd.read_csv(sys.argv[1])
rows = []
for _, r in sv[sv.test.isin(["drop", "add", "swap", "optional"])].iterrows():
    sid = C.resolve_skill(r.skill); a = C.skill_table()[sid]["alternatives"][0]
    dur = a["baseDuration"] / 10000 * DIST if a["baseDuration"] > 0 else None
    eff, ms, acc, hp = [], 0.0, 0.0, 0.0
    for e in a["effects"]:
        v = e["modifier"] / 10000; tg = e.get("target", 1); t = e["type"]
        if t in (1, 2, 3, 4, 5):
            eff.append(f"+{int(v)} {NAMES[t].split()[0].capitalize()}"); continue
        if t in (21, 22) and tg != 1:
            eff.append(f"{v:+g} m/s to others"); continue
        if t in (27, 21, 22):
            ms += v; eff.append(f"{v:+g} m/s {NAMES[t]}")
        elif t == 31:
            acc += v; eff.append(f"{v:+g} m/s² accel")
        elif t == 9:
            hp += v if tg == 1 else 0; eff.append(f"{100 * v:+.1f}% HP")
        elif t == 28:
            eff.append(f"{v:+g} lane speed")
        elif t == 29:
            eff.append("lower rushing chance")
        elif t == 8:
            eff.append("wider vision")
        elif t == 35:
            eff.append("lane change")
        else:
            eff.append(f"type{t} {v:+g}")
    drop = r.test == "drop"
    sp = abs(r.esp_delta) if drop else (r.esp_delta if r.test == "swap" else esp.esp(sid, True))
    pp = -r.d_team_top3 if drop else r.d_team_top3
    rows.append({"uma": r.uma.split()[0], "test": r.test, "variant": r.variant, "skill": r.skill, "kind": esp.kind(sid),
                 "v4_new": r.get("v4_new", False), "sp": sp, "effect": ", ".join(eff) + (f", {dur:.1f} s" if dur else ""),
                 "ms": ms or None, "ms_per_100sp": round(100 * ms / esp.esp(sid, True), 3) if ms else None,
                 "ms_x_s": round(ms * dur, 2) if ms and dur else None, "accel": acc or None,
                 "hp_pct": round(100 * hp, 1) if hp else None,
                 "pp": round(pp, 2), "lo": round(-r.hi if drop else r.lo, 2), "hi": round(-r.lo if drop else r.hi, 2),
                 "ind_pp": round(-r.d_ind_top3 if drop else r.d_ind_top3, 2),
                 "pp_per_100sp": round(100 * pp / sp, 2) if sp else None,
                 "hp_own%": r.get("hp_own%"), "hp_status": r.get("hp_status"), "accel_rule_ok": r.get("accel_rule_ok")})
df = pd.DataFrame(rows)
df.to_csv(sys.argv[2], index=False)
pd.set_option("display.width", 300); pd.set_option("display.max_colwidth", 60)
print(df.drop(columns=["variant"]).to_string())
