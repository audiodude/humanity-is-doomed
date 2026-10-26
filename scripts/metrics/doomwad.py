"""Read the vanilla maps in the DOOM / DOOM II IWADs into plain dataclasses,
with lookup tables for things, line specials and sector specials.

Run from the repo root:
    python3 scripts/metrics/doomwad.py           # one summary line per map
Use from another script in scripts/metrics/:
    from doomwad import load_all, IWADS
    for m in load_all(): ...

IWAD paths come from DOOM_WAD (Ultimate Doom) and DOOM2_WAD in the repo's
.env or the environment (see .env.example); use the v1.9 IWADs.
"""
import math
import os
import struct
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from levels.wad import IWAD_VARS, IWADS, read_wad  # noqa: E402

# ----------------------------------------------------------------- things ---
# Thing flags. Skill bits: EASY = ITYTD + HNTR, MEDIUM = HMP, HARD = UV + NM.
EASY, MEDIUM, HARD, AMBUSH, MULTI_ONLY = 1, 2, 4, 8, 16
SKILLS = {"easy": EASY, "medium": MEDIUM, "hard": HARD}

# type: (name, health). Spawners/brain included for completeness.
MONSTERS = {
    3004: ("zombieman", 20), 9: ("shotgunguy", 30), 65: ("chaingunner", 70), 84: ("wolfss", 50),
    3001: ("imp", 60), 3002: ("demon", 150), 58: ("spectre", 150), 3006: ("lostsoul", 100),
    3005: ("cacodemon", 400), 69: ("hellknight", 500), 3003: ("baron", 1000),
    68: ("arachnotron", 500), 71: ("painelemental", 400), 66: ("revenant", 300),
    67: ("mancubus", 600), 64: ("archvile", 700), 7: ("spidermastermind", 3000),
    16: ("cyberdemon", 4000), 72: ("keen", 100), 88: ("bossbrain", 250),
}
HITSCANNERS = {3004, 9, 65, 84, 7}
WEAPONS = {2005: "chainsaw", 2001: "shotgun", 82: "supershotgun", 2002: "chaingun",
           2003: "rocketlauncher", 2004: "plasmarifle", 2006: "bfg9000"}
# Ammo a pickup gives (single player, HNTR..UV; ITYTD and NM double it).
AMMO = {
    2007: {"bullets": 10}, 2048: {"bullets": 50}, 2008: {"shells": 4}, 2049: {"shells": 20},
    2010: {"rockets": 1}, 2046: {"rockets": 5}, 2047: {"cells": 20}, 17: {"cells": 100},
    8: {"bullets": 10, "shells": 4, "rockets": 1, "cells": 20},
    2001: {"shells": 8}, 82: {"shells": 8}, 2002: {"bullets": 20}, 2003: {"rockets": 2},
    2004: {"cells": 40}, 2006: {"cells": 40},
}
DROPS = {3004: {"bullets": 5}, 84: {"bullets": 5}, 9: {"shells": 4}, 65: {"bullets": 10}}
# Rough average damage per unit of ammo on a hit (matches levels/doom2.py).
DAMAGE_PER_AMMO = {"bullets": 10, "shells": 70, "rockets": 150, "cells": 22}
HEALTH = {2014: 1, 2011: 10, 2012: 25, 2013: 100, 83: 200}
ARMOR = {2015: 1, 2018: 100, 2019: 200, 83: 200}
POWERUPS = {2022: "invulnerability", 2023: "berserk", 2024: "invisibility", 2025: "radsuit",
            2026: "computermap", 2045: "lightamp", 2013: "soulsphere", 83: "megasphere", 8: "backpack"}
KEYS = {5: "blue", 40: "blue", 6: "yellow", 39: "yellow", 13: "red", 38: "red"}
PLAYER_STARTS = {1, 2, 3, 4}
TELEPORT_DEST = 14
BARREL = 2035

