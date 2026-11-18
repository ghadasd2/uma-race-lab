"""Experiment types. Every experiment returns a compact, JSON-able summary dict
(with an auto-generated `findings` list) and writes raw tables to a run folder.

  run      one scenario, N seeds: per-runner outcomes + what drives the focus runner's wins
  compare  named variants of a scenario on the SAME seeds (paired): deltas with CIs
  sweep    one parameter over a list of values (stat, strategy, ground, ...): response curve
  skills   add each candidate skill to the focus runner: rank by marginal value
"""
from __future__ import annotations

import json
import math
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from . import catalog as C
from . import engine, metrics, spec
from . import stats as S

RUNS_DIR = C.ROOT / "runs"


# --------------------------------------------------------------------------- utils

def _seeds(n: int, base: int = 1) -> list[int]:
    return list(range(base, base + n))


def _r(x, nd=3):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return None
    return round(float(x), nd)


def _pct(x):
    return _r(100 * x, 1)


def _simulate(scn: dict, seeds, frames, workers, variant="base"):
    comp = spec.Compiled(scn)
    replies = engine.simulate(comp, seeds, frames=frames, workers=workers)
    run, sk = metrics.tables(comp, seeds, replies, variant)
    return comp, run, sk


def _save(kind: str, name: str, scn, summary: dict, runners: pd.DataFrame, skills: pd.DataFrame,
          out_dir: str | None = None) -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in (name or kind))[:40]
    d = Path(out_dir) if out_dir else RUNS_DIR / f"{stamp}-{kind}-{slug}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "scenario.json").write_text(json.dumps(scn, indent=2, ensure_ascii=False))
    runners.to_csv(d / "runners.csv.gz", index=False)
    skills.to_csv(d / "skills.csv.gz", index=False)
    summary["run_dir"] = str(d)
    (d / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    from . import report
    (d / "report.md").write_text(report.markdown(summary))
    return str(d)


def runner_summary(df: pd.DataFrame, sk: pd.DataFrame, runner: str, n_seeds: int) -> dict:
    x = df[df.runner == runner]
    n = len(x)
    wins = int(x.win.sum())
    lo, hi = S.wilson(wins, n)
    out = {
        "runner": runner, "strategy": x.strategy.iloc[0] if n else None, "n": n,
        "win_pct": _pct(wins / n), "win_ci": [_pct(lo), _pct(hi)],
        "top3_pct": _pct(x.top3.mean()), "avg_place": _r(x.place.mean(), 2),
        "place_dist_pct": {int(k): _pct(v) for k, v in x.place.value_counts(normalize=True).sort_index().items()},
        "time_mean": _r(x.time.mean()), "time_sd": _r(x.time.std()),
        "behind_winner_s": _r(x.behind.mean()),
        "full_spurt_pct": _pct(x.full_spurt.mean()),
        "spurt_delay_m_mean": _r(x.spurt_delay_m.mean(), 1),
        "hp_empty_pct": _pct(x.hp_empty.mean()),
        "rushed_pct": _pct(x.rushed.mean()),
        "late_start_pct": _pct(x.late_start.mean()),
        "duel_pct": _pct((x.duels > 0).mean()),
    }
    if "hp_left" in x:
        out.update({"hp_left_mean": _r(x.hp_left.mean(), 1), "hp_left_pct_mean": _r(x.hp_left_pct.mean(), 1),
                    "blocked_frac_mean": _r(x.blocked_frac.mean()),
                    "rank_mid_mean": _r(x.rank_mid.mean(), 2), "rank_late_mean": _r(x.rank_late.mean(), 2)})
    s = sk[sk.runner == runner]
    skl = []
    for (sid, name), g in s.groupby(["skill_id", "skill"]):
        fired = g.seed.nunique()
        skl.append({"skill": name, "id": sid, "activation_pct": _pct(fired / n_seeds),
                    "t_median": _r(g.t.median(), 1), "t_p10_p90": [_r(g.t.quantile(.1), 1), _r(g.t.quantile(.9), 1)]})
    out["skills"] = sorted(skl, key=lambda d: -d["activation_pct"])
    return out


def _drivers(df: pd.DataFrame, sk: pd.DataFrame, focus: str, min_group: int = 30) -> list[dict]:
    """Conditional win-rate contrasts for the focus runner. Correlational, not causal."""
    x = df[df.runner == focus].set_index("seed")
    feats = {
        "rushed": x.rushed, "late_start": x.late_start, "full_spurt": x.full_spurt,
        "hp_empty": x.hp_empty, "dueled": x.duels > 0,
        "inner_gate(1-3)": x.gate <= 3, "outer_gate(last 3)": x.gate > (df.gate.max() - 3),
    }
    if "blocked_frac" in x:
        feats["blocked>20%"] = x.blocked_frac > 0.2
    s = sk[sk.runner == focus]
    for name, g in s.groupby("skill"):
        fired = x.index.isin(g.seed.unique())
        feats[f"skill fired: {name}"] = pd.Series(fired, index=x.index)
        # early vs late activation among firing races
        first = g.groupby("seed").t.min()
        if len(first) >= 2 * min_group:
            med = first.median()
            feats[f"{name} early (t<{med:.0f}s)"] = pd.Series(x.index.map(lambda sd: first.get(sd, np.inf) < med), index=x.index)
    out = []
    for name, mask in feats.items():
        mask = mask.astype(bool)
        k1, n1 = int(x.win[mask].sum()), int(mask.sum())
        k0, n0 = int(x.win[~mask].sum()), int((~mask).sum())
        if min(n1, n0) < min_group:
            continue
        t = S.two_prop(k0, n0, k1, n1)
        out.append({"factor": name, "share_pct": _pct(n1 / len(x)), "win_pct_if": _pct(k1 / n1),
                    "win_pct_else": _pct(k0 / n0), "delta_pp": _pct(t["diff"]), "p": t["p"],
                    "avg_place_if": _r(x.place[mask].mean(), 2), "avg_place_else": _r(x.place[~mask].mean(), 2)})
    ps = S.holm([d["p"] for d in out]) if out else []
    for d, p in zip(out, ps):
        d["p_holm"] = float(f"{p:.3g}")
        d["p"] = float(f"{d['p']:.3g}")
    return sorted(out, key=lambda d: (d["p_holm"], -abs(d["delta_pp"])))


# --------------------------------------------------------------------------- run

def run(scn: dict, n: int = 2000, frames: bool = False, workers=None, seed_base: int = 1,
        save: bool = True, out_dir=None) -> dict:
    scn = spec.load(scn)
    t0 = time.time()
    seeds = _seeds(n, seed_base)
    comp, df, sk = _simulate(scn, seeds, frames, workers)
    el = time.time() - t0
    field = [runner_summary(df, sk, r, n) for r in comp.names]
    field.sort(key=lambda d: -d["win_pct"])
    focus = next(f for f in field if f["runner"] == comp.focus)
    by_strategy = (df.groupby("strategy").agg(win_pct=("win", "mean"), avg_place=("place", "mean"), runners=("runner", "nunique"))
                   .assign(win_pct_per_runner=lambda t: 100 * t.win_pct / t.runners, win_pct=lambda t: 100 * t.win_pct)
                   .round(2).reset_index().to_dict("records"))
    by_gate = (df[df.runner == comp.focus].groupby("gate").agg(win_pct=("win", "mean"), avg_place=("place", "mean"), n=("win", "size"))
               .assign(win_pct=lambda t: 100 * t.win_pct).round(2).reset_index().to_dict("records"))
    summary = {
        "kind": "run", "name": scn.get("name", ""), "races": n, "seconds": round(el, 1),
        "races_per_sec": round(n / el), "setup": comp.describe(), "focus": focus,
        "field": [{k: f[k] for k in ("runner", "strategy", "win_pct", "win_ci", "top3_pct", "avg_place", "full_spurt_pct",
                                      "hp_empty_pct", "rushed_pct")} for f in field],
        "by_strategy": by_strategy, "focus_by_gate": by_gate,
        "drivers": _drivers(df, sk, comp.focus),
    }
    summary["findings"] = _findings_run(summary)
    if save:
        _save("run", scn.get("name", ""), scn, summary, df, sk, out_dir)
    summary["_tables"] = (df, sk)
    return summary


def _findings_run(s: dict) -> list[str]:
    f, out = s["focus"], []
    out.append(f"{f['runner']} wins {f['win_pct']}% (95% CI {f['win_ci'][0]}–{f['win_ci'][1]}), "
               f"avg place {f['avg_place']}, top-3 {f['top3_pct']}% over {f['n']} races.")
    if f["hp_empty_pct"] and f["hp_empty_pct"] > 5:
        out.append(f"STAMINA: {f['runner']} runs out of HP in {f['hp_empty_pct']}% of races.")
    if f["full_spurt_pct"] is not None and f["full_spurt_pct"] < 90:
        out.append(f"STAMINA: full last spurt only {f['full_spurt_pct']}% of the time "
                   f"(spurt starts on average {f['spurt_delay_m_mean']} m late).")
    if f["rushed_pct"] and f["rushed_pct"] > 15:
        out.append(f"WIT: rushes (kakari) in {f['rushed_pct']}% of races.")
    for d in s["drivers"][:6]:
        if d["p_holm"] < 0.01 and abs(d["delta_pp"]) >= 2:
            out.append(f"DRIVER: when '{d['factor']}' ({d['share_pct']}% of races) win rate is {d['win_pct_if']}% vs "
                       f"{d['win_pct_else']}% otherwise ({d['delta_pp']:+} pp, p_holm={d['p_holm']}). Correlational.")
    for sk in f["skills"]:
        if sk["activation_pct"] < 60:
            out.append(f"SKILL: '{sk['skill']}' only activates in {sk['activation_pct']}% of races.")
    top = s["field"][0]
    if top["runner"] != f["runner"]:
        out.append(f"FIELD: strongest runner is {top['runner']} ({top['strategy']}) at {top['win_pct']}%.")
    return out


# --------------------------------------------------------------------------- compare

METRICS = [("win", "win_pp", 100), ("top3", "top3_pp", 100), ("place", "place", 1), ("time", "time_s", 1),
           ("full_spurt", "full_spurt_pp", 100), ("hp_empty", "hp_empty_pp", 100), ("rushed", "rushed_pp", 100)]


def compare(scn: dict, variants: dict, n: int = 2000, frames=False, workers=None, seed_base=1,
            save=True, out_dir=None, kind="compare", label=None) -> dict:
    """variants: {"name": {changes}} or {"name": full_scenario}; a "base" variant is added automatically."""
    scn = spec.load(scn)
    seeds = _seeds(n, seed_base)
    t0 = time.time()
    all_v = {"base": scn}
    for name, ch in variants.items():
        all_v[name] = ch if "runners" in ch and "course" in ch else spec.apply_changes(scn, ch)
    dfs, sks, comps = [], [], {}
    for name, vs in all_v.items():
        comp, df, sk = _simulate(vs, seeds, frames, workers, name)
        comps[name] = comp
        dfs.append(df)
        sks.append(sk)
    el = time.time() - t0
    df, sk = pd.concat(dfs, ignore_index=True), pd.concat(sks, ignore_index=True)
    focus = comps["base"].focus
    f = df[df.runner == focus]
    base = f[f.variant == "base"].set_index("seed").sort_index()
    rows = []
    for name in all_v:
        v = f[f.variant == name].set_index("seed").sort_index()
        summ = runner_summary(df[df.variant == name], sk[sk.variant == name], focus, n)
        row = {"variant": name, **{k: summ[k] for k in ("win_pct", "win_ci", "top3_pct", "avg_place", "time_mean",
                                                       "full_spurt_pct", "hp_empty_pct", "rushed_pct")}}
        if "hp_left_pct_mean" in summ:
            row["hp_left_pct_mean"] = summ["hp_left_pct_mean"]
        if name != "base":
            for col, key, mult in METRICS:
                d = S.paired_diff(base[col].astype(float), v[col].astype(float))
                row[f"d_{key}"] = {"diff": _r(d["diff"] * mult, 3), "ci": [_r(d["lo"] * mult, 3), _r(d["hi"] * mult, 3)],
                                   "p": float(f"{d['p']:.3g}")}
            row["skills"] = summ["skills"]
        rows.append(row)
    ps = [r["d_win_pp"]["p"] for r in rows if "d_win_pp" in r]
    for r, p in zip([r for r in rows if "d_win_pp" in r], S.holm(ps)):
        r["d_win_pp"]["p_holm"] = float(f"{p:.3g}")
    summary = {"kind": kind, "name": label or scn.get("name", ""), "races": n * len(all_v), "seeds_per_variant": n,
               "seconds": round(el, 1), "setup": comps["base"].describe(), "focus": focus,
               "variants": {k: (v if not ("runners" in v and "course" in v) else "full scenario") for k, v in variants.items()},
               "results": rows}
    summary["findings"] = _findings_compare(summary)
    if save:
        _save(kind, summary["name"], {"base": scn, "variants": variants}, summary, df, sk, out_dir)
    summary["_tables"] = (df, sk)
    return summary


def _findings_compare(s: dict) -> list[str]:
    out = []
    base = s["results"][0]
    out.append(f"Baseline: {s['focus']} wins {base['win_pct']}% (avg place {base['avg_place']}).")
    ranked = sorted(s["results"][1:], key=lambda r: -r["d_win_pp"]["diff"])
    for r in ranked:
        d, t = r["d_win_pp"], r["d_time_s"]
        sig = "significant" if d.get("p_holm", d["p"]) < 0.01 else ("suggestive" if d["p"] < 0.05 else "not significant")
        out.append(f"{r['variant']}: win {d['diff']:+.1f} pp [{d['ci'][0]:+.1f}, {d['ci'][1]:+.1f}] ({sig}); "
                   f"time {t['diff']:+.3f}s; avg place {r['d_place']['diff']:+.2f}; "
                   f"full spurt {r['full_spurt_pct']}%; HP-out {r['hp_empty_pct']}%.")
    return out


# --------------------------------------------------------------------------- sweep

def sweep(scn: dict, path: str, values: list, n: int = 1000, frames=False, workers=None, seed_base=1,
          save=True, out_dir=None) -> dict:
    """path like 'runners.Mine.stamina' / 'runners.Mine.strategy' / 'ground'."""
    scn = spec.load(scn)
    variants = {f"{path.split('.')[-1]}={v}": {path: v} for v in values}
    s = compare(scn, variants, n, frames, workers, seed_base, save=False, kind="sweep",
                label=scn.get("name", "") + f" sweep {path}")
    rows = s["results"][1:]
    curve = [{"value": v, **{k: r[k] for k in ("win_pct", "win_ci", "top3_pct", "avg_place", "time_mean",
                                              "full_spurt_pct", "hp_empty_pct", "rushed_pct")},
              **({"hp_left_pct_mean": r["hp_left_pct_mean"]} if "hp_left_pct_mean" in r else {})}
             for v, r in zip(values, rows)]
    s.update({"path": path, "values": values, "curve": curve, "baseline": s["results"][0]})
    df, sk = s.pop("_tables")
    # paired test of every value against the best one (same seeds) on finishing place
    f = df[df.runner == s["focus"]]
    best_i = max(range(len(curve)), key=lambda i: (curve[i]["win_pct"], -curve[i]["avg_place"]))
    names = list(variants)
    bp = f[f.variant == names[best_i]].set_index("seed").sort_index().place
    for i, p in enumerate(curve):
        vp = f[f.variant == names[i]].set_index("seed").sort_index().place
        d = S.paired_diff(bp, vp)
        p["vs_best_place"] = {"diff": _r(d["diff"], 3), "ci": [_r(d["lo"], 3), _r(d["hi"], 3)], "p": float(f"{d['p']:.3g}")}
    s["findings"] = _findings_sweep(s)
    del s["results"]
    if save:
        _save("sweep", s["name"], {"base": scn, "path": path, "values": values}, s, df, sk, out_dir)
    s["_tables"] = (df, sk)
    return s


def _findings_sweep(s: dict) -> list[str]:
    c, out = s["curve"], []
    numeric = all(isinstance(p["value"], (int, float)) for p in c)
    best = max(c, key=lambda p: p["win_pct"])
    out.append(f"Best {s['path']} = {best['value']} → win {best['win_pct']}% (CI {best['win_ci'][0]}–{best['win_ci'][1]}).")
    if numeric and len(c) >= 3:
        w = [p["win_pct"] for p in c]
        diffs = np.diff(w)
        trend = "rises" if w[-1] > w[0] + 2 else ("falls" if w[-1] < w[0] - 2 else "is flat")
        out.append(f"Win rate {trend} from {w[0]}% to {w[-1]}% across {c[0]['value']}→{c[-1]['value']}.")
        # plateau: first value not significantly worse than the best (paired on avg place)
        plateau = next((p for p in c if p["vs_best_place"]["p"] >= 0.01 or p["vs_best_place"]["diff"] <= 0.01), None)
        if plateau and plateau["value"] != best["value"]:
            out.append(f"Diminishing returns: from {plateau['value']} on, results are within noise of the best "
                       f"(paired avg-place gap {plateau['vs_best_place']['diff']:+.3f}, p={plateau['vs_best_place']['p']}).")
        step = c[1]["value"] - c[0]["value"]
        if step:
            big = int(np.argmax(diffs))
            out.append(f"Largest single-step gain: {c[big]['value']}→{c[big + 1]['value']} ({diffs[big]:+.1f} pp).")
        for key, label, thr, better in (("hp_empty_pct", "HP never runs out (<2%)", 2, "below"),
                                       ("full_spurt_pct", "full spurt ≥95%", 95, "above")):
            hit = next((p for p in c if (p[key] < thr if better == "below" else p[key] >= thr)), None)
            if hit and hit is not c[0]:
                out.append(f"Threshold: {label} first reached at {hit['value']}.")
    return out


# --------------------------------------------------------------------------- skills

def skills(scn: dict, candidates: list | None = None, n: int = 1000, workers=None, seed_base=1, save=True,
           out_dir=None, query: str | None = None, max_cost: int | None = None) -> dict:
    """Marginal value of adding each candidate skill to the focus runner (same seeds, paired)."""
    scn = spec.load(scn)
    comp = spec.Compiled(scn)
    focus = comp.focus
    have = {s["skillId"] for s in comp.template["horses"][comp.focus_index]["skills"]}
    if candidates:
        ids = [C.resolve_skill(c) for c in candidates]
    else:
        ids = [d["id"] for d in C.search_skills(query or "", limit=10_000, kind="normal")]
    ids = [i for i in ids if i not in have]
    if max_cost is not None:
        ids = [i for i in ids if (C.skill_info(i)["cost"] or 0) <= max_cost]
    variants = {C.skill_names().get(i, i) + f" [{i}]": {f"runners.{focus}.skills+": [i]} for i in ids}
    s = compare(scn, variants, n, False, workers, seed_base, save=False, kind="skills",
                label=scn.get("name", "") + " skill value")
    D = comp.course["distance"]
    rows = []
    for r in s["results"][1:]:
        name, sid = r["variant"].rsplit(" [", 1)
        sid = sid.rstrip("]")
        info = C.skill_info(sid)
        act = next((x["activation_pct"] for x in r["skills"] if x["id"] == sid), 0.0)
        dt = r["d_time_s"]["diff"]
        speed = D / s["results"][0]["time_mean"]
        rows.append({"skill": name, "id": sid, "rarity": info["rarity"], "cost": info["cost"],
                     "activation_pct": act, "d_win_pp": r["d_win_pp"]["diff"], "d_win_ci": r["d_win_pp"]["ci"],
                     "p_holm": r["d_win_pp"].get("p_holm"), "d_time_s": dt,
                     "lengths_gained": _r(-dt * speed / 2.5, 2),  # 1 length (bashin) ≈ 2.5 m
                     "d_place": r["d_place"]["diff"],
                     "win_pp_per_100sp": _r(100 * r["d_win_pp"]["diff"] / info["cost"], 2) if info["cost"] else None})
    rows.sort(key=lambda d: -d["d_win_pp"])
    # Adding a skill changes the engine's random-number consumption even if it never fires,
    # so pairs partially de-synchronise. Skills that never activate measure that pure-RNG shift.
    inert = [r["d_win_pp"] for r in rows if r["activation_pct"] == 0]
    noise = {"inert_skills": len(inert), "mean_shift_pp": _r(float(np.mean(inert)), 2) if inert else None,
             "note": "Δ of skills that never fired: pure RNG re-draw effect. Treat smaller |Δ| as noise."}
    s.update({"baseline": s["results"][0], "ranking": rows, "noise_floor": noise})
    df, sk = s.pop("_tables")
    del s["results"]
    s["findings"] = _findings_skills(s)
    if save:
        _save("skills", s["name"], {"base": scn, "candidates": ids}, s, df, sk, out_dir)
    s["_tables"] = (df, sk)
    return s


def _findings_skills(s: dict) -> list[str]:
    out = [f"Baseline {s['focus']}: win {s['baseline']['win_pct']}%. Tested {len(s['ranking'])} skills × {s['seeds_per_variant']} races."]
    sig = [r for r in s["ranking"] if r["p_holm"] is not None and r["p_holm"] < 0.05 and r["d_win_pp"] > 0
           and r["activation_pct"] > 0]
    for r in s["ranking"][:8]:
        out.append(f"{r['skill']}: {r['d_win_pp']:+.1f} pp win, {r['lengths_gained']:+.2f} lengths, "
                   f"fires {r['activation_pct']}%" + (f", cost {r['cost']}" if r["cost"] else "")
                   + (" (significant)" if r in sig else ""))
    nf = s.get("noise_floor", {})
    if nf.get("inert_skills"):
        out.append(f"NOISE FLOOR: {nf['inert_skills']} never-firing skills still moved win rate by {nf['mean_shift_pp']:+} pp "
                   f"(RNG re-draw). Effects smaller than that are not distinguishable from noise; raise -n for precision.")
    dead = [r["skill"] for r in s["ranking"] if r["activation_pct"] < 5]
    if dead:
        out.append(f"Never/rarely activate here (<5%): {', '.join(dead[:12])}" + (" …" if len(dead) > 12 else ""))
    neg = [r for r in s["ranking"] if r["p_holm"] is not None and r["p_holm"] < 0.05 and r["d_win_pp"] < 0]
    for r in neg:
        out.append(f"HARMFUL here: {r['skill']} ({r['d_win_pp']:+.1f} pp).")
    return out
