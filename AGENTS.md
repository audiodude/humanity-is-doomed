# Agent notes

- **Build WADs in place.** While iterating on a map, build with `python3 -m levels <module>`, which writes `wads/<WAD>` (only that map's slot) and its preview. The user plays the WAD in `wads/` between iterations, so every build lands there and stays playable.
