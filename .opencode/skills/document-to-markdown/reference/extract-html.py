"""HTML extraction: text via markitdown, code blocks from <pre> tags."""

from markitdown import MarkItDown
from bs4 import BeautifulSoup
from pathlib import Path
import re


def extract_html(filepath, output_dir):
    output = Path(output_dir)
    (output / 'assets').mkdir(parents=True, exist_ok=True)
    (output / 'code').mkdir(parents=True, exist_ok=True)

    with open(filepath, 'r', errors='ignore') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Extract code blocks from <pre> tags
    code_num = 0
    for pre in soup.find_all('pre'):
        code_text = pre.get_text()
        # Skip if it looks like math/equations rather than code
        if '\\frac' in code_text or '\\sum' in code_text:
            continue
        code_num += 1
        (output / 'code' / f'listing-{code_num:02d}.code').write_text(code_text)

    # Handle custom component tags (Angular/React)
    custom_tags = soup.find_all(re.compile(r'^(app-|mb-|ng-)'))
    custom_notes = []
    for tag in custom_tags:
        if tag.get_text(strip=True):
            custom_notes.append(f"[Component: {tag.name}] {tag.get_text(strip=True)}")

    # Main text via markitdown
    md = MarkItDown()
    result = md.convert(filepath)
    content = result.text_content

    if custom_notes:
        content += "\n\n## Custom Components Found\n\n" + "\n".join(
            f"- {n}" for n in custom_notes
        )

    (output / 'content.md').write_text(content)
    return content
