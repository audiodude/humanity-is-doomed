"""Balance along the route, from the map alone: no bot, no ViZDoom.

The route is the reach model's critical path (progression_metrics.analyse's
legs): start -> each required key and trigger, in the wave it becomes
available (best order within a wave) -> exit, each leg the shortest region
path under that wave's heights. Along it:

- Engagement. A monster is engaged on the first leg whose path it can walk
  to (reach.closure for its size, under that leg's heights, with manual doors
  shut: it hasn't been woken to open them), or, unless it only bites (demons,
  spectres), whose path it can shoot from within ENGAGE_RANGE of anywhere it
  can walk (reach.shoot_site; sight is symmetric, and the Ambush flag doesn't
  stop a monster that sees you). The last leg of a wave also sees the next
  wave's heights: the triggers fired in a wave are sprung while walking it.
  Monsters never engaged are in side rooms, listed with the items there.
- Two supply curves, simulated leg by leg with carry caps (a backpack
  doubles them). Ammo counts as damage (DAMAGE_PER_AMMO, like
  checks.balance_report) and only for a weapon the player holds; monster drops
  count on the leg the monster is engaged. Each leg's pickups are taken, then
  its engaged monster HP is paid from one damage pool, shells first, then
  rockets, cells and bullets; what's left is capped (within a leg, pickups and
  fights interleave).
    thorough: an item counts once its region is reachable (secrets and side
              rooms included). Running out here means fights the map's
              items can't pay for (a quarter of the id maps have some).
    detour:   an item counts on a leg if a round trip off the path to its region,
              out and back, is within DETOUR units. Secret areas (sector special
              9, and anything behind ML_SECRET doors) don't count. This is a
              normal player.
  Health is paid at HEALTH_PER_HP per engaged HP (the DOOM II median of the
  highest rate a route affords, health_rate), fights first, then the leg's
  health pickups.
- Exposure: monsters that can shoot the start and face it (or stand within
  64 of it); long-range hitscan damage per second on each leg (hitscanners
  engaged on that leg, shooting from beyond LONG_RANGE); and, for each trigger
  on the route, the monster HP it releases against the ammo carried then.

Every finding is a warning judged against the id maps (THRESHOLDS, from
scripts/metrics/route_metrics.py): a quarter of them run short on the
thorough curve too. docs/balance-metrics.md has the design and calibration.

    lines, warnings = report(route_balance(m, md, res, legs, names=names), m.game)
"""
import heapq
import math
from collections import defaultdict
from dataclasses import dataclass, field

from .doom2 import (ACTORS, AMMO_PICKUPS, BACKPACK, BFG, CHAINGUY, DAMAGE_PER_AMMO, DEMON, DROPS, HEALTH_PICKUPS,
                    LAUNCHER, MEGA, MONSTERS, PLASMA, SARGE, SECRET_AREA, SHOTGUN, SOUL, SPECTRE, SPIDER, SS, SSG,
                    START_AMMO, THING_NAMES, ZOMBIE)
from .reach import MANUAL_STAY, MANUAL_WAIT
from .wadmap import HARD, ML_SECRET

DETOUR = 1024          # round trip off the route a normal player makes for an item
LONG_RANGE = 768       # hitscanners farther than this count as sniping
MELEE = {DEMON, SPECTRE}   # engaged only by coming to you
ENGAGE_RANGE = 1024    # a monster that can only hit the route from farther is a nuisance, not a fight
CAPS = {"bullets": 200, "shells": 50, "rockets": 50, "cells": 300}
USED_BY = {"shells": {SHOTGUN, SSG}, "rockets": {LAUNCHER}, "cells": {PLASMA, BFG}}   # bullets: the pistol
SPEND = ("shells", "rockets", "cells", "bullets")
# Health cost per engaged monster HP: the DOOM II median of health_rate()
# (route_health_per_khp / 1000 in scripts/metrics/route_metrics.py), so the column reads "health left if the
# fights cost what the median id map's route can afford".
HEALTH_PER_HP = 0.0173
# Rough expected damage per second of an awake hitscanner at range; only the
# ratios matter, since the warning threshold is calibrated on the IWAD with them.
HITSCAN_DPS = {ZOMBIE: 4, SARGE: 10, SS: 6, CHAINGUY: 20, SPIDER: 60}
# Warning thresholds by game, from the id maps at UV (route_metrics.py): the
# 10th percentile of the lowest detour ratio along the route, and the 90th of
# the long-range hitscan peak.
THRESHOLDS = {"doom2": (0.147, 88.4), "doom": (0.402, 46)}


