"""Per-map combat, encounter and resource metrics for the 68 vanilla maps
(Ultimate Doom E1M1-E4M9, DOOM II MAP01-MAP32).

Run from the repo root:
    python3 scripts/metrics/combat_metrics.py           # writes the CSVs
    python3 scripts/metrics/combat_metrics.py --summary # also prints the
                                                        # markdown tables used
                                                        # in research/facets/11-quant-combat.md
Outputs:
    research/data/metrics_combat.csv         one row per map
    research/data/combat_first_appearance.csv first map (hard skill) for each
                                              monster and weapon type
    research/data/combat_wiki_validation.csv  monster counts per type and
                                              skill vs the Doom Wiki tables
                                              (only if research/sources/doomwiki/
                                              has the wiki pages)

Skill groups follow the thing flags: easy = bit 1 (ITYTD + HNTR), medium =
bit 2 (HMP), hard = bit 4 (UV + NM). Single player only: MULTI_ONLY things
are skipped. Definitions of every column are in the facet report.
"""
import csv
import math
import os
import re
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from doomwad import (AMBUSH, AMMO, ARMOR, BARREL, DAMAGE_PER_AMMO, DAMAGE_SPECIALS, DROPS,  # noqa: E402
                     EASY, HARD, HEALTH, HITSCANNERS, KEYS, LINE_SPECIALS, MAX_STEP, MEDIUM, ML_BLOCKING,
                     ML_BLOCKMONSTERS, MONSTERS, MULTI_ONLY, POWERUPS, SECRET_SPECIAL, TELEPORT_DEST,
                     WEAPONS, load_all)

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "research")
OUT = os.path.join(ROOT, "data", "metrics_combat.csv")
OUT_FIRST = os.path.join(ROOT, "data", "combat_first_appearance.csv")
OUT_VALID = os.path.join(ROOT, "data", "combat_wiki_validation.csv")
WIKI = os.path.join(ROOT, "sources", "doomwiki")

SKILLS = (("easy", EASY), ("medium", MEDIUM), ("hard", HARD))
AMMO_TYPES = ("bullets", "shells", "rockets", "cells")
START_AMMO = {"bullets": 50}          # pistol start: pistol + 50 bullets
BOSS_BRAIN = 88                       # Icon of Sin: not a kill, not counted
BOSSES = {7, 16}                      # spider mastermind, cyberdemon
FODDER_MAX_HP = 99                    # zombieman, shotgun guy, SS, imp, chaingunner
HEAVY_MIN_HP = 400                    # caco, pain elemental and up (bosses excluded)
IMP = 3001
PLAYER1 = 1
TELEPORT_LINES = {39, 97, 125, 126}
TAG_TRIGGERS = {"W1", "WR", "S1", "SR", "G1", "GR"}
# Line kinds that can open a sealed sector or move monsters into reach.
MOVER_KINDS = {"door", "floor_lower", "floor_raise", "ceiling_raise", "lift", "platform", "stairs", "donut"}
WALKABLE_HEIGHT = 56                  # player height
LEDGE_HEIGHT = 64
CLOSET_MAX_AREA = 512 * 512          # sealed regions up to this walkable area are closets
PICKUPS = set(AMMO) | set(HEALTH) | set(ARMOR) | set(POWERUPS) | set(WEAPONS) | set(KEYS)
# Which ammo each weapon fires; pistol (bullets) is always present.
WEAPON_AMMO = {2001: "shells", 82: "shells", 2002: "bullets", 2003: "rockets", 2004: "cells", 2006: "cells"}
# Weapons a monster drops when it dies.
DROP_WEAPON = {9: 2001, 65: 2002}

WIKI_NAMES = {
    "zombieman": 3004, "shotgun guy": 9, "heavy weapon dude": 65, "wolfenstein ss": 84, "imp": 3001,
    "demon": 3002, "spectre": 58, "lost soul": 3006, "cacodemon": 3005, "hell knight": 69,
    "baron of hell": 3003, "arachnotron": 68, "pain elemental": 71, "revenant": 66, "mancubus": 67,
    "arch-vile": 64, "spiderdemon": 7, "cyberdemon": 16, "commander keen": 72, "romero's head": BOSS_BRAIN,
    "chainsaw": 2005, "shotgun": 2001, "super shotgun": 82, "chaingun": 2002, "rocket launcher": 2003,
    "plasma gun": 2004, "bfg9000": 2006,
}


