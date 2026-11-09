"""Load blocks/vocabulary.json and expose lookups."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

VOCAB_PATH = Path(__file__).resolve().parents[2] / "blocks" / "vocabulary.json"


@dataclass(frozen=True)
class Piece:
    id: int
    name: str
    kind: str                 # start | statement | head | tile | spine | corner
    family: str
    label: str = ""
    icon: str = ""
    socket: str | None = None  # for statements/heads: which tile type the socket accepts
    type: str | None = None    # for tiles: number | infinity | colour | note | expression | sensor
    value: Any = None
    takes: str | None = None   # for sensor tiles that need a second tile (sees_colour -> colour)
    rows: int = 0              # for spines
    extra: dict = field(default_factory=dict)


class Vocabulary:
    def __init__(self, path: Path = VOCAB_PATH):
        raw = json.loads(Path(path).read_text())
        self.dictionary: str = raw["dictionary"]
        self.geometry: dict = raw["geometry"]
        self.socket_accepts: dict[str, list[str]] = raw["socket_accepts"]
        self.by_id: dict[int, Piece] = {}
        self.by_name: dict[str, Piece] = {}
        known = {"id", "name", "kind", "family", "label", "icon", "socket", "type", "value", "takes", "rows"}
        for p in raw["pieces"]:
            piece = Piece(**{k: v for k, v in p.items() if k in known},
                          extra={k: v for k, v in p.items() if k not in known})
            if piece.id in self.by_id:
                raise ValueError(f"duplicate marker id {piece.id}")
            self.by_id[piece.id] = piece
            self.by_name[piece.name] = piece

    def pieces(self, kind: str | None = None) -> list[Piece]:
        return [p for p in self.by_id.values() if kind is None or p.kind == kind]

    def accepts(self, socket: str, tile: Piece) -> bool:
        return tile.kind == "tile" and tile.type in self.socket_accepts.get(socket, [])

    def marker_mm(self, piece: Piece) -> float:
        key = "tile" if piece.kind == "tile" else "block" if piece.kind in ("statement", "head", "start") else piece.kind
        return self.geometry["marker_mm"][key]

    def marker_offset(self, piece: Piece) -> tuple[float, float]:
        key = {"start": "start", "statement": "block", "head": "block", "tile": "tile", "spine": "spine"}[piece.kind]
        return tuple(self.geometry["marker_offset"][key])


_default: Vocabulary | None = None


def default() -> Vocabulary:
    global _default
    if _default is None:
        _default = Vocabulary()
    return _default
