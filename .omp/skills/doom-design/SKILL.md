---
name: doom-design
description: Design a DOOM II level for this repo's level builder before any code is written. Use when asked to make, create, or plan a new map or set of maps.
---

Produce a **design doc** for one map (or one per map, for a set): the shape a player will remember, the route through it, and enough layout to build from. No level code in this skill; `doom-build` takes the doc from here.

A map is remembered by its **shape**. Features (keys, a lift, a secret, a trap) serve the shape. Left to defaults, maps here have converged on three things, so treat them as the shapes to beat:

- **The template**: start room, central room, one wing per key, each key opening the next wing's door off the centre, exit room. It's a very tired trope, and six speed-built maps came out as it; there are better alternatives. Central rooms themselves, and rooms the route returns to, aren't the problem: half the official maps have a hub, often a landmark (an octagon, a lake, a hand) seen from new sides on each return.
- **The box plan**: every space an axis-aligned rectangle joined by rectangular corridors. All eight NUKAGE maps put 98-100% of their line length on the axes; id's DOOM II maps put a median 77% there, and three in five of their larger rooms have an angled, polygonal or curved edge.
- **Round it or across it**: NUKAGE's Tower, Crossing, Lockdown and Drain all go round one central feature, and Undercurrent crosses one and comes back underneath.

Shapes come from real maps. The **geometry atlas** has an agent's reading of 758 of them (every official map that decompiles, and community maps from releases rated 4.25 or higher): each map's shape in a sentence, its plan, and the geometry moves it makes, with sectors, coordinates and numbers. `geometry.md` in this skill's directory summarises it: the moves, how often id and community maps make them, how to build each with the builder's helpers, and maps to look at.

## 1. Read

