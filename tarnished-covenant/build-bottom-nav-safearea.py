from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

old_nav = ".tc-bottom-nav{position:fixed;z-index:30;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);height:70px;padding:5px 10px calc(5px + env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(4,1fr);background:linear-gradient(180deg,rgba(8,8,6,.88),rgba(6,6,5,.98) 28%);border-top:1px solid #2c281f;backdrop-filter:blur(12px)}"
new_nav = ".tc-bottom-nav{position:fixed;z-index:30;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);box-sizing:border-box;height:calc(58px + env(safe-area-inset-bottom));padding:3px 10px env(safe-area-inset-bottom);display:grid;grid-template-columns:repeat(4,1fr);background:linear-gradient(180deg,rgba(8,8,6,.88),rgba(6,6,5,.98) 28%);border-top:1px solid #2c281f;backdrop-filter:blur(12px)}"
if old_nav not in s:
    raise SystemExit('bottom nav source rule missing')
s = s.replace(old_nav, new_nav, 1)

old_shell = "padding:calc(8px + env(safe-area-inset-top)) 14px calc(70px + env(safe-area-inset-bottom));"
new_shell = "padding:calc(8px + env(safe-area-inset-top)) 14px calc(58px + env(safe-area-inset-bottom));"
if old_shell not in s:
    raise SystemExit('viewport shell nav allowance missing')
s = s.replace(old_shell, new_shell, 1)

# Non-viewport screens still reserve space for the same physical nav height.
s = s.replace(".app-shell{max-width:760px;padding:16px 14px calc(86px + env(safe-area-inset-bottom))}", ".app-shell{max-width:760px;padding:16px 14px calc(66px + env(safe-area-inset-bottom))}", 1)

for needle in ['box-sizing:border-box;height:calc(58px + env(safe-area-inset-bottom))','calc(58px + env(safe-area-inset-bottom))']:
    if needle not in s:
        raise SystemExit('bottom nav safe-area invariant missing: '+needle)

p.write_text(s)
