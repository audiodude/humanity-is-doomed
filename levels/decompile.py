"""Decompiles Doom-format maps into level modules (see docs/decompiler-spec.md).

    python3 -m levels.decompile SOURCE [MAP ...] [--verify] [--out DIR]

SOURCE is a WAD path, or doom / doom2 for the IWADs in .env; MAPs default to
every map in it. Each map becomes <DIR>/<source stem>_<slot>.py (default
levels/imported/, gitignored: id's map data is never committed), built with
`python3 -m levels imported.doom2_map01` into wads/imported/<SOURCE STEM>.WAD.

Lines split where another line's vertex lies on them (the builder splits
there too) and straight runs merge. A sector whose lines don't close into
loops is repaired by the fewest edits that close every loop (move a side to
another sector, leave out a side or a stray wall, turn a wall round, close a
gap with a wall) when that set of edits is unique, each written as a
`# repaired:` comment; otherwise the map is refused. The module holds what
the builder infers from as plain data (loops, wall, lower, face, kind, door
actions, SPECIAL_BETWEEN, SPECIAL_WALLS, FREE_LINES, SECRET_DOORS), the
original map's playability findings as KNOWN_ISSUES, and every other
difference from the original as OVERRIDES, found by building the guess with
mapgen.compile_level. --verify rebuilds each module without ZDBSP and
compares it with the original, both merged the same way: sectors and things
exactly, lines with their sides as multisets; only lines through a vertex a
repair edited may differ.
"""
import argparse
import csv
import importlib.util
import math
import os
import re
import statistics
import sys
import types
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace

from . import checks, doom2, model
from .doom2 import ACTION_NAMES, ACTORS, KEY_OF, LINE_SPECIALS, PLAYERS, SECTOR_NAMES, THING_NAMES, is_decal
from .mapgen import compile_level
from .measure import LABELS, fmt
from .model import (DOOR, LIFT, NO_TEX, ROOM, SECRET_HINT, SKY, THING_BITS, LevelError, Sector, Special, Thing,
                    area2, floor_movers, floor_range, load, on_segment, rect, segments_cross)
from .model import Line as LineOverride
from .model import Side as SideOverride
from .wad import IWADS, MAP_LUMPS, MAP_MARKER, UMAPINFO_ENTRY, iwad_textures, read_wad, umapinfo_body
from .wadmap import parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "levels", "imported")
RESEARCH = os.path.join(ROOT, "research", "data")
WIDTH = 110   # module line width

FLAG_NAMES = dict(sorted((v, n) for n, v in vars(model).items() if n.startswith("ML_")))   # {bit: "ML_..."}
LIQUIDS = {"NUKAGE": "nukage", "LAVA": "lava", "BLOOD": "blood", "SLIME": "slime"}

TITLES = dict(zip(
    [f"E{e}M{m}" for e in range(1, 5) for m in range(1, 10)] + [f"MAP{n:02}" for n in range(1, 33)],
    ["Hangar", "Nuclear Plant", "Toxin Refinery", "Command Control", "Phobos Lab", "Central Processing",
     "Computer Station", "Phobos Anomaly", "Military Base",
     "Deimos Anomaly", "Containment Area", "Refinery", "Deimos Lab", "Command Center",
     "Halls of the Damned", "Spawning Vats", "Tower of Babel", "Fortress of Mystery",
     "Hell Keep", "Slough of Despair", "Pandemonium", "House of Pain", "Unholy Cathedral", "Mt. Erebus",
     "Limbo", "Dis", "Warrens",
     "Hell Beneath", "Perfect Hatred", "Sever the Wicked", "Unruly Evil", "They Will Repent",
     "Against Thee Wickedly", "And Hell Followed", "Unto the Cruel", "Fear",
     "Entryway", "Underhalls", "The Gantlet", "The Focus", "The Waste Tunnels", "The Crusher",
     "Dead Simple", "Tricks and Traps", "The Pit", "Refueling Base", "Circle of Death", "The Factory",
     "Downtown", "The Inmost Dens", "Industrial Zone", "Suburbs", "Tenements", "The Courtyard",
     "The Citadel", "Gotcha!", "Nirvana", "The Catacombs", "Barrels o' Fun", "The Chasm", "Bloodfalls",
     "The Abandoned Mines", "Monster Condo", "The Spirit World", "The Living End", "Icon of Sin",
     "Wolfenstein", "Grosse"]))


class Refused(Exception):
    """The map can't be decompiled; the message says why."""


@dataclass(frozen=True)
class Sd:
    """A sidedef. None fields (sides a repair made up) take the builder's value."""
    sector: int
    upper: str | None
    lower: str | None
    mid: str | None
    x: int | None
    y: int | None


@dataclass
class Ln:
    """A linedef with its points and sides. flags None: the builder's (repairs)."""
    a: tuple[int, int]
    b: tuple[int, int]
    flags: int | None
    action: int
    tag: int
    front: Sd
    back: Sd | None

    @property
    def length(self):
        return math.dist(self.a, self.b)

    @property
    def free(self):
        return self.back is not None and self.back.sector == self.front.sector

    def key(self):
        return (self.a, self.b, self.flags, self.action, self.tag, self.front, self.back)


# ----------------------------------------------------------------- reading ---


def read_map_lines(m) -> list[Ln]:
    def side(i):
        s = m.sides[i]
        return Sd(s.sector, s.upper, s.lower, s.mid, s.x_offset, s.y_offset)
    return [Ln(m.verts[l.v1], m.verts[l.v2], l.flags, l.special, l.tag, side(l.front),
               side(l.back) if l.back >= 0 else None) for l in m.lines]


def map_entries(lumps):
    """[(slot, {lump: data})] for every map marker, in WAD order."""
    out = []
    for i, (name, _) in enumerate(lumps):
        if MAP_MARKER.fullmatch(name):
            j, parts = i + 1, {}
            while j < len(lumps) and lumps[j][0] in MAP_LUMPS:
                parts[lumps[j][0]] = lumps[j][1]
                j += 1
            out.append((name, parts))
    return out


QUOTED = re.compile(r'\s*(\w+)\s*=\s*"([^"]*)"\s*')


def umapinfo_entries(lumps) -> dict[str, dict[str, str] | str]:
    """{slot: UMAPINFO module value} from the WAD's UMAPINFO lump: a {key:
    value} dict if the builder writes that back as the same body, else the
    body as it is."""
    text = next((d.decode("latin-1") for n, d in lumps if n == "UMAPINFO"), "")
    out = {}
    for m in UMAPINFO_ENTRY.finditer(text):
        body = m.group(0)[m.group(0).index("{") + 1:-1]
        info = dict(QUOTED.fullmatch(ln).groups() for ln in body.splitlines() if QUOTED.fullmatch(ln))
        out[m.group(1).upper()] = info if umapinfo_body(info) == body else body
    return out


