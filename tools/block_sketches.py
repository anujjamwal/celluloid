#!/usr/bin/env python3
"""Generate concept sketches of the blocks as SVG files in docs/images/.

Dimensions are in millimetres and scaled to pixels with S. These are design
sketches, not the CAD; the CAD will be derived from the numbers in
docs/04-architecture.md once the vocabulary is frozen.
"""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "docs" / "images"

from brain.language.vocabulary import default as vocabulary  # noqa: E402

V = vocabulary()
try:
    from brain.reader.aruco import marker_cells as _real_cells
except Exception:  # OpenCV missing: fall back to a random pattern so sketches still render
    _real_cells = None


def marker_cells(marker_id: int):
    if _real_cells is not None:
        return _real_cells(marker_id, V.dictionary)
    rnd = random.Random(marker_id)
    return [[0 if r in (0, 5) or c in (0, 5) else int(rnd.random() < 0.5) for c in range(6)] for r in range(6)]


def pid(name: str) -> int:
    return V.by_name[name].id

# Block geometry (mm)
W = 32            # statement block width / height
TILE_W = 16       # parameter tile and spine width
NOTCH_X0, NOTCH_X1, NOTCH_D = 3, 13, 3      # top notch / bottom tab
SOCK_Y0, SOCK_Y1, SOCK_D, SOCK_FLARE = 16, 28, 4, 1   # right-edge dovetail socket
MARK = 10         # marker side on statement blocks
MARK_SMALL = 8    # marker side on tiles

COL = {
    "start": "#4caf50", "motion": "#4c97ff", "action": "#9966ff",
    "control": "#ffab19", "sensor": "#ffd54f", "param": "#f7f7f7",
    "spine": "#ffc85c", "stroke": "#2b2b2b", "ink": "#ffffff", "bg": "#ffffff",
}


def pts(seq):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in seq)


def statement_outline(x, y, socket=True):
    p = [(x, y), (x + NOTCH_X0, y), (x + NOTCH_X0, y + NOTCH_D), (x + NOTCH_X1, y + NOTCH_D),
         (x + NOTCH_X1, y), (x + W, y)]
    if socket:
        p += [(x + W, y + SOCK_Y0), (x + W - SOCK_D, y + SOCK_Y0 - SOCK_FLARE),
              (x + W - SOCK_D, y + SOCK_Y1 + SOCK_FLARE), (x + W, y + SOCK_Y1)]
    p += [(x + W, y + W), (x + NOTCH_X1, y + W), (x + NOTCH_X1, y + W + NOTCH_D),
          (x + NOTCH_X0, y + W + NOTCH_D), (x + NOTCH_X0, y + W), (x, y + W)]
    return p


def start_outline(x, y, S):
    r = 8
    m = lambda v: f"{v*S:.2f}"
    return (f"M{m(x)},{m(y+W)} L{m(x)},{m(y+r)} A{m(r)},{m(r)} 0 0 1 {m(x+r)},{m(y)} L{m(x+W-r)},{m(y)} "
            f"A{m(r)},{m(r)} 0 0 1 {m(x+W)},{m(y+r)} L{m(x+W)},{m(y+W)} L{m(x+NOTCH_X1)},{m(y+W)} "
            f"L{m(x+NOTCH_X1)},{m(y+W+NOTCH_D)} L{m(x+NOTCH_X0)},{m(y+W+NOTCH_D)} L{m(x+NOTCH_X0)},{m(y+W)} Z")


def tile_outline(x, y):
    """Parameter tile: 16 x 32 with a male dovetail on its left edge."""
    return [(x, y), (x + TILE_W, y), (x + TILE_W, y + W), (x, y + W), (x, y + SOCK_Y1),
            (x - SOCK_D, y + SOCK_Y1 + SOCK_FLARE), (x - SOCK_D, y + SOCK_Y0 - SOCK_FLARE), (x, y + SOCK_Y0)]


