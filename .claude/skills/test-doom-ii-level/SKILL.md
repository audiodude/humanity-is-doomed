---
name: test-doom-ii-level
description: Playtest a DOOM II level in this repo with ViZDoom: route script, wiring run, combat-bot balance runs, screenshots. Use after building or changing a map, or when asked whether a map works or is balanced.
---

Prove the map plays: the intended route works end to end, and a fight through it is survivable with the health and ammo the map provides. The map comes from `build-doom-ii-level`; its design doc (`levels/designs/<module>.md`) says what the route is.

The runner is `scripts/tools/playtest.py`; its docstring is the script language and option reference, and `README.md` "Playtests" shows the commands. ViZDoom comes from `uv run -q --with vizdoom`, never system Python. Run headless (no `--watch`).

## 1. Route script

Write `levels/playtests/<module>.playtest`: the doc's route as `walk`/`open`/`use` steps, with an `expect` after every trigger checking the floor or ceiling it moves, item and secret checks, a `look` + `shot NAME` at the start, each set piece and the exit, and a comment block per section of the route (the fight report uses those as section names).

Done when every door, switch, lift, key, trap trigger and secret on the doc's route, and the exit, has a step and a check, and each place the doc promises a view has a `shot`.

## 2. Wiring run

```sh
uv run -q --with vizdoom scripts/tools/playtest.py <WAD> MAPnn levels/playtests/<module>.playtest --shots /tmp/playtest-shots/<module>
```

Run against the scratch WAD while the map is changing. Fix the map for real failures; fix the script only for script mistakes (an `expect` taken before a slow floor finished).

Done when it reports 0 fails.

## 3. Look

Read every screenshot the run wrote. Check what the doc promises a player sees (the reveal, a goal visible across a gap) actually shows, and nothing looks broken: missing textures, bleeding sectors, a room lit like a corridor.

## 4. Fight runs

Run `--fight` on seeds 1, 2 and 3 (`--seed N`). The bot plays UV (`--skill 4`) unless told otherwise, so skill-specific changes need a run at that skill. Read each report: per-section time, kills, damage, deaths, health, ammo fired; the death list with times; ammo left.

For each place deaths cluster, decide **map** or **bot**, from the footage when the report doesn't settle it:

```sh
uv run -q --with vizdoom scripts/tools/playtest.py <WAD> MAPnn --replay --seed N --video /tmp/<module>-seedN.mp4
```

Then extract frames around the death times (`ffmpeg -ss M:SS -i … -frames:v 1 out.png`) and read them.

- **Map** problems: out of ammo before a fight ends, a start under fire, a trap with no way to fight back, a fall with no way out, sniping across a gap the player can't answer. Fix them in the map (pickups, monster placement, deaf flags, railings, cover) and re-run the wiring run.
- **Bot** problems, the bot's known weak spots: it uses lifts only at scripted `use` steps, so foraging detours back down a lift strand it; it strafes off ledges and stands in damaging floors; its stuck timeout (2 s) is shorter than a lift's wait at the bottom (3 s); it fires at monsters it can't reach. Work around these in the script when they block the run (a waypoint, a `wait`), not by reshaping the map.

Done when all three seeds have been run and read, every death cluster is classified, every map problem is fixed or written down with why it stays, and the wiring run still passes.

## 5. Report

The wiring result (checks, fails), each seed's totals (kills, deaths, ammo left), the death clusters with their map/bot call, the doc targets the map misses, and what a human should look at in dsda-doom: vanilla rendering, and whether it's fun, which none of this measures.
