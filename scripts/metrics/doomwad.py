"""The vanilla maps in the DOOM / DOOM II IWADs and the other official sets
(TNT, Plutonia, the Master Levels), and the lookup tables the research
scripts use, in their shapes. The map dataclasses and parser live in
levels/wadmap.py and the thing and line-action tables in levels/doom2.py;
this module re-exports both.

Run from the repo root:
    python3 scripts/metrics/doomwad.py              # one summary line per map
    python3 scripts/metrics/doomwad.py --set tnt    # the same for an official set
Use from another script in scripts/metrics/:
    from doomwad import load_all, IWADS
    for m in load_all(): ...

IWAD paths come from DOOM_WAD (Ultimate Doom) and DOOM2_WAD in the repo's
.env or the environment (see .env.example); use the v1.9 IWADs. The other
sets are read from DOOM_STEAM_BASE, the Steam "Ultimate Doom" base/ directory.
Every map carries its set and the WADs it loads with: m.set ("doom", "tnt"),
m.iwad, m.pwads (a tuple) and m.wad, the stem of the WAD its map lumps come
from ("DOOM2", "ATTACK"). with_meta(row, m) appends the per-map metadata
columns (META_COLS, defined in docs/metrics-data.md) to a metrics row.
"""
import csv
import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from levels.doom2 import (ACTORS, AMMO_PICKUPS, ARMOR_PICKUPS, BARREL, DAMAGE_PER_AMMO, DROPS,  # noqa: E402,F401
                          HEALTH_PICKUPS, HITSCANNERS, KEY_OF, LABELS, LIGHT_SPECIALS, LINE_SPECIALS,
                          MAX_STEP, PLAYER1, PLAYERS, SECRET_AREA, SECTOR_DAMAGE, TELEPORT_DEST, LineSpecial)
from levels.doom2 import POWERUPS as POWERUP_TYPES, WEAPONS as WEAPON_TYPES  # noqa: E402
from levels.model import SKY  # noqa: E402,F401
from levels.wad import IWAD_VARS, IWADS, read_env, read_wad  # noqa: E402,F401
from levels.wadmap import (AMBUSH, EASY, HARD, MEDIUM, ML_BLOCKING, ML_BLOCKMONSTERS,  # noqa: E402,F401
                           ML_DONTDRAW, ML_DONTPEGBOTTOM, ML_DONTPEGTOP, ML_MAPPED, ML_SECRET,
                           ML_SOUNDBLOCK, ML_TWOSIDED, MULTI_ONLY, SKILLS, Line, Map, Sector, Side, Thing,
                           load_maps, parse)

# type: (name, health); the boss brain included for completeness.
MONSTERS = {t: (LABELS[t], a.health) for t, a in ACTORS.items() if t not in PLAYERS}
WEAPONS = {t: LABELS[t] for t in WEAPON_TYPES}
POWERUPS = {t: LABELS[t] for t in POWERUP_TYPES}
AMMO, HEALTH, ARMOR, KEYS = AMMO_PICKUPS, HEALTH_PICKUPS, ARMOR_PICKUPS, KEY_OF
PLAYER_STARTS = PLAYERS
SECRET_SPECIAL = SECRET_AREA
DAMAGE_SPECIALS = SECTOR_DAMAGE   # special: damage per 32 tics

# Official sets beyond the 68 IWAD maps: {name: (IWAD, PWAD glob or None)},
# relative to DOOM_STEAM_BASE. All three are DOOM II maps.
SETS = {"tnt": ("tnt/TNT.WAD", None),
        "plutonia": ("plutonia/PLUTONIA.WAD", None),
        "master": ("doom2/DOOM2.WAD", "master/wads/*.WAD")}
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATA = os.path.join(ROOT, "research", "data")    # local research inputs: designers, reception, episode_maps
METRICS = os.path.join(ROOT, "data", "metrics")  # everything the metrics scripts write (tracked)
SETS_DATA = os.path.join(METRICS, "sets")
DECOMPILE_STATUS = os.path.join(METRICS, "decompile_status.csv")   # written by map_svgs.py

# Per-map metadata, appended (in this order) to every row the metrics scripts
# write; docs/metrics-data.md defines each column. Flavors are not here: they
# come from data/metrics/flavors.csv by `set`.
META_COLS = ("set", "game", "slot", "wad", "year", "year_source", "authors", "official", "format",
             "format_evidence", "nonvanilla_specials", "decompile", "progression_valid", "rating", "votes",
             "rating_scope")
