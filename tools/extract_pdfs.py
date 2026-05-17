"""
Extract text, tables, and images from every PDF in projects_data/.

Usage:
    python tools/extract_pdfs.py            # walk projects_data/, write text + images
    python tools/extract_pdfs.py --force    # overwrite existing outputs
    python tools/extract_pdfs.py --text-only --force
    python tools/extract_pdfs.py --images-only --force
    python tools/extract_pdfs.py --min-image-bytes 20000

Each PDF foo.pdf produces:
    foo.pdf.txt                         : text + tables (pdfplumber)
    foo_figures/figure1.png             : embedded images in document order (PyMuPDF)
    foo_figures/figure2.png
    ...

Naming: we keep figures in document order so they correspond to "Figure 1", "Figure 2", ...
where the PDF labels its figures sequentially. Tiny embedded images (logos, header
chrome) are filtered out by --min-image-bytes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "projects_data"

DEFAULT_MIN_IMAGE_BYTES = 8000  # filter logo/header chrome (rough heuristic)
DEFAULT_MAX_DIM = 1400          # downscale images whose long edge exceeds this


def format_table(table: list[list[str | None]]) -> str:
    rows = []
    for row in table:
        cells = [(c or "").replace("\n", " ").strip() for c in row]
        rows.append(" | ".join(cells))
    return "\n".join(rows)


def extract_text(pdf_path: Path) -> str:
    out: list[str] = []
    rel = pdf_path.relative_to(ROOT).as_posix()
    out.append(f"=== PDF: {rel} ===")

    with pdfplumber.open(pdf_path) as pdf:
        out.append(f"=== Pages: {len(pdf.pages)} ===\n")
        for i, page in enumerate(pdf.pages, 1):
            out.append(f"--- Page {i} ---")
            text = page.extract_text() or ""
            out.append(text.strip())

            tables = page.extract_tables() or []
            if tables:
                out.append(f"\n--- Page {i} tables ({len(tables)}) ---")
                for t_idx, table in enumerate(tables, 1):
                    out.append(f"[table {t_idx}]")
                    out.append(format_table(table))
            out.append("")

    return "\n".join(out).rstrip() + "\n"


def extract_images(
    pdf_path: Path,
    out_dir: Path,
    min_bytes: int,
    max_dim: int,
) -> tuple[int, int]:
    """Extract embedded images in document order to out_dir/figureN.png.

    Images whose long edge exceeds max_dim are downscaled (preserving aspect ratio)
    so they are web-sized and viewable through size-restricted clients.

    Returns (kept, skipped_small).
    """
    out_dir.mkdir(exist_ok=True)
    doc = fitz.open(pdf_path)
    seen_xrefs: set[int] = set()
    kept = 0
    skipped_small = 0
    figure_idx = 0

    try:
        for page in doc:
            for img in page.get_images(full=True):
                xref = img[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)

                try:
                    pix = fitz.Pixmap(doc, xref)
                    # Normalise CMYK / weird colorspaces to RGB
                    if pix.n - pix.alpha >= 4:
                        pix = fitz.Pixmap(fitz.csRGB, pix)

                    # Downscale if too large. PyMuPDF can shrink via Pixmap.shrink(n)
                    # which halves each dimension n times. Pick the smallest n that
                    # gets long_edge <= max_dim.
                    long_edge = max(pix.width, pix.height)
                    shrink_n = 0
                    while long_edge // (2 ** (shrink_n + 1)) >= max_dim and shrink_n < 4:
                        shrink_n += 1
                    if shrink_n > 0:
                        pix.shrink(shrink_n)

                    data = pix.tobytes("png")
                finally:
                    pix = None  # release

                if len(data) < min_bytes:
                    skipped_small += 1
                    continue

                figure_idx += 1
                out_path = out_dir / f"figure{figure_idx}.png"
                out_path.write_bytes(data)
                kept += 1
    finally:
        doc.close()

    return kept, skipped_small


def figures_dirname(pdf_path: Path) -> str:
    return pdf_path.stem.replace(" ", "_") + "_figures"


def process_pdf(
    pdf_path: Path,
    *,
    do_text: bool,
    do_images: bool,
    force: bool,
    min_image_bytes: int,
    max_dim: int,
) -> dict:
    rel = pdf_path.relative_to(ROOT).as_posix()
    res = {"rel": rel, "text": "skip", "images": "skip", "kept": 0, "small": 0}

    if do_text:
        txt_path = pdf_path.with_suffix(pdf_path.suffix + ".txt")
        if txt_path.exists() and not force:
            res["text"] = "exists"
        else:
            txt_path.write_text(extract_text(pdf_path), encoding="utf-8")
            res["text"] = "wrote"

    if do_images:
        img_dir = pdf_path.parent / figures_dirname(pdf_path)
        if img_dir.exists() and any(img_dir.glob("figure*.png")) and not force:
            res["images"] = "exists"
        else:
            # clear stale figures only when forcing
            if force and img_dir.exists():
                for f in img_dir.glob("figure*.png"):
                    f.unlink()
            kept, small = extract_images(pdf_path, img_dir, min_image_bytes, max_dim)
            res["images"] = "wrote"
            res["kept"] = kept
            res["small"] = small

    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="overwrite existing outputs")
    ap.add_argument("--text-only", action="store_true", help="skip image extraction")
    ap.add_argument("--images-only", action="store_true", help="skip text extraction")
    ap.add_argument(
        "--min-image-bytes",
        type=int,
        default=DEFAULT_MIN_IMAGE_BYTES,
        help=f"filter out images smaller than this (default: {DEFAULT_MIN_IMAGE_BYTES})",
    )
    ap.add_argument(
        "--max-dim",
        type=int,
        default=DEFAULT_MAX_DIM,
        help=f"downscale images whose long edge exceeds this (default: {DEFAULT_MAX_DIM})",
    )
    ap.add_argument(
        "--root",
        type=Path,
        default=DATA_DIR,
        help="directory to walk (default: projects_data/)",
    )
    args = ap.parse_args()

    if args.text_only and args.images_only:
        print("error: --text-only and --images-only are mutually exclusive", file=sys.stderr)
        return 2

    do_text = not args.images_only
    do_images = not args.text_only

    pdfs = sorted(args.root.rglob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found under {args.root}", file=sys.stderr)
        return 1

    print(f"Found {len(pdfs)} PDFs under {args.root.relative_to(ROOT)}")
    failed = 0
    total_kept = 0
    total_small = 0
    for pdf in pdfs:
        try:
            res = process_pdf(
                pdf,
                do_text=do_text,
                do_images=do_images,
                force=args.force,
                min_image_bytes=args.min_image_bytes,
                max_dim=args.max_dim,
            )
            extras = ""
            if res["images"] == "wrote":
                extras = f"  ({res['kept']} kept, {res['small']} skipped < {args.min_image_bytes}B)"
            print(f"  text:{res['text']:<6} images:{res['images']:<6}{extras}  {res['rel']}")
            total_kept += res["kept"]
            total_small += res["small"]
        except Exception as e:
            print(f"  FAIL  {pdf.relative_to(ROOT).as_posix()}: {e}")
            failed += 1

    print(f"\nDone. images: kept={total_kept}, small_skipped={total_small}, failed_pdfs={failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
