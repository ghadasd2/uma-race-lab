# Progress — step checklist for docs/MASTER_PROMPT.md

Status values: `todo`, `running` (a job is in flight — check its run folder before restarting),
`done`, `blocked` (say why). Update this file in every commit checkpoint.

| Step | Status | Run folder | Commit | Key result |
| --- | --- | --- | --- | --- |
| A0 Housekeeping (context, changelog, master prompt, archive, push) | done | — | see git log | Context saved and pushed to github.com/ghadasd2/uma-race-lab (branch master) |
| A1 Rules and pool | done | — | v4 A1 | Pool 56 → 61 skills; front accel rule in `buildgen.valid`; per-uma HP-out + floor helpers in `mock`; tests pass (10) |
| A2 Mock recalibration (CN 95–97 %) | done | runs/20261120-224122-loh-v4-a2-calibrate | v4 A2 | Shift 150 (incl. stamina) + 2 extra drops → CN 96.00 % (8,750 races); v3 champion 96.29 % but fails HP floor (Kitasan 3.15 %, Ines 4.41 %) |
| A3 v4 base team | done | runs/20261120-225351-loh-v4-a3-base | v4 A3 | Kitasan sta 1200 / spd 1380, Ines sta 1150 / spd 1380, Neo unchanged; HP-out 1.17 / 1.60 / 1.63 %; team 96.17 % |
| A4 Stamina requirement study | running | (chain: A4 → A5 → A6) | | |
| A5 Stat exchange rates | todo | | | |
| A6 Skill values + front accel test | todo | | | |
| A7 Constrained build search | todo | | | |
| A8 Validation | todo | | | |
| A9 v4 results summary | todo | | | |
| B1 Engine 2 intake + adapter | blocked | | | waiting for the user to provide engine 2 |
| B2 Engine 2 re-run of A2–A8 | todo | | | |
| C1 Cross-verification analysis | todo | | | |
| C2 Final cross-verified report | todo | | | |

## Notes
- Remote: `origin` = https://github.com/ghadasd2/uma-race-lab (private), branch `master`. In a new cloud
  session, attach the repo (add_repo, push access) and clone it; the working copy used so far is
  `/home/user/src/uma-race-lab` with the engine at `/home/user/src/GlobalSim` (run `./setup.sh` in a
  fresh clone to fetch, pin, patch and build it).
