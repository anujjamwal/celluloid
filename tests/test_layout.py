import pytest

from brain.language import layout, speech
from brain.language.layout import LayoutError
from brain.drivers.simulator import Simulator
from .helpers import block, spine, start, corners


def strip_src(program):
    out = []
    for st in program:
        st = {k: v for k, v in st.items() if k != "src"}
        for key in ("body", "then", "else"):
            if key in st:
                st[key] = strip_src(st[key])
        out.append(st)
    return out


def test_example_program_from_the_docs():
    placed = (corners() + start()
              + block("forward", 1, tiles=("n3",))
              + block("repeat", 2, tiles=("n4",)) + spine(3, 3)
              + block("forward", 3, 1, tiles=("n2",))
              + block("turn_right", 4, 1, tiles=("n1",))
              + block("beep", 5, 1)
              + block("light", 6, tiles=("red",)))
    lay = layout.parse(placed)
    assert strip_src(lay.program) == [
        {"op": "forward", "n": 3},
        {"op": "repeat", "n": 4, "body": [
            {"op": "forward", "n": 2},
            {"op": "turn", "dir": "right", "n": 1},
            {"op": "beep", "note": "mid"},
        ]},
        {"op": "light", "colour": "red"},
    ]
    assert lay.warnings == []
    assert lay.blocks == 6
    assert [st["src"] for st in lay.program] == [1, 2, 6]
    assert speech.sentence(lay.program) == (
        "Forward 3. Repeat 4 times:. Forward 2. Turn right. Beep. Light red. Done.")
    sim = Simulator()
    sim.run(lay.program)
    # forward 3, then a square of side 2: back where the square started, facing north
    assert (sim.x, sim.y, sim.heading) == (0, 3, "north")


def test_tolerates_camera_jitter():
    placed = start() + block("forward", 1, tiles=("n2",), jitter=(1.5, -1.2)) + block("beep", 2, jitter=(-2.0, 2.0))
    lay = layout.parse(placed)
    assert [st["op"] for st in lay.program] == ["forward", "beep"]


def test_defaults_when_socket_is_empty():
    lay = layout.parse(start() + block("forward", 1) + block("turn_left", 2) + block("wait", 3) + block("beep", 4) + block("face", 5))
    assert strip_src(lay.program) == [
        {"op": "forward", "n": 1}, {"op": "turn", "dir": "left", "n": 1}, {"op": "wait", "n": 1},
        {"op": "beep", "note": "mid"}, {"op": "face", "expr": "happy"}]


def test_if_else_and_sees_colour():
    placed = (start()
              + block("if", 1, tiles=("sees_colour", "red")) + spine(1, 2)
              + block("beep", 2, 1)
              + block("else", 3) + spine(1, 4)
              + block("light", 4, 1, tiles=("blue",))
              + block("stop", 5))
    lay = layout.parse(placed)
    assert strip_src(lay.program) == [
        {"op": "if", "cond": {"sensor": "sees_colour", "colour": "red"},
         "then": [{"op": "beep", "note": "mid"}], "else": [{"op": "light", "colour": "blue"}]},
        {"op": "stop"}]
    assert speech.phrases(lay.program)[:4] == ["if it sees red:", "  beep", "otherwise:", "  light blue"]
    sim = Simulator(sensors={"colour": "red"}); sim.run(lay.program)
    assert sim.log[0] == "beep mid"
    sim = Simulator(sensors={"colour": "green"}); sim.run(lay.program)
    assert sim.log[0] == "light blue"


def test_nested_repeat_and_forever():
    placed = (start()
              + block("repeat", 1, tiles=("forever",)) + spine(3, 2)
              + block("repeat", 2, 1, tiles=("n2",)) + spine(1, 3, 1)
              + block("forward", 3, 2)
              + block("turn_right", 4, 1))
    lay = layout.parse(placed)
    p = strip_src(lay.program)
    assert p[0]["n"] == "forever" and p[0]["body"][0]["n"] == 2 and p[0]["body"][0]["body"][0]["op"] == "forward"
    assert p[0]["body"][1]["op"] == "turn"
    sim = Simulator(max_steps=50); sim.run(lay.program)
    assert sim.log[-1] == "stopped: too many steps"


@pytest.mark.parametrize("placed, code, says", [
    (block("forward", 1), "no_start", "can't find the START"),
    (start() + start(), "two_starts", "two START"),
    (start() + block("forward", 2), "gap", "gap after the START"),
    (start() + block("forward", 1) + block("beep", 3), "gap", "gap after block 1"),
    (start() + block("forward", 1, 1), "too_far_right", "too far right"),
    (start() + block("repeat", 1, tiles=("n2",)) + block("beep", 2), "empty_body", "nothing inside"),
    (start() + block("repeat", 1), "needs_tile", "REPEAT block on row 1 needs a number"),
    (start() + block("light", 1), "needs_tile", "needs a colour"),
    (start() + block("if", 1) , "needs_tile", "sensor tile"),
    (start() + block("forward", 1, tiles=("red",)), "wrong_tile", "doesn't belong"),
    (start() + block("forward", 1) + [layout.Placed(18, 150, 150)], "orphan_tile", "number tile with no block"),
    (start() + block("else", 1), "else_without_if", "needs an IF"),
    (start() + [layout.Placed(1, 41, 55 + 4.5)], "off_grid", "not pressed onto the studs"),
    (start() + [layout.Placed(1, 41, 55, rotation=90)], "sideways", "sideways"),
    (start() + block("forward", 1) + block("beep", 1, 1), "two_in_row", "side by side"),
])
def test_child_friendly_errors(placed, code, says):
    with pytest.raises(LayoutError) as e:
        layout.parse(placed)
    assert e.value.code == code
    assert says in e.value.message


def test_missing_spine_is_only_a_warning():
    lay = layout.parse(start() + block("repeat", 1, tiles=("n2",)) + block("beep", 2, 1))
    assert lay.warnings == ["The REPEAT block on row 1 has no spine under it."]


def test_clip_keys_are_single_words():
    lay = layout.parse(start() + block("forward", 1, tiles=("n3",)) + block("turn_right", 2))
    assert speech.clip_keys(lay.program) == ["forward", "3", "pause", "turn", "right", "pause", "done"]