# ------------------------------------------------------------------ helpers ---
def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def r(x, nd=3):
    if x is None:
        return ""
    return round(x, nd)


def ratio(a, b):
    return a / b if b else None


def stair_chain(m, tagged):
    """Sectors raised by a stair build: each tagged sector, then (as in
    EV_BuildStairs) the back sector of any two-sided line fronted by the
    current step that shares its floor flat, repeatedly."""
    out = set()
    for s in tagged:
        cur, flat = s, m.sectors[s].ftex
        out.add(cur)
        while True:
            nxt = None
            for ln in m.lines:
                f, b = m.line_sectors(ln)
                if f == cur and b is not None and b not in out and m.sectors[b].ftex == flat:
                    nxt = b
                    break
            if nxt is None:
                break
            out.add(nxt)
            cur = nxt
    return out


class Geometry:
    """Per-map sector bookkeeping shared by the metrics."""

    def __init__(self, m):
        self.m = m
        sec = m.sectors
        self.nb = m.neighbours()
        self.area = m.sector_areas
        # Thing -> sector (cached by position).
        self._pos = {}
        # Line specials.
        self.manual_door_sectors = set()
        self.tag_door_sectors = set()
        self.movers = []       # (line index, LineSpecial) for tagged mover triggers
        self.tele_lines = []   # (line index) teleport lines with a destination
        dest_sectors = {self.sector(t) for t in m.things if t.type == TELEPORT_DEST}
        self.dest_sectors = dest_sectors - {None}
        for i, ln in enumerate(m.lines):
            sp = LINE_SPECIALS.get(ln.special)
            if not sp:
                continue
            f, b = m.line_sectors(ln)
            if sp.trigger == "D" and sp.kind == "door" and b is not None:
                self.manual_door_sectors.add(b)
            if sp.tagged and sp.kind == "door":
                self.tag_door_sectors.update(m.tagged(ln.tag))
            if sp.trigger in TAG_TRIGGERS and sp.kind in MOVER_KINDS and ln.tag:
                self.movers.append((i, sp))
            if ln.special in TELEPORT_LINES and set(m.tagged(ln.tag)) & self.dest_sectors:
                self.tele_lines.append(i)
        self.door_sectors = self.manual_door_sectors | self.tag_door_sectors
        self.walkable = [s.ceil - s.floor >= WALKABLE_HEIGHT or i in self.door_sectors
                         for i, s in enumerate(sec)]
        self.walkable_area = sum(a for a, w in zip(self.area, self.walkable) if w)
        # Regions: sectors joined by two-sided lines with a non-zero opening.
        parent = list(range(len(sec)))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        self.zero_lines = []
        for i, ln in enumerate(m.lines):
            f, b = m.line_sectors(ln)
            if b is None or b == f:
                continue
            opening = min(sec[f].ceil, sec[b].ceil) - max(sec[f].floor, sec[b].floor)
            if opening > 0:
                parent[find(f)] = find(b)
            else:
                self.zero_lines.append((i, f, b))
        self.region = [find(i) for i in range(len(sec))]
        self.members = defaultdict(set)
        for i, g in enumerate(self.region):
            self.members[g].add(i)
        # Seals: sectors outside a region across a zero-opening line.
        self.seals = defaultdict(set)
        for i, f, b in self.zero_lines:
            if self.region[f] != self.region[b]:
                self.seals[self.region[f]].add(b)
                self.seals[self.region[b]].add(f)
        # Sectors that a trigger can move (doors, lifts, floors, stair chains).
        self.moved = set(self.door_sectors)
        for i, sp in self.movers:
            tagged = m.tagged(m.lines[i].tag)
            self.moved.update(stair_chain(m, tagged) if sp.kind == "stairs" else tagged)
        self.reach = self._player_reach()
        # Secret areas: secret sectors plus everything the player can only
        # reach by passing through one.
        self.secret_sectors = {i for i, s in enumerate(sec) if s.special == SECRET_SPECIAL}
        self.secret_area = self.secret_sectors | (self.reach - self._player_reach(self.secret_sectors))
        # Monster movement regions: sectors joined where a monster can walk
        # (no blocking flags, 56+ opening, at most 24 up or down), treating
        # trigger-moved sectors as open.
        parent = list(range(len(sec)))
        for ln in m.lines:
            f, b = m.line_sectors(ln)
            if b is None or b == f or ln.flags & (ML_BLOCKING | ML_BLOCKMONSTERS):
                continue
            if f in self.moved or b in self.moved or (
                    min(sec[f].ceil, sec[b].ceil) - max(sec[f].floor, sec[b].floor) >= WALKABLE_HEIGHT
                    and abs(sec[f].floor - sec[b].floor) <= MAX_STEP):
                parent[find(f)] = find(b)
        self.mregion = [find(i) for i in range(len(sec))]

    def _player_reach(self, blocked=frozenset()):
        """Sectors the player can enter from the player-1 start, assuming every
        door, lift and tagged mover can be operated (keys found) and following
        player teleporters (39, 97) to their destination sectors. `blocked`
        sectors are never entered."""
        m, sec = self.m, self.m.sectors
        adj, tele = defaultdict(set), defaultdict(set)
        for ln in m.lines:
            f, b = m.line_sectors(ln)
            if ln.special in (39, 97):
                dests = set(m.tagged(ln.tag)) & self.dest_sectors
                for s in (f, b):
                    if s is not None:
                        tele[s] |= dests
            if b is None or b == f or ln.flags & ML_BLOCKING:
                continue
            for a, c in ((f, b), (b, f)):
                if a in self.moved or c in self.moved:
                    adj[a].add(c)
                elif (min(sec[a].ceil, sec[c].ceil) - max(sec[a].floor, sec[c].floor) >= WALKABLE_HEIGHT
                      and sec[c].floor - sec[a].floor <= MAX_STEP):
                    adj[a].add(c)
        p1 = next(t for t in m.things if t.type == PLAYER1)
        start = self.sector(p1)
        seen, todo = {start}, [start]
        while todo:
            a = todo.pop()
            for c in adj[a] | tele[a]:
                if c not in seen and c not in blocked:
                    seen.add(c)
                    todo.append(c)
        return seen

    def sector(self, t):
        key = (t.x, t.y)
        if key not in self._pos:
            self._pos[key] = self.m.sector_of_point(t.x, t.y)
        return self._pos[key]


