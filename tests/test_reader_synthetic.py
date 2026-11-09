"""End-to-end without hardware: draw a board with real ArUco markers, warp it
as a slightly tilted camera would see it, then run reader -> layout -> IR."""
import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from brain.language import layout
from brain.language.vocabulary import default
from brain.reader.aruco import detect
from brain.reader.grid import homography, to_placed

V = default()
PX_PER_MM = 8.0                      # roughly what a 2304 px frame over a 270 mm board gives
BOARD_MM = 280
CORNERS_MM = {90: (10, 10), 91: (BOARD_MM - 10, 10), 92: (10, BOARD_MM - 10), 93: (BOARD_MM - 10, BOARD_MM - 10)}
START_MM = (24.0, 24.0)


def draw_marker(img, marker_id, centre_mm, side_mm):
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    px = int(side_mm * PX_PER_MM)
    m = cv2.aruco.generateImageMarker(d, marker_id, px)
    cx, cy = (int(c * PX_PER_MM) for c in centre_mm)
    x0, y0 = cx - px // 2, cy - px // 2
    q = int(1.2 * PX_PER_MM)
    img[y0 - q:y0 + px + q, x0 - q:x0 + px + q] = 255          # quiet zone
    img[y0:y0 + px, x0:x0 + px] = m


def board(pieces, tilt=True):
    """pieces: (name, col16, row32) relative to START. Returns a BGR image."""
    size = int(BOARD_MM * PX_PER_MM)
    img = np.full((size, size), 140, np.uint8)                   # grey baseplate
    for cid, c in CORNERS_MM.items():
        draw_marker(img, cid, c, 10)
    for name, col, row in pieces:
        p = V.by_name[name]
        ox, oy = START_MM[0] + col * 16, START_MM[1] + row * 32
        # colour the block body so the markers sit on something non-white
        w = 16 if p.kind in ("tile", "spine") else 32
        h = 32 * (p.rows if p.kind == "spine" else 1)
        cv2.rectangle(img, (int(ox * PX_PER_MM), int(oy * PX_PER_MM)), (int((ox + w) * PX_PER_MM), int((oy + h) * PX_PER_MM)), 90, -1)
        mx, my = V.marker_offset(p)
        draw_marker(img, p.id, (ox + mx, oy + my), V.marker_mm(p))
    if tilt:   # camera a little off-axis and rotated
        src = np.float32([[0, 0], [size, 0], [0, size], [size, size]])
        dst = np.float32([[60, 40], [size - 30, 70], [20, size - 50], [size - 80, size - 20]])
        M = cv2.getPerspectiveTransform(src, dst)
        img = cv2.warpPerspective(img, M, (size, size), borderValue=200)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


EXAMPLE = [("start", 0, 0), ("forward", 0, 1), ("n3", 2, 1), ("repeat", 0, 2), ("n4", 2, 2), ("spine3", 0, 3),
           ("forward", 1, 3), ("n2", 3, 3), ("turn_right", 1, 4), ("n1", 3, 4), ("beep", 1, 5), ("light", 0, 6), ("red", 2, 6)]


def read(pieces, tilt=True):
    img = board(pieces, tilt)
    dets = detect(img)
    H = homography(dets, CORNERS_MM)
    return layout.parse(to_placed(dets, H))


def test_all_markers_are_found_and_mapped_to_mm():
    img = board(EXAMPLE)
    dets = detect(img)
    assert sorted(d.id for d in dets) == sorted([90, 91, 92, 93] + [V.by_name[n].id for n, _, _ in EXAMPLE])
    placed = to_placed(dets, homography(dets, CORNERS_MM))
    start = next(p for p in placed if p.id == 0)
    mx, my = V.marker_offset(V.by_name["start"])
    assert abs(start.x - (START_MM[0] + mx)) < 1.0 and abs(start.y - (START_MM[1] + my)) < 1.0
    assert all(abs(p.rotation) < 5 for p in placed)


def test_example_program_end_to_end():
    lay = read(EXAMPLE)
    ops = [(st["op"], st.get("n")) for st in lay.program]
    assert ops == [("forward", 3), ("repeat", 4), ("light", None)]
    assert [st["op"] for st in lay.program[1]["body"]] == ["forward", "turn", "beep"]
    assert lay.program[2]["colour"] == "red"
    assert lay.warnings == []


def test_errors_survive_the_camera_too():
    with pytest.raises(layout.LayoutError) as e:
        read([("start", 0, 0), ("forward", 0, 1), ("beep", 0, 3)])
    assert e.value.code == "gap"