- `research/REPORT.md` (gitignored, present locally): "The short version" (line 14), Part 2 sections that bear on your idea, "Part 4: Anti-patterns checklist" (line 459), "Part 6" (line 493).
- `geometry.md` (this skill's directory), whole.
- `docs/maps.md` and `SPOILERS.md`: the maps that already exist, so yours differs from them.
- For the target WAD, every map already in it (its set, `levels/sets/<set>.py`, lists them by slot; each module's docstring and `wads/previews/<module>.svg` preview).
- Atlas maps, looked at, not just listed. `python3 scripts/metrics/atlas.py find --plan <plan>`, `find --move <move>` or `find <words>` lists matches, official maps first, with the sectors and coordinates of each move; `read` the map's image (`research/atlas/maps/<key>.png`) and find the move in it. Look at five or more, at least three of them with a plan no map in the target WAD has.
- The texture contact sheets: `uv run --with pillow scripts/tools/texture_sheets.py`, then `/tmp/texture-sheets/doom2/index.txt` and the sheets (`read` the PNGs) for the families your theme suggests. Pick textures from what they look like, not from their names.

Done when you can name the shape and plan of each existing map in the target WAD in a phrase, and you have looked at five atlas maps.

## 2. Pitch

Write **five concepts**, each one paragraph:

- the shape in a phrase, and its plan (one of the atlas plans: `linear`, `loop`, `multi-loop`, `hub`, `ring-around-core`, `ascent`, `descent`, `crossing`, `tree`, `maze`, `arena`, `open`);
- the two or three geometry moves from `geometry.md` that make the shape, and the atlas map (key) you saw each in;
- how the route moves through it, and what the player sees before reaching it (the reveal);
- how progress is gated: keys, but also floors lowering, bridges rising, lifts, a door opened from its far side, a drop that can't be climbed back;
- the set piece.

Make the five structurally different from each other and from the maps in step 1: five different plans, none a plan the target WAD already has twice. Central rooms and rooms you return to are fine; a central room with a key in each wing off it is the template, and there are better alternatives.

For a set of maps, pitch for the whole set in one pass so the maps differ from one another; parallel designers working blind converge on the same idea.

Pick one per map and say why it beats the others. If the user is present and the choice is close, offer the top two or three with the `ask` tool.

Done when each chosen concept passes: it isn't the template (a central room with one key per wing), a player could describe the map in one sentence that isn't a list of rooms, and its shape depends on at least two moves that aren't boxes.

## 3. Write the doc

Save to `levels/designs/<module>.md` (`<module>` is the level module name the build will use, e.g. `quarry_descent`). Sections:

- **Concept**: the one-sentence shape, plan, theme, difficulty, slot (`MAPnn`, WAD).
- **Exemplars**: the two or three atlas maps the plan borrows from: key, the move, its sectors, and what you take from it and change. Borrow the idea and its proportions, not the outline.
- **Route**: ordered list of spaces. For each: its shape (which move), rough size, floor and ceiling heights, what gates leaving it, what's visible from it, encounter (monster roles, not just counts), pickups.
- **Sketch**: a ```` ```sketch ```` block with every space in the route as a polygon in map units (64 = one grid square), and marks for the start, keys, doors, lifts, switches, triggers and secrets. One space per line, `name floor/ceil [tags] : outline`; the outline is `x,y` pairs or a call to the builder's loop helpers (`rect`, `regular`, `chamfer`, `arc`, `inset`); later spaces draw over earlier ones, so an island follows the room it stands in. Marks are `* x,y text`:

  ```sketch
  # name     floor/ceil  tags        : outline (map units)
  yard       0/320       sky         : 0,0 1024,0 1024,640 768,896 0,896
  moat       -48/320     liquid sky  : regular(512, 448, 288, 8)
  tower      96/256                  : regular(512, 448, 160, 8)
  dock       24/160                  : chamfer(1024, 128, 1408, 512, 64)
  * 128,128 start
  * 512,448 yellow key
  ```

  Draw it with `python3 scripts/tools/sketch.py levels/designs/<module>.md`, which writes `levels/designs/<module>.svg` and reports crossings (errors: sectors meet only along shared edges), islands, and the plan's off-axis share and axis-aligned rooms. `read` the SVG with `:img` and redraw until it is the shape you pitched. Spaces that meet share their edge's vertices exactly, as the build will need. `doom-build` copies these outlines, so they are the map's real geometry: a box here is a box in the map.
- **Materials**: the palette, chosen from the sheets. Past maps here picked a new material for every room, or for each side of one courtyard, so the walls read as a collage. Plan instead:
  - A **base family** for the connective tissue (corridors, halls, the main open space), aiming for the most-used wall texture near id's 30% of wall area. Variants within one family (`STARTAN1`/`STARTAN3`, `BROWN1`/`BROWN96`) give variety without breaking the palette.
  - One **signature family per area** (a wing or a set-piece space, not each room), with what it says about the place: pipes for the pump wing, `COMP*` screens for the control room. Rooms within an area share it.
  - A **trim set** of one or two border textures (yellow on the sheets: `SUPPORT3`, `DOORTRAK`, `METAL`, `LITE5`, ...) for door frames, around switches, and wherever two materials meet in one wall plane.
  - A **reason for every material change**: an area boundary at a doorway or trim, a key colour, a secret cue, a landmark. One continuous space keeps one material; tell its sides apart with light, height and landmarks, never a different texture per side.
  - Floor and ceiling flats per area, to match the walls (rule 1: a flat changes only with a height change).

  Write it as a table: area, wall family (with the textures used), trim, flats, reason.
- **Secrets**: where, the hint a player gets, the reward.
- **Targets**, from the build's measurement table (DOOM II medians in brackets): optional share of area ≥ 0.3 [0.5], distinct floor heights ≥ 15 [23], secrets ≥ 2 [4], light-effect sectors ≥ 3 [9], deaf share (UV) ≥ 0.2 [0.42], most-used wall texture 0.2–0.45 [0.3] (below id's range means no material holds the map together; above it, monotexture), rule-2 seams with a border texture ≥ 0.5 [0.31; Romero 0.75; DOOM's best-liked third 0.57 against 0.18 for its worst], off-axis share of line length ≥ 0.11 [0.23], axis-aligned share of rooms ≥ 128×128 ≤ 0.5 [0.39], lowest ammo ratio near the route (UV) ≥ 1.2 [0.65] (the curve counts every shot as a hit; below 1.2 the build warns). Say where each comes from in the plan; a small map may miss area or monster counts, not these. The two plan-geometry numbers come from the sketch report and should come from the moves: walls turned off the grid just to pass them are a miss. For the ammo, plan where each big fight's shells sit, on the way to it: ammo in secrets and side rooms doesn't count.
- **Build risks**: mechanisms the shape depends on that are slow or fragile in this builder (rising floors, lifts, long drops, wide-open sightlines, doors or stairs on angled walls). `doom-build` lists the known gotchas.

Done when every section is filled, the sketch draws with no errors and has every space in the route, each target names the spaces that meet it, and every space in the route has a row in the materials table.
