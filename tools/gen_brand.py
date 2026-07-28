"""Generate Pinterest profile assets: avatar, profile cover, and board covers.

Sizes follow Pinterest's published specs:
  avatar       600x600  (1:1, cropped to a circle — keep the mark centred)
  cover       1600x900  (16:9, min 800x450 — crops on narrow screens, so the
                         type sits inside a central safe zone)
  board cover  600x600  (1:1, cropped to roughly 222x150 landscape on the
                         profile grid — so nothing important near top/bottom)

Palette matches the site (expat-site/styles.css :root).

Run:  python3 tools/gen_brand.py
Then: tools/.venv/bin/python tools/export_pins.py   (rasterises to PNG)
"""
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")

ACCENT_DEEP = "#123a54"
ACCENT = "#1a5276"
ACCENT_BRIGHT = "#2b7fb5"
SAND = "#e8c46a"
PAPER = "#f7f5f1"

SERIF = "Georgia, 'Times New Roman', serif"
UI = "system-ui, -apple-system, 'Segoe UI', sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def gradient_defs(gid="brand"):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{ACCENT_DEEP}"/>'
            f'<stop offset=".55" stop-color="{ACCENT}"/>'
            f'<stop offset="1" stop-color="{ACCENT_BRIGHT}"/></linearGradient>')


def rules(w, h, step=54, op=".07"):
    """Diagonal rule texture, matching the site header."""
    return "".join(
        f'<line x1="{-h + i*step}" y1="{h}" x2="{-h + i*step + h}" y2="0" '
        f'stroke="#ffffff" stroke-opacity="{op}" stroke-width="1.6"/>'
        for i in range(0, int((w + h) / step) + 1)
    )


# ------------------------------------------------------------------ avatar
def avatar():
    """600x600. Circle-cropped by Pinterest, so the mark is centred and the
    corners carry nothing that matters."""
    S = 600
    c = S / 2
    return (
        f'<svg viewBox="0 0 {S} {S}" width="{S}" height="{S}" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>{gradient_defs()}</defs>'
        f'<rect width="{S}" height="{S}" fill="url(#brand)"/>'
        f'{rules(S, S, 46, ".08")}'
        # outer keyline, sits just inside the circular crop
        f'<circle cx="{c}" cy="{c}" r="252" fill="none" stroke="#ffffff" stroke-opacity=".26" stroke-width="4"/>'
        f'<circle cx="{c}" cy="{c}" r="228" fill="none" stroke="{SAND}" stroke-opacity=".55" stroke-width="3"/>'
        # monogram
        f'<text x="{c}" y="{c + 34}" text-anchor="middle" font-family="{SERIF}" '
        f'font-size="196" font-weight="700" fill="#ffffff" letter-spacing="-6">EH</text>'
        # underline mark
        f'<rect x="{c - 66}" y="{c + 74}" width="132" height="7" rx="3.5" fill="{SAND}" fill-opacity=".9"/>'
        f'</svg>'
    )


