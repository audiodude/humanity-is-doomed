"""SPEEDY.WAD: the four timed SPEEDY rounds, three maps each. Rounds 1 and 2
(MAP01-MAP06) were built from feature checklists, rounds 3 and 4
(MAP07-MAP12) each around a layout idea."""
WAD = "SPEEDY.WAD"
MAPS = {
    "MAP01": "speedy_dead_air",
    "MAP02": "speedy_cinder_works",
    "MAP03": "speedy_ash_cathedral",
    "MAP04": "speedy2_rust_gate",
    "MAP05": "speedy2_hanging_gallery",
    "MAP06": "speedy2_hellforge",
    "MAP07": "speedy3_long_way_down",
    "MAP08": "speedy3_spire",
    "MAP09": "speedy3_ash_canyon",
    "MAP10": "speedy4_long_way_down",
    "MAP11": "speedy4_shaft",
    "MAP12": "speedy4_gorge",
}
UMAPINFO = {
    # No DOOM II text screens between rounds ("YOU HAVE ENTERED DEEPLY INTO THE INFESTED STARPORT..." and the next).
    "MAP06": "intertext = clear",
    "MAP11": "intertext = clear",
    # Cinder Gorge was built as a MAP06, under SKY1; MAP12 would give it SKY2.
    "MAP12": "skytexture = SKY1",
}
