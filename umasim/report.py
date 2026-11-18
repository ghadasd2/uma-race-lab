"""Markdown rendering of experiment summaries."""
from __future__ import annotations


def _table(rows: list[dict], cols: list[str]) -> str:
    if not rows:
        return "_none_\n"
    def fmt(v):
        if isinstance(v, dict) and "diff" in v:
            return f"{v['diff']:+g} [{v['ci'][0]:+g},{v['ci'][1]:+g}]"
        if isinstance(v, list):
            return "–".join(str(x) for x in v)
        return "" if v is None else str(v)
    out = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    for r in rows:
        out += "| " + " | ".join(fmt(r.get(c)) for c in cols) + " |\n"
    return out


def markdown(s: dict) -> str:
    setup = s.get("setup", {})
    c = setup.get("course", {})
    md = f"# {s['kind'].upper()}: {s.get('name') or ''}\n\n"
    md += (f"**Course** {c.get('label')} ({c.get('distanceType')}, {c.get('turn')}-handed) · "
           f"{setup.get('ground')} / {setup.get('weather')} / {setup.get('season')} · gates: {setup.get('gates')} · "
           f"focus: **{s.get('focus') if isinstance(s.get('focus'), str) else s['focus']['runner']}** · "
           f"{s.get('races')} races in {s.get('seconds')}s\n\n")
    md += "## Findings\n\n" + "".join(f"- {f}\n" for f in s.get("findings", [])) + "\n"
    k = s["kind"]
    if k == "run":
        md += "## Field\n\n" + _table(s["field"], ["runner", "strategy", "win_pct", "win_ci", "top3_pct", "avg_place",
                                                   "full_spurt_pct", "hp_empty_pct", "rushed_pct"])
        md += "\n## Focus runner skills\n\n" + _table(s["focus"]["skills"], ["skill", "activation_pct", "t_median", "t_p10_p90"])
        md += "\n## Win drivers (focus runner, correlational)\n\n" + _table(
            s["drivers"], ["factor", "share_pct", "win_pct_if", "win_pct_else", "delta_pp", "p_holm"])
        md += "\n## Focus by gate\n\n" + _table(s["focus_by_gate"], ["gate", "win_pct", "avg_place", "n"])
    elif k == "compare":
        md += "## Variants (paired on identical seeds; deltas vs base with 95% CI)\n\n" + _table(
            s["results"], ["variant", "win_pct", "d_win_pp", "avg_place", "d_place", "d_time_s", "full_spurt_pct", "hp_empty_pct", "rushed_pct"])
    elif k == "sweep":
        md += f"## Curve: {s['path']}\n\n" + _table(s["curve"], ["value", "win_pct", "win_ci", "top3_pct", "avg_place", "vs_best_place",
                                                             "time_mean", "full_spurt_pct", "hp_empty_pct", "rushed_pct"])
    elif k == "skills":
        md += "## Skill ranking (added to focus runner)\n\n" + _table(
            s["ranking"], ["skill", "rarity", "cost", "activation_pct", "d_win_pp", "d_win_ci", "lengths_gained", "d_place", "p_holm"])
    if s.get("run_dir"):
        md += f"\nRaw tables: `{s['run_dir']}/runners.csv.gz`, `skills.csv.gz`\n"
    return md