# {set: (release year, official)}; E4 came with The Ultimate Doom in 1995.
RELEASES = {"doom": (1993, True), "doom2": (1994, True), "tnt": (1996, True), "plutonia": (1996, True),
            "master": (1995, True)}
VANILLA_LINE_FLAGS = 0x1FF             # ML_BLOCKING .. ML_MAPPED
BOOM_THING_FLAGS = 0x20 | 0x40 | 0x80   # not in deathmatch, not in coop, MBF friendly
MBF21_SPECIALS = range(1024, 1027)      # MBF21's offset scrollers
GENERALIZED = 0x2F80                    # Boom generalized line types run 0x2F80-0x7FFF
JUNK_SPECIAL = 0xFFFF                   # DoomEd leftover (E2M7); does nothing in vanilla
VANILLA_LIMIT = 32767                   # vertex and sidedef indexes are signed 16-bit in vanilla


def _tagged(maps, set_name, iwad, pwads, wad):
    for m in maps:
        m.set, m.iwad, m.pwads, m.wad = set_name, iwad, pwads, wad
    return maps


def load_all():
    return [m for game in ("doom", "doom2") for m in _tagged(load_maps(game), game, IWADS[game], (), game.upper())]


def load_set(name):
    """Every map of an official set (see SETS); a Master Level's map comes
    from its own PWAD, loaded over DOOM2."""
    base = read_env().get("DOOM_STEAM_BASE")
    if not base:
        sys.exit("DOOM_STEAM_BASE is not set: add it to .env (see .env.example)")
    base = os.path.expanduser(base)
    iwad, pwad_glob = (os.path.join(base, p) if p else None for p in SETS[name])
    stem = lambda p: os.path.splitext(os.path.basename(p))[0].upper()   # noqa: E731
    if not pwad_glob:
        return _tagged(load_maps("doom2", iwad), name, iwad, (), stem(iwad))
    return [m for p in sorted(glob.glob(pwad_glob))
            for m in _tagged(load_maps("doom2", p), name, iwad, (p,), stem(p))]


def select(argv, out):
    """(maps, output path, rest of argv): the 68 IWAD maps and `out`, or with
    `--set NAME` that set's maps and data/metrics/sets/NAME/<out's file name>."""
    if "--set" not in argv:
        return load_all(), out, argv
    i = argv.index("--set")
    name = argv[i + 1]
    if name not in SETS:
        sys.exit(f"--set: one of {', '.join(SETS)}")
    return load_set(name), os.path.join(SETS_DATA, name, os.path.basename(out)), argv[:i] + argv[i + 2:]


# ---------------------------------------------------------------- metadata ---
_cache = {}


def _csv(path):
    """Rows of a research CSV, [] if it isn't there (yet)."""
    if path not in _cache:
        _cache[path] = []
        if os.path.exists(path):
            with open(path, newline="") as f:
                _cache[path] = list(csv.DictReader(f))
    return _cache[path]


def _wad_lumps(path):
    key = ("lumps", path)
    if key not in _cache:
        _cache[key] = [n.upper() for n, _ in read_wad(path)]
    return _cache[key]


