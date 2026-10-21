"""python3 -m levels LEVEL [--check]   e.g. python3 -m levels nukage_junction"""
import importlib
import sys

from . import LevelError, build

args = [a for a in sys.argv[1:] if a != "--check"]
if len(args) != 1:
    sys.exit(__doc__)
try:
    build(importlib.import_module(f"levels.{args[0]}"), check_only="--check" in sys.argv)
except LevelError as e:
    for line in str(e).splitlines():
        print("ERROR:", line)
    sys.exit(1)
