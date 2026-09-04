from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

required=[
    'tc-persistent-nav',
    'tc-nav-anchor',
    'tcPersistentNavObserver',
    "document.body.appendChild(tcPersistentBottomNav)",
    "navMarkup=function(active)",
    "document.addEventListener('click',event=>",
    "@keyframes tcScreenFade{from{opacity:.45}to{opacity:1}}",
]
for needle in required:
    if needle not in html:
        raise SystemExit('persistent-nav invariant missing: '+needle)

# The final nav renderer must no longer emit a fixed nav inside .tc-screen.
last_nav=html.rfind('navMarkup=function(active)')
if last_nav<0:
    raise SystemExit('final persistent navMarkup override missing')
chunk=html[last_nav:last_nav+500]
if '<nav class="tc-bottom-nav">' in chunk:
    raise SystemExit('final navMarkup still recreates bottom nav inside screen')
if 'tc-nav-anchor' not in chunk:
    raise SystemExit('final navMarkup does not emit persistent-nav anchor')

# Avoid the Safari fixed-within-transform bug that caused first-load floating.
if '@keyframes tcIn{from{opacity:.35;transform:translateY(5px)}' in html:
    # Legacy rule may remain earlier in CSS, but it must be superseded by our
    # final tc-screen animation declaration.
    final_screen=html.rfind('.tc-screen{animation:tcScreenFade')
    if final_screen<0:
        raise SystemExit('legacy transformed screen animation is not superseded')

print('Tarnished Covenant persistent navigation: PASS')
