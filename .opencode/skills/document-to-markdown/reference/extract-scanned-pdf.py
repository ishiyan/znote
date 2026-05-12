"""
Scanned PDF extraction pipeline.

Handles single-paged and double-paged (two real pages per PDF page) scanned PDFs.
Pipeline: render to PNG → split doubles → OCR → analyze borders → crop figures.

Dependencies: Pillow, tesseract (system), pdftoppm (poppler-utils)
"""

import os
import subprocess
from pathlib import Path
from PIL import Image
import numpy as np


# ---------------------------------------------------------------------------
# Step 1: Render PDF pages to PNGs
# ---------------------------------------------------------------------------

def render_pdf_to_pngs(pdf_path, output_dir, dpi=300):
    """Render each PDF page to a PNG using pdftoppm.

    Args:
        pdf_path: Path to the PDF file.
        output_dir: Directory for output PNGs.
        dpi: Resolution (300 recommended for OCR).

    Returns:
        List of output PNG paths, sorted.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = str(output_dir / "page")
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), str(pdf_path), prefix],
        check=True,
    )
    return sorted(output_dir.glob("page-*.png"))


# ---------------------------------------------------------------------------
# Step 2: Split double-paged scans
# ---------------------------------------------------------------------------

def is_double_paged(image_path):
    """Heuristic: image is double-paged if width > height (landscape)."""
    with Image.open(image_path) as img:
        return img.width > img.height


def split_double_pages(image_paths, output_dir, prefix="ch1"):
    """Split landscape (double-paged) scans into left/right halves.

    Args:
        image_paths: List of source PNG paths (from render_pdf_to_pngs).
        output_dir: Directory for output half-page PNGs.
        prefix: Naming prefix, e.g., "ch1" → ch1-p01.png, ch1-p02.png, ...

    Returns:
        List of output half-page PNG paths, sorted.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    page_num = 1
    outputs = []

    for src in image_paths:
        img = Image.open(src)
        w, h = img.size

        if w > h:
            # Double-paged: split into left and right
            mid = w // 2
            left = img.crop((0, 0, mid, h))
            right = img.crop((mid, 0, w, h))

            left_path = output_dir / f"{prefix}-p{page_num:02d}.png"
            right_path = output_dir / f"{prefix}-p{page_num + 1:02d}.png"
            left.save(str(left_path))
            right.save(str(right_path))
            outputs.extend([left_path, right_path])
            page_num += 2
        else:
            # Single-paged: copy as-is
            out_path = output_dir / f"{prefix}-p{page_num:02d}.png"
            img.save(str(out_path))
            outputs.append(out_path)
            page_num += 1

        img.close()

    return outputs


# ---------------------------------------------------------------------------
# Step 3: OCR
# ---------------------------------------------------------------------------

def ocr_page(image_path, psm=6):
    """Run tesseract OCR on a single page image.

    Args:
        image_path: Path to the page PNG.
        psm: Page segmentation mode (6 = uniform block of text).

    Returns:
        OCR text as a string.
    """
    result = subprocess.run(
        ["tesseract", str(image_path), "stdout", "--psm", str(psm)],
        capture_output=True, text=True, check=True,
    )
    return result.stdout


