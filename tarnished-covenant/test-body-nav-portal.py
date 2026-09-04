from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(x):
    if x not in html: raise SystemExit('missing body-nav invariant: '+x)

def forbid(x):
    if x in html: raise SystemExit('forbidden body-nav regression: '+x)

for needle in [
    'const tcNavMarkupBeforePortal=navMarkup;',
    "navMarkup=function(active){",
    "return '';",
    'function tcMountBodyNav(active=tcPendingNavActive)',
    "document.body.insertAdjacentHTML('beforeend',tcNavMarkupBeforePortal(active));",
    "document.querySelectorAll('body > .tc-bottom-nav, #app .tc-bottom-nav')",
    "document.addEventListener('click',event=>",
    'const tcRenderRunBeforeBodyNavPortal=renderRun;',
    'tcRemoveBodyNav();\n  return tcRenderRunBeforeBodyNavPortal();'
]: require(needle)

# Keep the known-good visual geometry untouched while changing only DOM ownership.
require('height:70px;padding:5px 10px calc(5px + env(safe-area-inset-bottom))')
require('.app-shell{max-width:760px;padding:16px 14px calc(86px + env(safe-area-inset-bottom))}')
forbid('tc-persistent-nav')
forbid('tcVisualViewport')

# The final navigation binder must be document-level, not delegated through #app.
last_bind=html.rfind('bindNav=function()')
if last_bind<0: raise SystemExit('final bindNav override missing')
tail=html[last_bind:last_bind+1200]
if "document.addEventListener('click',event=>" not in tail:
    raise SystemExit('final navigation binder is not document-level')
if "app.addEventListener('click',event=>" in tail:
    raise SystemExit('final navigation binder still depends on app container')

print('Tarnished Covenant body-nav portal invariants: PASS')
