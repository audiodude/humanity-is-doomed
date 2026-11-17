# Cursed Altar (`cursed_altar`)

## Concept

**You walk the length of a corrupted cathedral down one axis, from its doors to the altar at the far end of the choir, and taking the skull from the altar drops every pillar in the nave behind you, so the walk back out to the doors is a different hall full of what was sealed in them.**

- Plan: `linear`. One axis from the narthex (south) to the apse (north). The way to the choir is a horseshoe off the nave's west side, through the cloister and down into the crypt, coming up into the choir behind the rood screen. The way back is straight down the nave (the recessional) to the exit door, which is in the narthex where the map starts.
- Theme: gothic cathedral turned hellish. The nave is green marble, the cloister overgrown stone, the crypt dark block, and the choir and apse riveted flesh. Over the garth, the graveyard and the porch, the red hell sky (`SKY3`, set in UMAPINFO).
- Difficulty: medium-hard. Roster up to hell knights and cacodemons, with a baron on the altar (a hell knight on easy). Pistol start.
- Slot: MAP01 of Cathedral of Pain (`wads/CATHEDRAL.WAD`, set `levels/sets/cathedral.py`). Pitched and first built as The Procession.

## Exemplars

| Map | Move and sectors | What it borrows, and what changes |
|---|---|---|
| `tnt__MAP08` | funnel: room_174 to room_201, a 20-step stair whose walls splay about 14 degrees, widening from 128 to 768 into the octagon | The reveal down a widening stair. Here it is 7 steps of 16, 64 deep, the walls splaying at 2:1 (about 27 degrees), from the 128-wide great doors to a 576-wide mouth. The view runs past the pillars to the altar, about 3000 units away. |
| `plutonia__MAP09` | bays and pillar-field: room_0, the chamfered nave with octagonal chapels room_12 on both long sides and rows of octagonal pillars room_124 | A pillared nave with polygonal chapels. Here the chapels are on one side only (east); the west side has the cloister instead, so the nave isn't mirrored. The pillars are octagons 144 across that are also the trap's closets. |
| `plutonia__MAP19` | stair-curved: room_4 to room_11 and room_29 to room_33, two arcs of 8-unit treads hugging a blood pit at -128, one climbing and one descending | Twin stairs round a blood pit. Here both arcs climb from one foot at the south, 16 a step, round opposite sides of a 16-sided pit to meet at the dais in the north. |
| `doom2__MAP07` | walls that drop to open the fight | The revisit changes the space: the nave's pillars lower into the floor. |

## Route

