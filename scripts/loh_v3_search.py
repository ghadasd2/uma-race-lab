"""LoH v3 study 4: iterative build search (stats + skills, whole team) vs random mock teams.

Constraints per uma: stat box mock.MY_BOX, in-game cost <= mock.COST_BUDGET (points >1200 cost 2),
skills legal per buildgen.valid (pool only, ESP 4500-4600, <=23 incl. unique, <=3 inherited, tier groups).
Generation 0 = hypothesis candidates from studies 1-3; later generations = guided mutations of the champion:
  stat move : take 25/50 from one stat, spend the freed cost on another (box + budget respected)
  skill add : a pool skill (weighted by its study-2 add value) in, lowest-value held skills out until legal
  skill swap: buildgen.mutate (random legal 1-2 swap)
Each generation: paired successive halving on fresh seeds (n0 -> x3 -> x2); the champion is replaced only if
the winner beats it with the 95% CI lower bound > 0 on the final round.
Usage: loh_v3_search.py GENERATIONS CANDIDATES_PER_GEN N0"""
import copy, json, random, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import glob
import pandas as pd
from umasim import buildgen as G, mock, opt

GENS, M, N0 = (int(a) for a in sys.argv[1:4])
out = opt.run_dir("v3-search")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()
rng = random.Random(20261119)
STAT = ["spd", "sta", "pow", "guts", "wit"]

# study-2 values: value of holding a skill (drop loss) and of adding it
sv = pd.read_csv(sorted(glob.glob("runs/*v3-skill-values"))[-1] + "/skill_values.csv")
HOLD = {(r.uma, r.skill): -r.d_team_top3 for r in sv[sv.test == "drop"].itertuples()}
ADD = {(r.uma, r.skill): r.d_team_top3 for r in sv[sv.test.isin(["add", "swap"])].itertuples()}


def fill_budget(st):
    """Spend leftover cost on speed (then power) inside the box."""
    st = list(st)
    for k in (0, 2):
        while True:
            t = list(st); t[k] += 5
            if t[k] > mock.MY_BOX[k][1] or mock.stat_cost(t) > mock.COST_BUDGET:
                break
            st = t
    return st


def stat_ok(st):
    return mock.stat_cost(st) <= mock.COST_BUDGET and all(lo <= v <= hi for v, (lo, hi) in zip(st, mock.MY_BOX))


def stat_move(b):
    for _ in range(50):
        a, c = rng.sample(range(5), 2); step = rng.choice([25, 50])
        st = list(b["stats"]); st[a] -= step
        while True:
            t = list(st); t[c] += 5
            if t[c] > mock.MY_BOX[c][1] or mock.stat_cost(t) > mock.COST_BUDGET:
                break
            st = t
        if stat_ok(st) and st != b["stats"]:
            nb = copy.deepcopy(b); nb["stats"] = st
            return nb, f"{STAT[a]}-{step}->{STAT[c]}"
    return None, None


def add_skill(b, s):
    """Put s in; drop the lowest-hold-value non-locked skills until the build is legal (or give up)."""
    fixed = set(G.EVOLVED.get(b["name"], []))
    sk = [x for x in b["skills"] if G._group(x) != G._group(s)] + [s]
    for _ in range(6):
        ok, why = G.valid(b, sk)
        if ok:
            nb = copy.deepcopy(b); nb["skills"] = sk
            return nb
        if "ESP" in why and G.build_esp(sk) < G.esp_range()[0]:
            return None
        cands = [x for x in sk if x not in fixed and x != s]
        sk.remove(min(cands, key=lambda x: HOLD.get((b["name"], x), 0.0)))
    return None


def skill_add(b):
    pool = [p["skill"] for p in G.candidates(b) if p["skill"] not in b["skills"]]
    w = [max(0.05, ADD.get((b["name"], s), 0.0) + 0.3) for s in pool]
    for _ in range(20):
        s = rng.choices(pool, weights=w)[0]
        nb = add_skill(b, s)
        if nb:
            gone = sorted(set(b["skills"]) - set(nb["skills"]))
            return nb, f"+{s} -{'/'.join(gone)}"
    return None, None


def skill_swap(b):
    nb = G.mutate(b, rng)
    if not nb:
        return None, None
    return nb, f"+{'/'.join(sorted(set(nb['skills']) - set(b['skills'])))} -{'/'.join(sorted(set(b['skills']) - set(nb['skills'])))}"


def mutate_team(team):
    t = copy.deepcopy(team); desc = []
    for _ in range(rng.choice([1, 1, 2])):
        i = rng.randrange(3)
        f = rng.choices([stat_move, skill_add, skill_swap], weights=[0.45, 0.35, 0.2])[0]
        nb, d = f(t[i])
        if nb:
            t[i] = nb; desc.append(f"{t[i]['name'].split()[0]}: {d}")
    return t, "; ".join(desc)


