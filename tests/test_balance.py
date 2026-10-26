"""The resource curve and exposure checks along the route (levels/balance.py)."""
import os
import sys

from conftest import ROOT, module, needs_iwad

from levels import checks
from levels.balance import route_balance
from levels.doom2 import IMP, PLAYER1, SHELLBOX, SHOTGUN, W1_EXIT
from levels.mapgen import compile_level
from levels.model import Sector, Special, Thing, load, rect

pytestmark = needs_iwad("doom2")
sys.path.insert(0, os.path.join(ROOT, "scripts", "metrics"))
import progression_metrics as pm  # noqa: E402

WALL, F, C = "STARTAN3", "FLOOR4_8", "CEIL3_5"


def corridor_map(*things):
    """West room (start) -> a corridor east -> the exit room. A small room
    opens off the corridor's middle; a long dead end leads north to a far room."""
    def room(name, pts):
        return Sector(name, [pts], 0, 128, F, C, 160, WALL)
    return module(
        SECTORS=[room("west", rect(0, 0, 512, 512)),
                 room("hall1", rect(512, 192, 1024, 320)),
                 room("hall2", [(1024, 192), (1280, 192), (1280, 320), (1024, 320)]),
                 room("hall3", [(1280, 192), (3072, 192), (3072, 320), (2176, 320), (2048, 320), (1280, 320)]),
                 room("near", rect(1024, 320, 1280, 576)),
                 room("deadend", rect(2048, 320, 2176, 1600)),
                 room("far", [(1920, 1600), (2048, 1600), (2176, 1600), (2304, 1600), (2304, 1900), (1920, 1900)]),
                 room("east", rect(3072, 0, 3584, 512))],
        FREE_LINES={((3328, 128), (3328, 384)): Special(W1_EXIT)},
        THINGS=[Thing(PLAYER1, 64, 256), Thing(SHOTGUN, 256, 256), Thing(SHELLBOX, 1152, 448),
                Thing(SHELLBOX, 2112, 1750), *things])


def balance(mod):
    level = load(mod)
    m, md, res = checks.findings(level, compile_level(level)).reach
    return route_balance(m, md, res, pm.analyse(md, res)[1]["legs"], names=list(level.sectors))


def test_an_item_off_the_route_counts_only_within_the_detour():
    bal = balance(corridor_map())
    (leg,) = bal.legs
    assert leg.label == "exit" and leg.site == "east"
    pistol, shotgun, box = 500, 8 * 70, 20 * 70
    assert leg.thorough[1] == float("inf")          # nothing to fight: no ratio
    assert leg.thorough[0] == pistol + shotgun + 2 * box   # every reachable item
    assert leg.detour[0] == pistol + shotgun + box         # the near room's box, not the far one


def test_a_monster_facing_the_start_puts_it_under_fire():
    assert balance(corridor_map(Thing(IMP, 900, 256, 180))).start_fire == [(IMP, 900, 256)]
    assert balance(corridor_map(Thing(IMP, 900, 256, 0))).start_fire == []


def test_an_engaged_monster_is_paid_for_from_the_ammo_carried():
    (leg,) = balance(corridor_map(Thing(IMP, 900, 256, 0))).legs
    assert leg.engaged_hp == 60
    assert leg.detour[0] == 500 + 8 * 70 + 20 * 70 - 60