# ------------------------------------------------------------ line specials ---
# type: (trigger, kind, key). Trigger: D (use door), S1/SR (switch), W1/WR
# (walk), G1/GR (gun), or "" for passive (scrollers). Kinds group behaviour.
_LS = """
1 D door; 2 W1 door; 3 W1 door_close; 4 W1 door; 5 W1 floor_raise; 6 W1 crusher; 7 S1 stairs;
8 W1 stairs; 9 S1 donut; 10 W1 lift; 11 S1 exit; 12 W1 light; 13 W1 light; 14 S1 floor_raise;
15 S1 floor_raise; 16 W1 door_close; 17 W1 light; 18 S1 floor_raise; 19 W1 floor_lower;
20 S1 floor_raise; 21 S1 lift; 22 W1 floor_raise; 23 S1 floor_lower; 24 G1 floor_raise;
25 W1 crusher; 26 D door blue; 27 D door yellow; 28 D door red; 29 S1 door; 30 W1 floor_raise;
31 D door; 32 D door blue; 33 D door red; 34 D door yellow; 35 W1 light; 36 W1 floor_lower;
37 W1 floor_lower; 38 W1 floor_lower; 39 W1 teleport; 40 W1 ceiling_raise; 41 S1 ceiling_lower;
42 SR door_close; 43 SR ceiling_lower; 44 W1 ceiling_lower; 45 SR floor_lower; 46 GR door;
47 G1 floor_raise; 48 _ scroll; 49 S1 crusher; 50 S1 door_close; 51 S1 secret_exit; 52 W1 exit;
53 W1 platform; 54 W1 platform_stop; 55 S1 floor_raise; 56 W1 floor_raise; 57 W1 crusher_stop;
58 W1 floor_raise; 59 W1 floor_raise; 60 SR floor_lower; 61 SR door; 62 SR lift; 63 SR door;
64 SR floor_raise; 65 SR floor_raise; 66 SR floor_raise; 67 SR floor_raise; 68 SR floor_raise;
69 SR floor_raise; 70 SR floor_lower; 71 S1 floor_lower; 72 WR ceiling_lower; 73 WR crusher;
74 WR crusher_stop; 75 WR door_close; 76 WR door_close; 77 WR crusher; 79 WR light; 80 WR light;
81 WR light; 82 WR floor_lower; 83 WR floor_lower; 84 WR floor_lower; 86 WR door; 87 WR platform;
88 WR lift; 89 WR platform_stop; 90 WR door; 91 WR floor_raise; 92 WR floor_raise;
93 WR floor_raise; 94 WR floor_raise; 95 WR floor_raise; 96 WR floor_raise; 97 WR teleport;
98 WR floor_lower; 99 SR door blue; 100 W1 stairs; 101 S1 floor_raise; 102 S1 floor_lower;
103 S1 door; 104 W1 light; 105 WR door; 106 WR door; 107 WR door_close; 108 W1 door; 109 W1 door;
110 W1 door_close; 111 S1 door; 112 S1 door; 113 S1 door_close; 114 SR door; 115 SR door;
116 SR door_close; 117 D door; 118 D door; 119 W1 floor_raise; 120 WR lift; 121 W1 lift;
122 S1 lift; 123 SR lift; 124 W1 secret_exit; 125 W1 monster_teleport; 126 WR monster_teleport;
127 S1 stairs; 128 WR floor_raise; 129 WR floor_raise; 130 W1 floor_raise; 131 S1 floor_raise;
132 SR floor_raise; 133 S1 door blue; 134 SR door red; 135 S1 door red; 136 SR door yellow;
137 S1 door yellow; 138 SR light; 139 SR light; 140 S1 floor_raise; 141 W1 crusher
"""


@dataclass(frozen=True)
class LineSpecial:
    trigger: str  # D, S1, SR, W1, WR, G1, GR, or "" for passive
    kind: str
    key: str | None = None

    @property
    def tagged(self):
        """Acts on the sectors tagged like the line (manual doors act on the back sector)."""
        return self.trigger not in ("D", "")


LINE_SPECIALS = {}
for _item in _LS.split(";"):
    _p = _item.split()
    LINE_SPECIALS[int(_p[0])] = LineSpecial("" if _p[1] == "_" else _p[1], _p[2], _p[3] if len(_p) > 3 else None)

EXIT_KINDS = {"exit", "secret_exit"}

# ---------------------------------------------------------- sector specials ---
SECRET_SPECIAL = 9
DAMAGE_SPECIALS = {4: 20, 5: 10, 7: 5, 11: 20, 16: 20}  # special: damage per 32 tics
LIGHT_SPECIALS = {1: "blink_random", 2: "blink_fast", 3: "blink_slow", 4: "blink_fast", 8: "glow",
                  12: "blink_slow_sync", 13: "blink_fast_sync", 17: "flicker"}
DOOR_SECTOR_SPECIALS = {10: "close_after_30s", 14: "open_after_5min"}
SKY = "F_SKY1"

# Line flags.
ML_BLOCKING, ML_BLOCKMONSTERS, ML_TWOSIDED, ML_DONTPEGTOP, ML_DONTPEGBOTTOM = 1, 2, 4, 8, 16
ML_SECRET, ML_SOUNDBLOCK, ML_DONTDRAW, ML_MAPPED = 32, 64, 128, 256

PLAYER_HEIGHT, MAX_STEP = 56, 24


@dataclass
class Thing:
    x: int
    y: int
    angle: int
    type: int
    flags: int

    def on(self, skill_bit):
        """Present in single player on that skill."""
        return bool(self.flags & skill_bit) and not self.flags & MULTI_ONLY


@dataclass
class Side:
    x_offset: int
    y_offset: int
    upper: str
    lower: str
    mid: str
    sector: int


