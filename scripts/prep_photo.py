#!/usr/bin/env python3
"""Prep a source photo for ASCII-art conversion.

Usage: python prep_photo.py <path-to-photo>

Removes the background (rembg), composites the cutout onto a white
background, boosts local contrast with CLAHE, and writes a grayscale
PNG to scripts/source-prepped.png for make_ascii_svg.py to consume.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUTPUT_PATH = Path(__file__).parent / "source-prepped.png"


def prep_photo(input_path: str) -> Path:
    src = Image.open(input_path).convert("RGBA")

    cutout = remove(src)

    white_bg = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, cutout).convert("RGB")

    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)

    Image.fromarray(contrasted).save(OUTPUT_PATH)
    return OUTPUT_PATH


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python prep_photo.py <path-to-photo>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    if not Path(input_path).exists():
        print(f"File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    out = prep_photo(input_path)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
