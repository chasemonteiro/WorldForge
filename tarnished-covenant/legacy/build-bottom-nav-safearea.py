from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Preserve the exact bottom-nav geometry from the last generated build before
# the navigation regression. The base UI already owns the iPhone safe-area
# allowance correctly; this stage now acts only as a guard against later drift.
expected_nav = ".tc-bottom-nav{position:fixed;z-index:30;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);height:70px;padding:5px 10px calc(5px + env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(4,1fr);background:linear-gradient(180deg,rgba(8,8,6,.88),rgba(6,6,5,.98) 28%);border-top:1px solid #2c281f;backdrop-filter:blur(12px)}"
expected_shell = ".app-shell{max-width:760px;padding:16px 14px calc(86px + env(safe-area-inset-bottom))}"

for needle in [expected_nav, expected_shell]:
    if needle not in s:
        raise SystemExit('pre-regression navigation geometry missing: '+needle[:90])

# Explicitly reject the geometry introduced by the first safe-area experiment.
for forbidden in [
    'box-sizing:border-box;height:calc(58px + env(safe-area-inset-bottom))',
    '.app-shell{max-width:760px;padding:16px 14px calc(66px + env(safe-area-inset-bottom))}',
    'One dynamic viewport across every primary screen',
    'body.tc-run-active',
    'height:100dvh!important',
    'tcVisualViewport'
]:
    if forbidden in s:
        raise SystemExit('regressed navigation geometry returned: '+forbidden)

p.write_text(s)