# ------------------------------------------------------------- per-map rows ---
def map_metrics(m, first_seen):
    g = Geometry(m)
    sec = m.sectors
    row = {"map": m.slot, "game": "DOOM" if m.game == "doom" else "DOOM II"}
    p1 = next((t for t in m.things if t.type == PLAYER1), None)
    secret_sectors = g.secret_sectors
    row["secret_sectors"] = len(secret_sectors)
    row["secret_area_sectors"] = len(g.secret_area)

    # --- 1-2: monsters, ammo, health and armour for each skill -------------
    per = {}
    for name, bit in SKILLS:
        things = m.things_on(bit)
        mons = [t for t in things if t.type in MONSTERS and t.type != BOSS_BRAIN]
        hp = sum(MONSTERS[t.type][1] for t in mons)
        ammo = Counter()
        for t in things:
            for k, n in AMMO.get(t.type, {}).items():
                ammo[k] += n
            for k, n in DROPS.get(t.type, {}).items():
                ammo[k] += n
        dmg = sum(DAMAGE_PER_AMMO[k] * n for k, n in ammo.items())
        start_dmg = sum(DAMAGE_PER_AMMO[k] * n for k, n in START_AMMO.items())
        health = sum(HEALTH.get(t.type, 0) for t in things)
        armor = sum(ARMOR.get(t.type, 0) for t in things)
        per[name] = dict(things=things, mons=mons, hp=hp, ammo=ammo, dmg=dmg)
        row[f"monsters_{name}"] = len(mons)
        row[f"monster_hp_{name}"] = hp
        for k in AMMO_TYPES:
            row[f"{k}_{name}"] = ammo[k]
        row[f"ammo_damage_{name}"] = dmg
        row[f"ammo_ratio_{name}"] = r(ratio(dmg, hp))
        row[f"ammo_ratio_ps_{name}"] = r(ratio(dmg + start_dmg, hp))
        row[f"health_{name}"] = health
        row[f"armor_{name}"] = armor
        row[f"health_per_khp_{name}"] = r(ratio(health * 1000, hp), 1)
        row[f"armor_per_khp_{name}"] = r(ratio(armor * 1000, hp), 1)
    h = per["hard"]
    for a, b in (("easy", "hard"), ("medium", "hard")):
        row[f"count_ratio_{a}_{b}"] = r(ratio(len(per[a]["mons"]), len(per[b]["mons"])))
        row[f"hp_ratio_{a}_{b}"] = r(ratio(per[a]["hp"], per[b]["hp"]))
    for k in AMMO_TYPES:
        row[f"ammo_share_{k}_hard"] = r(ratio(DAMAGE_PER_AMMO[k] * h["ammo"][k], h["dmg"]))

    # --- composition (hard) -------------------------------------------------
    mons, n = h["mons"], len(h["mons"])
    hp = h["hp"]
    types = Counter(t.type for t in mons)
    row["monster_types_hard"] = len(types)
    tier = lambda t: ("boss" if t.type in BOSSES else "fodder" if MONSTERS[t.type][1] <= FODDER_MAX_HP
                      else "heavy" if MONSTERS[t.type][1] >= HEAVY_MIN_HP else "mid")
    tiers = Counter(tier(t) for t in mons)
    tier_hp = Counter()
    for t in mons:
        tier_hp[tier(t)] += MONSTERS[t.type][1]
    row["share_hitscan_hard"] = r(ratio(sum(t.type in HITSCANNERS for t in mons), n))
    row["share_imp_hard"] = r(ratio(types[IMP], n))
    for k in ("fodder", "mid", "heavy", "boss"):
        row[f"share_{k}_hard"] = r(ratio(tiers[k], n))
    row["hp_share_heavy_hard"] = r(ratio(tier_hp["heavy"], hp))
    row["hp_share_boss_hard"] = r(ratio(tier_hp["boss"], hp))
    row["boss_count_hard"] = tiers["boss"]
    row["mean_monster_hp_hard"] = r(ratio(hp, n), 1)
    row["walkable_area_mu2"] = r(g.walkable_area / 1e6)
    row["hp_density_hard"] = r(ratio(hp, g.walkable_area / 1e6), 1)
    row["monster_density_hard"] = r(ratio(n, g.walkable_area / 1e6), 2)
    row["barrels_hard"] = sum(t.type == BARREL for t in h["things"])
    seen = {("monster", MONSTERS[t][0]) for t in types}

    # --- 3: weapons and power-ups (pistol start, hard) ----------------------
    weapons = [t for t in h["things"] if t.type in WEAPONS]
    wtypes = sorted({t.type for t in weapons}, key=lambda x: list(WEAPONS).index(x))
    row["weapons_hard"] = ";".join(WEAPONS[w] for w in wtypes)
    via_drop = {DROP_WEAPON[t.type] for t in mons if t.type in DROP_WEAPON} - set(wtypes)
    row["weapons_drop_only_hard"] = ";".join(WEAPONS[w] for w in sorted(via_drop, key=lambda x: list(WEAPONS).index(x)))
    have = set(wtypes) | via_drop
    seen |= {("weapon_pickup", WEAPONS[w]) for w in wtypes}
    seen |= {("weapon_incl_drops", WEAPONS[w]) for w in have}
    seen |= {("powerup", POWERUPS[t.type]) for t in h["things"] if t.type in POWERUPS}
    for key in seen:
        first_seen.setdefault((m.game, *key), m.slot)
    for w, wn in WEAPONS.items():
        ds = [dist(p1, t) for t in weapons if t.type == w]
        row[f"dist_{wn}"] = r(min(ds), 0) if ds else ""
    near = min(weapons, key=lambda t: dist(p1, t), default=None)
    row["nearest_weapon"] = WEAPONS[near.type] if near else ""
    row["nearest_weapon_dist"] = r(dist(p1, near), 0) if near else ""
    pw = Counter(POWERUPS[t.type] for t in h["things"] if t.type in POWERUPS)
    row["powerups_hard"] = ";".join(f"{k}x{v}" if v > 1 else k for k, v in sorted(pw.items()))
    row["powerup_count_hard"] = sum(pw.values())
    # Ammo whose weapon is obtainable (pickup or monster drop) on a pistol start.
    usable = {"bullets"} | {WEAPON_AMMO[w] for w in have if w in WEAPON_AMMO}
    usable_dmg = sum(DAMAGE_PER_AMMO[k] * (h["ammo"][k] + START_AMMO.get(k, 0)) for k in usable)
    row["usable_ammo_ratio_ps_hard"] = r(ratio(usable_dmg, hp))

    # --- 4: secrets as resource valves (hard) -------------------------------
    # Two scopes: things standing in a secret-flagged sector, and things in
    # the secret area (flagged sectors plus sectors gated behind them).
    things = h["things"]
    values = {"health": lambda t: HEALTH.get(t.type, 0), "armor": lambda t: ARMOR.get(t.type, 0),
              "ammo": lambda t: sum(DAMAGE_PER_AMMO[k] * n for k, n in AMMO.get(t.type, {}).items()),
              "powerups": lambda t: t.type in POWERUPS}
    for scope, area in (("secret", secret_sectors), ("secret_area", g.secret_area)):
        for name, val in values.items():
            tot = sum(val(t) for t in things)
            row[f"{scope}_share_{name}_hard"] = r(ratio(sum(val(t) for t in things if g.sector(t) in area), tot))
    in_area = lambda t: g.sector(t) in g.secret_area
    row["secret_area_weapons_hard"] = sum(1 for t in weapons if in_area(t))
    secret_only = [w for w in wtypes if all(in_area(t) for t in weapons if t.type == w)]
    row["secret_only_weapons_hard"] = ";".join(WEAPONS[w] for w in secret_only)
    outside = {("weapon_outside_secret", WEAPONS[w]) for w in wtypes if w not in secret_only}
    seen |= outside
    for key in outside:
        first_seen.setdefault((m.game, *key), m.slot)

    # --- 5: encounter structure (hard) --------------------------------------
    p1_region = g.region[g.sector(p1)]
    row["ambush_share_hard"] = r(ratio(sum(bool(t.flags & AMBUSH) for t in mons), n))
    mon_sector = [g.sector(t) for t in mons]
    mon_regions = {g.region[s] for s in mon_sector if s is not None}
    # Sealed regions: non-start regions with no manual door on their seal,
    # released by a tagged mover trigger acting on the region or its seal,
    # from a line outside the region.
    sealed_kind, region_area = {}, {}
    for reg in mon_regions:
        if reg == p1_region or g.seals[reg] & g.manual_door_sectors:
            continue
        inside = g.members[reg]
        targets = inside | g.seals[reg]
        trig = set()
        for i, sp in g.movers:
            ln = m.lines[i]
            f, b = m.line_sectors(ln)
            if f in inside or b in inside:
                continue
            if set(m.tagged(ln.tag)) & targets:
                trig.add(sp.trigger[0])
        if trig:
            sealed_kind[reg] = "walk" if trig & {"W", "G"} else "switch"
            region_area[reg] = sum(g.area[s] for s in inside if g.walkable[s])
    # Unreachable monsters: outside the player's reach and in a monster
    # movement region without any single-player pickup (regions with pickups
    # are treated as player space, guarding against reachability misses).
    pickups = [t for t in m.things if t.type in PICKUPS and t.flags & (EASY | MEDIUM | HARD)
               and not t.flags & MULTI_ONLY]
    item_mregions = {g.mregion[s] for s in map(g.sector, pickups) if s is not None}
    row["reach_qa_unreached_items"] = sum(1 for t in pickups if g.sector(t) not in g.reach)
    # Teleport feeders: unreachable monsters whose movement region touches a
    # teleport line (39/97/125/126) that has a destination.
    tele_mregions = set()
    for i in g.tele_lines:
        for s in m.line_sectors(m.lines[i]):
            if s is not None:
                tele_mregions.add(g.mregion[s])
    reg_of = lambda s: g.region[s] if s is not None else None
    sealed = [reg_of(s) in sealed_kind for s in mon_sector]
    closet = [reg_of(s) in sealed_kind and region_area[reg_of(s)] <= CLOSET_MAX_AREA for s in mon_sector]
    closet_walk = [c and sealed_kind[reg_of(s)] == "walk" for c, s in zip(closet, mon_sector)]
    unreach = [s is not None and s not in g.reach and g.mregion[s] not in item_mregions for s in mon_sector]
    tele = [u and g.mregion[s] in tele_mregions for u, s in zip(unreach, mon_sector)]
    trap = [a or b for a, b in zip(closet, tele)]
    row["sealed_trigger_share_hard"] = r(ratio(sum(sealed), n))
    row["closet_share_hard"] = r(ratio(sum(closet), n))
    row["closet_walk_share_hard"] = r(ratio(sum(closet_walk), n))
    row["teleport_share_hard"] = r(ratio(sum(tele), n))
    row["trap_share_hard"] = r(ratio(sum(trap), n))
    row["trap_hp_share_hard"] = r(ratio(sum(MONSTERS[t.type][1] for t, x in zip(mons, trap) if x), hp))
    row["unreachable_share_hard"] = r(ratio(sum(unreach), n))
    row["start_region_share_hard"] = r(ratio(sum(reg_of(s) == p1_region for s in mon_sector), n))
    row["reachable_sector_share"] = r(len(g.reach) / len(sec))
    # Trigger lines that open/move sectors holding monsters or sealing them in.
    hot = {s for s in mon_sector if s is not None}
    for reg in mon_regions:
        if reg != p1_region:
            hot |= g.seals[reg]
    release = [i for i, sp in g.movers if set(m.tagged(m.lines[i].tag)) & hot]
    row["release_lines_hard"] = len(release)
    row["release_lines_walk_hard"] = sum(1 for i in release if LINE_SPECIALS[m.lines[i].special].trigger[0] in "WG")
    row["teleport_lines"] = len(g.tele_lines)
    row["monster_only_teleport_lines"] = sum(1 for i in g.tele_lines if m.lines[i].special in (125, 126))

    # --- 6: early pressure (hard) --------------------------------------------
    d = [dist(p1, t) for t in mons]
    row["hp_within_1024_hard"] = sum(MONSTERS[t.type][1] for t, x in zip(mons, d) if x <= 1024)
    row["hp_within_2048_hard"] = sum(MONSTERS[t.type][1] for t, x in zip(mons, d) if x <= 2048)
    row["hp_share_within_1024_hard"] = r(ratio(row["hp_within_1024_hard"], hp))
    row["monsters_within_1024_hard"] = sum(x <= 1024 for x in d)
    row["nearest_monster_dist_hard"] = r(min(d), 0) if d else ""

    # --- 7: elevation and hazards (hard) -------------------------------------
    strict = loose = hazard = sniper = 0
    for s in mon_sector:
        if s is None:
            continue
        fl = sec[s].floor
        nfl = [sec[x].floor for x in g.nb.get(s, {}) if sec[x].ceil > sec[x].floor]
        if nfl and all(fl - f >= LEDGE_HEIGHT for f in nfl):
            strict += 1
        if nfl and fl - min(nfl) >= LEDGE_HEIGHT:
            loose += 1
            sniper += s not in g.reach and g.mregion[s] not in item_mregions
        if sec[s].special in DAMAGE_SPECIALS:
            hazard += 1
    row["ledge_strict_share_hard"] = r(ratio(strict, n))
    row["ledge_loose_share_hard"] = r(ratio(loose, n))
    row["sniper_share_hard"] = r(ratio(sniper, n))
    row["damaging_floor_share_hard"] = r(ratio(hazard, n))
    p1s = g.sector(p1)
    row["above_start_share_hard"] = r(ratio(sum(s is not None and sec[s].floor - sec[p1s].floor >= LEDGE_HEIGHT
                                                for s in mon_sector), n))
    row["unplaced_things"] = sum(g.sector(t) is None for t in m.things if not t.flags & MULTI_ONLY)
    return row, seen


