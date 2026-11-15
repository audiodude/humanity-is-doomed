"""The explorer-vs-human rubric's scoring (scripts/tools/compare.py score,
docs/explore-rubric.md): a stall or L press is predicted only by bot stalls
in the same phase and the same place."""
import os
import sys

from conftest import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts", "tools"))
import compare  # noqa: E402

S = compare.SQUARE
KEY = ("key", "blue")


def run(parts, milestones, end=None):
    """A trace from (tics, square) parts, in order."""
    squares = [sq for n, sq in parts for _ in range(n)]
    return dict(milestones=milestones, squares=squares, lost=[], end=end or len(squares), exited=False, doors={})


def human():
    # Blue key at tic 100, then a minute lost in square (5,5) with one L press there.
    h = run([(100, (0, 0)), (60 * 35, (5, 5))], [(100, KEY)])
    h["lost"] = [(100 + 20 * 35, 5 * S + 10, 5 * S + 10)]
    return h


def test_same_phase_and_place_predicts():
    near = run([(50, (0, 0)), (60 * 35, (5, 6))], [(50, KEY)])       # stalls next door, after the key
    far = run([(50, (0, 0)), (60 * 35, (20, 20))], [(50, KEY)])
    sc = compare.score(human(), {1: near, 2: near, 3: far})
    assert sc["S3"] == [1, 1] and sc["S4"] == [1, 1] and sc["S5"] == [1, 1]
    assert sc["verdict"] == "Predicts"
    assert sc["lures"] == [(5, 5)]   # next door isn't inside: the square it never entered is still listed


def test_other_phase_does_not_predict():
    before = run([(60 * 35, (5, 6)), (50, (0, 0))], [(60 * 35, KEY)])   # same place, but before the key
    sc = compare.score(human(), {1: before, 2: before, 3: before})
    assert sc["S3"] == [0, 1] and sc["S4"] == [0, 1]
    assert sc["S5"] == [0, 1]   # its recurring stall is a false alarm
    assert sc["verdict"] == "Misses"


def test_sharing_only_the_start_does_not_predict():
    # A long human stall that wanders the map from where the key was, against bot
    # stalls that stay by the key: both start in the same square, nothing more.
    wander = [(5 * 35, (0, 0))] + [(5 * 35, (4 * k, 4 * (k % 3))) for k in range(1, 12)]
    h = run([(100, (0, 0))] + wander, [(100, KEY)])
    b = run([(50, (0, 0)), (40 * 35, (0, 0))], [(50, KEY)])
    sc = compare.score(h, {1: b, 2: b, 3: b})
    assert sc["S4"] == [0, 1] and sc["S5"] == [0, 1]


def test_l_press_marks_its_whole_stretch():
    # A minute wandering by (5,5), then off to (12,12), where L is pressed late:
    # the bots stalled by (5,5) and never went near (12,12).
    h = run([(100, (0, 0)), (60 * 35, (5, 5)), (15 * 35, (12, 12))], [(100, KEY)])
    h["lost"] = [(100 + 70 * 35, 12 * S + 10, 12 * S + 10)]
    b = run([(50, (0, 0)), (60 * 35, (5, 6))], [(50, KEY)])
    sc = compare.score(h, {1: b, 2: b, 3: b})
    assert sc["S3"] == [1, 1]