def hypotheses(team):
    """Generation 0: changes suggested by studies 1-3."""
    H = {}
    def h(name, fn):
        t = copy.deepcopy(team)
        try:
            if fn(t) is not False:
                assert all(G.valid(b, b["skills"])[0] and stat_ok(b["stats"]) for b in t), name
                H[name] = t
        except (AssertionError, TypeError) as e:
            log("skip hypothesis", name, e)
    def sp_kita(t):
        nb = add_skill(t[0], "Solid Preparation"); t[0] = nb
    def neo_pow(t):
        t[2]["stats"] = fill_budget([t[2]["stats"][0], 1000, 1250, 1200, 1200])
    def fill(t):
        for b in t: b["stats"] = fill_budget(b["stats"])
    def kita_rs_md(t):
        b = add_skill(t[0], "Racing Spirit: Stamina"); b = add_skill(b, "Mad Dash"); t[0] = b
        b["stats"] = fill_budget([1380, 1200, 1200, 1200, 1200])
    def ines_md(t):
        t[1] = add_skill(t[1], "Mad Dash")
    def neo_rs(t):
        t[2] = add_skill(t[2], "Racing Spirit: Stamina"); t[2]["stats"] = fill_budget([t[2]["stats"][0], 1000, 1250, 1200, 1200])
    def hesitant(t, i):
        t[i] = add_skill(t[i], "Hesitant Front Runners")
    def restraint(t, i):
        t[i] = add_skill(t[i], "Restraint")
    def ines_gait(t):
        t[1] = add_skill(t[1], "Superb Gait")
    def neo_prof(t):
        t[2] = add_skill(t[2], "Professor of Curvature")
    def neo_ls_corners(t):
        t[2] = add_skill(t[2], "Late Surger Corners ◎")
    def low_sta_front(t, i):
        t[i]["stats"] = fill_budget([t[i]["stats"][0], 1000] + t[i]["stats"][2:])
    h("fill budget (speed)", fill)
    h("Kita Groundwork->Solid Prep", sp_kita)
    h("Kita +RS+MD @1200 sta", kita_rs_md)
    h("Ines +Mad Dash", ines_md)
    h("Ines +Superb Gait", ines_gait)
    h("Ines +Hesitant FR", lambda t: hesitant(t, 1))
    h("Kita +Hesitant FR", lambda t: hesitant(t, 0))
    h("Kita +Restraint", lambda t: restraint(t, 0))
    h("Ines +Restraint", lambda t: restraint(t, 1))
    h("Neo sta->pow 1000/1250", neo_pow)
    h("Neo +RS sta 1000 pow 1250", neo_rs)
    h("Neo +Professor of Curvature", neo_prof)
    h("Neo +Late Surger Corners ◎", neo_ls_corners)
    h("Kita sta 1000", lambda t: low_sta_front(t, 0))
    h("Ines sta 1000", lambda t: low_sta_front(t, 1))
    return H


def generation(champ, cands, g):
    alive = {"base": champ, **cands}
    n, seed0 = N0, 60_000_000 + g * 1_000_000
    for r, keep in enumerate([8, 3, None]):
        seeds = list(range(seed0 + r * 100_000, seed0 + r * 100_000 + n))
        t0 = time.time()
        df = mock.evaluate(alive, seeds)
        s = mock.summarize(df)
        s.to_csv(out / f"gen{g:02d}_round{r}.csv", index=False)
        log(f"gen {g} round {r}: {len(alive)} x {n} = {len(df)} races {time.time() - t0:.0f}s; base {s[s.variant == 'base'].top3.iloc[0]:.2f}")
        others = s[s.variant != "base"]
        log("   " + " | ".join(f"{v} {d:+.2f}[{lo:+.2f}]" for v, d, lo in zip(others.variant.head(6), others.d_top3.head(6), others.d_top3_lo.head(6))))
        if keep is None:
            return others.iloc[0]
        alive = {v: alive[v] for v in ["base"] + list(others.head(keep).variant)}
        n *= 3 if r == 0 else 2


champ = json.loads(Path("data/loh/my_team_v3_base.json").read_text())
opt.save_team(out / "start_team.json", champ)
history = []
for g in range(GENS):
    if g == 0:
        cands = hypotheses(champ)
    else:
        cands, seen = {}, set()
        while len(cands) < M:
            t, d = mutate_team(champ)
            key = json.dumps([[b["stats"], sorted(b["skills"])] for b in t])
            if d and key not in seen:
                seen.add(key); cands[d] = t
    if g == 0:   # also a few random mutants in gen 0
        for _ in range(max(0, M - len(cands))):
            t, d = mutate_team(champ)
            if d: cands.setdefault(d, t)
    best = generation(champ, cands, g)
    accepted = best.d_top3_lo > 0
    history.append({"gen": g, "winner": best.variant, "d_top3": best.d_top3, "lo": best.d_top3_lo, "hi": best.d_top3_hi,
                    "d_points": best.d_points, "accepted": bool(accepted)})
    log(f"GEN {g}: {'ACCEPT' if accepted else 'keep champion'} {best.variant} {best.d_top3:+.2f} [{best.d_top3_lo:+.2f},{best.d_top3_hi:+.2f}]")
    if accepted:
        champ = cands[best.variant] if best.variant in cands else champ
        opt.save_team(out / f"champion_gen{g:02d}.json", champ)
    pd.DataFrame(history).to_csv(out / "history.csv", index=False)
opt.save_team(out / "final_team.json", champ)
for b in champ:
    log(f"FINAL {b['name']}: stats {b['stats']} cost {mock.stat_cost(b['stats'])} ESP {G.build_esp(b['skills'])} "
        f"{len(b['skills']) + 1} skills {b['skills']}")
log("done", out)
