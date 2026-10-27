# Nukage Storage (`nukage_storage`)

## Concept

**Thread a maze of steel casks across the store to the control tower, then throw the switch and watch every cask sink into the floor, turning the maze into an open hall full of the mancubi that were sealed among them.**

- **Shape:** one hall in two states. On the way in it's a maze: you see it whole from a gallery, then walk it aisle by aisle at floor level. After the switch it's a 1664×1472 arena with nothing standing but four columns. The second half isn't a revisit. It's a different place inside the same walls.
- **Theme:** the plant's spent-fuel store. Rows of steel casks stand in a concrete hall 384 high, under lamps that light the aisles between them. A staff wing with a decontamination corridor leads up to an observation gallery along the hall's west wall. The control tower stands outside the east wall, and its cab looks in through a window. The dispatch dock is behind blast shutters in the north wall, under an EXIT sign.
- **Gate to the exit: DOOM II's own MAP07 rule.** When the last mancubus on the map dies, every sector tagged 666 lowers to its lowest neighbour. That works by slot in vanilla and in the ports, and `levels/reach.py` models it (`BOSS["MAP07"]`). Here, tag 666 is on the dispatch shutters. DOOM II's Dead Simple is built on the same rule. This map uses the rule without copying that map's arena.
- **Difficulty:** hard, a step up from MAP06. About 30/54/75 monsters on easy/HMP/UV, and about 12,600 monster HP on UV, which is about 30% more than MAP06. The heavy share is about 23%: 6 mancubi, 3 arachnotrons, a baron, 2 hell knights, 2 revenants, 2 cacodemons and a pain elemental. It's the first fight in the set against six heavies at once. **Debut: the pain elemental**, alone in the open air over the cask field.
- **Slot:** MAP07 of `NUKAGE.WAD`. UMAPINFO: `levelname "Nukage Storage"`, `music "D_SHAWN"` (the slot's own track), no `next` (slot order follows), and **no `bossaction`**. Any `bossaction` replaces the slot's default boss behaviour and would remove the exit gate. (Built as Nukage Casks, and renamed.)

How it differs from the set:

| Map | Shape in a phrase |
|---|---|
| MAP01 Nukage Junction | the template: courtyard hub, one wing per key |
| MAP02 Nukage Crossing | two banks of a canal, joined by a sluice gate that sinks into a bridge |
| MAP03 Nukage Core | a spiral climb around a reactor to the crown |
| MAP04 Nukage Divided | a fork into two wings that never meet, keys crossed |
| MAP05 Nukage Drain | a ring of walkways raised one by one out of a flooded reservoir |
| MAP06 Nukage Undercurrent | one hall crossed twice: over it, then under it |
| **MAP07 Nukage Storage** | **one hall in two states: a maze on the way in, an arena once you sink it** |

None of these changes the shape of a whole space. MAP03's pens and MAP06's floodgate each drop one wall. MAP06 crosses its hall twice, while this map crosses its hall once and then changes it.

## Route

Heights are floor/ceiling. Monster counts are UV (HMP, easy), and "deaf" means the ambush flag. Coordinates are in the rectangle table under the sketch.

1. **Guardhouse (GH)**, the start. 256×192, 16/128. The player starts at (-576,-352) facing east. **Visible:** through the east window (sill 48) is the yard. You see the flatcar with its cask, the parked truck, and the store's concrete facade with its hazard-striped gate. A barred window beside the gate shows casks under lamps inside. **Gate:** none; a door in the north wall leads into the yard. **Encounter:** none. The nearest monster is about 650 away and faces away. **Pickups:** shotgun (about 100 from the start), stimpack, 4 shells.
2. **Yard (RY)**, 1600×416, 0/sky. **Gate:** the store's gate is shut and opens only from inside, later. The way on is the locker-room door in the yard's north-west corner, 300 from the guardhouse. **Visible:** the facade, the gate window, and the flatcar cask with its odd hatch (secret 1). **Encounter** (all deaf, facing away from the start): 2 shotgun guys (1, 1) by the truck, 3 zombiemen (2, 1) by the flatcar, 2 imps (2, 1) at the gate. Fodder is at range, hitscanners stay within 768 of the route, and the truck breaks the yard's long east–west sightline. **Pickups:** shells, clips, 2 armor bonuses. **Optional:** the east half (gate, flatcar, secret 1).
3. **Lockers (LK)**, 448×320, 0/128, bright. **Encounter:** 3 imps (2, 1) and a demon (1, 1), close. **Pickups:** **super shotgun** on a bench, medikit, shells.
4. **Decon corridor (DC)**, 192×512, -8/112, dark and flickering. A glowing but harmless nukage drain runs along its east side, and there are shower niches in the west wall. It has a door at each end. **Encounter:** 2 spectres (2, 1) in the dark and a chaingunner (1, 0) at the north end (a 512 sightline). **Pickups:** green armor, shells, stimpack.
5. **Stair (WS) and landing (LN).** Eight steps of 24 lead up to 192. LN is 576×96, 192/288. **Encounter:** 2 imps (2, 1) on the landing. **Optional:** a door to the records office, making a loop through the gallery's north end.
6. **Corridor (UC) and gallery passage (GP)**, 192 wide, 192/288, heading back south. There's a nook at the corridor's south end. **Encounter:** a shotgun guy (1, 0). **Pickups:** stimpack, and shells in the nook. **Gate:** door GD into the hall.
7. **Gallery (GL), the reveal.** A railed ledge, 192×944 at 192, along the hall's west wall, with the hall's 384 ceiling above.
   - **Visible:**
     - the whole cask field: rows of steel casks 96–192 high under lit aisles;
     - the yellow key glowing on top of the blue-lit cask stack (north centre, 144 up);
     - from the gallery's south end, the yellow door at the far east end, straight down aisle B1 over a low cask (the sightline clears that cask by 50);
     - the tower cab's lit window high in the east wall;
     - the striped shutters under an EXIT sign in the north wall;
     - the megasphere on the cask just below the stair.
   - **Encounter:**
     - **The pain elemental** (1, 1), deaf, starts on the tallest cask (B2H12, 192) in the field's centre-west, facing the gallery. It sees you at the door and comes at you through open air. Its lost souls come in over the 192-wide ledge, with the hall's whole volume around you.
     - 3 imps (3, 1) on cask tops, facing the gallery (turrets).
     - 2 imps (1, 1) at the gallery's north end.
     - 2 shotgun guys (1, 0) below in aisle A0.
   - **Pickups:** chaingun, box of bullets, medikit, stimpack.
   - **Gate:** the stair GS at the south end is the way down; rails stop you dropping anywhere else.
   - **Optional:** the records office, through the door at the north end.
8. **The cask field (H, maze state).** 1664×1472 at 0/384. Aisles are 192 wide (A0, A2, AP, B0, B2, B3) or 128 wide (A1, B1). They run between nine 256² cask blocks, and eight more casks plug aisle segments.
   - **Route:** down the stair → north up A0 under the gallery → east along B2 → north up A1 → east along B3 to the foot of the key stack → up the stack (space 9) → south down A2 → east along B1 → yellow door.
   - **Visible:** the key stack's lamps and the tower window above the cask tops (the landmarks you steer by), and the gallery behind you. Floor-level sightlines end at the next cask, 450 at most, until you're past B1's low cask.
   - **Encounter** (all deaf):
     - 2 demons (1, 1) in B2;
     - 2 spectres (2, 1) in A1;
     - a hell knight (1, 0) at the stack's foot, and 2 imps (1, 1) on cask tops in B3;
     - at the A2/B1 corner: a chaingunner (1, 0), 2 shotgun guys (1, 1) and a hell knight (0, 0);
     - **the revenant** (1, 0; easy: an imp) on the 160 cask beside the yellow door, the priority threat at the end of the maze.
   - **Pickups on the route:** shells, bullets, a medikit at the A1/B2 corner.
   - **Spurs:**
     - **The B1 spur** (west of the A2/B1 corner): 2 imps (1, 1), medikit, box of shells.
     - **The north-east spur** (B2 east, then AP north to the corner under the tower window): 3 imps (2, 1), medikit, box of rockets. Its dead end hides secret 3.
     - **B0**, the south aisle from the stair's foot: the gate switch, which opens the gate to the yard and closes a loop through the start, and the door to the cooling pond yard. 2 shotgun guys (1, 1) and a demon (1, 0); shells, a stimpack.
9. **The key stack (K2R3).** Five steps of blue-lit casks rise 24 each from B3 to a 128×128 top at 144. The yellow key sits in the middle of the top, under a glowing spotlight. **Taking the key opens two closets in the north wall across B3:** a baron (1, 0; easy: a hell knight) and 2 imps (1, 1). You're 144 up with the steps behind you, and the baron can climb them.
10. **Tower base (TB)**, through the yellow door. 256×256, 0/160, racks. **Encounter:** 2 shotgun guys (2, 1) and a chaingunner (0, 0) among the racks. **Pickups:** **rocket launcher**, 2 boxes of rockets, a box of shells, medikit.
11. **Tower stair (TS).** Seven steps 128 wide rise north to 192; the 96 step blinks. A shut closet sits behind its east wall. **Pickups:** stimpack.
12. **Tower cab (TC), the set piece.** 256×304, 192/320, bright screens. The window (sill 224) looks west over the whole field at eye height 233. **The switch beside the window lowers every cask in the hall.** It acts on one tag, lowering each cask to its lowest neighbour at 1 unit a tic, so the tallest cask takes 5.5 s.
    - The maze sinks into the floor while you watch. The lit lanes stay on the floor as stripes, and the cask footprints stay as steel plates.
    - The imps and the revenant on the cask tops come down with them, and so do the supplies on the tops.
    - The 6 mancubi (4, 2) sealed in cells among the casks are suddenly standing in the open, facing the window.
    - The same tag drops the wall of the stair closet behind you: a revenant (1, 0) and 2 imps (1, 2) come up the stair, so the cab isn't a place to camp.
    - **Pickups:** medikit, 2 rockets.
13. **The arena (H, open state).** The hall is now 1664×1472 and flat. The four SUPPORT2 columns, the gallery stair and the tower base are the cover.
    - **Encounter:** 6 mancubi (spatial pressure: they fill the floor with fireballs, and they soak damage), plus whatever is left of the maze.
    - **Pickups:** on the former cask tops, now at 0: the megasphere (south-west), 2 boxes of rockets, a box of shells, a cell pack.
    - **Gate: the last mancubus's death lowers the dispatch shutters** (tag 666). There's no switch. The shutters are under the EXIT sign the player has seen since the gallery, and they drop in sight of the fight.
14. **Dispatch bay (DS, DA, DST, DD).** The shutters sink to 0. Behind them is an apron (0/192, strobing) and two steps up to the dock (64/256, 960×352), which holds crate stacks.
    - **Encounter** (deaf): 3 arachnotrons (2, 1) spread between the crates, firing into the hall as soon as the shutters drop; 3 imps (2, 1); a chaingunner (1, 0) behind a crate.
    - **Pickups:** medikit, 2 boxes of rockets, cell pack.
15. **Exit (EX, EV).** A door in the dock's north wall, with an EXITSIGN over it, leads into a glowing vault (256×240, 72/200). The exit switch is on the vault's north wall.

Optional spaces:

16. **Records office (RO)**, 288×256, 192/320, wood-panelled. Doors lead to the gallery's north end and to the landing, closing a loop. **Encounter:** 2 zombiemen (2, 1), a shotgun guy (1, 0). **Pickups:** 2 stimpacks, armor bonuses. Secret 2 is behind a panel.
17. **Cooling pond yard (CP).** Reached through B0's east door and a corridor 304 long (CPC). It's 512×1088 under the sky. Walkways at -16 run round a damaging nukage pond (-40, `DAMAGE_5`), with an island in it that holds the **megaarmor**. Every edge of the pond is a 24 step, so you can climb out anywhere. **Encounter:** 2 cacodemons (1, 1) over the pond, 3 imps (2, 1) on the far walkway. **Pickups:** 2 boxes of rockets, medikit. **Visible:** the tower roof's blinking beacon, and the soulsphere on its edge, 256 up at the yard's north-west (secret 4).

## Sketch

The plan uses 64 units per character across and 64 per row. Each row label is that row's top edge (y). The x ticks are every 512 units, starting at x = -512.

```
  2304                      EEeE
  2240                      EEEE
  2176                      EEEE
  2112                      EXXE
  2048                kkkkkkkkkkkkkkk
  1984                k[[kkkkkkkkkkkk
  1920                k[[kkkkkkkkkkkk
  1856                kkkkkkkkkkkk[[k
  1792                kkkkkkkkkkkk[[k
  1728          22    kkkkkkkkkkkkkkk
  1664          2D      aaaaaa             333
  1600         oooo     aaaaaa  bbbb       333
  1536         oooo     vvvvvv  bbbb       3D3
  1472         ooooD===................####...
  1408         ooooD===................MMM#...
  1344         DD   ===................MMM#...
  1280   nnnnnnnnn  ===...####..###K...####...CCCC  RRR
  1216   www   uuu  ===...#MM#..###K...#PP#...WCCC  RRR
  1152   www   uuu  ===...#MM#..YY#K...#PP#...WCCCDRRRR
  1088   www   uuu  ===...####..YYKK...####...SCCC  RRR
  1024   www   uuuuD===.........####..........CCCC pppppppp
   960   www   uuuuD===.........####.......... ^^  pppppppp
   896   www   uuu  ===.........####.......... ^^  pppppppp
   832   ddd        ===...##########...####### ^^xxpp%%%%pp
   768   dd%        ===...#PP####MM#...#MM#### ^^  pp%%%%pp
   704   dd%        ===...#PP####MM#...#MM#### ^^  pp%%%%pp
   640   dd%        ===...##########...####### TTTTpp%%%%pp
   576   dd%        ===...##+#................!TTTTpp%%%%pp
   512   dd%        ///...####................!TTTTpp%ii%pp
   448   dd%        ///...#################### TTTTpp%%%%pp
   384   dd%        ///...#PP####MM#MM##PP####     pp%%%%pp
   320   LLLLLLL    ///...#PP####MM#MM##PP####     pp%%%%pp
   256   LLLLLLL    ///...##########MM########     pp%%%%pp
   192   LLLLLLL    ..........................     pp%%%%pp
   128   LLLLLLL    ..........................Dpppppppppppp
    64   LLLLLLL    .............z............Dpppppppppppp
     0     DD             gg GGG                   pppppppp
   -64   yyyyyyyyyyyyyyyyyyyyyyyyy
  -128   yyyyyyyyyyytttyyyyyyyyyyy
  -192   yyyyyyyyyyytttyyyyyyyyyyy
  -256   ssssyyyyyyyyyyyyyyyyyyyyy
  -320   ss@syyyyyyyyyffccffyyyyyy
  -384   ssssyyrrrrrrrffccffrrrrrr
            |       |       |       |       |       |
            -512    0       512     1024    1536    2048
```

**Legend.**

| Symbol | Meaning |
|---|---|
| **Start and yard** | |
| `@` | start, facing east |
| `s` | guardhouse, 16 |
| `y` | yard, 0, sky |
| `t` | truck crates, 64/128 |
| `r` | rails, -8 |
| `f` | flatcar, 24 |
| `c` | flatcar cask, 152 (secret 1 inside) |
| `g` | barred gate window |
| `G` | gate, opens from inside |
| **West wing** | |
| `L` | lockers, 0 |
| `d` | decon, -8 |
| `w` | stair, 16→184 |
| `n` | landing, 192 |
| `u` | corridor and passage, 192 |
| `o` | records office, 192 |
| `2` | secret 2 |
| **Hall** | |
| `=` | gallery, 192, railed on its east edge |
| `/` | gallery stair, 168→24 southward, railed on its east edge |
| `.` | aisles, 0 |
| `#` | casks, 96–192 (they sink with the switch) |
| `P` | columns (they stay) |
| `M` | mancubus cells, 0, sealed by casks |
| `K` | key-stack steps, 24–120 |
| `Y` | key-stack top, 144, yellow key |
| `+` | megasphere on a 128 cask |
| `z` | gate switch |
| `!` | yellow door |
| `b` | key-trap closets |
| `3` | secret 3, 16 |
| **Tower** | |
| `T` | tower base, 0 |
| `^` | tower stair, 24→168 |
| `x` | stair closet, 96 |
| `C` | cab, 192 |
| `W` | cab window, sill 224 |
| `S` | cask switch |
| `R` | tower roof and its steps, 216–256 (secret 4) |
| **Cooling pond yard** | |
| `p` | cooling pond yard, -16, sky |
| `i` | island, -16, megaarmor |
| **Dispatch and exit** | |
| `v` | dispatch shutters, 192→0, tag 666 |
| `a` | apron, 0, and steps, 24/48 |
| `k` | dock, 64 |
| `[` | crates |
| `X` | exit door |
| `E` | exit vault, 72 |
| `e` | exit switch |
| **Shared** | |
| `%` | nukage: the decon drain at -24 (harmless) and the cooling pond at -40 (damaging) |
| `D` | doors, including secret doors |

Rectangles (map units). They don't overlap, except where one is cut out of another (pillars, cells, the island, the flatcar cask).

| Id | x0..x1 | y0..y1 | Floor | Notes |
|---|---|---|---|---|
| GH | -704..-448 | -448..-256 | 16 | start (-576,-352) facing east; window in the east wall, y -416..-320, sill 48; door in the north wall at x -640..-512 |
| RY | -704..896 | -448..-32 | 0 | sky; split at x 0 into a west half (route) and an east half |
| TK | 0..192 | -256..-96 | 64 / 128 | the truck: crate stack |
| RB | -320..896 | -416..-352 | -8 | rail bed |
| FC / CK | 128..512 / 256..384 | -432..-336 | 24 / 152 | flatcar and its cask; the cask is hollow (64² at 24) with a hatch in its north face (secret 1) |
| BG / BGW | 576..768 / 384..512 | -32..0 | door / sill 32, lintel 128 | gate (no use action from the yard), barred window (MIDGRATE) |
| LK | -704..-256 | 0..320 | 0 | door from the yard at x -576..-448 |
| DC / DR | -704..-512 / -544..-512 | 320..832 / 352..800 | -8 / -24 | doors at y 320 and y 832; three shower niches in the west wall |
| WS | -704..-512 | 832..1216 | 16..184 | 8 steps, 48 deep, rising north |
| LN | -704..-128 | 1216..1312 | 192 | door to RO at x -288..-160, y 1312..1344 |
| UC / GP | -320..-128 / -128..-32 | 832..1216 / 896..1024 | 192 | gallery door GD at x -32..0, y 896..1024 |
| RO / S2 | -320..-32 / -256..-96 | 1344..1600 / 1632..1760 | 192 | door to the gallery at y 1344..1472; secret door in RO's north wall at x -192..-128 |
| H | 0..1664 | 0..1472 | 0 | hall, ceiling 384 |
| GS | 0..192 | 192..528 | 24..168 | 7 steps, 48 deep, descending south into B0; rail on x 192 |
| GL | 0..192 | 528..1472 | 192 | rail on x 192; three sectors (to y 896, to 1088, to 1472) |
| Aisles | A0 x 192..384, A1 640..768, A2 1024..1216, AP 1472..1664; B0 y 0..192, B1 448..576, B2 832..1024, B3 1280..1472 | | 0 | each split at block edges into node and segment sectors (lit lanes, optional share) |
| K1R1 | 384..640 | 192..448 | 128 | cask ring around column P1 (448..576, 256..384) |
| K2R1 | 768..1024 | 192..448 | 160 | ring around cell C1 (816..976, 240..400) |
| K3R1 | 1216..1472 | 192..448 | 160 | ring around column P2 (1280..1408, 256..384) |
| K1R2 | 384..640 | 576..832 | 96 | ring around column P3 (448..576, 640..768); an imp on its top |
| K2R2 | 768..1024 | 576..832 | 160 | ring around cell C2 (816..976, 624..784) |
| K3R2 | 1216..1472 | 576..832 | 160 | ring around cell C3 (1264..1424, 624..784) |
| K1R3 | 384..640 | 1024..1280 | 160 | ring around cell C4 (432..592, 1072..1232) |
| K3R3 | 1216..1472 | 1024..1280 | 128 | ring around column P4 (1280..1408, 1088..1216) |
| B1H01 | 384..640 | 448..576 | 128 | low cask: the gallery sees over it down B1; megasphere and an imp on top |
| A1V01 / A1V12 | 640..768 | 192..448 / 576..832 | 128 / 128 | rocket box on A1V01; an imp and a cell pack on A1V12 |
| B2H12 | 768..1024 | 832..1024 | 192 | tallest cask; the pain elemental starts on it |
| APV01 / APV12 | 1472..1664 | 192..448 / 576..832 | 128 / 160 | rocket box on APV01; the revenant on APV12 |
| A2V01 | 1024..1216 | 192..448 | 160 | ring around cell C5 (1056..1184, 224..416) |
| B3H23 | 1216..1472 | 1280..1472 | 160 | ring around cell C6 (1248..1440, 1312..1440) |
| Key stack (K2R3) | S1s 960..1024 × 1216..1280; S2s × 1152..1216; S3s × 1088..1152; S4s × 1024..1088; S5s 896..960 × 1024..1088; KT 768..896 × 1024..1152; KR the rest of 768..1024 × 1024..1280 | | 24, 48, 72, 96, 120; KT 144; KR 160 | yellow key at (832,1088); KT touches KR (+16, a dead end) and B2H12 (+48, too high to climb) |
| KC | 768..1024 | 1504..1600 | 0 | two key-trap closets; doors in the north wall at y 1472..1504 |
| S3 | 1472..1664 | 1504..1664 | 16 | secret door at x 1536..1600 in the north wall |
| DS | 256..640 | 1472..1504 | 192 → 0 | three shutter sectors 128 wide, floor = ceiling = 192, tag 666; SUPPORT2 jambs at x 224..256 and 640..672; EXITSIGN above |
| DA / DST | 256..640 | 1504..1600 / 1600..1696 | 0 / 24, 48 | apron (strobe), two steps 48 deep |
| DD | 128..1088 | 1696..2048 | 64 | crates CR1 (192..320, 1856..1984) at 128 and CR2 (896..1024, 1760..1888) at 192 |
| EX / EV | 576..704 / 512..768 | 2048..2064 / 2064..2304 | door / 72 | exit switch on EV's north wall |
| TD | 1664..1712 | 448..576 | door | yellow, with 128-high recesses on both sides |
| TB | 1712..1968 | 384..640 | 0 | |
| TS | 1712..1840 | 640..976 | 24..168 | 7 steps, 48 deep, rising north |
| TSW / TSC | 1840..1856 / 1856..1984 | 784..832 / 752..864 | 208 → 96 / 96 | closet wall on the cask tag (floor = ceiling = 208, lowers to the 96 step) |
| TC | 1680..1936 | 976..1280 | 192 | window WN at x 1664..1680, y 1088..1216, sill 224, lintel 320; switch on the west wall at y 1024..1088 |
| TRS / TR | 1936..2032 / 2032..2224 | 1072..1168 / 1024..1280 | 216, 240 / 256 | secret door at x 1936, y 1088..1152; sky; beacon |
| CPD / CPC | 1664..1696 / 1696..2000 | 32..160 | door / 0 | |
| CP / PD / IS | 2000..2512 / 2128..2384 / 2208..2304 | -64..1024 / 128..832 / 432..528 | -16 / -40 / -16 | sky; pond `DAMAGE_5`, glowing; TR's 272-high face is on CP's north edge at x 2032..2224 |

Triggers:

| Trigger | Where | Effect |
|---|---|---|
| Gate switch (S1, SW1CMT in a SUPPORT2 frame) | hall south wall at (832,0), in B0 | opens BG, the yard gate |
| Yellow-key pickup (W1 ring) | round the key on KT | opens the two KC closet doors |
| Yellow door (DR, yellow key) | TD | |
| Cask switch (S1 floor lower to lowest neighbour, SW1COMP in COMPSPAN) | TC's west wall beside the window | tag CASKS, 24 sectors: the 8 cask rings, the 8 plugs and the 7 key-stack sectors (all to 0), and TSW (to 96) |
| Last mancubus dies | MAP07's boss rule | tag 666: the three DS shutters lower to 0 |
| Last arachnotron dies | MAP07's boss rule | tag 667: no sector carries it, so nothing happens |
| Secret doors | CK hatch, RO north wall, S3 panel, TC east wall | open (DR, ML_SECRET) |
| Exit switch | EV north wall | exit |

## Materials

The base family is **CEMENT**: pale concrete panels with a hazard band at their foot. **CEMENT6** covers every wall of the hall, the store's outside facade, and the connective rooms between areas. The casks are **SILVER1** steel: objects standing in the room, not walls of it. **SUPPORT2** is the trim in grey areas and **SUPPORT3** in the warm ones. Every door at an area boundary gets **DOORTRAK** jambs, or a key colour.

| Area (spaces) | Walls | Trim | Floor / ceiling flats | Reason |
|---|---|---|---|---|
| Cask hall (H: every aisle, node and wall; GL and GS faces; the arena after the drop) | CEMENT6 | SUPPORT2 pilasters framing the shutters and the gate switch; DOORTRAK at GD, the RO door, CPD and BG; MIDBARS3 rail on the gallery and stair | aisles SLIME14 (riveted grey plates); gallery and stair FLAT1 / CEIL3_5 over the casks, FLAT17 light panels over the aisles | the base family. The one big space keeps one material. Its four sides read by landmark (gallery W, tower window E, shutters and EXIT sign N, gate S) and by the lit lanes |
| Casks (all blocks, rings and plugs) | SILVER1 | none: free-standing; they meet only the floor | tops FLAT23 (brushed steel); cells SLIME14 at 0, the aisle flat, so the drop leaves one floor | steel objects against concrete |
| Key stack (S1s–S5s, KT, KR) | SILVER2 (blue lamps) on all its faces | — | steps and KR FLAT23; KT FLAT22 (blue light disc) | the landmark you steer by; the lamps say this cask is different |
| Columns P1–P4 | SUPPORT2, full height | — | — | the hall's structure, which stays when the casks go; cover in the arena |
| Start and yard (GH, RY, TK, RB, FC, BG and BGW outside) | BIGBRIK2 for the yard's perimeter and the guardhouse, inside and out; the store's facade is CEMENT6 (the same building as the hall) | SUPPORT2 round the gate and the guardhouse window; DOORTRAK at the locker door; gate face BIGDOOR2; window bars MIDGRATE | yard FLAT10 (gravel) / F_SKY1 (SKY1); rails MFLR8_1 at -8; flatcar SLIME15 at 24; truck CRATE1 sides, CRATOP1 tops; GH FLOOR0_1 / CEIL5_1 | outdoors: the plant's older brick against the store's concrete |
| Flatcar cask (CK) | SILVER1, like the hall's casks; the hatch is SILVER3 | — | FLAT23 top; inside FLAT23 at 24 | the one access panel is the cue for secret 1 |
| Staff side (LK, DC, DR) | ICKWALL1 (stained white tiles); ICKWALL3 in the shower niches | LITE5 strips in DC; DOORTRAK at the yard door and at both decon doors | FLAT18 at 0 and -8 / CEIL3_6; drain NUKAGE1 | the only white, tiled rooms: the wet, decontaminated side |
| West-wing connectors (WS, LN, UC, GP) | CEMENT6 | DOORTRAK where they meet DC and the gallery | FLOOR0_6 / CEIL5_2 | connective tissue, base family |
| Records office (RO, S2) | PANEL6 wood panels | PANBORD1 jambs at both doors; LITE5 strip beside the secret panel | FLAT5_5 / CEIL1_1 | the manager's office, the only wood in the plant |
| Tower (TD, TB, TS, TSC, TC, WN) | COMPWERD racks in TB, TS and TSC; COMPTALL screens in TC, with COMPSTA2 under the window | DOORYEL jambs at TD; COMPSPAN between screen bays and round the switch; SUPPORT2 at corners | TB and TS FLOOR0_3 / CEIL5_2; TC FLAT14 / TLITE6_1 | control: the screens say where the store is run from |
| Tower roof (TRS, TR) | CEMENT6 parapet faces; beacon column LITE3 | — | FLAT1 / F_SKY1 | outside the cab; the blinking beacon is the tease from the cooling pond yard |
| Key-trap closets (KC) | CEMENT6; door faces CEMENT6 (disguised as the hall wall) | — | SLIME14 / CEIL5_2 | part of the hall |
| Inspection bay (S3) | SILVER3 instrument panels | LITE5 strip beside the door (the cue) | FLAT23 at 16 / CEIL5_2 | cask inspection gear: the casks' family |
| Cooling pond yard (CPD, CPC, CP, PD, IS) | CPC CEMENT6; CP BROWNPIP pipework | DOORTRAK at CPD; SUPPORT3 where CPC opens into CP | CPC SLIME14 / CEIL5_2; walkways and island FLOOR6_2 at -16, pond NUKAGE3 at -40 / F_SKY1 | the plant's cooling works: outdoors, wet, brown |
| Dispatch (DS, DA, DST, DD, crates) | STARTAN3 tan panels; shutter faces BIGDOOR2, like the gate | SUPPORT3 at corners and round the exit door | apron SLIME14 at 0 (the hall flat, so there's no seam once the shutters are down); steps and dock SLIME16 / CEIL5_1; crates CRATE2 and CRATWIDE, tops CRATOP2 | the loading dock: warm tan and crates, the way out |
| Exit (EX, EV) | SHAWN2 aluminium with LITE5 strips | EXITSIGN over EX; SUPPORT3 jambs | FLOOR1_7 at 72 (glowing) / TLITE6_5 | the exit marker: the brightest room |
| Spills (RB, GUTTER, the cell leaks, DTR) | the walls of the space they lie in | NUKEDGE1 risers | NUKAGE1, 8–24 below the floor round it, `DAMAGE_5` | added after a human playtest asked for more nukage: the plant's waste in the open (see As built) |

Notes for the build:

- The gate and the shutters share BIGDOOR2, because they are the store's two big doors.
- Every switch sits in a trim frame: SW1CMT in SUPPORT2, SW1COMP in COMPSPAN, SW1EXIT in SHAWN2/LITE5.
- The metric counts any texture change in one wall plane without a border texture, including variants of one family. So don't switch CEMENT variants within a wall. If a wall needs relief, use a SUPPORT2 pilaster.

## Secrets

| # | Where | Hint | Reward |
|---|---|---|---|
| 1 | Inside the cask on the yard's flatcar (CK), through a hatch in its north face | It's the only cask with a SILVER3 access panel, and it's in view from the start window. | backpack, box of shells, box of bullets |
| 2 | The filing room behind the records office's north wall (S2) | A PANEL6 panel is shifted half a panel out of line, with a LITE5 strip beside it. | **rocket launcher**, leaked a whole maze early; box of rockets |
| 3 | The inspection bay behind the hall's north wall, at the north-east dead end of the maze (S3) | The spur leads nowhere else. The CEMENT6 panel at its end is shifted, with a LITE5 strip beside it. | plasma rifle, cell pack |
| 4 | The tower roof (TR), through a COMPTALL screen shifted out of line in the cab's east wall | The blinking beacon and the soulsphere on the roof's edge are in view from the cooling pond yard, 256 below. | soulsphere, box of rockets |

## Targets

| Target (DOOM II median) | Plan | Where it comes from |
|---|---|---|
| Optional share of area ≥ 0.3 [0.5] | ≈ 0.45–0.5 | About 2.5M critical of about 5.0M reachable. The optional parts are: the cooling pond yard and its corridor (0.6M); the yard's east half; RO and S2; the B0 aisle; the B1 and north-east spurs; A0 north of B2; the gallery's north third; the key-trap closets; the cask footprints off the arena crossing; S1–S4. It holds only if the aisles are split into node and segment sectors and the yard, gallery and dock into parts, because one big sector on the path counts whole. If the build measures under 0.3, split the dock and the arena's former cask rings further. |
| Distinct floor heights ≥ 15 [23] | about 28 | -40 pond; -24 drain; -16 CP walkways; -8 decon and rails; 0; 16 GH, S3 and the first WS step; 24 flatcar and steps; 40, 64, 88, 112, 136, 160, 184 WS steps; 48, 72, 96, 120, 144, 168 stair and stack steps; 64 dock; 72 exit; 96, 128, 160, 192 casks; 152 flatcar cask; 192 gallery, cab and RO; 208 TSW; 216, 240, 256 tower roof |
| Secrets ≥ 2 [4] | 4 | S1–S4 above |
| Light-effect sectors ≥ 3 [9] | about 10 | DC flicker (2 sectors), drain glow, KT glow, TS blink (the 96 step), TR beacon blink, DA strobe, CP pond glow, S3 flicker, EV glow |
| Deaf share (UV) ≥ 0.2 [0.42] | ≈ 0.75 | every monster in the hall (cells, cask tops, aisles, the gallery's foes), both closets (KC, TSC), the dock, TB, CP, the yard sentries |
| Most-used wall texture 0.2–0.45 [0.3] | ≈ 0.33 CEMENT6 (SILVER1 next, ≈ 0.22) | Rough wall areas: hall walls 2.4M, facade 0.5M, connectors and gallery face 0.8M, out of about 9.8M in total. If CEMENT6 reads above 0.45, use CEMENT7 in the west-wing connectors. If it reads below 0.2, the cask faces came out larger than planned; that's fine as long as SILVER1 stays at or below 0.45. |
| Rule-2 seams with a border ≥ 0.5 [0.31] | ≥ 0.6 | DOORTRAK, DOORYEL or PANBORD1 jambs at every area-boundary door; SUPPORT2 pilasters framing the shutters, the gate and the gate switch; COMPSPAN between cab screens; SUPPORT3 at the dock's corners and exit door; LITE5 at the secret panels and in DC; every switch framed. |

Balance targets for the build:

- **Ammo:** UV pistol-start ammo ratio 1.6–2.0. That's tighter than MAP06's 2.26 and nearer DOOM II's later maps.
- **Health:** 35–45 per 1,000 monster HP. The megasphere comes down with the casks, and the megaarmor and soulsphere are optional.
- **Skill ratios:** easy/UV ≈ 0.40 and HMP/UV ≈ 0.72, with items kept.
- **Weapons:** one within 300 of the start (the shotgun). In route order: shotgun (start), super shotgun (lockers), chaingun (gallery), rocket launcher (tower base; secret 2 leaks it early), plasma rifle (secret 3).
- **The cask switch:** it releases about 4,000 HP (6 mancubi, plus the stair closet's revenant and 2 imps). The tower base's 2 rocket boxes and shell box are what the player carries into the cab. The rockets, shells and cells on the cask tops arrive with the drop. Expect the static balance to list this trap; it stays if the curve after the drop isn't short.

### As built

Measured by the build (`levels/nukage_storage.py`, 179 sectors, monsters 30/54/75): every target above is met.

| Target | Built |
|---|---|
| Optional share | 0.67 (above the plan's 0.45–0.5, inside the IQR) |
| Distinct floor heights | 33 |
| Secrets | 4 |
| Light-effect sectors | 10 |
| Deaf share (UV) | 0.84 |
| Most-used wall texture | 0.30 |
| Rule-2 seams with a border | 0.95; the build lists no unbordered seam |
| Ammo ratio (UV, pistol start) | 2.44 (1.92 as first built; raised after a human playtest, below) |
| Health per 1,000 monster HP | 44.3 |
| Easy/UV, HMP/UV | 0.40, 0.72 |
| Nearest monster to the start | 488; the shotgun is 56 from the start |

Changes from the plan above, and why:

- **Shutters** are 128 high (floor = ceiling = 128, lowering to 0), not 192, so BIGDOOR2 fills each 128-wide shutter exactly. The EXIT signs (over the shutters, and over the exit door) are 64×16 sign sectors hanging 16 below the ceiling, the only way to show EXITSIGN whole on a wall taller than 16.
- **Gate** is 128 wide (x 608..736), for the same reason.
- **Rails** are concrete parapet strips (x 176..192), not MIDBARS3 bars. Bars block every mover, so the pain elemental and its lost souls couldn't come over the ledge. The gallery's parapet is 32 above it. Each stair parapet is 56 above its step: at 32 it was only 8 above the next step up, and the parapets climbed as a stair of their own.
- **Key stack**: in the plan's layout S5s touches only casks, and a floor lowers to its lowest neighbour at the moment the switch fires, so it would stop at 96. As built, the steps run west along B3 (S1s 960..1024 at 24, S2s, S3s, S4s 768..832 at 96, all × 1216..1280), S5s (120) sits at 768..832 × 1152..1216, KT at 768..896 × 1024..1152, and KR is the rest. Every stack sector touches an aisle, so all seven sink to 0.
- **Secret 1's hatch** is a SILVER3 floor that sinks to 0 when used (S1 floor lower), not a door: a door's face would stand above the cask top up to the sky.
- **Heights**: GH is 16/144, and LN, UC, GP and RO are 192/320, so that the 128-high door faces fit; the WS steps' ceilings rise with them. TRS has a 320 ceiling instead of sky, so the secret screen door's back fits too.
- **Pond**: a sector has one special, so the damaging pond can't also glow; the island glows instead.
- **Ammo trims** to bring the ratio from 2.52 to 1.92, all in side rooms and the dock: cask hatch shells (not a box), B1 spur shells (not a box), secret 3 and the dock a cell (not a cell pack), the cooling yard one rocket box and a rocket, the roof a rocket, the dock one rocket box and a rocket. Health: the B1 spur and cooling yard medikits are stimpacks, RO's second stimpack and the tower stair's are health bonuses.
- **Ammo restored after a human playtest**, who ran dry before the cask drop and had to scavenge (and punched a baron to death). On the main route before the drop, four single pickups became boxes: the lockers' and the corridor's shells, the B0/A0 shells and bullets, the B1 spur's shells. Secret 1 now holds a backpack, a box of shells and a box of bullets instead of a backpack and 4 shells. The ratio went from 1.92 to 2.44, and the printed curve's first leg (which merges everything up to the cask drop) went from a detour ratio of 0.68 to 1.02.
- **More nukage, after the same playtest** ("NEEDS MORE NUKAGE"). Four damaging (`DAMAGE_5`) NUKAGE1 spills, each with NUKEDGE1 risers: the yard's rail bed (RB, -8), in view on the way to secret 1; a 64-wide drain gutter (-16) along the foot of the gallery down the west side of A0, from R1 to the north wall; a pool (-16, inset 24) in each mancubus cell, where the cask leaked, so the arena has six hazards once the casks sink (the cells stay at 0, so the rings still sink to 0); and a trench (40, dock at 64) across the dock's east half, with the third arachnotron standing in it.
- **The A2/B1 group** (chaingunner, 2 shotgun guys, hell knight) stands in A2 just south of B1, behind K2R2, so none is in B1's 1000-long sightline back to the gallery.
- **The cask switch's trap** isn't in the build's trap list, which counts only triggers that open doors; it releases the 6 mancubi (3,600 HP) and the stair closet (revenant, 2 imps).
- **The reach model and the cells**: `reach.shoot_site` counts a level shot into a sector as a hit, without the target's height, so it says the mancubi can be shot from the gallery and the key stack before the drop. It fires the boss rule in wave 0, and the route curve has two legs (`boss @ kr`, exit) with no cask-switch leg. A 3D ray test over the pre-drop floors (gallery eye 233, every stack sector, the cab) finds no line to any mancubus's top (64) or eye (48) that clears the rings, so in the game the switch is still the way. The same approximation makes the long-range hitscan figure 60/s (the A2/B1 group and B0's shotgun guys from the gallery's north end, GP and the RO door); the casks block those lines too. Below the 88.4 warning threshold, so it's left as is.
- **The cells in the game**: the playtest confirms the ray test. Screenshots with every mancubus alive, from the gallery (south end, middle, north end), the key top (towards C3, C4, C5, C6), the stack's bottom step and the cab, show no mancubus over any ring, so the cask switch is required. With a monster's height (64) added to the reach model's shot test, for analysis only, the curve has the legs the route has (thorough / detour ratio): yellow key 1.94 / 1.20, cask switch 1.58 / 1.07, last mancubus 1.84 / 1.40, exit 1.95 / 1.51. Health never falls below 75 and is 200 at the exit, the long-range hitscan peak is 20/s, and the cask switch releases 4,020 HP against 5,690 ammo damage carried on the detour curve. Nothing is short, and the lowest detour ratio (1.07, at the cask switch) is above the DOOM II median low point (0.65).
- **Views the plan promised that come out partial.** Column P4 (in K3R3) stands on the line between the cab window and the middle of the field. From the cab it fills the middle of the view west, so the drop is watched on either side of it. From the gallery the cab window shows only beside P4, from the south and north thirds, and from the key top it's hidden. The gallery's 32-high parapet hides the aisles within about 400 of the rail; past that, the cask tops, the key stack, the pain elemental and the far aisles show.
- **Playtest** (`levels/playtests/nukage_storage.playtest`, UV): the wiring run passes with 29 checks and no fails. Its `killall` comes first, because monsters left standing block its walks in the yard, lockers and decon corridor. That kills the mancubi too, so the run checks the shutters at 128 before it and at 0 after the arena, which shows ZDoom applying MAP07's boss rule to this PWAD. The three fight seeds died 31, 42 and 45 times, 15 to 24 of them `starved`, and killed 73, 77 and 73 (lost souls included). None killed all six mancubi, so each was warped past the shut shutters into the dispatch bay. Every cluster is the bot's, and the curve above is nowhere short. Before the cooling pond yard each seed had spent 48–64 shells, 100–136 bullets and 8 rockets on about 2,000 HP; the 8 rockets went point blank at the records office's zombies. It then fought the yard's cacodemons dry, standing in the pond. In the footage, starved, it fled the key trap's baron into the north-east spur's dead end. At the yellow door it met the mancubi converging on it, and it died in the tower base with a few shells left. The `unseen` deaths are the bot at low health facing a door or wall, not hidden ambushes. No map change came out of the playtest.

## Build risks

- **MAP07's boss rule is the exit gate.** In vanilla `A_BossDeath`, on MAP07 the last mancubus's death lowers tag 666 to its lowest neighbour, and the last arachnotron's death raises tag 667 to texture. `levels/reach.py` models both.
  - **Mancubi:** every mancubus on the map counts. All of them must be in the cells, with at least one on every skill (easy has 2) and none anywhere else. A stray mancubus in a side room would lock the exit.
  - **Tags:** tag 666 goes only on the three shutter sectors. No sector may carry 667: raise-to-texture depends on lower-texture heights and on vanilla's texture-0 quirk, so nothing should depend on it. The arachnotrons' deaths then do nothing.
  - **UMAPINFO:** no `bossaction`.
  - **The builder:** `model.floor_movers` reads only line triggers, so it doesn't know the shutters move. Their faces won't be chosen or pegged for a moving floor, and the texture-fit checks won't see them open. Set the shutter faces in `OVERRIDES` (lower texture, unpegged so it sinks with the floor), or teach `floor_movers` the slot's boss tags.
  - **The wiring run:** the playtest player has god mode and doesn't fight. After the drop, use `killall`, then `expect floor` on a shutter `== 0`. That run is also the test that the engine applies MAP07's rule to this PWAD. Check it once in dsda-doom too.
- **The cask drop.** 24 sectors share one tag: 8 rings, 8 plugs, the 7 key-stack sectors and TSW. Each must lower to the 0 floor of the aisles and cells, except TSW, which stops at the 96 step. A cask that borders anything lower than 0 would sink below the floor. At 1 unit per tic, B2H12 takes 5.5 s. Monsters and items on the tops ride down. Put the cells and a few former cask footprints in `MUST_REACH`, so the reach check proves they open.
- **Sightlines into the cells before the drop.** Cell rings are 160 high and at least 192 from the gallery rail and the cab window. B2H12 (192) screens C2 from the key stack's top. A mancubus that sees the player over its ring would fire early and break the set piece. If the build or a fight run shows one, raise its ring or move the cell.
- **Running-jump reach.** The reach model lets a player run off a ledge and land lower across a gap: roughly 30 units of drop over 128, and 70 over 192. The gallery and stair are railed along x 192 for that reason, and KT is bounded by casks that are either climbable dead ends (KR) or too high (B2H12). Check the reach output: before the switch, no cask top except the stack may be reachable, which keeps the megasphere out of reach.
- **Doors in a 384 hall.** TD, CPD, the KC doors, the gate, GD, and the RO door (at 192 under a 384 ceiling) all need 128-high recesses on any side taller than 128. The gate's recess on the yard side pushes the yard's facade line south by its depth.
- **The grid.** Every block corner touches four aisle sectors, so add the shared vertices. Splitting the aisles into nodes and segments gives about 33 aisle sectors, and the whole map comes to about 160–180 sectors, at the top of the IWAD band.
- **Heavies in the open.** The arachnotrons (radius 64) need the 384-wide steps and 128 of clearance round the crates. The mancubi (radius 48) fit the cells: the narrowest, C5 and C6, are 128 across, 32 more than a mancubus.
- **Hitscanners on long sightlines.**
  - The yard is 1600 long: hitscanners stay within 768 of the route, with the truck between them and the gate end.
  - B1 is 1000 long once you're past its low cask: no hitscanner at its east end.
  - A0 under the gallery: its two shotgun guys fire up at the ledge from 200–400.
- **The pain elemental's souls in the aisles.** The pain elemental is meant to fight in open air at the gallery. Placed deaf on B2H12 facing west, it engages there. If it survives into the maze, its souls in 128-wide aisles are the player's problem, not the map's.
- **The fight bot.** The exit needs all six mancubi dead. A fight run that doesn't kill them will skip the dispatch steps and warp, so read that as bot, not map, unless the curve is short there.
- **Set bookkeeping.**
  - Add MAP07 sections to README "Included WAD" and SPOILERS, and the preview `wads/NUKAGE-MAP07.svg`.
  - This worktree's `wads/NUKAGE.WAD` has no MAP06, which lives on branch `map06`. Build into a scratch WAD while iterating. Write the real WAD only on top of a NUKAGE.WAD that has MAP06, and never merge the binary: rebuild it with `python3 -m levels nukage_storage`.

## Concepts considered

1. **The Cask Store (chosen).** A maze that becomes an arena. You look over a field of casks from a gallery and walk it aisle by aisle to the control tower. The tower switch sinks every cask, freeing the mancubi sealed among them, and the last one's death drops the dispatch shutters to the exit. It's gated by the maze, a yellow key on a cask stack, the switch, and MAP07's boss rule.
2. **Skylights.** A stitch across the roofline. You start on a roof at night with the stack's beacon in view. Each roof ends at a skylight you drop through, one way, into a dark building; you clear it and climb out by a stair you unlock from inside onto the next, higher roof. The pain elemental debuts over the roofs.
3. **Outfall.** A zig-zag descent down a cascading river. You follow a nukage river from the overflow at the top of a hillside plant down its SFALL cascades, crossing it at every fall, to the outfall gate you saw from the top. It's gated by bridges lowered from the far bank and drops beside the falls.
4. **Lockdown.** A chain of loops strung on one corridor. A straight spine runs the length of the plant, cut by blast doors that open only from their far side. Each section is passed by a loop through rooms on alternate sides, and the spine opens up behind you as a shortcut.
5. **Breakout.** A funnel opening to the sky. You start sealed in the sump at the bottom of the plant, and each space is bigger, brighter and higher than the last, up to an open yard and the exit gate. A slit of daylight far above the start is the reveal.

The Cask Store wins for four reasons:

- **It's a one-sentence shape whose second half is a new place.** The space changes state, so the map gets its contrast (cramped aisles, then open floor) and its set piece from one mechanism.
- **It uses the slot.** MAP07's boss rule works by slot in vanilla and in the ports, and the reach model already handles it. NUKAGE's MAP07 nods to Dead Simple without being an arena map.
- **Its mechanisms are cheap and robust.** One S1 floor-lower on one tag, and one boss-death floor-lower. There are no lifts and no rising floors on the critical path.
- **It steps the difficulty up by toughness, not head count:** six mancubi at once, then three arachnotrons, after a maze of fodder.

The others lose on these grounds:

- **Skylights** has no single set piece. Its drop-and-climb repeats, the open roofs invite sniping, and it needs many one-way drops and pits.
- **Outfall** is a descent, and SPEEDY has three. It has long sightlines down a valley, and its nukage crossings repeat MAP02 and MAP05.
- **Lockdown** repeats its one trick at every door, and a corridor with rooms off both sides is the template strung out.
- **Breakout** is a gradient, not a shape. It's linear, and its climax is a yard, not a fight.
