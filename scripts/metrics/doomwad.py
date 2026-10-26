"""The vanilla maps in the DOOM / DOOM II IWADs, and the lookup tables the
research scripts use, in their shapes. The map dataclasses and parser live in
levels/wadmap.py and the thing and line-action tables in levels/doom2.py;
this module re-exports both.

Run from the repo root:
    python3 scripts/metrics/doomwad.py           # one summary line per map
Use from another script in scripts/metrics/:
    from doomwad import load_all, IWADS
    for m in load_all(): ...

IWAD paths come from DOOM_WAD (Ultimate Doom) and DOOM2_WAD in the repo's
.env or the environment (see .env.example); use the v1.9 IWADs.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from levels.doom2 import (ACTORS, AMMO_PICKUPS, ARMOR_PICKUPS, BARREL, DAMAGE_PER_AMMO, DROPS,  # noqa: E402,F401
                          HEALTH_PICKUPS, HITSCANNERS, KEY_OF, LABELS, LIGHT_SPECIALS, LINE_SPECIALS,
                          MAX_STEP, PLAYER1, PLAYERS, SECRET_AREA, SECTOR_DAMAGE, TELEPORT_DEST, LineSpecial)
from levels.doom2 import POWERUPS as POWERUP_TYPES, WEAPONS as WEAPON_TYPES  # noqa: E402
from levels.model import SKY  # noqa: E402,F401
from levels.wad import IWAD_VARS, IWADS  # noqa: E402,F401
from levels.wadmap import (AMBUSH, EASY, HARD, MEDIUM, ML_BLOCKING, ML_BLOCKMONSTERS,  # noqa: E402,F401
                           ML_DONTDRAW, ML_DONTPEGBOTTOM, ML_DONTPEGTOP, ML_MAPPED, ML_SECRET,
                           ML_SOUNDBLOCK, ML_TWOSIDED, MULTI_ONLY, SKILLS, Line, Map, Sector, Side, Thing,
                           load_maps, parse)

# type: (name, health); the boss brain included for completeness.
MONSTERS = {t: (LABELS[t], a.health) for t, a in ACTORS.items() if t not in PLAYERS}
WEAPONS = {t: LABELS[t] for t in WEAPON_TYPES}
POWERUPS = {t: LABELS[t] for t in POWERUP_TYPES}
AMMO, HEALTH, ARMOR, KEYS = AMMO_PICKUPS, HEALTH_PICKUPS, ARMOR_PICKUPS, KEY_OF
PLAYER_STARTS = PLAYERS
SECRET_SPECIAL = SECRET_AREA
DAMAGE_SPECIALS = SECTOR_DAMAGE   # special: damage per 32 tics


def load_all():
    return load_maps("doom") + load_maps("doom2")


def summary(m):
    hard = m.things_on(HARD)
    mons = [t for t in hard if t.type in MONSTERS]
    secrets = sum(1 for s in m.sectors if s.special == SECRET_SPECIAL)
    x0, y0, x1, y1 = m.bbox
    return (f"{m.slot:6} sectors={len(m.sectors):4} lines={len(m.lines):5} area={sum(m.sector_areas) / 1e6:6.2f}M "
            f"bbox={x1 - x0}x{y1 - y0} uv_monsters={len(mons):3} "
            f"uv_hp={sum(MONSTERS[t.type][1] for t in mons):6} secrets={secrets}")


if __name__ == "__main__":
    for m in load_all():
        print(summary(m))
