"""Decompiled maps rebuild to the same map (levels.decompile --verify)."""
import importlib.util
import os

import pytest
from conftest import ROOT, needs_iwad

from levels.decompile import decompile, map_entries, open_source, verify
from levels.model import load
from levels.wad import read_wad, replace_map, umapinfo_lump, write_wad


def module_from(path):
    spec = importlib.util.spec_from_file_location("levels.imported.test_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def round_trip(source, slot, tmp_path):
    src = open_source(source)
    res = decompile(src, slot, dict(map_entries(src.lumps))[slot])
    path = tmp_path / f"{res.modname}.py"
    path.write_text(res.text)
    return res, verify(src, res, str(path))


@needs_iwad("doom2")
@pytest.mark.parametrize("slot", ["MAP01", "MAP02", "MAP03", "MAP04", "MAP05"])
def test_our_maps_round_trip(slot, tmp_path):
    res, diffs = round_trip(os.path.join(ROOT, "wads", "NUKAGE.WAD"), slot, tmp_path)
    assert diffs == [] and res.done == []


@needs_iwad("doom")
def test_e1m1_round_trips(tmp_path):
    res, diffs = round_trip("doom", "E1M1", tmp_path)
    assert diffs == [] and res.done == []
    assert "KNOWN_ISSUES" in res.text


@needs_iwad("doom2")
def test_map_with_unclosed_sectors_is_repaired_and_round_trips(tmp_path):
    res, diffs = round_trip("doom2", "MAP22", tmp_path)
    assert diffs == [] and res.done
    assert "# repaired:" in res.text


@needs_iwad("doom2")
def test_umapinfo_entry_survives_decompile_and_rebuild(tmp_path):
    entry = ('MAP MAP01\n{\n  levelname = "Odd One"\n  par = 30\n  nointermission = true\n'
             '  bossaction = Fatso, 23, 666\n  bossaction = Arachnotron, 30, 667\n}')
    maps = read_wad(os.path.join(ROOT, "wads", "NUKAGE.WAD"))[:11]   # MAP01 and its lumps
    wad = tmp_path / "ODD.WAD"
    write_wad(str(wad), maps + [("UMAPINFO", entry.encode() + b"\n")])
    res, diffs = round_trip(str(wad), "MAP01", tmp_path)
    assert diffs == [] and '"""MAP01: Odd One' in res.text
    level = load(module_from(tmp_path / f"{res.modname}.py"))
    assert replace_map([], "MAP01", maps, umapinfo_lump(level))[-1] == ("UMAPINFO", entry.encode() + b"\n")