def spine_outline(x, y, rows):
    h = rows * W
    return [(x, y), (x + NOTCH_X0, y), (x + NOTCH_X0, y + NOTCH_D), (x + NOTCH_X1, y + NOTCH_D),
            (x + NOTCH_X1, y), (x + TILE_W, y), (x + TILE_W, y + h), (x + NOTCH_X1, y + h),
            (x + NOTCH_X1, y + h + NOTCH_D), (x + NOTCH_X0, y + h + NOTCH_D), (x + NOTCH_X0, y + h), (x, y + h)]


def marker(x, y, side, marker_id, S, quiet=1.0):
    """The real ArUco marker for marker_id: black cells on a white field, side mm,
    at (x, y) mm, with a white quiet zone of `quiet` mm around it."""
    cells = marker_cells(marker_id)
    c = side / 6
    out = [f'<rect x="{(x-quiet)*S:.2f}" y="{(y-quiet)*S:.2f}" width="{(side+2*quiet)*S:.2f}" '
           f'height="{(side+2*quiet)*S:.2f}" fill="#fff"/>']
    for r in range(6):
        for col in range(6):
            if cells[r][col] == 0:
                out.append(f'<rect x="{(x+c*col)*S:.2f}" y="{(y+c*r)*S:.2f}" '
                           f'width="{c*S+0.3:.2f}" height="{c*S+0.3:.2f}" fill="#000"/>')
    return "\n".join(out)


