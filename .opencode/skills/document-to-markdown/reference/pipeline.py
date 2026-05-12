"""Full extraction pipeline: detect format and dispatch to appropriate extractor."""

import json
from datetime import datetime
from pathlib import Path


def write_manifest(output_dir, source_file, detected_format, notes=""):
    output = Path(output_dir)
    assets = list((output / 'assets').glob('*')) if (output / 'assets').exists() else []
    code_files = list((output / 'code').glob('*')) if (output / 'code').exists() else []

    manifest = {
        "source": str(source_file),
        "format": detected_format,
        "extracted_at": datetime.now().isoformat(),
        "assets_count": len(assets),
        "code_listings_count": len(code_files),
        "assets": [f.name for f in assets],
        "code": [f.name for f in code_files],
        "notes": notes
    }
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2))


def extract_document(filepath, output_dir):
    """Full extraction pipeline."""
    from format_detection import detect_format
    from extract_pdf import extract_pdf
    from extract_pptx import extract_pptx
    from extract_ppt_legacy import extract_ppt
    from extract_html import extract_html
    from extract_mhtml import extract_mhtml
    from extract_docx import extract_docx
    from extract_xlsx import extract_xlsx

    fmt = detect_format(filepath)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    extractors = {
        'pdf': extract_pdf,
        'pptx': extract_pptx,
        'ppt': extract_ppt,
        'html': extract_html,
        'mhtml': extract_mhtml,
        'docx': extract_docx,
        'xlsx': extract_xlsx,
    }

    if fmt not in extractors:
        raise ValueError(f"Unsupported format: {fmt}")

    content = extractors[fmt](filepath, output_dir)
    write_manifest(output_dir, filepath, fmt)
    return fmt, content
