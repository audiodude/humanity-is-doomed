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
import multiprocessing as mp
import os
import re
import signal
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from levels.doom2 import (ACTORS, AMMO_PICKUPS, ARMOR_PICKUPS, BARREL, DAMAGE_PER_AMMO, DROPS,  # noqa: E402,F401
                          HEALTH_PICKUPS, HITSCANNERS, KEY_OF, LABELS, LIGHT_SPECIALS, LINE_SPECIALS,
                          MAX_STEP, PLAYER1, PLAYERS, SECRET_AREA, SECTOR_DAMAGE, TELEPORT_DEST, LineSpecial)
from levels.doom2 import POWERUPS as POWERUP_TYPES, WEAPONS as WEAPON_TYPES  # noqa: E402
from levels.model import SKY  # noqa: E402,F401
from levels.wad import IWAD_VARS, IWADS, iwad_textures, read_env, read_wad  # noqa: E402,F401
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


def _tagged(maps, set_name, iwad, pwads, wad, path):
    for m in maps:
        m.set, m.iwad, m.pwads, m.wad, m.path = set_name, iwad, pwads, wad, path
    return maps


def _stem(p):
    return os.path.splitext(os.path.basename(p))[0].upper()


def load_all():
    return [m for game in ("doom", "doom2")
            for m in _tagged(load_maps(game), game, IWADS[game], (), game.upper(), IWADS[game])]


def load_set(name):
    """Every map of an official set (see SETS); a Master Level's map comes
    from its own PWAD, loaded over DOOM2."""
    if name == COMMUNITY:
        return load_community()
    base = read_env().get("DOOM_STEAM_BASE")
    if not base:
        sys.exit("DOOM_STEAM_BASE is not set: add it to .env (see .env.example)")
    base = os.path.expanduser(base)
    iwad, pwad_glob = (os.path.join(base, p) if p else None for p in SETS[name])
    if not pwad_glob:
        return _tagged(load_maps("doom2", iwad), name, iwad, (), _stem(iwad), iwad)
    return [m for p in sorted(glob.glob(pwad_glob))
            for m in _tagged(load_maps("doom2", p), name, iwad, (p,), _stem(p), p)]


def select(argv, out):
    """(maps, output path, rest of argv): the 68 IWAD maps and `out`, or with
    `--set NAME` that set's maps and data/metrics/sets/NAME/<out's file name>.
    NAME is an official set (SETS) or `community` (load_community)."""
    if "--set" not in argv:
        return load_all(), out, argv
    i = argv.index("--set")
    name = argv[i + 1]
    if name not in SETS and name != COMMUNITY:
        sys.exit(f"--set: one of {', '.join([*SETS, COMMUNITY])}")
    return load_set(name), os.path.join(SETS_DATA, name, os.path.basename(out)), argv[:i] + argv[i + 2:]


# --------------------------------------------------------------- community ---
# The rated idgames releases research/fetch_idgames.py downloaded (manifest.csv:
# rating >= 4.0, votes >= 10), each extracted next to its zip. Each release is a
# set, named after its zip ("btsx_e1"); a name in both levels/doom and
# levels/doom2 gets "@doom" on the DOOM one.
COMMUNITY = "community"
IDGAMES = os.path.join(ROOT, "research", "sources", "idgames")
MAP_LUMPS = ("THINGS", "LINEDEFS", "SIDEDEFS", "VERTEXES", "SEGS", "SSECTORS", "NODES", "SECTORS", "REJECT",
             "BLOCKMAP", "BEHAVIOR", "TEXTMAP", "ZNODES", "ENDMAP", "DIALOGUE", "SCRIPTS")
YEAR_LINE = re.compile(r"(?i)\b(release[sd]?|date|completed|finished)\b[^\n]{0,60}?\b(199[3-9]|20[0-3]\d)\b")