1. **Porch** (exit). Sky, floor 120 (a step down out of the church), about 384x256 with angled sides. Reached only through the red door; the exit switch (`SW1EXIT`) is in a niche in its far wall.
2. **Narthex** (start). `chamfer(-320, 0, 320, 384, 64)`, floor 128, ceiling 256, wood panelling, light 160. The start is at (0,128) facing north toward the great doors (`BIGDOOR7`). Behind the player in the south wall is the red door (`BIGDOOR6` on red-key tracks, a red torch either side): the way out, seen in the first seconds. No monster can see the start. Pickups: the shotgun, shells and a stimpack.
3. **Great doors** (use, DR) at (0,384). Opening them is **the reveal**: the funnel stair widening down into the nave, two rows of octagonal pillars, the rood screen's bars at the far end, and beyond them the lit altar on its dais, 3000 units off, with the red skull on it.
4. **Funnel stair**. 7 trapezoid steps, 64 deep, 16 down each (112 to 16), walls splaying from 128 to 576 wide at 2:1. Ceiling 320. The nave's monsters below are deaf and face the altar; the nave and its aisles are one sound zone, so the first shot wakes them all, each as soon as it can see you.
5. **Nave**. 992x1520 at floor 0, ceiling 384, light 144, with five octagonal pillars (`regular(±400, y, 72, 8)`, 144 across) down each side. The pillars are sealed shells (floor 384) round octagonal closets. Fight: zombiemen and shotgunners (fodder) spread down the nave, two demons near the screen (meat shields), imps in both aisles. Leaving: open to both aisles, the screen blocks the north.
6. **West aisle** (16, ceiling 176, a step up between the pillars; brighter, 160) and **east aisle** (0, ceiling 176, dark, 112). Low roofs under the nave's arcade wall. The west aisle has the cloister door, the baptistery passage and the reliquary secret. The east aisle has the two chapels.
7. **Baptistery** (optional, west of the aisle's south end): `chamfer(-992, 928, -736, 1184, 64)` at 16 with a raised octagonal font of water (`regular(-864, 1056, 64, 8)`, 40, glowing). Chaingun beside the font; 2 zombiemen and an imp.
8. **Cloister door** (DR, wood) from the west aisle at (-640,1648), into the cloister's east walk.
9. **Cloister**. A ring walk (`chamfer(-1664, 1200, -768, 2096, 128)` with the garth as its hole), floor 16, ceiling 160, round an open-sky **garth** (`inset(..., 160)`, grass at 0). In the garth's middle a **pool** (water, -8, `regular(-1216, 1648, 208, 8)`) round the **fountain** (`regular(-1216, 1648, 104, 8)`, 16). **The yellow key** sits on the fountain, seen from the cloister door as you come in. Fight: 4 imps in the garth, 2 demons and a spectre on the walk. Taking the key (W1 on the fountain's edge) opens four closets in the walk's outer walls (bays: two in the west wall, two in the north): imps, a demon, and a hell knight on UV. The fountain is on open ground, so the closets come at you across the garth from three sides.
10. **Chapter house** (optional, off the cloister's south walk): `regular(-1216, 960, 208, 8)` at 16, ceiling 272. Green armor, a cacodemon and 2 imps.
11. **Yellow door** at (-1216,2096) on the cloister's north walk, then the **crypt stair**: 5 steps of 80, 16 down each (0 to -64), 128 wide, going north. Light falls from 144 to 96.
12. **Crypt**. `chamfer(-1536, 2544, -896, 3184, 96)` at -80, ceiling 48 (128 high), light 80, with two flickering lamp strips across it (light-shapes). A 3x3 grid of square pillars. Fight: 3 spectres (the dark is their job), 2 imps, a chaingunner by the stair up. The ossuary secret is behind the west wall.
13. **Crypt stair up**: 4 steps of 48, 16 up (-64 to -16), then a door (DR) into the choir's west wall at (-640,2816).
14. **Choir**. 1280x768 at 0, ceiling 384, light 128, chamfered south corners, riveted flesh walls. In its middle the **altar pit**: a 16-sided blood pit (`regular(0, 2848, 224, 16, -90)`, -8, damage 5, light 192), ringed by **twin curved stairs** (`curved_stairs(..., r1=224, r2=352, ...)`, 8 steps of 16 per side, 16 to 128). Both start at one foot at the south (0,2496), 64 in front of the screen's sill, and climb round opposite sides of the pit to meet at the dais. The foot steps are 24 above the pit, the only way out of it; the two pit edges there block monsters, so walking monsters can't drop into the pit and get stuck. Fight: a **baron** at the top of the stairs (a hell knight on easy), imps on the dais, a cacodemon over the pit. You arrive from the west, below them. The baron is deaf and faces the choir door; the screen blocks the nave's noise and the nave is behind him, so he wakes only when you come through the door (checked in the engine from the middle of the nave, both ends of the screen, the crypt and the stair at the door, standing quiet and firing).
15. **Dais and apse**. Floor 144, ceiling 320, light 192 flickering. The apse is a half-disc (`arc(0, 3200, 448, 0, 180, 8)`). The **altar** is a pedestal `rect(-64, 3392, 64, 3520)` at 168 with the **red skull key**. **The set piece**: taking the key (W1 on the altar's edge) lowers all ten pillar shells in the nave and the sill in the rood screen (one tag, `W1_FLOOR_LOWEST`, 1 unit a tic: the sill is open in 2 s, the pillars take 11 s to sink). The nave becomes an open hall, and what was sealed in the six pillars nearest the screen (two hell knights, one on UV only; two cacodemons on HMP and UV, imps on easy; two demons) comes up through the screen at the foot of the twin stairs. They face north, at the altar: sealed in, they hear nothing, so they wake by seeing you as their pillars sink. You hold the dais and fight them up the two arcs. The four southern pillars hold supplies for the way out: a box of bullets, a medikit, a box of shells, shells and a stimpack.
16. **Recessional**. Down the stairs, through the open screen, down the changed nave, up the funnel stair, through the narthex and the red door to the porch and the exit switch.
17. **East chapels and the graveyard** (optional, off the east aisle). Two wood-panelled octagonal chapels (`regular(816, y, 156, 8)`, 8). Chapel A's east door opens on a **graveyard**: an organic open-sky yard (grass at -8, 16 vertices, walled in grey marble) with 11 headstones (raised blocks, cover) and a **mausoleum** (a chamfered room standing in it, as a hole) holding the super shotgun. Fight: 3 imps and a cacodemon in the yard, a spectre in the mausoleum. There is no rocket launcher in the map.

## Sketch

Drawn by `python3 scripts/tools/sketch.py levels/designs/cursed_altar.md` (`levels/designs/cursed_altar.svg`): no crossings; off-axis share of line length 0.34; 7 of 32 larger spaces axis-aligned. Door strips are drawn as spaces (`door` tag); steps are drawn singly for the funnel and as two half-rings for the curved stairs (8 steps each in the build); the bays, lamp strips, crypt pillars and headstones are only in the build.

```sketch
# name     floor/ceil tags        : outline (map units)
porch       120/384    sky         : -192,-48 192,-48 192,-176 96,-304 -96,-304 -192,-176
d_exit      128/256    door        : rect(-64, -48, 64, 0)
narthex     128/256                : chamfer(-320, 0, 320, 384, 64)
d_great     128/256    door        : rect(-64, 384, 64, 432)
step1       112/320                : -64,432 64,432 96,496 -96,496
step2       96/320                 : -96,496 96,496 128,560 -128,560
step3       80/320                 : -128,560 128,560 160,624 -160,624
step4       64/320                 : -160,624 160,624 192,688 -192,688
step5       48/320                 : -192,688 192,688 224,752 -224,752
step6       32/320                 : -224,752 224,752 256,816 -256,816
step7       16/320                 : -256,816 256,816 288,880 -288,880
nave        0/384                  : -496,880 -288,880 288,880 496,880 496,2400 64,2400 -64,2400 -496,2400
aisle_w     16/176                 : -512,880 -496,880 -496,2400 -512,2400 -640,2272 -640,1008
aisle_e     0/176                  : 496,880 512,880 640,1008 640,2272 512,2400 496,2400
pil_w1      384/384                : regular(-400, 1136, 72, 8)
pil_w2      384/384                : regular(-400, 1392, 72, 8)
pil_w3      384/384                : regular(-400, 1648, 72, 8)
pil_w4      384/384                : regular(-400, 1904, 72, 8)
pil_w5      384/384                : regular(-400, 2160, 72, 8)
pil_e1      384/384                : regular(400, 1136, 72, 8)
pil_e2      384/384                : regular(400, 1392, 72, 8)
pil_e3      384/384                : regular(400, 1648, 72, 8)
pil_e4      384/384                : regular(400, 1904, 72, 8)
pil_e5      384/384                : regular(400, 2160, 72, 8)
screen_w    0/384                  : rect(-496, 2400, -64, 2432)
gate        72/384                 : rect(-64, 2400, 64, 2432)
screen_e    0/384                  : rect(64, 2400, 496, 2432)
choir       0/384                  : -640,2560 -512,2432 -496,2432 -64,2432 64,2432 496,2432 512,2432 640,2560 640,3200 448,3200 135,3173 249,3097 325,2983 352,2848 325,2713 249,2599 135,2523 0,2496 -135,2523 -249,2599 -325,2713 -352,2848 -325,2983 -249,3097 -135,3173 -448,3200 -640,3200
stair_w     16/384                 : 0,2496 -135,2523 -249,2599 -325,2713 -352,2848 -325,2983 -249,3097 -135,3173 0,3200 0,3072 -86,3055 -158,3006 -207,2934 -224,2848 -207,2762 -158,2690 -86,2641 0,2624
stair_e     16/384                 : 0,2496 135,2523 249,2599 325,2713 352,2848 325,2983 249,3097 135,3173 0,3200 0,3072 86,3055 158,3006 207,2934 224,2848 207,2762 158,2690 86,2641 0,2624
pit         -8/384     liquid      : regular(0, 2848, 224, 16, -90)
dais        144/320                : -135,3173 0,3200 135,3173 448,3200 414,3371 317,3517 171,3614 0,3648 -171,3614 -317,3517 -414,3371 -448,3200
altar       168/320                : rect(-64, 3392, 64, 3520)
bap_pass    16/144                 : rect(-736, 1008, -640, 1120)
baptistery  16/208                 : chamfer(-992, 928, -736, 1184, 64)
font        40/208     liquid      : regular(-864, 1056, 64, 8)
d_cloister  16/144     door        : rect(-768, 1584, -640, 1712)
cloister    16/160                 : chamfer(-1664, 1200, -768, 2096, 128)
garth       0/320      sky         : inset(chamfer(-1664, 1200, -768, 2096, 128), 160)
pool        -8/320     sky         : regular(-1216, 1648, 208, 8)
fountain    16/320     sky         : regular(-1216, 1648, 104, 8)
d_chapter   16/144     door        : rect(-1280, 1152, -1152, 1200)
chapter     16/272                 : regular(-1216, 960, 208, 8)
d_crypt     16/144     door        : rect(-1280, 2096, -1152, 2144)
crypt_down  -64/144                : rect(-1280, 2144, -1152, 2544)
crypt       -80/48                 : chamfer(-1536, 2544, -896, 3184, 96)
crypt_up    -16/112                : rect(-896, 2752, -704, 2880)
d_choir     -16/112    door        : rect(-704, 2752, -640, 2880)
chapel_a_in 8/176                  : rect(640, 1268, 672, 1388)
chapel_a    8/200                  : regular(816, 1328, 156, 8)
chapel_b_in 8/176                  : rect(640, 1908, 672, 2028)
chapel_b    8/200                  : regular(816, 1968, 156, 8)
sacristy    8/136      secret      : rect(976, 1888, 1232, 2048)
d_grave     8/136      door        : rect(976, 1264, 992, 1392)
graveyard   -8/320     sky         : 1008,1264 1008,1392 1072,1520 1136,1648 1264,1776 1440,1840 1632,1824 1792,1728 1888,1568 1904,1376 1840,1200 1712,1072 1536,992 1360,976 1216,1024 1104,1136
mausoleum   8/136                  : chamfer(1440, 1312, 1648, 1536, 32)
ossuary     -80/32     secret      : rect(-1744, 2784, -1568, 2944)
d_reliq     16/144     door        : rect(-656, 2176, -640, 2240)
reliquary   16/144     secret      : rect(-784, 2144, -656, 2272)
* 0,128 start
* 0,-296 exit switch
* 0,272 shotgun
* 0,3456 red skull key (trap: pillars drop, gate sinks)
* -1216,1648 yellow key on the fountain (trap: cloister bays open)
* -1216,2120 yellow door
* 0,-24 red door
* -864,976 chaingun by the font
* 1104,1968 berserk (secret)
* -1216,2192 crypt stair
* 1528,1424 super shotgun
```

## Materials

| Area | Walls | Trim | Flats (floor / ceiling) | Reason |
|---|---|---|---|---|
| Narthex, porch | `WOOD5` panelling; porch outside in `STONE` | `SUPPORT3` round the great doors; the red door's `DOORRED` tracks | `FLAT5_2` / `CEIL1_1`; porch `FLAT5_4` / sky | The wooden entrance hall; the porch is outdoors. |
| Funnel stair, nave, aisles (base) | `MARBLE1`; the pillars' faces `MARBLE2` (skull band); the screen's sill `MARBLE3` | `SUPPORT3` at the great doors, the cloister door and the aisle ends | `DEM1_5` nave, `DEM1_6` aisles and stair treads / `CEIL5_2` | One green-marble church holds the map together; `MARBLE1` is the most-used wall texture (26%). |
| Baptistery | `MARBLE1` with `MARBGRAY` round the font | `SUPPORT3` at the passage | `DEM1_6`, font `FWATER1` / `CEIL5_2` | Part of the church, with a water font. |
| Cloister walk, chapter house | `GSTONE1`; the garth's walls `GSTVINE1` | `SUPPORT3` at the doors | walk `FLOOR7_2`, garth `GRASS2`, pool `FWATER1`, fountain `DEM1_5` / walk `CEIL5_2`, garth sky | The overgrown outside: green stone and vines. The pool is water, not hazard. |
| Crypt and its stairs | `STONE2`; ossuary door `GSTSATYR` | `SUPPORT3` at the yellow door (yellow key strip `DOORYEL` on the track) | `FLOOR6_2` / `CEIL3_6` | Below ground: dark grey block, a different place. |
| Choir | `SKINMET2` riveted flesh | `SKINEDGE` where flesh meets marble (screen ends, choir door) | `DEM1_5`; pit `BLOOD1`; stair treads `DEM1_6` with `MARBLE3` risers / `CEIL5_2` | The corrupted end of the church: hell has grown through the walls behind the screen. |
| Dais and apse | `SKINFACE` on the apse arc; altar `METAL` sides (pedestal) | `SKINEDGE` | `DEM1_2` (pentagram) / `CEIL5_2`; altar `TLITE6_1` | The focal wall, seen from the narthex down the whole axis. |
| East chapels, sacristy | `WOOD1` with one `WOODGARG` panel per chapel | `SUPPORT3` at the openings | `FLAT5_2` / `CEIL1_1` | Wood-panelled side chapels; the panel that's off-centre in chapel B is the sacristy's secret door. |
| Graveyard, mausoleum | `MARBGRAY` (the yard's wall, headstones and the mausoleum) | the mausoleum's door is recessed, so its `WOODMET1` face has a plane of its own | `GRASS1` / sky; mausoleum `FLAT1` / `CEIL3_6` | Outside the church: grey stone and grass. |

## Secrets

1. **Sacristy** (behind chapel B's east wall): the chapel's `WOODGARG` panel on that face is a secret door, its face shifted off the wall pattern by the builder's `SECRET_HINT`. Reward: berserk, 2 boxes of shells, a demon inside. It held the super shotgun until tmoney found that too easy a gimme; the super shotgun moved to the mausoleum.
2. **Ossuary** (behind the crypt's west wall): a `GSTSATYR` face set 8 back in a `STONE2` wall, the only face in the crypt. Reward: soulsphere.
3. **Reliquary** (behind the west aisle's outer wall near its north end): a 64-wide panel of `MARBLE2` (skull band) in the aisle's `MARBLE1` wall, shifted off the wall pattern by `SECRET_HINT`. Reward: armor and a backpack.

## Targets

Measured by the build (DOOM II medians in brackets). All met.

| Target | Build | Where it comes from |
|---|---|---|
| Optional share of area ≥ 0.3 [0.5] | 0.30 | The east aisle, chapels, graveyard and mausoleum, the sacristy, the baptistery, the chapter house, the reliquary and ossuary. It was 0.23 before the graveyard was added. |
| Distinct floor heights ≥ 15 [23] | 20 | Narthex 128, porch 120, funnel 112 to 16, nave 0, aisles/walk 16, chapels 8, pool and graveyard -8, crypt stairs 0 to -64, crypt -80, curved stairs 16 to 128, dais 144, altar 168, sill 72, pillars 384. |
| Secrets ≥ 2 [4] | 3 | Sacristy, ossuary, reliquary. |
| Light-effect sectors ≥ 3 [9] | 5 | Altar (glow), font (glow), crypt lamps (flicker, 2), dais (flicker). |
| Deaf share (UV) ≥ 0.2 [0.42] | 0.29 | Nave, crypt and the choir's baron; closet and trap monsters are not deaf. |
| Most-used wall texture 0.2–0.45 [0.3] | 0.26 | `MARBLE1` in the funnel, nave and aisles. |
| Rule-2 seams with a border texture ≥ 0.5 [0.31] | 0.54 | `SUPPORT3` at the doors, `SKINEDGE` at the choir door, recessed secret and mausoleum doors. The one bare seam left is the ossuary door's satyr face in the crypt's west wall, which is its hint. |
| Off-axis share of line length ≥ 0.11 [0.23] | 0.31 | The funnel stair, octagonal pillars, chapels, chapter house and fountain, the 16-sided pit, the curved stairs, the apse arc, the graveyard and every chamfered corner. |
| Axis-aligned share of rooms ≥ 128×128 ≤ 0.5 [0.39] | 0.29 | The nave (shaped by its pillars), the crypt stairs, the altar pedestal and the three secrets. |
| Nearest monster to the start ≥ 300 [300] | 1,116 | The nearest nave monster is past the funnel stair. |
| Whole-map symmetry ≤ 0.65 [0.54] | 0.49 | The axis is mirrored, but the cloister, crypt, baptistery and chapter house sit only on the west, and the chapels and graveyard only on the east. |

Misses, left as they are: 56 monsters on UV against a median of 112, and 5.8M units² against 8.4M (a short map). Long-range hitscan peaks at 32/s on the first leg (median 0, IQR to 35.5; the warning is at 88.4), from the zombiemen and shotgunners down the nave's length; it was 42/s before a shotgunner by the screen became an imp.

### Playtest (2026-11-16)

- **Wiring**: 26 checks, 0 fails (`levels/playtests/cursed_altar.playtest`): every door, both key traps, the three secrets, the pillars and the sill sinking, and the exit.
- **Resource curve** (UV, pistol start), final: thorough ratios 2.98 / 2.70 / 3.00 on the three legs (yellow key, red skull, exit); detour 1.65 / 1.83 / 1.83. Overall ammo damage per monster HP 2.67, at the top of the DOOM II IQR (1.37-2.73), on purpose (next point). The static curve counts the baron on the first leg, because from the dais he could shoot along the nave; in the engine he doesn't wake until you reach the choir door.
- **Ammo starvation** (found by tmoney playing UV in dsda-doom: died twice out of ammo, the second time knowing where the backpack was). The sound zoning lengthened the critical path through the nave and the yellow-key leg's detour curve fell to 0.85 (-710 ammo damage left), which wasn't re-read after that change; it had been 1.06 before, already only 6% spare at a 100% hit rate. The crunch is the cloister: 1,460 HP on UV (a hell knight, three demons, a spectre, six imps) with 8 shells there, after the nave. 21% of the map's ammo damage is in the secrets (the sacristy alone holds 52 shells with the super shotgun), and 5 rockets and 20 cells count toward the ratio but are nearly useless (the launcher is in the optional graveyard; no cell weapon). Fix: a shell box on each of the cloister's walks (the west one was easy/HMP only, with 4 shells on UV) and three boxes of shells down the north nave and the west aisle, +48 shells on UV, all on the way to the key. Counting zone by zone along the route (no optional rooms, no secrets), the old layout broke even at a 60% hit rate and ran short in the cloister at 50%; the new one has about 900 damage spare at 50%. The fight bot missed it: it aims far better than a person, and it starved once in three runs.
- **Fight runs**, seeds 1-3, after the fixes: 10, 7 and 7 deaths, none in the opening (it had 2-3 per seed on the funnel stair before the sound zoning and the shotgun's move); kills 56, 55, 56; ammo left 60, 14 and 55 shells. One or two deaths per section, all combat but one starved (in the optional graveyard, seed 2). The nave's two halves and the cloister's bays cost the bot most: crossfire it never retreats from, the bot's known weak spot, where a player has the funnel and the cloister's doors for cover. Two skipped steps: the bot fell off the curved stairs, once to the choir floor and once into the pit (the pit's way out is the stairs' foot).
- **Fight runs after the ammo fix**, seeds 1-3: 4, 3 and 9 deaths, none starved; ammo left 56, 81 and 56 shells.
- **After the rename** (the baron, the super shotgun in the mausoleum and a berserk in the sacristy, no launcher, the nave one sound zone, the trap's monsters in the northern pillars, monster-blocking pit edges), seeds 1-3: 4, 10 and 12 deaths, none starved; shells left 58, 68 and 64. Seed 3's four hazard deaths are the bot walking into the altar pit during the trap fight, its known weak spot: the pit's way out is the stairs' foot. Wiring 26 checks, 0 fails.
- **Explore runs**, seeds 1-3: exits at 2:49, 2:50 and 2:39, walking 1.9-2.0 times the critical path and seeing 99-100% of the map. The one long stretch (about 1:51, from the yellow door to the altar) recurs on every seed. It is spent in the graveyard, the cloister walk, the mausoleum and the crypt: the explorer clears the optional east side and the chapter house before taking the open crypt. Intended: those are the side areas, and the crypt door is the yellow door the key just opened.

## Concepts considered

Pitched with the atlas; all five plans differ from each other and from NUKAGE's.

- **The Knot** (multi-loop, gothic keep): a keep wound round a raised octagonal sanctum you enter three times, from three heights; the floor drops into a ring pit on the last. After E3M3 and E1M3.
- **Blood Archipelago** (open): five blocks at different heights in a blood chasm, joined by walkways and a switchback causeway. After Plutonia MAP27 and MAP26 and DOOM II MAP14. Risk: an open map wakes all at once.
- **The Procession** (linear, chosen by the user; built, and renamed Cursed Altar): see above.
- **The Slant** (tree, starport): a hangar turned 45 degrees across a square base, with berths along its toothed wall leading to the branches. After TNT MAP12 and E2M2.
- **The Quarry** (ascent): from a flooded quarry pit up contour terraces and a switchback canyon to a ruined fort. After SUBTERRA, BAUHAUS MAP02 and E4M2. Too close to Nukage Outskirts' climb.

## Build risks

- **Pillar closets**: each pillar is a shell sector (two loops: `regular(.., 72, 8)` and `regular(.., 56, 8)`) at floor 384, ceiling 384, round a closet (`regular(.., 56, 8)`, 0/384). The closet's inradius is about 52, so it holds a monster of radius up to about 44 (a hell knight, a demon or a cacodemon, not a mancubus). `W1_FLOOR_LOWEST` takes each shell to its lowest neighbour, 0. Concentric `regular()` calls with the same `n` nest exactly.
- **One trigger, two jobs**: the altar's W1 line lowers both the shells and the screen's sill, so they share a tag; nothing else may carry it. The sill is 72 high, not a full block: a 128-wide block on the axis hid the altar from the nave.
- **Curved stairs**: the pit is `regular(0, 2848, 224, 16, -90)` so its vertices fall on `arc()`'s points every 22.5 degrees from 270; the two `curved_stairs()` calls (270→90 clockwise and -90→90) share them and their outer arc is the choir's notch. Steps are about 113 deep on the middle radius. Steps 3 and up are more than 24 above the choir floor, so the only way onto the stairs is at their foot.
- **Pit softlock**: the pit at -8 is enclosed by the stairs. The two foot steps at 16 are 24 above it, so the player can climb out there and nowhere else.
- **Doors on angled walls**: none. The chapter house's and the chapels' doors are on the axis-aligned faces of `regular(.., 8)` octagons. The fountain's trigger lines are angled, but triggers don't care.
- **Sound**: with the nave and choir open to each other, opening the great doors woke the whole nave, plus imps on the dais that could see down the axis, and the bot died 2-3 times on the funnel stair on every seed. The screen's lines now block sound, so the nave's noise stays out of the choir and the choir fight's out of the nave, and the choir's monsters face away from the nave. For a while the nave was also cut into two sound zones at y 1520-1536; tmoney then found a pillar cacodemon in the south half still asleep, back turned, after the altar fight, because the south zone never heard anything and the pillar monsters faced the altar from behind its back. The nave is one zone again, and the trap's monsters are in the six northern pillars facing the altar, so they wake by sight as their pillars sink: all six wake and reach the choir within 35 s of taking the skull, without a shot (checked in the engine). The shotgun stays in the narthex, in hand before the doors open.
- **Long sightline**: the axis view is about 3000 units. Keep hitscanners within 768 of where the player stands to fight them, and none on the dais facing the nave.
- **Exit marker**: `EXITDOOR` is a tech panel, wrong for a church, and an `EXITSIGN` can't sit over a 128-tall door in a 256 room without a picture-fit failure; the red door is a wooden `BIGDOOR6` flanked by red torches instead.
