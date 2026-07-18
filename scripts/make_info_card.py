#!/usr/bin/env python3
"""Hand-authored neofetch-style info card SVG.

Renders a fixed set of key/value rows in a dark terminal-style panel.
Rows fade + slide in, staggered, then freeze (no looping).

Set STATIC=1 to emit a frozen frame (all rows already visible, no
<animate> elements) for quick local preview without waiting on SMIL.

Usage: python make_info_card.py [output.svg]
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "info-card.svg"

WIDTH = 490
KEY_CHAR_W = 9.0
VALUE_CHAR_W = 8.4

BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"
TITLE_COLOR = "#58a6ff"
KEY_COLOR = "#7ee787"
VALUE_COLOR = "#c9d1d9"
DIM_COLOR = "#484f58"

ROWS = [
    ("Now", "CS @ Chennai Institute of Technology"),
    ("Prev", "Full Stack Dev Intern @ ATPAR UI Technology"),
    ("Stack", "Python · Next.js · Solidity · FastAPI"),
    ("Highlights", "Marine Ecosystem Monitoring System"),
]

DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]
SWATCH_COLORS = [
    "#0d1117", "#f85149", "#3fb950", "#d29922",
    "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9",
]

TITLE = "kiruthick01@github"
PAD_X = 28
TITLE_BAR_H = 40
HEADER_H = 34
ROW_H = 32
SWATCH_ROW_H = 40
PAD_BOTTOM = 24

ROW_STAGGER_S = 0.25
ROW_DUR_S = 0.4


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_svg(static: bool) -> str:
    key_col_w = max(len(k) for k, _ in ROWS) * KEY_CHAR_W + 12
    max_value_w = max(len(v) for _, v in ROWS) * VALUE_CHAR_W
    width = max(WIDTH, round(PAD_X * 2 + key_col_w + max_value_w) + 10)

    height = (
        TITLE_BAR_H
        + HEADER_H
        + ROW_H * len(ROWS)
        + SWATCH_ROW_H
        + PAD_BOTTOM
    )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, monospace">',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" '
        f'fill="{BG_COLOR}" stroke="{BORDER_COLOR}"/>',
    ]

    # Terminal title bar with traffic-light dots.
    for i, color in enumerate(DOT_COLORS):
        cx = PAD_X + i * 18
        parts.append(f'<circle cx="{cx}" cy="{TITLE_BAR_H / 2}" r="6" fill="{color}"/>')
    parts.append(
        f'<line x1="0" y1="{TITLE_BAR_H}" x2="{width}" y2="{TITLE_BAR_H}" '
        f'stroke="{BORDER_COLOR}"/>'
    )

    y = TITLE_BAR_H + HEADER_H
    parts.append(
        f'<text x="{PAD_X}" y="{TITLE_BAR_H + 24}" font-size="16" font-weight="bold" '
        f'fill="{TITLE_COLOR}">{escape_xml(TITLE)}</text>'
    )
    parts.append(
        f'<line x1="{PAD_X}" y1="{y - 6}" x2="{width - PAD_X}" y2="{y - 6}" '
        f'stroke="{DIM_COLOR}"/>'
    )

    for i, (key, value) in enumerate(ROWS):
        row_y = y + i * ROW_H + 22
        key_x = PAD_X
        value_x = PAD_X + key_col_w

        text_content = (
            f'<text x="{key_x}" y="{row_y}" font-size="14" font-weight="bold" '
            f'fill="{KEY_COLOR}">{escape_xml(key)}:</text>'
            f'<text x="{value_x}" y="{row_y}" font-size="14" '
            f'fill="{VALUE_COLOR}">{escape_xml(value)}</text>'
        )

        if static:
            parts.append(f'<g>{text_content}</g>')
        else:
            begin = round(i * ROW_STAGGER_S, 3)
            parts.append(f'<g opacity="0" transform="translate(-16,0)">')
            parts.append(text_content)
            parts.append(
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin}s" dur="{ROW_DUR_S}s" fill="freeze"/>'
            )
            parts.append(
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-16 0" to="0 0" begin="{begin}s" dur="{ROW_DUR_S}s" '
                f'fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            )
            parts.append("</g>")

    swatch_y = y + ROW_H * len(ROWS) + 20
    swatch_size = 16
    swatch_gap = 6
    for i, color in enumerate(SWATCH_COLORS):
        sx = PAD_X + i * (swatch_size + swatch_gap)
        parts.append(
            f'<rect x="{sx}" y="{swatch_y}" width="{swatch_size}" height="{swatch_size}" '
            f'rx="3" fill="{color}" stroke="{BORDER_COLOR}" stroke-width="0.5"/>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    static = os.environ.get("STATIC") == "1"

    svg = build_svg(static)
    output_path.write_text(svg)
    print(f"Wrote {output_path}" + (" (static frame)" if static else ""))


if __name__ == "__main__":
    main()
