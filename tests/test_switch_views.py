"""Is what a switch moves seen or heard from where it's used
(progression_metrics.switch_views, levels/measure.py switch_report)."""
import os
import sys

from conftest import ROOT, module, needs_iwad

from levels import checks
from levels.doom2 import PLAYER1, S1_DOOR_OPEN, W1_EXIT
from levels.mapgen import compile_level
from levels.measure import switch_report
from levels.model import Sector, Special, Thing, door, load, rect, switch_niche

pytestmark = needs_iwad("doom2")
sys.path.insert(0, os.path.join(ROOT, "scripts", "metrics"))
import progression_metrics as pm  # noqa: E402

WALL, F, C = "STARTAN3", "FLOOR4_8", "CEIL3_5"


def room(name, box):
    return Sector(name, [rect(*box)], 0, 128, F, C, 160, WALL)


def views(sectors, booth_at, facing, depth, exit_line):
    """The switch views and report of a map: the start in `hall`, a switch
    booth opening door d_exit (tag 1) on the way to the exit."""
    booth, walls = switch_niche("booth", booth_at, facing, Special(S1_DOOR_OPEN, 1, "SW1COMP"), floor=0, flat=F,
                                wall=WALL, ctex=C, light=160, depth=depth)
    level = load(module(SECTORS=[*sectors, booth], SPECIAL_WALLS=walls, FREE_LINES={exit_line: Special(W1_EXIT)},
                        THINGS=[Thing(PLAYER1, 64, 256)]))
    m, md, res = checks.findings(level, compile_level(level)).reach
    vs = pm.analyse(md, res)[1]["switches"]
    return vs, switch_report(md, vs, list(level.sectors))[1]


def test_a_switch_in_a_booth_counts_as_seen_from_where_the_player_stands_outside_it():
    # The booth is 48 deep in the hall's north wall: from inside it the door,
    # far along the east wall, is behind the booth's sides; from the hall it isn't.
    (v,), warnings = views([room("hall", (0, 0, 1024, 512)), door("d_exit", rect(1024, 192, 1040, 320), tag=1),
                            room("exit", (1040, 0, 1552, 512))],
                           (256, 512), "n", 48, ((1300, 128), (1300, 384)))
    assert v["required"] and v["visible"]
    assert v["eye"][1] < 512   # standing in the hall, not the booth
    assert warnings == []


def test_a_required_switch_moving_something_unseen_and_out_of_earshot_is_warned_about():
    # The door is round two bends, about 2,900 away by vanilla's sound distance.
    (v,), warnings = views([room("hall", (0, 0, 512, 512)), room("north", (448, 512, 512, 2048)),
                            room("east", (512, 1984, 2048, 2048)), door("d_exit", rect(2048, 1984, 2064, 2048), tag=1),
                            room("exit", (2064, 1792, 2576, 2304))],
                           (256, 0), "s", 16, ((2320, 1900), (2320, 2200)))
    assert v["required"] and not v["visible"] and not v["heard"] and v["dist"] > pm.SOUND_RANGE
    assert len(warnings) == 1 and "d_exit" in warnings[0]