def icon(kind, cx, cy, S, size=14, color="#fff"):
    """Simple icons centred at (cx, cy) mm."""
    s = size * S / 2
    X, Y = cx * S, cy * S
    st = f'stroke="{color}" stroke-width="{0.9*S:.1f}" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "flag":
        return (f'<path d="M{X-s*0.6},{Y+s} V{Y-s} H{X+s*0.7} L{X+s*0.3},{Y-s*0.45} L{X+s*0.7},{Y+s*0.1} H{X-s*0.6}" '
                f'fill="{color}" stroke="none"/>')
    if kind in ("up", "down"):
        d = -1 if kind == "up" else 1
        return (f'<path d="M{X},{Y-d*s} V{Y+d*s} M{X-s*0.7},{Y+d*s*0.2} L{X},{Y+d*s} L{X+s*0.7},{Y+d*s*0.2}" {st}/>')
    if kind in ("left", "right"):
        d = 1 if kind == "right" else -1
        return (f'<path d="M{X-d*s*0.8},{Y+s*0.6} A{s*0.9},{s*0.9} 0 0 {1 if d>0 else 0} {X+d*s*0.75},{Y-s*0.2} '
                f'M{X+d*s*0.75},{Y-s*0.9} V{Y-s*0.2} H{X+d*s*0.05}" {st}/>')
    if kind == "note":
        return (f'<path d="M{X-s*0.2},{Y+s*0.5} V{Y-s*0.9} L{X+s*0.8},{Y-s*1.0} V{Y+s*0.3}" {st}/>'
                f'<circle cx="{X-s*0.55}" cy="{Y+s*0.55}" r="{s*0.4}" fill="{color}"/>'
                f'<circle cx="{X+s*0.45}" cy="{Y+s*0.35}" r="{s*0.4}" fill="{color}"/>')
    if kind == "bulb":
        return (f'<circle cx="{X}" cy="{Y-s*0.25}" r="{s*0.6}" {st}/>'
                f'<path d="M{X-s*0.3},{Y+s*0.5} H{X+s*0.3} M{X-s*0.25},{Y+s*0.85} H{X+s*0.25}" {st}/>')
    if kind == "hourglass":
        return (f'<path d="M{X-s*0.6},{Y-s} H{X+s*0.6} L{X-s*0.6},{Y+s} H{X+s*0.6} Z" {st}/>')
    if kind == "loop":
        return (f'<path d="M{X+s*0.8},{Y-s*0.2} A{s*0.85},{s*0.85} 0 1 0 {X+s*0.55},{Y+s*0.55} '
                f'M{X+s*0.8},{Y-s*0.9} V{Y-s*0.2} H{X+s*0.1}" {st}/>')
    if kind == "fork":
        return (f'<path d="M{X},{Y+s} V{Y} M{X},{Y} L{X-s*0.7},{Y-s*0.8} M{X},{Y} L{X+s*0.7},{Y-s*0.8}" {st}/>'
                f'<circle cx="{X-s*0.7}" cy="{Y-s*0.8}" r="{s*0.2}" fill="{color}"/>'
                f'<circle cx="{X+s*0.7}" cy="{Y-s*0.8}" r="{s*0.2}" fill="{color}"/>')
    if kind == "eye":
        return (f'<path d="M{X-s},{Y} Q{X},{Y-s*1.1} {X+s},{Y} Q{X},{Y+s*1.1} {X-s},{Y} Z" {st}/>'
                f'<circle cx="{X}" cy="{Y}" r="{s*0.35}" fill="{color}"/>')
    if kind == "stop":
        return f'<rect x="{X-s*0.75}" y="{Y-s*0.75}" width="{s*1.5}" height="{s*1.5}" rx="{s*0.15}" fill="{color}"/>'
    if kind == "arm":
        return (f'<path d="M{X-s*0.8},{Y+s} V{Y-s*0.2} L{X+s*0.4},{Y-s*0.9} M{X+s*0.4},{Y-s*0.9} L{X+s*0.9},{Y-s*0.4}" {st}/>')
    if kind == "face":
        return (f'<circle cx="{X}" cy="{Y}" r="{s*0.95}" {st}/>'
                f'<circle cx="{X-s*0.35}" cy="{Y-s*0.25}" r="{s*0.12}" fill="{color}"/>'
                f'<circle cx="{X+s*0.35}" cy="{Y-s*0.25}" r="{s*0.12}" fill="{color}"/>'
                f'<path d="M{X-s*0.45},{Y+s*0.3} Q{X},{Y+s*0.75} {X+s*0.45},{Y+s*0.3}" {st}/>')
    if kind == "waves":
        return (f'<path d="M{X-s},{Y-s*0.5} q{s*0.5},{-s*0.5} {s},0 t{s},0 M{X-s},{Y+s*0.3} q{s*0.5},{-s*0.5} {s},0 t{s},0" {st}/>')
    if kind == "bump":
        return (f'<path d="M{X-s},{Y+s*0.6} H{X+s} M{X-s*0.4},{Y+s*0.6} V{Y-s*0.4} H{X+s*0.4} V{Y+s*0.6}" {st}/>'
                f'<path d="M{X},{Y-s} V{Y-s*0.6}" {st}/>')
    if kind == "arm_down":
        return (f'<path d="M{X-s*0.8},{Y-s} V{Y+s*0.2} L{X+s*0.4},{Y+s*0.9} M{X+s*0.4},{Y+s*0.9} L{X+s*0.9},{Y+s*0.4}" {st}/>')
    if kind == "else":
        return (f'<path d="M{X},{Y-s} V{Y} M{X},{Y} L{X-s*0.7},{Y+s*0.8} M{X},{Y} L{X+s*0.7},{Y+s*0.8}" {st}/>'
                f'<circle cx="{X-s*0.7}" cy="{Y+s*0.8}" r="{s*0.2}" fill="{color}"/>'
                f'<circle cx="{X+s*0.7}" cy="{Y+s*0.8}" r="{s*0.2}" fill="{color}"/>')
    if kind == "moon":
        return f'<path d="M{X+s*0.3},{Y-s*0.9} A{s*0.9},{s*0.9} 0 1 0 {X+s*0.9},{Y+s*0.5} A{s*0.7},{s*0.7} 0 1 1 {X+s*0.3},{Y-s*0.9} Z" fill="{color}"/>'
    if kind == "sun":
        rays = "".join(f'<line x1="{X+s*0.75*__import__("math").cos(a)}" y1="{Y+s*0.75*__import__("math").sin(a)}" '
                       f'x2="{X+s*1.0*__import__("math").cos(a)}" y2="{Y+s*1.0*__import__("math").sin(a)}" {st}/>'
                       for a in [i * 0.785 for i in range(8)])
        return f'<circle cx="{X}" cy="{Y}" r="{s*0.45}" fill="{color}"/>' + rays
    if kind == "shake":
        return (f'<rect x="{X-s*0.35}" y="{Y-s*0.6}" width="{s*0.7}" height="{s*1.2}" rx="{s*0.1}" {st}/>'
                f'<path d="M{X-s*0.7},{Y-s*0.5} q{-s*0.3},{s*0.5} 0,{s} M{X+s*0.7},{Y-s*0.5} q{s*0.3},{s*0.5} 0,{s}" {st}/>')
    if kind == "infinity":
        return (f'<path d="M{X},{Y} C{X-s*0.3},{Y-s*0.8} {X-s*1.1},{Y-s*0.6} {X-s*1.0},{Y} '
                f'C{X-s*1.1},{Y+s*0.6} {X-s*0.3},{Y+s*0.8} {X},{Y} '
                f'C{X+s*0.3},{Y-s*0.8} {X+s*1.1},{Y-s*0.6} {X+s*1.0},{Y} '
                f'C{X+s*1.1},{Y+s*0.6} {X+s*0.3},{Y+s*0.8} {X},{Y}" {st}/>')
    return ""


