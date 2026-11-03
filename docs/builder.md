# The level builder

`levels/` is a DOOM and DOOM II level compiler. You describe a map as a Python module of plain data: rooms as polygons with floor and ceiling heights, plus doors, lifts, stairs, switches, monsters and pickups. The builder works out the linedefs, sidedefs and texture alignment, checks that the map is actually playable, and writes it into a WAD with a top-down preview. All nine maps in `NUKAGE.WAD` came out of it, and the [decompiler](#decompiling-existing-maps) turns any Doom-format map back into this form.

## Building a map

Run from the repo root:

```sh
python3 -m levels nukage_outskirts         # check, then write MAP01 into wads/NUKAGE.WAD
python3 -m levels nukage_crossing          # same for MAP02
python3 -m levels nukage_core              # same for MAP03
python3 -m levels nukage_divided            # same for MAP04
python3 -m levels nukage_drain              # same for MAP05
python3 -m levels nukage_undercurrent       # same for MAP06
python3 -m levels nukage_storage            # same for MAP07
python3 -m levels nukage_lockdown           # same for MAP08
python3 -m levels nukage_meltdown           # same for MAP09
python3 -m levels nukage_outskirts --check # check only
```

From Python: `from levels import build, nukage_outskirts; build(nukage_outskirts)`. A build replaces only its own map slot and `UMAPINFO` entry, so several levels can share one WAD.

Requirements:
- **Python 3.10+**, standard library only.
- **ZDBSP** to build nodes, blockmap and reject. The default is the copy bundled with [Ultimate Doom Builder](https://github.com/UltimateDoomBuilder/UltimateDoomBuilder), at `/usr/lib/ultimate-doom-builder/Compilers/Nodebuilders/zdbsp` (Arch: `chaotic-aur/ultimate-doom-builder-git`), then `zdbsp` on `PATH`. Use `--zdbsp-path PATH` (or `build(..., zdbsp=PATH)`) for any other ZDBSP binary.
- **The IWADs** for the texture checks, the reach checks' texture heights and the measurements. Copy `.env.example` to `.env` and set `DOOM2_WAD` (and `DOOM_WAD`, Ultimate Doom, for `ExMy` maps) to their paths; a variable set in the environment overrides `.env`. Without them the texture checks are skipped with a warning.

## What every build checks

Findings come in two kinds. **Playability** findings fail every build:
- Geometry: lines only meet at shared vertices. A sector outline that crosses itself, or sectors and free lines that cut through each other, is an error. A sector standing free inside another (a pedestal, a crate, a pool) is cut out of it automatically; one touching the other's outline has to be listed as a hole by hand.
- Every thing is inside a sector with room for its height (a closed door has none), clear of walls, bars, fences and steps it can't climb, and not overlapping another monster or player on a skill they share. Thing types must exist in the map's game.
- Progression, worked out by the reach model in `levels/reach.py` on the built map, the way the engine does it: every vanilla line action (doors, floors, ceilings, lifts, stairs, donuts, teleporters, exits, boss deaths, and a `UMAPINFO` string's `bossaction`s in place of the slot's own boss deaths), keys, and the height each moving sector can reach. A switch can be used across a thin sector within use range, but not through a closed door. The exit, every `MUST_REACH` sector and every secret must be reachable from the player start.
- 100% kills: every monster can either be reached or walk (or fly) to somewhere the player can go, by monster rules: no keys, only plain use doors, blocked by monster-blocking lines. A sniper the player can only shoot at fails this too.
- No softlocks: from every damaging floor the player can get onto, the exit can still be reached.
- Every texture and flat exists in the IWAD (plus the module's `RESOURCES`), and so does a `UMAPINFO` `skytexture`.

**Style** findings fail our own maps; in an imported map (`IMPORTED = True`) they are warnings:
- Damaging floors sit lower than every neighbouring floor that isn't damaging.
- Pictures such as switches and door faces fit their wall exactly. Bars and fences can't use textures built from overlapping patches, which vanilla draws as garbage on two-sided lines (the medusa effect).
- The exit can be reached without a running jump. Jumps only count when the exit can't be reached any other way.

Textures vanilla can't tile cleanly, and line actions or thing types that aren't vanilla, get a warning. So does anything the engine does by map slot that the map doesn't account for (`levels/checks.py` `check_slot`, from id's source and the UMAPINFO spec):
- DOOM II's own text screens after MAP06, MAP11, MAP20 and MAP30, and after the MAP15 and MAP31 secret exits, when the map's `UMAPINFO` has no `intertext` (`intertextsecret`) of its own. `intertext = clear` turns one off; it has to be a string body, because the dict form quotes `"clear"` and ports show the word.
- A secret exit on a slot with no secret level. Without UMAPINFO, DOOM II only routes MAP15 and MAP31 (a secret exit elsewhere reloads the map), and DOOM sends every secret exit to ExM9, which returns to the map after id's own secret exit. With a `UMAPINFO` entry, a secret exit with no `nextsecret` goes where the normal exit does.
- Boss deaths. The slot's built-in rule (E1M8, E2M8, E3M8, E4M6, E4M8, MAP07) or a `bossaction` in its place: a `bossaction` that drops a built-in rule the map's tagged sectors relied on, a built-in rule on a tag a line also uses, E2M8/E3M8 ending the level on the boss's death when the map has its own exit, and a boss death that is the only way to move its sectors (or end the level) while the monster is missing on some skill. The reach model plays UV only, so that last case isn't caught elsewhere.

A module can list the playability findings and warnings it accepts in `KNOWN_ISSUES`: the build fails only on findings not on the list, doesn't print listed warnings, and says `fixed:` for listed entries that no longer occur.

Every build also prints:
- A balance report for each skill: monster health against ammo damage, health and armor.
- The sky, for a map that shows one, and where it comes from: the `UMAPINFO` `skytexture`, or the slot's default (DOOM II: `SKY1` for MAP01–MAP11, `SKY2` for MAP12–MAP20, `SKY3` from MAP21; DOOM: one per episode). Moving a map across MAP11/MAP12 or MAP20/MAP21 changes its sky unless it sets one. Vanilla `doom2.exe` only sets the sky when a game starts, so there it never changes in play.
- The research measurements (`levels/measure.py`, using `scripts/metrics/`): floor heights, lighting, texture variety, border textures, symmetry, optional area, secrets, monster mix, ammo and health, skill ratios and distance to the nearest monster, each beside the median and interquartile range of id's maps for that game and flagged `below` or `above` it. Then the balance along the route (`levels/balance.py`, design in `docs/balance-metrics.md`), with no bot: the reach model's critical path split into legs (one per required key or trigger), the monsters each leg engages (on the path, able to walk to it, or able to shoot it from within 1024 units), and two ammo curves leg by leg with carry caps: *thorough* (every reachable item) and *detour* (items within a 1024-unit round trip off the path, secrets excluded), plus health at the median id map's cost per monster HP, the long-range hitscan peak, side rooms, the monster HP each trap on the route releases against the ammo in hand, and monsters that can shoot the start. These are warnings judged against the id maps, never errors: a quarter of id's maps run short on the thorough curve too. Rule-1 slips (a floor texture change with no height change) are listed by sector pair, and rule-2 seams (two wall textures meeting in one plane with no border texture such as `SUPPORT3`, `DOORTRAK` or `LITE5` between them) by sector, texture pair and one junction's coordinates. This takes a couple of seconds.
- A top-down SVG preview, `wads/<WAD stem>-<MAP>.svg`: sectors shaded by floor height, special lines in red, bars and fences dashed, monsters by skill, pickups and keys.

A failed check prints `ERROR:` lines and stops the build before the WAD is touched. The preview is still written, so you can see what went wrong.

## Writing a level

A level is a module of plain data: `MAP`, `WAD`, `SECTORS`, `THINGS`, `SPECIAL_BETWEEN`, `SPECIAL_WALLS`, `FREE_LINES`, `MUST_REACH`, … To start a new one, copy `levels/nukage_junction.py`. `MAP` also picks the game: `E1M1`-style slots are Ultimate Doom, `MAP01`-style DOOM II. `WAD` may name a subdirectory of `wads/`.

Sectors are polygons: outer loops, holes that other sectors fill, and solid `pillars`. Whether a loop is an outer loop or a hole follows from nesting, so one sector can be several separate areas, as in many id maps. A hole's edges with no sector across become walls; a hole no sector touches at all is an error (make it a pillar). Edges that two sectors share become two-sided lines; the rest become walls. Texture x offsets follow each sector's outline, so patterns run continuously along a wall (`X_OFFSETS = "zero"` writes 0 instead, as id mostly did), and the wall above or below an opening uses the room's own texture. The exception is secret doors (`SECRET_DOORS`): their faces are shifted off the wall pattern by `SECRET_HINT` (16 across, 8 down) as the classic clue. Pass a `{name: (x, y)}` dict instead to pick offsets per door, with `(0, 0)` for a seamless door.

Lines that aren't sector edges go in `FREE_LINES`, keyed by their two endpoints: `{((384, 32), (384, 480)): Special(W1_DOOR_OPEN, 5)}` is a walk-over trigger across the middle of a room, so you don't have to split the room into two sectors for it. Give a `Special` a `texture` to hang bars or a fence: on a free line it stands inside one room (`Special(texture="MIDGRATE")`). In `SPECIAL_BETWEEN` it fills every opening between two sectors, such as bars between a cage and the room around it. These lines are impassable, and the texture stands on the floor. A free fence doesn't split its sector for the progression check, so to wall off part of a room with bars, make that part its own sector.

Helpers in `levels/model.py` build the common shapes. `doorway()` makes a door with optional recesses, plus its use action. Each recess is dressed for the room it opens into: `alcove_wall`/`alcove_flat`/`alcove_ctex` for the near one, `far_wall`/`far_flat`/`far_ctex` for the far one (each defaulting to the near one's), and `door()`'s `flat` sets the threshold, so floors can match the rooms (Romero's rule 1: floor texture changes only with a height change). A door face is a picture that must fit its wall, so a room taller than the face (128 for `BIGDOOR*`, 72 for `EXITDOOR`) needs a recess that tall on its side of the door: `alcove` before it, `far_alcove` after it. The doorway runs `alcove + thickness + far_alcove` from its wall. `stairs()` makes a run of steps. `lift()` makes a lift used (`SR_LIFT`) from below and from its top; `walk_on=True` makes it lower when walked onto from the top instead (`WR_LIFT`), which monsters can set off and ride too.

There are helpers for the rooms most maps repeat, sized so they pass the texture checks:
- `closet()`: a monster closet behind a door disguised as the wall, opened only by its tag.
- `pedestal()`: a glowing, metal-sided pedestal for a key or item. Stand it clear of the walls and the build cuts it out of the room. Put a W1 trigger on its edge in `SPECIAL_BETWEEN` to spring a trap when the item is taken.
- `switch_niche()`: a recess whose back wall is a switch, sized to the switch picture (64 × 128, or 32 × 72 for `SW1EXIT`). It returns the sector and the `SPECIAL_WALLS` entry for the switch. Make it deep (a booth) to fire a W1 trigger on its entrance just before the switch is used.
- `lit_ledge()`: a brightly lit ledge with an unlit strip against the wall behind it, so the wall isn't lit up too.
- `window()`: an opening between rooms. Walking monsters can't climb a sill more than 24 above their floor, and fliers need at least 56 of height.

Floors can move both ways for the progression check: the lowering actions (`S1_FLOOR_LOWEST` and kin) drop a tagged floor to its lowest neighbour, and the raise actions lift it to the next higher neighbouring floor, so a rising bridge stops level with the nearest higher floor around it. The raise-and-change actions (`S1_RAISE_CHANGE` and kin) take the floor texture of the trigger line's front sector and clear the sector's special, which dries a walkway raised out of nukage (MAP05 does this), but they move at 0.5 units a tic: 96 units take 5.5 s. The fast raises (`S1_FLOOR_NEXT_FAST` and kin) move at 4 units a tic and keep the floor's texture and special, so use them for bridges out of a pit or the dark.

Anything the builder infers can be overridden line by line in `OVERRIDES`, keyed by a line's two endpoints with its front on the right going from the first to the second: `{((1088, -3648), (1024, -3648)): Line(flags=ML_BLOCKING | ML_BLOCKMONSTERS, front=Side(mid="COMPSTA2", x=16))}`. Only the fields given replace the builder's choice (a picture such as a switch or sign set without `x` starts at x offset 0; a new `lower` on a step whose riser the builder unpegged to line up with the room's walls is pegged to the step's top again, so a switch on a console face starts at the console's top, unless the override gives `flags`); a key that matches no line is an error. Decompiled maps use this for every difference from what the builder would make.

`Thing` skills are any of `e`, `m`, `h`, plus `a` for ambush (deaf) and `n` for multiplayer only; `extra` holds other flag bits. `RESOURCES` lists PWADs whose textures, flats and patches the checks and measurements load after the IWAD (for remixes of community maps; they aren't copied into the built WAD).

## Agent skills

Three skills in `.omp/skills/` (linked as `.claude/skills/` for Claude Code) take an agent through a new map in order, each ending where the next begins:

- `doom-design`: pitch five structurally different concepts, pick one, and write a design doc to `levels/designs/<module>.md` (route, sketch, materials, secrets, measurement targets).
- `doom-build`: turn the doc into a level module that builds clean and matches it, with the builder's known gotchas.
- `doom-test`: route script, wiring run, screenshots, and combat-bot runs on three seeds, with each death cluster called as a map or bot problem.

They came out of four timed rounds of agents building maps from scratch: the six maps in `SPEEDY1.WAD`, built from feature checklists, all came out as the same hub with a wing per key, while the six in `SPEEDY2.WAD`, each built around a layout idea, didn't.

Agents choose textures by name unless they can see them, which is how a map ends up a collage. `scripts/tools/texture_sheets.py` renders the IWAD's wall textures (grouped into families by name, border textures labelled in yellow) and flats onto contact sheets in `/tmp/texture-sheets/<iwad>/`, with an `index.txt` of which sheet holds which family. The design skill has the agent look at them before writing the doc's materials plan:

```sh
uv run --with pillow scripts/tools/texture_sheets.py            # DOOM2_WAD from .env; --iwad for another
```

## Code layout

- `levels/model.py`: the dataclasses levels are written in (`Sector`, `Special`, `Thing`, `Line`, `Side`) and the shape helpers.
- `levels/mapgen.py`: `build()` and `compile_level()`, which turn sectors into lines and sides and place textures. Its docstring describes the level format.
- `levels/checks.py`: the checks and the balance report. `levels/reach.py`: the reach model, shared with the research scripts. `levels/measure.py`: the sector-overlap check, rule-1 slips and the research measurements. `levels/balance.py`: the resource curve and exposure checks along the route.
- `levels/decompile.py`: the decompiler. `levels/wadmap.py`: reads maps from WADs.
- `levels/preview.py`: the SVG preview. `levels/wad.py`: WAD reading and writing, IWAD paths from `.env`.
- `levels/doom2.py`: every DOOM and DOOM II thing type, monster sizes and health, pickups, line actions and sector specials.
- `tests/`: `uv run --with pytest pytest`. Tests that need an IWAD skip when it isn't set.

## Decompiling existing maps

`levels/decompile.py` turns maps from any Doom-format WAD into level modules, so id's maps can serve as worked examples, existing maps can be remixed in Python, and every check and measurement above can run on any map:

```sh
python3 -m levels.decompile doom2 MAP01        # from the DOOM2_WAD in .env -> levels/imported/doom2_map01.py
python3 -m levels.decompile doom               # every map in DOOM_WAD
python3 -m levels.decompile wads/NUKAGE.WAD    # any PWAD
python3 -m levels imported.doom2_map01 --check # check and measure it; without --check, build it into wads/imported/
python3 -m levels.decompile doom2 --verify     # rebuild each map and compare it with the original
```

Modules go to `levels/imported/` and their builds to `wads/imported/`. Both are gitignored: id's map data is never committed, so make them from your own IWADs.

A decompiled module is minimal-diff: what the builder would infer anyway (sector outlines, wall and step textures, doors, lifts, door actions, `SPECIAL_BETWEEN`, `SPECIAL_WALLS`) is ordinary module data, and only the rest is written as `OVERRIDES`. Sectors are named by role and original number (`room_5`, `door_12`, `lift_40`, `secret_83`, `nukage_7`), matching the sector numbers walkthroughs use. The docstring gives the map's title, monsters per skill, keys, secrets and check findings, and, if `research/data/` is there, its designers, reception and the measurements furthest from the medians. The original's playability findings become its `KNOWN_ISSUES`, and `IMPORTED = True` makes style findings warnings, so an unchanged map builds and a remix can't quietly add new problems.

Building a decompiled module gives back the same map: the same sectors, things, actions, flags, textures and offsets; only line order and where a straight wall is split into lines may differ. `--verify` proves it for each map and exits 1 on any difference. Sectors whose outlines don't close in the original (16 of id's 68 maps have some) are repaired with the fewest edits that close them, when that set of edits is unique, each noted in a `# repaired:` comment; otherwise the map is refused. Hexen-format and UDMF maps are refused.

## Playtests
`levels/playtests/<module>.playtest` scripts walk each map's intended route: doors, switches, lifts, key traps, secrets and the exit, checking floor and ceiling heights after each trigger. The runner, `scripts/tools/playtest.py`, plays them in [ViZDoom](https://vizdoom.farama.org/), a ZDoom-based engine packaged as a Python library. It drives the player with real inputs as fast as the machine runs the game, with god mode on and no window, so a whole route takes 4–10 seconds. Screenshots go to `/tmp/playtest-shots/<MAP>/`. The IWAD is `DOOM2_WAD` from `.env`; override with `--iwad` (for example with your `DOOM.WAD` for a decompiled `ExMy` map).

ViZDoom comes from Michał Kempka, Marek Wydmuch, Grzegorz Runc, Jakub Toczek and Wojciech Jaśkowski ([paper](https://arxiv.org/abs/1605.02097)), is maintained by the [Farama Foundation](https://github.com/Farama-Foundation/ViZDoom), and is built on [ZDoom](https://zdoom.org). It was made for research into AI that learns to play Doom from the screen, and the same hooks make playtesting simple. Python advances the game one tic at a time, so the runner steers like a player and checks as it goes; the GZDoom runner before it compiled each script to ZScript and played it in real time on a hidden X display. The runner reads the game's state straight from the engine: the player's position, health and ammo, every sector's floor and ceiling (`expect floor`, `expect ceil`), and every monster and item, which is how `expect has` sees a key taken and how the `--fight` bot finds monsters and pickups without any training. Saves give `checkpoint`, console commands give god mode, `give`, `killall` and `teleport`, seeds make a fight repeatable, recordings with the screen and sound buffers give `--replay` and `--video`, and ZDoom's compatibility settings give the vanilla rules described below.

ViZDoom isn't needed to build maps, so it isn't a requirement of the builder. `uv run --with vizdoom` fetches it into a cached environment the first time:

```sh
uv run --with vizdoom scripts/tools/playtest.py wads/NUKAGE.WAD MAP02 levels/playtests/nukage_crossing.playtest
uv run --with vizdoom scripts/tools/playtest.py wads/NUKAGE.WAD MAP05 levels/playtests/nukage_drain.playtest --from pump3
python3 scripts/tools/playtest.py wads/NUKAGE.WAD MAP02 --describe   # start, keys, special lines
```

Scripts say where to go, not how to get there: `walk X Y` finds its own way round walls, solid things, steps too high to climb and closed doors, avoiding damaging floors when it can, and `open` and `use` walk up to their line first. A script can mark `checkpoint NAME` steps; `--from NAME` resumes from the save the last full run made there, as long as the WAD, map, skill and every step before it are unchanged. The script language is in the runner's docstring.

With `--fight` the same scripts test balance instead: god mode is off and a bot fights its way along the route, picking up health and ammo when it's low. Each death is counted, with where, when and a label (`hazard`, `starved`, `unseen`, `stuck` or `combat`), and the run carries on. A step the bot gets stuck on, or 3 deaths in one spot within 30 s, is listed as skipped and the bot is warped to where the step was going, and `--max-time` (default 15 game minutes) caps the run, so a fight always finishes. The build's resource curve answers most balance questions faster; use fights to confirm it. It reports each section of the route with time, kills, damage taken, deaths, health and ammo fired. Runs are recorded: `--watch` shows one live in a window, `--replay` plays the last one back (pass the same `--seed`), and `--replay --video FILE.mp4` renders it with sound (`--hd` for 1080p). The bot is a weaker player than a person and its results vary with `--seed`, so try several seeds and check the footage before blaming the map.

```sh
uv run --with vizdoom scripts/tools/playtest.py wads/NUKAGE.WAD MAP03 levels/playtests/nukage_core.playtest --fight --seed 2
uv run --with vizdoom scripts/tools/playtest.py wads/NUKAGE.WAD MAP03 --replay --seed 2                  # watch it
uv run --with vizdoom scripts/tools/playtest.py wads/NUKAGE.WAD MAP03 --replay --seed 2 --video run.mp4  # needs ffmpeg
```

The runner turns on ZDoom's strict Doom compatibility, so a pass shows the map's wiring works under vanilla rules as far as ZDoom can follow them: the player can only use a line from its front side, pressing use stops at the first line with an action (so a walk-over trigger just in front of a door or switch blocks it), and monsters are infinitely tall. Vanilla rendering limits and the feel of the map still need a playthrough in dsda-doom.
