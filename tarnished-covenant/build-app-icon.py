from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Durable Safari / Home Screen icon wiring.
# Keep this idempotent so normal production rebuilds can rerun it safely.
s=re.sub(r'\n?\s*<link rel="apple-touch-icon"[^>]*>','',s)
s=re.sub(r'\n?\s*<link rel="icon"[^>]*data-tc-app-icon[^>]*>','',s)

anchor='  <meta name="apple-mobile-web-app-title" content="Tarnished Covenant">\n'
if anchor not in s:
    raise SystemExit('apple mobile title anchor missing')

icon_tags='''  <link rel="apple-touch-icon" sizes="180x180" href="./assets/tarnished-covenant-icon-v1.png">\n  <link rel="icon" type="image/png" sizes="180x180" href="./assets/tarnished-covenant-icon-v1.png" data-tc-app-icon>\n'''
s=s.replace(anchor,anchor+icon_tags,1)

for needle in ['rel="apple-touch-icon"','tarnished-covenant-icon-v1.png','data-tc-app-icon']:
    if needle not in s:
        raise SystemExit('app icon invariant missing: '+needle)

p.write_text(s)
