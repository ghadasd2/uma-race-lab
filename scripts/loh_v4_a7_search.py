"""v4 step A7: constrained whole-team build search vs the v4 mock field.
Constraints per uma: stat box BOX (stamina up to 1300), in-game cost <= 6400 (points > 1200 cost 2), skills legal per
buildgen.valid (pool, ESP 4500-4600, <= 23 incl. unique, <= 3 inherited, tier groups, FRONT START-ACCEL RULE), and the
HP-OUT FLOOR (each of my umas out of HP in <= 3/175 races):
  rounds 0-1 drop candidates with any uma's HP-out > LENIENT (small samples); the final round only accepts a winner that
  meets the floor on its 9x races.
Generation 0 = hypotheses from A4 (feasible stamina/drain combos), A6 (top adds, accel sets) + random mutants;
later generations = guided mutations of the champion (stat moves 25/50, value-weighted skill adds, swaps).
Each generation: paired successive halving on fresh seeds (n0 -> x3 -> x2); accept only if the 95 % CI lower bound > 0.
Resumable: pass the run dir; finished generations are read back from history.csv / champion files.
Usage: loh_v4_a7_search.py GENERATIONS CANDIDATES_PER_GEN N0 [RUN_DIR]"""
import copy, glob, json, random, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import buildgen as G, mock, opt

