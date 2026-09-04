from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

old = '''html:has(.tc-encounter-shell),body:has(.tc-encounter-shell),html:has(.tc-sanctuary-shell),body:has(.tc-sanctuary-shell){height:100%;overflow:hidden}
body:has(.tc-encounter-shell) .app-shell,body:has(.tc-sanctuary-shell) .app-shell{
  height:100svh;max-height:100svh;overflow:hidden;
  padding:calc(8px + env(safe-area-inset-top)) 14px calc(70px + env(safe-area-inset-bottom));
}
'''
if old not in s:
    raise SystemExit('screen-specific outer viewport lock not found')
s = s.replace(old, '', 1)

# The document owns the viewport and safe areas exactly once. The swipe shells
# remain flex containers, but their height is derived from the document's
# available viewport rather than forcing html/body into Safari's small viewport.
css = r'''
/* --- Unified primary-screen viewport: one document model for Grace, Encounter, Ledger --- */
html{min-height:100%}
body{min-height:100dvh}
body:has(.tc-encounter-shell),body:has(.tc-sanctuary-shell){
  height:auto!important;
  min-height:100dvh!important;
  overflow-x:hidden!important;
  overflow-y:auto!important;
}
body:has(.tc-encounter-shell) .app-shell,body:has(.tc-sanctuary-shell) .app-shell{
  height:calc(100dvh - env(safe-area-inset-top) - env(safe-area-inset-bottom))!important;
  max-height:none!important;
  min-height:0!important;
  overflow:hidden!important;
  padding:8px 14px 70px!important;
}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

for needle in [
    'Unified primary-screen viewport',
    'height:calc(100dvh - env(safe-area-inset-top) - env(safe-area-inset-bottom))!important',
    'padding:8px 14px 70px!important'
]:
    if needle not in s:
        raise SystemExit('unified viewport invariant missing: '+needle)

for forbidden in [
    'html:has(.tc-encounter-shell),body:has(.tc-encounter-shell),html:has(.tc-sanctuary-shell),body:has(.tc-sanctuary-shell){height:100%;overflow:hidden}',
    'height:100svh;max-height:100svh;overflow:hidden;\n  padding:calc(8px + env(safe-area-inset-top)) 14px calc(70px + env(safe-area-inset-bottom));'
]:
    if forbidden in s:
        raise SystemExit('old viewport lock remains: '+forbidden)

p.write_text(s)
