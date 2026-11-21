"""One example race for X1: Neo with the real Ignited Spirit WIT vs the no-effect clone on the same seed.
Picks (unless SEED is given) a frames-sample race where the skill fired, Neo finished top 3 with it and outside the
top 3 without it, choosing the largest metres gained by the end of the 9.6 s window. Prints a timeline.
Usage: loh_v4_x1_example.py RUN_DIR [SEED]"""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
from umasim import catalog as C, engine, mock

run = Path(sys.argv[1])
F = pd.read_csv(run / "neo_frames_features.csv.gz", keep_default_na=False, na_values=[""])
full = F[F.variant == "full"].set_index("seed"); none = F[F.variant == "none"].set_index("seed")
if len(sys.argv) > 2:
    seed = int(sys.argv[2])
else:
    c = full[full.fired.astype(bool) & (full.place <= 3) & (none.place > 3)].copy()
    c["gain"] = c.pos_end_win - none.loc[c.index].pos_end_win
    seed = int(c.gain.idxmax())

T = C.skill_table(); base = T["210052"]
e = copy.deepcopy(base); e["alternatives"][0]["effects"] = [dict(base["alternatives"][0]["effects"][1], modifier=0)]
T["299002"] = e
champ = json.loads(Path("data/loh/my_team_v4_champion.json").read_text())
def team(sid):
    t = copy.deepcopy(champ); sk = t[2]["skills"]; sk[sk.index("Ignited Spirit WIT")] = sid; return t
reps = {}
for name, sid in (("with", "210052"), ("without", "299002")):
    m = mock.MockMatchup(team(sid)); q = m.request(seed); q["omitFrames"] = False; q["retainAllFrames"] = True
    reps[name] = (engine.run_requests([q], 1)[0], q, list(m.names))
rep, q, names = reps["with"]
ev = [x for x in rep["skillEvents"] if x["horseIndex"] == 2 and x["skillId"] == 210052][0]
ta, du = ev["t"], ev["duration"]
out = [f"seed {seed}: Neo gate {q['horses'][2]['gateIndex'] + 1}, mood {q['horses'][2]['mood']}, "
       f"ground {q['groundCondition']}, Ignited Spirit WIT fires at t = {ta:.2f} s for {du:.1f} s"]
def at(rp, tt):
    fr = rp["frames"]; k = min(range(len(fr)), key=lambda j: abs(fr[j]["t"] - tt)); return fr[k]
hdr = f"{'t (s)':>6} | {'with: pos m':>11} {'lane':>5} {'speed':>6} {'blocked by':>12} | {'without: pos m':>14} {'lane':>5} {'speed':>6} {'blocked by':>12} | {'ahead m':>7}"
out += ["", hdr, "-" * len(hdr)]
for dt in np.arange(-1, du + 6.01, 1.0):
    tt = ta + dt; row = []
    for nm in ("with", "without"):
        h = at(reps[nm][0], tt)["horses"]; me = h[2]; b = me["blockFrontHorseIndex"]
        row.append((me["pos"], me["lane"] * 18, me["speed"], reps[nm][2][b] if b >= 0 else "-"))
    (p1, l1, s1, b1), (p2, l2, s2, b2) = row
    out.append(f"{tt:6.1f} | {p1:11.1f} {l1:5.2f} {s1:6.2f} {b1:>12} | {p2:14.1f} {l2:5.2f} {s2:6.2f} {b2:>12} | {p1 - p2:+7.2f}")
out.append("(lane in horse widths from the inside rail; 'blocked by' = runner directly in front capping her speed)")
out.append("")
for nm in ("with", "without"):
    rp = reps[nm][0]; fr = rp["frames"]
    pos = np.array([f["horses"][2]["pos"] for f in fr])
    s = []
    for x in (400, 1000, 1600, 2000):
        k = int(np.searchsorted(pos, x)); allp = [h["pos"] for h in fr[k]["horses"]]
        s.append(f"{x} m: {sum(p > pos[k] for p in allp) + 1}th")
    r = rp["results"][2]
    s.append(f"finish {r['finishOrder'] + 1} ({r['finishTimeRaw']:.2f} s)")
    out.append(f"{nm:>8}: " + ", ".join(s))
txt = "\n".join(out); print(txt)
(run / f"example_{seed}.txt").write_text(txt + "\n")