# --------------------------------------------------------- wiki validation ---
def wiki_counts(slot):
    """{type: (easy, medium, hard)} for monsters and weapons in the Doom Wiki
    single-player things table (columns 1-2, 3, 4-5)."""
    text = open(os.path.join(WIKI, f"{slot}.wiki"), encoding="utf-8").read()
    start = text.index('colspan="4"|Single-player')
    end = text.index("{{col-break", start)
    out = {}
    for line in text[start:end].splitlines():
        mm = re.match(r'\|style="text-align: left;"\|\[\[([^\]|]+)(?:\|[^\]]*)?\]\]\|\|(.*)', line)
        if not mm:
            continue
        typ = WIKI_NAMES.get(mm.group(1).strip().lower())
        if typ is None:
            continue
        vals = []
        for cell in mm.group(2).split("||"):
            cm = re.match(r'\s*colspan="(\d)"\|\s*(\d+)', cell)
            if cm:
                vals += [int(cm.group(2))] * int(cm.group(1))
            else:
                vals.append(int(cell.strip()))
        out[typ] = tuple(vals)
    return out


def validate(m):
    rows = []
    wiki = wiki_counts(m.slot)
    ours = {}
    for k, (name, bit) in enumerate(SKILLS):
        for t in m.things_on(bit):
            if t.type in MONSTERS or t.type in WEAPONS:
                ours.setdefault(t.type, [0, 0, 0])[k] += 1
    for typ in sorted(set(wiki) | set(ours), key=lambda x: (x in WEAPONS, MONSTERS.get(x, ("", x))[1])):
        w = wiki.get(typ, (0, 0, 0))
        o = tuple(ours.get(typ, (0, 0, 0)))
        rows.append({"map": m.slot, "kind": "weapon" if typ in WEAPONS else "monster",
                     "type": WEAPONS[typ] if typ in WEAPONS else MONSTERS[typ][0],
                     "wad_easy": o[0], "wad_medium": o[1], "wad_hard": o[2],
                     "wiki_easy": w[0], "wiki_medium": w[1], "wiki_hard": w[2], "match": int(o == tuple(w))})
    return rows


