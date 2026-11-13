"""Generate every ChangePay logo SVG from the existing app logo artwork.

    pip install fonttools uharfbuzz pillow potracer numpy
    python brand/scripts/build_logo.py

Source: brand/logo/source/consumer-logo.png — the logo shipped in ConsumerApp/DeliveryApp/SellerApp
(same artwork; only the gradient differs per app). It is traced once to smooth vector curves, split
into the ribbon mark and the "ChangePay" wordmark, and recoloured with each product's gradient from
tokens.json. The original PNGs stay in logo/source/ for reference.
"""

import json
from pathlib import Path

import numpy as np
import potrace
import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image

BRAND = Path(__file__).resolve().parent.parent
OUT = BRAND / "logo"
T = json.loads((BRAND / "tokens/tokens.json").read_text())
P, PRODUCTS = T["palette"], T["products"]
WHITE = "#FFFFFF"


def ref(c, scale):
    if c.startswith("#"):
        return c
    fam, step = c.replace("@", f"{scale}.").split(".")
    return P[fam][step]


# ------------------------------------------------------------------ trace
def trace(png):
    im = Image.open(png).convert("RGBA")
    w, h = im.size
    bm = np.array(im)[:, :, 3] > 127
    curves = []
    for c in potrace.Bitmap(bm).trace(turdsize=4, alphamax=1.0, opticurve=True, opttolerance=0.2):
        pts = [c.start_point] + [s.end_point for s in c.segments]
        xs, ys = [p.x for p in pts], [p.y for p in pts]
        box = (min(xs), min(ys), max(xs), max(ys))
        if box[0] <= 0 and box[1] <= 0 and box[2] >= w and box[3] >= h:
            continue  # potrace's frame around the canvas
        d = [f"M{c.start_point.x:.2f} {c.start_point.y:.2f}"]
        for s in c.segments:
            if s.is_corner:
                d.append(f"L{s.c.x:.2f} {s.c.y:.2f}L{s.end_point.x:.2f} {s.end_point.y:.2f}")
            else:
                d.append(f"C{s.c1.x:.2f} {s.c1.y:.2f} {s.c2.x:.2f} {s.c2.y:.2f} {s.end_point.x:.2f} {s.end_point.y:.2f}")
        curves.append((box, "".join(d) + "Z"))
    return curves


def union(boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


CURVES = trace(BRAND / "logo/source/consumer-logo.png")
# The ribbon is the tallest shape starting at the far left; its hole sits inside its box.
RIBBON = max(CURVES, key=lambda c: (c[0][3] - c[0][1]) * (c[0][0] < 100))
inside = lambda b, o: b[0] >= o[0] and b[1] >= o[1] and b[2] <= o[2] and b[3] <= o[3]
MARK = [c for c in CURVES if c is RIBBON or (inside(c[0], RIBBON[0]) and c[0][3] < 150)]
WORD = [c for c in CURVES if c not in MARK]
MARK_BOX, WORD_BOX = union([c[0] for c in MARK]), union([c[0] for c in WORD])
ALL_BOX = union([MARK_BOX, WORD_BOX])
MARK_D = "".join(c[1] for c in MARK)
WORD_D = "".join(c[1] for c in WORD)


# ------------------------------------------------------------------ descriptor text (Inter outlines)
class Outliner:
    def __init__(self, path):
        self.font = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
        self.tt = TTFont(str(path))
        self.gs, self.upm, self.order = self.tt.getGlyphSet(), self.tt["head"].unitsPerEm, self.tt.getGlyphOrder()
        self.cap = self.tt["OS/2"].sCapHeight

    def run(self, text, px, x, baseline, tracking=-0.01):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"kern": True})
        s, gx, pen, bp = px / self.upm, 0, SVGPathPen(self.gs), BoundsPen(self.gs)
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = self.order[info.codepoint]
            self.gs[name].draw(TransformPen(pen, (s, 0, 0, -s, x + gx * s, baseline)))
            self.gs[name].draw(TransformPen(bp, (1, 0, 0, 1, gx, 0)))
            gx += pos.x_advance + tracking * self.upm
        return pen.getCommands(), x + bp.bounds[2] * s


INTER = Outliner(BRAND / "fonts/ttf/Inter-SemiBold.ttf")


# ------------------------------------------------------------------ svg helpers
def grad(gid, colors, box):
    """Horizontal gradient across one shape's own box — how the original artwork is coloured."""
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{box[0]:.1f}" y1="0" x2="{box[2]:.1f}" y2="0">'
            f'<stop offset="0" stop-color="{colors[0]}"/><stop offset="1" stop-color="{colors[1]}"/></linearGradient>')


def svg(box, body, title, pad=8, defs=""):
    x, y, w, h = box[0] - pad, box[1] - pad, box[2] - box[0] + 2 * pad, box[3] - box[1] + 2 * pad
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.1f} {y:.1f} {w:.1f} {h:.1f}" '
            f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{title}"><title>{title}</title>'
            + (f"<defs>{defs}</defs>" if defs else "") + f"{body}</svg>\n")


def fill_paths(mark_fill, word_fill, mark=True, word=True):
    out = ""
    if mark:
        out += f'<path d="{MARK_D}" fill="{mark_fill}" fill-rule="evenodd"/>'
    if word:
        out += f'<path d="{WORD_D}" fill="{word_fill}" fill-rule="evenodd"/>'
    return out


