from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

old = "${String(index+1).padStart(2,'0')}"
new = "${String(Math.max(1,(run.state.history?.length||0)-index)).padStart(2,'0')}"
count = s.count(old)
if count < 3:
    raise SystemExit(f'expected at least 3 Compendium index labels, found {count}')
s = s.replace(old, new)

if new not in s:
    raise SystemExit('stable Compendium numbering invariant missing')

p.write_text(s)
