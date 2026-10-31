# Nukage Outskirts (`nukage_outskirts`)

## Concept

**Climb a sunlit hillside to the monitoring station on the ridge, find your way through it, and step out onto its observation deck: the far side of the hill drops into a nukage spill that fills the whole next valley, with the plant's wall beyond it.**

- **Shape:** up one side of a ridge and down the other, with the station as the gate between them. The climb is three switchback shelves cut into the hill. The hill itself hides the payoff, so the reveal comes from the terrain, not from a door onto a room you already knew about. Nothing on the climb side looks over the crest.
- **Theme:** the outskirts of the plant, before the meltdown has reached them. The climb side is still alive: grass on the valley floor, tan rock in sunlight, an abandoned UAC checkpoint booth, a cargo container toppled off the road. The station is clean UAC steel with blue instrument screens, in a dim interior under a red lockdown alarm. Over the ridge everything is scorched dark brown, and the only bright thing is the green glow of the spill. This light, colour and life contrast is what stops a short map from being drab.
- **Difficulty:** easy, the easiest map in the set. About 12/22/31 monsters on easy/HMP/UV, against MAP02's 21/43/57. Fodder only: zombiemen, shotgun guys, imps, and five demons, with no heavy monsters. The shotgun comes within 300 units of the start.
- **Slot:** MAP01 of `NUKAGE.WAD`, replacing Nukage Junction. `UMAPINFO`: `levelname` "Nukage Outskirts", `next` "MAP02", `music` D_RUNNIN. The sky is SKY1, DOOM II's own for MAP01-11, whose brown clouds suit the scorched valley.

How it differs from the set:

| Map | Shape in a phrase |
|---|---|
| MAP01 Nukage Junction (replaced) | the template: courtyard hub, one wing per key |
| MAP02 Nukage Crossing | two banks of a canal, joined by a sluice gate that sinks into a bridge |
| MAP03 Nukage Core | a spiral climb around a reactor to the crown |
| MAP04 Nukage Divided | a fork into two wings that never meet, keys crossed |
| MAP05 Nukage Drain | a ring of walkways raised one by one out of a flooded reservoir |
| MAP06 Nukage Undercurrent | one hall crossed twice: over it, then under it |
| MAP07 Nukage Storage | a cask maze sunk into an arena |
| MAP08 Nukage Lockdown | a loop round a spill basin, away from an exit you can see |
| MAP09 Nukage Meltdown | a descent down terraced falls to a cooling lake |
| **MAP01 Nukage Outskirts** | **up one side of a ridge; the spill is hidden on the other** |

Every later map shows its nukage early: MAP05 starts on the reservoir, MAP08 at a window over its basin, MAP09 on a balcony above the lake. This one hides it until the end, so the set opens with the reveal the later maps take for granted. MAP03 also climbs, but round a goal you can see the whole way up; here the goal is out of sight.

## Route

Heights are floor/ceiling. Coordinates are in the sketch's rectangle table. Skills are UV/HMP/easy.

