"""The build's map checks, run straight on the maps in any Doom-format WAD:
no decompiling, so it also takes maps the decompiler refuses.

    python3 scripts/tools/check_wad.py WAD [SLOT ...]      # e.g. wads/SLIGE01.WAD MAP01 MAP08

For each map (or just the slots given): the reach model's checks (the exit,
secret exit and every secret can be reached, every monster can be reached or
come to the player, no damaging floor is a softlock; levels/checks.py
check_reach), things (in a sector, headroom, not clipping walls or each
other; check_things), and non-vanilla thing types and line actions
(check_types). The map is a DOOM map if its slot is ExMy, else DOOM II, and
its textures are that IWAD's (DOOM_WAD / DOOM2_WAD in .env) with the WAD's
own over them. A UMAPINFO lump's `bossaction`s replace the slot's vanilla
boss deaths, as in the build. Sectors are named by number (sector_12).
Exits 1 if any map has a playability finding.
"""
import argparse
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from levels.checks import check_reach, check_things, check_types  # noqa: E402
from levels.decompile import umapinfo_entries  # noqa: E402
from levels.doom2 import SECRET_AREA  # noqa: E402
from levels.reach import solve, umapinfo_boss  # noqa: E402
from levels.wad import IWAD_VARS, IWADS, iwad_textures, read_wad  # noqa: E402
from levels.wadmap import load_maps  # noqa: E402


def reach_textures(game, path):
    """(textures, first texture's height) for the reach model: the game's IWAD
    with the WAD over it, or the IWAD's alone if the WAD's don't read."""
    iwad = IWADS[game]
    if not iwad or not os.path.exists(iwad):
        sys.exit(f"{IWAD_VARS[game]} is not set: add it to .env (see .env.example)")
    found = iwad_textures(iwad, (path,)) or iwad_textures(iwad)
    tx = found[0]
    return tx, next(iter(tx.values()))[1]


def check(m, textures, umapinfo):
    """(summary line, [(kind, finding)]) of one map; umapinfo: its UMAPINFO
    entry (levels.decompile.umapinfo_entries), or None."""
    found = SimpleNamespace(playability=[], style=[], warnings=[])
    names = [f"sector_{i}" for i in range(len(m.sectors))]
    try:
        boss = umapinfo_boss(umapinfo)
    except ValueError as e:
        found.playability.append(f"UMAPINFO {e}")
        boss = None
    md, res = solve(m, textures, boss)
    check_reach(SimpleNamespace(must_reach=[]), md, res, names, found)
    check_types(m, found)
    things = check_things(m, names)
    found.playability += things
    secrets = sum(1 for s in m.sectors if s.special == SECRET_AREA)
    has_secret_exit = any(kind == "secret_exit" for kind, _, _ in md.exits)
    parts = [f"{len(m.sectors)} sectors", f"{len(m.things)} things", f"{secrets} secrets"]
    if md.normal_exit(res):
        parts.append("exit reachable" + (" (running jump)" if md.use_jumps else ""))
    if has_secret_exit:
        parts.append("secret exit " + ("reachable" if md.secret_exit(res) else "UNREACHABLE"))
        if not md.secret_exit(res):
            found.playability.append("the secret exit can't be reached")
    findings = [(k, x) for k, xs in (("playability", found.playability), ("style", found.style),
                                     ("warning", found.warnings)) for x in xs]
    return f"{m.slot}: " + ", ".join(parts), findings


def main():
    ap = argparse.ArgumentParser(description="Run the build's map checks on every map in a WAD.")
    ap.add_argument("wad")
    ap.add_argument("slots", nargs="*", help="only these maps, e.g. MAP01 E1M3")
    args = ap.parse_args()
    lumps = read_wad(args.wad)
    names = [n for n, _ in lumps]
    umapinfo = umapinfo_entries(lumps)
    game = "doom" if any(n.startswith("E") and len(n) == 4 and n[2] == "M" for n in names) else "doom2"
    maps = [m for m in load_maps(game, args.wad) if not args.slots or m.slot in args.slots]
    if not maps:
        sys.exit("no maps" + (f" named {' '.join(args.slots)}" if args.slots else "") + f" in {args.wad}")
    textures = reach_textures(game, args.wad)
    bad = 0
    for m in maps:
        summary, findings = check(m, textures, umapinfo.get(m.slot))
        print(summary)
        for kind, x in findings:
            print(f"  {kind}: {x}")
        bad += any(kind == "playability" for kind, _ in findings)
    print(f"{len(maps) - bad} of {len(maps)} maps with no playability findings")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
