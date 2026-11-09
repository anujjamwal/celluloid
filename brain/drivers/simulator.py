"""Run a Program on an imaginary robot on a square grid. Used for tests and
for developing the language without a hub on the table."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

Program = list[dict[str, Any]]
HEADINGS = ["north", "east", "south", "west"]
DX = {"north": 0, "east": 1, "south": 0, "west": -1}
DY = {"north": 1, "east": 0, "south": -1, "west": 0}


@dataclass
class Simulator:
    sensors: dict[str, Any] = field(default_factory=dict)   # e.g. {"distance_close": True, "colour": "red"}
    max_steps: int = 1000
    on_block: Callable[[int], None] | None = None
    x: int = 0
    y: int = 0
    heading: str = "north"
    log: list[str] = field(default_factory=list)
    steps: int = 0

    def cond(self, c: dict) -> bool:
        if c["sensor"] == "sees_colour":
            return self.sensors.get("colour") == c["colour"]
        return bool(self.sensors.get(c["sensor"], False))

    def run(self, program: Program) -> None:
        for st in program:
            self.steps += 1
            if self.steps > self.max_steps:
                self.log.append("stopped: too many steps")
                return
            if self.on_block:
                self.on_block(st.get("src", 0))
            op = st["op"]
            if op in ("forward", "back"):
                sign = 1 if op == "forward" else -1
                self.x += sign * DX[self.heading] * st["n"]
                self.y += sign * DY[self.heading] * st["n"]
                self.log.append(f"{op} {st['n']} -> ({self.x},{self.y})")
            elif op == "turn":
                i = HEADINGS.index(self.heading)
                i = (i + (1 if st["dir"] == "right" else -1) * st["n"]) % 4
                self.heading = HEADINGS[i]
                self.log.append(f"turn {st['dir']} {st['n']} -> {self.heading}")
            elif op == "stop":
                self.log.append("stop")
            elif op in ("beep", "light", "face", "wait", "arm"):
                self.log.append(" ".join(str(v) for k, v in st.items() if k != "src"))
            elif op == "repeat":
                n = 10_000 if st["n"] == "forever" else st["n"]
                for _ in range(n):
                    self.run(st["body"])
                    if self.steps > self.max_steps:
                        return
            elif op == "if":
                self.run(st["then"] if self.cond(st["cond"]) else st.get("else", []))
            elif op == "wait_until":
                self.log.append(f"wait until {st['cond']}")
