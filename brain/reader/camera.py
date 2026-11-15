"""Still capture: Raspberry Pi CSI camera (picamera2), any USB webcam
(OpenCV / UVC), or a saved image for development.

Order of preference when nothing is forced: picamera2 if it imports and finds
a camera, else the first UVC device, else the fallback file.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np


class Camera:
    def __init__(self, size: tuple[int, int] = (2304, 1296), fallback_file: str | Path | None = None,
                 uvc_index: int | None = None):
        self.size = size
        self.fallback_file = fallback_file
        self._pi = None
        self._uvc = None
        if fallback_file is not None and uvc_index is None:
            return                                   # development: read the file, touch no hardware
        if uvc_index is not None:
            self._try_uvc(uvc_index, size)
        elif not self._try_picamera(size):
            self._try_uvc(0, size)
        if self._pi is None and self._uvc is None:
            raise RuntimeError("no camera found: no picamera2 device, no UVC webcam, and no --image file")

    def _try_picamera(self, size) -> bool:
        try:
            from picamera2 import Picamera2  # type: ignore
            self._pi = Picamera2()
            cfg = self._pi.create_still_configuration(main={"size": size, "format": "RGB888"})
            self._pi.configure(cfg)
            self._pi.start()
            return True
        except Exception:
            self._pi = None
            return False

    def _try_uvc(self, index: int, size) -> bool:
        import cv2
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            return False
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self._uvc = cap
        return True

    def capture(self) -> np.ndarray:
        """BGR image as OpenCV expects."""
        if self._pi is not None:
            rgb = self._pi.capture_array()
            return rgb[:, :, ::-1].copy()
        if self._uvc is not None:
            for _ in range(5):          # let auto-exposure settle, keep the last frame
                ok, frame = self._uvc.read()
            if not ok:
                raise RuntimeError("webcam returned no frame")
            return frame
        import cv2
        img = cv2.imread(str(self.fallback_file))
        if img is None:
            raise FileNotFoundError(self.fallback_file)
        return img
