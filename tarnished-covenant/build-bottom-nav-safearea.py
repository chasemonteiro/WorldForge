from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Keep this patch deliberately narrow. The bottom nav is fixed viewport chrome;
# this file only corrects its box sizing and iPhone home-indicator allowance.
old_nav = ".tc-bottom-nav{position:fixed;z-index:30;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);height:70px;padding:5px 10px calc(5px + env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(4,1fr);background:linear-gradient(180deg,rgba(8,8,6,.88),rgba(6,6,5,.98) 28%);border-top:1px solid #2c281f;backdrop-filter:blur(12px)}"
new_nav = ".tc-bottom-nav{position:fixed;z-index:30;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);box-sizing:border-box;height:calc(58px + env(safe-area-inset-bottom));padding:3px 10px env(safe-area-inset-bottom);display:grid;grid-template-columns:repeat(4,1fr);background:linear-gradient(180deg,rgba(8,8,6,.88),rgba(6,6,5,.98) 28%);border-top:1px solid #2c281f;backdrop-filter:blur(12px)}"
if old_nav not in s:
    raise SystemExit('bottom nav source rule missing')
s = s.replace(old_nav, new_nav, 1)

# Slightly reduce generic document clearance to match the shorter corrected bar.
s = s.replace(
    ".app-shell{max-width:760px;padding:16px 14px calc(86px + env(safe-area-inset-bottom))}",
    ".app-shell{max-width:760px;padding:16px 14px calc(66px + env(safe-area-inset-bottom))}",
    1,
)

for needle in [
    'box-sizing:border-box;height:calc(58px + env(safe-area-inset-bottom))',
    '.app-shell{max-width:760px;padding:16px 14px calc(66px + env(safe-area-inset-bottom))}'
]:
    if needle not in s:
        raise SystemExit('bottom navigation invariant missing: '+needle)

# Viewport geometry does NOT belong here. Keeping this invariant prevents the
# first-load/"Ledger fixes it" Safari regression from being reintroduced.
for forbidden in [
    'One dynamic viewport across every primary screen',
    'body.tc-run-active',
    'height:100dvh!important',
    'height:100svh',
    'tcVisualViewport'
]:
    if forbidden in s[s.find(new_nav):s.find(new_nav)+5000]:
        raise SystemExit('viewport experiment leaked into safe-area patch: '+forbidden)

p.write_text(s)
