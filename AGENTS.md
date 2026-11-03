# Agent notes

- **Build WADs in place.** While iterating on a map, build with `python3 -m levels <module>`, which writes its set's WAD in `wads/` (only that map's slot; `levels/sets/` says which WAD and slot) and its preview. The user plays the WAD in `wads/` between iterations, so every build lands there and stays playable. A map not yet in a set goes to `wads/scratch/<module>.WAD`; add it to its set once it has a slot.
