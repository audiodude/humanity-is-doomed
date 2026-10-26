import os
import sys
import types

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from levels.wad import IWADS  # noqa: E402


def needs_iwad(game):
    path = IWADS[game]
    return pytest.mark.skipif(not path or not os.path.exists(path),
                              reason=f"{'DOOM_WAD' if game == 'doom' else 'DOOM2_WAD'} not set (see .env.example)")


def module(**attrs):
    """A level module made of `attrs`, as level modules are read."""
    mod = types.ModuleType("levels.test_level")
    mod.__dict__.update(MAP="MAP01", WAD="test.wad", **attrs)
    return mod
