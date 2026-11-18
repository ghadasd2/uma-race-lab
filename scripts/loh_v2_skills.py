"""LoH v2 skill optimization with the realistic pool + ESP budget.

Phase A  random screen: N random legal builds per uma (others at anchors), paired successive halving
         vs the anchor team in both worlds. Every build's own 1st/2nd/3rd/top3 is recorded.
Mocks    builds whose individual top-3 sits in the 40-60th percentile (per uma) are saved as mock
         opponents, plus random Bourbon builds (in Ines' slot) scored the same way.
Phase B  local search: mutations (1-2 skill swaps) of each uma's best builds, halving again.
Output   runs/<stamp>-loh-v2-skills/: anchor_team.json, best_team.json, mocks.json, csvs, log.txt
Usage    loh_v2_skills.py [N_RANDOM=200] [N_MUT=30]
"""
import glob, json, random, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
from umasim import buildgen as G, loh, opt

N_RANDOM = int(sys.argv[1]) if len(sys.argv) > 1 else 200
N_MUT = int(sys.argv[2]) if len(sys.argv) > 2 else 30
out = opt.run_dir("v2-skills")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()

# anchors: CN builds made legal (ESP 4500-4600, pool only), low-value skills dropped first
val = {}
st1 = sorted(glob.glob(str(Path(__file__).resolve().parent.parent / "runs" / "*stage1-skills")))
if st1:
    dr = pd.read_csv(st1[-1] + "/drop_one.csv")
    for _, r in dr[dr.variant != "base"].iterrows():
        u, s = r.variant.split(": -"); val.setdefault(u, {})[s] = -r.d_top3
anchor = [G.anchor_build(u, val.get(u["name"])) for u in loh.my_baseline()]
opt.save_team(out / "anchor_team.json", anchor)
log("anchors:", [(b["name"], G.build_esp(b["skills"]), len(b["skills"]) + 1) for b in anchor])
NAMES = [b["name"] for b in anchor]


def individual(df, slot_of):
    """Per variant: individual placings of the varied uma (slot given per variant)."""
    rows = []
    for v, g in df.groupby("variant"):
        slot = slot_of.get(v)
        if slot is None:
            continue
        p = g[f"p{slot}"]
        rows.append({"variant": v, "ind_top3": 100 * (p <= 3).mean(), "ind_p1": 100 * (p == 1).mean(),
                     "ind_p2": 100 * (p == 2).mean(), "ind_p3": 100 * (p == 3).mean(), "ind_n": len(p)})
    return pd.DataFrame(rows)


def screen(variants, slot_of, tag, n0, keep, rounds, seed_base):
    alive, n, hist, first_df = dict(variants), n0, [], None
    for r in range(rounds):
        seeds = list(range(seed_base + r * 1_000_000, seed_base + r * 1_000_000 + n))
        t0 = time.time()
        df = opt.evaluate(alive, seeds)
        if r == 0:
            first_df = df
        summ = opt.summarize(df).merge(individual(df, slot_of), on="variant", how="left")
        summ["round"] = r; hist.append(summ)
        summ.to_csv(out / f"{tag}_round{r}.csv", index=False)
        log(f"{tag} round {r}: {len(alive)} variants x {n} seeds x 2 worlds in {time.time() - t0:.0f}s")
        if r == rounds - 1:
            break
        others = summ[summ.variant != "base"]
        k = max(3, int(np.ceil(len(others) * keep)))
        alive = {v: alive[v] for v in ["base"] + list(others.head(k).variant)}
        n *= 3
    return pd.concat(hist, ignore_index=True), first_df


rng = random.Random(20261118)
# ---------------- Phase A
variants, slot_of, builds = {"base": anchor}, {}, {}
for i, u in enumerate(anchor):
    seen = set()
    while len([k for k in builds if k.startswith(u["name"])]) < N_RANDOM:
        b = G.random_build(u, rng)
        key = tuple(sorted(b["skills"]))
        if key in seen:
            continue
        seen.add(key)
        name = f"{u['name']} #R{len(seen)}"
        t = [dict(x) for x in anchor]; t[i] = b
        variants[name] = t; slot_of[name] = i; builds[name] = b
