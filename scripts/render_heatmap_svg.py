#!/usr/bin/env python3
"""Render data/contributions.json as a classic GitHub-style contribution
heatmap SVG: 53 weeks x 7 days of rounded boxes, colored by level.

Boxes animate in with a diagonal slide-down, staggered by column then
row, and freeze in place after (no looping glow). Includes a Less->More
legend and a "N contributions in the last year" footer.

Usage: python render_heatmap_svg.py [contributions.json] [output.svg]
"""
import json
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_INPUT = REPO_ROOT / "data" / "contributions.json"
DEFAULT_OUTPUT = REPO_ROOT / "contrib-heatmap.svg"

WIDTH = 860

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

BG_COLOR = "#0d1117"
TEXT_COLOR = "#8b98a5"
DIM_TEXT_COLOR = "#484f58"

LEFT_MARGIN = 34
RIGHT_MARGIN = 20
TOP_MARGIN = 22
LEGEND_H = 24
FOOTER_H = 26
BOTTOM_PAD = 14

WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}  # Sunday=0 offset

COL_STAGGER_S = 0.018
ROW_STAGGER_S = 0.012
BOX_DUR_S = 0.35

MONTH_ABBR = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_data(path: Path) -> dict:
    return json.loads(path.read_text())


def build_grid(days: list[dict]) -> tuple[dict, int]:
    """Map (col, row) -> day dict. Row 0 = Sunday. Returns grid + num_cols."""
    if not days:
        return {}, 53

    parsed = [(datetime.strptime(d["date"], "%Y-%m-%d").date(), d) for d in days]
    parsed.sort(key=lambda p: p[0])
    start = parsed[0][0]

    grid = {}
    max_col = 0
    for d, day in parsed:
        row = (d.weekday() + 1) % 7  # Monday=0 -> shift so Sunday=0
        col = (d - start).days // 7
        grid[(col, row)] = day
        max_col = max(max_col, col)

    return grid, max_col + 1


def build_svg(data: dict) -> str:
    days = data["days"]
    stats = data["stats"]
    grid, num_cols = build_grid(days)

    available = WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    cell = available / num_cols
    box = cell * 0.78
    radius = box * 0.2

    grid_height = cell * 7
    height = round(TOP_MARGIN + grid_height + LEGEND_H + FOOTER_H + BOTTOM_PAD, 1)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, monospace">',
        f'<rect x="0" y="0" width="{WIDTH}" height="{height}" fill="{BG_COLOR}"/>',
    ]

    # Weekday row labels.
    for row, label in WEEKDAY_LABELS.items():
        ly = TOP_MARGIN + row * cell + box * 0.85
        parts.append(
            f'<text x="0" y="{ly:.1f}" font-size="9" fill="{TEXT_COLOR}">{label}</text>'
        )

    # Month labels: mark the column where a new month's first week begins.
    last_month = None
    parsed_sorted = sorted(
        ((datetime.strptime(d["date"], "%Y-%m-%d").date(), d) for d in days),
        key=lambda p: p[0],
    )
    start_date = parsed_sorted[0][0] if parsed_sorted else date.today()
    for d, _ in parsed_sorted:
        col = (d - start_date).days // 7
        if d.month != last_month:
            last_month = d.month
            lx = LEFT_MARGIN + col * cell
            parts.append(
                f'<text x="{lx:.1f}" y="{TOP_MARGIN - 8}" font-size="9" '
                f'fill="{TEXT_COLOR}">{MONTH_ABBR[d.month - 1]}</text>'
            )

    # Day boxes.
    for (col, row), day in grid.items():
        x = LEFT_MARGIN + col * cell
        y = TOP_MARGIN + row * cell
        color = PALETTE[min(day["level"], len(PALETTE) - 1)]
        begin = round(col * COL_STAGGER_S + row * ROW_STAGGER_S, 3)
        title = f'{day["count"]} contributions on {day["date"]}'

        parts.append(f'<g opacity="0" transform="translate(-6,-6)">')
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{box:.1f}" height="{box:.1f}" '
            f'rx="{radius:.1f}" fill="{color}"><title>{escape_xml(title)}</title></rect>'
        )
        parts.append(
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{begin}s" dur="{BOX_DUR_S}s" fill="freeze"/>'
        )
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="-6 -6" to="0 0" begin="{begin}s" dur="{BOX_DUR_S}s" '
            f'fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
        )
        parts.append("</g>")

    # Legend: Less [boxes] More
    legend_y = TOP_MARGIN + grid_height + 18
    legend_x = WIDTH - RIGHT_MARGIN - (len(PALETTE) * (box + 3)) - 70
    parts.append(
        f'<text x="{legend_x:.1f}" y="{legend_y:.1f}" font-size="10" '
        f'fill="{TEXT_COLOR}">Less</text>'
    )
    for i, color in enumerate(PALETTE):
        sx = legend_x + 32 + i * (box + 3)
        parts.append(
            f'<rect x="{sx:.1f}" y="{legend_y - box + 2:.1f}" width="{box:.1f}" '
            f'height="{box:.1f}" rx="{radius:.1f}" fill="{color}"/>'
        )
    more_x = legend_x + 32 + len(PALETTE) * (box + 3) + 4
    parts.append(
        f'<text x="{more_x:.1f}" y="{legend_y:.1f}" font-size="10" '
        f'fill="{TEXT_COLOR}">More</text>'
    )

    # Footer stats.
    footer_y = legend_y + FOOTER_H
    total = stats.get("total_contributions", 0)
    parts.append(
        f'<text x="{LEFT_MARGIN}" y="{footer_y:.1f}" font-size="12" '
        f'fill="{DIM_TEXT_COLOR}">{total} contributions in the last year</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    if not input_path.exists():
        print(f"Data file not found: {input_path}", file=sys.stderr)
        print("Run fetch_contributions.py first.", file=sys.stderr)
        sys.exit(1)

    data = load_data(input_path)
    svg = build_svg(data)
    output_path.write_text(svg)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
