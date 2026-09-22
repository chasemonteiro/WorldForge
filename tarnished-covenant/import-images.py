"""Import the supplied ERB/ERL archives. Run from the repository root.

Usage: python tarnished-covenant/import-images.py /path/ERB.zip /path/ERL.zip
Requires Pillow with AVIF support. Existing gameplay data is never changed.
"""
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from PIL import Image, ImageOps

root = Path('tarnished-covenant')

def key(name):
    return re.sub(r'[^a-z0-9]+', ' ', name.lower()).strip()

catalog = {}
for archive, kind in zip(sys.argv[1:], ['bosses', 'regions']):
    entries = {}
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            if member.is_dir() or Path(member.filename).suffix.lower() not in {'.jpg','.jpeg','.png','.webp','.avif'}:
                continue
            name = key(Path(member.filename).stem)
            path = root / 'assets' / kind / (name.replace(' ', '-') + '.webp')
            path.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(io.BytesIO(z.read(member))) as source:
                im = ImageOps.exif_transpose(source).convert('RGB')
                im.thumbnail((1280, 900))
                im.save(path, 'WEBP', quality=80, method=6)
            entries[name] = './' + path.relative_to(root).as_posix()
    catalog[kind] = entries
if len(catalog.get('bosses', {})) != 141 or len(catalog.get('regions', {})) != 17:
    raise SystemExit('Expected 141 boss images and 17 location images')
(root / 'image-catalog.json').write_text(json.dumps(catalog, indent=2) + '\n')
print('Imported 141 boss images and 17 location images')
