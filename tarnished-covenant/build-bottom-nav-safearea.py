from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

old_nav = ".tc-bottom-nav{position:fixed;z-index:30;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);height:70px;padding:5px 10px calc(5px + env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(4,1fr);background:linear-gradient(180deg,rgba(8,8,6,.88),rgba(6,6,5,.98) 28%);border-top:1px solid #2c281f;backdrop-filter:blur(12px)}"
new_nav = ".tc-bottom-nav{position:fixed;z-index:30;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);box-sizing:border-box;height:calc(58px + env(safe-area-inset-bottom));padding:3px 10px env(safe-area-inset-bottom);display:grid;grid-template-columns:repeat(4,1fr);background:linear-gradient(180deg,rgba(8,8,6,.88),rgba(6,6,5,.98) 28%);border-top:1px solid #2c281f;backdrop-filter:blur(12px)}"
if old_nav not in s:
    raise SystemExit('bottom nav source rule missing')
s = s.replace(old_nav, new_nav, 1)

# The fixed nav overlays the viewport. Do not shorten viewport-oriented screens to
# make room for it; that produced a visibly different bottom edge on Grace and
# Encounter compared with Ledger/Compendium. Instead, let the app shell reach the
# physical bottom and reserve tap-safe room inside scrollable content.
old_shell = "padding:calc(8px + env(safe-area-inset-top)) 14px calc(70px + env(safe-area-inset-bottom));"
new_shell = "padding:calc(8px + env(safe-area-inset-top)) 14px 0;"
if old_shell not in s:
    raise SystemExit('viewport shell nav allowance missing')
s = s.replace(old_shell, new_shell, 1)

# Non-viewport screens already behave like the Compendium reference: they may
# scroll beneath the fixed nav, with enough trailing content padding to remain usable.
s = s.replace(".app-shell{max-width:760px;padding:16px 14px calc(86px + env(safe-area-inset-bottom))}", ".app-shell{max-width:760px;padding:16px 14px calc(66px + env(safe-area-inset-bottom))}", 1)

css = r'''
/* --- One physical viewport across every primary screen --- */
html:has(.tc-bottom-nav),body:has(.tc-bottom-nav){min-height:100%;background-color:var(--bg)}
body:has(.tc-bottom-nav) .app-shell{min-height:100dvh}
body:has(.tc-sanctuary-shell) .app-shell,body:has(.tc-encounter-shell) .app-shell{height:100dvh;max-height:100dvh;min-height:100dvh}
.tc-sanctuary-shell,.tc-encounter-shell{height:100%;min-height:100%}
/* Content, not the screen, owns the nav clearance. This lets the patterned app
   surface continue behind the nav exactly like Ledger/Compendium. */
.tc-sanctuary-panel{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}
.tc-encounter-panel{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}
.tc-encounter-actions{position:relative;z-index:2;margin-bottom:calc(58px + env(safe-area-inset-bottom));padding-bottom:7px}
@supports(height:100svh){body:has(.tc-sanctuary-shell) .app-shell,body:has(.tc-encounter-shell) .app-shell{height:100svh;max-height:100svh;min-height:100svh}}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing for full-screen nav pass')
s = s.replace('</style>', css + '\n</style>', 1)

for needle in [
    'box-sizing:border-box;height:calc(58px + env(safe-area-inset-bottom))',
    'One physical viewport across every primary screen',
    'padding:calc(8px + env(safe-area-inset-top)) 14px 0',
    '.tc-sanctuary-panel{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}',
    '.tc-encounter-actions{position:relative;z-index:2;margin-bottom:calc(58px + env(safe-area-inset-bottom))'
]:
    if needle not in s:
        raise SystemExit('full-screen navigation invariant missing: '+needle)

p.write_text(s)
