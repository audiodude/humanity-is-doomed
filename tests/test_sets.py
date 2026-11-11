"""Set lists (levels/sets): where each level module builds."""
import importlib.util

import pytest
from conftest import module

from levels.doom2 import PLAYER1, W1_EXIT
from levels.model import LevelError, Place, Sector, Special, Thing, load, rect
from levels.sets import all_sets, place
from levels.wad import umapinfo_lump


def test_every_set_names_modules_that_exist_once_each():
    seen = {}
    for s in all_sets():
        for slot, name in s.MAPS.items():
            assert importlib.util.find_spec(f"levels.{name}"), f"{s.__name__} {slot}: no module levels.{name}"
            assert name not in seen, f"{name} is in {seen[name]} and {s.__name__}"
            seen[name] = s.__name__


def test_explicit_wad_or_slot_beats_the_set_and_no_set_is_a_scratch_build():
    from levels.sets import nukage
    slot = next(k for k, v in nukage.MAPS.items() if v == "nukage_storage")
    assert place("nukage_storage") == Place("NUKAGE.WAD", slot, nukage.UMAPINFO.get(slot, ""))
    assert place("nukage_storage", slot="map03") == Place("scratch/nukage_storage.WAD", "MAP03")
    assert place("nukage_storage", wad="/tmp/x.wad") == Place("/tmp/x.wad", "MAP01")
    assert place("nukage_junction") == Place("scratch/nukage_junction.WAD", "MAP01", scratch=True)


def room(**attrs):
    return module(SECTORS=[Sector("room", [rect(0, 0, 512, 512)], 0, 128, "FLOOR4_8", "CEIL3_5", 160, "STARTAN3")],
                  FREE_LINES={((256, 400), (320, 400)): Special(W1_EXIT)}, THINGS=[Thing(PLAYER1, 64, 64)], **attrs)


@pytest.mark.parametrize("umapinfo", [{"levelname": "Pump Hall"}, 'levelname = "Pump Hall"'])
def test_the_sets_lines_for_a_slot_join_the_maps_umapinfo_entry(umapinfo):
    level = load(room(UMAPINFO=umapinfo), Place("t.wad", "MAP06", "intertext = clear"))
    entry = umapinfo_lump(level).decode()
    assert entry.startswith("MAP MAP06\n{") and 'levelname = "Pump Hall"' in entry and "intertext = clear" in entry


def test_a_key_both_the_map_and_its_set_set_is_an_error():
    with pytest.raises(LevelError, match="UMAPINFO intertext: set by"):
        load(room(UMAPINFO={"intertext": "Hello"}), Place("t.wad", "MAP06", "intertext = clear"))


def test_a_module_that_still_sets_its_slot_is_an_error():
    with pytest.raises(LevelError, match="MAP and WAD set in"):
        load(room(MAP="MAP01", WAD="X.WAD"))
