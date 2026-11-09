"""Turn pieces placed on the baseplate into a Program.

Coordinates are baseplate millimetres with the origin wherever the reader
puts it; everything is made relative to the START block. Rows are 32 mm,
nesting levels are 16 mm, and the baseplate snaps everything to 8 mm studs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .vocabulary import Piece, Vocabulary, default

BLOCK = 32
INDENT = 16
STUD = 8
SNAP_TOL_MM = 3.0        # how far off the stud grid a marker may read before we complain
ROTATION_TOL_DEG = 25.0


@dataclass
class Placed:
    """One detected marker: its id and the position of its centre in mm."""
    id: int
    x: float
    y: float
    rotation: float = 0.0


class LayoutError(Exception):
    """A problem the child can fix. `message` is what the brain says aloud."""

    def __init__(self, code: str, message: str, block: int | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.block = block


@dataclass
class _Node:
    piece: Piece
    level: int
    row: int
    x: float
    y: float
    tiles: list["_Node"] = field(default_factory=list)
    src: int = 0
    target: dict | None = None      # for an ELSE node: the IF statement it belongs to


@dataclass
class Layout:
    program: list[dict[str, Any]]
    warnings: list[str]
    blocks: int


def _describe(piece: Piece) -> str:
    return piece.label.upper() if piece.kind in ("head", "start") else piece.label


def parse(placed: list[Placed], vocab: Vocabulary | None = None) -> Layout:
    vocab = vocab or default()
    nodes: list[_Node] = []
    tiles: list[_Node] = []
    spines: list[_Node] = []
    start: _Node | None = None

    for p in placed:
        piece = vocab.by_id.get(p.id)
        if piece is None or piece.kind == "corner":
            continue
        if abs(((p.rotation + 180) % 360) - 180) > ROTATION_TOL_DEG:
            raise LayoutError("sideways", f"The {_describe(piece)} block is sideways. Turn it so the picture is upright.")
        ox, oy = vocab.marker_offset(piece)
        node = _Node(piece, 0, 0, p.x - ox, p.y - oy)
        if piece.kind == "start":
            if start is not None:
                raise LayoutError("two_starts", "I see two START blocks. A program has just one, in the corner.")
            start = node
        elif piece.kind == "tile":
            tiles.append(node)
        elif piece.kind == "spine":
            spines.append(node)
        else:
            nodes.append(node)

    if start is None:
        raise LayoutError("no_start", "I can't find the START block. Put the green block in the corner.")

    def grid(node: _Node) -> tuple[float, float]:
        """Position relative to START, in studs, after checking it sits on the grid."""
        rx, ry = node.x - start.x, node.y - start.y
        sx, sy = round(rx / STUD), round(ry / STUD)
        if abs(rx - sx * STUD) > SNAP_TOL_MM or abs(ry - sy * STUD) > SNAP_TOL_MM:
            raise LayoutError("off_grid", f"The {_describe(node.piece)} block is not pressed onto the studs. Push it down.")
        return sx, sy

    # --- statements and heads onto (level, row)
    for n in nodes:
        sx, sy = grid(n)
        if sy % 4 != 0 or sy <= 0:
            raise LayoutError("not_in_line", f"The {_describe(n.piece)} block is not in line with the others.")
        if sx % 2 != 0 or sx < 0:
            raise LayoutError("not_in_line", f"The {_describe(n.piece)} block is not lined up. Slide it left or right.")
        n.level, n.row = sx // 2, sy // 4
    nodes.sort(key=lambda n: (n.row, n.level))

    rows_seen = [n.row for n in nodes]
    if len(set(rows_seen)) != len(rows_seen):
        dup = next(r for r in rows_seen if rows_seen.count(r) > 1)
        raise LayoutError("two_in_row", f"Two blocks are side by side on row {dup}. Only one block fits on a row.")
    for i, n in enumerate(nodes):
        if n.row != i + 1:
            prev = f"block {i}" if i else "the START block"
            raise LayoutError("gap", f"There is a gap after {prev}. Snap the next block right under it.")
        n.src = i + 1

    # --- tiles attach to the socket on the right of a block (or to a sensor tile)
    unattached = list(tiles)
    for n in nodes:
        right = start.x + n.level * INDENT + BLOCK
        found = [t for t in unattached if abs(t.x - right) <= SNAP_TOL_MM + 1 and abs(t.y - n.y) <= SNAP_TOL_MM + 1]
        if found:
            t = found[0]
            unattached.remove(t)
            n.tiles.append(t)
            if t.piece.takes:
                second = [u for u in unattached if abs(u.x - (right + INDENT)) <= SNAP_TOL_MM + 1 and abs(u.y - n.y) <= SNAP_TOL_MM + 1]
                if second:
                    unattached.remove(second[0])
                    n.tiles.append(second[0])
    if unattached:
        t = unattached[0]
        what = "number" if t.piece.type == "number" else t.piece.type or "small"
        raise LayoutError("orphan_tile", f"I see a {what} tile with no block next to it. Slide it into a block's slot.")

    # --- nesting from indentation
    warnings: list[str] = []
    program: list[dict[str, Any]] = []
    # stack frames: (level, body list being filled, head node that opened it)
    stack: list[tuple[int, list, _Node | None]] = [(0, program, None)]
    prev: _Node | None = None

    def close_frame():
        lvl, body, head = stack.pop()
        if not body:
            raise LayoutError("empty_body", f"The {_describe(head.piece)} block on row {head.row} has nothing inside it.")

    for n in nodes:
        while n.level < stack[-1][0]:
            close_frame()
        top_level, body, _ = stack[-1]
        if n.level == top_level + 1:
            if prev is None or prev.piece.kind != "head" or prev.level != top_level:
                raise LayoutError("too_far_right", f"Block {n.src} ({_describe(n.piece)}) is pushed too far right. Nothing is above it to belong to.")
            if prev.piece.name == "else":
                target = prev.target["else"]
            else:
                target = body[-1]["body"] if "body" in body[-1] else body[-1]["then"]
            stack.append((n.level, target, prev))
            body = target
        elif n.level > top_level + 1:
            raise LayoutError("too_far_right", f"Block {n.src} ({_describe(n.piece)}) is pushed too far right. Nothing is above it to belong to.")
        elif prev is not None and prev.piece.kind == "head" and prev.level == n.level:
            raise LayoutError("empty_body", f"The {_describe(prev.piece)} block on row {prev.row} has nothing inside it.")

        if n.piece.name == "else":
            # valid only right after an IF whose then-body has just been closed
            if not body or body[-1].get("op") != "if" or body[-1]["else"] or prev is None or prev.level <= n.level:
                raise LayoutError("else_without_if", f"The ELSE block on row {n.row} needs an IF block right above it.")
            n.target = body[-1]
            prev = n
            continue
        body.append(_statement(n, vocab))
        prev = n

    if prev is not None and prev.piece.kind == "head":
        raise LayoutError("empty_body", f"The {_describe(prev.piece)} block on row {prev.row} has nothing inside it.")
    while len(stack) > 1:
        close_frame()

    # --- spines are mechanical; check them softly
    for n in nodes:
        if n.piece.kind == "head":
            want_x, want_y = start.x + n.level * INDENT, n.y + BLOCK
            sp = [s for s in spines if abs(s.x - want_x) <= SNAP_TOL_MM + 1 and abs(s.y - want_y) <= SNAP_TOL_MM + 1]
            if not sp:
                warnings.append(f"The {_describe(n.piece)} block on row {n.row} has no spine under it.")
    return Layout(program=program, warnings=warnings, blocks=len(nodes))


def _tile_value(n: _Node, vocab: Vocabulary, socket: str):
    if not n.tiles:
        return None
    t = n.tiles[0]
    if not vocab.accepts(socket, t.piece):
        raise LayoutError("wrong_tile", f"The tile next to block {n.src} ({_describe(n.piece)}) doesn't belong there. It needs a {socket} tile.")
    return t


def _statement(n: _Node, vocab: Vocabulary) -> dict[str, Any]:
    p = n.piece
    st: dict[str, Any] = {"src": n.src}
    name = p.name
    if name in ("forward", "back"):
        t = _tile_value(n, vocab, "number")
        st.update(op=name, n=t.piece.value if t else 1)
    elif name in ("turn_left", "turn_right"):
        t = _tile_value(n, vocab, "number")
        st.update(op="turn", dir=name.split("_")[1], n=t.piece.value if t else 1)
    elif name == "stop":
        st.update(op="stop")
    elif name == "beep":
        t = _tile_value(n, vocab, "note")
        st.update(op="beep", note=t.piece.value if t else "mid")
    elif name == "light":
        t = _tile_value(n, vocab, "colour")
        if t is None:
            raise LayoutError("needs_tile", f"The LIGHT block (block {n.src}) needs a colour tile.")
        st.update(op="light", colour=t.piece.value)
    elif name == "face":
        t = _tile_value(n, vocab, "expression")
        st.update(op="face", expr=t.piece.value if t else "happy")
    elif name == "wait":
        t = _tile_value(n, vocab, "number")
        st.update(op="wait", n=t.piece.value if t else 1)
    elif name in ("arm_up", "arm_down"):
        st.update(op="arm", dir=name.split("_")[1])
    elif name == "repeat":
        t = _tile_value(n, vocab, "count")
        if t is None:
            raise LayoutError("needs_tile", f"The REPEAT block on row {n.row} needs a number tile. How many times?")
        st.update(op="repeat", n=t.piece.value, body=[])
    elif name in ("if", "wait_until"):
        t = _tile_value(n, vocab, "sensor")
        if t is None:
            raise LayoutError("needs_tile", f"The {_describe(p)} block on row {n.row} needs a yellow sensor tile.")
        cond: dict[str, Any] = {"sensor": t.piece.value}
        if t.piece.takes:
            if len(n.tiles) < 2 or n.tiles[1].piece.type != t.piece.takes:
                raise LayoutError("needs_tile", f"The SEES tile on row {n.row} needs a colour tile next to it. Which colour?")
            cond["colour"] = n.tiles[1].piece.value
        if name == "if":
            st.update(op="if", cond=cond, then=[])
            st["else"] = []
        else:
            st.update(op="wait_until", cond=cond)
    elif name == "else":
        st.update(op="else")
    else:
        raise LayoutError("unknown", f"I don't know block {n.src}.")
    return st
