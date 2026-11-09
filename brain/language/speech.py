"""Say a Program out loud: clip keys for pre-recorded audio, and a sentence."""
from __future__ import annotations

from typing import Any

Program = list[dict[str, Any]]

SENSOR_WORDS = {
    "distance_close": "it sees something close",
    "bumped": "it is bumped",
    "dark": "it is dark",
    "bright": "it is bright",
    "shaken": "it is shaken",
}


def _cond(c: dict) -> str:
    if c["sensor"] == "sees_colour":
        return f"it sees {c['colour']}"
    return SENSOR_WORDS[c["sensor"]]


def _times(n) -> str:
    if n == "forever":
        return "forever"
    return "once" if n == 1 else f"{n} times"


def phrases(program: Program, depth: int = 0) -> list[str]:
    """One short phrase per statement, nested phrases indented by depth."""
    out: list[str] = []
    pad = "  " * depth
    for st in program:
        op = st["op"]
        if op in ("forward", "back"):
            out.append(f"{pad}{op} {st['n']}")
        elif op == "turn":
            out.append(f"{pad}turn {st['dir']}" + (f" {st['n']} times" if st["n"] != 1 else ""))
        elif op == "stop":
            out.append(f"{pad}stop")
        elif op == "beep":
            out.append(f"{pad}beep" + ("" if st["note"] == "mid" else f" {st['note']}"))
        elif op == "light":
            out.append(f"{pad}light {st['colour']}")
        elif op == "face":
            out.append(f"{pad}{st['expr']} face")
        elif op == "wait":
            out.append(f"{pad}wait {st['n']}")
        elif op == "arm":
            out.append(f"{pad}arm {st['dir']}")
        elif op == "repeat":
            out.append(f"{pad}repeat {_times(st['n'])}:")
            out += phrases(st["body"], depth + 1)
        elif op == "if":
            out.append(f"{pad}if {_cond(st['cond'])}:")
            out += phrases(st["then"], depth + 1)
            if st.get("else"):
                out.append(f"{pad}otherwise:")
                out += phrases(st["else"], depth + 1)
        elif op == "wait_until":
            out.append(f"{pad}wait until {_cond(st['cond'])}")
    return out


def sentence(program: Program) -> str:
    """Everything the brain says before running, as one string."""
    parts = [p.strip() for p in phrases(program)]
    if not parts:
        return "There is nothing after START. Add a block."
    body = ". ".join(p[0].upper() + p[1:] for p in parts)
    return body + ". Done."


def clip_keys(program: Program) -> list[str]:
    """Keys of the audio clips to play, in order (one file per key)."""
    keys: list[str] = []
    for p in phrases(program):
        for word in p.strip().rstrip(":").replace(",", "").split():
            keys.append(word.lower())
        keys.append("pause")
    keys.append("done")
    return keys