GENS, M, N0 = (int(a) for a in sys.argv[1:4])
out = Path(sys.argv[4]) if len(sys.argv) > 4 else opt.run_dir("v4-a7-search")
logf = open(out / "log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); logf.write(m + "\n"); logf.flush()
rng = random.Random(20261120)
STAT = ["spd", "sta", "pow", "guts", "wit"]
BOX = [(1350, 1500), (950, 1300), (1100, 1250), (1000, 1250), (1100, 1250)]
LENIENT = 0.025
RES = Path("data/loh/results/v4")

sv = pd.read_csv(RES / "A6" / "skill_values.csv")
HOLD = {(r.uma, r.skill): -r.d_team_top3 for r in sv[sv.test == "drop"].itertuples()}
ADD = {(r.uma, r.skill): r.d_team_top3 for r in sv[sv.test.isin(["add", "swap"])].itertuples()}
REQ = pd.read_csv(RES / "A4" / "requirements.csv")
ACC = pd.read_csv(RES / "A6" / "accel_test.csv")


def stat_ok(st):
    return mock.stat_cost(st) <= mock.COST_BUDGET and all(lo <= v <= hi for v, (lo, hi) in zip(st, BOX))


def fill_budget(st):
    st = list(st)
    for k in (0, 2):
        while True:
            t = list(st); t[k] += 5
            if t[k] > BOX[k][1] or mock.stat_cost(t) > mock.COST_BUDGET:
                break
            st = t
    return st


def neutral(stats, k, val):
    s = list(stats); before = mock.stat_cost(s); s[k] = val
    diff = mock.stat_cost(s) - before
    s[0] -= -(-diff // 2) if s[0] > 1200 else diff
    return s


def stat_move(b):
    for _ in range(50):
        a, c = rng.sample(range(5), 2); step = rng.choice([25, 50])
        st = list(b["stats"]); st[a] -= step
        while True:
            t = list(st); t[c] += 5
            if t[c] > BOX[c][1] or mock.stat_cost(t) > mock.COST_BUDGET:
                break
            st = t
        if stat_ok(st) and st != b["stats"]:
            nb = copy.deepcopy(b); nb["stats"] = st
            return nb, f"{STAT[a]}-{step}->{STAT[c]}"
    return None, None


def add_skill(b, s):
    """Put s in; drop the lowest-hold-value removable skills until the build is legal (or give up)."""
    if b is None:
        return None
    fixed = set(G.EVOLVED.get(b["name"], []))
    sk = [x for x in b["skills"] if G._group(x) != G._group(s)] + [s]
    for _ in range(6):
        ok, why = G.valid(b, sk)
        if ok:
            nb = copy.deepcopy(b); nb["skills"] = sk
            return nb
        if "ESP" in why and G.build_esp(sk) < G.esp_range()[0]:
            return None
        cands = [x for x in sk if x not in fixed and x != s and G.front_accel_ok(b, [y for y in sk if y != x])]
        if not cands:
            return None
        sk.remove(min(cands, key=lambda x: HOLD.get((b["name"], x), 0.0)))
    return None


def skill_add(b):
    pool = [p["skill"] for p in G.candidates(b) if p["skill"] not in b["skills"]]
    w = [max(0.05, ADD.get((b["name"], s), 0.0) + 0.3) for s in pool]
    for _ in range(20):
        s = rng.choices(pool, weights=w)[0]
        nb = add_skill(b, s)
        if nb:
            return nb, f"+{s} -{'/'.join(sorted(set(b['skills']) - set(nb['skills'])))}"
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


DRAIN_SETS = {"RS": ["Racing Spirit: Stamina"], "MD": ["Mad Dash"], "RS+MD": ["Racing Spirit: Stamina", "Mad Dash"],
              "FT": ["Full Throttle"], "KG": ["Keep Going!"], "RS+FT": ["Racing Spirit: Stamina", "Full Throttle"],
              "RS+KG": ["Racing Spirit: Stamina", "Keep Going!"], "none": []}
DRAIN = {"Racing Spirit: Stamina", "Mad Dash", "Full Throttle", "Keep Going!"}


def hypotheses(team):
    H = {}
    def keep(name, t):
        if t and all(b and G.valid(b, b["skills"])[0] and stat_ok(b["stats"]) for b in t):
            H[name] = t
        else:
            log("skip hypothesis", name)
    t = copy.deepcopy(team)
    for b in t:
        b["stats"] = fill_budget(b["stats"])
    keep("fill budget (speed)", t)
    for i, b in enumerate(team):
        short = b["name"].split()[0]
        # A4: every drain set that beats no-drain at its best feasible stamina
        for r in REQ[(REQ.uma == b["name"])].itertuples():
            if pd.isna(r.best_feasible_stamina) or not (r.vs_best_none_pp > 0.3):
                continue
            t = copy.deepcopy(team)
            nb = copy.deepcopy(b); nb["skills"] = [x for x in nb["skills"] if x not in DRAIN]
            for s in DRAIN_SETS[r.skills]:
                nb = add_skill(nb, s)
            if nb is None:
                log("skip", short, r.skills, "(no legal build)"); continue
            nb["stats"] = neutral(nb["stats"], 1, int(r.best_feasible_stamina))
            t[i] = nb
            keep(f"{short} {r.skills} @ sta {int(r.best_feasible_stamina)}", t)
        # A6: top adds with CI above 0
        adds = sv[(sv.uma == b["name"]) & sv.test.isin(["add", "swap"]) & (sv.lo > 0)].sort_values("d_team_top3", ascending=False)
        for r in adds.head(4).itertuples():
            t = copy.deepcopy(team); t[i] = add_skill(b, r.skill)
            keep(f"{short} +{r.skill}", t)
        # A6: best accel set if it beats the base set
        a = ACC[(ACC.uma == b["name"]) & (ACC.lo > 0)].sort_values("d_team_top3", ascending=False)
        for r in a.head(1).itertuples():
            st = r.set.split(" + ")
            nb = copy.deepcopy(b)
            nb["skills"] = [x for x in nb["skills"] if x not in set(G.GROUNDWORK_FAMILY) | {"Taking the Lead"}]
            for s in st:
                nb = add_skill(nb, s)
            t = copy.deepcopy(team); t[i] = nb
            keep(f"{short} accel {r.set}", t)
    return H


def generation(champ, cands, g):
    alive = {"base": champ, **cands}
    n, seed0 = N0, 110_000_000 + g * 1_000_000
    for r, keep in enumerate([8, 3, None]):
        seeds = list(range(seed0 + r * 100_000, seed0 + r * 100_000 + n))
        t0 = time.time()
        df = mock.evaluate(alive, seeds)
        s = mock.summarize(df)
        s["hp_max%"] = s[["hp0%", "hp1%", "hp2%"]].max(axis=1)
        s.to_csv(out / f"gen{g:02d}_round{r}.csv", index=False)
        b = s[s.variant == "base"].iloc[0]
        log(f"gen {g} round {r}: {len(alive)} x {n} = {len(df)} races {time.time() - t0:.0f}s; base {b.top3:.2f} "
            f"(HP-out max {b['hp_max%']:.2f}%)")
        others = s[s.variant != "base"]
        if keep is None:
            ok = others[others.hp_ok]
            log("   " + " | ".join(f"{v} {d:+.2f}[{lo:+.2f}] hp{h:.1f}" for v, d, lo, h in
                                   zip(others.variant.head(4), others.d_top3.head(4), others.d_top3_lo.head(4), others["hp_max%"].head(4))))
            return (ok.iloc[0] if len(ok) else None), others
        others = others[others["hp_max%"] <= 100 * LENIENT]
        log("   " + " | ".join(f"{v} {d:+.2f}[{lo:+.2f}] hp{h:.1f}" for v, d, lo, h in
                               zip(others.variant.head(6), others.d_top3.head(6), others.d_top3_lo.head(6), others["hp_max%"].head(6))))
        if not len(others):
            return None, others
        alive = {v: alive[v] for v in ["base"] + list(others.head(keep).variant)}
        n *= 3 if r == 0 else 2


hist_file = out / "history.csv"
history = pd.read_csv(hist_file).to_dict("records") if hist_file.exists() else []
champs = sorted(out.glob("champion_gen*.json"))
champ = json.loads((champs[-1] if champs else Path("data/loh/my_team_v4_base.json")).read_text())
if not hist_file.exists():
    opt.save_team(out / "start_team.json", champ)
for g in range(len(history), GENS):
    cands, seen = ({}, set())
    if g == 0:
        cands = hypotheses(champ)
    while len(cands) < M:
        t, d = mutate_team(champ)
        key = json.dumps([[b["stats"], sorted(b["skills"])] for b in t])
        if d and key not in seen:
            seen.add(key); cands.setdefault(d, t)
    best, _ = generation(champ, cands, g)
    accepted = best is not None and best.d_top3_lo > 0
    history.append({"gen": g, "winner": None if best is None else best.variant,
                    "d_top3": None if best is None else best.d_top3, "lo": None if best is None else best.d_top3_lo,
                    "hi": None if best is None else best.d_top3_hi, "d_points": None if best is None else best.d_points,
                    "hp_max%": None if best is None else best["hp_max%"], "accepted": bool(accepted)})
    log(f"GEN {g}: {'ACCEPT' if accepted else 'keep champion'} " +
        ("(no candidate met the HP floor)" if best is None else f"{best.variant} {best.d_top3:+.2f} [{best.d_top3_lo:+.2f},{best.d_top3_hi:+.2f}]"))
    if accepted:
        champ = cands[best.variant]
        opt.save_team(out / f"champion_gen{g:02d}.json", champ)
    pd.DataFrame(history).to_csv(hist_file, index=False)
opt.save_team(out / "final_team.json", champ)
for b in champ:
    log(f"FINAL {b['name']}: stats {b['stats']} cost {mock.stat_cost(b['stats'])} ESP {G.build_esp(b['skills'])} "
        f"{len(b['skills']) + 1} skills {b['skills']}")
log("done", out)