# ---------------------------------------------------------------- summary ---
def group_of(slot):
    if slot.startswith("E"):
        return slot[:2]
    n = int(slot[3:])
    return ("MAP01-06" if n <= 6 else "MAP07-11" if n <= 11 else "MAP12-20" if n <= 20
            else "MAP21-30" if n <= 30 else "MAP31-32")


def num(v):
    return None if v in ("", None) else float(v)


def fmt(v):
    if v is None:
        return "–"
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:.2f}"


def quart(vals):
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return None, None, None
    if len(vals) < 4:
        med = statistics.median(vals)
        return med, med, med
    q = statistics.quantiles(vals, n=4, method="inclusive")
    return q[0], q[1], q[2]


KEY = ["monsters_hard", "monster_hp_hard", "count_ratio_easy_hard", "count_ratio_medium_hard",
       "hp_ratio_easy_hard", "monster_types_hard", "share_hitscan_hard", "share_fodder_hard",
       "share_heavy_hard", "hp_share_heavy_hard", "hp_density_hard", "ammo_ratio_hard",
       "ammo_ratio_ps_hard", "ammo_ratio_ps_easy", "usable_ammo_ratio_ps_hard", "health_per_khp_hard",
       "health_per_khp_easy", "armor_per_khp_hard", "secret_share_health_hard", "secret_share_armor_hard",
       "secret_share_ammo_hard", "secret_share_powerups_hard", "secret_area_share_health_hard",
       "secret_area_share_armor_hard", "secret_area_share_ammo_hard", "secret_area_share_powerups_hard",
       "ambush_share_hard",
       "sealed_trigger_share_hard", "closet_share_hard", "closet_walk_share_hard", "teleport_share_hard",
       "trap_share_hard", "trap_hp_share_hard", "unreachable_share_hard", "release_lines_hard",
       "hp_within_1024_hard", "hp_share_within_1024_hard", "nearest_monster_dist_hard",
       "nearest_weapon_dist", "ledge_strict_share_hard", "ledge_loose_share_hard", "sniper_share_hard",
       "above_start_share_hard", "damaging_floor_share_hard", "powerup_count_hard", "barrels_hard"]
