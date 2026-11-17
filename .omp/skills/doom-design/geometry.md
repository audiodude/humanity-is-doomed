# Geometry moves

What official and well-rated community maps do with space, from the geometry atlas: an agent read the top-down plan of 758 maps (150 official: DOOM, DOOM II, TNT, Plutonia, the Master Levels; 608 community maps from releases rated 4.25 or higher on idgames) and wrote down each one's shape, plan, and three to six of its most distinctive geometry moves. Use it to pitch shapes (`SKILL.md` step 2) and to sketch them (step 3).

Shares below are the share of maps whose entry names the move. Entries list what stands out, so a share is a floor for how common a move is, not a census. Numbers in the sections are as the atlas agents read them off the plans; check the vertices in the map's module before copying one.

## Searching the atlas

```sh
python3 scripts/metrics/atlas.py find --move ring           # every map making a move, official first, by rating
python3 scripts/metrics/atlas.py find --plan descent        # maps with a plan, with their shape and lesson
python3 scripts/metrics/atlas.py find zigzag nukage         # words in a move's name, how or effect
python3 scripts/metrics/atlas.py find --move bridge --source official -n 3
```

Each hit gives the sectors, a centre point, the size, how it is built and what it does. Then `read` `research/atlas/maps/<key>.png` (its `.txt` has the pixel-to-map transform and the sector list), and open `levels/imported/<module>.py` for exact outlines. The entries, images and modules are local and gitignored.

## Plans

| plan | official | community | what it looks like | look at |
|---|---|---|---|---|
| hub | 51% | 45% | one central space (polygonal hall, lake, courtyard, corridor ring) with wings off it; the route goes out to a wing and back through the centre | `doom__E1M4` polygonal hall with an octagonal key chamber inside; `doom__E3M2` rocky "palm" with five angled fingers; `doom2__MAP20` blood sea round an octagonal tower hall |
| linear | 10% | 14% | a chain of set-piece spaces along one axis, side loops rejoining it | `doom__E1M8` octagonal rooms up one axis to a star room; `tnt__MAP32` walled buildings as islands in a long lake |
| ring-around-core | 11% | 6% | a band you can walk all the way round a core (keep, octagon, pool), wings off its outside, the core entered last | `doom2__MAP07` square yard inside a square yard; `doom__E3M5` octagonal nave wrapped by a curving ambulatory; `plutonia__MAP21` octagonal walkway floating in a blood lake |
| multi-loop | 7% | 10% | a dense knot where most rooms have two or three exits, so the route keeps returning from new doors or from below | `doom__E3M3` rooms round a raised octagon crossed by high walkways; `doom__E1M7` halls wrapped round a crooked nukage river; `plutonia__MAP03` rock chambers joined by looping slime tubes |
| tree | 5% | 6% | a trunk (a spine or junction room) with set-piece branches you clear and come back from | `tnt__MAP31` spine of pyramid, nave and pod hall with a pier into a lake; `doom2__MAP23` shaped rooms end to end with an octagon branching both ways |
| open | 5% | 4% | one outdoor ground with separate buildings or islands visited in key order | `doom__E3M6` volcanic island in a hexagonal lava sea; `doom2__MAP14` four buildings in a shallow lake joined by wading channels; `doom2__MAP15` grass yard of free-standing towers |
| loop | 2% | 5% | a ring of rooms round something central, out one side and back the other | `doom2__MAP06` rooms round a slime hall and a deep pit; `doom__E3M9` pentagon, octagon and triangle halls joined into a circuit |
| descent | 3% | 3% | stages each lower than the last, mostly one way down | `tnt__MAP12` a diagonal factory hall dropping 1100 down a zigzag nukage gorge; `tnt__MAP26` a plateau 1500 up, a zigzag lift chain into mines |
| arena | 3% | 2% | one huge open floor with a centre and cover | `doom__E2M8` hexagon of pillars round a tower you start inside; `doom2__MAP30` slime arena with rising tiers |
| ascent | 0% | 2% | a one-way climb along a spine to a high climax | `community__ttp-rp__TTP_MAP09` sixteen-sided pit circled by four wings, each 64 higher; `community__nos4dead__NOS4DEAD_E1M8` mirrored procession over twin stairs and a causeway |
| crossing | 3% | 1% | a hazard filling the middle, spanned by catwalks, piers or stones | `plutonia__MAP04` plus-shaped causeway over four slime quadrants; `master__CATWALK_MAP01` one thin catwalk the length of a chasm |

A hub is the commonest plan in both groups: central rooms, and rooms the route returns to, are fine. What's tired is the template built on one, a central room with a key in each wing off it. id's hubs are a shape in their own right (an octagon, a lake, a hand) seen from every wing.

Grid, as the agents judged it: official maps 71% mixed (rectangles among angled, polygonal and curved spaces), 23% free, 6% box; community 66%, 25%, 9%. By measurement, DOOM II's median map has 23% of its line length off the axes and 61% of its larger rooms with an off-axis edge (`levels/measure.py`).