def map_format(m):
    """(format, evidence, non-vanilla line specials) from the map's line
    specials, thing flags and lumps, and its WAD's COMPLVL, UMAPINFO and
    DEHACKED lumps. UMAPINFO, DEHACKED and line flags are evidence only:
    vanilla ignores high line flags, and id's E2M7 has DoomEd junk in 249 of
    them (0xFE00) plus one special 65535 (JUNK_SPECIAL, also evidence only).
    A COMPLVL lump (vanilla, boom, mbf, mbf21) names the format outright.
    Limit-removing is only seen through index overflow; visplane and drawseg
    limits can't be checked statically."""
    path = m.pwads[-1] if m.pwads else m.iwad
    names = _wad_lumps(path)
    at = names.index(m.slot)
    own = set(names[at + 1:at + 12])
    specials = [ln.special & 0xFFFF for ln in m.lines if ln.special]
    junk = specials.count(JUNK_SPECIAL)
    specials = [s for s in specials if s != JUNK_SPECIAL]
    gen = sum(s >= GENERALIZED for s in specials)
    ext = sum(141 < s < GENERALIZED for s in specials)
    mbf21 = sum(s in MBF21_SPECIALS for s in specials)
    thing_bits = sum(bool(t.flags & BOOM_THING_FLAGS) for t in m.things)
    line_bits = sum(bool(ln.flags & ~VANILLA_LINE_FLAGS & 0xFFFF) for ln in m.lines)
    big = max(len(m.sides), len(m.verts)) > VANILLA_LIMIT
    evidence = [f"{k}={v}" for k, v in (("generalized", gen), ("specials>141", ext), ("mbf21_specials", mbf21),
                                        ("special_65535", junk), ("thing_flags", thing_bits),
                                        ("line_flags", line_bits)) if v]
    evidence += [n for n in ("COMPLVL", "UMAPINFO", "DEHACKED") if n in names]
    if big:
        evidence.append("index>32767")
    complvl = dict(read_wad(path)).get("COMPLVL", b"").decode("ascii", "replace").strip().lower() \
        if "COMPLVL" in names else ""
    if "TEXTMAP" in own:
        fmt = "udmf"
    elif "BEHAVIOR" in own:
        fmt = "hexen"
    elif complvl in ("vanilla", "boom", "mbf", "mbf21"):
        fmt = {"mbf": "boom"}.get(complvl, complvl)
    elif mbf21:
        fmt = "mbf21"
    elif gen or ext or thing_bits:
        fmt = "boom"
    elif big:
        fmt = "limit-removing"
    else:
        fmt = "vanilla"
    return fmt, ";".join(evidence), gen + ext + mbf21


def _authors(m):
    if m.set in ("doom", "doom2"):
        return next((r["designers"] for r in _csv(os.path.join(DATA, "designers.csv")) if r["map"] == m.slot), "")
    # episode_maps.csv (research/episode_metrics.py) credits each official
    # map; match on geometry, since the rerelease reorders the Master Levels.
    return next((r["author"] for r in _csv(os.path.join(DATA, "episode_maps.csv"))
                 if r["set"] == m.set and int(r["linedefs"]) == len(m.lines)
                 and int(r["sectors"]) == len(m.sectors)), "")


def metadata(m):
    """{column: value} for META_COLS."""
    fmt, evidence, nonvanilla = map_format(m)
    year, official = RELEASES[m.set]
    if m.set == "doom" and m.slot.startswith("E4"):
        year = 1995
    status = next((r["decompile"] for r in _csv(DECOMPILE_STATUS)
                   if (r["set"], r["wad"], r["slot"]) == (m.set, m.wad, m.slot)), "")
    rec = next((r for r in _csv(os.path.join(DATA, "reception.csv")) if r["map"] == m.slot), None) \
        if m.set in ("doom", "doom2") else None
    return {"set": m.set, "game": m.game, "slot": m.slot, "wad": m.wad, "year": year,
            "year_source": "official release" if official else "", "authors": _authors(m),
            "official": "true" if official else "false", "format": fmt, "format_evidence": evidence,
            "nonvanilla_specials": nonvanilla, "decompile": status,
            "progression_valid": "true" if all(ln.special in LINE_SPECIALS for ln in m.lines
                                               if ln.special and ln.special & 0xFFFF != JUNK_SPECIAL) else "false",
            "rating": rec["score"] if rec else "", "votes": rec["n_sources"] if rec else "",
            "rating_scope": "per-map" if rec else "none"}


def with_meta(row, m):
    """The row with the metadata columns appended. A column the row already
    has (`game`) keeps its place and takes the metadata value."""
    return {**row, **metadata(m)}


def summary(m):
    hard = m.things_on(HARD)
    mons = [t for t in hard if t.type in MONSTERS]
    secrets = sum(1 for s in m.sectors if s.special == SECRET_SPECIAL)
    x0, y0, x1, y1 = m.bbox
    return (f"{m.slot:6} sectors={len(m.sectors):4} lines={len(m.lines):5} area={sum(m.sector_areas) / 1e6:6.2f}M "
            f"bbox={x1 - x0}x{y1 - y0} uv_monsters={len(mons):3} "
            f"uv_hp={sum(MONSTERS[t.type][1] for t in mons):6} secrets={secrets}")


if __name__ == "__main__":
    for m in select(sys.argv[1:], "")[0]:
        print(m.wad, summary(m))
