"""DOCX extraction: text via markitdown, images via python-docx."""

from markitdown import MarkItDown
from docx import Document
from pathlib import Path


def extract_docx(filepath, output_dir):
    output = Path(output_dir)
    (output / 'assets').mkdir(parents=True, exist_ok=True)

    # Text via markitdown
    md = MarkItDown()
    result = md.convert(filepath)
    content = result.text_content

    # Images from document relationships
    doc = Document(filepath)
    img_num = 0
    for rel in doc.part.rels.values():
        if "image" in rel.reltype:
            img_num += 1
            image_data = rel.target_part.blob
            ext = Path(rel.target_ref).suffix
            (output / 'assets' / f'figure-{img_num:02d}{ext}').write_bytes(image_data)

    (output / 'content.md').write_text(content)
    return content