def texture_widths(game, resources):
    found = iwad_textures(IWADS[game], resources)
    return {t: w for t, (w, _) in found[0].items()} if found else {}


# ------------------------------------------------------- split and merge ---


def split_lines(lines: list[Ln]) -> list[Ln]:
    """Split lines at every vertex of another line lying on them, as the
    builder does; each piece's x offsets carry on from the line's."""
    verts = sorted({p for l in lines for p in (l.a, l.b)})
    xs = [p[0] for p in verts]
    out = []
    for l in lines:
        (x1, y1), (x2, y2) = l.a, l.b
        lo, hi = sorted((y1, y2))
        mids = [p for p in verts[bisect_left(xs, min(x1, x2)):bisect_right(xs, max(x1, x2))]
                if lo <= p[1] <= hi and on_segment(p, l.a, l.b)]
        if not mids:
            out.append(l)
            continue
        chain = [l.a] + sorted(mids, key=lambda p: math.dist(l.a, p)) + [l.b]
        for u, v in zip(chain, chain[1:]):
            front = replace(l.front, x=l.front.x + round(math.dist(l.a, u)))
            back = l.back and replace(l.back, x=l.back.x + round(math.dist(v, l.b)))
            out.append(replace(l, a=u, b=v, front=front, back=back))
    return out


def carries_on(s1: Sd, s2: Sd, length, widths):
    """s2's x offset continues s1's pattern after `length`, for each texture shown."""
    if (s1.sector, s1.upper, s1.lower, s1.mid, s1.y) != (s2.sector, s2.upper, s2.lower, s2.mid, s2.y) \
            or None in (s1.x, s2.x, s1.mid):
        return False
    x = s1.x + round(length)
    for t in {s1.upper, s1.lower, s1.mid} - {NO_TEX, ""}:
        w = widths.get(t)
        if (x - s2.x) % w if w else x != s2.x:
            return False
    return True


def mergeable(l1: Ln, l2: Ln, widths):
    """l1 ends where l2 starts; they run straight on and look the same."""
    (ax, ay), (px, py), (bx, by) = l1.a, l1.b, l2.b
    if (px - ax) * (by - ay) != (py - ay) * (bx - ax) or (px - ax) * (bx - px) + (py - ay) * (by - py) <= 0:
        return False
    if (l1.flags, l1.action, l1.tag) != (l2.flags, l2.action, l2.tag) or (l1.back is None) != (l2.back is None):
        return False
    return carries_on(l1.front, l2.front, l1.length, widths) and \
        (l1.back is None or carries_on(l2.back, l1.back, l2.length, widths))


def merge_lines(lines: list[Ln], widths) -> list[Ln]:
    """Merge straight runs: two lines meeting at a vertex no other line uses,
    collinear, with the same flags, action, tag, sectors and textures, and
    x offsets that carry on. Repeats until no two lines merge, so merging
    merged lines changes nothing."""
    lines = dict(enumerate(lines))
    ending, starting = defaultdict(set), defaultdict(set)
    for i, l in lines.items():
        ending[l.b].add(i)
        starting[l.a].add(i)
    todo = sorted(ending.keys() & starting.keys(), reverse=True)
    while todo:
        p = todo.pop()
        if len(ending[p]) != 1 or len(starting[p]) != 1:
            continue
        (i,), (j,) = ending[p], starting[p]
        if i == j or not mergeable(lines[i], lines[j], widths):
            continue
        m = lines.pop(j)
        lines[i] = replace(lines[i], b=m.b, back=m.back)
        ending[p].clear()
        starting[p].clear()
        ending[m.b] = {i if k == j else k for k in ending[m.b]}
        todo += [lines[i].a, m.b]
    return [lines[i] for i in sorted(lines)]


# ----------------------------------------------------------------- repair ---


def directed(lines):
    """{(u, v): sector} for every sector edge, the sector on the right."""
    out = {}
    for l in lines:
        if not l.free:
            out[l.a, l.b] = l.front.sector
            if l.back:
                out[l.b, l.a] = l.back.sector
    return out


def imbalance(lines):
    """{(sector, point): edges out - edges in}, nonzero only where a sector's
    lines don't close into loops."""
    imb = Counter()
    for (u, v), s in directed(lines).items():
        imb[s, u] += 1
        imb[s, v] -= 1
    return {k: d for k, d in imb.items() if d}


@dataclass(frozen=True)
class Edit:
    """One repair: "side" moves a line's side to `sector`, "flip" turns a wall
    round, "drop" leaves a side out (a wall's only side: the whole wall), "add"
    gives `sector` the edge u->v."""
    kind: str
    line: int
    which: int    # side: 0 front, 1 back
    sector: int
    u: tuple = None
    v: tuple = None
    vec: tuple = ()   # ((sector, point), change in imbalance)


def repair_candidates(lines, imb):
    bad = sorted({s for s, _ in imb})
    badv = {p for _, p in imb}
    edges = directed(lines)

    def aligned(vec):
        return all(imb.get(k, 0) * d < 0 and abs(d) <= abs(imb[k]) for k, d in vec)
    out = []
    for i, l in enumerate(lines):
        if l.free or l.a not in badv or l.b not in badv:
            continue
        for which, sd, other in ((0, l.front, l.back), (1, l.back, l.front)):
            if sd is None:
                continue
            u, v = (l.a, l.b) if which == 0 else (l.b, l.a)
            vec = (((sd.sector, u), -1), ((sd.sector, v), 1))
            if aligned(vec):
                out.append(Edit("drop", i, which, sd.sector, vec=vec))
            for t in sorted(set(bad) | ({other.sector} if other else set()) - {sd.sector}):
                vec = (((sd.sector, u), -1), ((sd.sector, v), 1), ((t, u), 1), ((t, v), -1))
                if aligned(vec):
                    out.append(Edit("side", i, which, t, vec=vec))
        if l.back is None:
            s = l.front.sector
            vec = (((s, l.a), -2), ((s, l.b), 2))
            if aligned(vec):
                out.append(Edit("flip", i, 0, s, vec=vec))
    verts = {p for l in lines for p in (l.a, l.b)}
    for s in bad:
        for u in sorted(p for (t, p), d in imb.items() if t == s and d < 0):
            for v in sorted(p for (t, p), d in imb.items() if t == s and d > 0):
                # A new wall may not cross or run along other lines.
                if (u, v) in edges or edges.get((v, u)) == s or \
                        any(segments_cross(u, v, l.a, l.b) for l in lines) or \
                        any(on_segment(p, u, v) for p in verts):
                    continue
                out.append(Edit("add", -1, 0, s, u, v, (((s, u), 1), ((s, v), -1))))
    return out