TOPBOTTOM = ["monster_hp_hard", "hp_density_hard", "ammo_ratio_ps_hard", "health_per_khp_hard",
             "armor_per_khp_hard", "count_ratio_easy_hard", "share_hitscan_hard", "hp_share_heavy_hard",
             "ambush_share_hard", "closet_share_hard", "teleport_share_hard", "trap_share_hard",
             "unreachable_share_hard", "hp_within_1024_hard", "nearest_monster_dist_hard",
             "nearest_weapon_dist", "ledge_loose_share_hard", "secret_area_share_health_hard",
             "secret_area_share_ammo_hard", "secret_area_share_armor_hard"]


def summary(rows, first, valid):
    p = print
    games = {"DOOM": [r_ for r_ in rows if r_["game"] == "DOOM"],
             "DOOM II": [r_ for r_ in rows if r_["game"] == "DOOM II"]}
    p("### DOOM vs DOOM II (median [Q1–Q3])\n")
    p("| Metric | DOOM | DOOM II | All 68 |\n|---|---|---|---|")
    for k in KEY:
        cells = []
        for grp in (games["DOOM"], games["DOOM II"], rows):
            q1, md, q3 = quart([num(x[k]) for x in grp])
            cells.append(f"{fmt(md)} [{fmt(q1)}–{fmt(q3)}]")
        p(f"| {k} | " + " | ".join(cells) + " |")
    groups = []
    for x in rows:
        if group_of(x["map"]) not in groups:
            groups.append(group_of(x["map"]))
    p("\n### Per-episode / chapter medians\n")
    p("| Metric | " + " | ".join(groups) + " |\n|---|" + "---|" * len(groups))
    for k in KEY:
        cells = [fmt(quart([num(x[k]) for x in rows if group_of(x["map"]) == gname])[1]) for gname in groups]
        p(f"| {k} | " + " | ".join(cells) + " |")
    p("\n### Top / bottom 5\n")
    p("| Metric | Top 5 (highest) | Bottom 5 (lowest) |\n|---|---|---|")
    for k in TOPBOTTOM:
        vals = [(num(x[k]), x["map"]) for x in rows if num(x[k]) is not None]
        vals.sort(key=lambda v: (-v[0], v[1]))
        top = ", ".join(f"{s} {fmt(v)}" for v, s in vals[:5])
        bot = ", ".join(f"{s} {fmt(v)}" for v, s in sorted(vals, key=lambda v: (v[0], v[1]))[:5])
        p(f"| {k} | {top} | {bot} |")
    p("\n### First appearance (hard skill, single player)\n")
    p("| Kind | Type | DOOM | DOOM II |\n|---|---|---|---|")
    keys = sorted({(k, t) for g_, k, t in first}, key=lambda kt: (kt[0], first.get(("doom", *kt), "Z"),
                                                                   first.get(("doom2", *kt), "Z")))
    for kind, t in keys:
        p(f"| {kind} | {t} | {first.get(('doom', kind, t), '–')} | {first.get(('doom2', kind, t), '–')} |")
    bad = [v for v in valid if not v["match"]]
    for kind in ("monster", "weapon"):
        rows_k = [v for v in valid if v["kind"] == kind]
        p(f"\nWiki validation ({kind}s): {sum(v['match'] for v in rows_k)}/{len(rows_k)} (map, type) rows "
          "match on all three skill columns")
    for v in bad:
        p(f"- {v['map']} {v['type']}: wad {v['wad_easy']}/{v['wad_medium']}/{v['wad_hard']} "
          f"vs wiki {v['wiki_easy']}/{v['wiki_medium']}/{v['wiki_hard']}")