1. **Valley floor (V)**, 1280×384 plus the 256×256 foot of the climb, floor 0, open sky (512). Grass, with the access road coming in from the west, buried under a rockfall (RF, a 72-high mound you can't climb). **Visible:** the hillside to the north, rising in three shelves. On top is the station's steel facade with its red lamp blinking over the front shutter: the goal is in view from the start. **Gate:** none. Leg 1 rises out of the valley's west end. **Encounter:** none; nothing can see the start. **Pickups:** a shotgun beside the rockfall (about 280 units from the start), 2 shells pickups, a clip.
2. **Guard hut (GH)**, optional, 256×256, 8/136. An abandoned UAC checkpoint booth on the valley's south side, with a small door. **Encounter:** none. **Pickups:** a stimpack, a clip. Its west wall has secret 1.
3. **Leg 1 (L1)**, 1024×256, rising east from 8 to 96 in six 16-unit steps, each 128 long. This is the road's first shelf, and its south edge becomes a drop to the valley as it rises. **Visible:** shelf 2's cliff face above, with a shotgun guy on the west hairpin. **Gate:** none. **Encounter:** 2 zombiemen at the east hairpin (2/2/1, fodder, deaf, facing east so they don't see the start). The shotgun guy on W2 shoots down at you here (see 6), which keeps you moving.
4. **East hairpin (E1)**, 256×512, 96. The road turns back west. **Visible:** east along the spur to the toppled container, and the lit ledge above it with the chaingun (secret 2). **Pickups:** a stimpack, shells.
5. **Spur (SP)**, optional, 384×256, 88. A dirt pull-off where a UAC cargo container (CW, top 144) lies askew off the road beside a crate (CR, 120). **Encounter:** 1 imp on the container (UV only). **Pickups:** shells. Climb crate → container → ledge (SL2, 168) for secret 2.
6. **Leg 2 (L2)**, 1024×256, rising west from 112 to 192. **Visible:** leg 3's face above and the forecourt's edge at the top. **Encounter:** 2 imps along the leg (2/1/1, turrets throwing down from W2 and L3). 1 shotgun guy on the west hairpin's south edge (1/1/0), who also covers L1 below.
7. **West hairpin (W2)**, 256×512, 192, in the shadow of the west cliff (light 160).
8. **Leg 3 (L3)**, 1024×256, rising east from 208 to 288. Its north side is the 16-96-high face of the forecourt, so monsters on the forecourt edge stand above you. **Encounter:** 2 zombiemen on the leg (2/1/1), and 2 imps on the forecourt edge above (2/2/1, turrets).
9. **Forecourt (FC)**, 1280×256 plus 512×256 at the east end, 288. The paved apron in front of the station. **Visible:** the facade. The front shutter (SPCDOOR3) is shut under a blinking red lamp, and there is no switch on this side. A barred window beside it looks straight across the lobby, through the stair arch and up the stairs to the **blue door** at the top, lit blue. This is the door before the key. A shotgun guy and a zombieman in the lobby shoot back through the bars. **Gate:** the shutter opens only from inside, so the way in is round the east side. **Pickups:** a clip, shells.
10. **Service ledge (SV) and loading yard (LY)**, 256×192 at 288, then a 448×384 yard at 272, walled in by rock. **Visible:** only the yard and the dock. The yard's north wall is rock, so nothing over the ridge shows. **Gate:** the dock door (BIGDOOR2, 128 wide) in the station's east wall opens with a switch beside it on the dock (DP, 320). A step (DS, 296) climbs from the yard onto the dock. **Encounter:** 2 imps on the dock (2/1/1, deaf, elevated turrets) and a shotgun guy in the yard (1/1/0), an open-air brawl round the step. **Pickups:** a box of bullets, shells.
11. **Storeroom (ST)**, 256×256, 304/432. Dim, with crate stacks (CRATE1/CRATE2) as cover. **Encounter:** 1 zombieman among the crates (1/1/0). **Gate:** doors west to the instrument room and south to the generator room. The station's rooms form a ring (ST, IR, LB, GR), so you can go either way round. The north wall hides closet GC.
12. **Generator room (GR)**, 256×256, 296/424. Dark (light 96), blinking at random, with a grate floor. **Encounter:** 1 demon (1/1/1, deaf) in the dark, the map's first demon, a few steps from the door. **Gate:** doors north to ST and west to the lobby.
13. **Instrument room (IR)**, 256×256, raised floor at 320, ceiling 440, flickering. Banks of blue screens, with the **blue key** on a lit console in the middle. **Encounter:** 2 zombiemen behind the console banks (2/1/1). **Trap:** taking the key opens closet GC in the storeroom's north wall. Out come 2 demons and an imp (demons 2/2/1, imp 1/0/0, all deaf), back through the storeroom and into IR by its east door, or round through GR and the lobby. **Pickups:** a medikit by the west door, shells.
14. **Lobby (LB)**, 640×256, 288/416. The station's front room. A red alarm strip blinks along its south wall, over the front shutter and the window. **Visible:** the stair arch in the north wall, and up it the blue door. **Gate:** a switch beside the front shutter (framed in SUPPORT2) opens it onto the forecourt, closing a loop: forecourt → yard → dock → ring → lobby → forecourt. **Encounter:** a shotgun guy and a zombieman by the window (2/2/1). The zombieman is the one easy keeps. **Pickups:** a medikit, a clip.
15. **West corridor (WC) and locker room (LK)**, optional, 128×256 at 288, then 256×256 at 296. Rows of METAL5 lockers. **Encounter:** 1 imp (1/1/0, deaf). **Pickups:** a stimpack. Secret 3 is behind a shifted locker.
16. **Stair hall (SH)**, 256×256, rising 288 → 352 in four 16-unit steps 48 deep. Walled in SILVER2, whose blue lights lead the eye to the **blue door** at the top. **Gate:** the blue door. **Encounter:** none: this is the breath before the reveal.
17. **Observation deck (DK), the reveal.** A 576×176 open grate deck at 352, railed along its north edge (MIDBARS3). **Visible:** the whole spill valley below, 2700 units wide and 336 down. The nukage fills it wall to wall. A long concrete jetty runs out across it to the intake house in the plant's concrete wall, with an EXIT sign over its arch. A rock island glows to the east with something blue on it (secret 4). In the far north-east corner, nukage pours from the plant's outfall down its wall. **Gate:** the stair down (F1) starts at the deck's west end. **Encounter:** none. The view is the event, and nothing in the valley can see the deck door (start-of-reveal safety). **Pickups:** none.
18. **Cliff stair (F1), landing (LD) and lift (LF)**. F1 is 576×128, descending west from 336 to 208 in nine 16-unit steps 64 deep, cut along the cliff below the deck, open on its north side (dropping off to the shore is allowed). LD is 192×192 at 192. LF is a 128×128 lift from 192 down to 16, walked on from the top and used from the shore to come back up. **Encounter:** 2 imps on the shore below the lift (2/1/1), throwing up at the stair.
19. **Shore (SHR)**, 2432×320, floor 16, open sky. Scorched mud along the foot of the cliff, 16 above the nukage, so you can step out of it anywhere. **Visible:** the jetty's root at x 1152, and the island. **Encounter:** 3 imps on the far bank across the spill (3/2/1, deaf). Once woken, they wade towards you through the nukage. 1 zombieman by the pump shed (1/0/0). **Pickups:** a stimpack, shells.
20. **Pump shed (PS)**, optional, 256×192, 24/152, at the shore's east end. **Pickups:** a box of shells, a clip.
21. **The spill (NP), island (IS) and far bank (FB)**, optional: the nukage pool at 0 (DAMAGE_5), a 192×192 rock island at 16 (secret 4), and a 128-deep bank at 16 along the foot of the plant wall. There's no radiation suit. Wading is a choice, at 5 health per second.
22. **Jetty (JT)**, 128×640, floor 24, straight out across the spill to the intake house. **Trigger:** a W1 line across the jetty's root opens closet JC in the intake house. **Encounter:** 2 demons charge out of the arch and down the jetty at you (2/2/1, deaf meat shields). The 128-wide jetty makes them a queue in your shotgun's cone, while the far-bank imps throw from the side.
23. **Intake house (IH) and exit**, 384×256 (half on the far bank, half over the spill), 24/152, glowing. The plant's own brown steel panels: the first piece of the plant itself. The exit switch is in a niche in its north wall, the way into the plant (and MAP02's canal).

## Sketch

Plan at 64 units per character, both across and per row. Row labels give each row's bottom edge (y); the x ticks are every 512 units.

```
  3264     -------------------XXXXXX-----------oooo--      plant wall along y 3328 (STONE), outfall falls at x 2048-2304
  3200     -------------------XXXXXX-----------oooo--
  3136     ~~~~~~~~~~~~~~~~~~~XXXXXX~~~~~~~~~~~~~~~~~
  3072     ~~~~~~~~~~~~~~~~~~~XXXXXX~~~~~~~~~~~~~~~~~      IH arch at y 3072, EXIT sign over it
  3008     ~~~~~~~~~~~~~~~~~~~~~JJ~~~~~~~~~~~~~~~~~~~
  2944     ~~~~~~~~~~~~~~~~~~~~~JJ~~~~~~~~~~~~~~~~~~~
  2880     ~~~~~~~~~~~~~~~~~~~~~JJ~~~~~~444~~~~~~~~~~
  2816     ~~~~~~~~~~~~~~~~~~~~~JJ~~~~~~444~~~~~~~~~~
  2752     ~~~~~~~~~~~~~~~~~~~~~JJ~~~~~~444~~~~~~~~~~
  2688     ~~~~~~~~~~~~~~~~~~~~~JJ~~~~~~~~~~~~~~~~~~~
  2624     ~~~~~~~~~~~~~~~~~~~~~JJ~~~~~~~~~~~~~~~~~~~
  2560     ~~~~~~~~~~~~~~~~~~~~~JJ~~~~~~~~~~~~~~~~~~~
  2496     ~~~~~~~~~~~~~~~~~~~~~JJ~~~~~~~~~~~~~~~~~~~
  2432     ~~~~~~~~~~~~~~~~~~~~~JJ~~~~~~~~~~~~~~~~~~~      W1 at the jetty root -> JC opens
  2368     __________________________________________
  2304     __________________________________________
  2240       vv__________________________________PPPP
  2176       vv__________________________________PPPP
  2112       ddd_________________________________PPPP    deck rail along y 2112
  2048       dddfffffffffDDDDDDDDD
  1984       dddfffffffffDDDDDDDDD gg
  1920                   DDDDDDDDD gg  yyyyyyy           blue door at x 704-832, y 1920
  1856               KKKK^^^^IIIITTTTkk=yyyyyy
  1792             33KKKK^^^^IIIITTTTkk=yyyyyy
  1728             33KKKK^^^^IIIITTTTkkyyyyyyy           dock door at x 1408, y 1728-1856
  1664               KKKK^^^^IIIITTTTkkyyyyyyy
  1600               wwLLLLLLLLLLGGGGkkyyyyyyy
  1536               wwLLLLLLLLLLGGGGllll
  1472               wwLLLLLLLLLLGGGGllll
  1408               wwLLLLLLLLLLGGGGllll                  facade y 1408: window x 704-832, shutter x 960-1088
  1344             FFFFFFFFFFFFFFFFFFFF
  1280             FFFFFFFFFFFFFFFFFFFF
  1216             FFFFFFFFFFFFFFFFFFFF
  1152             FFFFFFFFFFFFFFFFFFFF
  1088     WWWWccccccccccccccccFFFFFFFF                     L3 rises east 208 -> 288
  1024     WWWWccccccccccccccccFFFFFFFF
   960     WWWWccccccccccccccccFFFFFFFF
   896     WWWWccccccccccccccccFFFFFFFF
   832     WWWWbbbbbbbbbbbbbbbbEEEE                         L2 rises west 112 -> 192
   768     WWWWbbbbbbbbbbbbbbbbEEEE
   704     WWWWbbbbbbbbbbbbbbbbEEEE
   640     WWWWbbbbbbbbbbbbbbbbEEEE   22
   576     ....aaaaaaaaaaaaaaaaEEEEssssss                   L1 rises east 8 -> 96
   512     ....aaaaaaaaaaaaaaaaEEEEsxCCCs
   448     ....aaaaaaaaaaaaaaaaEEEEssCCCs
   384     ....aaaaaaaaaaaaaaaaEEEEssssss
   320 rrrr....................
   256 rrrr....................
   192 rrrr....................
   128 rrrr......@.............
    64 rrrr....................
     0 rrrr....................
   -64                 hhhh
  -128               11hhhh
  -192               11hhhh
  -256                 hhhh
       |       |       |       |       |       |
       -512    0       512     1024    1536    2048
```

Legend: `@` start at (128,128), facing north · `r` rockfall 72 · `.` valley floor 0 · `h` guard hut 8 · `1` secret 1 · `a` leg 1, 8→96 · `E` east hairpin 96 · `s` spur 88 · `x` crate 120 · `C` container 144 · `2` secret 2 ledge 168 · `b` leg 2, 112→192 · `W` west hairpin 192 · `c` leg 3, 208→288 · `F` forecourt 288 · `l` service ledge 288 · `y` loading yard 272 · `=` dock step 296 · `k` dock 320 · `w` west corridor 288 · `L` lobby 288 · `G` generator room 296 · `K` locker room 296 · `3` secret 3 · `^` stair hall 288→352 · `I` instrument room 320 · `T` storeroom 304 · `g` key closet 304 · `D` observation deck 352 · `f` cliff stair 336→208 · `d` landing 192 · `v` lift 192↔16 · `_` shore 16 · `P` pump shed 24 · `~` spill 0 · `4` secret 4 island 16 · `J` jetty 24 · `X` intake house 24 · `-` far bank 16 · `o` outfall channel. Blank is solid rock: the ridge between the two valleys has no openings except the station.

Section north–south through the station's axis, x ≈ 768, looking west. The ridge is what hides the spill:

```
      valley A (sunlit)              station                deck   valley B (scorched)
                                    +--------------+  blue  +--+ rail
  288 ........................ FC   |  lobby  stair|  door  |DK|  352
  192 ..................... L3/W2   |   288   /// |        |  |\
   96 ............. L2/E1           +--------------+        |  | \ cliff, F1 cut along it
    0 ....... L1 ...V (@)                                    rock \___ shore 16 ~~~~ spill 0 ~~~~ JT -> IH
```

Rectangles (map units). Steps within a leg are 128 long in x, at the same x on all three legs (x 256, 384, 512, 640, 768, 896), so the legs share vertices.

| Id | x0..x1 | y0..y1 | Floor | Notes |
|---|---|---|---|---|
| RF | -512..-256 | 0..384 | 72 | rockfall, unclimbable backdrop |
| V | -256..1024 / -256..0 | 0..384 / 384..640 | 0 | start (128,128); shotgun at (-128,256) |
| GH / SC1 | 512..768 / 384..512 | -256..0 / -192..-64 | 8 | door in GH's north wall at x 576..704; secret panel at x 512 |
| L1 | 0..1024 | 384..640 | 8, then 16..96 from x 256 | the junction with L2 is x 896..1024 (96 vs 112) |
| E1 | 1024..1280 | 384..896 | 96 | |
| SP / CR / CW / SL2 | 1280..1664 / 1344..1408 / 1408..1600 / 1472..1600 | 384..640 / 512..576 / 448..576 / 640..704 | 88 / 120 / 144 / 168 | CW may be drawn rotated about 20° in the build, keeping CR's edge on it |
| L2 | 0..1024 | 640..896 | 112 (x 768..1024) rising west to 192 (x 0..256) | the junction with L3 is x 0..256 (192 vs 208) |
| W2 | -256..0 | 640..1152 | 192 | |
| L3 | 0..1024 | 896..1152 | 208 (x 0..256) rising east to 288 (x 768..1024) | runs into FC at its east end |
| FC | 256..1536 / 1024..1536 | 1152..1408 / 896..1152 | 288 | porch lamp strip x 896..1152, y 1344..1408, canopy 432 |
| SV | 1408..1664 | 1408..1600 | 288 | |
| LY / DS | 1536..1984 / 1536..1600 | 1600..1984 / 1792..1920 | 272 / 296 | |
| DP | 1408..1536 | 1600..1920 | 320 | dock switch at x 1408, y 1632..1696 |
| WC | 384..512 | 1408..1664 | 288 | door to LB at x 512, y 1472..1600; to LK at y 1664 |
| LB | 512..1152 | 1408..1664 | 288 | window x 704..832 (sill 336); shutter x 960..1088; stair arch x 704..832 at y 1664 |
| GR | 1152..1408 | 1408..1664 | 296 | door to LB at x 1152, y 1472..1600; to ST at y 1664, x 1216..1344 |
| LK / SC3 | 384..640 / 256..384 | 1664..1920 / 1728..1856 | 296 | shifted locker at x 384, y 1760..1824 |
| SH | 640..896 | 1664..1920 | 288→352 | blue door at y 1920, x 704..832 |
| IR | 896..1152 | 1664..1920 | 320 | door to LB at y 1664, x 960..1088; to ST at x 1152, y 1728..1856; key console at (1024,1792) |
| ST / GC | 1152..1408 / 1280..1408 | 1664..1920 / 1920..2048 | 304 | dock door at x 1408, y 1728..1856; GC opens into ST |
| DK | 640..1216 | 1936..2112 | 352 | railed on the north |
| F1 / LD / LF | 64..640 / -128..64 / -128..0 | 1984..2112 / 1984..2176 / 2176..2304 | 336→208 / 192 / 192↔16 | |
| SHR | 0..2432 / -256..0 | 2112..2432 / 2304..2432 | 16 | excluding LD and PS |
| PS | 2176..2432 | 2112..2304 | 24 | |
| NP / IS | -256..2432 / 1600..1792 | 2432..3200 / 2752..2944 | 0 / 16 | |
| JT | 1088..1216 | 2432..3072 | 24 | W1 across it at y 2448 |
| IH / JC | 960..1344 / 960..1088 | 3072..3328 / 3136..3264 | 24 | exit niche at the north wall, x 1136..1168 |
| FB / OF | -256..2432 / 2048..2304 | 3200..3328 | 16 / -8 | OF channel with SFALL falls on the plant wall above it |

Triggers:

| Trigger | Where | Effect |
|---|---|---|
| Dock switch | DP, beside the dock door | opens the dock door (S1, stays open) |
| Blue-key pickup | line ring round the IR console | opens GC (W1) |
| Front shutter switch | LB, beside the shutter | opens the front shutter (S1, stays open): the loop to FC |
| Lift LF | top: walk-over; bottom: use | lowers to 16 / brings you back up |
| Jetty line | across JT at y 2448 | opens JC (W1) |
| Exit switch | IH's north niche | S1_EXIT |

## Materials

The base family is **ASHWALL** (ASHWALL4 main, ASHWALL3 on the lower faces near the water), the scorched rock of the spill valley. That valley is the biggest open space and the map's destination, so its material holds the map together. The climb side's signature is **ROCK5**, tan rock in sunlight, and the two never meet: the ridge and the station stand between them. The UAC buildings are **SHAWN2** outside and **SILVER1** inside, one steel family. The plant is **STARTAN3** and **STONE** at the very end. Trim is **SUPPORT2** wherever steel meets rock or a door or switch sits in a wall, **DOORTRAK** on door jambs, and **LITE5** strips as the secret language (the WAD's: a shifted panel beside a light line).

| Area (spaces) | Walls | Trim | Floor / ceiling flats | Reason |
|---|---|---|---|---|
| Climb side (V, RF, L1, E1, SP, L2, W2, L3, FC, SV, LY, DS) | ROCK5 cliffs and shelf faces; RF ROCK5 | SUPPORT2 where the facade meets the rock (x 384, x 1408) and round the dock | V GRASS1 at 0; legs, hairpins, FC, SV, LY FLOOR6_2 (road gravel); SP RROCK16; RF top RROCK09 / F_SKY1 | one continuous hillside, one material. Shelves are told apart by height and light (208 in the sun, 160 at W2 under the west cliff), never by texture |
| Container wreck (CR, CW) | CW SHAWN2 (a UAC container); CR CRATE1 | — | CW CRATOP1; CR CRATOP2 | an object on the hillside, not a wall of it |
| Secret 2 ledge (SL2) | ROCK5, with LITE5 strips either side of the alcove | LITE5 | RROCK09 at 168 | the lit ledge is the tease from E1 |
| UAC exteriors (station facade, dock DP, guard hut GH, pump shed PS) | SHAWN2; SHAWN1 (UAC logo) over the front shutter and on GH's front; front shutter SPCDOOR3; window bars MIDGRATE | SUPPORT2 frames on the shutter, window, dock door and switches; DOORTRAK jambs | DP FLAT5_4 at 320; porch strip FLOOR6_2 / TLITE6_5 (blinking red); GH and PS FLOOR0_6 / CEIL3_5 | one family for every UAC building outside the plant; the steel interrupts the rock, so every seam has a pilaster |
| Secret 1 (SC1) | SHAWN2 | LITE5 beside the shifted panel | FLOOR0_6 / CEIL3_5 | the WAD's secret cue |
| Station interior (WC, LB, GR, ST, GC) | SILVER1; ST crate stacks CRATE1/CRATE2 | SUPPORT2; DOORTRAK on door jambs; red alarm strip in LB | LB, WC FLOOR0_3 / CEIL3_5; GR MFLR8_1 at 296 / CEIL5_1; ST, GC FLOOR4_8 at 304 / CEIL3_5 | connective tissue inside the station. Rooms differ by light (GR dark and blinking, LB red alarm) and floor height, not by wall material |
| Instrument room (IR) | COMPTALL and COMPSTA1 screen banks in SILVER1 bays; console sides COMPSTA2 | COMPSPAN between screen bays, SUPPORT2 at corners | FLAT14 at 320 / TLITE6_1; console top CONS1_5 at 344 | the key room's signature: a monitoring station monitors; flickering screens |
| Locker room (LK, SC3) | SILVER1; METAL5 lockers set in SUPPORT2 frames along the east and west walls | SUPPORT2; LITE5 beside the shifted locker | FLOOR0_6 at 296 / CEIL3_5 | lockers as furniture in the steel family, framed so they don't read as a new material |
| Stair hall (SH) and blue door | SILVER2 (blue light panels); blue door BIGDOOR2 | DOORBLU jambs | FLOOR0_3, risers STEP4 / CEIL3_5 | the blue lights lead from the lobby window to the blue door; key colour |
| Observation deck (DK) | station's north wall SHAWN2; cliff ends ASHWALL4; rails MIDBARS3 | SUPPORT2 where SHAWN2 meets ASHWALL4 (x 640, x 1216) | FLAT20 grate at 352 / F_SKY1 | structure on the scorched side; the first sight of the base family |
| Cliff stair, landing, lift (F1, LD, LF) | ASHWALL4; risers ASHWALL3; lift faces PLAT1 | — | F1, LD FLAT5_4 (cut steps); LF FLAT23 | cut into the scorched cliff; PLAT1 is the lift cue |
| Spill valley (SHR, NP, IS, FB) | ASHWALL4 cliffs; ASHWALL3 below 96; shore and bank risers NUKEDGE1 | — | SHR, FB FLAT10 at 16; NP NUKAGE1 at 0 (DAMAGE_5); IS RROCK09 at 16 (lit 240) / F_SKY1 | the base family: one continuous valley, one material; its sides read by the jetty, the island, the outfall and the plant wall |
| Plant wall and outfall (north face of the valley, OF) | STONE (grey concrete); SFALL1-4 falls in the outfall opening | SUPPORT3 frame round the outfall mouth | OF NUKAGE3 at -8 (DAMAGE_5) | the plant's own wall: a landmark, and the boundary of the playable map |
| Jetty (JT) | sides METAL | — | FLAT5_4 at 24 | concrete on steel pilings |
| Intake house and exit (IH, JC, exit niche) | STARTAN3; EXITSIGN over the arch; exit niche SW1EXIT in STARTAN2 | SUPPORT3 at the arch and niche | FLOOR4_8 / TLITE6_5, glowing | the first piece of the plant itself, in the brown steel the later maps are built from; the exit marker |

Every doorway between areas is framed (DOORTRAK, SUPPORT2/3 or the key colour), and so is every switch and picture (dock switch, shutter switch, exit niche, IR screens).

## Secrets

| # | Where | Hint | Reward |
|---|---|---|---|
| 1 | Closet SC1 behind the guard hut's west wall. | A SHAWN2 panel offset from its neighbours, with a LITE5 strip beside it: the WAD's secret language, taught in the first room. | green armor, shells |
| 2 | Ledge SL2 cut into the rock above the spur, at 168. | Lit by LITE5 strips, with the chaingun on it, in view as you round the east hairpin. Climb the crate, then the container. | chaingun (the map's only one), a box of bullets |
| 3 | Closet SC3 behind the locker room's west wall. | One locker door offset, with a LITE5 strip beside it. | backpack, a box of shells |
| 4 | The rock island IS in the spill. | It glows (light 240) in plain view from the deck, with the soulsphere on it. Reaching it means wading about 200 units of nukage each way, a few seconds at 5 health per second. | soulsphere |

## Targets

| Target (DOOM II median) | Plan | Where it comes from |
|---|---|---|
| Optional share of area ≥ 0.3 [0.5] | ≈ 0.4 | The spill (about 2.1M units²), far bank (0.34M), island, pump shed, spur and ledge, guard hut and SC1, west corridor, locker room and SC3, and the key closet, against about 6.6M reachable. If the reach model doesn't count damaging floors as reachable, this drops to about 0.1. Then split the shore into a path strip and an optional east shore, and widen the spur and guard-hut areas, until it reads ≥ 0.3. |
| Distinct floor heights ≥ 15 [23] | ≈ 27 | 0 valley/spill; 8 L1 foot and hut; 16-96 (L1); 112-192 (L2); 208-288 (L3, FC); 72 rockfall; 88 spur; 120 crate; 144 container; 168 ledge; 24 jetty/IH/shed; -8 outfall; 296 GR/LK/dock step; 304 ST; 320 IR/dock; 344 console; 336-352 stair hall and deck. Many of these coincide on the 16 grid, so the distinct count is about 27. |
| Secrets ≥ 2 [4] | 4 | above |
| Light-effect sectors ≥ 3 [9] | 6 | porch lamp over the shutter (slow blink), LB alarm strip (slow blink), GR (random blink), IR (flicker), guard hut (flicker), intake house (glow) |
| Deaf share (UV) ≥ 0.2 [0.42] | ≈ 0.45 (14 of 31) | GC and JC closets (5), the GR demon, the dock imps (2), the far-bank imps (3), the locker imp, the E1 zombiemen (2) |
| Most-used wall texture 0.2-0.45 [0.3] | ≈ 0.3, ASHWALL4 | The spill valley's cliffs (about 1.5M of roughly 5.5M units² of wall) less what ASHWALL3 and NUKEDGE1 take near the water. ROCK5 on the climb side should come second at about 0.2-0.25. If ASHWALL4 reads above 0.45, lower the valley's sky ceiling from 512 to 448 (the deck needs 408); below 0.2, use ASHWALL4 on the lower faces too. |
| Rule-2 seams with a border ≥ 0.5 [0.31] | ≥ 0.7 | SUPPORT2 pilasters at both ends of the facade (rock to steel) and the deck wall (steel to scorched rock); SUPPORT2 frames on the front shutter, window, dock door, dock switch and shutter switch; DOORTRAK or DOORBLU jambs at every door; COMPSPAN bays in IR; SUPPORT2 locker frames; SUPPORT3 at the outfall mouth, IH arch and exit niche; LITE5 at all four secret cues. ROCK5 and ASHWALL never share a wall plane. |

Balance targets for the build: monsters 12/22/31 (ratios 0.39/0.71). UV pistol-start ammo ratio 1.8-2.4 and 45-60 health per 1,000 monster HP, both at the generous end, as the WAD's easiest map. That's about 1,860 UV monster HP, against 4 stimpacks and 2 medikits on the route plus the secrets. Heavy-monster share 0. The shotgun within 300 units of the start. No awake monster sees the start; the nearest monster (the E1 zombiemen) is about 1,050 away.

Encounter roles in one place:

| Space | UV / HMP / easy | Roles |
|---|---|---|
| E1 hairpin | 2 zombiemen / 2 / 1 | fodder; the shotgun's first targets |
| L2, W2 | 2 imps, 1 shotgun guy / 1 imp + SG / 1 imp | turrets from above; the shotgun guy is the reason not to dawdle on L1 |
| Spur | 1 imp / 0 / 0 | optional fodder on the container |
| L3 | 2 zombiemen / 1 / 1 | fodder |
| Forecourt edge | 2 imps / 2 / 1 | turrets above L3 |
| Loading yard | 2 imps (dock), 1 shotgun guy / imp + SG / 1 imp | elevated turrets plus a hitscanner at close range; cover is the dock step |
| Storeroom | 1 zombieman / 1 / 0 | fodder among crates |
| Generator room | 1 demon / 1 / 1 | the first demon, in the dark |
| Instrument room | 2 zombiemen / 1 / 1 | turrets behind the consoles |
| Key closet GC | 2 demons, 1 imp / 2 demons / 1 demon | the trap; the ring lets you back off and circle |
| Lobby | 1 shotgun guy, 1 zombieman / 2 / zombieman | seen first through the window |
| Locker room | 1 imp / 1 / 0 | optional fodder |
| Shore below the lift | 2 imps / 1 / 1 | turrets throwing up at the cliff stair |
| Far bank | 3 imps / 2 / 1 | turrets at range, then wading pressure |
| Pump shed | 1 zombieman / 0 / 0 | optional fodder |
| Jetty closet JC | 2 demons / 2 / 1 | meat shields down a 128-wide jetty: the final fight |

## Build risks

- **The reveal must be airtight.** Nothing in the spill valley may be visible from the climb side: no two-sided line between valley A, the yard or the station and valley B except through the blue door. Check in the preview that the yard and the forecourt are closed by one-sided rock, and look from the forecourt in a port. The sky is the only shared thing.
- **Switchback edges.** Each leg borders the next along 1024 units, and only the hairpin ends may differ by ≤ 24 (L1/L2 at x 896..1024, L2/L3 at x 0..256). Every other stretch differs by ≥ 32, as planned, but a stray step height breaks the climb into a staircase you can shortcut. The drops from an upper shelf to a lower one are allowed. Keep step boundaries at the same x on all three legs, so the long edges share vertices (doom-build gotcha).
- **Stairs.** The legs' steps are 16 high and 128 long, the stair hall's 48 deep, F1's 64 deep: all inside the walker's limits. The legs are sectors 128×256; build them with `stairs()` or plain sectors with `lower=` ROCK5.
- **Sound in the open hillside.** Valley A is one open space, so the first shot wakes every shelf, as intended. The yard must not wake with it: put two sound-blocking lines in series between FC/SV and LY (`ML_SOUNDBLOCK`, see `docs/monster-alerting.md`), or the dock imps walk round to the forecourt. The same goes for the far-bank imps: they're deaf, and a shot on the shore wakes them as soon as they have line of sight, which is what the fight wants.
- **Safe start.** The E1 zombiemen are about 1,050 units from the start with open sky between. Face them east (away from the start), and check the build's start-under-fire warning. If it fires, move them north along E1 behind leg 2's face.
- **Long sightlines across the spill.** About 1,000 units from the jetty to the far bank, so only projectile monsters there. The one shore zombieman is at the pump shed, out of the jetty's line.
- **Optional share and the nukage.** The plan counts the spill as optional reachable area (see Targets). Confirm how the build's measure treats a damaging floor before tuning anything else.
- **Doors in tall walls.** The front shutter, the dock door and the blue door each have a sky or a 400+ ceiling on one side, so they need `doorway(..., alcove=, far_alcove=)` recesses 128 high (doom-build gotcha). The forecourt and the deck push out 16-48 units for them. The guard hut's small door uses DOOR3 at 72 high in a hut 128 high, so it needs none.
- **Monsters at doors.** The GC demons have to come through the storeroom's doors to reach you. Use exactly door-width recesses (`doorway()` default), and check in play that they don't freeze at the ST/IR door (doom-build gotcha, `docs/door-stuck.md`). If they do, make GC open straight into IR instead.
- **Lift LF.** The walk-over from the top is wanted (you ride it down). Monsters may ride it too, so the shore imps could come up to the landing, which is fine. The landing's sky ceiling clears the reach check's 56 units.
- **Exit niche.** It's 32 wide, so leave it out of `MUST_REACH` (doom-build gotcha).
- **Island and shore heights.** The shore, bank and island are 16 above the nukage and the jetty 24, so every edge out of the spill is climbable and there's no inescapable pit.
- **Replacing Nukage Junction.** This map takes MAP01's slot. Per the user, `levels/nukage_junction.py` (and its playtest) stays in the repo, just out of the build: README's map list, build commands and SPOILERS' MAP01 section point at this module, and both say Junction is kept but not built (building it would overwrite this map's slot). `next` "MAP02" keeps the chain intact.
- **Sector count.** About 70-90, small for the set and right for a MAP01.

## As built

`levels/nukage_outskirts.py` is authoritative for coordinates. These are the departures from the plan above, each for a reason found in the build:

- **The station** was rebuilt for room after the first playtest, because the rooms of the plan (about 240 across, a 128-wide west corridor, a lobby 176 deep) were cramped. It's now two rows of rooms behind the facade, 16-unit walls between them, every door 128 wide:
  - **South row:** the lobby, 800×368 (the old west corridor folded into it), and the generator room, 304×384.
  - **North row:** the locker room 240×384, the stair hall 256 wide, the instrument room 304×384 and the storeroom 272×384.

  The station is 1,120 wide (x 400-1520), and the rooms end at y 2240, so everything over the ridge moved 320 north of the plan's coordinates and the deck starts at y 2256. The forecourt widened east to x 1792, so the service ledge (x 1552-1792) runs up the station's east side to a yard 496×576 and a dock 160 wide.
- **Station heights.** Every floor in the station is 288 and every ceiling 416, so the 128-high door pictures fill the wall above each door exactly. An earlier build gave the rooms floors of 280-312 for the floor-height count. That made each doorway a dip of 8-24 that did nothing for play, so it's gone. The console and pedestal are raised (328, 312), and the stair hall still rises 304-352 in four 48-deep steps, to a landing at 352 under a 480 ceiling. The loading yard is 256, the step 272 and the dock 288, level with the dock door.
- **Walls between rooms.** The front shutter sits in a recess (the porch, a blinking red canopy) with the window beside it, both cut into a 48-deep facade, and the lobby's red alarm strip runs along the inside of that wall. The window, the stair arch and the blue door are in one line (x 712-848), so the forecourt shows the blue door. The facade is plain SHAWN2: the SHAWN1 logo over the shutter wasn't used, because the wall above the porch is 224 high and the 128-high logo would tile into a cut-off second copy.
- **Storeroom.** One 64×64 crate stack in the middle, with lanes of 104 east and west and 160 north and south. The first layout's lanes were 32-48, narrower than a demon (60), which left the key-trap demons shut in half the room. The closet is 160 deep, so its imp clears the two demons.
- **Generator room.** It's 144, not 96, and its two door sectors are 48. A random blink drops to the darkest neighbour's light, and at 96 every neighbour was brighter, so it never blinked. Now it flashes between 144 and 48, and the demon in it is visible half the time.
- **The rockfall** is a heap climbing in 24s (24, 48, 72) with shells on top. As a 72-high block it was an outdoor floor you could see from every shelf and never reach (Romero's rule 5).
- **Service ledge** is two sectors (288, then 272 down to the yard), so the forecourt and the yard are separated by two sound-blocking lines in series.
- **Spur.** The crate, the container and the ledge are 112, 136 and 160: steps of 24, the most the player can climb (the plan's 120/144/168 had 32 for the first step). The crate's sides are METAL, a border texture, because CRATE1 beside the container's SHAWN2 was a rule-2 seam.
- **The deck's rail** is a kerb 16 high whose outer edge is impassable, not MIDBARS3. In ViZDoom the 72-high bars filled the view at eye height. The spill's sky is 288 (the shore's and the deck's 448), so from the deck you look out over the plant wall and the intake house, down at the nukage. With the spill's sky at 512, the plant wall filled the view as a dark band and the intake house rose like two towers.
- **EXIT sign over the arch.** The end of the jetty has a sky at 152, so the wall over the arch is 16 high and carries EXITSIGN, between SUPPORT3 pieces. Vanilla skips the wall between two sky ceilings, so from outside it still reads as open sky.
- **The jetty and the intake house split the spill and the far bank** into west and east halves; the island is in the east half. The intake-house closet is behind its north wall (the plant wall), not its west wall, which would have run into the far bank.
- **The cliff landing** is FLAT23, like the lift top, so the lift isn't a rule-1 slip.
- **Monsters** face away from the start, so the climb side doesn't see you until the first shot. Only the yard, station closets, the generator room's demon, the locker imp and the far bank are deaf (deaf share 0.39).
- **Measured** (build table, DOOM II median in brackets): optional share 0.47 [0.5], 32 floor heights [23], 4 secrets [4], 7 light-effect sectors [9], deaf share 0.39 [0.42], most-used wall texture 0.33 ROCK5 [0.3], rule-2 seams with a border 0.99 [0.31], symmetry 0.57 [0.54], monsters 12/22/31 (0.39/0.71), nearest monster 643. Every target is met. The most-used texture is ROCK5 (the climb side), not ASHWALL4 as planned. Lowering the spill's sky took wall area from the ash cliffs, and 0.33 is inside id's range. Rule-1 slips are 7% of flat changes (id's median 3%), all door thresholds: each door sits level with two rooms whose floors are different flats, so one side of it changes flat without a height change.
- **Balance** sits above the plan, deliberately, for the set's first map. UV ammo is 2.66× monster HP (plan 1.8-2.4; id's IQR tops out at 2.73), after cutting the first build's 5.6× down to four shell pickups, the clips and the shotgun. Health is 83 per 1000 HP (plan 45-60); the secret soulsphere is 100 of the 155. The route curve never runs short (lowest detour ratio 1.99).
- **Playtest** (`levels/playtests/nukage_outskirts.playtest`, UV). The wiring run checks:
  - all 4 secrets, the shells on the rubble heap, the shotgun, chaingun, blue key and soulsphere;
  - each door and switch, the lift both ways, both closets, and the exit.

  23 checks, 0 fails. Screenshots confirm the reveal (the spill, the island with the soulsphere, the jetty, and the EXIT sign over the intake-house arch) and that the forecourt shows nothing over the ridge. Static balance has no warnings. The lowest detour ratio is 1.99, on the last leg (blue key to exit), and nothing runs short on the thorough curve.
- **Fight runs** (seeds 1-3, the rebuilt station): kills 31, 28 and 31; deaths 10, 10 and 1. The deaths are the bot's:
  - **Seeds 1 and 2** reach the shore with no ammo: 3 and 7 starved deaths, plus hazard deaths punching imps in the nukage by the lift and wading to the island. The footage shows it pinned in the nukage's west corner, fists out, which the runner skips as a loop. The curve leaves a normal player 1,610 ammo damage at the exit. The bot fires about twice the monsters' HP: around 120 bullets and 32 shells in seed 1, against 1,860 HP.
  - **Seed 2** also starves in the locker room, after spending 16 shells in the valley.
  - **Seed 1** has a combat death in the instrument room, to the closet demons.
  - **Seed 3** has one combat death on the shore.

  Before the station was rebuilt (with the crate fix already in), the same seeds died 0, 1 and 2 times, with the bot ending seeds 2 and 3 nearly dry. The rebuilt layout changes the bot's path, so the seeds play differently, and it now runs dry before the shore rather than after it. A human should judge the ammo in dsda-doom. If it's tight, a box of shells at the cliff landing is the place for more (it would take the ammo ratio to about 2.8, just above id's IQR).

## Concepts considered

1. **Over the Ridge (chosen).** Switchbacks up a hill to the monitoring station on its crest. The deck on its far side reveals the spill filling the next valley.
2. **End of the Line.** A dead commuter halt, the station building (with the signal box as its maze), a dark tunnel, and a trestle high over the pool.
3. **Upstream.** Follow a nukage trickle up a ravine as it widens, through an intake station, to the weir and the pool behind the dam.
4. **The Checkpoint.** A security wall across the valley, with the station built into it and the containment pool on the far side.
5. **Substation.** A see-through fenced maze of transformer bays; a power cut blacks it out, and a cable trench leads to the shore.

The user chose Over the Ridge from all five. It wins because:

- it's the only one whose reveal comes from the terrain, so the spill is a real surprise;
- the climb gives the height targets for free and keeps changing the view, which answers "short but not drab";
- its mechanisms are cheap: stairs, two doors, a switch, one lift, two closets.

The others lose on these grounds:

- End of the Line is a straight line with little optional space.
- Upstream repeats MAP09's outfall and dam and MAP05's reservoir.
- The Checkpoint repeats MAP08's far-side shutters and puts hitscanner towers in the open.
- Substation echoes MAP07's maze and has the weakest reveal.
