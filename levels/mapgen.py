"""Builds DOOM-format WADs from level modules.

A level module is plain data, read as module attributes:

    MAP             map slot, e.g. "MAP01"; ExMy is a DOOM map, MAPxx DOOM II
                    (level.game), which picks the IWAD the checks use
    WAD             output file name, written to wads/; may name a
                    subdirectory, e.g. "imported/DOOM2.WAD"
    SECTORS         list[Sector]; list order is the SECTORS lump order
    THINGS          list[Thing]; needs a PLAYER1 start. Thing.skills: e/m/h,
                    a (ambush), n (multiplayer only); Thing.extra: other
                    flag bits
    SPECIAL_BETWEEN {(sector_name, sector_name): Special} for every line two
                    sectors share; the lines face the first sector, which
                    matters for teleports. A Special.texture hangs bars or a
                    grate in those lines and makes them impassable [optional]
    SPECIAL_WALLS   {(point, point): Special} for one-sided wall segments,
                    keyed by exact endpoints, e.g. switches          [optional]
    FREE_LINES      {(point, point): Special} for lines standing inside a
                    sector, not on its edge: walk-over triggers, or with a
                    texture an impassable fence. The front is on the right
                    going from the first point to the second         [optional]
    SECRET_DOORS    door sector names drawn as plain wall on the automap,
                    faces shifted by model.SECRET_HINT as a visual clue;
                    or {name: (x, y)} to pick offsets, (0, 0) = seamless
                                                                     [optional]
    MUST_REACH      sector names the progression check must reach    [optional]
    UMAPINFO        {key: value} for the map's UMAPINFO entry, values
                    written quoted; or a string, the entry's body between
                    the braces written as it is (decompiled maps whose entry
                    has repeated keys or unquoted values)             [optional]
    OVERRIDES       {(point, point): model.Line} changing a built line, keyed
                    by its exact endpoints after edges are split at vertices,
                    sector edges and free lines alike. The front is on the
                    right going from the first point to the second; a
                    two-sided line built the other way is flipped, a wall
                    must be keyed the way it was built. A Line/Side field that
                    isn't None replaces the builder's value (flags: the whole
                    word). Applied last; a key matching no line, or back= on
                    a one-sided line, is an error                    [optional]
    IMPORTED        True for decompiled maps                         [optional]
    KNOWN_ISSUES    playability findings and warnings it accepts     [optional]
    RESOURCES       PWAD paths (absolute, ~, or relative to the repo root)
                    whose textures, flats and patches the checks load after
                    the IWAD; not copied into the WAD                [optional]
    X_OFFSETS       "continuous" (default): x offsets run along each sector's
                    outline; "zero": every x offset is 0 (secret door hints
                    and OVERRIDES still apply). Decompiled maps use "zero"
                    when it needs fewer overrides                    [optional]

The dataclasses and shape helpers (doorway, stairs, lift) are in model.
Sectors are polygons: loops and solid pillars. A loop inside an even number
of the sector's other loops and pillars is an outer loop (a sector may have
several), an odd number a hole that other sectors fill; a hole's edges with
no sector across are walls. A sector standing free inside another is cut
out of it automatically. Edges two sectors share become two-sided linedefs;
the rest become walls. Doors get their Sector.action on every line into
them, and lifts get SR_LIFT on lines from every neighbour, facing the
neighbour (vanilla uses a line only from its front); a walk_on lift gets
WR_LIFT from neighbours at its top instead. SPECIAL_BETWEEN overrides both.

Textures are placed so walls read as continuous: x offsets run along each
sector's outline (unless X_OFFSETS is "zero"), and the wall above or below an
opening uses the room's own texture pegged like the rest of that wall.
Pictures (switches, door faces) start at offset 0.

compile_level() builds a level's lines, sides and map lumps. build() writes
an SVG preview, prints a balance report, runs checks.findings (thing
placement, progression and kills by the reach model over every vanilla line
action, texture fit against the map's game's IWAD): playability findings
not in KNOWN_ISSUES fail the build, style findings too unless IMPORTED. Then
it prints the measurements and runs ZDBSP (by default the copy bundled with
Ultimate Doom Builder) for nodes, blockmap and reject. Several level modules
can share a WAD: build() replaces only its own map slot and UMAPINFO entry.
"""
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass

