"""Doom-format maps read from a WAD into plain dataclasses (sector, line,
side and thing indexes as in the lumps), with geometry helpers.

    from levels.wadmap import load_maps, parse
    for m in load_maps("doom2"): ...             # every map in DOOM2_WAD
    m = parse("doom2", "MAP01", {name: data})    # from a map's lumps
"""
import math
import struct
import sys
from collections import defaultdict
from dataclasses import dataclass, field

from .wad import IWAD_VARS, IWADS, read_wad

# Thing flags. Skill bits: EASY = ITYTD + HNTR, MEDIUM = HMP, HARD = UV + NM.
EASY, MEDIUM, HARD, AMBUSH, MULTI_ONLY = 1, 2, 4, 8, 16
SKILLS = {"easy": EASY, "medium": MEDIUM, "hard": HARD}

# Line flags.
ML_BLOCKING, ML_BLOCKMONSTERS, ML_TWOSIDED, ML_DONTPEGTOP, ML_DONTPEGBOTTOM = 1, 2, 4, 8, 16
ML_SECRET, ML_SOUNDBLOCK, ML_DONTDRAW, ML_MAPPED = 32, 64, 128, 256


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


def parse(game, slot, lumps):
    """Map from its lumps ({name: data}: THINGS, LINEDEFS, SIDEDEFS, VERTEXES, SECTORS)."""
    things = [Thing(*v) for v in struct.iter_unpack("<hhhhh", lumps["THINGS"])]
    lines = [Line(*v) for v in struct.iter_unpack("<HHhhhhh", lumps["LINEDEFS"])]
    sides = [Side(x, y, _str8(u), _str8(lo), _str8(m), s)
             for x, y, u, lo, m, s in struct.iter_unpack("<hh8s8s8sh", lumps["SIDEDEFS"])]
    verts = list(struct.iter_unpack("<hh", lumps["VERTEXES"]))
    sectors = [Sector(f, c, _str8(ft), _str8(ct), lt, sp, tg)
               for f, c, ft, ct, lt, sp, tg in struct.iter_unpack("<hh8s8shhh", lumps["SECTORS"])]
    return Map(game, slot, things, lines, sides, verts, sectors)


def load_maps(game, path=None):
    """Every ExMy / MAPxx map in the WAD at path (default: the game's IWAD)."""
    path = path or IWADS[game]
    if not path:
        sys.exit(f"{IWAD_VARS[game]} is not set: add it to .env (see .env.example)")
    lumps = read_wad(path)
    maps = []
    for i, (name, _) in enumerate(lumps):
        if (name.startswith("E") and len(name) == 4 and name[2] == "M") or \
                (name.startswith("MAP") and len(name) == 5):
            maplumps = {n: d for n, d in lumps[i + 1:i + 11]}
            maps.append(parse(game, name, maplumps))
    return maps
