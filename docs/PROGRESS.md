# Progress — step checklist for docs/MASTER_PROMPT.md

Status values: `todo`, `running` (a job is in flight — check its run folder before restarting),
`done`, `blocked` (say why). Update this file in every commit checkpoint.

| Step | Status | Run folder | Commit | Key result |
| --- | --- | --- | --- | --- |
| A0 Housekeeping (context, changelog, master prompt, archive, push) | done (local; push blocked) | — | see git log | Context saved; no GitHub remote exists yet — the user must create an empty repo |
| A1 Rules and pool | done | — | v4 A1 | Pool 56 → 61 skills; front accel rule in `buildgen.valid`; per-uma HP-out + floor helpers in `mock`; tests pass (10) |
| A2 Mock recalibration (CN 95–97 %) | todo | | | |
| A3 v4 base team | todo | | | |
| A4 Stamina requirement study | todo | | | |
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
- Push status: the repository has no remote. GitHub token in this container is invalid and no
  `uma-race-lab` repo exists under the user's account. Once the user creates an empty private repo,
  attach it with push access and `git push -u origin master`.
