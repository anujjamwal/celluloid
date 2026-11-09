"""Build Placed lists the way the camera would report them."""
from brain.language.layout import Placed, BLOCK, INDENT
from brain.language.vocabulary import default

V = default()
ORIGIN = (16.0, 16.0)   # START block origin on the baseplate, mm


def _marker_centre(name: str, ox: float, oy: float) -> Placed:
    piece = V.by_name[name]
    mx, my = V.marker_offset(piece)
    return Placed(piece.id, ox + mx, oy + my)


def block(name: str, row: int, level: int = 0, tiles: tuple[str, ...] = (), jitter=(0.0, 0.0)) -> list[Placed]:
    """A statement/head at (row, level) with tiles plugged into its socket."""
    ox = ORIGIN[0] + level * INDENT + jitter[0]
    oy = ORIGIN[1] + row * BLOCK + jitter[1]
    out = [_marker_centre(name, ox, oy)]
    for i, t in enumerate(tiles):
        out.append(_marker_centre(t, ox + BLOCK + i * INDENT, oy))
    return out


def spine(rows: int, row: int, level: int = 0) -> list[Placed]:
    return [_marker_centre(f"spine{rows}", ORIGIN[0] + level * INDENT, ORIGIN[1] + row * BLOCK)]


def start() -> list[Placed]:
    return [_marker_centre("start", *ORIGIN)]


def corners() -> list[Placed]:
    return [Placed(90, 6, 6), Placed(91, 250, 6), Placed(92, 6, 250), Placed(93, 250, 250)]