@dataclass
class Leg:
    label: str
    site: str
    wave: int
    path: list
    length: float
    engaged_hp: int = 0
    thorough: tuple = ()   # _simulate's row: (ammo left, cumulative ratio, health, ammo before the fights)
    detour: tuple = ()
    long_hitscan: float = 0.0


@dataclass
class Balance:
    legs: list = field(default_factory=list)
    side_rooms: list = field(default_factory=list)   # (sector names, monster HP, ammo damage, health)
    start_fire: list = field(default_factory=list)   # (type, x, y)
    traps: list = field(default_factory=list)        # (label, released HP, carried damage, nearest, retreat)
    summary: dict = field(default_factory=dict)
    engaged: list = field(default_factory=list)      # (type, x, y, leg index) in thing order
    detour_inputs: tuple = ((), ())                  # (pickups, drops) per leg, for health_rate


def _region_name(md, r, names):
    o = md.nsec[r]
    return names[o] if names and o < len(names) else f"sector {o}"


def _label(md, lab):
    if lab.startswith("key:"):
        return f"{lab[4:]} key"
    if lab.startswith("trig:"):
        tag, kind = lab[5:].split("/", 1)
        t = next((t for t in md.triggers if str(t["group"][0]) == tag and t["group"][1] == kind), None)
        return f"{t['trig']} {kind} tag {tag}" if t else lab
    return lab


def _shot(md, pt, r, P, base, man, limit):
    """Something at pt (in region r) and a player somewhere in P can hit each
    other from at most `limit` apart."""
    s = md.shoot_site(pt, r, P, base, man)
    return s is not None and (s == r or math.dist(md.inner[s], pt) <= limit)


def _secret_doors(md):
    """Door regions whose every manual door line is ML_SECRET: the way into a secret."""
    secret, plain = set(), set()
    for i, ln in enumerate(md.m.lines):
        if ln.special in MANUAL_WAIT or ln.special in MANUAL_STAY:
            b = md.secs_of_line[i][1]
            if b is not None:
                (secret if ln.flags & ML_SECRET else plain).add(b)
    return secret - plain


def _graph(md, state, blocked):
    """Forward and reverse weighted edges over every region, under one snapshot."""
    base, man, keys, _ = state
    fwd, rev = defaultdict(list), defaultdict(list)
    for a in range(md.n):
        for b, w, _ in md.moves(a, base, man, keys):
            if b not in blocked:
                fwd[a].append((b, w))
                rev[b].append((a, w))
    return fwd, rev


def _dists(edges, sources, limit):
    dist = {s: 0.0 for s in sources}
    pq = [(0.0, s) for s in sources]
    while pq:
        d, a = heapq.heappop(pq)
        if d > dist[a]:
            continue
        for b, w in edges.get(a, ()):
            nd = d + w
            if nd <= limit and nd < dist.get(b, math.inf):
                dist[b] = nd
                heapq.heappush(pq, (nd, b))
    return dist


def _simulate(legs, pickups, drops, health_per_hp=None):
    """[(usable damage left after the leg's fights, cumulative supply ratio,
    health, usable damage before them)] per leg. pickups/drops: per leg, lists
    of thing types."""
    carried, caps, held = dict.fromkeys(CAPS, 0.0), dict(CAPS), set()
    for k, n in START_AMMO.items():
        carried[k] += n
    supply = sum(DAMAGE_PER_AMMO[k] * n for k, n in START_AMMO.items())
    health, cum_hp, out = 100.0, 0, []
    for leg, things, dropped in zip(legs, pickups, drops):
        for ty in sorted(things, key=lambda ty: ty != BACKPACK):   # the backpack's caps first
            if ty == BACKPACK and caps["bullets"] == CAPS["bullets"]:
                caps = {k: 2 * v for k, v in caps.items()}
            held.add(ty)
        gains = [AMMO_PICKUPS.get(ty, {}) for ty in things] + [DROPS[ty] for ty in dropped]
        for gain in gains:
            for kind, n in gain.items():
                carried[kind] += n
                supply += DAMAGE_PER_AMMO[kind] * n
        need = float(leg.engaged_hp)
        cum_hp += leg.engaged_hp
        usable = [k for k in SPEND if k == "bullets" or held & USED_BY[k]]
        before = sum(min(caps[k], carried[k]) * DAMAGE_PER_AMMO[k] for k in usable)
        for kind in usable:
            use = min(carried[kind], need / DAMAGE_PER_AMMO[kind])
            carried[kind] -= use
            need -= use * DAMAGE_PER_AMMO[kind]
        # Within a leg, pickups and fights interleave: only what's left after
        # them has to fit in the pack.
        carried = {k: min(caps[k], v) for k, v in carried.items()}
        left = (sum(carried[k] * DAMAGE_PER_AMMO[k] for k in usable) if need <= 1e-6 else -need)
        health -= (HEALTH_PER_HP if health_per_hp is None else health_per_hp) * leg.engaged_hp
        for ty in things:
            if ty == MEGA:
                health = max(health, 200)
            elif ty == SOUL:
                health = min(200, health + 100)
            elif ty in HEALTH_PICKUPS:
                health = max(health, min(100, health + HEALTH_PICKUPS[ty]))
        out.append((left, supply / cum_hp if cum_hp else math.inf, health, before))
    return out


