"""DOOM and DOOM II level builder. Levels are data modules in this package (see
mapgen); levels.decompile turns existing maps into such modules.

    from levels import build, nukage_junction
    build(nukage_junction)
"""
from .mapgen import LevelError, build

__all__ = ["LevelError", "build"]