def releases():
    """[{manifest row + set, folder, year, year_source}] for the downloaded releases."""
    if "releases" in _cache:
        return _cache["releases"]
    rows = _csv(os.path.join(IDGAMES, "manifest.csv"))
    names = [r["filename"][:-4].lower() for r in rows]
    caco = {}
    for c in _csv(os.path.join(IDGAMES, "cacowards.csv")):
        if c["filename"] and c["source"].isdigit():
            key = (c["dir"], c["filename"])
            caco[key] = min(caco.get(key, 9999), int(c["source"]))
    out = []
    for r, name in zip(rows, names):
        game_dir = r["dir"].split("/")[1]
        folder = os.path.join(IDGAMES, r["dir"][len("levels/"):], r["filename"][:-4])
        if names.count(name) > 1 and game_dir == "doom":
            name += "@doom"
        upload = int(r["date"][:4])
        year, source = upload, "idgames date"
        if (c := caco.get((r["dir"], r["filename"]))) and c <= upload + 1:
            year, source = min(c, upload), "cacowards"
        for txt in sorted(glob.glob(os.path.join(folder, "**", "*.txt"), recursive=True)):
            with open(txt, errors="replace") as f:
                m = YEAR_LINE.search(f.read(20000))
            if m and int(m.group(2)) <= upload:
                year, source = int(m.group(2)), "txt file"
                break
        has_deh = bool([p for p in glob.glob(os.path.join(folder, "**", "*"), recursive=True)
                        if p.lower().endswith((".deh", ".bex"))])
        out.append({**r, "set": name, "game_dir": game_dir, "folder": folder, "year": year,
                    "year_source": source, "has_deh": has_deh})
    _cache["releases"] = out
    return out


def refresh_decompile_column():
    """Rewrite the `decompile` column of every metrics CSV from
    decompile_status.csv, so decompiling (map_svgs.py, slow on community
    maps) and measuring can run in either order."""
    status = {(r["set"], r["wad"], r["slot"]): r["decompile"] for r in _csv_fresh(DECOMPILE_STATUS)}
    paths = glob.glob(os.path.join(METRICS, "metrics_*.csv")) + glob.glob(os.path.join(SETS_DATA, "*", "metrics_*.csv"))
    for path in paths:
        with open(path, "rb") as f:
            ending = "\r\n" if f.readline().endswith(b"\r\n") else "\n"
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            cols, rows = reader.fieldnames, list(reader)
        if "decompile" not in cols:
            continue
        for r in rows:
            r["decompile"] = status.get((r["set"], r["wad"], r["slot"]), "")
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator=ending)
            w.writeheader()
            w.writerows(rows)


def _csv_fresh(path):
    _cache.pop(path, None)
    _cache.pop(("index", "decompile"), None)
    return _csv(path)


def map_markers(lumps):
    """[(slot, {lump: data})] for every ExMy / MAPxx marker."""
    out = []
    for i, (name, _) in enumerate(lumps):
        name = name.upper()
        if (len(name) == 4 and name[0] == "E" and name[2] == "M" and name[1].isdigit() and name[3].isdigit()) or \
                (len(name) == 5 and name.startswith("MAP") and name[3:].isdigit()):
            parts = {}
            for n, d in lumps[i + 1:]:
                if n.upper() not in MAP_LUMPS:
                    break
                parts[n.upper()] = d
            out.append((name, parts))
    return out


def community_inventory():
    """Every map marker of every release: [(release, wad path, slot, format,
    map lumps)], format "doom" (parseable), "udmf", "hexen" or "broken".
    Identical maps (same lumps) repeated within a release are listed once."""
    if "inventory" in _cache:
        return _cache["inventory"]
    out = []
    for rel in releases():
        seen = set()
        rel["wads"] = wads = tuple(sorted(p for p in glob.glob(os.path.join(rel["folder"], "**", "*"),
                                                                recursive=True) if p.lower().endswith(".wad")))
        for p in wads:
            try:
                lumps = read_wad(p)
            except Exception:   # noqa: BLE001  (truncated or not a WAD)
                continue
            for slot, parts in map_markers(lumps):
                key = hash(tuple(sorted(parts.items())))
                if key in seen:
                    continue
                seen.add(key)
                fmt = "udmf" if "TEXTMAP" in parts else "hexen" if "BEHAVIOR" in parts else \
                    "doom" if all(k in parts for k in ("THINGS", "LINEDEFS", "SIDEDEFS", "VERTEXES", "SECTORS")) \
                    else "broken"
                out.append((rel, p, slot, fmt, parts))
    _cache["inventory"] = out
    return out