def fewest_repairs(imb, candidates, limit=8):
    """Every set of candidate edits, of the smallest size, that zeroes imb."""
    touching = defaultdict(list)
    for c in candidates:
        for k, _ in c.vec:
            touching[k].append(c)

    def search(res, used, left, found):
        if not res:
            found.add(frozenset(used))
            return
        if left == 0 or sum(map(abs, res.values())) > 4 * left:
            return
        k = min(res)
        for c in touching[k]:
            if c not in used and all(res.get(kk, 0) * d < 0 and abs(d) <= abs(res[kk]) for kk, d in c.vec):
                nxt = dict(res)
                for kk, d in c.vec:
                    nxt[kk] += d
                    if not nxt[kk]:
                        del nxt[kk]
                search(nxt, used | {c}, left - 1, found)
    for n in range(1, limit + 1):
        found = set()
        search(imb, frozenset(), n, found)
        if found:
            return found
    return set()


def describe(e: Edit, lines):
    """What id's data had and what the module does instead."""
    if e.kind == "add":
        l = next((l for l in lines if (l.a, l.b) == (e.v, e.u) and l.back is None), None)
        if l:
            return (f"line {l.a}-{l.b} has sector {e.sector} behind it but no back side; "
                    f"the module makes it two-sided")
        return f"sector {e.sector} is open between {e.u} and {e.v}; the module closes it with a wall"
    l = lines[e.line]
    if e.kind == "side":
        old = (l.front, l.back)[e.which].sector
        return (f"line {l.a}-{l.b}: its {('front', 'back')[e.which]} side is in sector {old}, which doesn't "
                f"close there; the module puts that side in sector {e.sector}")
    if e.kind == "flip":
        return (f"wall {l.a}-{l.b} faces away from its sector {e.sector}; "
                f"the module builds it as {l.b}-{l.a}")
    if l.back is None:
        return f"wall {l.a}-{l.b} of sector {e.sector} closes nothing; the module leaves it out"
    keep = (l.back, l.front)[e.which].sector
    return (f"line {l.a}-{l.b}: its {('front', 'back')[e.which]} side is in sector {e.sector}, which doesn't "
            f"close there; the module makes it a wall of sector {keep}")


def repair(lines):
    """(lines, [(edit, description)]): the lines with the unique fewest-edits
    repair that closes every sector applied. Raises Refused."""
    imb = imbalance(lines)
    if not imb:
        return lines, []
    found = fewest_repairs(imb, repair_candidates(lines, imb))
    if len(found) != 1:
        report = []
        for s in sorted({s for s, _ in imb}):
            pts = {p for (t, p) in imb if t == s}
            dangling = [f"{l.a}-{l.b}" for l in lines if not l.free and (l.a in pts or l.b in pts)
                        and s in (l.front.sector, l.back and l.back.sector)]
            report.append(f"sector {s} doesn't close at {sorted(pts)}; its lines there: {', '.join(dangling)}")
        if found:
            report.append(f"{len(found)} different repairs of {len(next(iter(found)))} edits close it:")
            report += ["  " + "; ".join(describe(e, lines) for e in sorted(f, key=repr)) for f in found]
        raise Refused("\n".join(report))
    edits = sorted(next(iter(found)), key=lambda e: (e.line, e.kind, repr(e)))
    done = [(e, describe(e, lines)) for e in edits]
    lines = list(lines)
    dropped = set()
    for e in edits:
        if e.kind == "side":
            l = lines[e.line]
            sd = replace((l.front, l.back)[e.which], sector=e.sector)
            lines[e.line] = replace(l, front=sd) if e.which == 0 else replace(l, back=sd)
        elif e.kind == "flip":
            lines[e.line] = replace(lines[e.line], a=lines[e.line].b, b=lines[e.line].a)
        elif e.kind == "drop" and lines[e.line].back is None:
            dropped.add(e.line)
        elif e.kind == "drop":
            l = lines[e.line]
            wall = Sd((l.back, l.front)[e.which].sector, None, None, None, None, None)
            lines[e.line] = replace(l, front=wall, back=None, flags=None) if e.which else \
                replace(l, a=l.b, b=l.a, front=wall, back=None, flags=None)
        else:
            new = Sd(e.sector, None, None, None, None, None)
            k = next((k for k, l in enumerate(lines) if (l.a, l.b) == (e.v, e.u) and l.back is None), None)
            if k is None:
                lines.append(Ln(e.u, e.v, None, 0, 0, new, None))
            else:
                lines[k] = replace(lines[k], back=new, flags=None)
    return [l for k, l in enumerate(lines) if k not in dropped], done


def repaired_at(done, lines):
    """The sectors and vertices the repairs touch."""
    sectors, points = set(), set()
    for e, _ in done:
        if e.kind == "add":
            sectors |= {e.sector} | {l.front.sector for l in lines if (l.a, l.b) == (e.v, e.u)}
            points |= {e.u, e.v}
        else:
            l = lines[e.line]
            sectors |= {e.sector, l.front.sector} | ({l.back.sector} if l.back else set())
            points |= {l.a, l.b}
    return sectors, points


# -------------------------------------------------------------- loops ---


def trace(edges):
    """Loops of directed edges [(u, v)], each a face boundary with the sector
    on the right: at a vertex the walk turns as far right as it can."""
    out_at = defaultdict(list)
    for u, v in edges:
        out_at[u].append(v)
    seen, loops = set(), []
    for start in edges:
        if start in seen:
            continue
        loop, (u, v) = [], start
        while True:
            seen.add((u, v))
            loop.append((u, v))
            back = math.atan2(u[1] - v[1], u[0] - v[0])
            ws = sorted(out_at[v], key=lambda w, v=v, back=back:
                        (math.atan2(w[1] - v[1], w[0] - v[0]) - back) % (2 * math.pi) or 2 * math.pi)
            if (v, ws[0]) == start:
                break
            w = next((w for w in ws if (v, w) not in seen), None)
            if w is None:
                break
            u, v = v, w
        loops.append(loop)
    return loops


def rect_args(loop):
    """(x1, y1, x2, y2) if rect() of them gives exactly this loop."""
    if len(loop) == 4:
        (x0, y0), _, (x2, y2), _ = loop
        if x0 != x2 and y0 != y2 and loop == rect(x0, y0, x2, y2):
            return x0, y0, x2, y2
    return None


def best_start(loop, sides, x_offsets):
    """The loop rotated so the builder's x offsets (distance along the loop,
    with X_OFFSETS "continuous") match the most original ones; ties prefer a
    rect() and then the first."""
    n = len(loop)
    lens = [math.dist(loop[i], loop[(i + 1) % n]) for i in range(n)]
    best = None
    for r in range(n):
        pos, hits = 0.0, 0
        for k in range(n if x_offsets == "continuous" else 0):
            i = (r + k) % n
            sd = sides[i]
            want = 0 if any(is_decal(t or "") for t in (sd.upper, sd.lower, sd.mid)) else round(pos) % 2048
            hits += sd.x is None or sd.x == want
            pos += lens[i]
        rotated = loop[r:] + loop[:r]
        score = (hits, rect_args(rotated) is not None, -r)
        if best is None or score > best[0]:
            best = (score, rotated)
    return best[1]


