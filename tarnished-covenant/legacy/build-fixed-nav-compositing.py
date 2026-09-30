from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# A transformed ancestor becomes the containing block for position:fixed
# descendants. The bottom nav is rendered inside .tc-screen, so the old
# translateY entrance animation can make Safari pin the nav to the screen
# compositor instead of the physical viewport. Keep the fade, remove transform.
old = '@keyframes tcIn{from{opacity:.35;transform:translateY(5px)}to{opacity:1;transform:none}}'
new = '@keyframes tcIn{from{opacity:.35}to{opacity:1}}'

if old not in s:
    raise SystemExit('screen entrance animation source rule missing')
s = s.replace(old, new, 1)

if 'transform:translateY(5px)' in s:
    raise SystemExit('fixed-nav-hostile screen transform remains')
if new not in s:
    raise SystemExit('transform-free screen animation missing')

p.write_text(s)
