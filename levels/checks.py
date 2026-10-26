"""Level validation and the balance report. findings() runs every check on a
compiled level and sorts the messages: playability (the map is broken: lines
crossing, things stuck or in the void, unreachable exit, secrets or monsters,
softlocks, unknown textures), style (house rules: sunken hazards, whole
pictures, no medusa, no running jump to the exit) and warnings. build()
decides what fails. Messages name sectors and coordinates, so they stay the
same across rebuilds (level modules list known ones in KNOWN_ISSUES).

Reachability comes from levels.reach, run once on the map lumps as built."""
from collections import defaultdict, deque
from dataclasses import dataclass, field

from .doom2 import (ACTORS, AMMO_PICKUPS, ARMOR_PICKUPS, BOSSBRAIN, DAMAGE_PER_AMMO, DAMAGING, DROPS,
                    HEALTH_PICKUPS, KEEN, LINE_SPECIALS, MAX_STEP, MONSTERS, PLAYER1, PLAYERS, SECRET_AREA,
                    START_AMMO, THING_GAMES, THING_NAMES, is_decal)
from .measure import check_sector_overlaps
from .model import ALL, DOOR, NO_TEX, THING_BITS, crossings, floor_movers, floor_range, seg_dist
from .reach import solve
from .wad import IWAD_VARS, IWADS, iwad_textures
from .wadmap import ML_BLOCKING, ML_BLOCKMONSTERS, MULTI_ONLY, parse

GAMES = {"doom": "DOOM", "doom2": "DOOM II"}


@dataclass
class Findings:
    playability: list[str] = field(default_factory=list)
    style: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    # (wadmap.Map, reach.Model, its run) for the measurements; None without a player 1 start.
    reach: tuple | None = field(default=None, repr=False, compare=False)


_iwads = {}


def level_textures(level):
    """iwad_textures of the level's game IWAD plus its RESOURCES (cached), or
    None if that IWAD isn't set."""
    key = (level.game, tuple(level.resources))
    if key not in _iwads:
        _iwads[key] = iwad_textures(IWADS[level.game], level.resources)
    return _iwads[key]


def findings(level, compiled) -> Findings:
    """Every check on a level and its compile_level() output."""
    found = Findings()
    m = parse(level.game, level.map, dict(compiled.lumps[1:]))
    names = list(level.sectors)   # SECTORS lump order
    found.playability += (crossings(compiled.lines) + check_sector_overlaps(level)
                          + check_things(m, names))
    check_types(m, found)
    iwad = level_textures(level)
    if iwad is None:
        found.warnings.append(f"no {level.game}.wad at {IWAD_VARS[level.game]}={IWADS[level.game]} "
                              "(set it in .env, see .env.example); skipping texture checks")
    else:
        check_textures(level, compiled.lines, compiled.sides, iwad, found)
    p1 = next((t for t in m.things if t.type == PLAYER1), None)
    if p1 is None or m.sector_of_point(p1.x, p1.y) is None:
        found.playability.append("no player 1 start inside a sector")
    else:
        sizes = iwad[0] if iwad else {}
        md, res = solve(m, (sizes, next(iter(sizes.values()))[1] if sizes else 0))
        found.reach = (m, md, res)
        check_reach(level, md, res, names, found)
    found.style += check_hazards(level, compiled.lines)
    return found


def _thing(t):
    return f"{THING_NAMES.get(t.type, t.type)} at {t.x},{t.y}"


def _sector_of(m, x, y):
    """Sector index at (x, y); a point on a line counts as on its front side."""
    o = m.sector_of_point(x, y)
    if o is None:
        o = next((m.sides[l.front].sector for l in m.lines
                  if seg_dist((x, y), m.verts[l.v1], m.verts[l.v2]) == 0), None)
    return o


def _skills(t):
    return "" if t.flags & MULTI_ONLY else "".join(sk for sk in ALL if t.flags & THING_BITS[sk])


def check_things(m, names):
    """Things sit inside a sector; actors fit under its ceiling (a closed
    door has no room), don't clip walls, steps or closed doors, and don't
    overlap each other."""
    errors = []
    lines = [(m.verts[l.v1], m.verts[l.v2], l.flags, *m.line_sectors(l)) for l in m.lines]
    for t in m.things:
        o = _sector_of(m, t.x, t.y)
        if o is None:
            errors.append(f"{_thing(t)} is in the void")
            continue
        actor = ACTORS.get(t.type)
        if actor is None:
            continue
        s = m.sectors[o]
        if s.ceil - s.floor < actor.height:
            errors.append(f"{_thing(t)} lacks headroom in {names[o]}")
        block = ML_BLOCKING if t.type in PLAYERS else ML_BLOCKING | ML_BLOCKMONSTERS
        for p, q, flags, f, b in lines:
            d = seg_dist((t.x, t.y), p, q)
            if d >= actor.radius or f == b:
                continue
            if b is None or flags & block:
                errors.append(f"{_thing(t)} clips wall {p}-{q} ({d:.0f}<{actor.radius})")
                continue
            n = m.sectors[b if f == o else f]
            if (not actor.flies and n.floor - s.floor > MAX_STEP
                    or min(n.ceil, s.ceil) - max(n.floor, s.floor) < actor.height):
                errors.append(f"{_thing(t)} clips step/door {p}-{q}")
    return errors + check_overlaps(m)