from .checks import balance_report, findings, level_textures
from .doom2 import ACTORS, PLAYERS, SR_LIFT, WR_LIFT, is_decal
from .model import (ALL, DOOR, LIFT, ML_BLOCKING, ML_DONTPEGBOTTOM, ML_DONTPEGTOP, ML_SECRET,
                    ML_TWOSIDED, NO_TEX, ROOM, ROOT, SKY, LevelError, Linedef, Sidedef, dist, edges,
                    floor_movers, floor_range, load, on_segment, oriented, sector_at)
from .measure import measure
from .preview import write_svg
from .wad import map_lumps, read_wad, replace_map, umapinfo_lump, write_wad

UDB_ZDBSP = "/usr/lib/ultimate-doom-builder/Compilers/Nodebuilders/zdbsp"


def find_zdbsp(path=None):
    """The ZDBSP executable to run: path if given, else the copy bundled with
    Ultimate Doom Builder, else zdbsp on PATH. Raises LevelError if there's none."""
    found = shutil.which(os.path.expanduser(path)) if path else shutil.which(UDB_ZDBSP) or shutil.which("zdbsp")
    if not found:
        raise LevelError(f"ZDBSP not found: {path} is not an executable" if path else
                         f"ZDBSP not found at {UDB_ZDBSP} or on PATH; install it or pass --zdbsp-path")
    return found


def build_lines(level):
    """Split every sector edge at vertices lying on it, then pair opposite
    directed edges into two-sided lines; unpaired edges become walls (a hole
    must touch another sector somewhere). Free lines are split the same way
    and each piece belongs to the sector it stands in. Lines should only meet
    at shared vertices; the checks report lines that cross (model.crossings)."""
    verts = sorted({p for s in level.sectors.values() for loop in s.loops + s.pillars for p in loop}
                   | {p for pq in level.free_lines for p in pq})
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
    lines, seen, problems, open_holes, filled = [], set(), {}, {}, set()
    for (a, b), (s, role, pos) in directed.items():
        if (a, b) in seen:
            continue
        seen.add((a, b))
        if (b, a) not in directed:
            if role.startswith("hole"):
                open_holes[(s.name, role)] = f"{s.name}: {role} at {a} has no sector in it; add one or move it to pillars"
            lines.append(Linedef(a, b, s, None, front_x=pos))
            continue
        seen.add((b, a))
        t, trole, tpos = directed[(b, a)]
        filled |= {(s.name, role), (t.name, trole)}
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
    problems.update((k, msg) for k, msg in open_holes.items() if k not in filled)
    for (p, q), sp in level.free_lines.items():
        if p == q:
            problems[(p, q)] = f"free line {p}-{q} has no length"
            continue
        chain = [p] + sorted((v for v in verts if on_segment(v, p, q)), key=lambda v: dist(p, v)) + [q]
        for u, v in zip(chain, chain[1:]):
            mid = ((u[0] + v[0]) / 2, (u[1] + v[1]) / 2)
            if (u, v) in directed or (v, u) in directed:
                problems[(p, q)] = f"free line {p}-{q} runs along a sector edge at {u}-{v}"
            elif any({l.v1, l.v2} == {u, v} for l in lines):
                problems[(p, q)] = f"free line {p}-{q} overlaps another free line at {u}-{v}"
            elif (sec := sector_at(level, mid)) is None:
                problems[(p, q)] = f"free line {p}-{q} is in the void at {u}-{v}"
            else:
                lines.append(Linedef(u, v, sec, sec, action=sp.action, tag=sp.tag, texture=sp.texture))
    if problems:
        raise LevelError("\n".join(problems.values()))
    return lines