def ocr_all_pages(image_paths, output_dir, psm=6):
    """OCR all page images and save text files.

    Args:
        image_paths: List of page PNG paths.
        output_dir: Directory for output .txt files.
        psm: Tesseract page segmentation mode.

    Returns:
        List of output text file paths.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []

    for img_path in image_paths:
        txt_path = output_dir / (Path(img_path).stem + ".txt")
        text = ocr_page(img_path, psm)
        txt_path.write_text(text)
        outputs.append(txt_path)
        print(f"OCR: {img_path.name} → {txt_path.name} ({len(text)} chars)")

    return outputs


# ---------------------------------------------------------------------------
# Step 5: Analyze borders for figure detection
# ---------------------------------------------------------------------------

def analyze_borders(image_path, dark_threshold=128):
    """Analyze dark pixel distribution per row to find chart borders and captions.

    Prints a summary of rows with notable dark pixel counts, grouped into:
    - BORDER rows (800+ dark pixels) — chart box edges
    - TEXT rows (200-600 dark pixels) — body text or captions
    - GAP rows (<50 dark pixels) — whitespace

    Args:
        image_path: Path to a half-page PNG.
        dark_threshold: Pixel brightness below which a pixel is "dark" (default 128).

    Returns:
        List of (y, dark_count) tuples for all rows.
    """
    img = Image.open(image_path).convert("L")
    pixels = np.array(img)
    h, w = pixels.shape

    row_counts = []
    for y in range(h):
        dark = int(np.sum(pixels[y, :] < dark_threshold))
        row_counts.append((y, dark))

    # Print summary: group consecutive rows with similar counts
    print(f"\n=== {Path(image_path).name} ({w}x{h}) ===")
    print(f"{'Y':>6} {'Dark px':>8}  Category")
    print("-" * 35)

    for y, count in row_counts:
        if count > 800:
            cat = "BORDER"
        elif count > 200:
            cat = "text"
        elif count > 50:
            cat = "sparse"
        else:
            continue  # skip blank rows for brevity
        # Only print transitions and notable rows
        print(f"{y:>6} {count:>8}  {cat}")

    return row_counts


def find_border_bands(row_counts, threshold=800, min_gap=5):
    """Group consecutive high-dark-pixel rows into border bands.

    Args:
        row_counts: List of (y, dark_count) from analyze_borders().
        threshold: Minimum dark pixels to qualify as a border row.
        min_gap: Maximum gap between rows to still be in the same band.

    Returns:
        List of (band_start_y, band_end_y) tuples.
    """
    border_rows = [y for y, count in row_counts if count >= threshold]
    if not border_rows:
        return []

    bands = []
    band_start = border_rows[0]
    prev = border_rows[0]

    for y in border_rows[1:]:
        if y - prev > min_gap:
            bands.append((band_start, prev))
            band_start = y
        prev = y
    bands.append((band_start, prev))

    return bands


# ---------------------------------------------------------------------------
# Step 5: Crop figures
# ---------------------------------------------------------------------------

def crop_figures(figure_specs, base_dir, output_dir):
    """Crop figures from page images using pre-determined coordinates.

    Args:
        figure_specs: List of tuples:
            (source_filename, output_filename, left, top, right, bottom)
            Coordinates are in pixels relative to the source image.
        base_dir: Directory containing the source page images.
        output_dir: Directory for cropped figure PNGs.

    Returns:
        List of output file paths.

    Example:
        specs = [
            ("ch1-p04.png", "fig1-1.png", 150, 275, 1600, 775),
            ("ch1-p05.png", "fig1-2.png", 150, 270, 1600, 1180),
        ]
        crop_figures(specs, "images/", "images/figures/")
    """
    base_dir = Path(base_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []

    for src_name, dst_name, left, top, right, bottom in figure_specs:
        src_path = base_dir / src_name
        img = Image.open(src_path)
        w, h = img.size

        # Clamp bounds to image dimensions
        right = min(right, w)
        bottom = min(bottom, h)

        cropped = img.crop((left, top, right, bottom))
        dst_path = output_dir / dst_name
        cropped.save(str(dst_path))
        outputs.append(dst_path)
        print(f"{dst_name}: crop=({left},{top},{right},{bottom}) -> {cropped.size}")

    print(f"\nDone! {len(outputs)} figures cropped.")
    return outputs


# ---------------------------------------------------------------------------
# Full pipeline orchestrator
# ---------------------------------------------------------------------------

def pipeline(pdf_path, output_dir, chapter_prefix="ch1", double_paged=True):
    """Run the full scanned PDF extraction pipeline.

    This orchestrates steps 1-3. Steps 4-6 (markdown composition, figure
    coordinate selection, and markdown reference updates) require human
    judgment and are done manually.

    Args:
        pdf_path: Path to the scanned PDF.
        output_dir: Base output directory.
        chapter_prefix: Prefix for page image naming (e.g., "ch1").
        double_paged: Whether the PDF has two real pages per PDF page.

    Returns:
        Dict with paths to intermediate outputs.
    """
    output_dir = Path(output_dir)
    raw_dir = output_dir / "raw_pages"
    images_dir = output_dir / "images"
    ocr_dir = output_dir / "ocr"

    # Step 1: Render
    print("Step 1: Rendering PDF pages to PNGs...")
    raw_pngs = render_pdf_to_pngs(pdf_path, raw_dir)
    print(f"  Rendered {len(raw_pngs)} PDF pages")

    # Step 2: Split (if double-paged)
    if double_paged:
        print("Step 2: Splitting double-paged scans...")
        page_pngs = split_double_pages(raw_pngs, images_dir, chapter_prefix)
        print(f"  Split into {len(page_pngs)} half-pages")
    else:
        print("Step 2: Single-paged — copying as-is...")
        page_pngs = split_double_pages(raw_pngs, images_dir, chapter_prefix)
        # split_double_pages handles single-page case too
        print(f"  {len(page_pngs)} pages")

    # Step 3: OCR
    print("Step 3: Running OCR...")
    ocr_files = ocr_all_pages(page_pngs, ocr_dir)
    print(f"  OCR'd {len(ocr_files)} pages")

    print("\n--- Automated steps complete ---")
    print("Next steps (manual):")
    print("  4. Review OCR output in ocr/ and compose markdown")
    print("  5. Run analyze_borders() on pages with figures to get crop coordinates")
    print("  6. Build figure_specs list and run crop_figures()")
    print("  7. Update markdown image references to point to cropped figures")

    return {
        "raw_pages": raw_pngs,
        "page_images": page_pngs,
        "ocr_files": ocr_files,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scanned PDF to markdown pipeline")
    sub = parser.add_subparsers(dest="command")

    # Full pipeline
    p_run = sub.add_parser("run", help="Run full pipeline (render + split + OCR)")
    p_run.add_argument("pdf", help="Path to scanned PDF")
    p_run.add_argument("output_dir", help="Output directory")
    p_run.add_argument("--prefix", default="ch1", help="Chapter prefix (default: ch1)")
    p_run.add_argument("--single", action="store_true", help="Single-paged PDF")

    # Analyze borders
    p_analyze = sub.add_parser("analyze", help="Analyze borders in a page image")
    p_analyze.add_argument("image", help="Path to page PNG")
    p_analyze.add_argument("--threshold", type=int, default=128)

    args = parser.parse_args()

    if args.command == "run":
        pipeline(args.pdf, args.output_dir, args.prefix, not args.single)
    elif args.command == "analyze":
        analyze_borders(args.image, args.threshold)
    else:
        parser.print_help()