def load_community():
    """Every Doom-format map of the rated idgames releases, over the IWAD its
    slot needs (ExMy: DOOM_WAD, MAPxx: DOOM2_WAD) with all the release's WADs
    as resources. m.release is its releases() row."""
    maps = []
    for rel, path, slot, fmt, parts in community_inventory():
        if fmt != "doom":
            continue
        game = "doom" if slot[0] == "E" else "doom2"
        try:
            m = parse(game, slot, parts)
        except Exception:   # noqa: BLE001  (malformed lumps)
            continue
        _tagged([m], rel["set"], IWADS[game], rel["wads"], _stem(path), path)
        m.release = rel
        maps.append(m)
    return maps


def parallel_rows(fn, jobs, maps, out, timeout=900):
    """Metrics rows with metadata: fn(job) -> row for each (job, map) on
    every core. A map whose job raises or times out gets no row; it goes to
    errors_<out's name> beside `out` (set, wad, slot, error), which is
    removed when there are none. Prints a count of failures."""
    rows, errors = [], []
    for m, (row, err) in zip(maps, pmap(fn, jobs, timeout)):
        if err is None:
            rows.append(with_meta(row, m))
        else:
            errors.append({"set": m.set, "wad": m.wad, "slot": m.slot, "error": err})
    path = os.path.join(os.path.dirname(out), "errors_" + os.path.basename(out))
    if errors:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(errors[0]))
            w.writeheader()
            w.writerows(errors)
        print(f"{len(errors)} of {len(maps)} maps failed: {os.path.relpath(path)}", file=sys.stderr)
    elif os.path.exists(path):
        os.remove(path)
    return rows


def _reach_tex(key):
    tx = iwad_textures(*key)[0]
    return tx, next(iter(tx.values()))[1]


def reach_textures(maps):
    """{(iwad, pwads): (textures, first texture's height)} for the reach
    model (levels.reach.solve), on every core; a release whose PWAD
    textures don't read gets its IWAD's."""
    keys = sorted({(m.iwad, m.pwads) for m in maps})
    out = {k: t for k, (t, _) in zip(keys, pmap(_reach_tex, keys))}
    for k in [k for k, t in out.items() if t is None]:
        out[k] = _reach_tex((k[0], ()))
    return out


def write_rows(rows, out):
    """Rows to the CSV `out`. Columns follow the longest row, then any
    others; a column a row lacks (a map with no route) is blank."""
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="") as f:
        cols = dict.fromkeys(k for r in sorted(rows, key=len, reverse=True) for k in r)
        w = csv.DictWriter(f, fieldnames=list(cols), restval="")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {os.path.relpath(out)} ({len(rows)} rows)")


def _call(job):
    fn, item, timeout, cpu = job
    if cpu:
        signal.setitimer(signal.ITIMER_PROF, timeout)
    else:
        signal.alarm(timeout)
    try:
        return fn(item), None
    except Exception as e:   # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"[:200]
    finally:
        signal.alarm(0)
        signal.setitimer(signal.ITIMER_PROF, 0)


def _alarm(*_):
    raise TimeoutError("timed out")


def _worker_init():
    signal.signal(signal.SIGALRM, _alarm)
    signal.signal(signal.SIGPROF, _alarm)


def pmap(fn, items, timeout=900, cpu=False):
    """[(result, None) or (None, error)] of fn over items on every core; an
    item that raises or runs past `timeout` seconds gets its error instead.
    The limit is wall-clock time, or with cpu=True the worker's CPU time, so
    a busy machine can't time an item out. fn must be a module-level function."""
    with mp.Pool(os.cpu_count() or 1, initializer=_worker_init, maxtasksperchild=50) as pool:
        return pool.map(_call, [(fn, x, timeout, cpu) for x in items], chunksize=1)




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