def main():
    maps = load_all()
    order = [f"E{e}M{i}" for e in range(1, 5) for i in range(1, 10)] + [f"MAP{i:02d}" for i in range(1, 33)]
    maps.sort(key=lambda m: order.index(m.slot))
    assert [m.slot for m in maps] == order, "expected all 68 maps"
    first, rows, valid, present = {}, [], [], Counter()
    for m in maps:
        row, seen = map_metrics(m, first)
        rows.append(row)
        if os.path.isdir(WIKI):
            valid += validate(m)
        present.update((m.game, kind, t) for kind, t in seen)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(OUT_FIRST, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["game", "kind", "type", "first_map", "maps_present"])
        for key, slot in sorted(first.items(), key=lambda kv: (kv[0][0], kv[0][1], order.index(kv[1]))):
            w.writerow([*key, slot, present[key]])
    if valid:
        with open(OUT_VALID, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(valid[0]))
            w.writeheader()
            w.writerows(valid)
    if "--summary" in sys.argv:
        summary(rows, first, valid)
    else:
        print(f"wrote {OUT} ({len(rows)} rows), {OUT_FIRST}" + (f", {OUT_VALID}" if valid else
              f"; no Doom Wiki pages in {WIKI}, so the validation was skipped"))


if __name__ == "__main__":
    main()
