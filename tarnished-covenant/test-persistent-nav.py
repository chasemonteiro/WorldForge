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
    "document.body.classList.add('tc-run-active')",
    "body.tc-run-active{",
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
    final_screen=html.rfind('.tc-screen{animation:tcScreenFade')
    if final_screen<0:
        raise SystemExit('legacy transformed screen animation is not superseded')

# First-paint viewport geometry must be explicit. Never key safe-area removal to
# the existence of the nav element itself; Safari can delay :has invalidation.
geometry_start=html.find('/* --- One dynamic viewport across every primary screen --- */')
geometry_end=html.find('</style>',geometry_start)
if geometry_start<0 or geometry_end<0:
    raise SystemExit('dynamic viewport geometry block missing')
geometry=html[geometry_start:geometry_end]
if 'body:has(.tc-bottom-nav)' in geometry or 'html:has(.tc-bottom-nav)' in geometry:
    raise SystemExit('first-paint geometry still depends on dynamic :has(.tc-bottom-nav)')
if 'body.tc-run-active' not in geometry:
    raise SystemExit('explicit tc-run-active geometry missing')

print('Tarnished Covenant persistent navigation: PASS')
