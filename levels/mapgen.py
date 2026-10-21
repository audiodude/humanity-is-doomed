"""Builds DOOM-format WADs from level modules.

A level module is plain data, read as module attributes:

    MAP             map slot, e.g. "MAP01"
    WAD             output file name, written to wads/
    SECTORS         list[Sector]; list order is the SECTORS lump order
    THINGS          list[Thing]; needs a PLAYER1 start
    SPECIAL_BETWEEN {(sector_name, sector_name): Special} for every line two
                    sectors share (pair order doesn't matter)       [optional]
    SPECIAL_WALLS   {(point, point): Special} for one-sided wall segments,
                    keyed by exact endpoints, e.g. switches          [optional]
    SECRET_DOORS    door sector names drawn as plain wall on the automap,
                    faces shifted by model.SECRET_HINT as a visual clue;
                    or {name: (x, y)} to pick offsets, (0, 0) = seamless
                                                                     [optional]
    MUST_REACH      sector names the progression check must reach    [optional]
    UMAPINFO        {key: value} for the UMAPINFO lump               [optional]

The dataclasses and shape helpers (doorway, stairs, lift) are in model.
Sectors are polygons: an outer loop, holes that other sectors fill, and
solid pillars. Edges two sectors share become two-sided linedefs; the rest
become walls. Doors get their Sector.action on every line into them, and
lifts get SR_LIFT from below and WR_LIFT from above, unless SPECIAL_BETWEEN
says otherwise.

Textures are placed so walls read as continuous: x offsets run along each
sector's outline, and the wall above or below an opening uses the room's own
texture pegged like the rest of that wall. Pictures (switches, door faces)
start at offset 0.

build() writes an SVG preview, prints a balance report, validates thing
placement, progression (derived from keys, door specials and tagged
triggers) and texture fit, then runs ZDBSP (bundled with Ultimate Doom
Builder) for nodes, blockmap and reject. Several level modules can share a
WAD: build() replaces only its own map slot and UMAPINFO entry.
"""
import os
import subprocess
import tempfile

from .checks import balance_report, check_progression, check_textures, check_things
from .doom2 import ACTORS, FLOOR_LOWERERS, PLAYERS, SR_LIFT, WR_LIFT, is_decal
from .model import (ALL, DOOR, LIFT, ML_BLOCKING, ML_DONTPEGBOTTOM, ML_DONTPEGTOP, ML_SECRET,
                    ML_TWOSIDED, NO_TEX, ROOM, SKY, LevelError, Linedef, Sidedef, dist, edges,
                    floor_range, load, on_segment, oriented)
from .preview import write_svg
from .wad import (IWAD, iwad_textures, map_lumps, read_wad, replace_map, umapinfo_lump,
                  write_wad)

ZDBSP = "/usr/lib/ultimate-doom-builder/Compilers/Nodebuilders/zdbsp"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_lines(level):
    """Split every sector edge at vertices lying on it, then pair opposite
    directed edges into two-sided lines; unpaired edges become walls."""
    verts = sorted({p for s in level.sectors.values() for loop in s.loops + s.pillars for p in loop})
    directed = {}   # (a, b) -> (sector on its right, loop role, distance along the loop at a)
    for sec in level.sectors.values():
        for loop, role in oriented(sec):
            pos = 0.0
            for a, b in edges(loop):
                mids = sorted((p for p in verts if on_segment(p, a, b)), key=lambda p: dist(a, p))
                chain = [a] + mids + [b]
                for u, v in zip(chain, chain[1:]):
                    if (u, v) in directed:
                        raise LevelError(f"overlap: edge {u}->{v} in {directed[(u, v)][0].name} and {sec.name}")
                    directed[(u, v)] = (sec, role, pos)
                    pos += dist(u, v)
    lines, seen, problems = [], set(), {}
    for (a, b), (s, role, pos) in directed.items():
        if (a, b) in seen:
            continue
        seen.add((a, b))
        if (b, a) not in directed:
            if role.startswith("hole"):
                problems[(s.name, role)] = f"{s.name}: {role} at {a} has no sector in it; add one or move it to pillars"
            lines.append(Linedef(a, b, s, None, front_x=pos))
            continue
        seen.add((b, a))
        t, trole, tpos = directed[(b, a)]
        if t is s:
            raise LevelError(f"sector {s.name} borders itself at {a}-{b}")
        for sec, r, o in ((s, role, t), (t, trole, s)):
            if r.startswith("pillar"):
                problems[(sec.name, r)] = f"{sec.name}: {r} at {a} touches sector {o.name}; pillars must be solid"
        # Doors, lifts and other movers go on the back side.
        if s.kind != ROOM and t.kind == ROOM:
            lines.append(Linedef(b, a, t, s, front_x=tpos, back_x=pos))
        else:
            lines.append(Linedef(a, b, s, t, front_x=pos, back_x=tpos))
    if problems:
        raise LevelError("\n".join(problems.values()))
    return lines