@dataclass
class Line:
    v1: int
    v2: int
    flags: int
    special: int
    tag: int
    front: int  # sidedef index
    back: int   # sidedef index or -1


@dataclass
class Sector:
    floor: int
    ceil: int
    ftex: str
    ctex: str
    light: int
    special: int
    tag: int


@dataclass
class Map:
    game: str   # "doom" or "doom2"
    slot: str   # "E1M1" or "MAP01"
    things: list[Thing]
    lines: list[Line]
    sides: list[Side]
    verts: list[tuple[int, int]]
    sectors: list[Sector]
    _areas: list[float] | None = field(default=None, repr=False)

    # -- geometry ---------------------------------------------------------
    def line_sectors(self, ln):
        """(front sector, back sector or None)."""
        f = self.sides[ln.front].sector
        b = self.sides[ln.back].sector if ln.back >= 0 else None
        return f, b

    def length(self, ln):
        (x1, y1), (x2, y2) = self.verts[ln.v1], self.verts[ln.v2]
        return math.hypot(x2 - x1, y2 - y1)

    def midpoint(self, ln):
        (x1, y1), (x2, y2) = self.verts[ln.v1], self.verts[ln.v2]
        return (x1 + x2) / 2, (y1 + y2) / 2

    @property
    def sector_areas(self):
        """Area of each sector (map units^2) by the shoelace formula over its
        sides. A sector's sides run clockwise around it, holes included."""
        if self._areas is None:
            acc = [0.0] * len(self.sectors)
            for ln in self.lines:
                (x1, y1), (x2, y2) = self.verts[ln.v1], self.verts[ln.v2]
                cross = x1 * y2 - x2 * y1
                f, b = self.line_sectors(ln)
                acc[f] -= cross
                if b is not None:
                    acc[b] += cross
            self._areas = [abs(a) / 2 for a in acc]
        return self._areas

    @property
    def bbox(self):
        xs = [v[0] for v in self.verts]
        ys = [v[1] for v in self.verts]
        return min(xs), min(ys), max(xs), max(ys)

    def neighbours(self):
        """{sector: {neighbour sector: [line indexes]}} over two-sided lines."""
        adj = defaultdict(lambda: defaultdict(list))
        for i, ln in enumerate(self.lines):
            f, b = self.line_sectors(ln)
            if b is not None and b != f:
                adj[f][b].append(i)
                adj[b][f].append(i)
        return adj

    def tagged(self, tag):
        return [i for i, s in enumerate(self.sectors) if tag and s.tag == tag]

    def sector_of_point(self, x, y):
        """Sector containing (x, y), by casting a ray to +x and taking the
        nearest crossed line's facing side. None if outside the map."""
        best, best_d = None, math.inf
        for ln in self.lines:
            (x1, y1), (x2, y2) = self.verts[ln.v1], self.verts[ln.v2]
            if (y1 > y) == (y2 > y):
                continue
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi < x or xi - x >= best_d:
                continue
            # Side of the line the point is on: front is right of v1->v2.
            right = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1) < 0
            f, b = self.line_sectors(ln)
            best, best_d = (f if right else b), xi - x
        return best

    # -- things -----------------------------------------------------------
    def things_on(self, skill_bit):
        return [t for t in self.things if t.on(skill_bit)]


def _str8(b):
    return b.split(b"\0")[0].decode("ascii", "replace").upper()


def _parse(game, slot, lumps):
    things = [Thing(*v) for v in struct.iter_unpack("<hhhhh", lumps["THINGS"])]
    lines = [Line(*v) for v in struct.iter_unpack("<HHhhhhh", lumps["LINEDEFS"])]
    sides = [Side(x, y, _str8(u), _str8(lo), _str8(m), s)
             for x, y, u, lo, m, s in struct.iter_unpack("<hh8s8s8sh", lumps["SIDEDEFS"])]
    verts = list(struct.iter_unpack("<hh", lumps["VERTEXES"]))
    sectors = [Sector(f, c, _str8(ft), _str8(ct), lt, sp, tg)
               for f, c, ft, ct, lt, sp, tg in struct.iter_unpack("<hh8s8shhh", lumps["SECTORS"])]
    return Map(game, slot, things, lines, sides, verts, sectors)


def load_maps(game, path=None):
    path = path or IWADS[game]
    if not path:
        sys.exit(f"{IWAD_VARS[game]} is not set: add it to .env (see .env.example)")
    lumps = read_wad(path)
    maps = []
    for i, (name, _) in enumerate(lumps):
        if (name.startswith("E") and len(name) == 4 and name[2] == "M") or \
                (name.startswith("MAP") and len(name) == 5):
            maplumps = {n: d for n, d in lumps[i + 1:i + 11]}
            maps.append(_parse(game, name, maplumps))
    return maps


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