# ---------------------------------------------------------------- guesses ---


def skills_of(flags):
    """Thing flags -> (Thing.skills letters, Thing.extra: the other bits)."""
    return "".join(c for c, b in THING_BITS.items() if flags & b), flags & ~sum(THING_BITS.values())


@dataclass
class Guess:
    """The module's data, before writing."""
    names: list[str]
    loops: list[list]
    pillars: list[list]
    fields: list[dict]          # per sector: wall, lower, face, kind, action
    x_offsets: str              # X_OFFSETS
    special_between: dict = field(default_factory=dict)
    special_walls: dict = field(default_factory=dict)
    free_lines: dict = field(default_factory=dict)
    secret_doors: dict = field(default_factory=dict)
    overrides: dict = field(default_factory=dict)


def sector_list(m, g: Guess):
    return [Sector(g.names[i], g.loops[i], s.floor, s.ceil, s.ftex, s.ctex, s.light, f["wall"], lower=f["lower"],
                   face=f["face"], special=s.special, tag=s.tag, kind=f["kind"], action=f["action"],
                   pillars=g.pillars[i])
            for i, (s, f) in enumerate(zip(m.sectors, g.fields))]


def level_of(m, g: Guess, wad, things, overrides=None, resources=()):
    return load(types.SimpleNamespace(
        MAP=m.slot, WAD=wad, SECTORS=sector_list(m, g), THINGS=things, SPECIAL_BETWEEN=g.special_between,
        SPECIAL_WALLS=g.special_walls, FREE_LINES=g.free_lines, SECRET_DOORS=g.secret_doors,
        OVERRIDES=overrides or {}, IMPORTED=True, RESOURCES=resources, X_OFFSETS=g.x_offsets))


def matched(level, compiled, by_ends):
    """[(original line, built line, built sides as (front, back) in the
    original's direction, flipped)] and the built lines no original matches."""
    out, problems = [], []
    idx = {name: i for i, name in enumerate(level.sectors)}
    for bl, bs in zip(compiled.lines, compiled.sides):
        ol = by_ends.get(frozenset((bl.v1, bl.v2)))
        if ol is None:
            problems.append(f"built line {bl.v1}-{bl.v2} matches no original line")
            continue
        flipped = (bl.v1, bl.v2) != (ol.a, ol.b)
        f, b = bs[0], bs[1] if len(bs) == 2 else None
        if flipped:
            f, b = b, f
        if f is None or idx[f.sector.name] != ol.front.sector or \
                (b and idx[b.sector.name]) != (ol.back and ol.back.sector):
            problems.append(f"built line {bl.v1}-{bl.v2} has other sectors than the original")
            continue
        out.append((ol, bl, (f, b), flipped))
    if len(out) != len(by_ends):
        built = {frozenset((ol.a, ol.b)) for ol, *_ in out}
        problems += [f"original line {l.a}-{l.b} isn't built" for k, l in by_ends.items() if k not in built]
    return out, problems


def side_diff(osd: Sd | None, bsd):
    if osd is None:
        return None
    d = {k: o for k, o, b in (("upper", osd.upper, bsd.upper), ("lower", osd.lower, bsd.lower),
                               ("mid", osd.mid, bsd.mid), ("x", osd.x, bsd.x_offset), ("y", osd.y, bsd.y_offset))
         if o is not None and o != b}
    return SideOverride(**d) if d else None


def overrides_of(pairs):
    out = {}
    for ol, bl, (bf, bb), flipped in pairs:
        d = {k: o for k, o, b in (("action", ol.action, bl.action), ("tag", ol.tag, bl.tag),
                                   ("flags", ol.flags, bl.flags)) if o is not None and o != b}
        if f := side_diff(ol.front, bf):
            d["front"] = f
        if ol.back and (b := side_diff(ol.back, bb)):
            d["back"] = b
        if d or flipped:
            out[ol.a, ol.b] = LineOverride(**d)
    return out


def top(votes: Counter, prefer=None):
    """The most-voted texture; ties go to `prefer`, then alphabetical."""
    if not votes:
        return prefer
    return max(votes, key=lambda t: (votes[t], t == prefer, [-ord(c) for c in t]))


def guess(m, lines, x_offsets):
    """Sector loops, names and fields, specials, free lines from the
    (repaired) lines; the textures and SPECIAL_BETWEEN come later."""
    n = len(m.sectors)
    edges = [{} for _ in range(n)]
    for l in lines:
        if not l.free:
            edges[l.front.sector][l.a, l.b] = l.front
            if l.back:
                edges[l.back.sector][l.b, l.a] = l.back
    one_sided = {(l.a, l.b) for l in lines if l.back is None}
    loops, pillars = [], []
    for i in range(n):
        outer, holes, solid = [], [], []
        for lp in trace(edges[i]):
            pts = best_start([u for u, _ in lp], [edges[i][e] for e in lp], x_offsets)
            if area2(pts) < 0:
                outer.append(pts)
            else:
                (solid if all(e in one_sided for e in lp) else holes).append(pts)
        loops.append(outer + holes)
        pillars.append(solid)
    tagged = defaultdict(set)
    for i, s in enumerate(m.sectors):
        if s.tag:
            tagged[s.tag].add(i)
    opened, lowered = set(), set()
    for l in lines:
        sp = LINE_SPECIALS.get(l.action)
        if sp and sp.kind == "door":
            if sp.trigger == "D":
                if l.back:
                    opened.add(l.back.sector)
            else:
                opened |= tagged[l.tag]
        elif sp and sp.kind == "lift":
            lowered |= tagged[l.tag]
    two_sided, walls = defaultdict(list), defaultdict(Counter)
    for l in lines:
        if l.back and not l.free:
            two_sided[l.front.sector].append(l)
            two_sided[l.back.sector].append(l)
        elif l.back is None and l.front.mid not in (None, NO_TEX, ""):
            walls[l.front.sector][l.front.mid] += l.length
    names, fields = [], []
    for i, s in enumerate(m.sectors):
        kind = DOOR if s.ceil <= s.floor and i in opened else LIFT if i in lowered else ROOM
        acts = {l.action for l in two_sided[i]}
        action = acts.pop() if len(acts) == 1 else 0
        if not (action and LINE_SPECIALS.get(action) and LINE_SPECIALS[action].trigger == "D"
                and all(l.back.sector == i for l in two_sided[i])):
            action = 0
        liquid = next((v for k, v in LIQUIDS.items() if s.ftex.startswith(k)), "hazard")
        role = "door" if kind == DOOR else "lift" if kind == LIFT else "secret" if s.special == doom2.SECRET_AREA \
            else liquid if s.special in doom2.DAMAGING else "room"
        names.append(f"{role}_{i}")
        wall = top(walls[i], NO_TEX)
        fields.append({"wall": wall, "lower": None, "face": wall if kind == DOOR else None, "kind": kind,
                       "action": action})
    g = Guess(names, loops, pillars, fields, x_offsets)
    for l in lines:
        if l.free:
            mid = l.front.mid
            g.free_lines[l.a, l.b] = Special(l.action, l.tag, None if mid in (NO_TEX, "") else mid)
    special_walls(g, lines)
    return g


