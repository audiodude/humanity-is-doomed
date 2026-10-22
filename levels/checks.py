"""Level validation (thing placement, progression, kills, secrets, hazards,
textures) and the balance report. Check functions return lists of messages;
build() decides what fails."""
from collections import defaultdict, deque

from .doom2 import (ACTORS, AMMO_PICKUPS, ARMOR_PICKUPS, DAMAGE_PER_AMMO, DAMAGING, DROPS, EXITS,
                    FLOOR_LOWERERS, HEALTH_PICKUPS, KEY_OF, PLAYER1, PLAYERS, SECRET_AREA, START_AMMO,
                    TAG_DOOR_OPENERS, TELEPORT_DEST, USE_DOORS, WR_TELEPORT, is_decal)
from .model import (ALL, DOOR, LIFT, ML_BLOCKING, NO_TEX, floor_range, neighbours, open_ceil,
                    sector_at, seg_dist)


def check_things(level, lines):
    """Things sit inside a sector, don't clip walls, ledges or each other,
    and fit."""
    errors = []
    for t in level.things:
        where = f"thing {t.type} at {t.x},{t.y}"
        s = sector_at(level, (t.x, t.y))
        if s is None:
            errors.append(f"{where} is in the void")
            continue
        if s.kind == DOOR:
            errors.append(f"{where} inside door {s.name}")
        actor = ACTORS.get(t.type)
        if actor is None:
            continue
        if not actor.flies and s.ceil - s.floor < actor.height:
            errors.append(f"{where} lacks headroom in {s.name}")
        for l in lines:
            d = seg_dist((t.x, t.y), l.v1, l.v2)
            if d >= actor.radius:
                continue
            if l.back is None or l.flags & ML_BLOCKING:
                errors.append(f"{where} clips wall {l.v1}-{l.v2} ({d:.0f}<{actor.radius})")
            else:
                o = l.other(s)
                if o.floor - s.floor > 24 or o.kind == DOOR:
                    errors.append(f"{where} clips step/door {l.v1}-{l.v2}")
    return errors + check_overlaps(level)


def check_overlaps(level):
    """Actors that appear on a common skill don't overlap. Doom blocks
    actors as squares (|dx| and |dy| both under the summed radii), and
    overlapping ones start stuck."""
    actors = [t for t in level.things if t.type in ACTORS]
    errors = []
    for i, a in enumerate(actors):
        for b in actors[i + 1:]:
            shared = "".join(sk for sk in ALL if sk in a.skills and sk in b.skills)
            reach = ACTORS[a.type].radius + ACTORS[b.type].radius
            if shared and abs(a.x - b.x) < reach and abs(a.y - b.y) < reach:
                errors.append(f"thing {a.type} at {a.x},{a.y} overlaps thing {b.type} at "
                              f"{b.x},{b.y} on skills {shared}")
    return errors


