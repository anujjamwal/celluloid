"""Voice: one pre-recorded clip per key from clips/<key>.wav, played with
aplay (ALSA, any board). Falls back to printing. A Piper TTS backend can be
added here later without touching the rest of the brain."""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path


class Speaker:
    def __init__(self, clips: Path | None = None):
        self.clips = clips
        self.aplay = shutil.which("aplay")

    def say_keys(self, keys: list[str]) -> None:
        for k in keys:
            f = (self.clips / f"{k}.wav") if self.clips else None
            if f and f.exists() and self.aplay:
                subprocess.run([self.aplay, "-q", str(f)], check=False)
            elif k == "pause":
                time.sleep(0.15)
            else:
                print(f"[say] {k}")

    def say(self, sentence: str) -> None:
        print(f"[say] {sentence}")
