#!/usr/bin/env python3
"""Generate concept sketches of the blocks as SVG files in docs/images/.

Dimensions are in millimetres and scaled to pixels with S. These are design
sketches, not the CAD; the CAD will be derived from the numbers in
docs/04-architecture.md once the vocabulary is frozen.
"""
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "images"

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


def marker(x, y, side, seed, S):
    """A fake 4x4 ArUco marker with black border, side mm, at (x, y) mm."""
    rnd = random.Random(seed)
    c = side / 6
    out = [f'<rect x="{x*S:.1f}" y="{y*S:.1f}" width="{side*S:.1f}" height="{side*S:.1f}" fill="#111"/>']
    for i in range(4):
        for j in range(4):
            if rnd.random() < 0.5:
                out.append(f'<rect x="{(x+c*(1+i))*S:.1f}" y="{(y+c*(1+j))*S:.1f}" '
                           f'width="{c*S:.1f}" height="{c*S:.1f}" fill="#fff"/>')
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
    if kind == "infinity":
        return (f'<path d="M{X},{Y} C{X-s*0.3},{Y-s*0.8} {X-s*1.1},{Y-s*0.6} {X-s*1.0},{Y} '
                f'C{X-s*1.1},{Y+s*0.6} {X-s*0.3},{Y+s*0.8} {X},{Y} '
                f'C{X+s*0.3},{Y-s*0.8} {X+s*1.1},{Y-s*0.6} {X+s*1.0},{Y} '
                f'C{X+s*1.1},{Y+s*0.6} {X+s*0.3},{Y+s*0.8} {X},{Y}" {st}/>')
    return ""


def text(x, y, s, S, size=3.2, anchor="middle", weight="700", color="#fff", font="Arial, Helvetica, sans-serif"):
    return (f'<text x="{x*S:.1f}" y="{y*S:.1f}" font-family="{font}" font-size="{size*S:.1f}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{s}</text>')


def statement(x, y, S, family, ic, label, seed, socket=True, stroke=None):
    fill = COL[family]
    out = [f'<polygon points="{pts([(px*S, py*S) for px, py in statement_outline(x, y, socket)])}" '
           f'fill="{fill}" stroke="{stroke or COL["stroke"]}" stroke-width="{0.5*S:.1f}" stroke-linejoin="round"/>']
    out.append(marker(x + 20, y + 2, MARK, seed, S))
    out.append(icon(ic, x + 11, y + 15, S))
    if socket:
        # engraved outline of the empty socket so a missing parameter is visible
        out.append(f'<rect x="{(x+W-SOCK_D-0.5)*S:.1f}" y="{(y+SOCK_Y0-1.6)*S:.1f}" width="{(SOCK_D+0.5)*S:.1f}" '
                   f'height="{(SOCK_Y1-SOCK_Y0+3.2)*S:.1f}" fill="#00000022"/>')
    out.append(text(x + 14, y + 29.2, label, S, size=3.6))
    return "\n".join(out)


def start(x, y, S, seed=1):
    out = [f'<path d="{start_outline(x, y, S)}" fill="{COL["start"]}" stroke="{COL["stroke"]}" '
           f'stroke-width="{0.5*S:.1f}" stroke-linejoin="round"/>']
    out.append(marker(x + 20, y + 4, MARK, seed, S))
    out.append(icon("flag", x + 11, y + 15, S))
    out.append(text(x + 16, y + 29.2, "START", S, size=3.6))
    return "\n".join(out)


def tile(x, y, S, kind, value, seed):
    fill = COL["sensor"] if kind == "sensor" else COL["param"]
    ink = "#2b2b2b"
    out = [f'<polygon points="{pts([(px*S, py*S) for px, py in tile_outline(x, y)])}" fill="{fill}" '
           f'stroke="{COL["stroke"]}" stroke-width="{0.5*S:.1f}" stroke-linejoin="round"/>']
    out.append(marker(x + 4, y + 2, MARK_SMALL, seed, S))
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
    elif kind == "sensor":
        out.append(icon(value, x + 8, y + 19, S, size=10, color=ink))
        out.append(text(x + 8, y + 30, {"waves": "close", "bump": "bump", "eye": "sees"}[value], S, size=2.8, color=ink))
    return "\n".join(out)


