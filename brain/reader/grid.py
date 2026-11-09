"""Map marker detections from pixels to baseplate millimetres.

Four corner markers fixed to the camera stand (ids 90..93) frame the
baseplate. Their known positions in mm give a homography, so the camera can
sit at any height or slight angle.
"""
from __future__ import annotations

import cv2
import numpy as np

from brain.language.layout import Placed
from .aruco import Detection

CORNER_IDS = (90, 91, 92, 93)     # top-left, top-right, bottom-left, bottom-right


class GridError(Exception):
    pass


def homography(detections: list[Detection], corner_mm: dict[int, tuple[float, float]]) -> np.ndarray:
    """corner_mm: marker centre in mm for each corner id, as built into the stand."""
    src, dst = [], []
    for d in detections:
        if d.id in corner_mm:
            src.append(d.centre)
            dst.append(corner_mm[d.id])
    if len(src) < 4:
        raise GridError(f"only {len(src)} of 4 corner markers visible; is something covering the edge of the board?")
    H, _ = cv2.findHomography(np.array(src, dtype=np.float32), np.array(dst, dtype=np.float32))
    return H


def to_placed(detections: list[Detection], H: np.ndarray) -> list[Placed]:
    out: list[Placed] = []
    for d in detections:
        if d.id in CORNER_IDS:
            continue
        pt = cv2.perspectiveTransform(np.array([[d.centre]], dtype=np.float32), H)[0][0]
        # rotation in board space: transform the marker's top edge too
        top = cv2.perspectiveTransform(d.corners[:2].reshape(1, 2, 2).astype(np.float32), H)[0]
        dx, dy = top[1] - top[0]
        rot = float(np.degrees(np.arctan2(dy, dx)))
        out.append(Placed(d.id, float(pt[0]), float(pt[1]), rot))
    return out


def read_board(image, corner_mm: dict[int, tuple[float, float]], dictionary: str = "DICT_4X4_100") -> list[Placed]:
    from .aruco import detect
    dets = detect(image, dictionary)
    return to_placed(dets, homography(dets, corner_mm))
