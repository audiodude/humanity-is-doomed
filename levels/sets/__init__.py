"""Set lists: which maps each WAD holds, in which slots. One module per WAD:

    WAD       file name under wads/, e.g. "NUKAGE.WAD"
    MAPS      {slot: level module}, e.g. {"MAP01": "nukage_outskirts", ...};
              modules are named as `python3 -m levels` takes them
    UMAPINFO  {slot: lines} added to that slot's UMAPINFO entry, whichever
              map is in it: the set's text screens and its ending. A key the
              map's own UMAPINFO also sets is an error.            [optional]

A map's slot comes from here, so reordering a WAD is an edit to its MAPS, and
a map's UMAPINFO without `music` or `next` gets the slot's own (the spec's
default handling). A module in no set builds to wads/scratch/<module>.WAD as
MAP01 (place()).
"""
import importlib
import pkgutil

from ..model import LevelError, Place


def all_sets():
    """Every set module, checked."""
    for info in pkgutil.iter_modules(__path__):
        s = importlib.import_module(f"{__name__}.{info.name}")
        if extra := set(getattr(s, "UMAPINFO", {})) - set(s.MAPS):
            raise LevelError(f"{s.__name__}: UMAPINFO for {', '.join(sorted(extra))}, which MAPS doesn't fill")
        yield s


def place(name, wad=None, slot=None) -> Place:
    """Where level module `name` (e.g. "nukage_drain") builds: `wad` and
    `slot` if either is given (the other defaulting to the scratch WAD or
    MAP01), else its set's WAD and slot, else MAP01 of the scratch WAD
    wads/scratch/<module>.WAD, a scratch build."""
    scratch = f"scratch/{name.rsplit('.', 1)[-1]}.WAD"
    if wad or slot:
        return Place(wad or scratch, (slot or "MAP01").upper())
    found = [(s, k) for s in all_sets() for k, v in s.MAPS.items() if v == name]
    if len(found) > 1:
        raise LevelError(f"{name} is in more than one set: " + ", ".join(f"{s.__name__} {k}" for s, k in found))
    if not found:
        return Place(scratch, "MAP01", scratch=True)
    s, slot = found[0]
    return Place(s.WAD, slot, getattr(s, "UMAPINFO", {}).get(slot, ""))
