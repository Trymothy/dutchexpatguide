"""Rasterise the Pinterest infographics from SVG to PNG.

Pinterest does not accept SVG uploads, so the create-pin flow needs a raster
file. The site itself keeps serving the SVGs (crisp and a fraction of the
size); these PNGs exist purely to be uploaded to Pinterest.

Pipeline: svglib parses the SVG -> reportlab writes a vector PDF -> macOS
`sips` rasterises the PDF at the exact pixel width. No system Cairo needed,
which is why this works where cairosvg and rlPyCairo do not.

Run with the tooling venv:
    tools/.venv/bin/python tools/export_pins.py

Output: images/png/<name>.png at 1000x1500 (Pinterest's preferred 2:3).
"""
import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "images")
OUT = os.path.join(SRC, "png")

TARGET_W = 1000  # Pinterest recommends 1000x1500

PINS = [
    "pin-first-weeks-netherlands",
    "pin-cost-of-living-netherlands",
    "pin-30-percent-ruling-2026",
    "pin-health-insurance-netherlands",
    "pin-box-3-wealth-tax",
    "pin-best-dutch-cities",
]


def export(name):
    svg_path = os.path.join(SRC, f"{name}.svg")
    if not os.path.exists(svg_path):
        return f"  MISSING {name}.svg"

    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF

    drawing = svg2rlg(svg_path)
    if drawing is None:
        return f"  FAILED to parse {name}.svg"

    scale = TARGET_W / drawing.width
    drawing.width, drawing.height = TARGET_W, drawing.height * scale
    drawing.scale(scale, scale)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name
    try:
        renderPDF.drawToFile(drawing, pdf_path)
        png_path = os.path.join(OUT, f"{name}.png")
        subprocess.run(
            ["sips", "-s", "format", "png", "--resampleWidth", str(TARGET_W),
             pdf_path, "--out", png_path],
            check=True, capture_output=True,
        )
    finally:
        os.unlink(pdf_path)

    size_kb = os.path.getsize(png_path) / 1024
    dims = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", png_path],
        capture_output=True, text=True,
    ).stdout
    w = h = "?"
    for line in dims.splitlines():
        if "pixelWidth" in line:
            w = line.split(":")[1].strip()
        if "pixelHeight" in line:
            h = line.split(":")[1].strip()
    return f"  {name}.png  {w}x{h}  {size_kb:.0f} KB"


if __name__ == "__main__":
    if sys.platform != "darwin":
        sys.exit("This exporter relies on macOS `sips`.")
    os.makedirs(OUT, exist_ok=True)
    for pin in PINS:
        print(export(pin))
    print("done")
