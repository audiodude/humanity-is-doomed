---
name: design-doom-ii-level
description: Design a DOOM II level for this repo's level builder before any code is written. Use when asked to make, create, or plan a new map or set of maps.
---

Produce a **design doc** for one map (or one per map, for a set): the shape a player will remember, the route through it, and enough layout to build from. No level code in this skill; `build-doom-ii-level` takes the doc from here.

A map is remembered by its **shape**: a descent, a tower around a shaft, a canyon crossed by climbing, a loop that floods behind you. Features (keys, a lift, a secret, a trap) serve the shape. Left to defaults, every map converges on the **template**: start room, central hub, one wing per key, key door off the hub, exit room. Six speed-built maps here came out as that template, so treat it as the shape to beat.

## 1. Read

- `research/REPORT.md` (gitignored, present locally): "The short version" (line 14), Part 2 sections that bear on your idea, "Part 4: Anti-patterns checklist" (line 459), "Part 6" (line 493).
- `README.md` "Included WAD" sections and `SPOILERS.md`: the maps that already exist, so yours differs from them.
- For the target WAD, every map already in it (its module's docstring and `wads/<WAD stem>-<MAP>.svg` preview).
- The texture contact sheets: `uv run --with pillow scripts/tools/texture_sheets.py`, then `/tmp/texture-sheets/doom2/index.txt` and the sheets (`read` the PNGs) for the families your theme suggests. Pick textures from what they look like, not from their names.

Done when you can name the shape of each existing map in the target WAD in a phrase.

## 2. Pitch

Write **five concepts**, each one paragraph: the shape in a phrase, how the route moves through it, what the player sees before reaching it (the reveal), how progress is gated, and the set piece. Make the five structurally different from each other and from the maps in step 1. Gating can be keys, but also floors lowering, bridges rising, lifts, a door opened from its far side, a drop that can't be climbed back.

For a set of maps, pitch for the whole set in one pass so the maps differ from one another; parallel designers working blind converge on the same idea.

Pick one per map and say why it beats the others. If the user is present and the choice is close, offer the top two or three with the `ask` tool.

Done when each chosen concept passes: the route doesn't return to one central room between objectives, and a player could describe the map in one sentence that isn't a list of rooms.

## 3. Write the doc

Save to `levels/designs/<module>.md` (`<module>` is the level module name the build will use, e.g. `quarry_descent`). Sections:

- **Concept**: the one-sentence shape, theme, difficulty, slot (`MAPnn`, WAD).
- **Route**: ordered list of spaces. For each: rough size, floor and ceiling heights, what gates leaving it, what's visible from it, encounter (monster roles, not just counts), pickups.
- **Sketch**: an ASCII plan with approximate coordinates (map units; 64 = one grid square), marking heights, doors, lifts, triggers, secrets and the start.
- **Materials**: the palette, chosen from the sheets. Past maps here picked a new material for every room, or for each side of one courtyard, so the walls read as a collage. Plan instead:
  - A **base family** for the connective tissue (corridors, halls, the main open space), aiming for the most-used wall texture near id's 30% of wall area. Variants within one family (`STARTAN1`/`STARTAN3`, `BROWN1`/`BROWN96`) give variety without breaking the palette.
  - One **signature family per area** (a wing or a set-piece space, not each room), with what it says about the place: pipes for the pump wing, `COMP*` screens for the control room. Rooms within an area share it.
  - A **trim set** of one or two border textures (yellow on the sheets: `SUPPORT3`, `DOORTRAK`, `METAL`, `LITE5`, ...) for door frames, around switches, and wherever two materials meet in one wall plane.
  - A **reason for every material change**: an area boundary at a doorway or trim, a key colour, a secret cue, a landmark. One continuous space keeps one material; tell its sides apart with light, height and landmarks, never a different texture per side.
  - Floor and ceiling flats per area, to match the walls (rule 1: a flat changes only with a height change).

  Write it as a table: area, wall family (with the textures used), trim, flats, reason.
- **Secrets**: where, the hint a player gets, the reward.
- **Targets**, from the build's measurement table (DOOM II medians in brackets): optional share of area ≥ 0.3 [0.5], distinct floor heights ≥ 15 [23], secrets ≥ 2 [4], light-effect sectors ≥ 3 [9], deaf share (UV) ≥ 0.2 [0.42], most-used wall texture 0.2–0.45 [0.3] (below id's range means no material holds the map together; above it, monotexture), rule-2 seams with a border texture ≥ 0.5 [0.31; Romero 0.75; DOOM's best-liked third 0.57 against 0.18 for its worst]. Say where each comes from in the plan; a small map may miss area or monster counts, not these.
- **Build risks**: mechanisms the shape depends on that are slow or fragile in this builder (rising floors, lifts, long drops, wide-open sightlines). `build-doom-ii-level` lists the known gotchas.

Done when every section is filled, the sketch accounts for every space in the route, each target names the spaces that meet it, and every space in the route has a row in the materials table.