def check_overlaps(m):
    """Actors that appear on a common skill don't overlap. Doom blocks
    actors as squares (|dx| and |dy| both under the summed radii), and
    overlapping ones start stuck."""
    actors = [t for t in m.things if t.type in ACTORS]
    errors = []
    for i, a in enumerate(actors):
        for b in actors[i + 1:]:
            shared = "".join(sk for sk in _skills(a) if sk in _skills(b))
            reach = ACTORS[a.type].radius + ACTORS[b.type].radius
            if shared and abs(a.x - b.x) < reach and abs(a.y - b.y) < reach:
                errors.append(f"{_thing(a)} overlaps {_thing(b)} on skills {shared}")
    return errors


def check_types(m, found):
    """Thing types exist in the map's game; non-vanilla thing types and line
    actions are warnings (the checks don't know what they do)."""
    for t in m.things:
        if t.type not in THING_NAMES:
            found.warnings.append(f"thing type {t.type} at {t.x},{t.y} isn't a vanilla thing")
        elif m.game not in THING_GAMES[t.type]:
            found.playability.append(f"{_thing(t)} doesn't exist in {GAMES[m.game]}")
    unknown = defaultdict(list)
    for ln in m.lines:
        if ln.special and ln.special not in LINE_SPECIALS:
            unknown[ln.special].append(f"{m.verts[ln.v1]}-{m.verts[ln.v2]}")
    for action, places in sorted(unknown.items()):
        more = f" (+{len(places) - 1} more)" if len(places) > 1 else ""
        found.warnings.append(f"line action {action} isn't vanilla, at {places[0]}{more}")


def check_reach(level, md, res, names, found):
    """With the reach model's run: every MUST_REACH sector, secret and the
    exit can be reached (a running jump to the exit is a style finding);
    every monster can be reached or walk (fly) to where the player can go,
    firing the walk lines monsters fire (100% kills; a sniper the player can
    only shoot at fails this too; the boss brain and Keen are shot); and
    the exit can still be reached from every damaging floor the player can
    get onto (no softlock in a pit of nukage)."""
    R = res["R"]
    reached = {md.nsec[r] for r in R}
    found.playability += [f"unreachable: {n}" for n in level.must_reach if names.index(n) not in reached]
    found.playability += [f"secret {names[o]} is unreachable" for o, s in enumerate(md.m.sectors)
                          if s.special == SECRET_AREA and o not in reached]
    base, man, keys = md.final_state(res)
    for t in md.m.things:
        if t.type not in MONSTERS or t.type in (BOSSBRAIN, KEEN) or not _skills(t):   # shot, never met
            continue
        r = md.region_of_point(t.x, t.y)
        if r is None or r in R:
            continue
        if not R & md.monster_closure(res, r, ACTORS[t.type]):
            found.playability.append(f"{_thing(t)} in {names[md.nsec[r]]} can't be reached and can't "
                                     f"come to the player")
    if not (any(kind == "exit" for kind, _, _ in md.exits) or md.exit_sectors
            or any(act == "exit" for _, act, _ in md.boss)):
        found.playability.append("no exit")
        return
    ex = md.normal_exit(res)
    if ex is None:
        found.playability.append("the exit can't be reached")
        return
    if md.use_jumps:
        found.style.append(f"the exit (from {names[md.nsec[ex[1]]]}) can only be reached with a running jump")
    # Regions the exit can be reached from at the end, by walking back from it.
    into = defaultdict(set)
    for a in R:
        for b, _, _ in md.moves(a, base, man, keys):
            into[b].add(a)
    out, q = {ex[1]}, deque([ex[1]])
    while q:
        for a in into[q.popleft()] - out:
            out.add(a)
            q.append(a)
    pits = {md.nsec[r] for r in R - out if md.sec(r).special in DAMAGING}
    found.playability += [f"damaging floor {names[o]} is a softlock: the exit can't be reached from it"
                          for o in sorted(pits, key=lambda o: names[o])]


def check_hazards(level, lines):
    """Damaging floors sit below every neighbour that isn't damaging, so the
    hazard reads as a pit (and Romero's rule 1 holds)."""
    bad = set()
    for l in lines:
        if l.back and (l.front.special in DAMAGING) != (l.back.special in DAMAGING):
            h, n = (l.front, l.back) if l.front.special in DAMAGING else (l.back, l.front)
            if n.floor <= h.floor:
                bad.add((h.name, h.floor, n.name, n.floor))
    return [f"damaging floor {h} ({hf}) isn't below its neighbour {n} ({nf})" for h, hf, n, nf in sorted(bad)]


