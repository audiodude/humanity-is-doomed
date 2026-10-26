---
name: doom-test
description: Playtest a DOOM II level in this repo: the build's static balance curve, then ViZDoom route script, wiring run, combat-bot balance runs, screenshots. Use after building or changing a map, or when asked whether a map works or is balanced.
---

Prove the map plays: the intended route works end to end, and a fight through it is survivable with the health and ammo the map provides. The map comes from `doom-build`; its design doc (`levels/designs/<module>.md`) says what the route is.

Balance is answered first from the map itself: `build()` prints a resource curve and exposure warnings along the route (`levels/balance.py`, design and calibration in `docs/balance-metrics.md`), deterministic and in seconds. The fight bot confirms it; it is a weaker player than a person, so where it and the curve disagree, the curve wins unless the footage shows a real map problem.

The runner is `scripts/tools/playtest.py`; its docstring is the script language and option reference, and `README.md` "Playtests" shows the commands. ViZDoom comes from `uv run -q --with vizdoom`, never system Python. Run headless (no `--watch`).

## 1. Route script

Write `levels/playtests/<module>.playtest`: the doc's route as `walk`/`open`/`use` steps, with an `expect` after every trigger checking the floor or ceiling it moves, item and secret checks, a `look` + `shot NAME` at the start, each set piece and the exit, and a comment block per section of the route (the fight report uses those as section names).

Done when every door, switch, lift, key, trap trigger and secret on the doc's route, and the exit, has a step and a check, and each place the doc promises a view has a `shot`.

## 2. Wiring run

```sh
uv run -q --with vizdoom scripts/tools/playtest.py <WAD> MAPnn levels/playtests/<module>.playtest --shots /tmp/playtest-shots/<module>
```

Run against the scratch WAD while the map is changing. Fix the map for real failures; fix the script only for script mistakes (an `expect` taken before a slow floor finished).

The runner plays with ZDoom's strict Doom compatibility, so vanilla rules apply: lines are used from their front side only, pressing use stops at the first line with any action (a walk-over trigger just in front of a door or switch blocks it: a map bug, move the trigger), and monsters are infinitely tall.

Done when it reports 0 fails.

## 3. Look

Read every screenshot the run wrote. Check what the doc promises a player sees (the reveal, a goal visible across a gap) actually shows, and nothing looks broken: missing textures, bleeding sectors, a room lit like a corridor. Check the walls look like the doc's materials table: each area reads as one place, and where two materials meet in view there is a trim or a reason. A wall that looks picked at random goes back to `doom-build`.

## 4. Static balance

Build the map (the `doom-build` command) and read what it prints after the measurement table. Both need `DOOM2_WAD` set (from `.env`; a fresh worktree has none, so `set -a; . <main checkout>/.env; set +a`): without it the build skips them with a warning.

- **Resource curve**, one row per leg of the critical path (start → each required key or trigger → exit), at UV, pistol start, ammo counted as damage. Columns: path length, engaged monster HP, then `ammo left` and `ratio` (cumulative supply / engaged HP) on two curves, then `health` and the leg's long-range hitscan.
  - *thorough*: every reachable item, secrets and side rooms included. Negative `ammo left` (`!! short even taking everything`) means fights the map's items can't pay for.
  - *detour* (D=1024): only items within a 1024-unit round trip off the path, no secrets. This is the normal player. `!! detour` marks a leg below the id maps' 10th percentile (0.147 DOOM II, 0.402 Ultimate): the ammo is there but off the way.
  - *health*: health left if fights cost what the median id map's route affords (17.3 per 1000 HP).
