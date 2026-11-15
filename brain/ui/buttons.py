"""RUN / STOP / STEP buttons.

Backends: gpiozero (Raspberry Pi), libgpiod v2 (any Linux board), console.
Buttons are wired between the pin and ground; the pin is pulled up.
"""
from __future__ import annotations

import time

DEFAULT_PINS = {"run": 17, "stop": 27, "step": 22}      # BCM numbers on a Pi; line offsets on gpiod


class Buttons:
    def __init__(self, pins: dict[str, int] | None = None, gpiochip: str = "/dev/gpiochip0"):
        self.pins = pins or DEFAULT_PINS
        self.backend = "console"
        self._gz = None
        self._req = None
        try:
            from gpiozero import Button  # type: ignore
            self._gz = {name: Button(pin) for name, pin in self.pins.items()}
            self.backend = "gpiozero"
            return
        except Exception:
            self._gz = None
        try:
            import gpiod  # type: ignore
            from gpiod.line import Bias, Direction, Edge  # type: ignore
            settings = gpiod.LineSettings(direction=Direction.INPUT, bias=Bias.PULL_UP, edge_detection=Edge.FALLING,
                                          debounce_period=__import__("datetime").timedelta(milliseconds=20))
            self._req = gpiod.request_lines(gpiochip, consumer="blocks", config={tuple(self.pins.values()): settings})
            self._by_offset = {v: k for k, v in self.pins.items()}
            self.backend = "gpiod"
        except Exception:
            self._req = None

    def wait(self) -> str:
        """Block until a button is pressed; returns 'run', 'stop', 'step' or 'quit'."""
        if self._gz is not None:
            while True:
                for name, b in self._gz.items():
                    if b.is_pressed:
                        time.sleep(0.25)          # crude debounce / release wait
                        return name
                time.sleep(0.02)
        if self._req is not None:
            while True:
                if self._req.wait_edge_events(1.0):
                    ev = self._req.read_edge_events()[-1]
                    return self._by_offset[ev.line_offset]
        line = input("[buttons] r=RUN s=STOP t=STEP q=quit > ").strip().lower()
        return {"r": "run", "s": "stop", "t": "step", "q": "quit"}.get(line[:1], "none")
