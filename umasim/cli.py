"""umasim command line.

  umasim run      SCENARIO [-n 2000] [--frames]
  umasim compare  SCENARIO --variant NAME='{"runners.Mine.stamina":1000}' ... | --variants FILE
  umasim sweep    SCENARIO --path runners.Mine.stamina --values 600:1400:100
  umasim skills   SCENARIO [--candidates "A,B,C" | --query corner] [--max-cost 200]
  umasim courses  [filter]
  umasim skill    QUERY            (search skill table: names, ids, conditions)
  umasim check    SCENARIO          (validate + show resolved setup, no simulation)

Output: compact JSON summary on stdout (or --md for markdown). Raw per-race tables are
saved under runs/<timestamp>-<kind>-<name>/.
"""
from __future__ import annotations

import argparse
import json
import sys

from . import catalog as C
from . import experiments as X
from . import report, spec


def _values(s: str):
    if ":" in s and "," not in s:
        a, b, step = (float(x) for x in s.split(":"))
        vals, v = [], a
        while v <= b + 1e-9:
            vals.append(int(v) if v.is_integer() else v)
            v += step
        return vals
    out = []
    for x in s.split(","):
        x = x.strip()
        try:
            out.append(int(x))
        except ValueError:
            try:
                out.append(float(x))
            except ValueError:
                out.append(x)
    return out


def _emit(summary: dict, md: bool):
    summary.pop("_tables", None)
    if md:
        print(report.markdown(summary))
    else:
        print(json.dumps(summary, indent=1, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(prog="umasim", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, n_default):
        sp.add_argument("scenario")
        sp.add_argument("-n", type=int, default=n_default, help="races (seeds) per variant")
        sp.add_argument("--workers", type=int, default=None)
        sp.add_argument("--seed-base", type=int, default=1)
        sp.add_argument("--md", action="store_true", help="print markdown instead of JSON")
        sp.add_argument("--no-save", action="store_true")

    sp = sub.add_parser("run"); common(sp, 2000)
    sp.add_argument("--frames", action="store_true", help="collect HP-left/blocking/position metrics (slower)")
    sp = sub.add_parser("compare"); common(sp, 2000)
    sp.add_argument("--variant", action="append", default=[], help='NAME=JSON changes')
    sp.add_argument("--variants", help="JSON file {name: changes}")
    sp.add_argument("--frames", action="store_true")
    sp = sub.add_parser("sweep"); common(sp, 1000)
    sp.add_argument("--path", required=True)
    sp.add_argument("--values", required=True, help="a:b:step or comma list")
    sp.add_argument("--frames", action="store_true")
    sp = sub.add_parser("skills"); common(sp, 1000)
    sp.add_argument("--candidates", help="comma-separated skill names/ids")
    sp.add_argument("--query", help="filter normal skills by name/condition text")
    sp.add_argument("--max-cost", type=int)
    sp = sub.add_parser("courses"); sp.add_argument("filter", nargs="*")
    sp = sub.add_parser("skill"); sp.add_argument("query", nargs="*"); sp.add_argument("--limit", type=int, default=25)
    sp.add_argument("--conditions", action="store_true", help="show activation conditions")
    sp = sub.add_parser("check"); sp.add_argument("scenario")

    a = p.parse_args(argv)
    try:
        if a.cmd == "courses":
            f = " ".join(a.filter).lower()
            for c in C.list_courses():
                if all(w in c["label"].lower() + " " + c["distanceType"].lower() for w in f.split()):
                    print(f"{c['courseId']}\t{c['label']}\t{c['distanceType']}\t{c['turn']}\tcorners={c['corners']}"
                          f"\tslopes={c['slopes']}\tfinal_straight={c['finalStraight']}m")
            return
        if a.cmd == "skill":
            for d in C.search_skills(" ".join(a.query), a.limit):
                line = f"{d['id']}\t{d['name']}\t{d['kind']}/{d['rarity']}\tcost={d['cost']}"
                if a.conditions:
                    line += "\n\t" + "\n\t".join(d["conditions"])
                print(line)
            return
        if a.cmd == "check":
            comp = spec.Compiled(spec.load(a.scenario))
            print(json.dumps(comp.describe(), indent=1, ensure_ascii=False))
            return
        scn = spec.load(a.scenario)
        kw = dict(n=a.n, workers=a.workers, seed_base=a.seed_base, save=not a.no_save)
        if a.cmd == "run":
            s = X.run(scn, frames=a.frames, **kw)
        elif a.cmd == "compare":
            variants = json.load(open(a.variants)) if a.variants else {}
            for v in a.variant:
                name, js = v.split("=", 1)
                variants[name] = json.loads(js)
            if not variants:
                p.error("give --variant or --variants")
            s = X.compare(scn, variants, frames=a.frames, **kw)
        elif a.cmd == "sweep":
            s = X.sweep(scn, a.path, _values(a.values), frames=a.frames, **kw)
        elif a.cmd == "skills":
            cands = [c.strip() for c in a.candidates.split(",")] if a.candidates else None
            s = X.skills(scn, cands, query=a.query, max_cost=a.max_cost, **kw)
        _emit(s, a.md)
    except (ValueError, KeyError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
