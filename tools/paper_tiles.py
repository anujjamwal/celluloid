#!/usr/bin/env python3
"""Printable 1:1 paper tiles for the Phase 0 play test and the Phase 1 webcam
pipeline. Writes A4 SVG pages (1 unit = 1 mm) to docs/paper/ and, if
Playwright is available, a combined PDF.

Print at 100 % scale on card, cut on the grey lines, and the pieces are
exactly the size the 3D-printed blocks will be. Marker ids are the real ones
from blocks/vocabulary.json, so the camera code reads paper and plastic alike.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.block_sketches import V, piece_svg, marker, text, svg, W, TILE_W  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "docs" / "paper"
PAGE_W, PAGE_H, MARGIN = 210, 297, 10

# how many of each piece to print for the first set
COUNTS = {
    "start": 1, "forward": 4, "back": 2, "turn_left": 2, "turn_right": 2, "stop": 1,
    "beep": 2, "light": 2, "face": 1, "wait": 2, "arm_up": 1, "arm_down": 1,
    "repeat": 2, "if": 1, "else": 1, "wait_until": 1,
    **{f"n{i}": 2 for i in range(1, 10)}, "forever": 1,
    "red": 1, "green": 1, "blue": 1, "yellow": 1, "white": 1,
    "note_low": 1, "note_mid": 1, "note_high": 1, "happy": 1, "surprised": 1, "sleepy": 1,
    "close": 1, "bumped": 1, "sees_colour": 1, "dark": 1, "bright": 1, "shaken": 1,
    "spine1": 2, "spine2": 2, "spine3": 2, "spine4": 1,
}


def cut_box(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#bbb" stroke-width="0.2" stroke-dasharray="1 1"/>'


def pages():
    """Yield (title, [svg fragments]) per A4 page, packing pieces left to right."""
    items = []
    for name, n in COUNTS.items():
        p = V.by_name[name]
        w = TILE_W if p.kind in ("tile", "spine") else W
        h = W * (p.rows if p.kind == "spine" else 1)
        # tabs/dovetails stick out: leave 4 mm around every piece
        items += [(name, w + 8, h + 8)] * n
    # tallest first so rows pack well
    items.sort(key=lambda t: (-t[2], -t[1]))
    page, x, y, row_h = [], MARGIN, MARGIN + 8, 0
    pageno = 1
    for name, w, h in items:
        if x + w > PAGE_W - MARGIN:
            x, y, row_h = MARGIN, y + row_h, 0
        if y + h > PAGE_H - MARGIN:
            yield pageno, page
            pageno += 1
            page, x, y, row_h = [], MARGIN, MARGIN + 8, 0
        page.append(cut_box(x, y, w, h))
        page.append(piece_svg(name, x + 4, y + 4, 1))
        x += w
        row_h = max(row_h, h)
    if page:
        yield pageno, page


def stand_page():
    """The four corner markers for the camera stand, plus a 100 mm ruler to check print scale."""
    body = [text(MARGIN, MARGIN, "Corner markers for the camera stand. Check the ruler is exactly 100 mm.", 1, size=4, anchor="start", color="#222")]
    for i, (cid, label) in enumerate([(90, "top-left"), (91, "top-right"), (92, "bottom-left"), (93, "bottom-right")]):
        x, y = MARGIN + (i % 2) * 60, MARGIN + 15 + (i // 2) * 60
        body.append(cut_box(x, y, 40, 40))
        body.append(marker(x + 15, y + 12, 10, cid, 1, quiet=2))
        body.append(text(x + 20, y + 34, f"{label}  (id {cid})", 1, size=3, color="#222"))
    y = MARGIN + 150
    body.append(f'<line x1="{MARGIN}" y1="{y}" x2="{MARGIN+100}" y2="{y}" stroke="#000" stroke-width="0.4"/>')
    for i in range(11):
        body.append(f'<line x1="{MARGIN+i*10}" y1="{y-3}" x2="{MARGIN+i*10}" y2="{y+3}" stroke="#000" stroke-width="0.3"/>')
    body.append(text(MARGIN + 50, y + 8, "100 mm", 1, size=3.5, color="#222"))
    return body


def write_pages():
    OUT.mkdir(parents=True, exist_ok=True)
    files = []
    for n, frags in pages():
        head = text(MARGIN, MARGIN + 3, f"Paper blocks, page {n}. Print at 100 % on card. Cut on the dotted lines.", 1, size=3.5, anchor="start", color="#222")
        f = OUT / f"tiles-{n}.svg"
        f.write_text(svg(PAGE_W, PAGE_H, 1, head + "\n" + "\n".join(frags), f"Paper tiles {n}").replace(
            f'width="{PAGE_W}" height="{PAGE_H}"', f'width="{PAGE_W}mm" height="{PAGE_H}mm"', 1))
        files.append(f)
    f = OUT / "stand-markers.svg"
    f.write_text(svg(PAGE_W, PAGE_H, 1, "\n".join(stand_page()), "Stand markers").replace(
        f'width="{PAGE_W}" height="{PAGE_H}"', f'width="{PAGE_W}mm" height="{PAGE_H}mm"', 1))
    files.append(f)
    return files


def to_pdf(files, out):
    """Combine the SVG pages into one A4 PDF with headless Chromium (Playwright)."""
    script = Path(__file__).with_name("svg_to_pdf.js")
    subprocess.run(["node", str(script), str(out)] + [str(f) for f in files], check=True)


if __name__ == "__main__":
    files = write_pages()
    for f in files:
        print("wrote", f)
    try:
        to_pdf(files, OUT / "paper-blocks.pdf")
        print("wrote", OUT / "paper-blocks.pdf")
    except Exception as e:
        print("no PDF (needs node + playwright):", e)
