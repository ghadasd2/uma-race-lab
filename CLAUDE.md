# uma-race-lab

Monte Carlo race-analysis lab for Umamusume **Global**, built on the GlobalSim engine
(`vendor/GlobalSim`, AGPL-3.0, run unmodified as a subprocess).

You are the race analyst. For any question about builds, stats, skills, strategies, courses or why a
runner wins, follow `.claude/skills/race-analyst/SKILL.md`: frame → scenario → experiment → stats →
mechanism → verify → conclude. Never answer from intuition when a simulation can answer it.

- CLI: `./umasim.sh {run,compare,sweep,skills,check,courses,skill}`. Python API: `umasim.experiments`.
- Scenarios live in `scenarios/`. Results land in `runs/<stamp>-<kind>-<name>/` (summary.json, report.md, CSVs).
- Mechanics reference: `vendor/GlobalSim/docs/RACE-MECHANICS.md` (also MATHEMATICS, SKILLS, FIELD-MECHANICS).
- Validated v77 profile + v70 skill table, extended with legacy-table skills converted to the same shape
  (`approximated` flag; LoH opponent skills among them were checked against in-game data in
  `data/loh/skill_specs.json`). Do not enable experimental/JP-only engine switches.
- League of Heroes project: `umasim/loh.py` (race model), `umasim/opt.py` (optimizer), `scripts/loh_stage*.py`,
  data and rules in `data/loh/`.
- Tests: `python3 -m pytest -q tests`. First-time setup: `./setup.sh`.
