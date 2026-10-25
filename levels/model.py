"""Level data model: the dataclasses level modules are written in, geometry
primitives, and shape helpers (doorway, stairs, lift)."""
from dataclasses import dataclass, field

from .doom2 import DR_DOOR, FLOOR_LOWERERS, FLOOR_RAISERS, LIGHT_GLOW, SECRET_AREA

Point = tuple[int, int]
Loop = list[Point]

ROOM, DOOR, LIFT = "room", "door", "lift"
SKY = "F_SKY1"
NO_TEX = "-"

# Linedef flags.
ML_BLOCKING, ML_TWOSIDED, ML_DONTPEGTOP, ML_DONTPEGBOTTOM, ML_SECRET = 1, 4, 8, 16, 32


class LevelError(Exception):
    """The level data is inconsistent; the message lists every problem."""


@dataclass(eq=False)   # identity hashing: sectors are used as dict keys
class Sector:
    """loops[0] is the outer boundary; loops[1:] are holes that other sectors
    fill exactly. pillars are holes left solid. lower: texture this sector
    shows on neighbours' lower parts (step risers, crate and lift sides),
    default wall. face: a door's face texture. action: line action put on
    every line this sector shares with another, unless SPECIAL_BETWEEN
    overrides it (doors use this)."""
    name: str
    loops: list[Loop]
    floor: int
    ceil: int
    ftex: str
    ctex: str
    light: int
    wall: str
    lower: str | None = None
    face: str | None = None
    special: int = 0
    tag: int = 0
    kind: str = ROOM
    action: int = 0
    pillars: list[Loop] = field(default_factory=list)

    def __post_init__(self):
        self.lower = self.lower or self.wall

    def contains(self, p: Point) -> bool:
        outer, *holes = self.loops
        return point_in_loop(p, outer) and not any(point_in_loop(p, h) for h in holes + self.pillars)


@dataclass(frozen=True)
class Special:
    action: int = 0
    tag: int = 0
    # Middle texture. On a one-sided wall: the switch picture. On a two-sided
    # line (SPECIAL_BETWEEN, FREE_LINES): bars, a grate or a fence hung in the
    # opening, standing on the floor; the line becomes impassable.
    texture: str | None = None


SKILL_BITS = {"e": 1, "m": 2, "h": 4}
ALL = "emh"


@dataclass(frozen=True)
class Thing:
    type: int
    x: int
    y: int
    angle: int = 0
    skills: str = ALL   # any of e/m/h; "a" adds the ambush (deaf) flag

    @property
    def flags(self) -> int:
        return sum(SKILL_BITS[c] for c in self.skills if c in SKILL_BITS) | (8 if "a" in self.skills else 0)


@dataclass
class Linedef:
    v1: Point
    v2: Point
    front: Sector
    back: Sector | None   # None: one-sided wall; front itself: a free-standing line inside front
    flags: int = 0
    action: int = 0
    tag: int = 0
    texture: str | None = None   # middle texture (see Special.texture)
    front_x: float = 0   # distance along the front/back sector's loop: texture x offset
    back_x: float = 0

    @property
    def length(self) -> float:
        (x1, y1), (x2, y2) = self.v1, self.v2
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def touches(self, s: Sector) -> bool:
        return s is self.front or s is self.back

    def other(self, s: Sector) -> Sector | None:
        return self.back if s is self.front else self.front


@dataclass
class Sidedef:
    upper: str
    lower: str
    mid: str
    sector: Sector
    x_offset: int = 0
    y_offset: int = 0


@dataclass
class Level:
    name: str
    map: str
    wad: str
    sectors: dict[str, Sector]
    things: list[Thing]
    special_between: dict[tuple[str, str], Special]
    special_walls: dict[tuple[Point, Point], Special]
    free_lines: dict[tuple[Point, Point], Special]
    secret_doors: dict[str, tuple[int, int]]
    must_reach: list[str]
    umapinfo: dict[str, str]


