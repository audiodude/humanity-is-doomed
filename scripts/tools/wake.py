"""Which monsters one shot wakes: fire from a spot in ViZDoom, wait, and list
the monsters that moved.

    uv run --with vizdoom scripts/tools/wake.py LEVEL [X,Y ...] [--skill 4] [--seconds 10]
    uv run --with vizdoom scripts/tools/wake.py WAD MAP [X,Y ...]

LEVEL is a level module (its set's WAD and slot, as in playtest.py). Each
spot is tested from a fresh start of the map: the player is warped there in
god mode, fires a pistol shot, and stands still for --seconds; any monster
that moved more than 8 units is counted as woken. With no spot, it fires
from the player start. Runs under ZDoom's strict Doom compatibility, so
sound floods and stops the vanilla way (docs/monster-alerting.md).

A monster that woke but can't move (boxed in, or a turret on a ledge with
nowhere to go) isn't counted, and one that wanders in from asleep-but-close
is; read the list, not just the count.
"""
import argparse
import math
import os
import re
import sys
from importlib.util import find_spec

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playtest import CACHE, DEFAULT_IWAD, ROOT, VANILLA_ARGS, place  # noqa: E402

MONSTERS = {"Zombieman", "ShotgunGuy", "ChaingunGuy", "WolfensteinSS", "DoomImp", "Demon", "Spectre", "LostSoul",
            "Cacodemon", "HellKnight", "BaronOfHell", "Arachnotron", "PainElemental", "Revenant", "Fatso",
            "Archvile", "Cyberdemon", "SpiderMastermind"}


def woken(vzd, args, spot):
    """(moved, total): the monsters that moved after a shot from spot (None: the start)."""
    g = vzd.DoomGame()
    g.set_doom_game_path(args.iwad)
    g.set_doom_scenario_path(args.wad)
    os.makedirs(CACHE, exist_ok=True)
    g.set_doom_config_path(os.path.join(CACHE, "vizdoom.ini"))   # not the working directory
    g.set_doom_map(args.map)
    g.set_doom_skill(args.skill)
    g.set_window_visible(False)
    g.set_mode(vzd.Mode.PLAYER)
    g.set_objects_info_enabled(True)
    g.set_render_hud(False)
    g.set_available_buttons([vzd.Button.ATTACK])
    g.add_game_args("+sv_cheats 1 " + VANILLA_ARGS)
    g.init()
    g.new_episode()
    g.send_game_command("god")
    if spot:
        g.send_game_command(f"warp {spot[0]} {spot[1]}")
    for _ in range(3):
        g.make_action([0])

    def monsters():
        return {o.id: (o.name, o.position_x, o.position_y) for o in g.get_state().objects if o.name in MONSTERS}

    before = monsters()
    for _ in range(20):
        g.make_action([1])
    for _ in range(int(args.seconds * 35)):
        g.make_action([0])
    after = monsters()
    g.close()
    moved = sorted(before[i] for i in before if i in after and math.dist(before[i][1:], after[i][1:]) > 8)
    return moved, len(before)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("target", nargs="+", help="LEVEL, or WAD MAP, then any spots as X,Y")
    p.add_argument("--iwad", default=DEFAULT_IWAD, help="DOOM II IWAD (default: DOOM2_WAD from .env)")
    p.add_argument("--skill", type=int, default=4, help="1 ITYTD .. 4 UV, 5 NM (default 4)")
    p.add_argument("--seconds", type=float, default=10, help="how long to wait after the shot (default 10)")
    args, extra = p.parse_known_args()   # spots like -672,1400 look like options to argparse
    if bad := [e for e in extra if not re.fullmatch(r"-?[\d.]+,-?[\d.]+", e)]:
        p.error(f"unrecognized arguments: {' '.join(bad)}")
    if not args.iwad:
        p.error("no IWAD: set DOOM2_WAD in .env (see .env.example) or pass --iwad")
    pos = args.target + extra
    if re.fullmatch(r"[\w.]+", pos[0]) and not pos[0].lower().endswith(".wad") and find_spec(f"levels.{pos[0]}"):
        at = place(pos[0])
        pos = [os.path.join(ROOT, "wads", at.wad), at.slot, *pos[1:]]
    if len(pos) < 2:
        p.error("give LEVEL or WAD MAP")
    args.wad, args.map = pos[0], pos[1].upper()
    try:
        spots = [tuple(float(v) for v in s.split(",")) for s in pos[2:]] or [None]
    except ValueError:
        p.error("spots are X,Y")
    import vizdoom as vzd
    for spot in spots:
        moved, total = woken(vzd, args, spot)
        where = f"({spot[0]:.0f}, {spot[1]:.0f})" if spot else "the start"
        print(f"shot from {where}: {len(moved)} of {total} monsters moved in {args.seconds:g} s")
        for name, x, y in moved:
            print(f"  {name:14} from ({x:.0f}, {y:.0f})")


if __name__ == "__main__":
    main()