def explore(level, lines):
    """Flood-fill from the player 1 start, picking up keys and firing tagged
    triggers as their sectors become reachable, until nothing changes.
    Returns (reached sectors, adjacency, move), or None without a player 1
    start. adjacency maps a sector to [(sector, line)], line None for a
    teleport. move(a, b, line, actor) says whether `actor` (an Actor) can
    cross from a to b once the player has every key, door and floor they can
    get; only the player opens keyed doors."""
    p1 = next((t for t in level.things if t.type == PLAYER1), None)
    start = p1 and sector_at(level, (p1.x, p1.y))
    if start is None:
        return None
    player = ACTORS[PLAYER1]
    adj = defaultdict(list)
    for l in lines:
        if l.back:
            adj[l.front].append((l.back, l))
            adj[l.back].append((l.front, l))
    dests = defaultdict(list)   # tag -> sectors holding a teleport destination
    for t in level.things:
        s = t.type == TELEPORT_DEST and sector_at(level, (t.x, t.y))
        if s and s.tag:
            dests[s.tag].append(s)
    for l in lines:
        if l.action == WR_TELEPORT:   # fires crossing from the front side
            adj[l.front] += [(d, None) for d in dests[l.tag]]
    keys_at = [(KEY_OF[t.type], sector_at(level, (t.x, t.y))) for t in level.things if t.type in KEY_OF]
    # (tag, action, sectors the player can trigger it from)
    triggers = [(l.tag, l.action, (l.front,) if l.back is None else (l.front, l.back))
                for l in lines if l.tag and l.action in TAG_DOOR_OPENERS | FLOOR_LOWERERS]

    def heights(s, lowered):
        floor = min(n.floor for n in neighbours(s, lines)) if s.tag in lowered else s.floor
        ceil = open_ceil(s, lines) if s.kind == DOOR else s.ceil
        return floor, ceil

    def passable(a, b, line, actor, keys, opened, lowered):
        if line is None:
            return True
        if line.length <= 2 * actor.radius or line.flags & ML_BLOCKING:   # bars and fences block
            return False
        if b.kind == DOOR and b.tag not in opened:
            if line.action not in USE_DOORS:
                return False
            key = USE_DOORS[line.action]
            if key and (actor is not player or key not in keys):
                return False
        fa, ca = heights(a, lowered)
        fb, cb = heights(b, lowered)
        if not actor.flies and fb - fa > 24 and LIFT not in (a.kind, b.kind):
            return False
        return min(ca, cb) - max(fa, fb) >= actor.height

    state = (set(), set(), set())   # keys, opened door tags, lowered floor tags
    while True:
        seen = flood({start}, adj, lambda a, b, line: passable(a, b, line, player, *state))
        fired = {(tag, action) for tag, action, secs in triggers if any(s in seen for s in secs)}
        new = ({k for k, s in keys_at if s in seen},
               {tag for tag, action in fired if action in TAG_DOOR_OPENERS},
               {tag for tag, action in fired if action in FLOOR_LOWERERS})
        if new == state:
            break
        state = new
    return seen, adj, lambda a, b, line, actor: passable(a, b, line, actor, *state)


def flood(start, adj, ok):
    """Sectors reachable from `start` over edges where ok(a, b, line)."""
    seen = set(start)
    q = deque(start)
    while q:
        a = q.popleft()
        for b, line in adj[a]:
            if b not in seen and ok(a, b, line):
                seen.add(b)
                q.append(b)
    return seen


def check_reach(level, lines):
    """Every MUST_REACH sector and every secret can be reached, every monster
    can be reached or walk (fly) to where the player can go (100% kills; a
    sniper the player can only shoot at fails this too), and the exit can
    still be reached from every damaging floor the player can get onto (no
    softlock in a pit of nukage)."""
    found = explore(level, lines)
    if found is None:
        return ["no player 1 start inside a sector"]
    seen, adj, move = found
    names = {s.name for s in seen}
    errors = [f"unreachable: {n}" for n in level.must_reach if n not in names]
    errors += [f"secret {s.name} is unreachable" for s in level.sectors.values()
               if s.special == SECRET_AREA and s not in seen]
    for t in level.things:
        s = sector_at(level, (t.x, t.y))
        if t.type in PLAYERS or t.type not in ACTORS or s is None or s in seen:
            continue
        actor = ACTORS[t.type]
        if not seen & flood({s}, adj, lambda a, b, line: move(a, b, line, actor)):
            errors.append(f"thing {t.type} at {t.x},{t.y} in {s.name} can't be reached and can't come "
                          f"to the player")
    exits = {s for l in lines if l.action in EXITS for s in (l.front, l.back) if s}
    if not exits:
        return errors + ["no exit line"]
    exits |= {n for s in exits for n in neighbours(s, lines)}   # exit switches sit in niches
    player = ACTORS[PLAYER1]
    for s in sorted((s for s in seen if s.special in DAMAGING), key=lambda s: s.name):
        if not exits & flood({s}, adj, lambda a, b, line: move(a, b, line, player)):
            errors.append(f"damaging floor {s.name} is a softlock: the exit can't be reached from it")
    return errors


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


