"""
Downscale extracted PDF figures into small previews the Claude API can ingest.

The PDF-figure extractor caps the long edge at 1400px, but some images that were
already small are still emitted at their original dimensions (e.g. 2528 wide).
The Claude API rejects images whose long edge exceeds 2000px when batched.
This script reads every figureN.png under a folder and writes a sibling
figureN.preview.png with the long edge clamped to MAX_EDGE.

Usage:
    python tools/make_previews.py projects_data/2025-improved-freq-dobbler/designnotat_4_figures
    python tools/make_previews.py projects_data --recursive
    python tools/make_previews.py projects_data --recursive --force
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

MAX_EDGE = 1400


def process_image(src: Path, force: bool) -> str:
    out = src.with_suffix(".preview.png")
    if out.exists() and not force:
        return "skip"

    with Image.open(src) as im:
        long_edge = max(im.size)
        if long_edge <= MAX_EDGE:
            scale = 1.0
        else:
            scale = MAX_EDGE / long_edge
        new_size = (max(1, int(im.width * scale)), max(1, int(im.height * scale)))
        preview = im.convert("RGB").resize(new_size, Image.LANCZOS)
        preview.save(out, format="PNG", optimize=True)
    return "wrote"


def iter_figures(root: Path, recursive: bool):
    pattern = "**/figure*.png" if recursive else "figure*.png"
    for p in sorted(root.glob(pattern)):
        # never re-process preview outputs
        if p.name.endswith(".preview.png") or ".preview" in p.suffixes:
            continue
        yield p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", type=Path, help="figure dir, or a parent if --recursive")
    ap.add_argument("-r", "--recursive", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite existing previews")
    args = ap.parse_args()

    if not args.path.exists():
        print(f"error: {args.path} does not exist", file=sys.stderr)
        return 2

    figures = list(iter_figures(args.path, args.recursive))
    if not figures:
        print(f"no figures found under {args.path}", file=sys.stderr)
        return 1

    wrote = 0
    skipped = 0
    for fig in figures:
        try:
            status = process_image(fig, args.force)
        except Exception as e:
            print(f"  FAIL {fig}: {e}")
            continue
        if status == "wrote":
            wrote += 1
        else:
            skipped += 1
        print(f"  {status:<5}  {fig.relative_to(args.path) if args.recursive else fig.name}")

    print(f"\nDone. wrote={wrote}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