def route_balance(m, md, res, legs, skill=HARD, names=None, detour=DETOUR):
    """The Balance of a map along its critical path. legs: [(label, wave,
    region path, length)] from progression_metrics.analyse's debug data."""
    bal = Balance()
    if not legs:
        return bal
    snaps = res["snaps"]
    things = m.things_on(skill)
    region = {id(t): md.region_of_point(t.x, t.y) for t in things}
    for lab, w, path, length in legs:
        bal.legs.append(Leg(_label(md, lab), _region_name(md, path[-1], names), w, path, length))

    # ---- engagement. The last leg of a wave also sees the next wave's state:
    # the triggers that wave fired (closets, the floor under the key) are
    # sprung while walking it.
    closures, sights, shut = {}, {}, [None] * md.n
    monsters = [t for t in things if t.type in MONSTERS and region[id(t)] is not None]
    engaged = {}    # id(thing) -> leg index
    for k, leg in enumerate(bal.legs):
        waves = [leg.wave]
        if (k + 1 == len(bal.legs) or bal.legs[k + 1].wave > leg.wave) and leg.wave + 1 < len(snaps):
            waves.append(leg.wave + 1)
        P = set(leg.path)
        for w in waves:
            base, man, _, _ = snaps[w]
            for t in monsters:
                if id(t) in engaged:
                    continue
                r, actor = region[id(t)], ACTORS[t.type]
                if (w, r, actor) not in closures:   # manual doors shut: it hasn't been woken to open them
                    closures[(w, r, actor)] = md.closure(base, shut, (), [r], actor)
                reach = closures[(w, r, actor)]
                if reach & P:
                    engaged[id(t)] = k
                    leg.engaged_hp += ACTORS[t.type].health
                    continue
                if t.type in MELEE:
                    continue

                def sees(c):
                    if (k, w, c) not in sights:
                        sights[(k, w, c)] = _shot(md, md.inner[c], c, P, base, man, ENGAGE_RANGE)
                    return sights[(k, w, c)]
                if _shot(md, (t.x, t.y), r, P, base, man, ENGAGE_RANGE) or any(map(sees, reach)):
                    engaged[id(t)] = k
                    leg.engaged_hp += ACTORS[t.type].health

    bal.engaged = [(t.type, t.x, t.y, engaged[id(t)]) for t in monsters if id(t) in engaged]

    # ---- items, per curve
    blocked = _secret_doors(md)
    items = [t for t in things if (t.type in AMMO_PICKUPS or t.type in HEALTH_PICKUPS) and region[id(t)] is not None]
    sw = res["sector_wave"]
    thorough = [[] for _ in bal.legs]
    for t in items:
        r = region[id(t)]
        if r in sw:
            k = next((k for k, leg in enumerate(bal.legs) if leg.wave >= sw[r]), None)
            if k is not None:
                thorough[k].append(t.type)
    graphs, near = {}, [[] for _ in bal.legs]
    left = [t for t in items if md.sec(region[id(t)]).special != SECRET_AREA and region[id(t)] not in blocked]
    for k, leg in enumerate(bal.legs):
        if leg.wave not in graphs:
            graphs[leg.wave] = _graph(md, snaps[leg.wave], blocked)
        fwd, rev = graphs[leg.wave]
        out, back = _dists(fwd, leg.path, detour), _dists(rev, leg.path, detour)
        keep = []
        for t in left:
            r = region[id(t)]
            if r in out and r in back and out[r] + back[r] <= detour:
                near[k].append(t.type)
            else:
                keep.append(t)
        left = keep
    drops = [[] for _ in bal.legs]
    for t in monsters:
        if id(t) in engaged and t.type in DROPS:
            drops[engaged[id(t)]].append(t.type)
    bal.detour_inputs = (near, drops)
    for leg, th, de in zip(bal.legs, _simulate(bal.legs, thorough, drops), _simulate(bal.legs, near, drops)):
        leg.thorough, leg.detour = th, de

    # ---- side rooms: optional regions holding monsters never engaged
    on_route = {r for leg in bal.legs for r in leg.path}
    optional = set(res["R"]) - on_route
    comp = {}
    for s in optional:
        if s in comp:
            continue
        comp[s], todo = s, [s]
        while todo:
            a = todo.pop()
            for b in md.adj[a]:
                if b in optional and b not in comp:
                    comp[b] = s
                    todo.append(b)
    rooms = defaultdict(lambda: [set(), 0, 0, 0])
    for t in monsters:
        r = region[id(t)]
        if id(t) not in engaged and r in comp:
            room = rooms[comp[r]]
            room[1] += ACTORS[t.type].health
            room[2] += sum(DAMAGE_PER_AMMO[a] * n for a, n in DROPS.get(t.type, {}).items())
    for t in items:
        r = region[id(t)]
        if r in comp and comp[r] in rooms:
            room = rooms[comp[r]]
            room[2] += sum(DAMAGE_PER_AMMO[a] * n for a, n in AMMO_PICKUPS.get(t.type, {}).items())
            room[3] += HEALTH_PICKUPS.get(t.type, 0)
    for root, (_, hp, dmg, hl) in rooms.items():
        secs = sorted({_region_name(md, r, names) for r, c in comp.items() if c == root})
        bal.side_rooms.append((secs, hp, dmg, hl))
    bal.side_rooms.sort(key=lambda x: x[2] - x[1])

    # ---- start under fire
    base0, man0, _, _ = snaps[0]
    sx, sy = md.start_pt
    for t in monsters:
        r = region[id(t)]
        d = math.dist((t.x, t.y), (sx, sy))
        to_start = math.degrees(math.atan2(sy - t.y, sx - t.x))
        facing = abs((to_start - t.angle + 180) % 360 - 180) <= 90
        if (d <= 64 or facing) and md.shoot_site((t.x, t.y), r, {md.start}, base0, man0) is not None:
            bal.start_fire.append((t.type, t.x, t.y))

    # ---- long-range hitscan per leg
    for k, leg in enumerate(bal.legs):
        base, man, _, _ = snaps[leg.wave]
        scanners = [t for t in monsters if engaged.get(id(t)) == k and t.type in HITSCAN_DPS]
        for p in set(leg.path):
            dps = sum(HITSCAN_DPS[t.type] for t in scanners
                      if math.dist((t.x, t.y), md.inner[p]) > LONG_RANGE
                      and md.shoot_site((t.x, t.y), region[id(t)], {p}, base, man) is not None)
            leg.long_hitscan = max(leg.long_hitscan, dps)

    # ---- traps: triggers on the route and the monsters they let out
    seen_groups = set()
    for ti, tw in sorted(res["trig_wave"].items(), key=lambda x: x[1]):
        site, t = res["trig_site"][ti], md.triggers[ti]
        if site not in on_route or t["group"] in seen_groups or t["action"] in ("lift", "perpetual"):
            continue
        seen_groups.add(t["group"])
        opened = {r for o in md.tagged.get(t["tag"], []) for r in md.group[o]}
        opened |= {b for r in opened for b in md.adj[r]}
        before = [k for k, leg in enumerate(bal.legs) if leg.wave <= tw]
        released = [mo for mo in monsters if region[id(mo)] in opened and id(mo) in engaged
                    and engaged[id(mo)] >= (before[-1] if before else 0)]
        if not released:
            continue
        # ammo in hand when it springs, at best: all of the trigger leg's
        # pickups taken and none of its fights fought yet
        carried = bal.legs[before[-1] if before else 0].detour[3]
        ln = md.m.lines[t["line"]]
        mid = md.m.midpoint(ln)
        nearest = min(math.dist(mid, (mo.x, mo.y)) for mo in released)
        retreat = True
        if tw + 1 < len(snaps) and before:
            _, man, keys, _ = snaps[tw + 1]
            came_from = next((leg.path[0] for leg in bal.legs if leg.wave >= tw), bal.legs[-1].path[-1])
            retreat = came_from in md.closure(res["snap_now"][tw + 1], man, keys, [site])
        label = f"{t['trig']} {t['group'][1]} tag {t['tag']} @ {_region_name(md, site, names)}"
        bal.traps.append((label, sum(ACTORS[mo.type].health for mo in released), carried, nearest, retreat))

    det = [leg.detour[1] for leg in bal.legs if leg.detour[1] != math.inf]
    shares, cum = [], 0
    for leg in bal.legs:
        cum += leg.engaged_hp
        if cum:
            shares.append(leg.thorough[0] / cum)
    bal.summary = dict(route_min_detour_ratio=round(min(det), 3) if det else "",
                       route_min_thorough_share=round(min(shares), 3) if shares else "",
                       route_max_long_hitscan=max(leg.long_hitscan for leg in bal.legs))
    return bal