def descriptor(text, color):
    """Product descriptor right of the wordmark: divider + Inter SemiBold, cap height = wordmark x-height."""
    base = WORD_BOX[3] - 33  # wordmark baseline (above the descender of g/y)
    px = 150
    x0 = WORD_BOX[2] + 50
    rule = f'<rect x="{x0:.1f}" y="{WORD_BOX[1] + 6:.1f}" width="6" height="{base - WORD_BOX[1] - 4:.1f}" rx="3" fill="{color}" opacity=".3"/>'
    d, x1 = INTER.run(text, px, x0 + 56, base)
    return rule + f'<path d="{d}" fill="{color}"/>', x1


def write(name, text):
    f = OUT / name
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text)


def app_icon(colors, filled, rounded, gid):
    """1024 icon. Default (filled=False) matches today's launchers: white tile, gradient mark."""
    bx = MARK_BOX
    k = 700 / max(bx[2] - bx[0], bx[3] - bx[1])
    cx, cy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
    tile_grad = (f'<linearGradient id="{gid}t" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{colors[0]}"/>'
                 f'<stop offset="1" stop-color="{colors[1]}"/></linearGradient>')
    rx = ' rx="225"' if rounded else ""
    tile = f'<rect width="1024" height="1024"{rx} fill="{"url(#" + gid + "t)" if filled else WHITE}"/>'
    mark_fill = WHITE if filled else f"url(#{gid})"
    body = (f"<defs>{grad(gid, colors, bx)}{tile_grad}</defs>{tile}"
            f'<g transform="translate(512 520) scale({k:.4f}) translate({-cx:.1f} {-cy:.1f})">'
            f'<path d="{MARK_D}" fill="{mark_fill}" fill-rule="evenodd"/></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024" '
            f'role="img" aria-label="ChangePay"><title>ChangePay</title>{body}</svg>\n')


def main():
    for old in OUT.glob("**/*.svg"):
        if "source" not in old.parts:
            old.unlink()

    brand = PRODUCTS["consumer"]["gradient"]
    # master logo, mark, wordmark (flagship gradient)
    d = grad("m", brand, MARK_BOX) + grad("w", brand, WORD_BOX)
    write("changepay-logo.svg", svg(ALL_BOX, fill_paths("url(#m)", "url(#w)"), "ChangePay", defs=d))
    write("changepay-mark.svg", svg(MARK_BOX, fill_paths("url(#m)", "", word=False), "ChangePay", defs=grad("m", brand, MARK_BOX)))
    write("changepay-wordmark.svg", svg(WORD_BOX, fill_paths("", "url(#w)", mark=False), "ChangePay", defs=grad("w", brand, WORD_BOX)))
    for suffix, col in (("-white", WHITE), ("-mono", "currentColor")):
        write(f"changepay-logo{suffix}.svg", svg(ALL_BOX, fill_paths(col, col), "ChangePay"))
        write(f"changepay-mark{suffix}.svg", svg(MARK_BOX, fill_paths(col, "", word=False), "ChangePay"))
        write(f"changepay-wordmark{suffix}.svg", svg(WORD_BOX, fill_paths("", col, mark=False), "ChangePay"))
    # on dark backgrounds: gradient mark + white wordmark
    write("changepay-logo-on-dark.svg", svg(ALL_BOX, fill_paths("url(#m)", WHITE), "ChangePay", defs=grad("m", ["#7A60C9", "#22BFB9"], MARK_BOX)))
    write("favicon.svg", svg(MARK_BOX, fill_paths("url(#m)", "", word=False), "ChangePay", pad=20, defs=grad("m", brand, MARK_BOX)))

    for key, prod in PRODUCTS.items():
        colors = [ref(c, prod["scale"]) for c in prod["gradient"]]
        d = grad("m", colors, MARK_BOX) + grad("w", colors, WORD_BOX)
        # product logo = the app's existing logo treatment (same artwork, product gradient)
        write(f"product/{key}/logo.svg", svg(ALL_BOX, fill_paths("url(#m)", "url(#w)"), f"ChangePay {prod['name']}", defs=d))
        write(f"product/{key}/mark.svg", svg(MARK_BOX, fill_paths("url(#m)", "", word=False), "ChangePay", defs=grad("m", colors, MARK_BOX)))
        # lockup with descriptor — for web tools / places where colour alone can't tell products apart
        if prod["descriptor"]:
            text_col = P[prod["scale"]]["600"]
            desc, x1 = descriptor(prod["descriptor"], text_col)
            box = (ALL_BOX[0], ALL_BOX[1], x1, ALL_BOX[3])
            write(f"product/{key}/lockup.svg", svg(box, fill_paths("url(#m)", "url(#w)") + desc, f"ChangePay {prod['descriptor']}", defs=d))
            desc_w, _ = descriptor(prod["descriptor"], WHITE)
            write(f"product/{key}/lockup-white.svg", svg(box, fill_paths(WHITE, WHITE) + desc_w, f"ChangePay {prod['descriptor']}"))
        write(f"product/{key}/app-icon.svg", app_icon(colors, filled=False, rounded=False, gid="i"))
        write(f"product/{key}/app-icon-rounded.svg", app_icon(colors, filled=False, rounded=True, gid="i"))
        write(f"product/{key}/app-icon-filled.svg", app_icon(colors, filled=True, rounded=False, gid="i"))
        write(f"product/{key}/app-icon-filled-rounded.svg", app_icon(colors, filled=True, rounded=True, gid="i"))
    print("logos written to", OUT, "| mark box", [round(v) for v in MARK_BOX], "| word box", [round(v) for v in WORD_BOX])


if __name__ == "__main__":
    main()
