"""Legacy PPT extraction via OLE stream parsing."""

import olefile
import re
from pathlib import Path


def extract_ppt(filepath, output_dir):
    output = Path(output_dir)
    (output / 'assets').mkdir(parents=True, exist_ok=True)

    ole = olefile.OleFileIO(filepath)

    # Extract images from Pictures stream
    if ole.exists('Pictures'):
        pictures_data = ole.openstream('Pictures').read()
        img_num = 0

        # Scan for JPEG signatures
        for match in re.finditer(b'\xff\xd8\xff', pictures_data):
            img_num += 1
            start = match.start()
            end = pictures_data.find(b'\xff\xd9', start) + 2
            if end > start:
                (output / 'assets' / f'figure-{img_num:02d}.jpg').write_bytes(
                    pictures_data[start:end]
                )

        # Scan for PNG signatures
        for match in re.finditer(b'\x89PNG\r\n\x1a\n', pictures_data):
            img_num += 1
            start = match.start()
            iend = pictures_data.find(b'IEND', start)
            if iend > 0:
                end = iend + 8
                (output / 'assets' / f'figure-{img_num:02d}.png').write_bytes(
                    pictures_data[start:end]
                )

    # Extract text (heuristic — scan for ASCII strings)
    text_parts = []
    if ole.exists('PowerPoint Document'):
        ppt_stream = ole.openstream('PowerPoint Document').read()
        current = []
        for byte in ppt_stream:
            if 32 <= byte < 127:
                current.append(chr(byte))
            else:
                if len(current) > 20:  # Filter noise
                    text_parts.append(''.join(current))
                current = []

    ole.close()
    content = '\n\n'.join(text_parts)
    (output / 'content.md').write_text(content)
    return content