def face(l: Linedef, v1):
    """Flip l so it starts at v1 (its front is then on the other side)."""
    if l.v1 != v1:
        l.v1, l.v2, l.front, l.back = l.v2, l.v1, l.back, l.front
        l.front_x, l.back_x = l.back_x, l.front_x


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
            if f is b:
                pass   # free-standing: action, tag and texture came from FREE_LINES
            elif sp := level.special_between.get((f.name, b.name)):
                l.action, l.tag, l.texture = sp.action, sp.tag, sp.texture
            elif sp := level.special_between.get((b.name, f.name)):
                l.action, l.tag, l.texture = sp.action, sp.tag, sp.texture
                face(l, l.v2)
            elif f.action or b.action:
                l.action = b.action or f.action
            elif LIFT in (f.kind, b.kind) and f.kind != b.kind:
                lft, nb = (b, f) if b.kind == LIFT else (f, b)
                if not lft.tag:
                    raise LevelError(f"lift {lft.name} needs a tag")
                walk = lft.walk_on and nb.floor >= lft.floor
                l.action, l.tag = (WR_LIFT if walk else SR_LIFT), lft.tag
                if not walk and l.front is not nb:
                    face(l, l.v2)   # vanilla uses a line only from its front: face where the player stands
            if l.texture:
                l.flags |= ML_BLOCKING | ML_DONTPEGBOTTOM   # bars or fence, standing on the floor
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


def line_sides(l: Linedef, secret_doors, ranges, x_offsets) -> list[Sidedef]:
    """Pick textures for the line's sides, and set its pegging flags so the
    wall above or below an opening lines up with the rest of the wall.
    ranges: {sector: (lowest floor, highest floor)}; a side gets a lower
    texture whenever the other sector's floor can be above its own.
    x_offsets: "continuous" runs x offsets along the sector's outline,
    "zero" leaves them 0."""
    front_x, back_x = (l.front_x, l.back_x) if x_offsets == "continuous" else (0, 0)
    if l.back is None:
        tex = l.texture or l.front.wall
        return [Sidedef(NO_TEX, NO_TEX, tex, l.front, x_offset(front_x, tex))]
    mid = l.texture or NO_TEX
    if l.front is l.back:
        return [Sidedef(NO_TEX, NO_TEX, mid, l.front), Sidedef(NO_TEX, NO_TEX, mid, l.front)]
    sides = []
    for me, other, pos in ((l.front, l.back, front_x), (l.back, l.front, back_x)):
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
        sides.append(Sidedef(up, lo, mid, me, x_offset(pos, up, lo, mid) + dx, dy))
    return sides


def apply_overrides(level, lines, sides):
    """Apply OVERRIDES (see model.Line) to the built lines and their sides,
    flipping a two-sided line first if it was built the other way round. A
    one-sided wall can't be flipped (it would face the void): its key must
    run the way it was built."""
    at = {(l.v1, l.v2): i for i, l in enumerate(lines)}
    problems, done = [], {}
    for (p, q), ov in level.overrides.items():
        i = at.get((p, q))
        if i is None and (i := at.get((q, p))) is not None:
            l = lines[i]
            if l.back is None:
                problems.append(f"override {p}-{q} runs against one-sided wall {q}-{p}; key it {q}-{p}")
                continue
            l.v1, l.v2 = l.v2, l.v1
            l.front, l.back, l.front_x, l.back_x = l.back, l.front, l.back_x, l.front_x
            sides[i].reverse()
            at[(p, q)] = at.pop((q, p))
        if i is None:
            problems.append(f"override {p}-{q} matches no line")
            continue
        if i in done:
            problems.append(f"overrides {done[i]} and {p}-{q} are the same line")
        done[i] = f"{p}-{q}"
        l = lines[i]
        for name in ("action", "tag", "flags"):
            if getattr(ov, name) is not None:
                setattr(l, name, getattr(ov, name))
        for k, s in enumerate((ov.front, ov.back)):
            if s is None:
                continue
            if k >= len(sides[i]):
                problems.append(f"override {p}-{q} sets back= on a one-sided line")
                continue
            for name, attr in (("upper", "upper"), ("lower", "lower"), ("mid", "mid"), ("x", "x_offset"),
                               ("y", "y_offset")):
                if getattr(s, name) is not None:
                    setattr(sides[i][k], attr, getattr(s, name))
    if problems:
        raise LevelError("\n".join(problems))


