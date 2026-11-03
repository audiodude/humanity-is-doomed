"""python3 -m levels LEVEL [--check] [--wad WAD] [--map SLOT] [--zdbsp-path PATH]   e.g. python3 -m levels nukage_drain"""
import argparse
import importlib
import sys

from . import LevelError, build
from .mapgen import UDB_ZDBSP

parser = argparse.ArgumentParser(prog="python3 -m levels", description="Validate a level module and build its map.")
parser.add_argument("level", help="level module in levels/, e.g. nukage_outskirts")
parser.add_argument("--check", action="store_true", help="only validate (still writes the SVG preview)")
parser.add_argument("--wad", help="build into this WAD (under wads/, or a path) instead of the set's "
                                  "(levels/sets/); with no set and no --wad: wads/scratch/LEVEL.WAD")
parser.add_argument("--map", metavar="SLOT", help="build into this slot instead of the set's (default: MAP01)")
parser.add_argument("--zdbsp-path", metavar="PATH",
                    help=f"ZDBSP node builder executable (default: {UDB_ZDBSP}, else zdbsp on PATH)")
args = parser.parse_args()
try:
    build(importlib.import_module(f"levels.{args.level}"), check_only=args.check, wad=args.wad, slot=args.map,
          zdbsp=args.zdbsp_path)
except LevelError as e:
    for line in str(e).splitlines():
        print("ERROR:", line)
    sys.exit(1)