def assign_specials(level, lines):
    used_walls = set()
    for l in lines:
        if l.back is None:
            l.flags |= ML_BLOCKING
            key = (l.v1, l.v2)
            if key not in level.special_walls:
                key = key[::-1]
            if key in level.special_walls:
                sp = level.special_walls[key]
                l.action, l.tag, l.texture = sp.action, sp.tag, sp.texture
                used_walls.add(key)
            if l.front.kind == DOOR:
                l.flags |= ML_DONTPEGBOTTOM   # door track stays put while the door moves
        else:
            l.flags |= ML_TWOSIDED
            f, b = l.front, l.back
            sp = level.special_between.get((f.name, b.name)) or level.special_between.get((b.name, f.name))
            if sp:
                l.action, l.tag = sp.action, sp.tag
            elif f.action or b.action:
                l.action = b.action or f.action
            elif LIFT in (f.kind, b.kind) and f.kind != b.kind:
                lft, nb = (b, f) if b.kind == LIFT else (f, b)
                if not lft.tag:
                    raise LevelError(f"lift {lft.name} needs a tag")
                l.action, l.tag = (WR_LIFT if nb.floor >= lft.floor else SR_LIFT), lft.tag
        if l.front.name in level.secret_doors or (l.back and l.back.name in level.secret_doors):
            # Shown as a plain wall on the map; the face is pegged like the wall it
            # hides in, so only the level's hint offset makes it stand out.
            l.flags |= ML_SECRET | (ML_DONTPEGTOP if l.back else 0)
    if missing := set(level.special_walls) - used_walls:
        raise LevelError(f"special walls not found: {missing}")
    for pair in level.special_between:
        if not any(l.back and {l.front.name, l.back.name} == set(pair) for l in lines):
            raise LevelError(f"no shared edge between {pair}")


def x_offset(pos, *textures):
    """Texture x offset continuing the wall pattern; pictures start at 0.
    2048 is a multiple of every power-of-two texture width."""
    return 0 if any(is_decal(t) for t in textures) else round(pos) % 2048


def line_sides(l: Linedef, secret_doors, ranges) -> list[Sidedef]:
    """Pick textures for the line's sides, and set its pegging flags so the
    wall above or below an opening lines up with the rest of the wall.
    ranges: {sector: (lowest floor, highest floor)}; a side gets a lower
    texture whenever the other sector's floor can be above its own."""
    if l.back is None:
        tex = l.texture or l.front.wall
        return [Sidedef(NO_TEX, NO_TEX, tex, l.front, x_offset(l.front_x, tex))]
    sides = []
    for me, other, pos in ((l.front, l.back, l.front_x), (l.back, l.front, l.back_x)):
        up = lo = NO_TEX
        dx = dy = 0
        if other.kind == DOOR:
            up = other.face
            dx, dy = secret_doors.get(other.name, (0, 0))
        elif other.ceil < me.ceil and not (me.ctex == SKY and other.ctex == SKY):
            up = me.wall
            l.flags |= ML_DONTPEGTOP
        moving = LIFT in (me.kind, other.kind)
        if ranges[other][1] > ranges[me][0] or moving:
            lo = other.lower
            if lo == me.wall and not moving:
                l.flags |= ML_DONTPEGBOTTOM
        sides.append(Sidedef(up, lo, NO_TEX, me, x_offset(pos, up, lo) + dx, dy))
    return sides


def build(module, check_only=False, out=None):
    """Validate a level module and write its map into its WAD (default
    wads/<WAD>), keeping any other maps already there, plus an SVG preview
    wads/<WAD stem>-<MAP>.svg. The preview is written first, even when checks
    fail or check_only is set. Returns the WAD path, or None with check_only.
    Raises LevelError."""
    level = load(module)
    out = out or os.path.join(ROOT, "wads", level.wad)
    lines = build_lines(level)
    assign_specials(level, lines)
    lowered = {l.tag for l in lines if l.tag and l.action in FLOOR_LOWERERS}
    ranges = {s: floor_range(s, lines, lowered) for s in level.sectors.values()}
    sides = [line_sides(l, level.secret_doors, ranges) for l in lines]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    svg = f"{os.path.splitext(out)[0]}-{level.map}.svg"
    write_svg(level, lines, svg)
    monsters = [t for t in level.things if t.type in ACTORS and t.type not in PLAYERS]
    print(f"{level.name}: {len(level.sectors)} sectors, {len(lines)} linedefs, "
          f"{sum(map(len, sides))} sidedefs, {len(level.things)} things; monsters "
          + "/".join(str(sum(sk in t.skills for t in monsters)) for sk in ALL) + " (e/m/h)")
    print("preview:", svg)
    print("\n".join(balance_report(level)))
    errors = check_things(level, lines) + check_progression(level, lines)
    iwad = iwad_textures()
    if iwad is None:
        print(f"warning: {IWAD} not found (set DOOM2_WAD); skipping texture checks")
    else:
        tex_errors, tex_warnings = check_textures(level, lines, sides, iwad)
        errors += tex_errors
        for w in tex_warnings:
            print("warning:", w)
    if errors:
        raise LevelError("\n".join(errors))
    if check_only:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "raw.wad")
        built = os.path.join(tmp, "built.wad")
        write_wad(raw, map_lumps(level, lines, sides))
        subprocess.run([ZDBSP, "-R", "-w", "-t", "-o", built, raw], check=True, stdout=subprocess.DEVNULL)
        lumps = read_wad(built)
    existing = read_wad(out) if os.path.exists(out) else []
    info = umapinfo_lump(level) if level.umapinfo else None
    write_wad(out, replace_map(existing, level.map, lumps, info))
    print("wrote", out)
    return out