@dataclass
class Compiled:
    """A level's built lines, each line's sides, and its map lumps (no nodes)."""
    lines: list[Linedef]
    sides: list[list[Sidedef]]
    lumps: list[tuple[str, bytes]]


def compile_level(level) -> Compiled:
    """Build the level's lines, specials and sides, apply its OVERRIDES, and
    pack its map lumps. Raises LevelError."""
    lines = build_lines(level)
    assign_specials(level, lines)
    movers = floor_movers(lines)
    ranges = {s: floor_range(s, lines, movers) for s in level.sectors.values()}
    sides = [line_sides(l, level.secret_doors, ranges, level.x_offsets) for l in lines]
    apply_overrides(level, lines, sides)
    return Compiled(lines, sides, map_lumps(level, lines, sides))


def build(module, check_only=False, out=None, zdbsp=None):
    """Validate a level module and write its map into its WAD (default
    wads/<WAD>), keeping any other maps already there, plus an SVG preview
    wads/<WAD stem>-<MAP>.svg. The preview is written first, even when checks
    fail or check_only is set. zdbsp is the node builder executable (default:
    see find_zdbsp). Returns the WAD path, or None with check_only. Raises
    LevelError."""
    level = load(module)
    out = out or os.path.join(ROOT, "wads", level.wad)
    compiled = compile_level(level)
    lines, sides, lumps = compiled.lines, compiled.sides, compiled.lumps
    os.makedirs(os.path.dirname(out), exist_ok=True)
    svg = f"{os.path.splitext(out)[0]}-{level.map}.svg"
    write_svg(level, lines, svg)
    monsters = [t for t in level.things if t.type in ACTORS and t.type not in PLAYERS and "n" not in t.skills]
    print(f"{level.name}: {len(level.sectors)} sectors, {len(lines)} linedefs, "
          f"{sum(map(len, sides))} sidedefs, {len(level.things)} things; monsters "
          + "/".join(str(sum(sk in t.skills for t in monsters)) for sk in ALL) + " (e/m/h)")
    print("preview:", svg)
    print("\n".join(balance_report(level)))
    found = findings(level, compiled)
    known = set(level.known_issues)
    errors = [f for f in found.playability if f not in known]
    if level.imported:
        found.warnings = found.style + found.warnings
    else:
        errors += found.style
    for w in found.warnings:
        if w not in known:
            print("warning:", w)
    if errors:
        raise LevelError("\n".join(errors))
    seen = set(found.playability) | set(found.warnings)
    if found.reach and level_textures(level) is not None:
        report, warnings = measure(level, lines, found)
        print("\n".join(report + [f"warning: {w}" for w in warnings if w not in known]))
        seen |= set(warnings)
    for issue in level.known_issues:
        if issue not in seen:
            print("fixed:", issue)
    if check_only:
        return None
    zdbsp = find_zdbsp(zdbsp)
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "raw.wad")
        built = os.path.join(tmp, "built.wad")
        write_wad(raw, lumps)
        subprocess.run([zdbsp, "-R", "-w", "-t", "-o", built, raw], check=True, stdout=subprocess.DEVNULL)
        lumps = read_wad(built)
    existing = read_wad(out) if os.path.exists(out) else []
    info = umapinfo_lump(level) if level.umapinfo else None
    write_wad(out, replace_map(existing, level.map, lumps, info))
    print("wrote", out)
    return out
