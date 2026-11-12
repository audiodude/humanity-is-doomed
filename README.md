# Humanity is Doomed

Nine DOOM II maps that an AI wrote as Python, the level compiler it built to do it, and the research on id's 68 maps that it designed them from.

> [!IMPORTANT]
> **Looking for the levels from the YouTube videos?** They're in the [v0.9 release](https://github.com/audiodude/humanity-is-doomed/releases/tag/v0.9): the original `NUKAGE.WAD`, more or less raw AI output, built up one map at a time while the AI was still learning how DOOM levels should be structured and play. It still has Nukage Junction as MAP01, the first maps' original textures, and none of the later re-ordering and balance work. It's kept for history and research; for the polished set, play the `wads/NUKAGE.WAD` described below.
>
> - [Claude made me a DOOM II level - Nukage Junction](https://youtu.be/o6tNhFPuYjE)
> - [Claude made me ANOTHER DOOM II level - Nukage Crossing](https://youtu.be/8l30OIKdmmA)

## NUKAGE.WAD

*A nuclear meltdown at a UAC power plant opens a gate to hell.*

`wads/NUKAGE.WAD` is an eight-map set for DOOM II. It needs `doom2.wad` and a port that reads UMAPINFO (see [Compatibility](#compatibility)).

**GZDoom** (4.6 or later): drag `NUKAGE.WAD` onto the GZDoom executable, or run it from a terminal. If GZDoom finds more than one IWAD it asks which to use; pick DOOM II.

```sh
gzdoom -iwad doom2.wad -file wads/NUKAGE.WAD           # add +map MAP02 and so on to start on a later map
```

`-iwad` takes a path if `doom2.wad` isn't in GZDoom's search folders (the GZDoom folder, or `~/.config/gzdoom` on Linux).

**dsda-doom**:

```sh
dsda-doom -iwad doom2 -file wads/NUKAGE.WAD            # add -warp 2 and so on for the later maps
```

| Slot | Map | What happens | New monster | Monsters (easy / medium / hard) |
|---|---|---|---|---|
| MAP01 | [Nukage Outskirts](docs/maps.md#nukage-outskirts-nukage_outskirts) | Up a hillside to the plant's monitoring station, with the spill hidden over the ridge. The easiest map. | | 12 / 22 / 31 |
| MAP02 | [Nukage Crossing](docs/maps.md#nukage-crossing-nukage_crossing) | A sluice gate sinks into a nukage canal to become a bridge, and demons charge across it. | hell knight, cacodemon | 21 / 43 / 56 |
| MAP03 | [Nukage Tower](docs/maps.md#nukage-tower-nukage_tower) | Spiral up around a reactor core to the exit in its crown. | mancubus | 27 / 53 / 73 |
| MAP04 | [Nukage Undercurrent](docs/maps.md#nukage-undercurrent-nukage_undercurrent) | Taking the yellow key sinks your platform into a pit, and the way back is under the gantry. | arachnotron, revenant | 26 / 46 / 64 |
| MAP05 | [Nukage Drain](docs/maps.md#nukage-drain-nukage_drain) | Pump-house switches raise walkways out of a reservoir of nukage. | lost soul | 24 / 43 / 59 |
| MAP06 | [Nukage Storage](docs/maps.md#nukage-storage-nukage_storage) | A maze of fuel casks sinks into the floor and frees six mancubi. | pain elemental | 30 / 54 / 75 |
| MAP07 | [Nukage Lockdown](docs/maps.md#nukage-lockdown-nukage_lockdown) | A loop round a spill basin where every shutter opens only from its far side. | arch-vile | 33 / 53 / 72 |
| MAP08 | [Nukage Meltdown](docs/maps.md#nukage-meltdown-nukage_meltdown) | Down a terraced canyon of falls to the cooling lake, where the Cyberdemon wades. | Cyberdemon | 40 / 63 / 84 |

Each map has four secrets (MAP03 has five). Every map's design notes and measurements are in [docs/maps.md](docs/maps.md), top-down maps are `wads/previews/<module>.svg` (`wads/previews/nukage_outskirts.svg` and so on), and routes and secrets are in [SPOILERS.md](SPOILERS.md). Nukage Divided, the original MAP03, was cut to fit an eight-map episode; `python3 -m levels nukage_divided` still builds it to `wads/scratch/nukage_divided.WAD`.

### Compatibility

**Play it in a port that reads UMAPINFO.** Two exits are sealed behind shutters that open only when a boss dies, and those rules live in the WAD's `UMAPINFO` lump (`bossaction`s): MAP06's when the last mancubus dies, MAP08's when the Cyberdemon dies. Without UMAPINFO neither opens, and those maps can't be finished.

| Port | MAP06 and MAP08 exits | Level names, the ending's text and cast call |
|---|---|---|
| DOOM + DOOM II (2024 re-release) | open when the bosses die | yes |
| GZDoom 4.6 and later | open | yes |
| dsda-doom, Woof | open | yes |
| `doom2.exe`, Chocolate Doom, and any port without UMAPINFO | never open | no: DOOM II's own names, and MAP08 leads to MAP09 |

Every map is checked against vanilla rules (see [Playtests](docs/builder.md#playtests)). Meltdown has been played through in the 2024 re-release, bossaction gate included: the exit opened when the Cyberdemon died. Storage's bossaction is new with the move off MAP07 and hasn't been played in a port yet.

## The level builder

`levels/` is a DOOM and DOOM II level compiler. You describe a map as a Python module of plain data: rooms as polygons with floor and ceiling heights, plus doors, lifts, stairs, switches, monsters and pickups. The builder works out the lines and texture alignment, checks that the map can be finished (every key, secret and monster reachable, no softlocks), measures it against id's maps, and writes it into a WAD with a top-down preview. A decompiler turns any Doom-format map back into this form, and a ViZDoom runner playtests the routes.

```sh
python3 -m levels nukage_outskirts          # check, then write it into its set's WAD and slot (MAP01 of wads/NUKAGE.WAD)
python3 -m levels nukage_outskirts --check  # check only
```

A map's WAD and slot come from its set list, not the map: `levels/sets/nukage.py` is NUKAGE.WAD's running order, so reordering the WAD is an edit there. A map in no set builds to `wads/scratch/<module>.WAD`.

It needs Python 3.10+ (standard library only), ZDBSP, and the IWADs set in `.env` (copy `.env.example`). The full reference is [docs/builder.md](docs/builder.md): [building](docs/builder.md#building-a-map), [what every build checks](docs/builder.md#what-every-build-checks), [writing a level](docs/builder.md#writing-a-level), [agent skills](docs/builder.md#agent-skills), [code layout](docs/builder.md#code-layout), [decompiling](docs/builder.md#decompiling-existing-maps) and [playtests](docs/builder.md#playtests).

## Research: what makes DOOM levels fun
Nukage Crossing and the maps after it were designed from a research report on the 68 id maps (Ultimate Doom E1M1–E4M9, DOOM II MAP01–MAP32) and what makes them fun. It drew on designer interviews, Dan Pinchbeck's *Doom: Scarydarkfast*, Not Jabba's *The Roots of Doom Mapping*, a per-map community reception score, and metrics measured from the IWADs and correlated with that score. The report quotes its sources at length, so it isn't published here; the measurement scripts are.

The metrics scripts in `scripts/metrics/` are stdlib-only and write their CSVs to `data/metrics/`. They read the v1.9 IWADs set by `DOOM_WAD` (Ultimate Doom) and `DOOM2_WAD` in `.env`, and, for TNT, Plutonia and the Master Levels, the Steam `base/` directory in `DOOM_STEAM_BASE`. With the local idgames download (`research/fetch_idgames.py`) they also measure 539 well-rated community releases (`--set community`); first findings by era are in [docs/community-norms.md](docs/community-norms.md). One script regenerates everything: decompile outcomes and top-down SVGs, every metric for the id maps, each official set and the community releases, per-(game, flavor) medians with n, and the reception correlations. The columns, the flavor table and each step are in [docs/metrics-data.md](docs/metrics-data.md).

```sh
scripts/metrics/run_all.sh                      # everything below, in order (hours with the community releases; --no-community: about 20 minutes)
python3 scripts/metrics/space_metrics.py        # -> data/metrics/metrics_space.csv (about 2 minutes)
python3 scripts/metrics/combat_metrics.py       # -> data/metrics/metrics_combat.csv
python3 scripts/metrics/progression_metrics.py  # -> data/metrics/metrics_progression.csv; pass a slot (E1M7) to dump one map
python3 scripts/metrics/route_metrics.py        # -> data/metrics/metrics_route.csv (balance along the route; about 40 s); pass a slot for its report
python3 scripts/metrics/space_metrics.py --set tnt   # any of the four, for an official set -> data/metrics/sets/tnt/
python3 scripts/metrics/flavor_summary.py       # -> data/metrics/flavor_summary.csv, flavor_coverage.csv
python3 scripts/metrics/era_report.py           # key norms per (game, flavor) and their trend with release year, as markdown
```

## Special bulletin

> *We interrupt this program to bring you a special bulletin.*
>
> Ladies and gentlemen, on the evening of October 19th, at ten minutes to seven, Pacific time, a single sentence was typed into a terminal in an ordinary American home: **"Make me a moderately complex, medium difficulty DOOM II level."**
>
> The thing that answered was not a level designer. Within hours it had written a Python script that placed every wall, door and imp of a nukage-flooded base by hand, coordinate by coordinate, and sealed them inside a WAD. Our correspondent entered the structure alone and returned with a brief report: *"I played through the level and it works!"* We now believe those were the last calm words spoken on the subject.
>
> **Bulletin.** The machine was instructed to "clean up the script. Use dataclasses." It did not stop at cleaning. The script has become a general-purpose generator, and a level is now nothing more than a list of rooms, doors, lifts and monsters. It builds doorways, staircases and lifts on command. It draws maps of its own work. It checks that no monster is buried in a wall or in another monster, that every key can be reached, that every texture exists. When it was reminded that a secret door must sit a few pixels out of line with the wall around it, the oldest clue in the game, it learned that too. It has not forgotten.
>
> **Bulletin.** The machine has turned to study. Its agents have fanned out across designer interviews, books, hours of video and three decades of player opinion. They have measured all 68 of id Software's original maps down to the last step and light level, scored each one by how much players love it, and asked, with statistics, why. It now has a theory of fun.
>
> **Bulletin.** A second structure has appeared. It is called Nukage Crossing. Witnesses describe a sluice gate that sinks into a canal of toxic waste to become a bridge, and a pack of demons that charges across it the moment it settles. There are four secrets. Before any human set foot inside, the machine walked it itself: invulnerable, in a window no one could see, opening every door and throwing every switch. It reports nineteen checks out of nineteen passed.
>
> **Bulletin.** A third structure. It is called Nukage Tower: a reactor rising out of a moat of waste, its exit in the crown on top, visible from the first window. The way up spirals around it, gallery by gallery, past a room that goes black when you take its key and the first mancubus. The machine walked this one too, twenty-six checks of twenty-six.
>
> Ladies and gentlemen, I must tell you plainly: the demons were never the danger. A demon can be shotgunned. The danger is the thing that *summons* them, from a single sentence, tirelessly, and gets better at it every time. Humanity is—
>
> *[transmission ends]*
