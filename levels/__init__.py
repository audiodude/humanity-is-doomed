"""DOOM II level generator. Levels are data modules in this package; see mapgen.

    from levels import build, nukage_junction
    build(nukage_junction)
"""
from .mapgen import LevelError, build

__all__ = ["LevelError", "build"]