def special_walls(g: Guess, lines):
    g.special_walls = {}
    for l in lines:
        if l.back is None and l.action:
            mid = l.front.mid
            g.special_walls[l.a, l.b] = Special(l.action, l.tag, None if mid == g.fields[l.front.sector]["wall"]
                                                else mid)


def vote_textures(g: Guess, level, compiled, pairs):
    """Pick each sector's wall, lower and face from what the builder would
    put where, against what the original has there."""
    secs = list(level.sectors.values())
    movers = floor_movers(compiled.lines)
    ranges = {s: floor_range(s, compiled.lines, movers) for s in secs}
    walls, lowers, faces, pegged, shown = (defaultdict(Counter) for _ in range(5))
    for ol, *_ in pairs:
        if ol.back is None:
            if ol.front.mid not in (None, NO_TEX, "") and not ol.action:
                walls[ol.front.sector][ol.front.mid] += ol.length
            continue
        if ol.free:
            continue
        for sd, osd in ((ol.front, ol.back), (ol.back, ol.front)):
            me, other = secs[sd.sector], secs[osd.sector]
            if sd.upper is not None:
                if other.kind == DOOR:
                    faces[osd.sector][sd.upper] += 1
                elif other.ceil < me.ceil and not (me.ctex == SKY and other.ctex == SKY) \
                        and sd.upper not in (NO_TEX, ""):
                    walls[sd.sector][sd.upper] += ol.length
            moving = LIFT in (me.kind, other.kind)
            if sd.lower is not None and (ranges[other][1] > ranges[me][0] or moving):
                lowers[osd.sector][sd.lower] += 1
                if not moving:
                    # The builder unpegs a lower that is the sector's own wall.
                    (pegged if ol.flags is not None and ol.flags & 16 else shown)[sd.sector][sd.lower] += 1
    for i, f in enumerate(g.fields):
        f["wall"] = top(walls[i]) or top(pegged[i])
    near = defaultdict(Counter)
    for ol, *_ in pairs:
        if ol.back and not ol.free:
            for me, other in ((ol.front.sector, ol.back.sector), (ol.back.sector, ol.front.sector)):
                if g.fields[other]["wall"]:
                    near[me][g.fields[other]["wall"]] += 1
    for i, f in enumerate(g.fields):
        if f["wall"] is None:
            # Nothing shows this sector's wall: pick a neighbour's that unpegs nothing.
            f["wall"] = top(Counter({t: n for t, n in near[i].items() if t not in shown[i]})) or NO_TEX
        lower = top(lowers[i], f["wall"])
        f["lower"] = None if lower == f["wall"] else lower
        f["face"] = (top(faces[i]) or f["wall"]) if f["kind"] == DOOR else None


def choose_between(g: Guess, pairs):
    """SPECIAL_BETWEEN for sector pairs whose shared lines all have one
    action, tag and middle texture, where that saves overrides."""
    by_pair = defaultdict(list)
    for p in pairs:
        ol = p[0]
        if ol.back and not ol.free:
            by_pair[tuple(sorted((ol.front.sector, ol.back.sector)))].append(p)
    for (a, b), ps in sorted(by_pair.items()):
        acts = {(ol.action, ol.tag) for ol, *_ in ps}
        mids = {sd.mid for ol, *_ in ps for sd in (ol.front, ol.back)}
        if len(acts) != 1 or None in mids:
            continue
        action, tag = acts.pop()
        tex = mids.pop() if len(mids) == 1 else NO_TEX
        tex = None if tex in (NO_TEX, "") else tex
        fronts = Counter(ol.front.sector for ol, *_ in ps)
        first = a if fronts[a] >= fronts[b] else b
        with_ = sum(ol.front.sector != first or any(sd.mid != (tex or NO_TEX) for sd in (ol.front, ol.back))
                    for ol, *_ in ps)
        without = sum(flipped or (bl.action, bl.tag) != (ol.action, ol.tag)
                      or (bf.mid, bb.mid) != (ol.front.mid, ol.back.mid) for ol, bl, (bf, bb), flipped in ps)
        if with_ + 1 < without or (with_ < without and (action, tag, tex) != (0, 0, None)):
            g.special_between[g.names[first], g.names[b if first == a else a]] = Special(action, tag, tex)


def choose_secret_doors(g: Guess, lines):
    """Doors whose lines are mostly ML_SECRET, offsets found later."""
    for i, f in enumerate(g.fields):
        if f["kind"] != DOOR:
            continue
        touching = [l for l in lines if not l.free and i in (l.front.sector, l.back and l.back.sector)
                    and l.flags is not None]
        if sum(bool(l.flags & 32) for l in touching) * 2 > len(touching):
            g.secret_doors[g.names[i]] = (0, 0)


def secret_offsets(g: Guess, pairs):
    """Each secret door's face offsets: the most common difference between
    the original and the built (unshifted) sides showing its face."""
    idx = {name: i for i, name in enumerate(g.names)}
    for name in g.secret_doors:
        d = idx[name]
        diffs = Counter()
        for ol, bl, (bf, bb), _ in pairs:
            if ol.back and not ol.free:
                for sd, bsd, other in ((ol.front, bf, ol.back), (ol.back, bb, ol.front)):
                    if other.sector == d and sd.sector != d and sd.x is not None:
                        diffs[sd.x - bsd.x_offset, sd.y - bsd.y_offset] += 1
        g.secret_doors[name] = max(diffs, key=lambda k: (diffs[k], k == SECRET_HINT)) if diffs else (0, 0)


# ----------------------------------------------------------------- writer ---


def q(s):
    return f'"{s}"' if '"' not in s and "\\" not in s else repr(s)


def pt(p):
    return f"({p[0]}, {p[1]})"


def wrap(first, atoms, indent, end):
    """first, then atoms joined by ", ", then end; wrapped at WIDTH."""
    if not atoms:
        return [first + end]
    out, cur = [], first
    for k, a in enumerate(atoms):
        piece = a + (", " if k < len(atoms) - 1 else end)
        if len(cur) + len(piece.rstrip()) > WIDTH and cur.strip() and len(cur) > indent:
            out.append(cur.rstrip())
            cur = " " * indent
        cur += piece
    out.append(cur.rstrip())
    return out


def loop_atoms(lp):
    if r := rect_args(lp):
        return [f"rect{r}"]
    pts = [pt(p) for p in lp]
    return ["[" + pts[0]] + pts[1:-1] + [pts[-1] + "]"]


def loops_atoms(loops):
    atoms = [a for lp in loops for a in loop_atoms(lp)]
    if not atoms:
        return ["[]"]
    atoms[0] = "[" + atoms[0]
    atoms[-1] += "]"
    return atoms