def health_rate(bal):
    """The highest health cost per monster HP at which the detour curve's
    health never drops below 0 (HEALTH_PER_HP is the DOOM II median of it)."""
    if not any(leg.engaged_hp for leg in bal.legs):
        return None
    lo, hi = 0.0, 1.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if min(h for _, _, h, _ in _simulate(bal.legs, *bal.detour_inputs, health_per_hp=mid)) >= 0:
            lo = mid
        else:
            hi = mid
    return lo


def report(bal, game="doom2", detour=DETOUR):
    """(lines, warnings) of a Balance. Nothing here is an error: the id maps
    themselves run short on the curves (see THRESHOLDS), so these are flags to
    look at, judged against the IWAD."""
    if not bal.legs:
        return [], []
    low_detour, high_hitscan = THRESHOLDS[game]
    lines = [f"resource curve (UV, pistol start; ammo as damage)    thorough            detour D={detour}",
             f" #  {'phase':<36} {'path':>5} {'eng.HP':>6}  {'ammo left':>9} {'ratio':>5}  "
             f"{'ammo left':>9} {'ratio':>5} {'health':>6}  long hitscan"]
    warnings = []
    for k, leg in enumerate(bal.legs, 1):
        (tl, tr, _, _), (dl, dr, dh, _) = leg.thorough, leg.detour
        flag = "  !! short even taking everything" if tl < 0 else "  !! detour" if dr < low_detour else ""
        ratio = lambda r: "-" if r == math.inf else f"{r:.2f}"   # noqa: E731
        lines.append(f"{k:>2}  {(leg.label + ' @ ' + leg.site)[:36]:<36} {leg.length:>5.0f} {leg.engaged_hp:>6}  "
                     f"{tl:>9.0f} {ratio(tr):>5}  {dl:>9.0f} {ratio(dr):>5} {dh:>6.0f}  "
                     f"{leg.long_hitscan:>4.0f}{flag}")
    if short := [k for k, leg in enumerate(bal.legs, 1) if leg.thorough[0] < 0]:
        warnings.append(f"resource curve: even taking every reachable item the route runs short of ammo on leg(s) "
                        f"{', '.join(map(str, short))} (a quarter of the id maps do; check those fights)")
    if low := [k for k, leg in enumerate(bal.legs, 1) if leg.thorough[0] >= 0 and leg.detour[1] < low_detour]:
        warnings.append(f"resource curve: near the route, ammo is scarcer than on 90% of the id maps on leg(s) "
                        f"{', '.join(map(str, low))} (detour ratio below {low_detour}); the ammo is off the way")
    if snipe := [k for k, leg in enumerate(bal.legs, 1) if leg.long_hitscan > high_hitscan]:
        warnings.append(f"long-range hitscan above {high_hitscan}/s (the id maps' 90th percentile) on leg(s) "
                        f"{', '.join(map(str, snipe))}")
    if bal.side_rooms:
        lines.append("side rooms (net = ammo damage - monster HP): " + "; ".join(
            f"{'/'.join(s[:3])}{'...' if len(s) > 3 else ''} {dmg - hp:+.0f} (HP {hp}, ammo {dmg}, health {hl})"
            for s, hp, dmg, hl in bal.side_rooms))
    for label, hp, carried, nearest, retreat in bal.traps:
        lines.append(f"trap {label}: releases {hp} HP, {carried:.0f} ammo damage carried (detour), nearest "
                     f"{nearest:.0f} away{'' if retreat else ', no way back'}")
        if carried < hp:
            warnings.append(f"trap {label} releases {hp} HP against {carried:.0f} ammo damage carried")
    for ty, x, y in bal.start_fire:
        warnings.append(f"start under fire: {THING_NAMES.get(ty, ty)} at {x},{y} can shoot the start and faces it")
    return lines, warnings
