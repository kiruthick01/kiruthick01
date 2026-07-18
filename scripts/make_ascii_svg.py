#!/usr/bin/env python3
"""Turn a prepped grayscale photo into an animated ASCII-art SVG.

Downsamples the source image to a ~100x53 character grid, maps each
cell's average brightness onto a density ramp, and writes an SVG where
each row "types" itself in left-to-right via an animated clipPath,
staggered top to bottom. Animation plays once and freezes.

Usage: python make_ascii_svg.py [source.png] [output.svg]
"""
import sys
from pathlib import Path

from PIL import Image

SCRIPTS_DIR = Path(__file__).parent
REPO_ROOT = SCRIPTS_DIR.parent

DEFAULT_INPUT = SCRIPTS_DIR / "source-prepped.png"
DEFAULT_OUTPUT = REPO_ROOT / "avi-ascii.svg"

GRID_W = 100
GRID_H = 53

# Bright -> sparse, dark -> dense.
RAMP = " .`:-=+*cs#%@"

CHAR_W = 6
CHAR_H = 11

BG_COLOR = "#0d1117"
TEXT_COLOR = "#8b98a5"

ROW_STAGGER_S = 0.03
ROW_DUR_S = 0.5


def brightness_to_char(brightness: int) -> str:
    idx = round((255 - brightness) / 255 * (len(RAMP) - 1))
    return RAMP[idx]


def image_to_grid(path: Path) -> list[str]:
    img = Image.open(path).convert("L")
    img = img.resize((GRID_W, GRID_H), Image.LANCZOS)
    pixels = img.load()

    rows = []
    for y in range(GRID_H):
        row_chars = [brightness_to_char(pixels[x, y]) for x in range(GRID_W)]
        rows.append("".join(row_chars))
    return rows


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_svg(rows: list[str]) -> str:
    width = GRID_W * CHAR_W
    height = GRID_H * CHAR_H

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, monospace">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{BG_COLOR}"/>',
    ]

    for i, row in enumerate(rows):
        row_text = escape_xml(row)
        row_y = i * CHAR_H
        text_y = row_y + CHAR_H - 2
        clip_id = f"rowClip{i}"
        begin = round(i * ROW_STAGGER_S, 3)

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(f'<rect x="0" y="{row_y}" width="0" height="{CHAR_H}">')
        parts.append(
            f'<animate attributeName="width" from="0" to="{width}" '
            f'begin="{begin}s" dur="{ROW_DUR_S}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
        )
        parts.append("</rect>")
        parts.append("</clipPath>")

        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(
            f'<text x="0" y="{text_y}" xml:space="preserve" font-size="{CHAR_H}" '
            f'fill="{TEXT_COLOR}" textLength="{width}" lengthAdjust="spacingAndGlyphs">'
            f"{row_text}</text>"
        )
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    if not input_path.exists():
        print(f"Source image not found: {input_path}", file=sys.stderr)
        print("Run prep_photo.py first.", file=sys.stderr)
        sys.exit(1)

    rows = image_to_grid(input_path)
    svg = build_svg(rows)
    output_path.write_text(svg)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
