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
- **Secrets**: where, the hint a player gets, the reward.
- **Targets**, from the build's measurement table (DOOM II medians in brackets): optional share of area ≥ 0.3 [0.5], distinct floor heights ≥ 15 [23], secrets ≥ 2 [4], light-effect sectors ≥ 3 [9], deaf share (UV) ≥ 0.2 [0.42]. Say where each comes from in the plan; a small map may miss area or monster counts, not these.
- **Build risks**: mechanisms the shape depends on that are slow or fragile in this builder (rising floors, lifts, long drops, wide-open sightlines). `build-doom-ii-level` lists the known gotchas.

Done when every section is filled, the sketch accounts for every space in the route, and each target names the spaces that meet it.
