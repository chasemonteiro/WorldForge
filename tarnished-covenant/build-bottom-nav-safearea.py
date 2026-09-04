from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

old_nav = ".tc-bottom-nav{position:fixed;z-index:30;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);height:70px;padding:5px 10px calc(5px + env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(4,1fr);background:linear-gradient(180deg,rgba(8,8,6,.88),rgba(6,6,5,.98) 28%);border-top:1px solid #2c281f;backdrop-filter:blur(12px)}"
new_nav = ".tc-bottom-nav{position:fixed;z-index:30;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);box-sizing:border-box;height:calc(58px + env(safe-area-inset-bottom));padding:3px 10px env(safe-area-inset-bottom);display:grid;grid-template-columns:repeat(4,1fr);background:linear-gradient(180deg,rgba(8,8,6,.88),rgba(6,6,5,.98) 28%);border-top:1px solid #2c281f;backdrop-filter:blur(12px)}"
if old_nav not in s:
    raise SystemExit('bottom nav source rule missing')
s = s.replace(old_nav, new_nav, 1)

# A fixed bottom nav should overlay one shared dynamic viewport. Previous passes
# shortened only Grace / Encounter and then tried to compensate with svh, which
# produces a visibly different bottom edge on iOS. Remove that reservation.
old_shell = "padding:calc(8px + env(safe-area-inset-top)) 14px calc(70px + env(safe-area-inset-bottom));"
new_shell = "padding:calc(8px + env(safe-area-inset-top)) 14px 0;"
if old_shell not in s:
    raise SystemExit('viewport shell nav allowance missing')
s = s.replace(old_shell, new_shell, 1)

s = s.replace(".app-shell{max-width:760px;padding:16px 14px calc(86px + env(safe-area-inset-bottom))}", ".app-shell{max-width:760px;padding:16px 14px calc(66px + env(safe-area-inset-bottom))}", 1)

css = r'''
/* --- One dynamic viewport across every primary screen --- */
/* Geometry is keyed to an explicit runtime class rather than :has(.tc-bottom-nav).
   Safari can delay :has() invalidation when the persistent nav is mounted after
   first paint, which made Grace / Encounter start too high until Ledger rerendered. */
html{width:100%;min-height:100dvh;background-color:var(--bg)}
body.tc-run-active{
  width:100%;min-height:100dvh;background-color:var(--bg);padding:0!important;
}
body.tc-run-active .app-shell{
  width:100%;min-height:100dvh;
}
body.tc-run-active .app-shell:has(.tc-sanctuary-shell),
body.tc-run-active .app-shell:has(.tc-encounter-shell){
  height:100dvh!important;max-height:100dvh!important;min-height:100dvh!important;
}
.tc-sanctuary-shell,.tc-encounter-shell{
  height:100%!important;min-height:100%!important;
}
/* Content owns the nav clearance; the visual screen itself never stops early. */
.tc-sanctuary-panel{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}
.tc-encounter-panel{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}
.tc-encounter-actions{position:relative;z-index:2;margin-bottom:calc(58px + env(safe-area-inset-bottom));padding-bottom:7px}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing for full-screen nav pass')
s = s.replace('</style>', css + '\n</style>', 1)

for needle in [
    'box-sizing:border-box;height:calc(58px + env(safe-area-inset-bottom))',
    'One dynamic viewport across every primary screen',
    'padding:calc(8px + env(safe-area-inset-top)) 14px 0',
    'body.tc-run-active{',
    'padding:0!important;',
    '.tc-sanctuary-panel{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}'
]:
    if needle not in s:
        raise SystemExit('full-screen navigation invariant missing: '+needle)

# Explicitly reject the old nav-dependent geometry selector and old small viewport
# override. Neither should ever control first-paint layout again.
if 'body:has(.tc-bottom-nav)' in css or 'html:has(.tc-bottom-nav)' in css:
    raise SystemExit('nav-dependent :has geometry must not return')
if '@supports(height:100svh)' in css or 'height:100svh' in css:
    raise SystemExit('svh viewport override must not return')

p.write_text(s)
