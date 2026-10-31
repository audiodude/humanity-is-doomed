"""DOOM and DOOM II level builder. Levels are data modules in this package (see
mapgen); levels.decompile turns existing maps into such modules.

    from levels import build, nukage_outskirts
    build(nukage_outskirts)
"""
from .mapgen import LevelError, build

__all__ = ["LevelError", "build"]