def spine(x, y, rows, S):
    return (f'<polygon points="{pts([(px*S, py*S) for px, py in spine_outline(x, y, rows)])}" fill="{COL["spine"]}" '
            f'stroke="{COL["stroke"]}" stroke-width="{0.5*S:.1f}" stroke-linejoin="round"/>'
            + text(x + 8, y + rows * W - 3, "end", S, size=3, color="#2b2b2b"))


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
        ("Start and motion (blue)", [("start",), ("motion", "up", "forward", True), ("motion", "down", "back", True),
                                     ("motion", "left", "turn left", True), ("motion", "right", "turn right", True), ("motion", "stop", "stop", False)]),
        ("Action (purple)", [("action", "note", "beep", True), ("action", "bulb", "light", True), ("action", "face", "face", True),
                             ("action", "hourglass", "wait", True), ("action", "arm", "arm up", False)]),
        ("Control (orange) and the spine that makes a loop body", [("control", "loop", "repeat", True), ("control", "fork", "if", True),
                                                                    ("control", "eye", "wait until", True), ("spine", 2)]),
    ]
    seed = 100
    for title, items in rows:
        y += 8
        body.append(text(4, y, title, S, size=3.2, anchor="start", weight="400", color="#444"))
        y += 3
        x = 6
        for it in items:
            seed += 1
            if it[0] == "start":
                body.append(start(x, y, S, seed))
            elif it[0] == "spine":
                body.append(spine(x, y, it[1], S))
                body.append(text(x + 20, y + 10, "spine, 1 to 4 rows long,", S, size=2.6, anchor="start", weight="400", color="#444"))
                body.append(text(x + 20, y + 14, "hangs under REPEAT or IF;", S, size=2.6, anchor="start", weight="400", color="#444"))
                body.append(text(x + 20, y + 18, "the loop body sits to its right", S, size=2.6, anchor="start", weight="400", color="#444"))
                x += 20
            else:
                fam, ic, label, sock = it
                body.append(statement(x, y, S, fam, ic, label, seed, socket=sock))
            x += 42
        y += W + 6
    y += W + 6
    body.append(text(4, y, "Parameter tiles (white) and sensor tiles (yellow): they plug into the socket on the right of a block", S, size=3.2, anchor="start", weight="400", color="#444"))
    y += 3
    x = 10
    for kind, val in [("number", 1), ("number", 3), ("number", 5), ("colour", "#e53935"), ("colour", "#1e88e5"), ("infinity", None),
                      ("sensor", "waves"), ("sensor", "bump"), ("sensor", "eye")]:
        seed += 1
        body.append(tile(x, y, S, kind, val, seed))
        x += 24
    y += W + 10
    return svg(262, y, S, "\n".join(body), "Block gallery")


# ---------------------------------------------------------------- layout
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
    for (mx, my) in [(pad, oy), (pad + base - 12, oy), (pad, oy + base - 12), (pad + base - 12, oy + base - 12)]:
        body.append(marker(mx + 1, my + 1, 10, 900 + mx + my, S))
    ox, r = pad + 16, oy + 16
    # program: START, forward 3, repeat 4 { forward 2, turn right, beep }, light red, stop
    body.append(start(ox, r, S, 1))
    body.append(statement(ox, r + W, S, "motion", "up", "forward", 2)); body.append(tile(ox + W, r + W, S, "number", 3, 3))
    body.append(statement(ox, r + 2 * W, S, "control", "loop", "repeat", 4)); body.append(tile(ox + W, r + 2 * W, S, "number", 4, 5))
    body.append(spine(ox, r + 3 * W, 3, S))
    body.append(statement(ox + TILE_W, r + 3 * W, S, "motion", "up", "forward", 6)); body.append(tile(ox + TILE_W + W, r + 3 * W, S, "number", 2, 7))
    body.append(statement(ox + TILE_W, r + 4 * W, S, "motion", "right", "turn right", 8)); body.append(tile(ox + TILE_W + W, r + 4 * W, S, "number", 1, 9))
    body.append(statement(ox + TILE_W, r + 5 * W, S, "action", "note", "beep", 10, socket=False))
    body.append(statement(ox, r + 6 * W, S, "action", "bulb", "light", 11)); body.append(tile(ox + W, r + 6 * W, S, "colour", "#e53935", 12))
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
