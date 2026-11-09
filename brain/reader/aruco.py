"""Find ArUco markers in an image."""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

DICTS = {"DICT_4X4_50": cv2.aruco.DICT_4X4_50, "DICT_4X4_100": cv2.aruco.DICT_4X4_100}


@dataclass
class Detection:
    id: int
    corners: np.ndarray      # 4x2 pixel corners, clockwise from top-left of the marker
    centre: tuple[float, float]
    rotation: float          # degrees, 0 = marker upright in the image


def marker_cells(marker_id: int, dictionary: str = "DICT_4X4_100") -> list[list[int]]:
    """6x6 grid (border included) of 0 = black, 1 = white for a marker id."""
    d = cv2.aruco.getPredefinedDictionary(DICTS[dictionary])
    img = cv2.aruco.generateImageMarker(d, marker_id, 6)
    return [[1 if img[r, c] > 127 else 0 for c in range(6)] for r in range(6)]


def detect(image: np.ndarray, dictionary: str = "DICT_4X4_100") -> list[Detection]:
    gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    params = cv2.aruco.DetectorParameters()
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    detector = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(DICTS[dictionary]), params)
    corners, ids, _ = detector.detectMarkers(gray)
    out: list[Detection] = []
    if ids is None:
        return out
    for c, i in zip(corners, ids.flatten()):
        pts = c.reshape(4, 2)
        cx, cy = pts.mean(axis=0)
        dx, dy = pts[1] - pts[0]                      # top edge, left to right
        rot = float(np.degrees(np.arctan2(dy, dx)))
        out.append(Detection(int(i), pts, (float(cx), float(cy)), rot))
    return out