def flags_expr(flags):
    names = [n for b, n in FLAG_NAMES.items() if flags & b]
    rest = flags & ~sum(FLAG_NAMES)
    return " | ".join(names + ([str(rest)] if rest else [])) or "0"


def action_expr(a):
    return ACTION_NAMES.get(a, str(a))


def special_expr(sp: Special):
    args = [action_expr(sp.action), str(sp.tag), q(sp.texture) if sp.texture else None]
    n = 3 if sp.texture else 2 if sp.tag else 1 if sp.action else 0
    return f"Special({', '.join(args[:n])})"


def side_expr(s: SideOverride):
    parts = [f"{k}={q(v) if isinstance(v, str) else v}" for k, v in
             (("upper", s.upper), ("lower", s.lower), ("mid", s.mid), ("x", s.x), ("y", s.y)) if v is not None]
    return f"Side({', '.join(parts)})"


def line_expr(o: LineOverride):
    parts = []
    if o.action is not None:
        parts.append(f"action={action_expr(o.action)}")
    if o.tag is not None:
        parts.append(f"tag={o.tag}")
    if o.flags is not None:
        parts.append(f"flags={flags_expr(o.flags)}")
    if o.front:
        parts.append(f"front={side_expr(o.front)}")
    if o.back:
        parts.append(f"back={side_expr(o.back)}")
    return parts


def neighbour_sectors(lines):
    out = defaultdict(set)
    for l in lines:
        if l.back and not l.free:
            out[l.front.sector].add(l.back.sector)
            out[l.back.sector].add(l.front.sector)
    return out


def sector_expr(i, s, g: Guess, near, used):
    """The Sector(...) call, or a helper call that builds exactly the same sector."""
    f, name, loops, pillars = g.fields[i], g.names[i], g.loops[i], g.pillars[i]
    lower = f["lower"] or f["wall"]
    box = rect_args(loops[0]) if len(loops) == 1 and not pillars else None
    plain = s.special == 0 and f["action"] == 0
    if f["kind"] == DOOR and len(loops) == 1 and not pillars and s.ctex == "FLAT20" and s.ceil == s.floor \
            and s.special == 0 and lower == f["wall"] and f["face"]:
        used.add("door")
        kw = [(k, v, d) for k, v, d in (
            ("face", q(f["face"]), q("BIGDOOR2")), ("track", q(f["wall"]), q("DOORTRAK")),
            ("action", action_expr(f["action"]), action_expr(0 if s.tag else doom2.DR_DOOR)),
            ("tag", str(s.tag), "0"), ("light", str(s.light), "144"), ("floor", str(s.floor), "0"),
            ("flat", q(s.ftex), q("FLAT20")))]
        return "door", [q(name), *loop_atoms(loops[0])] + [f"{k}={v}" for k, v, d in kw if v != d]
    if f["kind"] == LIFT and box and plain and s.tag and not f["face"]:
        used.add("lift")
        args = [q(name), f"({', '.join(map(str, box))})", str(s.floor), str(s.ceil), str(s.tag), q(s.ctex),
                str(s.light), q(f["wall"])]
        args += [f"ftex={q(s.ftex)}"] * (s.ftex != "STEP1") + [f"side={q(lower)}"] * (lower != "PLAT1")
        return "lift", args
    if f["kind"] == ROOM and box and s.tag == 0 and f["action"] == 0 and s.light == 240 and lower == "METAL" \
            and s.special in (0, doom2.LIGHT_GLOW):
        used.add("pedestal")
        args = [q(name), f"({', '.join(map(str, box))})", str(s.floor), str(s.ceil), q(f["wall"]), q(s.ctex)]
        args += [f"flat={q(s.ftex)}"] * (s.ftex != "TLITE6_1") + ["glow=False"] * (s.special == 0)
        return "pedestal", args
    if f["kind"] == ROOM and box and plain and s.tag == 0 and len(near[i]) == 2 and \
            all(s.floor > o.floor and s.ceil < o.ceil for o in near[i]):
        used.add("window")
        args = [q(name), f"({', '.join(map(str, box))})", str(s.floor), str(s.ceil), q(f["wall"]), str(s.light)]
        args += [f"flat={q(s.ftex)}"] * (s.ftex != "FLAT5_4") + [f"ctex={q(s.ctex)}"] * (s.ctex != "CEIL5_1") \
            + [f"lower={q(lower)}"] * (lower != "METAL")
        return "window", args
    used.add("Sector")
    args = [q(name)] + loops_atoms(loops) + [str(s.floor), str(s.ceil), q(s.ftex), q(s.ctex), str(s.light),
                                             q(f["wall"])]
    if f["lower"]:
        args.append(f"lower={q(f['lower'])}")
    if f["face"]:
        args.append(f"face={q(f['face'])}")
    if s.special:
        args.append(f"special={SECTOR_NAMES.get(s.special, str(s.special))}")
    if s.tag:
        args.append(f"tag={s.tag}")
    if f["kind"] != ROOM:
        used.add(f["kind"].upper())
        args.append(f"kind={f['kind'].upper()}")
    if f["action"]:
        args.append(f"action={action_expr(f['action'])}")
    if pillars:
        p = loops_atoms(pillars)
        args += ["pillars=" + p[0]] + p[1:]
    return "Sector", args


def research_lines(slot, game):
    """Designers, reception and the measurements furthest outside the game's
    medians, from research/data/ when it's there."""
    out = []

    def rows(name):
        path = os.path.join(RESEARCH, name)
        if not os.path.exists(path):
            return {}
        with open(path, newline="") as f:
            return {r["map"]: r for r in csv.DictReader(f)}
    if d := rows("designers.csv").get(slot):
        out.append(f"Designers: {d['designers']}.")
    if r := rows("reception.csv").get(slot):
        out.append(f"Reception: {r['score']} ({r['tier']}).")
    metrics = defaultdict(dict)
    for name in ("metrics_space.csv", "metrics_combat.csv", "metrics_progression.csv"):
        for m, r in rows(name).items():
            metrics[m].update(r)
    if slot not in metrics:
        return out
    same = [r for m, r in metrics.items() if bool(re.fullmatch(r"E\dM\d", m)) == (game == "doom")]
    far = []
    for k, label in LABELS.items():
        vals = [float(r[k]) for r in same if r.get(k) not in (None, "")]
        if len(vals) < 4 or metrics[slot].get(k) in (None, ""):
            continue
        q1, med, q3 = statistics.quantiles(vals, n=4)
        v = float(metrics[slot][k])
        spread = (q3 - q1) or 1
        if v < q1 or v > q3:
            far.append(((q1 - v if v < q1 else v - q3) / spread, label, v, q1, med, q3))
    if far:
        out.append(f"Furthest outside the {'Ultimate Doom' if game == 'doom' else 'DOOM II'} medians [IQR]:")
        out += [f"    {label:<44} {fmt(v):>9}   {fmt(med)} [{fmt(q1)}-{fmt(q3)}]"
                for _, label, v, q1, med, q3 in sorted(far, reverse=True)[:5]]
    return out


