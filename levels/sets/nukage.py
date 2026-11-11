"""NUKAGE.WAD: eight maps for DOOM II. Storage and Meltdown open their exits
by UMAPINFO bossactions, so every map works in any slot. Nukage Divided was
cut for the eight-map episode; it still builds to wads/scratch/."""
WAD = "NUKAGE.WAD"
MAPS = {
    "MAP01": "nukage_outskirts",
    "MAP02": "nukage_crossing",
    "MAP03": "nukage_tower",
    "MAP04": "nukage_undercurrent",
    "MAP05": "nukage_drain",
    "MAP06": "nukage_storage",
    "MAP07": "nukage_lockdown",
    "MAP08": "nukage_meltdown",
}
UMAPINFO = {
    # No text screen: DOOM II's own after MAP06 is "YOU HAVE ENTERED DEEPLY INTO THE INFESTED STARPORT...".
    "MAP06": "intertext = clear",
    # The ending: the bulletin, then the cast. intertext is one quoted string per line, separated by
    # commas; the screen fits 17 lines of up to about 39 characters.
    "MAP08": """
endcast = true
intertext = "Bulletin. The plant has gone critical.",
            "Our modestly armed nuclear inspector",
            "followed the spill down the meltdown",
            "source, falls by falls, to the lake at",
            "the bottom. Witnesses describe a ",
            "creature the size of a house wading in",
            "the waste, and a figure in the dome ",
            "reviving the demons.",
            "",
            "72 hours have passed and the inspector",
            "has not reported back in. Thankfully,",
            "though, the army of demon spawn has ",
            "stopped emerging from the NUKAGE.",
            "",
            "The inspector reached the core.",
            "The machine reports every check",
            "passed, and asks what to build next."
""",
}
