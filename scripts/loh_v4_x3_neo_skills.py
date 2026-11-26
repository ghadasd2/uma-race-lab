"""v4 extra X3: niche skill tests on Neo Universe (v4 champion, others unchanged).
Skills: Condor's Fury (inherited, 910141), Break the Mold (202522, condition fixed from the in-game page via
data/loh/skill_overrides.json), Racing Spirit: Power (210111), Latch On (202472), Pedal to the Metal (202452).
Variants: base; drop Slick Surge (Neo's weakest held skill in A6); each skill added on top (cap/ESP ignored) and
swapped in for Slick Surge. Paired on the same seeds (197M). Per race: team top-3, points, Neo place, HP-out per
uma, and whether / where the tested skill fired for Neo.
Usage: loh_v4_x3_neo_skills.py N [RUN_DIR_TO_RESUME] [--skills JSON] [--drop "A;B"] [--tag NAME]
  --skills  {"name": "skill id", ...} to test instead of the X3 set (each added on top and swapped for Slick Surge)
  --drop    held skills of Neo to remove (value of holding them), separated by ';'
  --tag     run-folder tag (default v4-x3-neo-skills)
The skill set is written to RUN_DIR/skills.json for the analysis script."""
import copy, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import buildgen as G, catalog as C, engine, esp, loh, mock, opt

args = sys.argv[1:]
def opt_arg(flag, default=None):
    if flag in args:
        k = args.index(flag); v = args[k + 1]; del args[k:k + 2]; return v
    return default
SKILLS_ARG, DROP_ARG, TAG = opt_arg("--skills"), opt_arg("--drop", ""), opt_arg("--tag", "v4-x3-neo-skills")
N = int(args[0])
out = Path(args[1]) if len(args) > 1 else opt.run_dir(TAG)
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()

NEO, SWAP_OUT = 2, "Slick Surge"
SKILLS = {"Condor's Fury (inherited)": "910141", "Break the Mold": "202522", "Racing Spirit: Power": "210111",
          "Latch On": "202472", "Pedal to the Metal": "202452"}
if SKILLS_ARG:
    SKILLS = json.loads(SKILLS_ARG)
DROPS = [x for x in DROP_ARG.split(";") if x]
(out / "skills.json").write_text(json.dumps({"skills": SKILLS, "drops": DROPS}, ensure_ascii=False, indent=1) + "\n")
champ = json.loads(Path("data/loh/my_team_v4_champion.json").read_text())
base_sk = champ[NEO]["skills"]
def team(skills):
    t = copy.deepcopy(champ); t[NEO]["skills"] = skills; return t
# with --drop, the base variant records where the first dropped (held) skill fires
V = {"base": (team(list(base_sk)), C.resolve_skill(DROPS[0]) if DROPS else None),
     f"drop {SWAP_OUT}": (team([s for s in base_sk if s != SWAP_OUT]), None)}
for d in DROPS:
    assert d in base_sk, d
    V[f"drop {d}"] = (team([s for s in base_sk if s != d]), None)
for name, sid in SKILLS.items():
    V[f"add {name}"] = (team(base_sk + [sid]), sid)
    V[f"swap {name}"] = (team([sid if s == SWAP_OUT else s for s in base_sk]), sid)
T = C.skill_table()
for name, sid in SKILLS.items():
    a = T[sid]["alternatives"][0]
    log(f"{name} {sid}: {esp.kind(sid)} {esp.esp(sid, True)} SP, wit check {bool(T[sid]['wisdomCheck'])}, "
        f"{a['baseDuration'] / 1e4 * 2.4:.2f} s at 2400 m, effects {[(f['type'], f['modifier'] / 1e4) for f in a['effects']]}, "
        f"condition {a['condition']}")
log(f"Neo ESP base {G.build_esp(base_sk)}; {SWAP_OUT} {esp.esp(C.resolve_skill(SWAP_OUT), True)} SP")

seeds = list(range(197_000_000, 197_000_000 + N))
csv = out / "races.csv.gz"
done = set(pd.read_csv(csv).variant.unique()) if csv.exists() else set()
t0 = time.time()
for var, (tm, sid) in V.items():
    if var in done:
        continue
    mm = mock.MockMatchup(tm); rows = []
    for k in range(0, N, 1000):
        part = seeds[k:k + 1000]; reqs = [mm.request(s) for s in part]
        for s, q, rp in zip(part, reqs, engine.run_requests(reqs)):
            if "error" in rp:
                raise engine.EngineError(rp["error"])
            res = rp["results"]; pl = [res[i]["finishOrder"] + 1 for i in range(3)]
            ev = [e for e in rp.get("skillEvents", []) if e["horseIndex"] == NEO and sid and str(e["skillId"]) == sid]
            gi = q["horses"][NEO]["gateIndex"]
            pos = [e["pos"] for e in rp.get("skillPosLog", []) if e["horseIndex"] == gi and sid and str(e["skillId"]) == sid]
            rows.append({"variant": var, "seed": s, "p0": pl[0], "p1": pl[1], "p2": pl[2],
                         "team_top3": 100 * sum(p <= 3 for p in pl) / 3, "points": sum(loh.points(p) for p in pl),
                         **{f"hp{i}": bool(res[i].get("hpEmptyOnRace")) for i in range(3)},
                         "fired": bool(ev), "fire_t": ev[0]["t"] if ev else None, "fire_pos": pos[0] if pos else None,
                         "gate": gi + 1})
    pd.DataFrame(rows).to_csv(csv, mode="a", header=not csv.exists(), index=False)
    log(f"{var}: {N} races {time.time() - t0:.0f}s")
log("done", out)
