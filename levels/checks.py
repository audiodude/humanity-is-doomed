"""Level validation (thing placement, progression, textures) and the balance
report. Check functions return lists of messages; build() decides what fails."""
from collections import defaultdict, deque

from .doom2 import (ACTORS, AMMO_PICKUPS, ARMOR_PICKUPS, DAMAGE_PER_AMMO, DROPS, FLOOR_LOWERERS,
                    HEALTH_PICKUPS, KEY_OF, PLAYER1, PLAYERS, START_AMMO, TAG_DOOR_OPENERS,
                    USE_DOORS, is_decal)
from .model import ALL, DOOR, LIFT, NO_TEX, floor_range, neighbours, open_ceil, sector_at, seg_dist


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
            if l.back is None:
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


def check_progression(level, lines):
    """Flood-fill from the player 1 start, picking up keys and firing tagged
    triggers as their sectors become reachable, until nothing changes."""
    p1 = next((t for t in level.things if t.type == PLAYER1), None)
    start = p1 and sector_at(level, (p1.x, p1.y))
    if start is None:
        return ["no player 1 start inside a sector"]
    adj = defaultdict(list)
    for l in lines:
        if l.back:
            adj[l.front].append((l.back, l))
            adj[l.back].append((l.front, l))
    keys_at = [(KEY_OF[t.type], sector_at(level, (t.x, t.y))) for t in level.things if t.type in KEY_OF]
    # (tag, action, sectors the player can trigger it from)
    triggers = [(l.tag, l.action, (l.front,) if l.back is None else (l.front, l.back))
                for l in lines if l.tag and l.action in TAG_DOOR_OPENERS | FLOOR_LOWERERS]

    def heights(s, lowered):
        floor = min(n.floor for n in neighbours(s, lines)) if s.tag in lowered else s.floor
        ceil = open_ceil(s, lines) if s.kind == DOOR else s.ceil
        return floor, ceil

    def passable(a, b, line, keys, opened, lowered):
        if line.length < 33:   # player is 32 wide
            return False
        if b.kind == DOOR and b.tag not in opened:
            if line.action not in USE_DOORS:
                return False
            key = USE_DOORS[line.action]
            if key and key not in keys:
                return False
        fa, ca = heights(a, lowered)
        fb, cb = heights(b, lowered)
        if fb - fa > 24 and LIFT not in (a.kind, b.kind):
            return False
        return min(ca, cb) - max(fa, fb) >= 56

    state = (set(), set(), set())   # keys, opened door tags, lowered floor tags
    while True:
        seen = {start}
        q = deque([start])
        while q:
            a = q.popleft()
            for b, line in adj[a]:
                if b not in seen and passable(a, b, line, *state):
                    seen.add(b)
                    q.append(b)
        fired = {(tag, action) for tag, action, secs in triggers if any(s in seen for s in secs)}
        new = ({k for k, s in keys_at if s in seen},
               {tag for tag, action in fired if action in TAG_DOOR_OPENERS},
               {tag for tag, action in fired if action in FLOOR_LOWERERS})
        if new == state:
            break
        state = new
    names = {s.name for s in seen}
    return [f"unreachable: {n}" for n in level.must_reach if n not in names]


def check_textures(level, lines, sides, iwad):
    """Every texture and flat exists, and textures fit the walls they're on.
    Returns (errors, warnings); each is one message per texture and problem."""
    textures, flats = iwad
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