def header(src, m, title, done, found, modname):
    monsters = [t for t in m.things if t.type in ACTORS and t.type not in PLAYERS and not t.flags & 16]
    per_skill = "/".join(str(sum(bool(t.flags & b) for t in monsters)) for b in (1, 2, 4))
    keys = sorted({THING_NAMES[t.type] for t in m.things if t.type in KEY_OF})
    secrets = sum(s.special == doom2.SECRET_AREA for s in m.sectors)
    lines = [f"{m.slot}: {title}" if title else m.slot, "",
             f"Decompiled from {os.path.basename(src.path)} {m.slot} by levels.decompile.",
             f"Monsters (e/m/h): {per_skill}. Keys: {', '.join(keys) or 'none'}. Secrets: {secrets}."]
    lines.append(f"Checks: {len(found.playability)} playability findings (KNOWN_ISSUES), "
                 f"{len(found.style)} style, {len(found.warnings)} warnings.")
    if done:
        lines.append(f"Repaired: {len(done)} edits (see the # repaired: comments).")
    if not src.pwad:
        lines += research_lines(m.slot, m.game)
    lines += ["", f"    python3 -m levels imported.{modname}"]
    return '"""' + "\n".join(lines) + '\n"""'


def module_text(src, m, g: Guess, lines, done, found, modname):
    used = set()
    near = defaultdict(list, {i: [m.sectors[o] for o in sorted(ns)] for i, ns in neighbour_sectors(lines).items()})
    secs = []
    for i, s in enumerate(m.sectors):
        fn, args = sector_expr(i, s, g, near, used)
        secs += wrap(f"    {fn}(", args, 4 + len(fn) + 1, "),")
    if any("rect(" in s for s in secs):
        used.add("rect")
    body = [f"MAP = {q(m.slot)}", f'WAD = "imported/{src.stem}.WAD"', "IMPORTED = True"]
    if g.x_offsets == "zero":
        body.append('X_OFFSETS = "zero"')
    if src.pwad:
        body.append(f"RESOURCES = [{q(src.resource)}]")
    if isinstance(info := src.umapinfo.get(m.slot), dict):
        body += wrap("UMAPINFO = {", [f"{q(k)}: {q(v)}" for k, v in info.items()], 12, "}")
    elif info:
        body.append(f'UMAPINFO = """{info}"""' if '"""' not in info and "\\" not in info and not info.endswith('"')
                    else f"UMAPINFO = {info!r}")
    body.append("")
    body += [f"# repaired: {d}" for _, d in done]
    body += ["SECTORS = ["] + secs + ["]"]

    def table(name, items, value):
        if not items:
            return []
        used.add("Special")
        out = ["", f"{name} = {{"]
        for k, v in items.items():
            out += wrap(f"    {value(k)}: ", [value(v)], 8, ",")
        return out + ["}"]
    body += table("SPECIAL_BETWEEN", g.special_between,
                  lambda x: f"({q(x[0])}, {q(x[1])})" if isinstance(x, tuple) else special_expr(x))
    for name, items in (("SPECIAL_WALLS", g.special_walls), ("FREE_LINES", g.free_lines)):
        body += table(name, items, lambda x: f"({pt(x[0])}, {pt(x[1])})" if isinstance(x, tuple) else special_expr(x))
    if g.secret_doors:
        if all(v == SECRET_HINT for v in g.secret_doors.values()):
            body += [""] + wrap("SECRET_DOORS = {", [q(n) for n in g.secret_doors], 16, "}")
        else:
            body += [""] + wrap("SECRET_DOORS = {", [f"{q(n)}: {pt(v)}" for n, v in g.secret_doors.items()], 16, "}")
    tuples = []
    for t in m.things:
        skills, extra = skills_of(t.flags)
        args = [THING_NAMES.get(t.type, str(t.type)), str(t.x), str(t.y), str(t.angle), q(skills), str(extra)]
        n = 6 if extra else 5 if skills != "emh" else 4 if t.angle else 3
        tuples.append(f"({', '.join(args[:n])})")
    used.add("Thing")
    body += ["", "# (type, x, y, angle=0, skills=\"emh\", extra=0)", "THINGS = [Thing(*t) for t in ["]
    body += wrap("    ", tuples, 4, ",") + ["]]"]
    body += ["", "OVERRIDES = {"]
    for (a, b), o in g.overrides.items():
        used.add("Line")
        used |= {"Side"} if o.front or o.back else set()
        used |= {FLAG_NAMES[k] for k in FLAG_NAMES if o.flags is not None and o.flags & k}
        body += wrap(f"    ({pt(a)}, {pt(b)}): Line(", line_expr(o), 8, "),")
    body += ["}", "", "KNOWN_ISSUES = ["]
    body += [f"    {q(f)}," for f in found.playability] + ["]"]
    # isort order: constants, classes, functions.
    names = sorted(used, key=lambda n: (not n.isupper(), not n[0].isupper(), n))
    imports = wrap("from ..model import (", names, 21, ")")
    return "\n".join([header(src, m, src.title(m.slot), done, found, modname),
                      "from ..doom2 import *  # noqa: F403 - thing types, actions, sector specials",
                      *imports, "", *body, ""])


# ----------------------------------------------------------------- driver ---


@dataclass
class Source:
    path: str
    stem: str        # upper case, e.g. "DOOM2", "NUKAGE"
    pwad: bool
    lumps: list
    umapinfo: dict   # {slot: UMAPINFO module value}

    @property
    def resource(self):
        """The path as RESOURCES gives it: relative to the repo root if inside it."""
        rel = os.path.relpath(os.path.abspath(self.path), ROOT)
        return os.path.abspath(self.path) if rel.startswith("..") else rel

    def title(self, slot):
        if not self.pwad:
            return TITLES.get(slot)
        info = self.umapinfo.get(slot, {})
        if isinstance(info, str):
            name = re.search(r'^\s*levelname\s*=\s*"([^"]*)"', info, re.MULTILINE | re.IGNORECASE)
            return name and name.group(1)
        return info.get("levelname")


@dataclass
class Result:
    modname: str
    map: object                  # wadmap.Map as read
    merged: list[Ln]             # its lines, split and merged
    text: str = ""
    overrides: int = 0
    done: list = field(default_factory=list)
    repaired: set = field(default_factory=set)          # sectors the repairs touch
    repaired_points: set = field(default_factory=set)   # vertices of the edited lines
    problems: list = field(default_factory=list)


