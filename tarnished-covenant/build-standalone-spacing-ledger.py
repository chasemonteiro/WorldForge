from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Keep Ledger inside the same installed-app viewport model as Grace/Encounter.
# It still scrolls, but iOS no longer has to switch the whole document between
# locked and unlocked viewport modes when entering/leaving the Ledger.
pat = r"(function renderLedger\(\) \{.*?app\.innerHTML=`)<section class=\"tc-screen\">"
s, n = re.subn(pat, r'\1<section class="tc-screen tc-ledger-shell">', s, count=1, flags=re.S)
if n != 1 and 'class="tc-screen tc-ledger-shell"' not in s:
    raise SystemExit('could not mark Ledger shell')

css = r'''
/* --- Standalone spacing + stable Ledger shell --- */
@media (display-mode: standalone) {
  /* The fixed-height briefing now has the full installed-app viewport. Let the
     boss art use more of it instead of leaving a dead band above the actions. */
  html.tc-standalone .tc-encounter-panel[data-panel="boss"] .tc-boss-art{
    height:clamp(190px,31vh,275px)!important;
    max-height:34vh!important;
  }
  html.tc-standalone .tc-encounter-panel[data-panel="boss"]{
    padding-bottom:4px!important;
  }
  html.tc-standalone .tc-encounter-hint{
    margin-top:-5px!important;
    margin-bottom:3px!important;
  }

  /* Do not make iOS tear down the fixed app viewport just because Ledger is a
     vertically scrolling screen. The app shell stays fixed; Ledger scrolls in it. */
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
    -webkit-overflow-scrolling:touch;
    padding-bottom:calc(86px + env(safe-area-inset-bottom))!important;
  }
  html.tc-standalone .tc-ledger-shell{
    min-height:100%!important;
  }
}
'''

if 'Standalone spacing + stable Ledger shell' not in s:
    if '</style>' not in s:
        raise SystemExit('style marker missing')
    s = s.replace('</style>', css + '\n</style>', 1)

required = [
    'class="tc-screen tc-ledger-shell"',
    'Standalone spacing + stable Ledger shell',
    'height:clamp(190px,31vh,275px)!important',
    'body:has(.tc-ledger-shell) .app-shell',
    '-webkit-overflow-scrolling:touch',
]
for needle in required:
    if needle not in s:
        raise SystemExit('standalone polish invariant missing: ' + needle)

p.write_text(s)
