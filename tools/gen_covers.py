"""Generate wide SVG cover art for guides that have no unique photograph.

Five guides previously fell back to a shared category photo, so different
articles showed the same picture. These covers are deliberately illustrative
rather than photographic, drawn from the site's own palette, so a reader can
tell two guides apart at a glance.

The canvas is 1400x420 — a very wide 3.3:1 band — so every composition is
laid out horizontally and sized to fill the frame rather than clustering.

Output: images/hero-<article-id>.svg — build.py picks these up automatically
(priority 3 in assign_images), below a real photo but above the category pool.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
W, H = 1400, 420
CY = H / 2

INK = "#0b1f2b"


def frame(bg_from, bg_to, scene, tint="#ffffff"):
    """Gradient field + diagonal rule texture + the motif, with only a light
    bottom scrim — just enough for the category chip to read."""
    texture = "".join(
        f'<line x1="{-H + i*58}" y1="{H}" x2="{-H + i*58 + H}" y2="0" '
        f'stroke="{tint}" stroke-opacity=".07" stroke-width="1.5"/>'
        for i in range(0, int((W + H) / 58) + 1)
    )
    return (
        f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg" role="img">'
        f'<defs>'
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{bg_from}"/><stop offset="1" stop-color="{bg_to}"/></linearGradient>'
        f'<linearGradient id="scrim" x1="0" y1="1" x2="0" y2="0">'
        f'<stop offset="0" stop-color="{INK}" stop-opacity=".34"/>'
        f'<stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient>'
        f'</defs>'
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>{texture}{scene}'
        f'<rect y="{H*0.55}" width="{W}" height="{H*0.45}" fill="url(#scrim)"/>'
        f'</svg>'
    )


def rings(cx, cy, radii, colour="#ffffff", op=".13", width=2):
    return "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{colour}" '
        f'stroke-opacity="{op}" stroke-width="{width}"/>' for r in radii
    )


# ---------------------------------------------------------------- covers
def cover_checklist():
    """Five steps left to right — the arrival sequence, on a connecting spine."""
    s = rings(1210, 120, [250, 186, 124])
    s += f'<line x1="150" y1="{CY}" x2="1250" y2="{CY}" stroke="#ffffff" stroke-opacity=".26" stroke-width="4"/>'
    for i in range(5):
        cx = 190 + i * 255
        s += (f'<circle cx="{cx}" cy="{CY}" r="46" fill="#12405a" stroke="#ffffff" '
              f'stroke-opacity=".85" stroke-width="5"/>')
        s += (f'<path d="M {cx-19} {CY+2} L {cx-5} {CY+17} L {cx+21} {CY-16}" fill="none" '
              f'stroke="#ffd98a" stroke-opacity=".95" stroke-width="7" '
              f'stroke-linecap="round" stroke-linejoin="round"/>')
        s += (f'<rect x="{cx-58}" y="{CY+74}" width="116" height="11" rx="5.5" '
              f'fill="#ffffff" fill-opacity="{.34 - i*.045:.2f}"/>')
    return frame("#0f3d55", "#1d6d93", s)


def cover_citizenship():
    """A passport stamp, and years accumulating toward it."""
    s = rings(360, CY, [292, 224, 158], "#ffffff", ".12")
    s += (f'<circle cx="360" cy="{CY}" r="112" fill="rgba(255,255,255,.09)" stroke="#ffffff" '
          f'stroke-opacity=".85" stroke-width="7"/>')
    # stamp serration
    import math
    for k in range(24):
        a = k * (math.pi * 2 / 24)
        x1, y1 = 360 + math.cos(a) * 122, CY + math.sin(a) * 122
        x2, y2 = 360 + math.cos(a) * 138, CY + math.sin(a) * 138
        s += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#ffffff" stroke-opacity=".42" stroke-width="4"/>'
    s += (f'<path d="M 314 {CY} L 346 {CY+34} L 408 {CY-32}" fill="none" stroke="#ffd98a" '
          f'stroke-opacity=".95" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
    for i, h in enumerate([70, 116, 162, 208, 254]):
        s += (f'<rect x="{680 + i*116}" y="{H-62-h}" width="72" height="{h}" rx="8" '
              f'fill="#ffffff" fill-opacity="{.16 + i*.13:.2f}"/>')
    return frame("#0e3f4d", "#18728a", s)


def cover_parental():
    """Two overlapping rings and a third between them — leave shared."""
    s = rings(1140, 140, [230, 168, 108], "#ffffff", ".11")
    s += (f'<circle cx="560" cy="{CY-18}" r="128" fill="rgba(255,255,255,.07)" stroke="#ffffff" '
          f'stroke-opacity=".82" stroke-width="8"/>')
    s += (f'<circle cx="760" cy="{CY-18}" r="128" fill="rgba(255,255,255,.07)" stroke="#bfe6cf" '
          f'stroke-opacity=".88" stroke-width="8"/>')
    s += (f'<circle cx="660" cy="{CY+96}" r="60" fill="rgba(255,217,138,.14)" stroke="#ffd98a" '
          f'stroke-opacity=".92" stroke-width="7"/>')
    return frame("#134c37", "#23855c", s)


def cover_sick():
    """A pulse that flattens, then recovers — the two-year arc."""
    heights = [0, 0, -26, 58, -104, 44, -8, 0, 0, 0, 0, 0, 0, -20, 34, -52, 22, 0, 0]
    x = 40
    d = f"M {x} {CY}"
    for h in heights:
        x += 70
        d += f" L {x} {CY + h}"
    s = rings(1180, 300, [232, 168, 106], "#ffffff", ".11")
    s += f'<line x1="40" y1="{CY}" x2="1360" y2="{CY}" stroke="#ffffff" stroke-opacity=".16" stroke-width="2"/>'
    s += (f'<path d="{d}" fill="none" stroke="#ffffff" stroke-opacity=".92" stroke-width="7" '
          f'stroke-linejoin="round" stroke-linecap="round"/>')
    s += f'<circle cx="390" cy="{CY-104}" r="15" fill="#ffd98a"/>'
    return frame("#123f52", "#1f7593", s)


def cover_aov():
    """A shield with a break in its outline — cover you do not automatically have."""
    s = rings(1130, CY, [252, 186, 122], "#ffe9c4", ".13")
    s += ('<path d="M 430 74 L 592 136 L 592 262 Q 592 350 430 400 Q 268 350 268 262 L 268 136 Z" '
          'fill="rgba(255,255,255,.09)" stroke="#ffffff" stroke-opacity=".85" stroke-width="9" '
          'stroke-dasharray="286 74" stroke-linejoin="round"/>')
    s += ('<path d="M 366 244 L 410 292 L 500 190" fill="none" stroke="#ffd98a" stroke-opacity=".95" '
          'stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>')
    for i, h in enumerate([54, 96, 138]):
        s += (f'<rect x="{760 + i*104}" y="{H-96-h}" width="62" height="{h}" rx="7" '
              f'fill="#ffe9c4" fill-opacity="{.18 + i*.14:.2f}"/>')
    return frame("#5c3510", "#a06a22", s, tint="#ffe9c4")


COVERS = {
    "moving-to-netherlands-checklist": cover_checklist,
    "dutch-citizenship-naturalisation-2026": cover_citizenship,
    "parental-leave-netherlands-expats-guide": cover_parental,
    "sick-leave-netherlands-expat-rights": cover_sick,
    "aov-disability-insurance-self-employed-netherlands": cover_aov,
}

if __name__ == "__main__":
    for aid, fn in COVERS.items():
        with open(os.path.join(OUT, f"hero-{aid}.svg"), "w", encoding="utf-8") as f:
            f.write(fn())
        print(f"  wrote images/hero-{aid}.svg")
    print("done")
