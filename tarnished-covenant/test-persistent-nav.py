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
    'window.visualViewport',
    'function tcApplyVisualViewport()',
    "--tc-vvh",
    "--tc-nav-top",
    "nav.querySelectorAll('[data-screen]').forEach",
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

# CSS viewport units are only a fallback now. The final persistent-nav layer must
# use the measured VisualViewport for both screen height and nav top position.
persistent_start=html.rfind('/* --- Persistent bottom navigation: measured viewport chrome')
if persistent_start<0:
    raise SystemExit('measured persistent nav CSS block missing')
persistent_tail=html[persistent_start:]
for needle in [
    'height:var(--tc-vvh,100dvh)!important',
    'top:var(--tc-nav-top,auto)!important',
    'bottom:auto!important',
    'viewportTop+viewportHeight-navHeight',
    'requestAnimationFrame(tcApplyVisualViewport)',
    'setTimeout(tcApplyVisualViewport,260)'
]:
    if needle not in persistent_tail:
        raise SystemExit('measured visual viewport invariant missing: '+needle)

# Updating the selected tab must not rebuild the persistent bar on every screen.
sync_start=html.rfind('function tcSyncPersistentNav()')
sync_tail=html[sync_start:sync_start+900]
if 'nav.innerHTML=' in sync_tail:
    raise SystemExit('persistent nav is still rebuilding its buttons during sync')
if "classList.toggle('active'" not in sync_tail:
    raise SystemExit('persistent nav does not update active tab in-place')

print('Tarnished Covenant persistent navigation: PASS')
