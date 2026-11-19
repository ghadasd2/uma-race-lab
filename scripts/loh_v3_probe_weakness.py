import sys, copy; sys.path.insert(0, '/home/user/src/uma-race-lab')
from umasim import loh, mock
cn = loh.opponent_team("cn"); seeds = list(range(41_000_000, 41_002_000))
orig = mock.mock_runner
def run(tag, f):
    mock._DRAWS.clear()
    mock.mock_runner = lambda rng, u: f(orig(rng, u))
    df = mock.evaluate({"base": cn}, seeds); mock.mock_runner = orig
    x = df; print(f"{tag:40s} CN team top3 {100*x.top3.mean():.1f}  pts {x.points.mean():.0f}  sweep {100*(x.top3==1).mean():.1f}", flush=True)
def lvl(b, L): b = copy.deepcopy(b); b["unique"]["level"] = L; return b
def apt(b): b = copy.deepcopy(b); b["distance"] = "A"; return b
def shift(b, d): b = copy.deepcopy(b); b["stats"] = [s - d for s in b["stats"]]; return b
def drop(b, k):
    import random; b = copy.deepcopy(b); r = random.Random(hash(tuple(b["stats"])))
    fixed = set(mock.G.EVOLVED.get(b["name"], [])); cand = [s for s in b["skills"] if s not in fixed]
    for s in r.sample(cand, min(k, len(cand))): b["skills"].remove(s)
    return b
run("spec (baseline)", lambda b: b)
run("unique Lv3", lambda b: lvl(b, 3))
run("distance A", apt)
run("drop +4 more skills", lambda b: drop(b, 4))
run("drop +8 more skills", lambda b: drop(b, 8))
run("all stats -100", lambda b: shift(b, 100))
run("all stats -200", lambda b: shift(b, 200))
run("Lv3 + dist A + drop 4 + stats -100", lambda b: shift(drop(apt(lvl(b, 3)), 4), 100))
