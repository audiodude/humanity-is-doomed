# Nukage Meltdown (`nukage_meltdown`)

## Concept

**You climb down a staircase of nukage waterfalls, shelf by shelf, to the meltdown lake at the bottom, where the Cyberdemon wades in front of the cracked reactor dome.**

- **Shape:** a descent. The plant's emergency outfall runs down a canyon in four terraced shelves. Each shelf has a trough at the back that catches the falls from the shelf above, a dry bank across the middle, and a pond at the front that pours over a railed lip onto the next shelf down. At the bottom the outfall drains into the reactor's cooling lake, which the meltdown has turned to nukage. The route switchbacks: along a bank, then down through a building at its end, then back along the next bank the other way. It never returns to a room it has left. The last two steps down are drops you can't climb back up: through a breach in shelf 3's bank, and over the dam's floodgate into the lake.
- **Theme:** the plant has gone critical. Nukage pours out of the outfall at the top, fills every pond, falls over every lip, and ends up in the lake, the biggest body of nukage in the set (about 3.5M units², nearly twice MAP08's basin). The reactor dome stands in the lake, its hatch shut and its core melted down. Red alarm lamps blink in the operations block where you start. The light rises as you go down, toward the glow.
- **The reveal, in two parts.** From the start you step onto the operations balcony and see the whole map: below you four glowing ponds step down the canyon, the floodgate sits in the middle of the dam, and beyond it the dome. A gap in shelf 3's railing (the breach) is visible from the start, and the red door at the far end of shelf 2. The outfall's falls show once you're down on shelf 1. The Cyberdemon is a hint, not a sight: a speck over the dam at most, and his roar and footsteps as you come down. By the time the gatehouse hands you the BFG you know what's in the lake. **The arch-vile is the real reveal:** as you drop over the floodgate the hatch opens, and through it, past the Cyberdemon, he stands lit in the exit alcove at the back of the dome, too far off to attack yet, giving you the seconds to get to cover.
- **Gating:** the first two steps down are free: the stairwell, then the sluice house's stair. Shelf 2 is gated by the red key, held in a valve tower out in the pond. Then come a lift, a breach you drop through (or the optional settling house down beside it), and the floodgate. The floodgate's switch is in the gatehouse at the west end of the dam. The final drop rides the dam's falls 240 down into the lake.
- **Difficulty:** the hardest map in the set. The per-space counts below sum to 40/63/84 monsters on easy/HMP/UV (ratios 0.48/0.75, counting easy's stand-ins) and about 20,400 monster HP on UV, 4,000 of it the Cyberdemon, before resurrections. The heavy share is 25%: the Cyberdemon, an arch-vile, 5 revenants, 2 mancubi, 2 arachnotrons, 9 hell knights and a baron. **Debut: the Cyberdemon**, in the lake. **The arch-vile** returns from MAP08, in the dome, to raise the Cyberdemon's support.
- **Slot:** MAP09 of `NUKAGE.WAD`, the last map. UMAPINFO is written as a string body, because it needs `endcast = true`, a multi-line `intertext` and a `bossaction`; the module's dict form quotes every value. The body is `UMAPINFO` in `levels/nukage_meltdown.py`: the level name, the slot's own track `D_IN_CIT` (as on every map in the set), the end text (`intertext`, one quoted string per line) and the cast call after it, and `bossaction = Cyberdemon, 103, 7`, which opens the shutter over the exit console (tag 7) when the Cyberdemon dies. MAP08's entry has no `next`, so MAP08 leads here. Ports that don't read UMAPINFO never open the shutter (see Build risks).

How it differs from the set:

| Map | Shape in a phrase |
|---|---|
| MAP01 Nukage Junction | the template: courtyard hub, one wing per key |
| MAP02 Nukage Crossing | two banks of a canal, joined by a sluice gate that sinks into a bridge |
| MAP03 Nukage Core | a spiral climb around a reactor to the crown |
| MAP04 Nukage Divided | a fork into two wings that never meet, keys crossed |
| MAP05 Nukage Drain | a ring of walkways raised one by one out of a flooded reservoir |
| MAP06 Nukage Undercurrent | one hall crossed twice: over it, then under it |
| MAP07 Nukage Storage | one hall in two states: a maze on the way in, an arena once you sink it |
| MAP08 Nukage Lockdown | a loop away from the exit you can see, closed by wading back through the spill |
| **MAP09 Nukage Meltdown** | **a descent down a staircase of nukage falls to the lake it all drains into** |

It is the set's first descent, the reverse of MAP03's climb. MAP05 and MAP08 both put one nukage body in the middle and route you round it. Here the nukage *is* the route: you follow it down every lip, and the lake isn't something you circle but the floor of the final fight.

## Route

Heights are floor/ceiling. Monster counts are UV (HMP, easy), and "deaf" means the ambush flag. Every outdoor monster is deaf and faces south, away from the start and from the shelves above it, unless noted. Coordinates are in the rectangle table under the sketch.

1. **Operations deck (OD, OB)**, the start. 768×320 at 832/960, TEKGREN control room; its south strip is an open balcony (OB, 768×64, sky) with a railing over the drop. The player starts at (1024,2688) facing south. Light 176; two red lamp strips in the ceiling blink (the meltdown alarm).
   - **Visible:** everything (see Concept) but the outfall: its falls face south in the wall plane the balcony stands behind, so they show from shelf 1. Shelf 2's valve tower, with something glinting on the pillar beside it (secret 2), stands in the pond below the first lip, right of the line down to the breach and the floodgate.
   - **Gate:** the west door to the corridor is the only way out.
   - **Encounter:** none. Nothing awake can see the balcony.
   - **Pickups:** shotgun at the balcony rail (about 100 from the start), so taking it walks you into the view; 4 shells and a stimpack on the consoles at the deck's front ends.
2. **Corridor and stairwell (OC, SW, SWL).** The corridor runs west 1024 at 832, then seven 24 steps (48 deep) go down south to a landing at 640. CEMENT7, light 128.
   - **Encounter:** 2 zombiemen (1, 1) and 2 imps (1, 1) on the landing, deaf, facing the door: the first shots of the map.
   - **Pickups:** box of shells, clip.
   - **Gate:** the landing's east door onto shelf 1.
3. **Shelf 1 (S1T, S1B, S1P).** 2048 long: a trough (64 deep, 624), the bank (192, 640), the pond (256, 624). Sky 1024, light 160. The outfall's falls (x 1536..1792) pour from the plant into the trough behind the bank.
   - **Visible:** over the railing, shelf 2 directly below with the valve tower and the red door at its far west end, and the rest of the cascade.
   - **Encounter:** 4 imps (3, 2) along the bank, kept out from under the balcony (more than 300 from the start); 2 demons (2, 1) by the sluice house door at the east end, the meat shields in the way; a cacodemon (1, 0) over shelf 2's pond below the lip. It fires up at you over the railing and follows you down the cascade.
   - **Pickups:** box of shells, medikit; armor bonuses along the trough (in the nukage, optional).
   - **Gate:** the sluice house door at the bank's east end.
4. **Sluice house (B1G, B1S, B1P, B1M).** A gallery at 640/768 (BROWN1, light 144) runs along the north and east sides of the machine room, which lies open 128 below it (512/800, 512×640, BROWN96 with BROWNPIP, light 96, flickering). A stair of eight 16 steps runs down the east side to a passage into the machine room.
   - **Encounter:** 2 imps (1, 1) on the gallery. In the machine room: 2 spectres (2, 1) in the dark, 2 demons (2, 0), 2 shotgun guys (1, 1) on a machine plinth, with short sightlines inside. A hell knight (1, 0; easy: an imp) stands in the passage at the stair foot, blocking the way down.
   - **Pickups:** **super shotgun** on the control desk in the gallery's north-east corner, in view from the door; box of shells, medikit.
   - **Gate:** the machine room's west door onto shelf 2. You can drop off the gallery's edge into the machine room instead of taking the stair.
5. **Shelf 2 and the valve tower (S2T, S2B, S2P, FB, VTI).** Bank 512, trough and pond 496, sky 896, light 176. You come out at the east end. Shelf 1's pond pours over the full width of the lip into the trough behind the bank, in one sheet of falls.
   - **Visible:** the red door at the far west end of the bank (door before key: it also shows from the start and from shelf 1). In the pond, a 64-wide footbridge leads out to the valve tower, and through its doorway the red key glows on the valve console. Below the next lip: shelf 3, its breach, and the dam.
   - **Encounter:** 3 imps (3, 1) along the bank; 2 hell knights (1, 1) at the red door; 2 zombiemen (1, 1) in the tower, which has a window in its south face looking down the cascade.
   - **Key trap:** taking the red key (a W1 ring round it) opens the closet KC in the pond's east wall. A mancubus (1, 1), a revenant (1, 0; easy: an imp) and 2 imps (1, 1) come out, not deaf, and wade across the pond at the tower. The footbridge is the only dry way back to the bank.
   - **Pickups:** red key, medikit, box of bullets.
   - **Gate:** the red door (DR, red key).
6. **Pump station (B2H, B2P, B2L, B2G).** The pump hall is one open hall, 1088×512 at 512/768 (PIPE2, light 112). The sump (optional, 496) is a bay in its north wall, three PIPES pumps standing in nukage at its back, dark and flickering (light 80). A lift (128 travel) goes down to the lower gallery (384/576, light 128).
   - **Encounter:** an arachnotron (1, 0; easy: 2 imps) at the hall's far west end, facing the red door down about 1,000 of open floor: spatial pressure from the moment the door opens. 2 chaingunners (1, 1) on the low pump plinths put on time pressure. 3 imps (3, 3). In the sump, 2 spectres (1, 1); in the lower gallery, 2 shotgun guys (1, 0).
   - **Pickups:** **rocket launcher** on a pump plinth in the hall; 2 rockets, box of bullets, medikit. Sump: berserk pack.
   - **Gate:** the lift (SR from both levels), then the lower gallery's east door onto shelf 3.
7. **Shelf 3 and the breach (S3T, S3B, BRK, S3P).** Bank 384, trough and pond 368, sky 768, light 192. You arrive at the west end and walk east 896 to the breach. There, 256 of bank and railing have fallen into the pond: three rubble blocks (CEMENT6, top 416) lie in the nukage, leaving a winding channel to the broken lip, and the pond pours over the lip with no railing. The breach is lit brighter (240) than the shelf, two tech lamps stand in the pond either side of the broken lip, and a trail of armor bonuses runs from the bank through the rubble to the drop: this is the main way down.
   - **Visible:** the gap in the railing. Below: the dam crest with the radiation suit glowing on its pedestal, the floodgate, the lake. Across the breach: the settling house's lit door at the east end of the bank.
   - **Gate (the fork):** step down into the breach, wade 256 south to the broken lip and drop 128 into shelf 4's trough (one-way). Or wade across the breach to the east bank and go down through the settling house (optional, below).
   - **Encounter:** 3 imps (3, 1) on the west bank; 2 cacodemons (1, 1) over the pond; a revenant (1, 0; easy: an imp) on the east bank by the settling house door, a turret firing across the breach; a mancubus (1, 0) at the east bank's far end.
   - **Pickups:** medikit, box of rockets on the bank by the breach.
8. **Shelf 4, the dam (S4T, S4C, S4P, FGG, RSP).** Crest 256, trough and pond 240, sky 640, light 208. The pond pours over the dam's full width into the lake, 240 below. You land in the trough below the breach, or come out of the settling house at the crest's east end.
   - **Visible:** the lake over the dam's railing; the Cyberdemon, if he's awake, wading toward the dam. Behind him the dome's hatch is shut. To the west, the cooling-tower stump has something glowing inside its ring (secret 4); beyond it the islands. In the middle of the lip stands the floodgate, a steel gate 128 above the pond. The gatehouse is at the west end of the crest.
   - **Gate:** the floodgate, opened from the gatehouse.
   - **Encounter:** 2 hell knights (1, 1) on the crest facing the trough, to meet you where you land; 3 imps (3, 1); a pain elemental (1, 0) in a closet in the canyon's east wall at pond level (PEC), let out when you reach the shelf, off the breach or down the settling house's spillway; an arachnotron (1, 0) at the crest's east end, facing west along it.
   - **Pickups:** **radiation suit** on a lit pedestal on the crest beside the floodgate; box of rockets, medikit.
9. **Gatehouse (B4C).** 768×512 at 256/416, GRAY7 with GRAYPOIS signs, light 176. A window in its east wall (sill 32) looks down the pond at the floodgate.
   - **Encounter:** 2 revenants (1, 0) in an enclosed room, the priority threats; 2 chaingunners (1, 0); 2 imps (1, 1; easy: one more for a revenant).
   - **Pickups:** **BFG9000** on a lit pedestal in the middle; a cell pack by the switch; medikit.
   - **Gate:** the floodgate switch beside the window. The gate sinks into the dam while you watch, leaving a 256-wide gap in the lip.
10. **The floodgate (FGG).** Back east along the crest about 900, past the radiation suit, into the pond, and over the gap: you ride the falls 240 down into the lake. Crossing the gap (W1) opens the dome's hatch. One-way.
11. **The lake, the final fight (L).** 2560×1920 of nukage at 0 (`DAMAGE_10`), sky 384, light 224, rising to 255 round the dome. Behind you the dam's falls run the full width of the canyon, and above them the cascade you came down, shelf over shelf.
    - **Encounter:**
      - **The Cyberdemon** (all skills), deaf, about 550 south of the floodgate with his back to the dam. Gunfire on the shelves reaches him (the dam's sound-blocking lines let one crossing through), so he wakes as soon as he can see you, usually from the balcony rail or shelf 3, and you hear him from then on. He is the spatial threat: dodge his rockets, keep cover between you.
      - **The dome group** is not deaf: the arch-vile (1, 0; easy: a hell knight) in the exit alcove at the back of the dome, and 2 hell knights (1, 1) inside the hatch. They wake when the hatch opens and they see you. Nothing stands in front of the hatch: you see the vile from where you land, about 1,950 away, beyond the 1,088 an arch-vile attacks from, so he has to come out through the dome and most of the way up the lake to reach you. The vile is the time threat: kill it first, or it raises every imp and knight it reaches.
      - **Support,** deaf and spread over the islands for the vile to raise: 6 imps (5, 2), 2 hell knights (2, 1), a revenant (1, 0) on the east island, 2 cacodemons (1, 1) over the west and east islands. The islands' outlines are sound-blocking lines, so gunfire on the shelves never reaches them: they're still spread out on their islands when you land, and wake when you fire in the lake.
      - **Infighting:** the Cyberdemon's rockets splash whatever is near you, and whatever they hit turns on him, the vile included.
    - **Cover:** the cooling-tower ring (64 high), the two tank stubs on the east island, four pylons and a dome fragment. The islands, at 16, let you stand out of the nukage.
    - **Pickups:** radiation suits on the west and east islands; a cell pack and a medikit on the east island; a box of rockets and a medikit on each of the west and south-east islands; stimpacks either side of the hatch.
12. **The dome (DH, DI, EXR, EXD, EXC).** A gatehouse against the lake's south wall: the hatch face on the lake, its corners cut 192 back to the wall. Through the hatch (256 wide, SPCDOOR1 in a 128-high recess) is a shallow hall, 128 deep and 416–672 wide, floor 16, ceiling 320, SHAWN2, light 255 strobing. Opposite the hatch, recessed into the south wall, is the exit alcove: the reactor's melted core pours down all its walls in falling nukage (SFALL1), the shutter at its back included, and the EXIT sign hangs on its lintel. The arch-vile waits in it. The shutter seals the exit console (72 high, SW1EXIT); it rises when the Cyberdemon dies.

Optional spaces:

13. **Outfall valve room (OV)**, 512×320 at 832, off the deck's east side: the outfall's valve gear (TEKGREN1). **Pickups:** green armor, stimpack. Secret 1 is behind its east wall.
14. **Troughs and ponds**, every shelf: armor bonuses, and the views. Every one is 16 below its bank, so you can step out anywhere.
15. **The valve tower's pillar (VTP)**, secret 2.
16. **The sump (B2P)**, the berserk pack.
17. **Settling house (B3H, B3C, B3N)**, the second way down from shelf 3, by its east bank. A hall at 384/544 (ICKWALL3, light 112) with two settling tanks of nukage at 368; at its south-east corner the floor ends in a 128 drop into the dry spillway (256, one-way), then the landing at 256 and a door onto the crest's east end.
    - **Encounter:** a baron (1, 1; easy: a hell knight), 4 imps (3, 2), a chaingunner (1, 0), 2 demons (1, 1).
    - **Pickups:** **plasma rifle** on a tank's rim; cell pack on the landing. Secret 3 is off the hall.
18. **The crest's east half**, the arachnotron's end.
19. **Armory (B4A)**, 384×192 at 256, off the gatehouse's south wall. **Pickups:** cell pack, box of rockets, medikit.
20. **The lake beyond the route strip**: the islands and their pickups, and secret 4 in the cooling-tower stump.

## Sketch

64 units per character; each row label is that row's top edge (y). x ticks every 512 from -768.

```
 2944        ooooooooooooooooOOOOOOOOOOOOVVVVVVVV
 2880        ooooooooooooooooOOOOOOOOOOOOVVVVVVVV11
 2816        ^^^^            OOOOOOOOOOOOVVVVVVVV11
 2752        ^^^^            OOOOOO@OOOOOVVVVVVVV
 2688        ^^^^            OOOOOOOOOOOOVVVVVVVV
 2624        ^^^^            OOOOOOOOOOOO  MMMM
 2560        ^^^^  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 2496        llllll================================gggggggggggg
 2432        llllll================================gggggggggggg
 2368        llllll================================gggggggggggg
 2304              ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~mmmmmmmm ggg
 2240              ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~mmmmmmmm ggg
 2176              ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~mmmmmmmm ggg
 2112              ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~mmmmmmmm ^^^
 2048  hhhhhhhhhhhh~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~mmmmmmmm ^^^
 1984  hhsssssshhhh================================mmmmmmmm ^^^
 1920  hhsssssshhhh================================mmmmmmmm ^^^
 1856  hhsssssshhhh================================mmmmmmmm ^^^
 1792  hhsssssshhhh~~~~~~~~~~~~~~~~~~~~~b~~~~~~~~~~mmmmmmmm ^^^
 1728  hhhhhhhhhhhh~~~~~~~~~~~~~~~~~~~~~b~~~~~~~~~~mmmmmmmmpppp
 1664          LL  ~~~~~~~~~~~~~~~~~~~2TTTk~~~~~~~~KKKK
 1600          LL  ~~~~~~~~~~~~~~~~~~~~TTTT~~~~~~~~KKKK
 1536  wwwwwwwwwwww~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~        33
 1472  wwwwwwwwwwww==============xxxx==============HHHHHHHHHHHH
 1408  wwwwwwwwwwww==============xxxx==============HHHHHHHHHHHH
 1344  wwwwwwwwwwww==============xxxx==============HHHHHHHHHHHH
 1280  wwwwwwwwwwww~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~HHHHHHHHHHHH
 1216              ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~HHHHHHHHHHHH
 1152              ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~HHHHHHHHHHHH
 1088  BBBBBBBBBBBB~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~        cccc
 1024  BBBBBBBBBBBB~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~        cccc
  960  BBBBBBBBBBBB================================        cccc
  896  BBBBBFFBBBBB================================nnnnnnnnnnnn
  832  BBBBBFFBBBBB===================S============nnnnnnnnnnnn
  768  BBBBBBBBBBBB~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  704  BBBBBBBBBBBB~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  640  BBBBBBBBBBBB~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  576  aaaaaa      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  512  aaaaaa  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  448  aaaaaa  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  384          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  320          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  256          ~~~~~~~~~~~~#~~~~~~~~~~~~~~#~~~~~~~~~~~~
  192          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  128          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   64          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    0          ~~~CCCCCCC~~~~~~~~~~~~~Q~~~~~~~~~~~~~~~~
  -64          ~~~C44444C~~~~~~~~~~~~~~~~~~~~~iiiiiii~~
 -128          ~~~C44444C~~~~~~~~~~~~~~~~~~~~~iiiiYYi~~
 -192          ~~~C44444C~~~~~~~~~~~~~~~~~~~~~iiiiYYi~~
 -256          ~~~C44444C~~~##~~~~~~~~~~~~~~~~iYYiiii~~
 -320          ~~~C44444C~~~~~~~~~~~~~~~~~~~~~iYYiiii~~
 -384          ~~~CCCCCCC~~~~~~~~~~~~~~~~~~~~~iiiiiii~~
 -448          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 -512          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 -576          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 -640          ~~~~~~~~~~~#~~~~~~~~~~~~~~~~~#~~~~~~~~~~
 -704          ~~iiiiii~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 -768          ~~iiiiii~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 -832          ~~iiiiii~~~~~~~~~~~~~~~~~~~~~~iiiiii~~~~
 -896          ~~iiiiii~~~~~~~~~~~~~~~~~~~~~~iiiiii~~~~
 -960          ~~iiiiii~~~~~~~~~~~~~~~~~~~~~~iiiiii~~~~
-1024          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~iiiiii~~~~
-1088          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-1152          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-1216          ~~~~~~~~~~~~~~~~~DddddD~~~~~~~~~~~~~~~~~
-1280          ~~~~~~~~~~~~~~~~DDDDDDDD~~~~~~~~~~~~~~~~
-1344          ~~~~~~~~~~~~~~~DDDDDDDDDD~~~~~~~~~~~~~~~
-1408                             XX
       |       |       |       |       |       |       |
       -768    -256    256     768     1280    1792    2304
```

Each shelf reads, north to south: a row of `~` (the trough, under the falls from above), three rows of `=` (the bank), four rows of `~` (the pond). The pond's south edge is the railed lip.

**Legend.**

| Symbol | Meaning |
|---|---|
| `@` | start (1024,2688), facing south |
| `O` | operations deck, 832; its bottom row is the balcony (OB, sky) |
| `o` | corridor, 832 |
| `V` | outfall valve room, 832 |
| `M` | outfall mouth, 752 (nukage, out of reach) |
| `^` | stairs: the stairwell (808→664, then the landing), the sluice house stair (624→512) |
| `l` | stairwell landing, 640 |
| `~` | nukage: troughs and ponds 16 below their bank (624, 496, 368, 240), the sump (496), the lake (0) |
| `=` | banks: 640, 512, 384; the dam crest, 256 |
| `g` | sluice house gallery, 640 |
| `m` | machine room, 512 |
| `p` | passage at the stair foot, 512 |
| `K` | red-key trap closet, 496 |
| `b` | footbridge, 512 |
| `T` | valve tower, 512 |
| `k` | red key |
| `h` / `s` | pump hall, 512 / sump, 496 |
| `L` | pump station lift, 512 → 384 |
| `w` | pump station lower gallery, 384 |
| `x` | the breach: collapsed bank, nukage at 368, unrailed lip |
| `H` / `c` / `n` | settling house hall 384 / spillway 256, a 128 drop below the hall / landing 256 |
| `S` | radiation suit pedestal, 264 |
| `B` / `F` / `a` | gatehouse 256 / BFG pedestal 264 / armory 256 |
| (no symbol) | the floodgate FGG, 16 deep, at the pond's lip x 896..1152, y 512..528 |
| `C` | cooling-tower ring, top 64 |
| `i` | islands, 16 |
| `Y` | tank stubs, top 144 |
| `#` | pylons; a dome fragment |
| `Q` | the Cyberdemon (1248,-32), facing south |
| `D` / `d` | dome interior 16 / hatch |
| `X` | exit alcove at the dome's back: the arch-vile, the console, the falls |
| `1`–`4` | secrets |

Rectangles (map units), as built (see Build notes for where they differ from the first plan). They don't overlap, except where one is cut out of another (the sump and plinths from B2H, the islands and everything on them from L).

| Id | x0..x1 | y0..y1 | Floor / ceiling | Notes |
|---|---|---|---|---|
| OD | 640..1408 | 2624..2976 | 832 / 960 | start (1024,2688) facing south; the south side is open onto OB; two blinking TLITE6_5 lamp strips; COMPSTA1 consoles (24 high) at 704..832 and 1216..1344 × 2640..2688 |
| OB | 640..1408 | 2560..2624 | 832 / sky 1024 | balcony; impassable railing (MIDBARS3) along y 2560; shotgun at the rail (1024,2592) |
| OC | -384..608 | 2816..2944 | 832 / 960 | door x 608..624 filling its east end, 16-deep recess on OD's side |
| OV | 1456..1904 | 2624..2944 | 832 / 960 | TEKGREN1; door x 1424..1440, y 2752..2880, recesses both sides |
| S1x | 1920..2048 | 2752..2880 | 832 / 928 | secret 1; secret door x 1904..1920, y 2784..2848 |
| OM | 1536..1792 | 2560..2608 | 752 / 832 | outfall mouth, nukage; SFALL1 128 down to S1T; SUPPORT3 either side |
| SW | -384..-128 | 2480..2816 | 808..664 | seven 24 steps, 48 deep, descending south |
| SWL | -384..-64 | 2304..2480 | 640 / 768 | landing; door x -48..-32, y 2336..2464, recesses both sides |
| S1T / S1B / S1P | 0..2048 | 2496..2560 / 2304..2496 / 2048..2304 | 624 / 640 / 624, sky 1024 | railed lip at y 2048 |
| B1G | 2112..2816 × 2304..2496; 2624..2816 × 2112..2304 | | 640 / 768 | door x 2080..2096, y 2336..2464; SSG on a desk 2720..2784 × 2400..2464 at 664; open edge over B1M along y 2304 |
| B1S | 2624..2816 | 1728..2112 | 624..512 | eight 16 steps, 48 deep, descending south |
| B1P | 2560..2816 | 1664..1728 | 512 / 640 | |
| B1M | 2112..2560 | 1664..2304 | 512 / 800 | flickers; door x 2080..2096, y 1824..1952 onto S2B; plinth 2240..2432 × 1920..2048 at 536 |
| KC | 2064..2320 | 1536..1648 | 496 / 624 | trap closet; 112-wide door x 2048..2064 faced CEMENT6, damaging like the nukage either side |
| PEC | 2064..2224 | 576..704 | 240 / 368 | the pain elemental's closet; 128-wide door x 2048..2064 faced CEMENT6, damaging like the pond |
| S2T / S2B / S2P | 0..2048 | 1984..2048 / 1792..1984 / 1536..1792 | 496 / 512 / 496, sky 896 | railed lip at y 1536 |
| S2P_z | 1152..1600 | 1536..1792 | 496 / sky 704 | the pond round the tower, less the tower, VTP and FB: its low sky stops the tower's walls at 704 |
| FB | 1376..1440 | 1664..1792 | 512 / sky 704 | footbridge |
| VT | 1280..1536 | 1536..1664 | | the tower: interior VTI 1296..1520 × 1552..1648 at 512 / 640; doorway 1376..1440 on its north face; window 1344..1472 in its south face, sill 544, lintel 608, both its lines block monsters; red key at (1472,1600) on a glowing spot |
| VTP | 1216..1280 | 1600..1664 | 640 (lift to 496) / sky 704 | secret 2; soulsphere on top; the panel is VTI's west wall, y 1568..1632 |
| B2H | -1152..-64 | 1664..2176 | 512 / 768 | red door x -48..-32, y 1824..1952; the sump bay cut from its north wall; plinths -480..-352 × 1680..1744 and 1968..2032 at 536 |
| B2P | -960..-576 | 2048..2176 | 496 / 768 | sump, a bay in B2H's north wall; three PIPES pumps, 64×48, along its back |
| B2L | -256..-128 | 1536..1664 | 512 → 384 | lift, top FLOOR5_1 like the hall; B2G's ceiling is 192 above its bottom |
| B2G | -768..-64 | 1216..1536 | 384 / 576 | door x -48..-32, y 1312..1440 |
| S3T / S3B / S3P | 0..2048 | 1472..1536 / 1280..1472 / 1024..1280 | 368 / 384 / 368, sky 768 | railed lip at y 1024, except x 896..1152 |
| BRK | 896..1152 | 1024..1472 | 368 | the collapsed bank and the pond strip in front of it, one sector, light 240; rubble at 416: 1056..1120 × 1264..1392, 944..1008 × 1392..1456, 944..1008 × 1168..1232; tech lamps at (872,1048) and (1176,1048); armor-bonus trail from (816,1320) to (1024,1080) |
| B3H | 2112..2816 | 1120..1472 | 384 / 544 | door x 2080..2096, y 1312..1440; tanks 2176..2368 and 2496..2688 × 1184..1312 at 368 |
| S3x | 2560..2688 | 1488..1552 | 384 / 512 | secret 3; secret door x 2592..2656, y 1472..1488 |
| B3C | 2560..2816 | 928..1120 | 256 / 544 | the spillway: the hall's floor drops 128 into it (one-way), riser ICKWALL1 |
| B3N | 2112..2816 | 768..928 | 256 / 416 | door x 2080..2096, y 784..912 onto S4C |
| S4T / S4C / S4P | 0..2048 | 960..1024 / 768..960 / 512..768 | 240 / 256 / 240, sky 640 | railed lip at y 512, except FGG; S4P split into the strip in front of the floodgate (896..1152 × 528..768) and the rest |
| FGG | 896..1152 | 512..528 | 368 → 0 | floodgate, SPCDOOR3 to the pond, SUPPORT3 ends and lake face; the S4P strip–FGG line is the W1 that opens DH |
| RSP | 1184..1248 | 784..848 | 264 | radiation suit, glowing; at the crest's pond edge, off the walk along the crest |
| B4C | -768..-64 | 576..1088 | 256 / 416 | door x -48..-32, y 816..944; window x -64..0, y 592..704, sill 288, lintel 368; switch niche y 720..784; BFG pedestal -448..-320 × 768..896 at 264; GRAYPOIS niches in the west wall |
| B4A | -768..-384 | 384..528 | 256 / 384 | armory; door y 544..560, x -640..-512 |
| L | -256..2304 | -1408..512 | 0 / sky 384 | `DAMAGE_10`; split into the route strip (768..1280 × -1216..512) and the rest, which the strip and the dome divide into west and east loops |
| CT / CTI | -64..384 × -448..0 / 0..320 × -384..-64 | | ring 64 / interior 16 | secret 4; the ring section at x 320..384, y -288..-160 lowers to 0 when used |
| I2 / I3 / I4 | -128..256 × -1024..-704 / 1728..2176 × -448..-64 / 1664..2048 × -1088..-800 | | 16 | islands |
| TK | 1792..1920 × -384..-256; 1984..2112 × -256..-128 | | 144 | tank stubs on I3 |
| PY | 64² centred on (512,192), (1472,192), (448,-704), (1600,-704) | | 352 | pylons, tops out of reach |
| FR | 576..704 × -320..-256 | | 96 | dome fragment |
| DM | 640..1408 × -1408..-1216: the hatch face 832..1216 at -1216, corners cut 192 back to the south wall | | | METAL2 exterior; shell 64 thick on the hatch side, about 32 on the chamfers; its back is the lake's south wall |
| DH | 896..1152 | -1264..-1232 | door, 16 → 140 | hatch, SPCDOOR1 (four 64-wide faces a side) in 16-deep, 128-high SUPPORT3 recesses on both sides |
| DI | (816,-1280) (1232,-1280) (1360,-1408) (688,-1408) | | 16 / 320 | strobes |
| EXR | 944..1104 | -1488..-1408 | 24 / 128 | exit alcove recessed into the south wall on the hatch's axis, SFALL1 walls (the melted core); its first 16 (-1424..-1408) is a lintel at 16 / 144 with EXITSIGN (128..144) on its inner face; arch-vile at (1024,-1456) |
| EXD | 992..1056 | -1504..-1488 | door, 24 → 124 | the shutter, faced SFALL1 like the alcove, SUPPORT3 jambs, tag 7: opened by the bossaction |
| EXC | 1008..1040 | -1520..-1504 | 96 | exit console behind the shutter, SW1EXIT on its north face |

Triggers:

| Trigger | Where | Effect |
|---|---|---|
| Red key pickup (W1 ring) | VTI | opens KC (door open, stays) |
| Breach lip, spillway drop (W1) | the BRK–S4T line; the B3C–B3N line | opens PEC (door open, stays) |
| Red door | B2H's east wall | DR, red key |
| B2L lift | pump station | SR lift from both levels |
| SILVER3 panel (SR lift) | VTI's west wall | lowers VTP to 496; it rises back to 640 with you on it |
| Floodgate switch (S1) | B4C's east wall | FGG floor lowers to its lowest neighbour (the lake, 0). It sinks 368 in about 10.5 s; its top is down to the pond after about 4 |
| Floodgate crossing (W1) | the S4P–FGG line | opens DH (door open, stays) |
| Ring section (S1, secret) | CT's east face | lowers to 0 |
| Secret doors | OV's east wall, B3H's north wall | DR, `ML_SECRET` |
| The Cyberdemon's death (UMAPINFO `bossaction = Cyberdemon, 103, 7`) | the whole map | opens EXD, the shutter over the exit console (door open, stays) |
| Exit switch | EXC's north face, behind EXD | exit |

## Materials

The base family is **CEMENT** (weathered concrete with a hazard-striped foot): **CEMENT6** on every wall of the outdoor cascade, the canyon walls, the retaining walls, every building facade that faces the cascade, and the rubble. The cascade is one continuous space, so it keeps one material from the balcony to the dam. Its shelves are told apart by height, light (brighter on each shelf down) and landmarks: the outfall, the valve tower, the breach, the floodgate. Variants: **CEMENT7** (blocks) in the stairwell, **CEMENT9** (mossy blocks) on the cooling-tower ring. **SFALL1** (animated green falls) is the face of every lip's falls, the outfall, the dam and the core. **NUKE24** is the riser wherever a bank steps 16 down to nukage.

The trim set is **SUPPORT3** (brown-green rivets), at every corner where CEMENT6 meets another material in one wall plane (the dam's abutments, the outfall, the canyon mouth) and round every switch and window, plus **DOORTRAK** on every door jamb. **LITE5** marks every secret. Railings are **MIDBARS3** on impassable lines.

| Area (spaces) | Walls | Trim | Floor / ceiling flats | Reason |
|---|---|---|---|---|
| Operations block (OD, OB, OC, OV, S1x) | TEKGREN2; TEKGREN5 light panels; TEKGREN1 over the outfall valves in OV; COMPSTA1 console faces along the balcony | SUPPORT3 at the balcony's ends and round the doors; DOORTRAK; LITE5 beside the S1x panel | FLOOR0_6 / CEIL3_5 with TLITE6_5 lamp strips (blinking); OB FLOOR0_6 / F_SKY1 | the plant's control room, where the alarm is going off |
| Stairwell (SW, SWL) | CEMENT7; risers CEMENT7 | DOORTRAK at both doors | FLAT1 / CEIL5_2 | concrete service stair: base family, block variant |
| The cascade (S1T/B/P, S2T/B/P, FB, S3T/B/P, BRK, S4T/C/P, RSP, FGG, OM) | CEMENT6; falls SFALL1; bank risers NUKE24; FGG faced SPCDOOR3 above the pond | SUPPORT3 either side of the outfall and at both dam abutments; MIDBARS3 railings on every lip except the breach | banks and crest FLAT1, ponds and troughs NUKAGE1 / F_SKY1; RSP TLITE6_1 | one open space: the outfall, shelf after shelf |
| Sluice house (B1G, B1S, B1P, B1M) | BROWN1 on the gallery; BROWN96 and BROWNPIP in the machine room | SUPPORT3 at the stair head and foot; DOORTRAK at both doors | gallery MFLR8_1 / CEIL5_2; machine room and stair FLOOR4_8 / CEIL5_2 | old brown sluice machinery |
| Trap closet (KC) | CEMENT7 inside; door face CEMENT6 | none: disguised in the retaining wall | NUKAGE1 / CEIL5_2 | behind the pond wall |
| Valve tower (VTI, VTP) | outside CEMENT6; inside SILVER1, SILVER3 instrument panels; VTP's inner face SILVER3, shifted | SUPPORT3 round the doorway and the window; LITE5 beside the VTP panel | FLAT23 / CEIL5_1; VTP top TLITE6_1 (lit) | the cascade's valve gear, the key's spotlit room |
| Pump station (B2H, B2P, B2L, B2G) | PIPE2; PIPE4 round the sump; PIPES pumps | SUPPORT3 at the lift and both doors; DOORRED2 jambs at the red door | FLOOR5_1 / CEIL5_2; sump NUKAGE1; lift PLAT1 sides, FLOOR5_1 top (rule 1); B2G FLOOR5_1 / CEIL5_2 | the pumps: pipes everywhere |
| Settling house (B3H, S3x, B3C, B3N) | ICKWALL3; ICKWALL4 (poison sign) over the tanks; the spillway's drop ICKWALL1 | DOORTRAK at both doors; LITE5 beside the S3x panel | SLIME13 / CEIL3_5; tanks NUKAGE1 | the slimed settling tanks |
| Gatehouse (B4C, B4A) | GRAY7; GRAYPOIS signs flanking the window | SUPPORT3 round the window and the switch (SW1GRAY); DOORTRAK | FLAT19 / CEIL3_5; BFG pedestal TLITE6_1 | the dam's control house, its radiation signs facing the lake |
| The lake (L, I2, I3, I4, PY, TK, CT, CTI) | cliffs TANROCK5; pylons CEMENT6; tank stubs SILVER1; ring CEMENT9 | SUPPORT3 where the cliffs meet the dam; NUKE24 island risers; LITE5 beside the CT panel | NUKAGE1 / F_SKY1; islands and CTI RROCK18; TK tops FLAT23; ring top FLAT1 | the valley the plant drained into: rock, with the plant's wreckage standing in it |
| Dome exterior (DM, FR, DH) | METAL2; hatch SPCDOOR1 | SUPPORT3 framing the hatch recess | FR top FLAT23 | the reactor's steel containment and its wreckage |
| Reactor hall (DI, EXR, EXD, EXC) | SHAWN2; the exit alcove's walls and its shutter SFALL1 (the melted core breaking through); console SW1EXIT | SUPPORT3 at the hatch's inner recess, on the alcove's lintel and the shutter's jambs | FLAT20 / TLITE6_6; alcove FLOOR1_7 (glowing) | the exit, as in MAP07 and MAP08: the brightest room |

Notes for the build:

- Every switch sits in a SUPPORT3 frame: the floodgate's SW1GRAY, the exit's SW1EXIT in the console.
- Light is the shelves' identity: S1 160, S2 176, S3 192, S4 208, the lake 224, the dome 255. The buildings between them are dark (96–144). Every step down from the balcony is brighter.
- Don't mix CEMENT variants within one wall. Relieve a long canyon wall with a SUPPORT3 pilaster, not a different panel.

## Secrets

| # | Where | Hint | Reward |
|---|---|---|---|
| 1 | A closet behind the outfall valve room's east wall (S1x) | A TEKGREN2 panel shifted out of line, with LITE5 beside it | backpack, megaarmor |
| 2 | The pillar beside the valve tower (VTP), at 640 | The soulsphere on its lit top, in view from the start, shelf 1 and the footbridge. Inside the tower, the west wall is SILVER3 shifted out of line, with LITE5 beside it; using it lowers the pillar, which carries you up | soulsphere, cell pack (first a plasma rifle, which the settling house hands you a minute later anyway; then a megasphere, too much on a map already heavy with health) |
| 3 | A closet off the settling house hall (S3x) | An ICKWALL3 panel shifted out of line, with LITE5 beside it | green armor |
| 4 | Inside the cooling-tower stump (CTI), in the lake | The ring's lit interior and its soulsphere, in view from the dam crest over the 64-high ring. On the ring's east face, a CEMENT9 section is shifted out of line with LITE5 beside it; using it lowers that section | soulsphere, in the middle of the boss fight |

## Targets

| Target (DOOM II median) | Plan | Where it comes from |
|---|---|---|
| Optional share of area ≥ 0.3 [0.5] | ≈ 0.6 | Of about 11.3M reachable, the critical path covers about 4.2M: the banks, the buildings on the route, the breach strip, the crest's west half, and the lake strip from the floodgate to the hatch. Every trough and pond except the breach strip and the strip in front of the floodgate is optional, as are B3, OV, B4A, the sump, and the lake beyond the strip (about 3.2M). Split S3P, S4P and L into strip and rest so the metric sees it. |
| Distinct floor heights ≥ 15 [23] | about 29 | 0 lake; 16 islands, dome, CT interior; 24 exit alcove; 240 S4 nukage; 256 crest, gatehouse, B3 spillway and landing; 264 pedestals; 368 S3 nukage, B3 tanks; 384 S3 bank, B2G, B3H; 496 S2 nukage, sump, KC; 512 S2 bank, tower, B2H, B1M; 528–624 the B1 stair; 624 S1 nukage; 640 S1 bank, gallery, landing, VTP; 664–808 the stairwell; 832 operations |
| Secrets ≥ 2 [4] | 4 | S1x, VTP, S3x, CTI |
| Light-effect sectors ≥ 3 [9] | about 10 | two OD alarm strips (blink), B1M (flicker), the sump (flicker), the red key's spot in VTI (glow), RSP (glow), a lamp strip at the floodgate (blink), CTI (glow), a glow ring in the lake round the dome, DI (strobe) |
| Deaf share (UV) ≥ 0.2 [0.42] | ≈ 0.9 | every monster except the KC closet's 4, the pain elemental in PEC, and the dome's 3 |
| Most-used wall texture 0.2–0.45 [0.3] | ≈ 0.25 | CEMENT6 (canyon and retaining walls, about 2.5M of wall) and TANROCK5 (the lake's cliffs, about 2.5M at a 384 sky) lead together, with SFALL1 (about 1.5M: four lips, the dam, the outfall, the core) third. If either reads above 0.45, lower the shelves' or the lake's sky. If both read under 0.2, raise the lake's sky to 448. |
| Rule-2 seams with a border ≥ 0.5 [0.31] | ≥ 0.7 | Every building meets the cascade at a door with DOORTRAK jambs; SUPPORT3 at the outfall, both dam abutments, the canyon mouth, every window and every switch; the hatch in a SUPPORT3 recess |

As built (`python3 -m levels nukage_meltdown`): optional share 0.66, 36 distinct floor heights, 4 secrets, 11 light-effect sectors, deaf share 0.92, most-used wall texture 0.21 (CEMENT6), rule-2 border share 0.96 with no unbordered seams. Every target is met. The rule-1 slips left are all door thresholds (each building door, and the valve tower's open doorway).

Balance targets:

- **Ammo:** UV pistol-start ratio 2.0–2.4, counting the Cyberdemon at 4,000. He takes no splash damage, so only direct rockets, plasma and the BFG count against him. From the gatehouse on, the critical path must carry at least 240 cells: the BFG's 40, the gatehouse's cell pack, and the east island's cell pack (the armory's is extra). That is six BFG shots, four or five for the Cyberdemon.
- **The arch-vile:** the static balance doesn't count resurrections. Budget the lake's fodder twice over (about 1,400 HP more).
- **Health:** 35–45 per 1,000 monster HP, not counting the soulsphere (secret 4) or the megaarmor (secret 1). That is about 800 on UV: a medikit in every space and two per island.
- **Suits:** one on the crest for the drop, one on each of the west and east islands.
- **Skill ratios:** easy/UV ≈ 0.45, HMP/UV ≈ 0.73 as planned. The Cyberdemon is on every skill; easy gets a hell knight in the vile's place.
- **Weapons:** shotgun (deck), super shotgun (sluice house), chaingun (from the pump station's chaingunners), rocket launcher (pump station), plasma rifle (the settling house), BFG9000 (gatehouse).

As built: UV ammo 2.23 (2.10 with the vile's 1,400 HP of resurrections), every leg of the route covered taking only what's on it (lowest leg 1.29, the red key's); health 965 on UV without the soulsphere, 47 per 1,000 monster HP, the megasphere (secret 2) included. From the gatehouse on the route carries 240 cells (the BFG, the gatehouse's and the east island's packs); the armory's and the west island's are extra. **Miss:** easy/UV is 0.48 and HMP/UV 0.75: the stand-ins easy gets (2 imps for the pump station's arachnotron, an imp for each revenant, a hell knight for the vile) count as easy monsters, which the plan's 0.45/0.73 left out. Kept, since each is the doc's own stand-in.

### Playtest

The wiring run (`uv run -q --with vizdoom scripts/tools/playtest.py wads/NUKAGE.WAD MAP09 levels/playtests/nukage_meltdown.playtest`) passes all 30 checks: every door, the red key and its closet, the pillar secret, the pump station lift, the breach drop, the floodgate switch, the drop over the gap and the hatch it opens, the four secrets and the exit. The static balance prints no warnings: lowest detour ratio 1.29 (the red key's leg), health never below 71 on the median model, long-range hitscan peak 20/s. Changes the playtest led to:

- **The radiation suit's pedestal** moved to the crest's pond edge (see Build notes): the route walked over it on the way to the gatehouse.
- **The EXIT sign** hung under a beam, then moved with the exit to the alcove's lintel (see Build notes): at the ceiling it never showed.
- **Two boxes of shells on shelf 2,** in the valve tower beside the key and at the red door's end of the bank. In the first fight round every seed ran out of shells between the key and the pump station's rocket launcher (10, 20 and 8 starved deaths there), the curve's low point (detour 1.13 then). UV ammo 2.27, inside the 2.0–2.4 target.

Views checked in screenshots:

- **From the start** the balcony's 64 of floor hides the near cascade: you see the far shelves, the dome and the canyon through the railing. Taking the shotgun at the rail is the reveal: shelf 1's pond, the lip, the valve tower, the floodgate, the dome and the slab, and the Cyberdemon, about 13 px tall at 2,600 units, behind the dam's railing.
- **From each bank** the lip hides the shelf directly below until you stand at the railing; the far shelves and the lake show. So the red door shows from shelf 1 only as its top edge.
- **Miss: the gatehouse window** looks along the dam's lip line, so the floodgate shows end-on, a 16-wide sliver at the window's edge, and its sinking barely reads. It reads on the walk back east along the crest (it takes 10.5 s to sink, about 4 s to walk back). Left as built: a window that saw the gate's face would need the gatehouse beside the pond rather than at its end.
- The settling house, gatehouse and machine room are dark (96–176) as the doc's light plan says; every area's walls match the materials table.

Fight runs on UV, seeds 1–3, after those changes, with `--max-time 25` (the map's route is long: the first round's seed 3 hit the default 15-minute cap at the gatehouse):

| Seed | Kills | Deaths (labels) | Skipped steps | Ammo left |
|---|---|---|---|---|
| 1 | 95 | 56 (41 hazard, 11 combat, 3 stuck, 1 unseen) | 5 | 9 rockets, 71 cells |
| 2 | 110 | 115 (105 hazard, 6 combat, 3 starved, 1 stuck) | 14 | none |
| 3 | 101 | 98 (72 hazard, 23 starved, 2 combat, 1 stuck) | 19 | 10 bullets, 6 shells, 5 rockets, 53 cells |

Every seed reaches the exit. Kills exceed the 84 monsters because the arch-vile raises them. Clusters and calls:

- **The lake and the dome** (23, 79 and 24 deaths): almost all labelled hazard, but they come one to three seconds apart, faster than the nukage (10 per second) can kill. In the footage they're the Cyberdemon's rockets and the arch-vile, with the bot standing in the open nukage, backing into the lake's corners, and spending its cells on imps rather than the Cyberdemon. Bot: a person uses the islands, the cover and the suits. Whether the fight is fair is for a human to judge in dsda-doom.
- **Shelf 2, the key trap and the pillar** (13, 13, 34): the bot wades the pond and the trough fighting the trap's mancubus and revenant and the red door's hell knights, and misses the pillar's lift timing while they wade at it. Seed 3 arrives on shelf 2 out of shells after firing about twice the HP it killed, and punches hell knights in the trough. Bot: the curve's detour ratio there is 1.29, and seeds 1 and 2 don't starve there.
- **The breach** (12, 16, 20 across shelf 3, the settling house and the breach): seed 2 is knocked over the unrailed lip twice while wading across the breach under the east bank's revenant, landing on shelf 4 early (the settling house is skipped, not a softlock). The tanks' and the breach's nukage do the rest. Bot. It can happen to a person too; that's the breach.
- **`open`/`use` fails** (the red door in every seed; seed 1 also the settling house door and the lift): the bot backs into a door alcove's corner from the hell knights, and the runner presses use at the line's midpoint, 66 away from there, past the 64 use range. Reproduced on its own: the same door opens in a wiring run with the monsters alive. Bot (the runner).
- **Unseen** (seed 1, once): a Cyberdemon rocket from off screen in the lake. Bot.

#### After the first human playthrough (DOOM + DOOM II 2024)

The user's notes, and what changed:

- **The Cyberdemon** isn't visible from the rail, but you hear him as you come down; better as a hint than a sight. Kept (see The view from the balcony).
- **The slab in front of the hatch hid the arch-vile,** the biggest threat. The slab is gone, and the exit and the melted core moved to an alcove at the dome's back where the vile waits, in view from the floodgate, out of his attack range (see Build notes).
- **The lake's trash met the drop in a clump.** They were already deaf; deaf doesn't hold an open space. Sound blocks at the dam and the islands now keep them asleep and spread out until you fire in the lake (see Build notes, and `docs/monster-alerting.md`).
- **The settling house's chute** read as stairs you couldn't climb. It's a 128 drop now.
- **The EXIT sign and the exit switch were misaligned** (the builder kept the wall's texture offset when an override put a picture on it). Fixed in the builder: a picture set by an override starts at offset 0. MAP07's and MAP08's EXIT signs had the same fault and were rebuilt.
- **The lake fight was extremely hard** (a reload to beat it). The clump and the hidden vile were the parts called out; both are fixed. The Cyberdemon meeting you at the foot of the dam is kept (the user's call).
- **The exit is locked behind the Cyberdemon's death** (the user's call, aiming at the 2024 re-release and GZDoom): a UMAPINFO `bossaction` opens a shutter over the exit console (see Build risks). Building it showed the reach model letting a switch be used through a closed door within use range, so the gate passed the check with or without the bossaction; the model now needs an opening on the line between (a use stops at a closed door, `PTR_UseTraverse`). No other map's result changed.
- **New end text** from the user (the inspector, 72 hours later).

#### After the second playthrough

- **Monsters stuck at doors** (a cacodemon at the machine room's west door): every door recess is now as wide as its door, as in id's maps, which roughly halves how often a monster freezes at a plain door ([docs/door-stuck.md](../../docs/door-stuck.md)). The doors stay DR; whether any should stay open once opened (D1) is left for a later analysis. The wiring run passes all 31 checks. The fight bot can't test it: ZDoom, which ViZDoom runs, randomises monsters out of the stuck state.

The wiring run passes all 31 checks (the shutter's is new). Fight runs on UV, `--max-time 25`, seeds 1–5, before the shutter (4 and 5 added because 1, 3 and 4 never fought the new lake properly):

| Seed | Kills | Deaths (labels) | Skipped steps | Ammo left | Lake / dome deaths |
|---|---|---|---|---|---|
| 1 | 95 | 115 (86 hazard, 20 starved, 7 combat, 1 stuck, 1 unseen) | 19 | none | 47 / 25, hatch never opened (warped past the floodgate line) |
| 2 | 129 | 69 (48 hazard, 14 starved, 6 combat, 1 stuck) | 14 | 100 cells | 12 / 0, exited |
| 3 | 48 | 84 (76 hazard, 7 starved, 1 combat) | 5 | 12 shells, 1 rocket | never reached: hit the cap in shelf 2's pond |
| 4 | 73 | 101 (75 hazard, 16 starved, 6 combat, 4 stuck) | 9 | 10 bullets, 8 shells, 5 rockets, 98 cells | never reached: hit the cap on the crest |
| 5 | 101 | 96 (65 hazard, 24 starved, 5 combat, 2 stuck) | 21 | none | 19 / 11, exited |

Calls:

- **The lake** (seeds 2 and 5): the bot reaches the floodgate having fired 180–220 cells on the crest (seed 5: 181 cells and no kill in that section), drops in starved, and dies in bursts at the foot of the dam and in the lake's corners. Bot: the curve has 1.46 of the lake's monster HP in ammo on the detour curve.
- **The Cyberdemon waits under the drop.** Gunfire on the shelves wakes him (by design: that's how you hear him), he walks to the foot of the dam below you, and he's there when you land. Seed 2 died three times in its first second in the lake. Shooting him from the lip before dropping may be a way round it (untested); whether to keep it is a question for the next playthrough.
- **Shelf 2's pond and the crest** (seeds 3 and 4 used up their 25 minutes there): the bot wading the nukage round the pillar secret, and stuck fighting on the crest. Bot; unchanged by this round.

#### Reshaping the lake and the dome

The user's call, from the preview: the lake runs 256 further south, to -1408, and the dome loses its middle. What's left of it is the angled front (the hatch and its cut corners), backed onto the lake's new south wall, with the exit alcove recessed into that wall behind it. The dais, the hall's straight walls and their LITE5 strips went with the middle; the two hell knights and the hall's medikits moved into the shallow hall left behind. The alcove's shutter is faced in SFALL1 too, so the whole alcove is falling nukage and the falls rise away when the Cyberdemon dies. The arch-vile is now about 1,950 from the landing (it was about 1,500), still past the 1,088 he attacks from. The wiring run passes all 31 checks.

#### After the third playthrough (pistol start, DOOM + DOOM II 2024)

- **Confirmed in the 2024 re-release:** the breach now reads as the way down (lamps, bonus trail, rubble channel); the Cyberdemon's death opens the exit shutter (the `bossaction`), which ViZDoom can't show; the bigger, open pump hall makes the arachnotron a real threat; the pain elemental comes out of his closet into the crest fight.
- **Too much health,** megasphere or not. First cut: secret 2's megasphere is a soulsphere (UV health 1065 → 965, 52 → 47 per 1,000 monster HP).
- **The rubble left a pocket** east of the channel where the east bank's mancubus couldn't hit you. The rubble is mirrored east-west (see Build notes).
- **The exit switch was misaligned** once the shutter opened. The console's riser was SUPPORT3, the alcove's own wall texture, so the builder unpegged it to line up with the walls; the override swapped in SW1EXIT but kept the flag, and the picture hung from the open shutter's ceiling (124) instead of the console's top (96). Fixed in the builder: a lower texture set by an override on such a riser is pegged to the step again (README, OVERRIDES). The only other map it changed is MAP07, whose dock trench risers (NUKEDGE1 by override) now peg like every other NUKEDGE1 riser in the set.

## Build risks

- **One open canyon.** The four shelves and the lake are one space, and you can see all of it from the balcony. Every outdoor monster is deaf and faces south, away from the start and from the shelves above. Check with the build's line-of-sight test that nothing awake sees OB. No hitscanner stands on a bank, the crest or the lake: the chaingunners and shotgun guys are all indoors, and the tower's zombiemen are inside it. The nearest monster to the start is on shelf 1, kept more than 300 away, not under the balcony.
- **The view from the balcony.** The deck stands 192 above shelf 1, and every pond is at the front of its shelf, so each lip hides only the back of the shelf below. Worked out from eye height (873): every pond's front half shows; the lake shows south of about y -280. The Cyberdemon was meant to show head and shoulders over the dam; built, he's a speck at most from the rail, and that's kept: playing it, he's better as a hint (a speck, then his roar and footsteps as you come down) than a sight, and the arch-vile through the hatch is the reveal.
- **Sealing the shelves.** Every lip is an impassable railing except the breach (S3) and the floodgate (S4, shut until the switch). So is the balcony. Otherwise the player can drop down the cascade past the sluice house and the red door. The valve tower stands in the pond below S1's lip, 384 from it, so the pillar top (640) is out of reach from shelf 1. Check that the reach check reaches B2 only with the red key.
- **One-way drops.** The breach (368 → 240) and the floodgate (240 → 0) can't be climbed back. The reach check has to follow them down and still reach EXC's room. Put EXR in `MUST_REACH`, and the islands, so the lake's every piece is proved.
- **The floodgate** lowers to its lowest neighbour. FGG neighbours only S4P (240) and the lake (0), so it stops at 0. The W1 that opens the hatch is on the S4P–FGG line, crossed only by stepping off into the gap, and a monster can't trigger a door-open line.
- **Pits.** Every nukage floor has an exit within 24: troughs and ponds (16 below their bank), the breach (wade to S3B's east end, or drop), the sump (16), B3's tanks (16), the lake (islands and the dome at 16). The lake has no way back up the dam, by design. Its suits, islands and the dome make it survivable.
- **The hatch.** DH is 256 wide and the dome's hall is 304 tall, so the door needs 128-high recesses on both sides (the doom-build door gotcha). Shut, it blocks sound, so the dome group sleeps until you open it. Open, it frames the arch-vile in the exit alcove for you to see from the floodgate; keep the line from the floodgate through the hatch to the alcove clear.
- **The Cyberdemon.** 4,000 HP, splash-immune, 110 tall, 80 across. He fits through the hatch and between the pylons, so he will follow you, and he can't climb the dam (240). He is deaf with his back to the dam, so the first shot is yours. With a carried BFG and full cells he goes down fast. That's acceptable on the last map, but test from a pistol start.
- **The exit is tied to his death** (after the first playthrough). Vanilla DOOM II has no MAP09 boss rule, so it's a UMAPINFO `bossaction` (`Cyberdemon, 103, 7`): a shutter seals the exit console and opens when he dies. It works only in ports that read UMAPINFO: the 2024 re-release (written with a space after each comma, which it needs), GZDoom 4.6+, dsda-doom, Woof. In `doom2.exe`, Chocolate Doom and the ViZDoom playtests the shutter never opens; the playtest checks it's shut and warps past it. The reach check reads the bossaction, and the switch behind the 16-deep shutter is out of use until it opens (a use stops at a closed door).
- **Railings.** MIDBARS3 on lip lines: lower-unpegged so the bars stand on the higher floor, 72 tall, above 128–240 of falls. Mid textures don't tile vertically in vanilla, so the bars must fit their opening (the sky is far above).
- **Falls faces.** SFALL1 is 128 tall and tiles: the lip falls are 128, the dam 240, the exit alcove's walls 104. Peg the dam's falls so the seam isn't at eye level from the lake.
- **Sky.** Each shelf's sky steps down (1024, 896, 768, 640) and the lake's is 384, so the canyon walls stay about 384 tall. Sky-to-sky joins draw no wall. Buildings' outer walls show CEMENT6 up to the shelf's sky.
- **Visplanes.** The balcony sees most of the map. Keep each shelf to one trough, one bank and one pond sector, the lake to as few sectors as its islands allow, and check in dsda-doom that nothing drops out.
- **Lifts and the spillway.** B2L travels 128, and B2G's ceiling is 192 above its floor (the lift gotcha needs 56 above the lift top). The settling house's way down is a 128 drop into the spillway, one-way, and it should look it: a wall from below, not steps.
- **UMAPINFO.** Write it as a string body (`endcast = true` is unquoted; `intertext` is a comma-separated list; `bossaction` takes bare values). The end text screen fits 17 lines of up to about 39 characters (vanilla draws them 11 apart from y=10 on a 200-high screen, and stops at the first that runs past x=320). Check in a port that the text plays after MAP09 and the cast call follows. ViZDoom ignores UMAPINFO.
- **Set bookkeeping.** Add MAP09 to README "Included WAD" (nine maps) and SPOILERS, write the preview `wads/NUKAGE-MAP09.svg`, and write `levels/playtests/nukage_meltdown.playtest`.

## Build notes

Where the build differs from the first plan, and why (the rectangle table is as built):

- **The valve tower moved east,** from x 896..1152 to 1280..1536, with its pillar, footbridge and key. At 896..1152 it stood on the start's line of sight to the breach, the floodgate and the Cyberdemon, all at x ≈ 1024. Its walls are void, which rises to its sector's sky, so the pond round it (S2P_z) has its own sky at 704: the tower stands 208 over the pond instead of 400, below the start's eye. Sky-to-sky joins draw no wall, so the step in the sky doesn't show.
- **The Cyberdemon stands at (1248,-32),** not (1024,-64): there he stood in the floodgate's shadow from the start. A sight check from the start's eye (1024,2688,873) sees him from about 82 up (head and shoulders, through the dam's railing), the floodgate's top, the breach's broken lip, the red door's top and the pillar top.
- **The floodgate is 128 above the pond** (top 368, not 304): SPCDOOR3 is a 128-tall picture and the build makes pictures fit their walls. Its ends and its lake face are SUPPORT3, so from the lake it reads as a steel pier in the falls.
- **Every door has recesses on both sides,** DOORTRAK (DOORRED2 at the red door), so no door face sits flat in a material wall; the recesses on the shelves' side are 32 deep. Each building beside the canyon starts 64 further out for them (B1G, B1M, B3H, B3N from x 2112; B2H, B2G, B4C, SWL end at x -64). OD runs to y 2976 to take the corridor door's recess.
- **Door recesses are as wide as their doors** (`doorway()` since the second playthrough). They were 160 wide, leaving a 16-unit stub of wall beside each door in its plane; a vanilla monster pressed into one while over a plain door's line "uses" the door and freezes, as a cacodemon did at the machine room's door. See docs/door-stuck.md.
- **Settling house:** the hall is 1120..1472 (tanks 1184..1312), the spillway 928..1120 and the landing 768..928, so the landing's door recess (128 wide) fits it. The spillway was first a chute of three 32 steps; from the landing they read as stairs you couldn't climb, so it's one 128 drop.
- **KC** is 112 wide (y 1536..1648), 16 clear of the machine room, which the 128-wide plan touched. Its door is damaging nukage like the floor on both sides of it (the hazard check needs damaging floors below every dry neighbour).
- **Pump station:** first built 768×384 with the sump in the middle and a PIPES column on each plinth; playing it, the arachnotron's room was too small and too broken up by pillars to make him a threat. It's now 1088×512 and open: the sump moved into a bay in the north wall, the columns are gone, and the arachnotron stands at the west end with a clear line down the hall to the red door. The two plinths (24 high) still hold the chaingunners and the rocket launcher. The lift's top is FLOOR5_1 like the hall (rule 1); PLAT1 sides mark it when it moves. The sump flickers but doesn't hurt: a sector has one special.
- **The breach and the pond strip in front of it are one sector** (BRK, 896..1152 × 1024..1472).
- **The breach marks the main path** (playtest: it read as a side gap, and the settling house looked like the way on). Rubble0 runs 128 further south and a third block lies near the lip, so the rubble walls in a channel. The rubble is mirrored east-west from the first cut (third playthrough): the open nukage east of the channel, between two blocks, was a pocket the east bank's mancubus couldn't shoot into, and rubble0 now fills it; the breach is lit 240 against the shelf's 192 (it can't blink: its nukage hurts, and a sector has one special); two tech lamps frame the broken lip, and armor bonuses lead down the channel.
- **The tower's window blocks monsters** (playtest, every time: the pain elemental flew in through it from the shelves and spent the fight inside the tower). It's 64 tall, enough for a flier, so both its lines are `ML_BLOCKMONSTERS`; shots, sight and the player still cross it.
- **The pain elemental is in a closet** (playtest, every time: from over shelf 4's pond he woke at gunfire on the shelves above, flew up the cascade and fought from the valve tower). Deaf doesn't hold in the open canyon, and sound blocks at shelf 3's lip would also have silenced the Cyberdemon, so he waits in PEC, behind a shut door that keeps all sound out, until you reach shelf 4. The settling house's trigger is at the spillway drop, not the landing's door: a walk line in front of a door stops the door being used in vanilla.
- **The glow ring round the dome isn't built:** the lake has to keep `DAMAGE_10`, and a sector has one special. There are 10 light-effect sectors without it (11 before the reshape took the dais).
- **The gatehouse's GRAYPOIS signs** are 72-high niches in its west wall, facing the window: its east wall holds the window, the switch niche and the door, with no room beside the window.
- **Dome:** the shell is 64 thick on the hatch side, so the hatch (32 deep) has 16-deep recesses both sides inside it. The slab that screened the hatch is gone, and the melted core and the exit moved from the dome's middle to an alcove at its back on the hatch's axis, where the arch-vile waits (playtest: the slab hid the biggest threat; you should see him the moment the hatch opens). Since the reshape (see Playtest) the dome is only its angled front against the lake's south wall, and the alcove is recessed into that wall. The core is the alcove's falling-nukage walls and shutter; the EXIT sign hangs on the alcove's lintel, 16 tall at 128..144, where it shows through the hatch.
- **Sound blocks at the dam and the islands** (playtest: the lake's deaf trash woke from gunfire on the shelves, gathered at the foot of the dam and met the drop in a clump). The dam's lip lines and every island's outline are sound-blocking, so the shelves' noise reaches the open lake (the Cyberdemon) but not the islands. Checked in ViZDoom: twelve shots on the crest used to set four island monsters walking; now none move until you fire in the lake. The two cacodemons moved from over the open lake to over the west and east islands, under the same shield.
- **The radiation suit's pedestal** stands at the crest's pond edge, not mid-crest: the playtest walked over it on the way west from the settling house's landing to the gatehouse and took the suit there, a minute before the drop needs it.
- **Pickups** beyond the plan's list, for the balance targets: a medikit in nearly every space, two on each island, two in the dome; boxes of shells on each shelf and in the buildings on the route; boxes of rockets in the lower gallery, on the crest and in the gatehouse; a cell pack on the west island and a box of rockets on the east island for the vile's resurrections.

## Concepts considered

1. **The Outfall (chosen; named Nukage Meltdown by the user).** A descent down terraced nukage falls to the meltdown lake, with every step down one-way at the end.
2. **High Tide.** A 512-deep containment well; each tier's switch raises the whole nukage surface to the next gallery, carrying the Cyberdemon up with it to the roof.
3. **The Archipelago.** The plant flooded to the rooftops: one nukage sea crossed island to island, with radiation suits as the clock and the Cyberdemon hunting between the islands.
4. **Two Titans.** A straight crossing of a nukage lake between the Spider Mastermind's tower and the Cyberdemon's, setting them on each other.
5. **Meltdown Run.** A run outward from the core while every floor you cross lowers into the nukage behind you.

The Outfall wins because:

- **It's the set's first descent,** and its reveal is the whole map: you see the route and the final fight from the first balcony, as MAP29 shows its fortress.
- **The nukage is the route.** You follow it down every lip to where all of it ends up, which closes the WAD.
- **Its mechanisms are cheap:** doors, one lift, drops, one lowering gate. No rising floors.
- **The boss gets a house:** build-up (seen from every shelf), cover, support for the vile to raise, and the BFG one room before.

The others lose:

- **High Tide** reuses MAP05's rising floors at four times the scale, with 5–8 s waits between tiers.
- **The Archipelago** is MAP05's reservoir scaled up, the most open space this builder has tried, and the whole sea wakes at the first shot.
- **Two Titans'** Spider Mastermind is a hitscanner across open nukage, on the research's cheap list, and it's a set piece more than a shape.
- **Meltdown Run** repeats the sinking floors of MAP06 and MAP07.
