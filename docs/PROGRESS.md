# Progress — step checklist for docs/MASTER_PROMPT.md

Status values: `todo`, `running` (a job is in flight — check its run folder before restarting),
`done`, `blocked` (say why). Update this file in every commit checkpoint.

| Step | Status | Run folder | Commit | Key result |
| --- | --- | --- | --- | --- |
| A0 Housekeeping (context, changelog, master prompt, archive, push) | done | — | see git log | Context saved and pushed to github.com/ghadasd2/uma-race-lab (branch master) |
| A1 Rules and pool | done | — | v4 A1 | Pool 56 → 61 skills; front accel rule in `buildgen.valid`; per-uma HP-out + floor helpers in `mock`; tests pass (10) |
| A2 Mock recalibration (CN 95–97 %) | done | runs/20261120-224122-loh-v4-a2-calibrate | v4 A2 | Shift 150 (incl. stamina) + 2 extra drops → CN 96.00 % (8,750 races); v3 champion 96.29 % but fails HP floor (Kitasan 3.15 %, Ines 4.41 %) |
| A3 v4 base team | done | runs/20261120-225351-loh-v4-a3-base | v4 A3 | Kitasan sta 1200 / spd 1380, Ines sta 1150 / spd 1380, Neo unchanged; HP-out 1.17 / 1.60 / 1.63 %; team 96.17 % |
| A4 Stamina requirement study | done | runs/20261120-225551-loh-v4-a4-stamina | v4 A4 | Floor-meeting stamina: Kitasan 1200 (no drain set feasible ≤ 1350); Ines 1100 / RS 1150 / MD 1200; Neo 1000 / RS, FT, KG 1100 / RS+FT, RS+KG 1200 (best: RS+KG +0.99 pp) |
| A5 Stat exchange rates | done | runs/20261120-232411-loh-v4-a5-exchange | v4 A5 | Weak field shrinks rates: speed 0.15–0.22 pp/100 cost; power & wit above 1200 now 0.16–0.49 (≥ speed); guts ≈ 0; Ines at 1150 sta is on the floor (1.95 % here) → A7 starts with Ines 1200 |
| A6 Skill values + front accel test | done | runs/20261120-234112-loh-v4-a6-skill-values | v4 A6 | Keep SP (Kitasan) and SP + TtL (Ines): every other legal accel set loses 0.4–0.9 pp; Ines RS: Speed +0.68 and Downhill Speedster +0.54; Neo Keep Going! +1.09 / Full Throttle +0.84 (need 1100 stamina); Killer Tunes on Ines +0.62 |
| A7 Constrained build search | done | runs/20261121-002043-loh-v4-a7-search | v4 A7 | 8 gens; only gen 0 accepted (Kitasan + Hesitant Front Runners +0.43 [0.13, 0.74]); champion → `data/loh/my_team_v4_champion.json`; drain sets under the real cap ≈ 0 (Neo RS + KG @ 1200 −0.01) |
| A8 Validation | done | runs/20261121-014012-loh-v4-a8-validate | v4 A8 | 17,500 races: champion 96.31 % (HP floor ok), base 96.17 % (Ines 1.76 % fail), v3 champion 96.22 % (fail), CN 96.05 %; champion − base +0.14 [−0.07, 0.36] |
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
