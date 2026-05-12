"""PDF extraction: text via markitdown, images via pdfplumber."""

import pdfplumber
from pathlib import Path


def extract_pdf(filepath, output_dir):
    output = Path(output_dir)
    (output / 'assets').mkdir(parents=True, exist_ok=True)
    (output / 'code').mkdir(parents=True, exist_ok=True)

    # Text extraction (use markitdown for simple PDFs)
    from markitdown import MarkItDown
    md = MarkItDown()
    result = md.convert(filepath)
    content = result.text_content

    # Image extraction via pdfplumber
    figure_num = 0
    with pdfplumber.open(filepath) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            for img in page.images:
                figure_num += 1
                bbox = (img['x0'], img['top'], img['x1'], img['bottom'])
                cropped = page.crop(bbox).to_image(resolution=150)
                cropped.save(str(output / 'assets' / f'figure-{figure_num:02d}.png'))

    (output / 'content.md').write_text(content)
    return content


def extract_two_column(page):
    """Multi-column PDF workaround: extract left and right halves separately."""
    mid_x = page.width / 2
    left = page.crop((0, 0, mid_x, page.height))
    right = page.crop((mid_x, 0, page.width, page.height))
    return left.extract_text() + "\n\n" + right.extract_text()