def _wad_text_lumps(path):
    """{name: data} of a WAD's COMPLVL and UMAPINFO lumps."""
    key = ("text", path)
    if key not in _cache:
        _cache[key] = {n.upper(): d for n, d in read_wad(path) if n.upper() in ("UMAPINFO", "COMPLVL")}
    return _cache[key]


def _index(name, path, key):
    """{key(row): row} for a CSV, cached."""
    k = ("index", name)
    if k not in _cache:
        _cache[k] = {key(r): r for r in _csv(path)}
    return _cache[k]


def map_format(m):
    """(format, evidence, non-vanilla line specials) from the map's line
    specials, thing flags and lumps, and its WAD's COMPLVL, UMAPINFO and
    DEHACKED lumps. UMAPINFO, DEHACKED and line flags are evidence only:
    vanilla ignores high line flags, and id's E2M7 has DoomEd junk in 249 of
    them (0xFE00) plus one special 65535 (JUNK_SPECIAL, also evidence only).
    A COMPLVL lump (vanilla, boom, mbf, mbf21) names the format outright.
    Limit-removing is only seen through index overflow; visplane and drawseg
    limits can't be checked statically."""
    path = m.path
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
    if getattr(m, "release", None) and m.release["has_deh"]:
        evidence.append("deh_file")
    if big:
        evidence.append("index>32767")
    complvl = _wad_text_lumps(path).get("COMPLVL", b"").decode("ascii", "replace").strip().lower() \
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
        return _index("designers", os.path.join(DATA, "designers.csv"), lambda r: r["map"]).get(
            m.slot, {}).get("designers", "")
    if m.set in SETS:
        # episode_maps.csv (research/episode_metrics.py) credits each official
        # map; match on geometry, since the rerelease reorders the Master Levels.
        return next((r["author"] for r in _csv(os.path.join(DATA, "episode_maps.csv"))
                     if r["set"] == m.set and int(r["linedefs"]) == len(m.lines)
                     and int(r["sectors"]) == len(m.sectors)), "")
    # Community: the map's UMAPINFO author, else the release's.
    if info := _wad_text_lumps(m.path).get("UMAPINFO"):
        entry = re.search(rf"(?is)\bmap\s+{m.slot}\b(.*?)\}}", info.decode("ascii", "replace"))
        if entry and (a := re.search(r'(?i)\bauthor\s*=\s*"([^"]*)"', entry.group(1))):
            return a.group(1)
    return m.release["author"]


def metadata(m):
    """{column: value} for META_COLS."""
    fmt, evidence, nonvanilla = map_format(m)
    if m.set in RELEASES:
        year, official = RELEASES[m.set]
        if m.set == "doom" and m.slot.startswith("E4"):
            year = 1995
        year_source = "official release"
    else:
        year, official, year_source = m.release["year"], False, m.release["year_source"]
    status = _index("decompile", DECOMPILE_STATUS, lambda r: (r["set"], r["wad"], r["slot"])).get(
        (m.set, m.wad, m.slot), {}).get("decompile", "")
    if m.set in ("doom", "doom2"):
        rec = _index("reception", os.path.join(DATA, "reception.csv"), lambda r: r["map"]).get(m.slot)
        rating, votes, scope = (rec["score"], rec["n_sources"], "per-map") if rec else ("", "", "none")
    elif m.set in SETS:
        rating, votes, scope = "", "", "none"
    else:
        rating, votes, scope = m.release["rating"], m.release["votes"], "per-WAD"
    return {"set": m.set, "game": m.game, "slot": m.slot, "wad": m.wad, "year": year,
            "year_source": year_source, "authors": _authors(m),
            "official": "true" if official else "false", "format": fmt, "format_evidence": evidence,
            "nonvanilla_specials": nonvanilla, "decompile": status,
            "progression_valid": "true" if all(ln.special in LINE_SPECIALS for ln in m.lines
                                               if ln.special and ln.special & 0xFFFF != JUNK_SPECIAL) else "false",
            "rating": rating, "votes": votes, "rating_scope": scope}


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
