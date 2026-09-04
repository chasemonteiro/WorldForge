from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Keep Ledger inside the same installed-app viewport model as Grace/Encounter.
pat = r"(function renderLedger\(\) \{.*?app\.innerHTML=`)<section class=\"tc-screen(?: tc-ledger-shell)?\">"
s, n = re.subn(pat, r'\1<section class="tc-screen tc-ledger-shell">', s, count=1, flags=re.S)
if n != 1 and 'class="tc-screen tc-ledger-shell"' not in s:
    raise SystemExit('could not mark Ledger shell')

# Replace the first version of this patch if it is already present.
old_start = s.find('/* --- Standalone spacing + stable Ledger shell --- */')
if old_start != -1:
    old_end = s.find('</style>', old_start)
    if old_end == -1:
        raise SystemExit('could not locate old polish CSS end')
    s = s[:old_start] + s[old_end:]

css = r'''
/* --- Standalone spacing + stable Ledger shell --- */
/* Use the JS-applied tc-standalone class directly. iOS Home Screen mode is
   reliably exposing navigator.standalone on this device even when the CSS
   display-mode media query does not match. */
html.tc-standalone .tc-encounter-panel[data-panel="boss"] .tc-boss-art{
  height:clamp(250px,38vh,350px)!important;
  max-height:42vh!important;
  aspect-ratio:auto!important;
  margin-bottom:5px!important;
}
html.tc-standalone .tc-encounter-panel[data-panel="boss"]{
  padding-bottom:2px!important;
}
html.tc-standalone .tc-encounter-hint{
  margin-top:-5px!important;
  margin-bottom:3px!important;
}

/* Grace gets the same post-viewport-fix spacing treatment. */
html.tc-standalone .tc-sanctuary-panel[data-panel="grace"] .tc-grace-art{
  height:clamp(230px,34vh,320px)!important;
  max-height:38vh!important;
  aspect-ratio:auto!important;
  margin:7px 0 7px!important;
}
html.tc-standalone .tc-sanctuary-panel[data-panel="grace"] .tc-title{
  margin-top:7px!important;
}
html.tc-standalone .tc-sanctuary-hint{
  margin-top:-4px!important;
  margin-bottom:3px!important;
}

/* Keep the document in one fixed standalone viewport when moving to Ledger.
   Ledger becomes the scroll container instead of switching body geometry. */
html.tc-standalone:has(.tc-ledger-shell),
html.tc-standalone body:has(.tc-ledger-shell){
  height:100%!important;
  overflow:hidden!important;
}
html.tc-standalone body:has(.tc-ledger-shell) .app-shell{
  height:100vh!important;
  max-height:100vh!important;
  overflow-x:hidden!important;
  overflow-y:auto!important;
  overscroll-behavior-y:contain;
  -webkit-overflow-scrolling:touch;
  padding-bottom:calc(86px + env(safe-area-inset-bottom))!important;
}
html.tc-standalone .tc-ledger-shell{
  min-height:100%!important;
  padding-bottom:8px!important;
}
'''

if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

required = [
    'class="tc-screen tc-ledger-shell"',
    'Standalone spacing + stable Ledger shell',
    'height:clamp(250px,38vh,350px)!important',
    'height:clamp(230px,34vh,320px)!important',
    'html.tc-standalone body:has(.tc-ledger-shell) .app-shell',
]
for needle in required:
    if needle not in s:
        raise SystemExit('standalone polish invariant missing: ' + needle)

# This exact bug was caused by putting the patch behind display-mode.
polish = s[s.find('/* --- Standalone spacing + stable Ledger shell --- */'):s.find('</style>', s.find('/* --- Standalone spacing + stable Ledger shell --- */'))]
if '@media (display-mode: standalone)' in polish:
    raise SystemExit('polish must not depend on display-mode media query')

p.write_text(s)