def load(module) -> Level:
    sectors = {}
    for s in module.SECTORS:
        if s.name in sectors:
            raise LevelError(f"duplicate sector name {s.name}")
        sectors[s.name] = s
    level = Level(
        name=getattr(module, "__name__", repr(module)),
        map=module.MAP,
        wad=module.WAD,
        sectors=sectors,
        things=list(module.THINGS),
        special_between=dict(getattr(module, "SPECIAL_BETWEEN", {})),
        special_walls=dict(getattr(module, "SPECIAL_WALLS", {})),
        free_lines=dict(getattr(module, "FREE_LINES", {})),
        secret_doors=secret_door_offsets(getattr(module, "SECRET_DOORS", ())),
        must_reach=list(getattr(module, "MUST_REACH", ())),
        umapinfo=dict(getattr(module, "UMAPINFO", {})),
    )
    named = {n for pair in level.special_between for n in pair} | set(level.secret_doors) | set(level.must_reach)
    if unknown := named - sectors.keys():
        raise LevelError(f"unknown sector names: {sorted(unknown)}")
    return level


# Secret doors' faces are shifted off the surrounding wall pattern by this much,
# the classic visual clue that a wall opens.
SECRET_HINT = (16, 8)


def secret_door_offsets(doors) -> dict[str, tuple[int, int]]:
    """SECRET_DOORS is a collection of door sector names, which all get
    SECRET_HINT, or a {name: (x, y)} dict to choose offsets per door;
    (0, 0) hides a door seamlessly."""
    return dict(doors) if isinstance(doors, dict) else {name: SECRET_HINT for name in doors}

# ------------------------------------------------------------- geometry ---


def edges(loop):
    return zip(loop, loop[1:] + loop[:1])


def dist(a: Point, b: Point) -> float:
    return ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5


def area2(loop):
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in edges(loop))


def oriented(sec):
    """[(loop, role)], role "outer", "hole N" or "pillar N". The outer loop
    runs clockwise and holes counter-clockwise, so the sector is always on
    the right of each directed edge, matching Doom front-sidedef rules."""
    out = []
    roles = ["outer"] + [f"hole {i}" for i in range(1, len(sec.loops))] + \
        [f"pillar {i}" for i in range(len(sec.pillars))]
    for loop, role in zip(sec.loops + sec.pillars, roles):
        a = area2(loop)
        if (role == "outer" and a > 0) or (role != "outer" and a < 0):
            loop = loop[::-1]
        out.append((loop, role))
    return out


def on_segment(p, a, b):
    """p lies strictly between a and b."""
    (px, py), (ax, ay), (bx, by) = p, a, b
    if (bx - ax) * (py - ay) != (by - ay) * (px - ax):
        return False
    return min(ax, bx) <= px <= max(ax, bx) and min(ay, by) <= py <= max(ay, by) and p not in (a, b)


def point_in_loop(p, loop):
    x, y = p
    inside = False
    for (x1, y1), (x2, y2) in edges(loop):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def cross(o, a, b) -> int:
    """z of (a - o) x (b - o): > 0 if b is left of o->a, < 0 right, 0 on the line."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def segments_cross(a, b, c, d) -> bool:
    """ab and cd cross at a point inside both; touching or overlapping doesn't count."""
    return (cross(a, b, c) * cross(a, b, d) < 0) and (cross(c, d, a) * cross(c, d, b) < 0)


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return ((px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2) ** 0.5


def sector_at(level, p):
    return next((s for s in level.sectors.values() if s.contains(p)), None)


def neighbours(sec, lines):
    """Sectors across sec's two-sided lines; free-standing lines inside it don't count."""
    return [l.other(sec) for l in lines if l.back and l.touches(sec) and l.front is not l.back]


def open_ceil(door_sec, lines):
    """Height a door's ceiling rises to: lowest neighbouring ceiling - 4."""
    return min(n.ceil for n in neighbours(door_sec, lines)) - 4

def floor_movers(lines):
    """{tag: "lower" | "raise"} for every tag a floor-moving trigger moves."""
    return {l.tag: ("lower" if l.action in FLOOR_LOWERERS else "raise") for l in lines
            if l.tag and l.action in FLOOR_LOWERERS | FLOOR_RAISERS}


def moved_floor(sec, lines, movers):
    """Where sec's floor ends up once its trigger fires: lowering floors drop
    to their lowest neighbour, raising floors rise to the next higher
    neighbouring floor. movers: {tag: kind}, as from floor_movers."""
    kind = sec.tag and movers.get(sec.tag)
    if kind == "lower":
        return min(n.floor for n in neighbours(sec, lines))
    if kind == "raise":
        return min((n.floor for n in neighbours(sec, lines) if n.floor > sec.floor), default=sec.floor)
    return sec.floor


def floor_range(sec, lines, movers):
    """Lowest and highest floor `sec` can have: lifts drop to their lowest
    neighbour, and floors tagged by a floor-moving trigger move as
    moved_floor says. movers: {tag: kind}, as from floor_movers."""
    if sec.kind == LIFT:
        return min(n.floor for n in neighbours(sec, lines)), sec.floor
    to = moved_floor(sec, lines, movers)
    return min(sec.floor, to), max(sec.floor, to)

# --------------------------------------------------------------- helpers ---


DIRS = {"n": (0, 1), "s": (0, -1), "e": (1, 0), "w": (-1, 0)}


def rect(x1, y1, x2, y2) -> Loop:
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]