def check_textures(level, lines, sides, iwad):
    """Every texture and flat exists, and textures fit the walls they're on.
    Returns (errors, warnings); each is one message per texture and problem."""
    textures, flats, medusa = iwad
    errors = [f"{s.name}: unknown flat {f}" for s in level.sectors.values()
              for f in (s.ftex, s.ctex) if f not in flats]
    lowered = {l.tag for l in lines if l.action in FLOOR_LOWERERS}
    problems = defaultdict(list)   # (texture, message, is_error) -> places
    for l, line_sides in zip(lines, sides):
        for sd in line_sides:
            me, other = sd.sector, (l.other(sd.sector) if l.back else None)
            if other is None:
                parts = [(sd.mid, me.ceil - me.floor)]
            else:
                top = other.floor if other.kind == DOOR else other.ceil   # closed door: whole face shows
                span = (floor_range(other, lines, lowered)[1] - floor_range(me, lines, lowered)[0])
                parts = [(sd.upper, me.ceil - top), (sd.lower, span)]
                if sd.mid != NO_TEX and (found := mid_fit(sd.mid, textures, medusa)):
                    problems[(sd.mid, *found)].append(f"{me.name} {l.v1}-{l.v2}")
            for tex, h in parts:
                if tex == NO_TEX or h <= 0:
                    continue
                if found := texture_fit(tex, h, l.length, textures):
                    problems[(tex, *found)].append(f"{me.name} {l.v1}-{l.v2}")
    warnings = []
    for (tex, msg, is_error), places in problems.items():
        more = f" (+{len(places) - 1} more)" if len(places) > 1 else ""
        (errors if is_error else warnings).append(f"{tex}: {msg}, at {places[0]}{more}")
    return errors, warnings


def mid_fit(tex, textures, medusa):
    """(message, is_error) if `tex` can't hang in a two-sided line, else None.
    Vanilla draws it once, never tiled vertically, so its height is free: a
    short one leaves a gap above, a tall one is cut off at the ceiling."""
    if tex not in textures:
        return "unknown texture", True
    if tex in medusa:
        return ("has columns made of several patches, which vanilla draws as garbage "
                "(the medusa effect) on a two-sided line"), True
    w = textures[tex][0]
    if w & (w - 1):
        return f"width {w} isn't a power of two; vanilla repeats only part of it", False
    return None


def texture_fit(tex, h, length, textures):
    """(message, is_error) if `tex` doesn't fit a wall part `h` tall on a
    line `length` long, else None."""
    if tex not in textures:
        return "unknown texture", True
    w, th = textures[tex]
    if is_decal(tex):
        if round(length) != w:
            return f"{w} wide but the line is {length:.0f}; a picture must be shown whole", True
        if not th - 8 <= h <= th:
            return f"{th} tall but the wall is {h}; a picture must be shown whole", True
        return None
    if w & (w - 1):
        return f"width {w} isn't a power of two; vanilla repeats only part of it", False
    if h > th and th != 128:
        return f"{th} tall on a {h}-tall wall; vanilla only tiles 128-tall textures cleanly", False
    return None


def balance_report(level):
    """Per-skill monster health against ammo damage, health and armor. Ammo
    counts the pistol start, pickups and monster drops; damage per unit is a
    rough average for hits (see DAMAGE_PER_AMMO). ITYTD doubles ammo."""
    rows = ["skill  monsters  monster HP  ammo damage  ratio  health  armor"]
    for sk, label in zip(ALL, ("easy", "medium", "hard")):
        things = [t for t in level.things if sk in t.skills]
        monsters = [t for t in things if t.type in ACTORS and t.type not in PLAYERS]
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
