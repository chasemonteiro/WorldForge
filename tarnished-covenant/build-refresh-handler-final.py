from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# useCovenantBoon owns the one-at-a-time guard itself. Any late wrapper that
# sets __tcBoonBusy before delegating makes the real handler immediately return.
wrapper=re.compile(r"""\n?if\(typeof useCovenantBoon==='function'&&!window\.__tcBoonStabilized\)\{\s*window\.__tcBoonStabilized=true;\s*const\s+tcUseCovenantBoonBefore[A-Za-z0-9_]*=useCovenantBoon;\s*useCovenantBoon=async function\(kind\)\{.*?\};\s*\}\s*""",re.S)
s,n=wrapper.subn('\n',s)

if 'tcUseCovenantBoonBefore' in s:
    raise SystemExit('outer Covenant boon wrapper remains')
if "if(typeof useCovenantBoon==='function'&&!window.__tcBoonStabilized)" in s:
    raise SystemExit('Covenant boon stabilizer wrapper remains')

required=[
    "if(window.__tcBoonBusy||!run?.state?.current)return;window.__tcBoonBusy=true;",
    "const btn=event.target.closest('[data-use-boon]');",
    "if(btn)useCovenantBoon(btn.dataset.useBoon);",
]
for needle in required:
    if needle not in s:
        raise SystemExit('refresh handler invariant missing: '+needle)

# There must be exactly one owner of the live busy flag: the real handler.
if s.count("if(window.__tcBoonBusy||!run?.state?.current)return;window.__tcBoonBusy=true;") != 1:
    raise SystemExit('unexpected Covenant boon busy-guard count')

p.write_text(s)
print(f'Removed {n} outer Covenant refresh wrapper(s).')
