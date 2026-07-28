"""Rasterise the Pinterest infographics from SVG to PNG.

Pinterest does not accept SVG uploads, so the create-pin flow needs a raster
file. The site itself keeps serving the SVGs (crisp and a fraction of the
size); these PNGs exist purely to be uploaded to Pinterest.

Pipeline: svglib parses the SVG -> reportlab writes a vector PDF -> macOS
`sips` rasterises the PDF at the exact pixel width. No system Cairo needed,
which is why this works where cairosvg and rlPyCairo do not.

Two compatibility steps matter, and skipping them produced files Pinterest
rejected as broken. sips tags its output Display P3 and writes a `cICP`
chunk, which is a recent addition to the PNG spec that stricter decoders
refuse. So the output is converted to sRGB and then reduced to the baseline
chunks (IHDR/PLTE/IDAT/tRNS/IEND) that every decoder understands.

Run with the tooling venv:
    tools/.venv/bin/python tools/export_pins.py

Covers the pins plus the profile assets (avatar, cover, board covers);
see ASSETS for the target width of each.

Output: images/png/<name>.png
"""
import os
import struct
import subprocess
import sys
import tempfile

SRGB_PROFILE = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"

# Chunks every PNG decoder is required to understand. Everything else —
# colour profiles, EXIF, XMP — is dropped for maximum uploader compatibility.
BASELINE_CHUNKS = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS"}


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "images")
OUT = os.path.join(SRC, "png")


def strip_to_baseline(path):
    """Rewrite a PNG keeping only the chunks required by the spec."""
    raw = open(path, "rb").read()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    out = bytearray(raw[:8])
    i, dropped = 8, []
    while i < len(raw):
        length = struct.unpack(">I", raw[i:i + 4])[0]
        ctype = raw[i + 4:i + 8]
        if ctype in BASELINE_CHUNKS:
            out += raw[i:i + 12 + length]
        else:
            dropped.append(ctype.decode("latin1"))
        i += 12 + length
    open(path, "wb").write(bytes(out))
    return dropped


# (source svg name, output pixel width) — heights follow the SVG's own ratio
ASSETS = [
    # pins: Pinterest's preferred 2:3 -> 1000x1500
    ("pin-first-weeks-netherlands", 1000),
    ("pin-cost-of-living-netherlands", 1000),
    ("pin-30-percent-ruling-2026", 1000),
    ("pin-health-insurance-netherlands", 1000),
    ("pin-box-3-wealth-tax", 1000),
    ("pin-best-dutch-cities", 1000),
    # profile assets
    ("brand-avatar", 600),        # 1:1, cropped to a circle
    ("brand-cover", 1600),        # 16:9 profile cover
    ("board-cover-moving", 600),  # 1:1, cropped to ~222x150 on the grid
    ("board-cover-cost", 600),
    ("board-cover-tax", 600),
]


def export(name, target_w):
    svg_path = os.path.join(SRC, f"{name}.svg")
    if not os.path.exists(svg_path):
        return f"  MISSING {name}.svg"

    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF

    drawing = svg2rlg(svg_path)
    if drawing is None:
        return f"  FAILED to parse {name}.svg"

    scale = target_w / drawing.width
    drawing.width, drawing.height = target_w, drawing.height * scale
    drawing.scale(scale, scale)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name
    try:
        renderPDF.drawToFile(drawing, pdf_path)
        png_path = os.path.join(OUT, f"{name}.png")
        subprocess.run(
            ["sips", "-s", "format", "png", "--resampleWidth", str(target_w),
             pdf_path, "--out", png_path],
            check=True, capture_output=True,
        )
        # normalise colour, then reduce to baseline chunks
        if os.path.exists(SRGB_PROFILE):
            subprocess.run(["sips", "-m", SRGB_PROFILE, png_path, "--out", png_path],
                           check=True, capture_output=True)
        strip_to_baseline(png_path)
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
    for name, width in ASSETS:
        print(export(name, width))
    print("done")
