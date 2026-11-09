"""Intermediate representation: what the robot will do, independent of hub.

A Program is a list of statements (plain dicts so it serialises to JSON as-is):

  {"op": "forward", "n": 3}
  {"op": "turn", "dir": "right", "n": 1}
  {"op": "beep", "note": "mid"}          {"op": "light", "colour": "red"}
  {"op": "face", "expr": "happy"}        {"op": "wait", "n": 2}
  {"op": "arm", "dir": "up"}             {"op": "stop"}
  {"op": "repeat", "n": 4 | "forever", "body": [...]}
  {"op": "if", "cond": {...}, "then": [...], "else": [...]}
  {"op": "wait_until", "cond": {...}}

A cond is {"sensor": "distance_close" | "bumped" | "dark" | "bright" | "shaken"}
or {"sensor": "sees_colour", "colour": "red"}.

Every statement also carries "src": the 1-based block number in reading order,
so the hub can report progress and the brain can point at a block in speech.
"""
from __future__ import annotations

import json
from typing import Any

Program = list[dict[str, Any]]


def to_json(program: Program) -> str:
    return json.dumps(program, separators=(",", ":"))


def walk(program: Program):
    """Yield every statement depth-first, in execution order of first visit."""
    for st in program:
        yield st
        for key in ("body", "then", "else"):
            if key in st:
                yield from walk(st[key])


def count(program: Program) -> int:
    return sum(1 for _ in walk(program))
