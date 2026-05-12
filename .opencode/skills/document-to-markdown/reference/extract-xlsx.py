"""XLSX extraction: text via markitdown."""

from markitdown import MarkItDown
from pathlib import Path


def extract_xlsx(filepath, output_dir):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    md = MarkItDown()
    result = md.convert(filepath)
    (output / 'content.md').write_text(result.text_content)
    return result.text_content
