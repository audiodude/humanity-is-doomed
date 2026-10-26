# Humanity is Doomed

> *We interrupt this program to bring you a special bulletin.*
>
> Ladies and gentlemen, on the evening of October 19th, at ten minutes to seven, Pacific time, a single sentence was typed into a terminal in an ordinary American home: **"Make me a moderately complex, medium difficulty DOOM II level."**
>
> The thing that answered was not a level designer. Within hours it had written a Python script that placed every wall, door and imp of a nukage-flooded base by hand, coordinate by coordinate, and sealed them inside a WAD. Our correspondent entered the structure alone and returned with a brief report: *"I played through the level and it works!"* We now believe those were the last calm words spoken on the subject.
>
> **Bulletin.** The machine was instructed to "clean up the script. Use dataclasses." It did not stop at cleaning. The script has become a general-purpose generator, and a level is now nothing more than a list of rooms, doors, lifts and monsters. It builds doorways, staircases and lifts on command. It draws maps of its own work. It checks that no monster is buried in a wall or in another monster, that every key can be reached, that every texture exists. When it was reminded that a secret door must sit a few pixels out of line with the wall around it, the oldest clue in the game, it learned that too. It has not forgotten.
>
> **Bulletin.** The machine has turned to study. Its agents have fanned out across designer interviews, books, hours of video and three decades of player opinion. They have measured all 68 of id Software's original maps down to the last step and light level, scored each one by how much players love it, and asked, with statistics, why. It now has a theory of fun.
>
> **Bulletin.** A second structure has appeared. It is called Nukage Crossing. Witnesses describe a sluice gate that sinks into a canal of toxic waste to become a bridge, and a pack of demons that charges across it the moment it settles. There are four secrets. Before any human set foot inside, the machine walked it itself: invulnerable, in a window no one could see, opening every door and throwing every switch. It reports nineteen checks out of nineteen passed.
>
> **Bulletin.** A third structure. It is called Nukage Core: a reactor rising out of a moat of waste, its exit in the crown on top, visible from the first window. The way up spirals around it, gallery by gallery, past a room that goes black when you take its key and the first mancubus. The machine walked this one too, twenty-six checks of twenty-six.
>
> Ladies and gentlemen, I must tell you plainly: the demons were never the danger. A demon can be shotgunned. The danger is the thing that *summons* them, from a single sentence, tirelessly, and gets better at it every time. Humanity is—
>
> *[transmission ends]*

## Included WAD - NUKAGE.WAD

