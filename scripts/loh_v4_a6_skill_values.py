"""LoH v4 step A6 (from v3 study 2): value of every skill vs the v4 mock field, others held at the v4 base.
  drop-one : each held non-evolved skill removed
  add-one  : each legal pool skill not held, added (if it shares a tier group with a held skill it replaces it,
             e.g. Groundwork -> Solid Preparation); ignores the 23-skill / ESP caps so the raw value is measured
  accel test: every legal front start-accel set (Ines {GW+TtL, SP, SP+TtL}; Kitasan {GW, SP}), 6,000 races
  optional  : Killer Tunes on Ines (disabled in generation; labelled 'optional')
  every variant: per-uma HP-out % and floor status, and whether it keeps the front start-accel rule
Values are paired team top-3 deltas and the uma's own top-3 delta; ESP of the skill given for pp per 100 ESP.
Usage: loh_v4_a6_skill_values.py N_SEEDS N_ACCEL"""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import buildgen as G, catalog as C, esp, mock, opt

N, NA = int(sys.argv[1]), int(sys.argv[2])
team = json.loads(Path("data/loh/my_team_v4_base.json").read_text())
out = opt.run_dir("v4-a6-skill-values")
V4_NEW = {"Downhill Speedster", "Racing Spirit: Wit", "Racing Spirit: Speed", "Full Throttle", "Keep Going!"}
opt.save_team(out / "base_team.json", team)
v, meta = {"base": team}, {}


def put(name, i, skills, kind, skill, esp_delta):
    t = copy.deepcopy(team); t[i]["skills"] = skills
    v[name] = t
    meta[name] = {"uma": team[i]["name"], "slot": i, "test": kind, "skill": skill, "esp_delta": esp_delta,
                  "v4_new": skill in V4_NEW, "accel_rule_ok": G.front_accel_ok(team[i], skills)}


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
# optional: Killer Tunes on Ines (not in generation)
kt = "Killer Tunes"
put(f"Ines Fujin: +{kt} (optional)", 1, team[1]["skills"] + [kt], "optional", kt, esp.esp(C.resolve_skill(kt), True))
print(len(v) - 1, "variants", flush=True)

# accel test: legal start-accel sets on each front (separate seeds and size)
va, ma = {"base": team}, {}
ACC = set(G.GROUNDWORK_FAMILY) | {"Taking the Lead"}
for i, b in enumerate(team):
    for st in G.legal_accel_sets(b):
        if not st:
            continue
        sk = [x for x in b["skills"] if x not in ACC] + st
        if sorted(sk) == sorted(b["skills"]):
            continue
        t = copy.deepcopy(team); t[i]["skills"] = sk
        nm = f"{b['name']}: accel " + " + ".join(st)
        va[nm] = t
        ma[nm] = {"uma": b["name"], "slot": i, "set": " + ".join(st),
                  "esp_delta": G.build_esp(sk) - G.build_esp(b["skills"]), "accel_rule_ok": G.front_accel_ok(b, sk)}

t0 = time.time()
df = mock.evaluate(v, list(range(104_000_000, 104_000_000 + N)))
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
                 "pp_per_100esp": 100 * r.d_top3 / m["esp_delta"] if m["esp_delta"] else None,
                 "hp_own%": r[f"hp{m['slot']}%"], "hp_status": mock.hp_status(df[df.variant == r.variant])})
res = pd.DataFrame(rows).sort_values(["uma", "test", "d_team_top3"], ascending=[True, True, False])
res.to_csv(out / "skill_values.csv", index=False)
pd.set_option("display.width", 250)
print(res.drop(columns=["variant", "slot"]).round(2).to_string())
b = s[s.variant == "base"].iloc[0]
print(f"base: team top3 {b.top3:.2f}, HP-out % {b['hp0%']:.2f} {b['hp1%']:.2f} {b['hp2%']:.2f}")

# accel test
dfa = mock.evaluate(va, list(range(104_500_000, 104_500_000 + NA)))
dfa.to_csv(out / "accel_races.csv.gz", index=False)
sa = mock.summarize(dfa)
base_ind_a = {k: 100 * (dfa[dfa.variant == "base"][f"p{k}"] <= 3).mean() for k in range(3)}
arows = []
for _, r in sa.iterrows():
    if r.variant == "base":
        continue
    m = ma[r.variant]
    arows.append({"variant": r.variant, **m, "d_team_top3": r.d_top3, "lo": r.d_top3_lo, "hi": r.d_top3_hi,
                  "d_points": r.d_points, "d_ind_top3": r[f"ind{m['slot']}"] - base_ind_a[m["slot"]],
                  "hp_own%": r[f"hp{m['slot']}%"], "hp_status": mock.hp_status(dfa[dfa.variant == r.variant])})
acc = pd.DataFrame(arows)
acc.to_csv(out / "accel_test.csv", index=False)
print(acc.drop(columns=["variant", "slot"]).round(2).to_string())
print(f"{len(df) + len(dfa)} races {time.time() - t0:.0f}s\ndone {out}")