def text(x, y, s, S, size=3.2, anchor="middle", weight="700", color="#fff", font="Arial, Helvetica, sans-serif"):
    return (f'<text x="{x*S:.1f}" y="{y*S:.1f}" font-family="{font}" font-size="{size*S:.1f}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{s}</text>')


def statement(x, y, S, family, ic, label, marker_id, socket=True, stroke=None):
    fill = COL[family]
    out = [f'<polygon points="{pts([(px*S, py*S) for px, py in statement_outline(x, y, socket)])}" '
           f'fill="{fill}" stroke="{stroke or COL["stroke"]}" stroke-width="{0.5*S:.1f}" stroke-linejoin="round"/>']
    mx, my = V.geometry["marker_offset"]["block"]
    out.append(marker(x + mx - MARK / 2, y + my - MARK / 2, MARK, marker_id, S))
    out.append(icon(ic, x + 11, y + 15, S))
    if socket:
        # engraved outline of the empty socket so a missing parameter is visible
        out.append(f'<rect x="{(x+W-SOCK_D-0.5)*S:.1f}" y="{(y+SOCK_Y0-1.6)*S:.1f}" width="{(SOCK_D+0.5)*S:.1f}" '
                   f'height="{(SOCK_Y1-SOCK_Y0+3.2)*S:.1f}" fill="#00000022"/>')
    out.append(text(x + 14, y + 29.2, label, S, size=3.6))
    return "\n".join(out)


def start(x, y, S, marker_id=0):
    out = [f'<path d="{start_outline(x, y, S)}" fill="{COL["start"]}" stroke="{COL["stroke"]}" '
           f'stroke-width="{0.5*S:.1f}" stroke-linejoin="round"/>']
    mx, my = V.geometry["marker_offset"]["start"]
    out.append(marker(x + mx - MARK / 2, y + my - MARK / 2, MARK, marker_id, S))
    out.append(icon("flag", x + 11, y + 15, S))
    out.append(text(x + 16, y + 29.2, "START", S, size=3.6))
    return "\n".join(out)


