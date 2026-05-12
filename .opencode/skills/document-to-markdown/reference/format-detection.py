"""Format detection via magic bytes. Do NOT trust file extensions alone."""

import struct


def detect_format(filepath):
    """Detect file format via magic bytes."""
    with open(filepath, 'rb') as f:
        header = f.read(8)

    # ZIP-based formats (.pptx, .docx, .xlsx)
    if header[:4] == b'PK\x03\x04':
        import zipfile
        with zipfile.ZipFile(filepath) as zf:
            names = zf.namelist()
            if any('ppt/' in n for n in names):
                return 'pptx'
            elif any('word/' in n for n in names):
                return 'docx'
            elif any('xl/' in n for n in names):
                return 'xlsx'
        return 'zip'

    # PDF
    if header[:5] == b'%PDF-':
        return 'pdf'

    # OLE2 Compound Document (.ppt, .doc, .xls legacy)
    if header[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
        import olefile
        ole = olefile.OleFileIO(filepath)
        if ole.exists('PowerPoint Document'):
            ole.close()
            return 'ppt'
        elif ole.exists('WordDocument'):
            ole.close()
            return 'doc'
        ole.close()
        return 'ole'

    # Text-based: HTML or MHTML
    with open(filepath, 'r', errors='ignore') as f:
        start = f.read(500)
    if start.startswith('From:') or 'MIME-Version:' in start[:200]:
        return 'mhtml'
    if '<html' in start.lower() or '<!doctype' in start.lower():
        return 'html'

    return 'unknown'
