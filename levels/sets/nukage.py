"""NUKAGE.WAD: nine maps for DOOM II. The four that loop round a nukage pool
(Crossing, Tower, Drain, Lockdown) sit on even slots, so no two are adjacent."""
WAD = "NUKAGE.WAD"
MAPS = {
    "MAP01": "nukage_outskirts",
    "MAP02": "nukage_crossing",
    "MAP03": "nukage_divided",
    "MAP04": "nukage_tower",
    "MAP05": "nukage_undercurrent",
    "MAP06": "nukage_drain",
    "MAP07": "nukage_storage",   # its exit opens by MAP07's own boss rule, so only in MAP07
    "MAP08": "nukage_lockdown",
    "MAP09": "nukage_meltdown",
}
UMAPINFO = {
    # No text screen: DOOM II's own after MAP06 is "YOU HAVE ENTERED DEEPLY INTO THE INFESTED STARPORT...".
    "MAP06": "intertext = clear",
    # The ending: the bulletin, then the cast. intertext is one quoted string per line, separated by
    # commas; the screen fits 17 lines of up to about 39 characters.
    "MAP09": """
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
