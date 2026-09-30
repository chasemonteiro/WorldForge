from pathlib import Path

html = Path('tarnished-covenant/index.html').read_text()

def require(x):
    if x not in html: raise SystemExit('missing unified viewport invariant: '+x)

def forbid(x):
    if x in html: raise SystemExit('obsolete split viewport remains: '+x)

require('Unified primary-screen viewport')
require('body:has(.tc-encounter-shell),body:has(.tc-sanctuary-shell)')
require('height:calc(100dvh - env(safe-area-inset-top) - env(safe-area-inset-bottom))!important')
require('padding:8px 14px 70px!important')
require('body > .tc-bottom-nav')

forbid('html:has(.tc-encounter-shell),body:has(.tc-encounter-shell),html:has(.tc-sanctuary-shell),body:has(.tc-sanctuary-shell){height:100%;overflow:hidden}')
forbid('height:100svh;max-height:100svh;overflow:hidden;\n  padding:calc(8px + env(safe-area-inset-top)) 14px calc(70px + env(safe-area-inset-bottom));')

print('Unified viewport invariants: PASS')
