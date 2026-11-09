"""Still capture on the Raspberry Pi. Falls back to a file for development."""
from __future__ import annotations

from pathlib import Path

import numpy as np


class Camera:
    def __init__(self, size: tuple[int, int] = (2304, 1296), fallback_file: str | Path | None = None):
        self.size = size
        self.fallback_file = fallback_file
        self._cam = None
        try:
            from picamera2 import Picamera2  # type: ignore
            self._cam = Picamera2()
            cfg = self._cam.create_still_configuration(main={"size": size, "format": "RGB888"})
            self._cam.configure(cfg)
            self._cam.start()
        except Exception:
            if fallback_file is None:
                raise

    def capture(self) -> np.ndarray:
        """BGR image as OpenCV expects."""
        if self._cam is not None:
            rgb = self._cam.capture_array()
            return rgb[:, :, ::-1].copy()
        import cv2
        img = cv2.imread(str(self.fallback_file))
        if img is None:
            raise FileNotFoundError(self.fallback_file)
        return img