## Moves

| move | official | community | build with |
|---|---|---|---|
| [island](#island) | 65% | 58% | its outline as its own sector and as a hole in the space round it |
| [polygon-room](#polygon-room) | 57% | 45% | `regular()` |
| [channel](#channel) | 42% | 39% | a drawn strip, or `[outer, inset(outer, w)]` for a moat |
| [organic](#organic) | 27% | 41% | drawn points |
| [pillar-field](#pillar-field) | 31% | 31% | `pillars=[...]` of `rect()` or small `regular()` |
| [terraces](#terraces) | 21% | 33% | successive `inset()` bands, or drawn slanted bands |
| [nested-rooms](#nested-rooms) | 27% | 26% | the inner room as a hole of the outer space |
| [skewed-room](#skewed-room) | 25% | 20% | drawn points |
| [bridge](#bridge) | 17% | 19% | a walkway sector splitting the liquid |
| [ring](#ring) | 23% | 15% | `[regular(R), regular(r)]` or `[outer, inset(outer, w)]` |
| [light-shapes](#light-shapes) | 10% | 18% | sectors that change only light (or a few units of height) |
| [stair-straight](#stair-straight) | 23% | 15% | `stairs()` |
| [funnel](#funnel) | 18% | 15% | a drawn trapezoid |
| [stair-curved](#stair-curved) | 19% | 15% | `curved_stairs()` |
| [perimeter-ledge](#perimeter-ledge) | 13% | 15% | `[outer, inset(outer, w)]` |
| [bays](#bays) | 13% | 15% | notches in the outline, or `closet()` |
| [diagonal-run](#diagonal-run) | 19% | 13% | a corridor at 45 degrees |
| [curve](#curve) | 12% | 14% | `arc()` |
| [chamfer](#chamfer) | 9% | 13% | `chamfer()` |
| [stair-wrap](#stair-wrap) | 17% | 9% | `curved_stairs()` round a `regular()` core, or `stairs()` round a square one |
| [sawtooth](#sawtooth) | 8% | 9% | zigzag points |
| [split-level](#split-level) | 7% | 6% | sectors at different floors with no wall between |
| [interlock](#interlock) | 8% | 4% | an L or U outline sharing edges with what it wraps |
| [overlook](#overlook) | 2% | 6% | a high sector on a low one's edge, railed |
| [courtyard](#courtyard) | 1% | 5% | a sky sector with the buildings as holes |

Only 3% of official maps (and 2% of community ones) needed a `box-and-corridor` move, the name the agents kept for plans that are mostly boxes.

The builder's outline helpers are in `levels/model.py` and `docs/builder.md` "Writing a level"; the sketch takes the same calls. `doorway()`, `stairs()`, `lift()`, `window()` and the niches are axis-aligned, so put them on an axis-aligned edge of an angled space.

### island

A floor shape standing inside a larger sector, usually liquid or a pit, seen from all sides: the player circles it, crosses to it, or finds a way up.
- **Numbers**: from 64x64 posts and 96x96 stepping stones through 192-576 platforms to landmasses thousands across. 8-16 above the liquid for low rocks, 56-128 for cover blocks, 280-600 for towers. Often off-axis: octagons, chamfered squares, blobs of 25-160 vertices. Sometimes lit brighter than its surroundings (255 against 128 in E1M7).
- **Variants**: a fortress rising hundreds of units out of a lake as the map's goal (`doom2__MAP29`); equal blocks on a grid as cover (`doom2__MAP07`: four 192x192 blocks 56 high, 320 apart); a line of stepping stones (`community__draftex__DRAFTEX_E4M5`); a key dais in a moat (`doom__E1M4`, `doom2__MAP16`).
- **Does**: a landmark in view from every shore; shows the goal before it's reachable, so the route is working out how to get on; cover in an open fight; gives a square room a centre to move round.
- **Look at**: `doom2__MAP29` (blood_0, room_46, room_45); `doom2__MAP07` (room_22, room_21, room_27, room_26); `community__btsx_e1__BTSX_E1A_MAP17` (room_280, nukage_281).
- **Build**: the island's outline is its own sector's loop and a hole in the surrounding sector (standing clear, the build cuts it out). Liquid round it sits below every dry neighbour. A reachable island needs a visible way up: stairs, a lift, a bridge.
- **Watch**: a square island in a square pool is a box in a box; an island with no visible way up strands players.

### polygon-room

A room whose outline is a regular or near-regular polygon (hexagon, octagon, 12-24 sided round), usually symmetrical, among ordinary rooms.
- **Numbers**: mostly 300-1100 across; 8-54 vertices; 45-degree cuts 96-256 long. Inner features 8-32 off the floor, sunken centres to -112 by 16-unit steps; lit insets 30-160 brighter.
- **Variants**: a hub octagon with corridors off several faces, diagonal ones included (`doom__E2M6` room_6, `doom__E1M4` room_6); an island polygon seen before it's reachable (`doom__E3M6`); nested polygons stepping down or brightening to a centre (`community__pe4_dt3__PE4_DT3_E4M2` room_119); an elongated hexagon lined up with a path (`doom__E1M3` room_7).
- **Does**: a landmark you recognise on later passes; a junction where each face is a separate choice; a centre that draws the player in; a sunken middle to fight round.
- **Look at**: `doom__E3M3` (room_5, room_31, room_32: a chamfered octagon with a teleport pillar you keep crossing); `doom__E2M6` (room_6: a 256-wide octagon with a corridor on every face); `community__pe4_dt3__PE4_DT3_E4M2` (room_119-121).
- **Build**: `regular(cx, cy, r, n)`. With `n` divisible by 4 the flat faces lie on the axes and take `doorway()`. Concentric calls with the same `n` nest exactly for a dais, ring or pool.
- **Watch**: very large and empty, it stops reading as a room (E2M8's arena); repeated identical polygons disorient.

### channel

A long narrow strip of liquid or sunken floor, straight, kinked, snaking or ringed, splitting a space into banks you cross or follow.
- **Numbers**: 64-130 wide for gutters, 128-320 for canals, 300-1000 for moats; 500 to over 6000 long. Bed 8-24 down for wadeable liquid, 56-192 for trenches. Winding ones have 16-170 vertices, mostly off-axis. Some beds step down 12-24 along their course. Lava often lit 255.
- **Variants**: a snaking river with banks walkways follow and cross (`doom2__MAP29`); a straight canal cutting a hall, crossed once (`doom__E4M3`); a moat round an island or building (`doom__E2M4`, `doom2__MAP19`); a stepped watercourse that reads as running downhill (`community__btsx_e1__BTSX_E1A_MAP32`).
- **Does**: makes each crossing an exposed moment; a long straight one is a spine that shows where the wings are; a diagonal or winding stroke breaks a square plan; following it gives the route a direction.
- **Look at**: `doom__E4M8` (room_134, room_202: a 64-128 wide blood stream snaking diagonally across a box hall); `doom__E1M7` (nukage_3, nukage_119: the river as the base's spine); `community__btsx_e1__BTSX_E1A_MAP32` (room_709, room_711).
- **Build**: draw the strip's points; a moat round a block is `[outer, inset(outer, w)]`. A bridge across it splits it into two sectors.
- **Watch**: a rectangular pool with straight edges is still a box; long cramped damaging runs drag.

### organic

A free-form outline with most edges off the grid (lobes, hooks, jagged shores), usually a cave, lake, river or canyon.
- **Numbers**: 9-160 vertices per key sector, half or more off-axis. Pockets 300-500 wide, channels 96-500, basins 1000-2500. Floors step 8-24 within one space; rims 100-350 above the floor or liquid.
- **Variants**: a free-drawn shoreline against a built base (`community__btsx_e1__BTSX_E1A_MAP13`); one winding canyon (`doom__E4M2`: three switchbacks with lava cracks lit 255 against 112 at each bend); a bowl of irregular plates stepping down (`community__btsx_e1__BTSX_E1A_MAP14`); a small irregular pocket or secret cave (`doom__E2M7`).
- **Does**: reads as found ground rather than a room; bulges block long sightlines and hide monsters; causeways and island chains lay the route without walls; makes square buildings look set into a landscape.
- **Look at**: `doom2__MAP28` (room_0, hazard_7: a 157-vertex cave with no right angles); `doom__E4M2` (room_52, room_53, room_57); `community__draftex__DRAFTEX_E4M6` (blood_283-292: a river whose bed drops 16 at a time).
- **Build**: draw the points, 32-128 apart, whole units; neighbours list the shared vertices.
- **Watch**: big sprawls that only the automap explains (E3M2); arms that look alike; a lone organic scrap in a square map looks pasted on.

### pillar-field

Free-standing solid shapes (columns, posts, wall fragments) inside a hall, breaking it up without dividing it.
- **Numbers**: pillars 48-128 across, 64x64 squares and 64-80 octagons most often; 4 to about 17 of them, 128-370 apart on grids. Plinths step 8-24 per tier. Columns often octagonal or turned 45 degrees.
- **Variants**: a regular or staggered grid filling a square hall (`community__pe4_dt3__PE4_DT3_E4M4`: 4x4 on 256 centres); two rows dividing a nave from aisles at another height (`master__PARADOX_MAP01`); ruined outcrops scattered in liquid (`doom__E3M2`, `doom__E3M6`); pillars that are mechanisms: closet blocks, cages (`doom2__MAP32`).
- **Does**: breaks sightlines so a fight circles and dodges; splits a damaging floor into lanes; a colonnade frames an axis; a recognisable pattern marks a hub.
- **Look at**: `doom__E2M2` (room_84: four 80-wide octagonal pillars under a ceiling twice the corridors' height); `doom2__MAP06` (room_17, room_23); `community__fth666__FTH666_MAP06` (room_40, room_4: U-shaped cells turning a 1440-square hall into a flanking fight).
- **Build**: `pillars=[...]` on the floor sector, of `rect()` or `regular(cx, cy, 40, 8)`. Leave 64 or more between them.
- **Watch**: too dense or too small becomes a maze of posts; a low-ceilinged hall full of blocks feels cramped.

### terraces

A floor split into nested or parallel bands, each a fixed step from the next, following a bowl, slope or shore rather than a corridor stair.
- **Numbers**: steps 8-24 (24 in Plutonia MAP06 and MAP28); landform tiers 64-130. Bands 32-64 deep in tight sets, 150-350 on hillsides; 3-8 tiers, 30-300 total height. Dividing lines usually 20-45 degrees off the grid.
- **Variants**: concentric polygon rings stepping down to a pit or pool (`plutonia__MAP28`, `plutonia__MAP06`); parallel slanted strips reading as a hillside (`master__SUBTERRA_MAP01`); chevron steps pointing at a door (`master__CANYON_MAP01`); free-drawn shelves round a lake (`community__pe4_dt3__PE4_DT3_E4M5`).
- **Does**: shows the low point from the rim before you walk down; every ring overlooks the floor, so fights come from all sides; chevrons point the way; makes outdoor space read as ground.
- **Look at**: `plutonia__MAP28` (room_166-169: octagonal rings each 24 lower and 128 narrower, ceilings rising in step); `doom2__MAP29` (room_93, room_96, room_100); `community__btsx_e1__BTSX_E1A_MAP32` (room_587, room_589).
- **Build**: each band is `[inset(outer, k*d), inset(outer, (k+1)*d)]` at its own floor, the innermost `inset(outer, n*d)`; or draw slanted bands. Walkable steps are 24 at most.
- **Watch**: uneven rises read as a rippled floor; square-cut tiers in a rectangle keep the box.

### nested-rooms

A room or building standing free inside a larger room or yard, so the outer space runs round it.
- **Numbers**: outer spaces 500 to over 3000 across, the inner block a quarter to two thirds of the width, a band 64-200 wide round it. Layers differ by 8-128 in floor, inner ceilings or light by 40-100.
- **Variants**: concentric rings of one shape changing floor or ceiling layer by layer (`doom2__MAP07`); a solid block the floor runs round as an arena loop (`doom__E2M8`); a building on an island in a moat, one bridge in (`doom__E4M6`, `doom2__MAP15`); an open pavilion of corner posts round a key dais (`community__btsx_e1__BTSX_E1A_MAP15`).
- **Does**: a landmark in the middle of a big space; turns a room into a loop; a key seen across a hazard or through gaps; doors in the inner walls can open together for an ambush.
- **Look at**: `doom2__MAP07` (room_4, room_10, room_0: sky, a low dim band, sky again); `doom__E4M6` (lava_42, room_43); `community__nos4dead__NOS4DEAD_E1M5` (room_54, room_18, room_26: three octagons one inside another).
- **Build**: the inner room's outline is a hole of the outer space; doors go on its axis-aligned faces.
- **Watch**: plain squares at one floor read as a diagram; a sealed block with no visible way in stalls players.

### skewed-room

A room or yard turned off the grid, whole (usually 45 degrees) or with diagonal walls (20-65 degrees): a diamond, wedge or trapezoid among square rooms.
- **Numbers**: mostly 300-1300 across, small diamonds 256-450, yards 2900-4400. Single slanted walls most often 30 or 60 degrees.
- **Variants**: a room rotated 45 degrees with its contents on the same diagonal (`doom__E1M3` room_131, a 1000-unit square turned 45 degrees with a spiral of walls inside); a wedge whose walls converge on a key or exit (`doom__E3M9` room_32); an outdoor yard with no two walls parallel (`doom2__MAP16` room_0); a gridded room holding a rotated dais or lift (`doom2__MAP21`).
- **Does**: throws off the sense of direction after gridded rooms; converging walls aim the eye; makes a building recognisable from a distance; splits a fight into lanes not all visible at once.
- **Look at**: `doom__E1M3` (room_131); `doom__E3M4` (room_107: a slanted wall widening the hall from 600 to 1600, never seen whole); `community__fth666__FTH666_MAP09` (room_20: a whole keep rotated 45 degrees).
- **Build**: draw the outline. 45 degrees and 2:1 slopes keep vertices whole along a wall. Keep an axis-aligned edge for each door, or hand-build the door with `door()`.
- **Watch**: a rotated empty square is still a box; when every room is angled the contrast is lost.

### bridge

A strip of walkable floor across liquid or a pit, the only safe way across.
- **Numbers**: 32-250 wide, mostly 96-200. 8-24 above the hazard (E1M1, E1M2) to 120-300 over chasms. Snaking ones have 7-72 vertices in legs 20-50 degrees off the grid.
- **Variants**: a zigzag walkway with the hazard filling the teeth (`doom__E1M1`, `doom2__MAP26`); a straight pier out to a goal (`community__btsx_e1__BTSX_E1A_MAP13`); a plus-shaped crossing quartering a pool (`plutonia__MAP04`); stepping stones (`master__VESPERAS_MAP09`).
- **Does**: makes a short room a long walk with hazard on both hands; exposes the player on one line; shows a goal at a pier's end from the shore; a cross over a round room organises the map.
- **Look at**: `doom__E1M1` (room_56, nukage_57, nukage_53: a 14-vertex zigzag 24 above nukage); `doom2__MAP26` (lava_42, room_43-46: an S of three switchbacks); `community__btsx_e1__BTSX_E1A_MAP13` (room_107, room_111: a fenced 200-wide pier 530 into lava).
- **Build**: the walkway sector runs bank to bank, so the liquid either side is two sectors (or one, flowing round). Bars along it go in `SPECIAL_BETWEEN`.
- **Watch**: identical crossings disorient (E1M6's three plus-walkway tanks); a straight causeway between mirrored rectangular pools is a box with a stripe.

### ring

A walkable band, usually octagonal or rounded, round a central pool, pit, block or inner room.
- **Numbers**: bands 96-300 wide; the figure 500-1600 across. 8-16 sided, 20-60 vertices. Ring to centre 16-24 (E2M7, MAP07) up to 120-250 over liquid.
- **Variants**: a walkway round a moat with an island in it (`doom__E1M3`, `plutonia__MAP09`); a corridor round a closed inner room (`doom__E2M4`); nested rings alternating floor and liquid (`community__remain1__REMAIN1_MAP11`); a ring that climbs or spirals inward (`doom2__MAP17`, `doom2__MAP15`).
- **Does**: the centre stays in view, so it orients; a loop to circle-strafe; paths leave its faces so you go out one way and come back another; a goal in the centre is walked round first.
- **Look at**: `doom__E1M3` (room_47, nukage_46: a 100-150 wide octagonal walkway 120 above slime); `doom__E1M6` (room_125: a 160-wide ring round a plus-shaped block with a corridor off each face); `community__remain1__REMAIN1_MAP11` (room_4, nukage_3, room_1).
- **Build**: one sector with loops `[regular(cx, cy, R, n), regular(cx, cy, r, n)]`, the core `regular(cx, cy, r, n)`; for other shapes `[outer, inset(outer, w)]`.
- **Watch**: a thin ring over a deep drop exposes the player to everything in the middle; a box with a block in it is a loop but no landmark.

### light-shapes

Extra sectors inside a level room (rings, wedges, stripes) that change only light, ceiling or a few units of floor, so a pattern shows on a flat floor.
- **Numbers**: bands 24-128 deep, strips 20-64 wide; floors level or within 4-25. Light steps 8-18 between neighbours, 30-110 between the pattern and its surroundings.
- **Variants**: concentric rings brightening to a centre (`doom2__MAP06`); radial wedges or a sunburst (`master__VESPERAS_MAP09`); diagonal X or lattice cuts (`master__NESSUS_MAP07`); a gradient along a corridor (`community__pe4_dt3__PE4_DT3_E4M9`).
- **Does**: gives a flat room a medallion to recognise; chevrons point the way; fading bands make a passage feel longer; marks spots on a big floor.
- **Look at**: `master__VESPERAS_MAP09` (room_141-155: wedges round a diamond at 192, 160, 112); `doom2__MAP06` (room_27-29); `community__pe4_dt3__PE4_DT3_E4M6` (room_703-709: seven rings rising 16 in light each).
- **Build**: shaped sectors with the room's floor and flat (rule 1: a flat changes only with a height change) and their own light.
- **Watch**: differences of a few units barely show.

### stair-straight

Thin step sectors side by side along one line.
- **Numbers**: 32-256 wide, mostly 128 or 192; rises 8 or 16, 3-15 steps.
- **Variants**: a long axial flight (`doom__E1M8`); a diagonal flight of rotated squares (`community__remain1__REMAIN1_MAP11`, `plutonia__MAP06`); mirrored flights meeting at a door (`master__PARADOX_MAP01`); a whole room cut into step bands (`doom2__MAP21`).
- **Does**: shows the climb and its goal at once; makes height legible (in E1M9 the hub is always uphill); a narrow flight over a hazard is exposed footing; a broad one is a formal approach.
- **Look at**: `doom__E1M8` (room_52-67); `doom__E4M3` (room_86-94: two flights side by side, one up and one down); `community__remain1__REMAIN1_MAP11` (room_266-272).
- **Build**: `stairs()`. Steps 48 deep or more pass the reach check (id's are often 32; ours failed at 32).
- **Watch**: identical rectangles on the grid read as a corridor with lines on the floor; vary the risers, light or angle.

### funnel

A space whose side walls angle in or out (usually 30-45 degrees), from a narrow neck to a wide mouth, pointing at one door, stair or view.
- **Numbers**: necks 96-320, mouths 256-900 (1100-1830 outdoors). Steps of 8-16 or V bands rising 8 inside the taper; ceilings often jump at the wide end (128 to 384 in E2M1).
- **Variants**: a reveal mouth, a stair flaring onto a big space (`tnt__MAP08`: 128 to 768 over 20 steps); an aiming wedge tapering to the exit or key (`doom2__MAP05`); an hourglass with a chokepoint inside one space (`community__tdevil2__TDEVIL2_MAP06`); a fan of chevron bands stepping up to the focus (`plutonia__MAP32`).
- **Does**: stepping out of the neck shows the whole hall; converging walls point at the next door; a waist concentrates a fight.
- **Look at**: `tnt__MAP08` (room_174, room_185); `doom2__MAP03` (room_13, room_15, lift_14: a bow-tie hall flaring from a lift to 700); `community__tdevil2__TDEVIL2_MAP06` (room_53-55).
- **Build**: a drawn trapezoid; the neck's edge stays axis-aligned for its door.
- **Watch**: a taper with nothing at its narrow end only squeezes the player.

### stair-curved

Wedge or trapezoid steps whose risers run off the grid, so the stair turns, hooks or curls round something while it climbs.
- **Numbers**: 4 to about 40 steps turning 45-300 degrees (mostly 90-180); 64-200 wide; rises 8 or 16.
- **Variants**: a quarter-turn fan at a corner (`doom2__MAP14`); a rim stair curling round a pool or pit (`plutonia__MAP19`, `community__b2b__B2B_E2M3`); twin arcs either side of a hall (`doom2__MAP20`); a hook round a solid core (`doom__E3M3`).
- **Does**: the bend hides the destination until you climb round it; circling a pool keeps it in view below; a long rise felt as a journey.
- **Look at**: `doom__E3M3` (room_130-137, hazard_51: 8-unit wedges curling 270 degrees round a kidney pool); `plutonia__MAP19` (two 180-degree arcs hugging a blood pit, one up and one down); `community__b2b__B2B_E2M3` (14 wedges dropping 8 round a nukage pool).
- **Build**: `curved_stairs(name, centre, r1, r2, a0, a1, steps, ...)`, steps 48 or more deep along the middle radius; rooms and rings built from `arc()` on the same radii and angles share its edges.
- **Watch**: three to five wedges hardly read as a curve; narrow steps beside liquid invite falls.

### perimeter-ledge

A band following a large room's or pit's outline at another height, so the middle reads as sunken and the edge as a gallery.
- **Numbers**: 48-200 wide (400-500 on big yards); 10-32 for a low rim, 64-192 for most galleries, 256-512 over pits. Inner corners often cut at 45 degrees.
- **Variants**: a full ring round a sunken arena with corner lifts (`community__remain1__REMAIN1_MAP06`); a U-shaped barred ledge over a pit (`plutonia__MAP15`); an aisle set apart only by a lower ceiling (`doom2__MAP32`); side galleries high above a nave (`tnt__MAP24`).
- **Does**: monsters on it fire down from all round; the player sees the space before committing; the lap becomes the route; a chamfered rim makes a big space read as a crater.
- **Look at**: `doom__E1M5` (nukage_72, room_75: a walkway 24 above slime on three sides); `plutonia__MAP15` (blood_126, room_127); `community__remain1__REMAIN1_MAP06` (room_98: a 384-high ring you enter on, look down from, then fight under).
- **Build**: the ledge sector is `[outer, inset(outer, w)]`, the floor inside `inset(outer, w)`; stairs or lifts join them.
- **Watch**: an even band round a square pit is a box with a shelf; barred ledges strand monsters behind long detours.

### bays

A row of recesses at a regular pitch along a wall, so the outline becomes a comb.
- **Numbers**: 32x32 notches and 64x64 closets through 96-192 alcoves to 350-700 apses; every 64-240 (usually 128), rows of 3 to 15. Bay floors often offset (+8-16, shelves +96-128, pits -128 to -256), ceilings lower, light different.
- **Variants**: closets that open together as an ambush (`tnt__MAP04`: twenty 64x64 closets along a 512x1280 hall); barred cells showing monsters before release (`plutonia__MAP31`); apses round a symmetrical hall (`plutonia__MAP09`); raised firing shelves (`community__fth666__FTH666_MAP07`).
- **Does**: danger from the edges, from many recesses at once; rhythm along a long hall; cover and item pockets off the middle; a theme at a glance (prison, temple).
- **Look at**: `tnt__MAP04` (room_361-381); `plutonia__MAP09` (room_0, room_12); `community__fth666__FTH666_MAP07` (room_2-9: eight 112-square alcoves 112 above the floor).
- **Build**: notch the outline's points, each bay its own sector where its floor, ceiling or light differ; `closet()` for a door disguised as wall.
- **Watch**: identical bays on every wall become a search; bays along a plain straight corridor still read as a tube.

### diagonal-run

A corridor, stair or channel at an angle to the grid (usually 45 degrees) joining rooms that sit on it.
- **Numbers**: 64-300 wide (mostly 96-200), up to about 2100 long, legs of 200-400 between jogs.
- **Variants**: a diagonal crossroads of four arms at a diamond centre (`doom__E2M2`); a chain of rotated-square steps (`tnt__MAP13`); a zigzag tunnel (`tnt__MAP05`); a diagonal hazard band across a square space (`doom__E1M9`, `doom2__MAP04`).
- **Does**: a shortcut across a ring or grid; a landmark among box rooms; bends hide the next space; a long straight one gives a sightline to its far end.
- **Look at**: `doom__E2M2` (room_41, room_43, room_44: arms meeting at a bright diamond); `doom2__MAP05` (room_36, room_80: a dark 192-wide tunnel at 45 degrees as a shortcut); `community__fth666__FTH666_MAP09` (diamond rooms on a causeway across a valley).
- **Build**: a corridor polygon at 45 degrees (whole vertices all along it); square off the ends where its doors go.
- **Watch**: when every joining space is skewed the route stops reading as a line.

### curve

A wall, floor edge or route drawn as a chain of short segments bending round a void, pool or room.
- **Numbers**: corridors 64-300 wide bending 90-180 degrees; apses to 768 across; 20-80 vertices in one sector, or chains of 5-40 segments at about 22 or 45 degrees. Stepped chains change 8-25 per segment.
- **Variants**: a bending corridor or ramp of chained trapezoids (`doom__E2M4`, `tnt__MAP14`); a corridor hooking round a void or hidden room (`tnt__MAP13`); a semicircular apse on a hall (`plutonia__MAP25`); curved liquid wrapping a structure (`doom__E4M8`).
- **Does**: hides what's ahead until the bend; keeps a centre in view all the way round; gives a building a silhouette.
- **Look at**: `doom__E4M8` (room_23, room_38: a D-shaped walkway wrapping lava round an octagon); `tnt__MAP14` (room_132, room_263: a 128-wide ramp bending through a half circle); `community__btsx_e1__BTSX_E1A_MAP32` (room_685: an apse with fans of wedge steps).
- **Build**: `arc(cx, cy, r, a0, a1, n)` points joined into outlines; a curved band is `arc(r_outer) + arc(r_inner)[::-1]`.
- **Watch**: a bend alone doesn't make a space good; chamfered corners only suggest a curve.

### chamfer

A room's corners cut by short diagonal walls, so a rectangle becomes an octagon or hexagon.
- **Numbers**: cuts of 16 on small cells, 64-128 in most rooms, 128-256 on halls 480-1024 across; almost all 45 degrees.
- **Variants**: one room cut on all four corners round a dais (`tnt__MAP01`); triangular corner sectors framing a walkway round a pool (`doom2__MAP06`); a chain of small chamfered cells (`doom__E4M6`); concentric chamfered sectors stepping toward the centre (`community__nos4dead__NOS4DEAD_E1M5`).
- **Does**: a shaped hub you recognise; a diagonal corner points at an exit or hides a secret door; ties a map's rooms into one architecture.
- **Look at**: `doom2__MAP06` (room_38, room_36); `doom__E4M6` (room_193-209: 128x112 cells with 16-unit cuts and alternating light); `community__nos4dead__NOS4DEAD_E1M6` (room_29, room_39: no room in the map is a box).
- **Build**: `chamfer(x1, y1, x2, y2, c)`; the sides stay axis-aligned for doors.
- **Watch**: a chamfer alone is cosmetic; pair it with height, pillars or light inside.

### stair-wrap

A stair or stepped walkway that turns round a central pit, pool, core or room while it climbs.
- **Numbers**: 290x290 shafts to 800-1500 arena rings; treads 32-64 deep, runs 32-128 wide; rises 8-16, 70-230 per wrap (416 in MAP15).
- **Variants**: a square-cornered spiral round a block (`doom2__MAP06`, `doom2__MAP15`); a ring of wedge treads round a round core (`tnt__MAP05`); a mirrored pair round both sides of a pool (`doom__E1M5`); a single switchback (`plutonia__MAP24`).
- **Does**: the centre stays in view while you change height; a large climb in a small footprint, ending above where you started; fights between turns of the same walkway.
- **Look at**: `doom2__MAP06` (room_157-172 round lava_168: 64x64 steps rising 8 each, spiralling inward); `tnt__MAP05` (room_141-142 round room_148: one full circle gaining 120 in a 290 shaft); `community__fth666__FTH666_MAP08` (one lap at 16 a step climbing 224 round a nukage pit).
- **Build**: `curved_stairs()` round a `regular()` core with the same centre, or `stairs()` runs on each side of a square core.
- **Watch**: single-tread ledges over open drops punish one misstep.

### sawtooth

A wall cut into a repeated run of notches, teeth or buttress bays.
- **Numbers**: notches 32-128 deep and wide, every 64-200 (bastions to 300-400). Square versions keep every edge on an axis; zigzags are mostly off-axis.
- **Variants**: square buttress bays down a corridor (`doom__E3M9`); 45-degree V-notches making a jagged outline (`doom__E4M6`); fins from alternate walls (`doom__E3M2`).
- **Does**: every notch is a cubby a monster steps out of; zigzags show a passage a section at a time; a castle or church rhythm; a jagged frame round one clean goal.
- **Look at**: `doom__E3M9` (room_42, room_44: a 137-vertex corridor with about 21 notches); `doom__E4M6` (room_70, lava_69: a starburst hall framing a square key island); `community__32innail__32INNAIL_MAP02` (room_19-26).
- **Build**: zigzag points in the outline.
- **Watch**: very fine notching adds vertices, not play.

### split-level

One open room whose floor is at two or more heights (shelf, pit, catwalk, terrace) with no wall between.
- **Numbers**: rooms 500x500 to 2480x1824; levels 56-144 apart (to 260 for second storeys); raised strips 48-312 wide.
- **Variants**: a raised pulpit over a hall reached by a stair (`doom__E1M1` room_41); a hall cut lengthwise into lanes at different heights (`doom2__MAP23`); a sunken court ringed by a rim (`tnt__MAP17`); a raised spine between two basins (`tnt__MAP24`).
- **Does**: from the upper level you see the room before fighting in it; monsters on shelves fire down; height becomes a route choice.
- **Look at**: `doom__E1M1` (room_41, room_42: a 256x192 platform 104 above a trapezoidal hall); `tnt__MAP24` (room_11, room_5: two 120-high plateaus round a chasm); `community__fth666__FTH666_MAP15` (room_89, room_202).
- **Build**: sectors at different floors inside one outline, joined by `stairs()` or `lift()`.
- **Watch**: look-alike halls joined only by lifts confuse (MAP05).

### interlock

A corridor or room bent into an L, U, C or spiral that wraps round another room, block or void, so shapes hook into each other.
- **Numbers**: wrapping bands 64-256 wide, mostly 128-200; clusters 450x500 to 3500x3500; steps of 8-64 between layers common.
- **Variants**: a corridor folding round the rooms it serves (`doom__E1M5`); nested brackets stepping down a level outward (`master__NESSUS_MAP07`); L-shapes forming a pinwheel round an octagon (`community__zone300__ZONE300_MAP32`).
- **Does**: shows the target from outside before you reach it; loops for flanking and more than one way back; the route doubles back past earlier places from a new side.
- **Look at**: `doom2__MAP03` (room_0, room_4: a sunken start square with an L-shaped floor wrapping two sides above it); `master__NESSUS_MAP07` (room_12, room_44: C-shaped halls stepping down 64 per layer); `community__resurge__RESURGE_MAP13` (room_0, room_23).
- **Build**: the wrapping outline shares edge vertices with what it wraps.
- **Watch**: same-width wrapped passages become a maze; a wrapper with no openings into what it wraps is a long walk back.

### overlook

A raised floor along the edge of a much lower open space, so the player sees down and across it first.
- **Numbers**: drops of 128-280 for balconies, 450-1900 for cliffs; ledges 32-192 wide, porches 200-400, galleries 1000-2500 long; edges often off-grid and lined with bars or posts.
- **Variants**: a walkway round the top of a hall reached by lifts (`doom__E3M3`); a porch over a yard with a way down (`community__zone300__ZONE300_MAP04`); a barred gallery the length of a lake (`community__btsx_e1__BTSX_E1A_MAP17`).
- **Does**: shows the next area, often the whole map, before going down; sets up a descent the player chooses; perches for monsters; scale.
- **Look at**: `doom__E3M3` (room_98, room_94: walkways 144 above an octagon's floor); `master__VESPERAS_MAP09` (room_215: a crescent ledge with sixteen pillars over a pit); `community__pe4_dt3__PE4_DT3_E4M9` (room_83).
- **Build**: a high sector beside a low one, railed with `SPECIAL_BETWEEN` bars or a sill; a drop the player can take needs a way back up unless the doc makes it one-way.
- **Watch**: under 48 high there's no view to speak of.

### courtyard

A large open-sky sector between or round buildings, its outline bent by diagonals and notches, the rooms opening onto it.
- **Numbers**: 1200-3600 on a side; sky 150-520 up; 25-420 vertices, 2-72 holes; small height changes inside (patches 8 lower, rock rings 16-48 up).
- **Variants**: a hub plaza with a centre post (`doom2__MAP18`); a yard wrapping a building (`community__jpcp__JPCP_MAP17`); a landscape field of patches and outcrops (`community__vv__VV_MAP04`).
- **Does**: shows several entrances at once, so the route is planned by looking; opens up after cramped halls; makes interiors read as buildings in a landscape.
- **Look at**: `doom2__MAP18` (room_0, room_33: a 35-vertex sky polygon with no right angles and a central post); `tnt__MAP13` (room_77: a 129-vertex street); `community__vv__VV_MAP04` (room_456, room_604).
- **Build**: one sector with `SKY` ceiling, the buildings and outcrops as holes or pillars.
- **Watch**: a plain rectangle with a thin border is a bigger box.