- **Side rooms**: monsters never engaged by the route, with their HP and the ammo and health there. Listed, not warned; id's maps often have closets that cost more than they hold.
- **Traps**: each trigger on the route, the HP it releases against ammo carried then (an optimistic figure), the nearest monster's distance, and `no way back` when the retreat is gone.
- **Warnings**: short on either curve, long-range hitscan above the id maps' 90th percentile (88.4/s DOOM II, 46/s Ultimate), a trap releasing more HP than the ammo in hand, a start under fire (a monster that can shoot the start and faces it, or stands within 64 of it).
- Four measures join the measurement table with id's quartiles: lowest detour ratio, lowest thorough ammo left / HP, hitscan peak, health per 1000 HP the route affords.

Nothing here is an error: a quarter of the DOOM II maps run short on the thorough curve and 9 of 32 have a start under fire. Judge each warning against the doc's targets and the map's intent. Fix starvation near the route with pickups on the way, not ammo in a side room; fix sniping with cover or by moving the hitscanner within 768; fix a start under fire by turning the monster, adding a wall or moving it to a higher skill.

Done when every warning is fixed or written into the doc's Targets section with why it stays, and the detour curve's low point is no lower than the doc's ammo target allows.

## 5. Fight runs

Run `--fight` on seeds 1, 2 and 3 (`--seed N`); they're independent, so run them in parallel. The bot plays UV (`--skill 4`) unless told otherwise, so skill-specific changes need a run at that skill. A fight always finishes: a step the bot gets stuck on, or 3 deaths within 128 units and 30 s (a loop), is listed as skipped and the bot is warped to where the step was going, and `--max-time` (default 15 game minutes) caps the run. Exit status 1 means it hit the cap; deaths and skipped steps are in the report, not the exit status.

Read each report: per-section time, kills, damage, deaths, health, ammo fired; the death list with times and labels; the skipped steps; ammo left. Each death is labelled when it happens:

| Label | Means | Usually |
|---|---|---|
| `starved` | no ammo for any weapon but the pistol | map if the curve's detour ratio for that part of the route is low; bot waste if it had ammo to spare there |
| `stuck` | moved under 32 units in the 2 s before | bot |
| `hazard` | on a damaging floor | bot |
| `unseen` | no monster on screen in the last second | map: an ambush the player can't see |
| `combat` | anything else | read the numbers and the footage |

Script sections don't map onto curve legs automatically: match a `starved` death's place to the leg whose path covers it by hand.

For each place deaths cluster, and each skipped step, decide **map** or **bot**, from the labels and the curve first, and from the footage when they don't settle it:

```sh
uv run -q --with vizdoom scripts/tools/playtest.py <WAD> MAPnn --replay --seed N --video /tmp/<module>-seedN.mp4
```

Then extract frames around the death times (`ffmpeg -ss M:SS -i … -frames:v 1 out.png`) and read them.

- **Map** problems: out of ammo before a fight ends (and the curve agrees), a start under fire, a trap with no way to fight back, a fall with no way out, an unseen ambush, sniping across a gap. Fix them in the map (pickups, monster placement, deaf flags, railings, cover), then rebuild and re-read the curve and re-run the wiring run.
- **Bot** problems, the bot's known weak spots: it uses lifts only at scripted `use` steps, so foraging detours back down a lift strand it; it strafes off ledges and stands in damaging floors; its stuck timeout (2 s) is shorter than a lift's wait at the bottom (3 s); it fires at monsters it can't reach (it gives up after 5 s, and won't fire bullets past 768 units). Stuck steps and loops no longer block the run, so leave the script alone unless they skip so much of the route that a section goes untested; then add a waypoint or a `wait`, never reshape the map for the bot.

Done when all three seeds have been run and read, every death cluster and skipped step is classified, every map problem is fixed or written down with why it stays, and the wiring run still passes.

## 6. Report

The wiring result (checks, fails), the curve's low points (lowest detour ratio and the leg, any leg short on the thorough curve, health at the exit) and every static warning with its fix or reason, each seed's totals (kills, deaths by label, skipped steps, ammo left), the death clusters with their map/bot call, the doc targets the map misses, and what a human should look at in dsda-doom: vanilla rendering, and whether it's fun, which none of this measures.
