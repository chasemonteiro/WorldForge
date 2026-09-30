from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# The final audit layer deliberately wraps encounter-mutating controls, including
# useCovenantBoon. On a subsequent clean production rebuild, remove that generated
# late layer first; it is reapplied after all core/treasury/appeal layers finish.
s,audit_removed=re.subn(
    r"\n?/\* --- Today systems audit hardening --- \*/.*?"
    r"/\* --- End today systems audit hardening --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

# useCovenantBoon owns the one-at-a-time guard itself. Any obsolete stability
# wrapper that sets __tcBoonBusy before delegating makes the real handler return.
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
print(f'Removed {n} obsolete Covenant refresh wrapper(s) and {audit_removed} generated audit layer(s) before final rebuild.')