# Bourbon mocks in Ines' slot (scored individually; not candidates for my team)
bourbon_rec = json.loads((loh.DATA / "cn_team.json").read_text())["reference"][0]
bourbon = loh._from_record(bourbon_rec, distance="S", style="A")
bourbon["stats"] = loh.project_stats(bourbon["stats"], *loh.stat_box())
for k in range(max(40, N_RANDOM // 3)):
    b = G.random_build(bourbon, rng)
    name = f"Mihono Bourbon #R{k + 1}"
    t = [dict(x) for x in anchor]; t[1] = b
    variants[name] = t; slot_of[name] = 1; builds[name] = b
json.dump(builds, open(out / "phaseA_builds.json", "w"), ensure_ascii=False)
log(f"phase A: {len(variants) - 1} variants ({N_RANDOM} per uma + Bourbon mocks)")

# round 0 on everything (gives percentiles), then halving only among my umas' builds
histA, df0 = screen(variants, slot_of, "phaseA", 150, 1.0, 1, 10_000_000)
ind0 = individual(df0, slot_of)
mocks = {}
for nm in NAMES + ["Mihono Bourbon"]:
    x = ind0[ind0.variant.str.startswith(nm + " #")]
    lo, hi = np.percentile(x.ind_top3, [40, 60])
    sel = x[(x.ind_top3 >= lo) & (x.ind_top3 <= hi)]
    mocks[nm] = [{"variant": v, "ind_top3_round0": round(t, 1), "build": builds[v]} for v, t in zip(sel.variant, sel.ind_top3)]
    log(f"mocks {nm}: {len(mocks[nm])} builds with individual top3 in [{lo:.1f}, {hi:.1f}] (median of {len(x)})")
(out / "mocks.json").write_text(json.dumps(mocks, indent=1, ensure_ascii=False))

mine = {k: v for k, v in variants.items() if k == "base" or not k.startswith("Mihono Bourbon")}
r0 = histA[histA.variant.isin(mine)]
keep0 = ["base"] + list(r0[r0.variant != "base"].head(max(3, int(len(r0) * 0.25))).variant)
histA2, _ = screen({k: mine[k] for k in keep0}, slot_of, "phaseA_halving", 450, 0.3, 2, 11_000_000)
last = histA2[histA2["round"] == histA2["round"].max()]
best_by_uma = {}
for i, nm in enumerate(NAMES):
    rows = last[last.variant.str.startswith(nm + " #")]
    best_by_uma[nm] = list(rows.head(3).variant)
    log(f"phase A best {nm}: " + "; ".join(f"{v} team+{d:.2f}pp ind_top3 {t:.1f}" for v, d, t in zip(rows.variant, rows.d_top3, rows.ind_top3)))

# new anchors = best phase-A build per uma (if it beat the anchor)
anchor2 = [dict(b) for b in anchor]
for i, nm in enumerate(NAMES):
    rows = last[last.variant.str.startswith(nm + " #")]
    if len(rows) and rows.iloc[0].d_top3 > 0:
        anchor2[i] = builds[rows.iloc[0].variant]
opt.save_team(out / "phaseA_team.json", anchor2)

# ---------------- Phase B: local search around each uma's top builds, others at anchor2
variants, slot_of2 = {"base": anchor2}, {}
for i, nm in enumerate(NAMES):
    parents = [builds[v] for v in best_by_uma[nm]] or [anchor2[i]]
    seen = set()
    for k in range(N_MUT * len(parents)):
        m = G.mutate(parents[k % len(parents)], rng)
        if not m:
            continue
        key = tuple(sorted(m["skills"]))
        if key in seen:
            continue
        seen.add(key)
        name = f"{nm} #M{len(seen)}"
        t = [dict(x) for x in anchor2]; t[i] = m
        variants[name] = t; slot_of2[name] = i; builds[name] = m
log(f"phase B: {len(variants) - 1} mutants")
histB, _ = screen(variants, slot_of2, "phaseB", 300, 0.3, 3, 12_000_000)
lastB = histB[histB["round"] == histB["round"].max()]
best = [dict(b) for b in anchor2]
for i, nm in enumerate(NAMES):
    rows = lastB[lastB.variant.str.startswith(nm + " #")]
    if len(rows) and rows.iloc[0].d_top3 > 0 and rows.iloc[0].d_top3_lo > 0:
        best[i] = builds[rows.iloc[0].variant]
        log(f"phase B improved {nm}: {rows.iloc[0].variant} +{rows.iloc[0].d_top3:.2f}pp [{rows.iloc[0].d_top3_lo:.2f},{rows.iloc[0].d_top3_hi:.2f}]")
    else:
        log(f"phase B: no credible improvement for {nm}")
json.dump(builds, open(out / "all_builds.json", "w"), ensure_ascii=False)
opt.save_team(out / "best_team.json", best)
for b in best:
    log(f"BEST {b['name']}: ESP {G.build_esp(b['skills'])}, {len(b['skills']) + 1} skills: {b['skills']}")
df = opt.evaluate({"base": anchor, "best": best}, list(range(13_000_000, 13_003_000)))
log(opt.summarize(df).round(3).to_string())
log("done", out)