def strip(at: Point, facing: str, start: int, depth: int, width: int) -> Loop:
    """Rectangle `width` across, centred on `at`, running from `start` to
    `start + depth` units from `at` toward `facing` (n/s/e/w)."""
    if width % 2:
        raise LevelError(f"strip width {width} at {at} must be even")
    (x, y), (dx, dy) = at, DIRS[facing]
    if dx:
        x1, x2 = sorted((x + dx * start, x + dx * (start + depth)))
        return rect(x1, y - width // 2, x2, y + width // 2)
    y1, y2 = sorted((y + dy * start, y + dy * (start + depth)))
    return rect(x - width // 2, y1, x + width // 2, y2)


def door(name, loop, face="BIGDOOR2", track="DOORTRAK", action=None, tag=0, light=144, floor=0,
         flat="FLAT20") -> Sector:
    """Closed door: ceiling == floor; it opens to its lowest neighbouring
    ceiling - 4. Untagged doors open on use (DR_DOOR) unless `action` says
    otherwise (e.g. DR_BLUE); tagged doors only open from their trigger.
    `flat` is the threshold's floor (match the rooms for Romero's rule 1)."""
    if action is None:
        action = 0 if tag else DR_DOOR
    return Sector(name, [loop], floor, floor, flat, "FLAT20", light, track,
                  face=face, kind=DOOR, tag=tag, action=action)


def doorway(name, at, facing, width=128, *, alcove=0, far_alcove=0, alcove_wall="STARTAN3",
            alcove_height=128, alcove_flat="FLAT1", far_flat=None, thickness=16, floor=0,
            **door_kw) -> list[Sector]:
    """A door through a wall. `at` is the centre of the opening on the wall
    you come from and `facing` (n/s/e/w) points through it. Optional
    recesses 32 wider than the door sit before it (`alcove` deep, floor
    `alcove_flat`) and after it (`far_alcove` deep, floor `far_flat`, default
    `alcove_flat`); keep `alcove_height` at the face texture's height so the
    face isn't tiled. door_kw goes to door(). Returns the sectors:
    <name>_alcove, <name>, <name>_far."""
    out = []
    if alcove:
        out.append(Sector(f"{name}_alcove", [strip(at, facing, 0, alcove, width + 32)], floor,
                          floor + alcove_height, alcove_flat, "CEIL5_1", 176, alcove_wall))
    out.append(door(name, strip(at, facing, alcove, thickness, width), floor=floor, **door_kw))
    if far_alcove:
        out.append(Sector(f"{name}_far", [strip(at, facing, alcove + thickness, far_alcove, width + 32)],
                          floor, floor + alcove_height, far_flat or alcove_flat, "CEIL5_1", 176, alcove_wall))
    return out


def closet(name, at, facing, tag, *, face, flat, wall, floor=0, width=160, depth=160, height=128,
           ctex="CEIL5_1", light=96, special=0, door_width=128, **door_kw) -> list[Sector]:
    """A monster closet: a door in the wall at `at` that only `tag` opens,
    disguised as the wall it's in (`face`), and a room `width` x `depth`
    behind it. Returns the sectors d_<name>, <name>."""
    return [*doorway(f"d_{name}", at, facing, door_width, face=face, track=face, tag=tag, floor=floor,
                     flat=flat, **door_kw),
            Sector(name, [strip(at, facing, door_kw.get("thickness", 16), depth, width)], floor, floor + height,
                   flat, ctex, light, wall, special=special)]


def pedestal(name, box, floor, ceil, wall, ctex, *, flat="TLITE6_1", glow=True) -> Sector:
    """A lit pedestal for a key, weapon or power-up, with metal sides; its
    top is `floor`. Put a W1 trigger on its edge (SPECIAL_BETWEEN) to make
    taking the item spring a trap."""
    return Sector(name, [rect(*box)], floor, ceil, flat, ctex, 240, wall, lower="METAL",
                  special=LIGHT_GLOW if glow else 0)


def switch_niche(name, at, facing, special, *, floor, flat, wall, ctex, light, width=64, height=128,
                 depth=16) -> tuple[Sector, dict]:
    """A recess `depth` deep in the wall at `at`, whose back wall is a switch
    (special.texture). Size it to the switch picture: SW1EXIT is 32 x 72,
    most others 64 x 128. A deep niche (a booth) makes the player step in to
    reach the switch, so a W1 line on its entrance fires just before it.
    Returns (sector, {back wall: special}) for SECTORS and SPECIAL_WALLS."""
    (x, y), (dx, dy) = at, DIRS[facing]
    bx, by = x + dx * depth, y + dy * depth
    half = width // 2
    back = ((bx - half, by), (bx + half, by)) if dy else ((bx, by - half), (bx, by + half))
    return (Sector(name, [strip(at, facing, 0, depth, width)], floor, floor + height, flat, ctex, light, wall),
            {back: special})


def lit_ledge(name, box, wall_side, *, floor, ceil, flat, ctex, light, ambient, wall, lower="METAL",
              special=SECRET_AREA, spacer=16) -> list[Sector]:
    """A brightly lit ledge against a wall (on its `wall_side`, n/s/e/w),
    with an unlit `spacer`-wide strip between it and the wall, at `ambient`
    light, so the wall behind isn't lit up with it. Returns <name>,
    <name>_back."""
    x1, y1, x2, y2 = box
    s = spacer
    lit, back = {"n": ((x1, y1, x2, y2 - s), (x1, y2 - s, x2, y2)), "s": ((x1, y1 + s, x2, y2), (x1, y1, x2, y1 + s)),
                 "e": ((x1, y1, x2 - s, y2), (x2 - s, y1, x2, y2)), "w": ((x1 + s, y1, x2, y2), (x1, y1, x1 + s, y2))
                 }[wall_side]
    return [Sector(name, [rect(*lit)], floor, ceil, flat, ctex, light, wall, lower=lower, special=special),
            Sector(f"{name}_back", [rect(*back)], floor, ceil, flat, ctex, ambient, wall, lower=lower)]


def window(name, box, floor, ceil, wall, light, *, flat="FLAT5_4", ctex="CEIL5_1", lower="METAL") -> Sector:
    """An opening between two rooms: a sill at `floor` and a lintel at
    `ceil`. Monsters fire through it; walking monsters can only climb a sill
    24 or less above their floor, and fliers need it at least 56 tall."""
    return Sector(name, [rect(*box)], floor, ceil, flat, ctex, light, wall, lower=lower)


def stairs(name, box, facing, steps, floor, rise, ceil, ftex, ctex, light, wall, riser) -> list[Sector]:
    """`steps` equal steps filling box=(x1, y1, x2, y2), changing height by
    `rise` per step toward `facing` (negative rise goes down). The first
    step, at `floor`, is on the side `facing` points away from. Sectors are
    named <name>1..N."""
    x1, y1, x2, y2 = box
    dx, dy = DIRS[facing]
    span = (x2 - x1) if dx else (y2 - y1)
    if span % steps:
        raise LevelError(f"{name}: {span} units don't divide into {steps} steps")
    d = span // steps
    out = []
    for i in range(steps):
        if dx > 0:
            r = rect(x1 + i * d, y1, x1 + (i + 1) * d, y2)
        elif dx < 0:
            r = rect(x2 - (i + 1) * d, y1, x2 - i * d, y2)
        elif dy > 0:
            r = rect(x1, y1 + i * d, x2, y1 + (i + 1) * d)
        else:
            r = rect(x1, y2 - (i + 1) * d, x2, y2 - i * d)
        out.append(Sector(f"{name}{i + 1}", [r], floor + i * rise, ceil, ftex, ctex, light, wall, lower=riser))
    return out


def lift(name, box, floor, ceil, tag, ctex, light, wall, ftex="STEP1", side="PLAT1") -> Sector:
    """A lift resting at `floor` (its top) that lowers to its lowest
    neighbour. build() puts SR_LIFT on lines from lower neighbours and
    WR_LIFT on lines from neighbours at its top."""
    return Sector(name, [rect(*box)], floor, ceil, ftex, ctex, light, wall, lower=side, tag=tag, kind=LIFT)
