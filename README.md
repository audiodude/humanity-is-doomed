# humanity-is-doomed

DOOM II level work: research into what makes maps fun, a Python level generator, and the maps it builds.

The classic-editor VMs (DCK 3.62 and DoomEd 4.2 on Windows 98) moved to `~/code/vibes/doomedit`.

## Generated levels
`levels/` is a small, dependency-free Python level generator. It uses the ZDBSP that ships with Ultimate Doom Builder to build nodes. Run it from the repo root:

```sh
python3 -m levels nukage_junction          # validate, then write MAP01 into wads/NUKAGE.WAD and wads/NUKAGE-MAP01.svg
python3 -m levels nukage_crossing          # same for MAP02 (wads/NUKAGE-MAP02.svg)
python3 -m levels nukage_junction --check  # only validate (still writes the SVG preview)
dsda-doom -iwad doom2 -file wads/NUKAGE.WAD          # add -warp 2 to start on MAP02
```

Several level modules can share a WAD. `build()` replaces only its own map slot and `UMAPINFO` entry and keeps the other maps, so `NUKAGE.WAD` holds both MAP01 and MAP02.

or from Python: `from levels import build, nukage_junction; build(nukage_junction)`.

- `levels/model.py`: the dataclasses levels are written in (`Sector`, `Special`, `Thing`) and shape helpers. `doorway()` makes a door with optional recesses, plus its use action. Its `alcove_flat`/`far_flat`, and `door()`'s `flat`, set the recess and threshold floors so they can match the rooms (Romero's rule 1: floor texture changes only with a height change). `stairs()` makes a run of steps; `lift()` makes a lift whose SR/WR actions are added automatically.
- `levels/mapgen.py`: `build()`, which turns sectors into lines and sides and places textures. Its docstring describes the level format.
- `levels/checks.py`: validation and the balance report. `levels/preview.py` draws the SVG, and `levels/wad.py` reads and writes WADs.
- `levels/doom2.py`: DOOM II thing types, monster sizes and health, pickups, line actions and sector specials.
- Each level is a module of plain data (`MAP`, `WAD`, `SECTORS`, `THINGS`, `SPECIAL_BETWEEN`, `SPECIAL_WALLS`, `MUST_REACH`, …). To add one, copy `levels/nukage_junction.py`.

Sectors are polygons: an outer loop, holes that other sectors fill, and solid `pillars`. A hole with no sector in it is an error. Edges that two sectors share become two-sided lines; the rest become walls. Texture x offsets follow each sector's outline, so patterns run continuously along a wall, and the wall above or below an opening uses the room's own texture. The exception is secret doors (`SECRET_DOORS`): their faces are shifted off the wall pattern by `SECRET_HINT` (16 across, 8 down) as the classic clue. Pass a `{name: (x, y)}` dict instead to pick offsets per door, with `(0, 0)` for a seamless door.

On every run, `build()`:
- writes a top-down SVG preview next to the WAD, one per map (sectors shaded by floor height, special lines in red, monsters by skill, pickups and keys);
- prints a balance report: monster health against ammo damage, health and armor, for each skill;
- checks that every thing is inside a sector, not stuck in a wall, and not overlapping another monster or player on a skill they share;
- walks the progression from the player start, working out which keys, door specials and tagged switches/triggers open what, and fails if a `MUST_REACH` sector can't be reached;
- checks every texture and flat against `doom2.wad` (`~/.local/share/dsda-doom/doom2.wad`, or set `DOOM2_WAD`). Pictures such as switches and door faces must fit their wall exactly. Textures that vanilla can't tile cleanly print a warning.

### Playtests in GZDoom
`levels/playtests/<module>.playtest` scripts walk each map's intended route in GZDoom: doors, switches, lifts, key traps, secrets and the exit, checking floor and ceiling heights after each trigger. The runner is the `doom-playtest` agent skill (`~/.agents/skills/doom-playtest/`). It runs GZDoom (`gzdoom` from chaotic-aur) headless on a hidden X display, with god mode, and writes screenshots to `/tmp/playtest-shots/<MAP>/`. A full route takes about a minute:

```sh
python3 ~/.agents/skills/doom-playtest/playtest.py wads/NUKAGE.WAD MAP02 levels/playtests/nukage_crossing.playtest
python3 ~/.agents/skills/doom-playtest/playtest.py wads/NUKAGE.WAD MAP02 --describe   # start, keys, special lines
```

A pass shows the map's wiring works in GZDoom, run in its strict Doom compatibility mode. Vanilla rendering limits and the feel of the map still need a playthrough in dsda-doom.

### Nukage Junction (`nukage_junction`)
A medium-difficulty MAP01 replacement: 46 sectors, 24/45/52 monsters on easy/medium/hard, one secret.

Route: tech start room → courtyard hub with a nukage pool → warehouse (lift to a ledge switch that lowers the blue-key island; the fake wall in the west wall leads to the secret) → blue door → lab (lift to the red key; grabbing it opens a monster closet) → red door → exit arena (ambush closets on entry) → exit switch. The `UMAPINFO` lump names the level for ports that read it (dsda-doom, GZDoom). Vanilla DOOM II still calls it "entryway".

### Nukage Crossing (`nukage_crossing`)
MAP02, built from the findings in [`REPORT.md`](REPORT.md): 96 sectors, 21/43/57 monsters on easy/medium/hard, four secrets.

- **Set piece:** a 128-high sluice gate stands in a nukage canal. A switch in the silver control tower lowers it into a footbridge, and you can watch it sink through the window beside the switch. The pinkies pacing the far yard then charge across.
- **Route:** start window with a view across the canal to the red door and a soulsphere on a lit pedestal → south yard → dark blinking pipe corridor → bright pump hall, up a step to the blue key (grabbing it opens a closet behind you) → blue door → north bank → control tower → across the bridge to the sealed south-east yard (red key; grabbing it opens closets between you and the bridge and a guardroom by the red door) → back across → terrace → red door → exit. A switch in the south-east yard opens a gate back to the start, which closes a loop through the start yard.
- **Secrets:** each is marked by a shifted panel or a light. A start-room closet holds armor. A canal ledge, reached by wading in from the pump hall's intake, holds the rocket launcher. A tower panel opens onto a pier and a lift down to the soulsphere island. The filter house hides a backpack.

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

## Research: what makes DOOM levels fun
[`REPORT.md`](REPORT.md) studies the 68 id maps (Ultimate Doom E1M1–E4M9, DOOM II MAP01–MAP32) and what makes them fun. It draws on designer interviews, Dan Pinchbeck's *Doom: Scarydarkfast*, Not Jabba's *The Roots of Doom Mapping*, a per-map community reception score, and metrics measured from the IWADs and correlated with that score. It ends with a list of checks `levels/` could add. Supporting material is in `research/`: facet reports in `facets/`, CSVs in `data/`, cleaned sources in `sources/`, and scripts in `tools/`.

The metrics scripts are stdlib-only and read the Steam v1.9 IWADs by default (override with `DOOM_WAD` / `DOOM2_WAD`). Run them from the repo root:

```sh
python3 research/tools/space_metrics.py        # -> research/data/metrics_space.csv (about 2 minutes)
python3 research/tools/combat_metrics.py       # -> research/data/metrics_combat.csv
python3 research/tools/progression_metrics.py  # -> research/data/metrics_progression.csv; pass a slot (E1M7) to dump one map
python3 research/tools/correlate.py            # -> research/data/correlations.csv, metrics vs research/data/reception.csv
```