`wads/NUKAGE.WAD` holds five generated maps for DOOM II: MAP01, [Nukage Junction](#nukage-junction-nukage_junction), MAP02, [Nukage Crossing](#nukage-crossing-nukage_crossing), MAP03, [Nukage Core](#nukage-core-nukage_core), MAP04, [Nukage Divided](#nukage-divided-nukage_divided), and MAP05, [Nukage Drain](#nukage-drain-nukage_drain). It needs `doom2.wad` and works in the DOOM + DOOM II (2024) re-release as well as in source ports such as dsda-doom (`dsda-doom -iwad doom2 -file wads/NUKAGE.WAD`, add `-warp 2` and so on for the later maps) and GZDoom. Top-down maps of the levels are in `wads/NUKAGE-MAP01.svg`, `wads/NUKAGE-MAP02.svg`, `wads/NUKAGE-MAP03.svg`, `wads/NUKAGE-MAP04.svg` and `wads/NUKAGE-MAP05.svg`. Routes, secrets and set pieces are in [SPOILERS.md](SPOILERS.md).

### Nukage Junction (`nukage_junction`)
A medium-difficulty MAP01 replacement: 46 sectors, 24/45/52 monsters on easy/medium/hard, one secret.

The `UMAPINFO` lump names the level for ports that read it (dsda-doom, GZDoom). Vanilla DOOM II still calls it "entryway".

### Nukage Crossing (`nukage_crossing`)
MAP02, designed from the [research](#research-what-makes-doom-levels-fun) below: 99 sectors, 21/43/57 monsters on easy/medium/hard, four secrets.

Measured with the research scripts against the DOOM II maps (median in brackets):

| Measure | MAP02 | DOOM II median |
|---|---|---|
| Rule-1 flat changes without a height change | 1% | 3% |
| Distinct floor heights | 22 | 23 |
| Light-effect sectors | 11 | 9 |
| UV ammo per monster HP (pistol start) | 2.1 | 1.8 |
| Health per 1000 monster HP | 58 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.37 / 0.75 | 0.33 / 0.70 |
| Deaf monsters | 37% | 42% |
| Nearest monster to the start | 487 | 300 |

No monster can see the start window. Whole-map symmetry (0.82) is above the id range, because the two banks mirror each other across the canal; they are told apart by their materials and landmarks.

### Nukage Core (`nukage_core`)
MAP03, also designed from the research: 111 sectors, 27/53/73 monsters on easy/medium/hard, five secrets. It introduces the mancubus.

A reactor core stands in a nukage moat, with the exit in the crown on top; you see it from the start and climb around it to get there.

Measured with the research scripts against the DOOM II maps:

| Measure | MAP03 | DOOM II median |
|---|---|---|
| Rule-1 flat changes without a height change | 0% | 3% |
| Distinct floor heights | 29 | 23 |
| Light-effect sectors | 10 | 9 |
| Optional share of the reachable area | 40% | 50% |
| Heavy-monster share (UV) | 15% | 10% |
| UV ammo per monster HP (pistol start) | 2.7 | 1.8 |
| Health per 1000 monster HP | 38 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.37 / 0.73 | 0.33 / 0.70 |
| Deaf monsters | 48% | 42% |
| Nearest monster to the start | 353 | 300 |
| Whole-map symmetry | 0.62 | 0.54 |

### Nukage Divided (`nukage_divided`)
MAP04: 112 sectors, 23/43/56 monsters on easy/medium/hard, four secrets, and the first barons.

You leave the start room facing a wall that is half lava, half blue computer screens: a red furnace wing on one side, a blue cooling wing on the other. The wings never meet, and each ends at its own key beside a locked arena door of the other colour, with the other key in sight across a nukage pit.

| Measure | MAP04 | DOOM II median |
|---|---|---|
| Rule-1 flat changes without a height change | 2% | 3% |
| Distinct floor heights | 23 | 23 |
| Light SD / light-effect sectors | 39 / 11 | 23 / 9 |
| Most-used wall texture | 26% | 30% |
| UV ammo per monster HP (pistol start) | 1.8 | 1.8 |
| Health per 1000 monster HP | 36 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.41 / 0.77 | 0.33 / 0.70 |
| Nearest monster to the start | 563 | 300 |
| Whole-map symmetry | 0.71 | 0.54 |

Symmetry is high because the two wings mirror each other's footprint around the fork and the pit; their materials, lighting and monsters are opposites.

### Nukage Drain (`nukage_drain`)
MAP05: 82 sectors, 24/43/59 monsters on easy/medium/hard, four secrets, and the first revenants.

You start on the only dry catwalk of a reservoir full of nukage, with the exit vault standing in the middle. Each of three pump houses has a switch beside an opening onto the reservoir: throw it and watch the next walkway rise out of the sludge to take you onward, while whatever was waiting inside the vault's pillar comes out at you.

| Measure | MAP05 | DOOM II median |
|---|---|---|
| Rule-1 flat changes without a height change | 0% | 3% |
| Distinct floor heights | 13 | 23 |
| Light SD / light-effect sectors | 24 / 9 | 23 / 9 |
| Optional share of the reachable area | 36% | 50% |
| UV ammo per monster HP (pistol start) | 1.9 | 1.8 |
| Health per 1000 monster HP | 35 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.41 / 0.73 | 0.33 / 0.70 |
| Nearest monster to the start | 697 | 300 |
| Whole-map symmetry | 0.64 | 0.54 |

It has fewer floor heights than most id maps because the reservoir is one flat pool; symmetry is high because it's a square reservoir with a pump house off each side.

## The level builder

`levels/` is a DOOM and DOOM II level compiler. You describe a map as a Python module of plain data: rooms as polygons with floor and ceiling heights, plus doors, lifts, stairs, switches, monsters and pickups. The builder works out the linedefs, sidedefs and texture alignment, checks that the map is actually playable, and writes it into a WAD with a top-down preview. All five maps in `NUKAGE.WAD` came out of it, and the [decompiler](#decompiling-existing-maps) turns any Doom-format map back into this form.

### Building a map

Run from the repo root:

```sh
python3 -m levels nukage_junction          # check, then write MAP01 into wads/NUKAGE.WAD
python3 -m levels nukage_crossing          # same for MAP02
python3 -m levels nukage_core              # same for MAP03
python3 -m levels nukage_divided            # same for MAP04
python3 -m levels nukage_drain              # same for MAP05
python3 -m levels nukage_junction --check  # check only
```

From Python: `from levels import build, nukage_junction; build(nukage_junction)`. A build replaces only its own map slot and `UMAPINFO` entry, so several levels can share one WAD.

Requirements:
- **Python 3.10+**, standard library only.
- **ZDBSP** to build nodes, blockmap and reject. The default is the copy bundled with [Ultimate Doom Builder](https://github.com/UltimateDoomBuilder/UltimateDoomBuilder), at `/usr/lib/ultimate-doom-builder/Compilers/Nodebuilders/zdbsp` (Arch: `chaotic-aur/ultimate-doom-builder-git`), then `zdbsp` on `PATH`. Use `--zdbsp-path PATH` (or `build(..., zdbsp=PATH)`) for any other ZDBSP binary.
- **The IWADs** for the texture checks, the reach checks' texture heights and the measurements. Copy `.env.example` to `.env` and set `DOOM2_WAD` (and `DOOM_WAD`, Ultimate Doom, for `ExMy` maps) to their paths; a variable set in the environment overrides `.env`. Without them the texture checks are skipped with a warning.

### What every build checks

Findings come in two kinds. **Playability** findings fail every build:
- Geometry: lines only meet at shared vertices. A sector outline that crosses itself, or sectors and free lines that cut through each other, is an error. A sector standing free inside another (a pedestal, a crate, a pool) is cut out of it automatically; one touching the other's outline has to be listed as a hole by hand.
- Every thing is inside a sector with room for its height (a closed door has none), clear of walls, bars, fences and steps it can't climb, and not overlapping another monster or player on a skill they share. Thing types must exist in the map's game.
- Progression, worked out by the reach model in `levels/reach.py` on the built map, the way the engine does it: every vanilla line action (doors, floors, ceilings, lifts, stairs, donuts, teleporters, exits, boss deaths), keys, and the height each moving sector can reach. The exit, every `MUST_REACH` sector and every secret must be reachable from the player start.
- 100% kills: every monster can either be reached or walk (or fly) to somewhere the player can go, by monster rules: no keys, only plain use doors, blocked by monster-blocking lines. A sniper the player can only shoot at fails this too.
- No softlocks: from every damaging floor the player can get onto, the exit can still be reached.
- Every texture and flat exists in the IWAD (plus the module's `RESOURCES`).

**Style** findings fail our own maps; in an imported map (`IMPORTED = True`) they are warnings:
- Damaging floors sit lower than every neighbouring floor that isn't damaging.
- Pictures such as switches and door faces fit their wall exactly. Bars and fences can't use textures built from overlapping patches, which vanilla draws as garbage on two-sided lines (the medusa effect).
- The exit can be reached without a running jump. Jumps only count when the exit can't be reached any other way.

Textures vanilla can't tile cleanly, and line actions or thing types that aren't vanilla, get a warning. A module can list playability findings it accepts in `KNOWN_ISSUES`: the build fails only on findings not on the list, and says `fixed:` for listed ones that no longer occur.

Every build also prints:
- A balance report for each skill: monster health against ammo damage, health and armor.
- The research measurements (`levels/measure.py`, using `scripts/metrics/`): floor heights, lighting, texture variety, border textures, symmetry, optional area, secrets, monster mix, ammo and health, skill ratios and distance to the nearest monster, each beside the median and interquartile range of id's maps for that game and flagged `below` or `above` it. Then the balance along the route (`levels/balance.py`, design in `docs/balance-metrics.md`), with no bot: the reach model's critical path split into legs (one per required key or trigger), the monsters each leg engages (on the path, able to walk to it, or able to shoot it from within 1024 units), and two ammo curves leg by leg with carry caps: *thorough* (every reachable item) and *detour* (items within a 1024-unit round trip off the path, secrets excluded), plus health at the median id map's cost per monster HP, the long-range hitscan peak, side rooms, the monster HP each trap on the route releases against the ammo in hand, and monsters that can shoot the start. These are warnings judged against the id maps, never errors: a quarter of id's maps run short on the thorough curve too. Rule-1 slips (a floor texture change with no height change) are listed by sector pair, and rule-2 seams (two wall textures meeting in one plane with no border texture such as `SUPPORT3`, `DOORTRAK` or `LITE5` between them) by sector, texture pair and one junction's coordinates. This takes a couple of seconds.
- A top-down SVG preview, `wads/<WAD stem>-<MAP>.svg`: sectors shaded by floor height, special lines in red, bars and fences dashed, monsters by skill, pickups and keys.

A failed check prints `ERROR:` lines and stops the build before the WAD is touched. The preview is still written, so you can see what went wrong.

### Writing a level

A level is a module of plain data: `MAP`, `WAD`, `SECTORS`, `THINGS`, `SPECIAL_BETWEEN`, `SPECIAL_WALLS`, `FREE_LINES`, `MUST_REACH`, … To start a new one, copy `levels/nukage_junction.py`. `MAP` also picks the game: `E1M1`-style slots are Ultimate Doom, `MAP01`-style DOOM II. `WAD` may name a subdirectory of `wads/`.

Sectors are polygons: outer loops, holes that other sectors fill, and solid `pillars`. Whether a loop is an outer loop or a hole follows from nesting, so one sector can be several separate areas, as in many id maps. A hole's edges with no sector across become walls; a hole no sector touches at all is an error (make it a pillar). Edges that two sectors share become two-sided lines; the rest become walls. Texture x offsets follow each sector's outline, so patterns run continuously along a wall (`X_OFFSETS = "zero"` writes 0 instead, as id mostly did), and the wall above or below an opening uses the room's own texture. The exception is secret doors (`SECRET_DOORS`): their faces are shifted off the wall pattern by `SECRET_HINT` (16 across, 8 down) as the classic clue. Pass a `{name: (x, y)}` dict instead to pick offsets per door, with `(0, 0)` for a seamless door.

Lines that aren't sector edges go in `FREE_LINES`, keyed by their two endpoints: `{((384, 32), (384, 480)): Special(W1_DOOR_OPEN, 5)}` is a walk-over trigger across the middle of a room, so you don't have to split the room into two sectors for it. Give a `Special` a `texture` to hang bars or a fence: on a free line it stands inside one room (`Special(texture="MIDGRATE")`). In `SPECIAL_BETWEEN` it fills every opening between two sectors, such as bars between a cage and the room around it. These lines are impassable, and the texture stands on the floor. A free fence doesn't split its sector for the progression check, so to wall off part of a room with bars, make that part its own sector.

Helpers in `levels/model.py` build the common shapes. `doorway()` makes a door with optional recesses, plus its use action; its `alcove_flat`/`far_flat`, and `door()`'s `flat`, set the recess and threshold floors so they can match the rooms (Romero's rule 1: floor texture changes only with a height change). A door face is a picture that must fit its wall, so a room taller than the face (128 for `BIGDOOR*`, 72 for `EXITDOOR`) needs a recess that tall on its side of the door: `alcove` before it, `far_alcove` after it. The doorway runs `alcove + thickness + far_alcove` from its wall. `stairs()` makes a run of steps. `lift()` makes a lift used (`SR_LIFT`) from below and from its top; `walk_on=True` makes it lower when walked onto from the top instead (`WR_LIFT`), which monsters can set off and ride too.

There are helpers for the rooms most maps repeat, sized so they pass the texture checks:
- `closet()`: a monster closet behind a door disguised as the wall, opened only by its tag.
- `pedestal()`: a glowing, metal-sided pedestal for a key or item. Stand it clear of the walls and the build cuts it out of the room. Put a W1 trigger on its edge in `SPECIAL_BETWEEN` to spring a trap when the item is taken.
- `switch_niche()`: a recess whose back wall is a switch, sized to the switch picture (64 × 128, or 32 × 72 for `SW1EXIT`). It returns the sector and the `SPECIAL_WALLS` entry for the switch. Make it deep (a booth) to fire a W1 trigger on its entrance just before the switch is used.
- `lit_ledge()`: a brightly lit ledge with an unlit strip against the wall behind it, so the wall isn't lit up too.
- `window()`: an opening between rooms. Walking monsters can't climb a sill more than 24 above their floor, and fliers need at least 56 of height.

Floors can move both ways for the progression check: the lowering actions (`S1_FLOOR_LOWEST` and kin) drop a tagged floor to its lowest neighbour, and the raise actions lift it to the next higher neighbouring floor, so a rising bridge stops level with the nearest higher floor around it. The raise-and-change actions (`S1_RAISE_CHANGE` and kin) take the floor texture of the trigger line's front sector and clear the sector's special, which dries a walkway raised out of nukage (MAP05 does this), but they move at 0.5 units a tic: 96 units take 5.5 s. The fast raises (`S1_FLOOR_NEXT_FAST` and kin) move at 4 units a tic and keep the floor's texture and special, so use them for bridges out of a pit or the dark.

Anything the builder infers can be overridden line by line in `OVERRIDES`, keyed by a line's two endpoints with its front on the right going from the first to the second: `{((1088, -3648), (1024, -3648)): Line(flags=ML_BLOCKING | ML_BLOCKMONSTERS, front=Side(mid="COMPSTA2", x=16))}`. Only the fields given replace the builder's choice; a key that matches no line is an error. Decompiled maps use this for every difference from what the builder would make.

`Thing` skills are any of `e`, `m`, `h`, plus `a` for ambush (deaf) and `n` for multiplayer only; `extra` holds other flag bits. `RESOURCES` lists PWADs whose textures, flats and patches the checks and measurements load after the IWAD (for remixes of community maps; they aren't copied into the built WAD).

### Agent skills

Three skills in `.claude/skills/` take an agent through a new map in order, each ending where the next begins:

- `design-doom-ii-level`: pitch five structurally different concepts, pick one, and write a design doc to `levels/designs/<module>.md` (route, sketch, materials, secrets, measurement targets).
- `build-doom-ii-level`: turn the doc into a level module that builds clean and matches it, with the builder's known gotchas.
- `test-doom-ii-level`: route script, wiring run, screenshots, and combat-bot runs on three seeds, with each death cluster called as a map or bot problem.

They came out of four timed rounds of agents building maps from scratch: the six maps in `SPEEDY1.WAD`, built from feature checklists, all came out as the same hub with a wing per key, while the six in `SPEEDY2.WAD`, each built around a layout idea, didn't.

Agents choose textures by name unless they can see them, which is how a map ends up a collage. `scripts/tools/texture_sheets.py` renders the IWAD's wall textures (grouped into families by name, border textures labelled in yellow) and flats onto contact sheets in `/tmp/texture-sheets/<iwad>/`, with an `index.txt` of which sheet holds which family. The design skill has the agent look at them before writing the doc's materials plan:

```sh
uv run --with pillow scripts/tools/texture_sheets.py            # DOOM2_WAD from .env; --iwad for another
```

### Code layout

- `levels/model.py`: the dataclasses levels are written in (`Sector`, `Special`, `Thing`, `Line`, `Side`) and the shape helpers.
- `levels/mapgen.py`: `build()` and `compile_level()`, which turn sectors into lines and sides and place textures. Its docstring describes the level format.
- `levels/checks.py`: the checks and the balance report. `levels/reach.py`: the reach model, shared with the research scripts. `levels/measure.py`: the sector-overlap check, rule-1 slips and the research measurements. `levels/balance.py`: the resource curve and exposure checks along the route.
- `levels/decompile.py`: the decompiler. `levels/wadmap.py`: reads maps from WADs.
- `levels/preview.py`: the SVG preview. `levels/wad.py`: WAD reading and writing, IWAD paths from `.env`.
- `levels/doom2.py`: every DOOM and DOOM II thing type, monster sizes and health, pickups, line actions and sector specials.
- `tests/`: `uv run --with pytest pytest`. Tests that need an IWAD skip when it isn't set.

### Decompiling existing maps

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

### Playtests
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

## Research: what makes DOOM levels fun
Nukage Crossing and the maps after it were designed from a research report on the 68 id maps (Ultimate Doom E1M1–E4M9, DOOM II MAP01–MAP32) and what makes them fun. It drew on designer interviews, Dan Pinchbeck's *Doom: Scarydarkfast*, Not Jabba's *The Roots of Doom Mapping*, a per-map community reception score, and metrics measured from the IWADs and correlated with that score. The report quotes its sources at length, so it isn't published here; the measurement scripts are.

The metrics scripts in `scripts/metrics/` are stdlib-only and write their CSVs to `research/data/`. They read the v1.9 IWADs set by `DOOM_WAD` (Ultimate Doom) and `DOOM2_WAD` in `.env`. Run them from the repo root:

```sh
python3 scripts/metrics/space_metrics.py        # -> research/data/metrics_space.csv (about 2 minutes)
python3 scripts/metrics/combat_metrics.py       # -> research/data/metrics_combat.csv
python3 scripts/metrics/progression_metrics.py  # -> research/data/metrics_progression.csv; pass a slot (E1M7) to dump one map
python3 scripts/metrics/route_metrics.py        # -> research/data/metrics_route.csv (balance along the route; about 40 s); pass a slot for its report
```