def tile(x, y, S, kind, value, marker_id):
    fill = COL["sensor"] if kind == "sensor" else COL["param"]
    ink = "#2b2b2b"
    out = [f'<polygon points="{pts([(px*S, py*S) for px, py in tile_outline(x, y)])}" fill="{fill}" '
           f'stroke="{COL["stroke"]}" stroke-width="{0.5*S:.1f}" stroke-linejoin="round"/>']
    mx, my = V.geometry["marker_offset"]["tile"]
    out.append(marker(x + mx - MARK_SMALL / 2, y + my - MARK_SMALL / 2, MARK_SMALL, marker_id, S, quiet=0.8))
    if kind == "number":
        n = int(value)
        rows = [min(3, n - 3 * r) for r in range((n + 2) // 3)]
        for r, cnt in enumerate(rows):
            for i in range(cnt):
                cx = x + 8 + 4 * (i - (cnt - 1) / 2)
                cy = y + 15 + 3.8 * r
                out.append(f'<circle cx="{cx*S:.1f}" cy="{cy*S:.1f}" r="{1.3*S:.1f}" fill="{ink}"/>')
        out.append(text(x + 8, y + 30, str(n), S, size=5.5, color=ink))
    elif kind == "colour":
        out.append(f'<rect x="{(x+2.5)*S:.1f}" y="{(y+13)*S:.1f}" width="{11*S:.1f}" height="{16*S:.1f}" '
                   f'rx="{1.5*S:.1f}" fill="{value}" stroke="{ink}" stroke-width="{0.4*S:.1f}"/>')
    elif kind == "infinity":
        out.append(icon("infinity", x + 8, y + 21, S, size=10, color=ink))
    elif kind == "note":
        h = {"low": 4, "mid": 7, "high": 10}[value]
        out.append(icon("note", x + 8, y + 19, S, size=9, color=ink))
        out.append(f'<rect x="{(x+3)*S:.1f}" y="{(y+30-h)*S:.1f}" width="{2*S:.1f}" height="{h*S:.1f}" fill="{ink}"/>')
    elif kind == "expression":
        out.append(icon("face", x + 8, y + 19, S, size=9, color=ink))
        out.append(text(x + 8, y + 30, value[:5], S, size=2.6, color=ink))
    elif kind == "sensor":
        out.append(icon(value, x + 8, y + 19, S, size=10, color=ink))
        out.append(text(x + 8, y + 30, SENSOR_LABEL.get(value, ""), S, size=2.8, color=ink))
    return "\n".join(out)


def spine(x, y, rows, S):
    mx, my = V.geometry["marker_offset"]["spine"]
    return (f'<polygon points="{pts([(px*S, py*S) for px, py in spine_outline(x, y, rows)])}" fill="{COL["spine"]}" '
            f'stroke="{COL["stroke"]}" stroke-width="{0.5*S:.1f}" stroke-linejoin="round"/>'
            + marker(x + mx - MARK_SMALL / 2, y + my - MARK_SMALL / 2, MARK_SMALL, pid(f"spine{rows}"), S, quiet=0.8)
            + text(x + 8, y + rows * W - 3, "end", S, size=3, color="#2b2b2b"))


SENSOR_LABEL = {"waves": "close", "bump": "bump", "eye": "sees", "moon": "dark", "sun": "bright", "shake": "shake"}


def svg(width_mm, height_mm, S, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_mm*S:.0f}" height="{height_mm*S:.0f}" '
            f'viewBox="0 0 {width_mm*S:.0f} {height_mm*S:.0f}" font-family="Arial, Helvetica, sans-serif">\n'
            f'<title>{title}</title>\n<rect width="100%" height="100%" fill="{COL["bg"]}"/>\n{body}\n</svg>\n')


def callout(S, x1, y1, x2, y2, label, anchor="start"):
    return (f'<line x1="{x1*S:.1f}" y1="{y1*S:.1f}" x2="{x2*S:.1f}" y2="{y2*S:.1f}" stroke="#555" stroke-width="{0.25*S:.1f}"/>'
            f'<circle cx="{x1*S:.1f}" cy="{y1*S:.1f}" r="{0.6*S:.1f}" fill="#555"/>'
            + text(x2 + (0.8 if anchor == "start" else -0.8), y2 + 1, label, S, size=2.6, anchor=anchor, weight="400", color="#222"))


def dim(S, x1, y1, x2, y2, label, offset=(0, -1.5)):
    return (f'<line x1="{x1*S:.1f}" y1="{y1*S:.1f}" x2="{x2*S:.1f}" y2="{y2*S:.1f}" stroke="#888" stroke-width="{0.25*S:.1f}" '
            f'marker-start="url(#a)" marker-end="url(#a)"/>'
            + text((x1 + x2) / 2 + offset[0], (y1 + y2) / 2 + offset[1], label, S, size=2.4, weight="400", color="#444"))


# ---------------------------------------------------------------- anatomy
def anatomy():
    S = 9
    body = ['<defs><marker id="a" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">'
            '<circle cx="3" cy="3" r="1.5" fill="#888"/></marker></defs>']
    body.append(text(4, 7, "One statement block, top view (Forward) with its parameter tile", S, size=3.6, anchor="start", color="#222"))
    bx, by = 72, 16
    body.append(statement(bx, by, S, "motion", "up", "forward", 7))
    body.append(tile(bx + W + 6, by, S, "number", 3, 21))
    # callouts
    body.append(callout(S, bx + 8, by + 1.5, bx - 4, by - 4, "notch on top: the block above hooks in", anchor="end"))
    body.append(callout(S, bx + 25, by + 7, bx + 60, by - 6, "ArUco marker 10 mm, printed white-on-black; this is what the camera reads"))
    body.append(callout(S, bx + 11, by + 15, bx - 4, by + 15, "raised icon, 0.6 mm, tactile", anchor="end"))
    body.append(callout(S, bx + 30, by + 22, bx + 60, by + 22, "dovetail socket; engraved outline shows when empty"))
    body.append(callout(S, bx + 14, by + 28.5, bx - 4, by + 33, "word for early readers (optional)", anchor="end"))
    body.append(callout(S, bx + 8, by + 33.5, bx - 4, by + 42, "tab underneath: hooks into the block below", anchor="end"))
    body.append(callout(S, bx + W + 6 + 8, by + 20, bx + 60, by + 34, "parameter tile 16 x 32 mm: dots and digit, small marker"))
    body.append(callout(S, bx + W + 6 - 3.5, by + 22, bx + 60, by + 40, "male dovetail: fits only the socket, only this way round"))
    body.append(dim(S, bx, by + 40, bx + W, by + 40, "32 mm (4 studs)", (0, 3.5)))
    # side view / cross-section
    sy = by + 56
    body.append(text(4, sy - 3, "Cross-section (front view) through the same block, snapped on a baseplate", S, size=3.6, anchor="start", color="#222"))
    base_y = sy + 16
    body.append(f'<rect x="{(bx-10)*S}" y="{base_y*S}" width="{(W+30)*S}" height="{3.2*S}" fill="#d8d8d8" stroke="#888" stroke-width="{0.25*S}"/>')
    for i in range(6):
        sx = bx - 6 + i * 8
        body.append(f'<rect x="{(sx+1.6)*S:.1f}" y="{(base_y-1.7)*S:.1f}" width="{4.8*S:.1f}" height="{1.7*S:.1f}" fill="#d8d8d8" stroke="#888" stroke-width="{0.25*S}"/>')
    # block body: 9.6 tall, open cavities underneath around the studs (anti-studs)
    top = base_y - 9.6
    body.append(f'<path d="M{bx*S},{base_y*S} V{top*S} H{(bx+W)*S} V{base_y*S} H{(bx+W-1.6)*S} V{(base_y-2.2)*S} H{(bx+W-6.4)*S} V{base_y*S} '
                f'H{(bx+W-9.6)*S} V{(base_y-2.2)*S} H{(bx+W-14.4)*S} V{base_y*S} H{(bx+W-17.6)*S} V{(base_y-2.2)*S} H{(bx+W-22.4)*S} V{base_y*S} '
                f'H{(bx+W-25.6)*S} V{(base_y-2.2)*S} H{(bx+W-30.4)*S} V{base_y*S} Z" fill="{COL["motion"]}" stroke="{COL["stroke"]}" stroke-width="{0.4*S}"/>')
    # icon relief and marker inlay
    body.append(f'<rect x="{(bx+7)*S}" y="{(top-0.6)*S}" width="{8*S}" height="{0.6*S}" fill="#fff" stroke="{COL["stroke"]}" stroke-width="{0.3*S}"/>')
    body.append(f'<rect x="{(bx+20)*S}" y="{(top)*S}" width="{10*S}" height="{0.6*S}" fill="#111"/>')
    for i in range(5):
        body.append(f'<rect x="{(bx+21.7+i*1.67)*S:.1f}" y="{top*S}" width="{0.8*S}" height="{0.6*S}" fill="#fff"/>')
    body.append(callout(S, bx + 11, top - 0.3, bx - 4, top - 6, "icon stands 0.6 mm proud", anchor="end"))
    body.append(callout(S, bx + 25, top + 0.3, bx + 60, top - 6, "marker: top 0.6 mm printed in a second colour (pause and swap filament)"))
    body.append(callout(S, bx + 4, base_y - 1.1, bx - 4, base_y + 10, "anti-stud cavities grip the baseplate studs", anchor="end"))
    body.append(callout(S, bx + 14, top + 5, bx + 60, top + 5, "solid body, 9.6 mm (three plates), PETG"))
    body.append(dim(S, bx + W + 4, top, bx + W + 4, base_y, "9.6", (4.5, 0)))
    body.append(text(bx - 60, base_y + 14, "The top is flat like a LEGO tile: nothing to block the camera's view of the marker and icon.", S, size=2.8, anchor="start", weight="400", color="#444"))
    return svg(235, base_y + 20, S, "\n".join(body), "Block anatomy")


# ---------------------------------------------------------------- gallery
def gallery():
    S = 5
    body = []
    y = 6
    body.append(text(4, y, "Version 1 block families (icons are first drafts to test on paper)", S, size=4, anchor="start", color="#222"))
    rows = [
        ("Start and motion (blue)", ["start", "forward", "back", "turn_left", "turn_right", "stop"]),
        ("Action (purple)", ["beep", "light", "face", "wait", "arm_up", "arm_down"]),
        ("Control (orange) and the spine that makes a loop body", ["repeat", "if", "else", "wait_until", "spine2"]),
    ]
    for title, names in rows:
        y += 8
        body.append(text(4, y, title, S, size=3.2, anchor="start", weight="400", color="#444"))
        y += 3
        x = 6
        for name in names:
            body.append(piece_svg(name, x, y, S))
            if name.startswith("spine"):
                body.append(text(x + 20, y + 10, "spine, 1 to 4 rows long,", S, size=2.6, anchor="start", weight="400", color="#444"))
                body.append(text(x + 20, y + 14, "hangs under REPEAT, IF or ELSE;", S, size=2.6, anchor="start", weight="400", color="#444"))
                body.append(text(x + 20, y + 18, "the body sits to its right", S, size=2.6, anchor="start", weight="400", color="#444"))
                x += 20
            x += 42
        y += W + 6
    y += W + 6
    body.append(text(4, y, "Parameter tiles (white) and sensor tiles (yellow): they plug into the socket on the right of a block", S, size=3.2, anchor="start", weight="400", color="#444"))
    y += 3
    x = 10
    for name in ["n1", "n3", "n5", "forever", "red", "blue", "note_mid", "happy", "close", "bumped", "sees_colour", "dark", "bright", "shaken"]:
        body.append(piece_svg(name, x, y, S))
        x += 24
    y += W + 10
    return svg(362, y, S, "\n".join(body), "Block gallery")


def piece_svg(name: str, x: float, y: float, S: float) -> str:
    """Draw any vocabulary piece by name with its real marker."""
    p = V.by_name[name]
    if p.kind == "start":
        return start(x, y, S, p.id)
    if p.kind in ("statement", "head"):
        return statement(x, y, S, p.family, p.icon, p.label, p.id, socket=p.socket is not None)
    if p.kind == "spine":
        return spine(x, y, p.rows, S)
    if p.kind == "tile":
        value = {"number": p.value, "colour": p.extra.get("hex"), "infinity": None, "sensor": p.icon,
                 "note": p.value, "expression": p.value}[p.type]
        return tile(x, y, S, p.type, value, p.id)
    raise ValueError(name)


# ---------------------------------------------------------------- layout
# (piece name, x in 16 mm columns, y in 32 mm rows), relative to START
EXAMPLE_PROGRAM = [
    ("start", 0, 0),
    ("forward", 0, 1), ("n3", 2, 1),
    ("repeat", 0, 2), ("n4", 2, 2),
    ("spine3", 0, 3),
    ("forward", 1, 3), ("n2", 3, 3),
    ("turn_right", 1, 4), ("n1", 3, 4),
    ("beep", 1, 5),
    ("light", 0, 6), ("red", 2, 6),
]


def corner_centres(pad, oy, base):
    """Centres (mm) of the four stand markers, keyed by marker id."""
    return {90: (pad + 6, oy + 6), 91: (pad + base - 6, oy + 6),
            92: (pad + 6, oy + base - 6), 93: (pad + base - 6, oy + base - 6)}


def layout():
    S = 3.2
    pad = 6
    base = 256
    body = []
    body.append(text(pad, 5, "A program on a 32 x 32 baseplate, as the camera sees it", S, size=4, anchor="start", color="#222"))
    oy = 10
    body.append(f'<rect x="{pad*S}" y="{oy*S}" width="{base*S}" height="{base*S}" fill="#e9e9e9" stroke="#999" stroke-width="{0.3*S}"/>')
    for i in range(32):
        for j in range(32):
            body.append(f'<circle cx="{(pad+4+8*i)*S:.1f}" cy="{(oy+4+8*j)*S:.1f}" r="{1.9*S:.1f}" fill="#dcdcdc" stroke="#c8c8c8" stroke-width="{0.2*S}"/>')
    # four stand markers at the corners of the baseplate area
    for cid, (cx, cy) in corner_centres(pad, oy, base).items():
        body.append(marker(cx - 5, cy - 5, 10, cid, S))
    ox, r = pad + 16, oy + 16
    # program: START, forward 3, repeat 4 { forward 2, turn right, beep }, light red, stop
    for name, col, row in EXAMPLE_PROGRAM:
        body.append(piece_svg(name, ox + col * TILE_W, r + row * W, S))
    # read-aloud transcript on the right
    tx = pad + 150
    ty = oy + 20
    body.append(text(tx, ty, "What the brain says before running:", S, size=3.4, anchor="start", color="#222"))
    lines = ["“Forward three.", "Repeat four times:", "    forward two,", "    turn right,", "    beep.", "Light red.", "Done.”",
             "", "How the layout is read:", "• START fixes the origin", "• blocks are read top to bottom", "• a block 16 mm to the right", "   belongs to the spine beside it",
             "• a tile in a socket is that", "   block's parameter", "• corner markers on the stand", "   map pixels to millimetres"]
    for i, ln in enumerate(lines):
        body.append(text(tx, ty + 6 + i * 5.2, ln, S, size=3.0, anchor="start", weight="400", color="#333"))
    return svg(base + 2 * pad, base + oy + pad, S, "\n".join(body), "Program layout")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("block-anatomy.svg", anatomy), ("block-gallery.svg", gallery), ("program-layout.svg", layout)]:
        (OUT / name).write_text(fn())
        print("wrote", OUT / name)