def open_source(source):
    if source in IWADS:
        path = IWADS[source]
        if not path:
            sys.exit(f"{source}: its IWAD path is not set: add {'DOOM_WAD' if source == 'doom' else 'DOOM2_WAD'} "
                     "to .env (see .env.example)")
    else:
        path = source
    with open(path, "rb") as f:
        pwad = f.read(4) == b"PWAD"
    lumps = read_wad(path)
    return Source(path, os.path.splitext(os.path.basename(path))[0].upper(), pwad, lumps, umapinfo_entries(lumps))


_widths = {}


def widths_for(game, src):
    key = (game, src.path if src.pwad else None)
    if key not in _widths:
        _widths[key] = texture_widths(game, [src.path] if src.pwad else [])
    return _widths[key]


def decompile(src: Source, slot, parts) -> Result:
    """Decompile one map. Raises Refused."""
    if "TEXTMAP" in parts:
        raise Refused("UDMF map (TEXTMAP): only Doom-format maps decompile")
    if "BEHAVIOR" in parts:
        raise Refused("Hexen-format map (BEHAVIOR): only Doom-format maps decompile")
    game = "doom" if re.fullmatch(r"E\dM\d", slot) else "doom2"
    m = parse(game, slot, parts)
    widths = widths_for(game, src)
    res = Result(f"{src.stem.lower()}_{slot.lower()}", m, merge_lines(split_lines(read_map_lines(m)), widths))
    lines, res.done = repair(res.merged)
    res.repaired, res.repaired_points = repaired_at(res.done, res.merged)
    lines = merge_lines(lines, widths)
    by_ends = {frozenset((l.a, l.b)): l for l in lines}
    if len(by_ends) != len(lines):
        raise Refused("two lines join the same two vertices")
    things = [Thing(t.type, t.x, t.y, t.angle, *skills_of(t.flags)) for t in m.things]
    wad = f"imported/{src.stem}.WAD"
    resources = [src.resource] if src.pwad else []

    def build(g, overrides=None):
        level = level_of(m, g, wad, things, overrides, resources)
        try:
            compiled = compile_level(level)
        except LevelError as e:
            raise Refused(f"the builder can't make the decompiled geometry:\n{e}") from None
        return level, compiled, *matched(level, compiled, by_ends)

    def attempt(x_offsets):
        g = guess(m, lines, x_offsets)
        level, compiled, pairs, _ = build(g)
        vote_textures(g, level, compiled, pairs)
        special_walls(g, lines)
        choose_between(g, pairs)
        choose_secret_doors(g, lines)
        _, _, pairs, _ = build(g)
        secret_offsets(g, pairs)
        _, _, pairs, problems = build(g)
        g.overrides = overrides_of(pairs)
        return g, problems
    # X_OFFSETS "zero" only where it needs fewer overrides.
    g, res.problems = min((attempt(x) for x in ("continuous", "zero")), key=lambda gp: len(gp[0].overrides))
    res.overrides = len(g.overrides)
    level, compiled, pairs, _ = build(g, g.overrides)
    if leftover := overrides_of(pairs):
        res.problems.append(f"{len(leftover)} lines still differ with OVERRIDES applied")
    found = checks.findings(level, compiled)
    res.text = module_text(src, m, g, lines, res.done, found, res.modname)
    return res


def verify(src: Source, res: Result, path):
    """Rebuild the module without ZDBSP and compare it with the original map.
    Returns a list of differences, empty if it round-trips (lines through a
    vertex a repair edited may differ)."""
    spec = importlib.util.spec_from_file_location(f"levels.imported.{res.modname}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    level = load(module)
    compiled = compile_level(level)
    m = res.map
    rebuilt = parse(m.game, m.slot, dict(compiled.lumps[1:]))
    out = []
    if rebuilt.sectors != m.sectors:
        out.append(f"sectors differ: {sum(a != b for a, b in zip(rebuilt.sectors, m.sectors))} of {len(m.sectors)}"
                   + (f", {len(rebuilt.sectors)} built" if len(rebuilt.sectors) != len(m.sectors) else ""))
    if rebuilt.things != m.things:
        out.append("things differ")
    widths = widths_for(m.game, src)
    a = Counter(l.key() for l in res.merged)
    b = Counter(l.key() for l in merge_lines(split_lines(read_map_lines(rebuilt)), widths))
    for (key, n), sign in [(kv, "-") for kv in (a - b).items()] + [(kv, "+") for kv in (b - a).items()]:
        if any(p in key[:2] or on_segment(p, *key[:2]) for p in res.repaired_points):
            continue
        out.append(f"{sign} line {key[0]}-{key[1]} flags {key[2]} action {key[3]} tag {key[4]} "
                   f"front {key[5]} back {key[6]}" + (f" x{n}" if n > 1 else ""))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m levels.decompile",
                                     description="Decompile Doom-format maps into level modules.")
    parser.add_argument("source", help="a WAD path, or doom / doom2 for the IWADs in .env")
    parser.add_argument("maps", nargs="*", metavar="MAP", help="map slots, e.g. E1M1 MAP01 (default: every map)")
    parser.add_argument("--verify", action="store_true",
                        help="rebuild each module without ZDBSP and compare it with the original")
    parser.add_argument("--out", default=OUT, metavar="DIR", help="where modules go (default: levels/imported)")
    args = parser.parse_args(argv)
    src = open_source(args.source)
    entries = dict(map_entries(src.lumps))
    slots = [s.upper() for s in args.maps] or list(entries)
    if missing := [s for s in slots if s not in entries]:
        sys.exit(f"{src.path} has no map {', '.join(missing)}")
    os.makedirs(args.out, exist_ok=True)
    init = os.path.join(args.out, "__init__.py")
    if not os.path.exists(init):
        with open(init, "w") as f:
            f.write('"""Decompiled maps, written by levels.decompile (gitignored)."""\n')
    failed = False
    if args.verify:
        print(f"{'map':<6} {'sectors':>7} {'lines':>6} {'overrides':>9} {'repaired':>8}  result")
    for slot in slots:
        try:
            res = decompile(src, slot, entries[slot])
        except Refused as e:
            failed = True
            print(f"{slot:<6} refused: " + str(e).replace("\n", "\n       "))
            continue
        path = os.path.join(args.out, res.modname + ".py")
        with open(path, "w") as f:
            f.write(res.text)
        for p in res.problems:
            print(f"{slot}: warning: {p}")
        if not args.verify:
            print(f"wrote {os.path.relpath(path)}: {len(res.map.sectors)} sectors, {len(res.merged)} lines, "
                  f"{res.overrides} overrides" + (f", {len(res.done)} repairs" if res.done else ""))
            continue
        diffs = verify(src, res, path)
        failed |= bool(diffs)
        result = "ok" if not diffs else f"MISMATCH ({len(diffs)})"
        print(f"{slot:<6} {len(res.map.sectors):>7} {len(res.merged):>6} {res.overrides:>9} "
              f"{len(res.repaired):>8}  {result}")
        for d in diffs[:20]:
            print("       " + d)
        for _, d in res.done:
            print("       repaired: " + d)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