# ------------------------------------------------------------------ cover
def cover():
    """1600x900. Pinterest crops the sides on narrow viewports, so everything
    that must be read lives within a central ~1100px band."""
    W, H = 1600, 900
    cx = W / 2
    chips = ["Banking", "Healthcare", "Taxes", "Housing", "Identity", "Utilities"]

    # centred chip row
    widths = [30 + len(c) * 15.5 for c in chips]
    total = sum(widths) + 18 * (len(chips) - 1)
    x = cx - total / 2
    chip_svg = ""
    for label, w in zip(chips, widths):
        chip_svg += (f'<rect x="{x:.0f}" y="612" width="{w:.0f}" height="54" rx="27" '
                     f'fill="#ffffff" fill-opacity=".10" stroke="#ffffff" stroke-opacity=".34" stroke-width="2"/>'
                     f'<text x="{x + w/2:.0f}" y="647" text-anchor="middle" font-family="{UI}" '
                     f'font-size="23" fill="#ffffff" fill-opacity=".92">{esc(label)}</text>')
        x += w + 18

    return (
        f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>{gradient_defs()}</defs>'
        f'<rect width="{W}" height="{H}" fill="url(#brand)"/>'
        f'{rules(W, H, 62, ".06")}'
        # decorative rings, off to the sides where cropping is safe
        f'<circle cx="150" cy="760" r="300" fill="none" stroke="#ffffff" stroke-opacity=".08" stroke-width="3"/>'
        f'<circle cx="150" cy="760" r="212" fill="none" stroke="#ffffff" stroke-opacity=".08" stroke-width="3"/>'
        f'<circle cx="1470" cy="150" r="268" fill="none" stroke="#ffffff" stroke-opacity=".08" stroke-width="3"/>'
        f'<circle cx="1470" cy="150" r="186" fill="none" stroke="{SAND}" stroke-opacity=".18" stroke-width="3"/>'
        # eyebrow
        f'<text x="{cx}" y="278" text-anchor="middle" font-family="{UI}" font-size="26" '
        f'font-weight="700" letter-spacing="5" fill="{SAND}" fill-opacity=".95">INDEPENDENT · UPDATED · SOURCED</text>'
        # wordmark
        f'<text x="{cx}" y="404" text-anchor="middle" font-family="{SERIF}" font-size="112" '
        f'font-weight="700" fill="#ffffff" letter-spacing="-2">Expat in Holland</text>'
        f'<rect x="{cx - 90}" y="440" width="180" height="6" rx="3" fill="{SAND}" fill-opacity=".9"/>'
        # tagline
        f'<text x="{cx}" y="516" text-anchor="middle" font-family="{UI}" font-size="34" '
        f'fill="#ffffff" fill-opacity=".88">Practical guides for internationals in the Netherlands</text>'
        f'{chip_svg}'
        f'<text x="{cx}" y="762" text-anchor="middle" font-family="{UI}" font-size="26" '
        f'fill="#ffffff" fill-opacity=".72">hollandexpatguide.com</text>'
        f'</svg>'
    )


# ------------------------------------------------------------------ board covers
def board_cover(title_lines, accent, motif):
    """600x600, but Pinterest crops to a ~222x150 landscape strip from the
    middle — so the type is vertically centred and nothing lives at the edges."""
    S = 600
    cx = S / 2
    y = 268 if len(title_lines) > 1 else 300
    text = ""
    for line in title_lines:
        text += (f'<text x="{cx}" y="{y}" text-anchor="middle" font-family="{SERIF}" '
                 f'font-size="52" font-weight="700" fill="#ffffff">{esc(line)}</text>')
        y += 62
    return (
        f'<svg viewBox="0 0 {S} {S}" width="{S}" height="{S}" xmlns="http://www.w3.org/2000/svg">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{accent[0]}"/><stop offset="1" stop-color="{accent[1]}"/>'
        f'</linearGradient></defs>'
        f'<rect width="{S}" height="{S}" fill="url(#g)"/>'
        f'{rules(S, S, 44, ".07")}'
        f'{motif}'
        f'{text}'
        f'<rect x="{cx - 46}" y="{y + 4}" width="92" height="5" rx="2.5" fill="{SAND}" fill-opacity=".9"/>'
        f'</svg>'
    )


def board_moving():
    motif = ('<circle cx="300" cy="300" r="196" fill="none" stroke="#ffffff" stroke-opacity=".14" stroke-width="3"/>'
             '<circle cx="300" cy="300" r="146" fill="none" stroke="#ffffff" stroke-opacity=".14" stroke-width="3"/>')
    return board_cover(["Moving to the", "Netherlands"], ("#123a54", "#2b7fb5"), motif)


def board_cost():
    motif = "".join(
        f'<rect x="{188 + i*58}" y="{392 - h}" width="38" height="{h}" rx="5" '
        f'fill="#ffffff" fill-opacity="{.16 + i*.09:.2f}"/>'
        for i, h in enumerate([40, 66, 92, 118])
    )
    return board_cover(["Cost of Living", "& Budgeting"], ("#4a235a", "#7d4a94"), motif)


def board_tax():
    motif = ('<circle cx="300" cy="300" r="188" fill="none" stroke="#ffffff" stroke-opacity=".13" stroke-width="3"/>'
             '<text x="300" y="404" text-anchor="middle" font-family="Georgia, serif" font-size="150" '
             'fill="#ffffff" fill-opacity=".12">%</text>')
    return board_cover(["Dutch Taxes", "& Admin"], ("#7d3c1a", "#b5702f"), motif)


ASSETS = {
    "brand-avatar": avatar,
    "brand-cover": cover,
    "board-cover-moving": board_moving,
    "board-cover-cost": board_cost,
    "board-cover-tax": board_tax,
}

if __name__ == "__main__":
    for name, fn in ASSETS.items():
        path = os.path.join(OUT, f"{name}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(fn())
        print(f"  wrote images/{name}.svg")
    print("done")
