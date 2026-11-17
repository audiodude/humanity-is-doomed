# Geometry atlas: reading a map's plan

You are building one entry of a geometry atlas for DOOM level designers. Agents designing new maps for this repo kept making boxes: rooms as axis-aligned rectangles strung along corridors, every map going round something or across something. The atlas records what id's and well-rated community maps do instead, in terms a designer can reuse: the shape of each space, how spaces nest and connect, and how height and angle make a plan memorable.

## Inputs

For each map you are given a key. Its files are in `research/atlas/maps/`:

- `<key>.png`: the top-down preview. Grey fill is floor height (lighter is higher), green is liquid, brown a door, yellow a lift, purple a secret. Solid black lines are walls, thin grey lines are steps between sectors, dashed lines are bars or fences, red lines carry a special. Labels are `<sector name> <floor height>`. The green dot is the player start; small coloured squares are keys.
- `<key>.txt`: the title, author, year and rating; the pixel-to-map-unit transform for the PNG; the map's size, floor range, off-axis share of wall length and how many of its larger sectors are pure axis-aligned shapes; then its sectors, largest first, with floor/ceiling, light, bounding box, area, vertex count, off-axis edge count, holes and pillars.

Read both. Use sector names from the image labels or the `.txt`, never invented ones. When the image is too small to read a region, crop and enlarge it: `magick research/atlas/maps/<key>.png -crop 700x700+X+Y +repage -resize 200% /tmp/<key>_crop.png`, then read the crop. The decompiled module named in the `.txt` holds the exact outlines if you need a vertex.

## What to write

One JSON file per map, `research/atlas/entries/<key>.json`:

```json
{
  "key": "doom2__MAP11",
  "shape": "A nukage lake with an octagonal ring walkway round a central island, and wings off the lake's rim.",
  "plan": "ring-around-core",
  "plan_note": "Every wing opens off the lake; the ring is crossed and re-crossed rather than walked round.",
  "grid": "mixed",
  "moves": [
    {
      "name": "ring",
      "sectors": ["room_1"],
      "at": [576, 1280],
      "size": "1536x1280",
      "how": "An octagonal walkway 192-256 wide at 128 around an octagonal nukage pool at 0, with gaps where the bridges cross; pillars stand on its outer edge.",
      "effect": "The landmark you orient by: every wing is a spoke off it, and it is visible from most of them."
    }
  ],
  "lesson": "Make the hub a shape (an octagon in a lake) rather than a room, so crossing it is the set piece."
}
```

Fields:

- `shape`: one sentence a player would use to describe the map after playing it, about its space, not a list of rooms.
- `plan`: the overall layout, one of `linear`, `loop`, `multi-loop`, `hub`, `ring-around-core`, `ascent`, `descent`, `crossing`, `tree`, `maze`, `arena`, `open`, `other`; `plan_note` says how the route actually uses it, in one sentence.
- `grid`: `box` (almost every space an axis-aligned rectangle), `mixed` (rectangles with angled, polygonal or curved spaces among them), or `free` (most spaces are angled, curved or organic).
- `moves`: 3 to 6 geometry moves this map makes, the most distinctive first. Favour moves that a box-and-corridor map would not make. Skip the ordinary (a rectangular room joined by a door to a rectangular corridor) unless the map does nothing else, in which case say so in one move named `box-and-corridor`. Each move:
  - `name`: from the vocabulary below when one fits; otherwise a new short lowercase hyphenated name.
  - `sectors`: the sectors that make it (at most 8 names).
  - `at`: its approximate centre in map units, from the transform in the `.txt`.
  - `size`: the extent of the move itself (not of the whole area round it) in map units, `WxH`.
  - `how`: how it is built, with numbers: angles, widths, vertex counts, floor and ceiling heights relative to its neighbours, light changes. Enough that someone could rebuild it.
  - `effect`: what it does for the player in one sentence: a view, a fight, a route choice, a landmark, a sense of place.
- `lesson`: the one geometry idea from this map most worth taking into a new map, in one sentence.

## Move vocabulary

Outlines of a space:

| name | meaning |
|---|---|
| `chamfer` | a mostly rectangular space with its corners cut off at an angle |
| `polygon-room` | a hexagonal, octagonal or other regular-polygon space, or a round one |
| `skewed-room` | a space whose walls run off the grid: a trapezoid, wedge, parallelogram or rotated room |
| `diagonal-run` | a corridor or passage running at an angle across the grid |
| `curve` | a wall or edge drawn as many short segments: an arc, a round tower, a curving corridor |
| `organic` | an irregular outline with no straight logic: a cave, canyon, cliff edge or shoreline |
| `sawtooth` | a wall broken into a repeating zigzag, notches or buttresses |
| `bays` | small recesses along a wall for lights, items or monsters |
| `funnel` | a space that narrows from wide to narrow, or widens out |

Inside a space:

| name | meaning |
|---|---|
| `island` | a raised or sunken region inside a larger space: dais, platform, pit, pool |
| `pillar-field` | repeated pillars or columns standing in a space |
| `perimeter-ledge` | a band at another height running along the space's edge: balcony, walkway, sunken trench |
| `terraces` | a big space split into floor bands that step up or down across it: hillside, amphitheatre, bowl |
| `channel` | a strip of liquid or a sunken trench cutting across or around a space: canal, moat, river |
| `bridge` | a walkway over a pit or liquid |
| `ring` | a walkway that circles a core |
| `split-level` | one space with two or more floor levels open to each other |
| `nested-rooms` | a room standing inside a larger space, with the larger space flowing round it |

Between spaces:

| name | meaning |
|---|---|
| `window` | an opening you can see through but not walk through: a sill, bars, a high slot |
| `overlook` | a high place looking down into another space you will reach later or have left |
| `wide-opening` | spaces joined by an opening much wider than a door, so they read as one |
| `interlock` | spaces wrapped round each other: a corridor folding round a room, L-shapes fitting together |
| `stair-straight`, `stair-curved`, `stair-wrap` | stairs that run straight, curve, or wrap round a space or another stair |
| `courtyard` | an open-sky space hemmed in by buildings, entered from several sides |
| `light-shapes` | sectors that exist only to shape light or a floor pattern: light strips, pools under lamps, trim |

A move can combine names when that is what the map does (`island` with a `ring` round it is two moves).

## Done

Each map's JSON file parses, every sector it names appears in the `.txt` or the image, and every `at` lies inside the map's size. Write the files; your final reply is just the keys you wrote, one per line, and any key you couldn't do with the reason.
