"""MHTML extraction: parse MIME parts, extract HTML and embedded images."""

import email
from bs4 import BeautifulSoup
from pathlib import Path


def extract_mhtml(filepath, output_dir):
    output = Path(output_dir)
    (output / 'assets').mkdir(parents=True, exist_ok=True)
    (output / 'code').mkdir(parents=True, exist_ok=True)

    with open(filepath, 'rb') as f:
        msg = email.message_from_bytes(f.read())

    html_part = None
    images = []
    for part in msg.walk():
        ct = part.get_content_type()
        if ct == 'text/html' and html_part is None:
            html_part = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        elif ct.startswith('image/'):
            images.append((
                part.get_filename() or f'image-{len(images)+1}',
                part.get_payload(decode=True)
            ))

    # Save images
    for i, (name, data) in enumerate(images, 1):
        ext = Path(name).suffix or '.png'
        (output / 'assets' / f'figure-{i:02d}{ext}').write_bytes(data)

    # Parse HTML for code and text
    if html_part:
        soup = BeautifulSoup(html_part, 'html.parser')

        code_num = 0
        for pre in soup.find_all('pre'):
            code_num += 1
            (output / 'code' / f'listing-{code_num:02d}.code').write_text(pre.get_text())

        from markitdown import MarkItDown
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as tmp:
            tmp.write(html_part)
            tmp_path = tmp.name
        md = MarkItDown()
        result = md.convert(tmp_path)
        content = result.text_content
        Path(tmp_path).unlink()
    else:
        content = "# No HTML content found in MHTML"

    (output / 'content.md').write_text(content)
    return content