def check_textures(level, lines, sides, iwad, found):
    """Every texture and flat exists (playability), pictures fit their walls
    and two-sided middle textures have no medusa (style), and textures tile
    cleanly (warnings). One message per place for a missing texture, else
    one per texture and problem."""
    textures, flats, medusa = iwad
    found.playability += [f"{s.name}: unknown flat {f}" for s in level.sectors.values()
                          for f in (s.ftex, s.ctex) if f not in flats]
    movers = floor_movers(lines)
    problems = defaultdict(list)   # (texture, message, Findings field) -> places
    for l, line_sides in zip(lines, sides):
        for sd in line_sides:
            me, other = sd.sector, (l.other(sd.sector) if l.back else None)
            if other is None:
                parts = [(sd.mid, me.ceil - me.floor)]
            else:
                top = other.floor if other.kind == DOOR else other.ceil   # closed door: whole face shows
                span = (floor_range(other, lines, movers)[1] - floor_range(me, lines, movers)[0])
                parts = [(sd.upper, me.ceil - top), (sd.lower, span)]
                if sd.mid != NO_TEX and (problem := mid_fit(sd.mid, textures, medusa)):
                    problems[(sd.mid, *problem)].append(f"{me.name} {l.v1}-{l.v2}")
            for tex, h in parts:
                if tex == NO_TEX or h <= 0:
                    continue
                if problem := texture_fit(tex, h, l.length, textures):
                    problems[(tex, *problem)].append(f"{me.name} {l.v1}-{l.v2}")
    for (tex, msg, kind), places in problems.items():
        if kind == "playability":   # one per place, so KNOWN_ISSUES stays valid when other lines change
            found.playability += [f"{tex}: {msg}, at {p}" for p in places]
        else:
            more = f" (+{len(places) - 1} more)" if len(places) > 1 else ""
            getattr(found, kind).append(f"{tex}: {msg}, at {places[0]}{more}")


def mid_fit(tex, textures, medusa):
    """(message, Findings field) if `tex` can't hang in a two-sided line, else
    None. Vanilla draws it once, never tiled vertically, so its height is
    free: a short one leaves a gap above, a tall one is cut off at the
    ceiling."""
    if tex not in textures:
        return "unknown texture", "playability"
    if tex in medusa:
        return ("has columns made of several patches, which vanilla draws as garbage "
                "(the medusa effect) on a two-sided line"), "style"
    w = textures[tex][0]
    if w & (w - 1):
        return f"width {w} isn't a power of two; vanilla repeats only part of it", "warnings"
    return None


def texture_fit(tex, h, length, textures):
    """(message, Findings field) if `tex` doesn't fit a wall part `h` tall on
    a line `length` long, else None."""
    if tex not in textures:
        return "unknown texture", "playability"
    w, th = textures[tex]
    if is_decal(tex):
        if round(length) != w:
            return f"{w} wide but the line is {length:.0f}; a picture must be shown whole", "style"
        if not th - 8 <= h <= th:
            return f"{th} tall but the wall is {h}; a picture must be shown whole", "style"
        return None
    if w & (w - 1):
        return f"width {w} isn't a power of two; vanilla repeats only part of it", "warnings"
    if h > th and th != 128:
        return f"{th} tall on a {h}-tall wall; vanilla only tiles 128-tall textures cleanly", "warnings"
    return None


def balance_report(level):
    """Per-skill monster health against ammo damage, health and armor. Ammo
    counts the pistol start, pickups and monster drops; damage per unit is a
    rough average for hits (see DAMAGE_PER_AMMO). ITYTD doubles ammo.
    Multiplayer-only things don't count."""
    rows = ["skill  monsters  monster HP  ammo damage  ratio  health  armor"]
    for sk, label in zip(ALL, ("easy", "medium", "hard")):
        things = [t for t in level.things if sk in t.skills and "n" not in t.skills]
        monsters = [t for t in things if t.type in MONSTERS]
        hp = sum(ACTORS[t.type].health for t in monsters)
        ammo = defaultdict(int, START_AMMO)
        for t in things:
            for kind, n in AMMO_PICKUPS.get(t.type, {}).items():
                ammo[kind] += n
            for kind, n in DROPS.get(t.type, {}).items():
                ammo[kind] += n
        damage = sum(DAMAGE_PER_AMMO[k] * n for k, n in ammo.items())
        health = sum(HEALTH_PICKUPS.get(t.type, 0) for t in things)
        armor = sum(ARMOR_PICKUPS.get(t.type, 0) for t in things)
        rows.append(f"{label:<6} {len(monsters):>8}  {hp:>10}  {damage:>11}  {damage / max(hp, 1):>5.2f}"
                    f"  {health:>6}  {armor:>5}")
    return rows
