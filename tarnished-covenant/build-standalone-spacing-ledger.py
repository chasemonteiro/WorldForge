from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Mark Ledger so the standalone shell can treat it as a first-class screen.
pat = r"(function renderLedger\(\) \{.*?app\.innerHTML=`)<section class=\"tc-screen(?: tc-ledger-shell)?\">"
s, n = re.subn(pat, r'\1<section class="tc-screen tc-ledger-shell">', s, count=1, flags=re.S)
if n != 1 and 'class="tc-screen tc-ledger-shell"' not in s:
    raise SystemExit('could not mark Ledger shell')

# iOS may preserve a nested scroll container's vertical offset when the app
# rerenders. Reset all briefing panels on mount, and reset the selected panel
# whenever its tab is chosen. This prevents boss/Grace headings from opening
# already clipped beneath the tab bar.
old = "const go=i=>{i=Math.max(0,Math.min(count-1,i));setIndex(i);track.scrollTo({left:i*track.clientWidth,behavior:'smooth'});tabs.querySelectorAll('button').forEach((b,j)=>b.classList.toggle('active',j===i));};"
new = "const go=i=>{i=Math.max(0,Math.min(count-1,i));setIndex(i);const panels=track.querySelectorAll('.tc-encounter-panel,.tc-sanctuary-panel');if(panels[i])panels[i].scrollTop=0;track.scrollTo({left:i*track.clientWidth,behavior:'smooth'});tabs.querySelectorAll('button').forEach((b,j)=>b.classList.toggle('active',j===i));};"
if old in s:
    s = s.replace(old, new, 1)
elif "if(panels[i])panels[i].scrollTop=0" not in s:
    raise SystemExit('panel go() target missing')

old_raf = "requestAnimationFrame(()=>{track.scrollLeft=getIndex()*track.clientWidth;});"
new_raf = "requestAnimationFrame(()=>{track.scrollLeft=getIndex()*track.clientWidth;track.querySelectorAll('.tc-encounter-panel,.tc-sanctuary-panel').forEach(panel=>{panel.scrollTop=0;});});"
if old_raf in s:
    s = s.replace(old_raf, new_raf, 1)
elif "forEach(panel=>{panel.scrollTop=0;})" not in s:
    raise SystemExit('panel mount reset target missing')

# Replace any earlier version of this focused CSS block.
old_start = s.find('/* --- Standalone spacing + stable Ledger shell --- */')
if old_start != -1:
    old_end = s.find('</style>', old_start)
    if old_end == -1:
        raise SystemExit('could not locate old polish CSS end')
    s = s[:old_start] + s[old_end:]

css = r'''
/* --- Standalone spacing + stable Ledger shell --- */
/* Keep artwork substantial but do not use it to paper over panel-scroll bugs. */
html.tc-standalone .tc-encounter-panel[data-panel="boss"] .tc-boss-art{
  height:clamp(180px,24vh,230px)!important;
  max-height:230px!important;
  aspect-ratio:auto!important;
  margin:7px 0 8px!important;
}
html.tc-standalone .tc-encounter-panel[data-panel="boss"]{
  padding-top:2px!important;
  padding-bottom:6px!important;
}
html.tc-standalone .tc-encounter-hint{
  margin:-2px 0 4px!important;
}
html.tc-standalone .tc-sanctuary-panel[data-panel="grace"] .tc-grace-art{
  height:clamp(175px,23vh,225px)!important;
  max-height:225px!important;
  aspect-ratio:auto!important;
  margin:8px 0!important;
}
html.tc-standalone .tc-sanctuary-panel[data-panel="grace"] .tc-title{
  margin-top:8px!important;
}

/* Ledger remains in the fixed installed-app shell, but Ledger itself is the
   scroll container. Its scroll position therefore survives DOM detachment. */
html.tc-standalone:has(.tc-ledger-shell),
html.tc-standalone body:has(.tc-ledger-shell){
  height:100%!important;
  overflow:hidden!important;
}
html.tc-standalone body:has(.tc-ledger-shell) .app-shell{
  height:100vh!important;
  max-height:100vh!important;
  overflow:hidden!important;
  padding:16px 14px calc(70px + env(safe-area-inset-bottom))!important;
}
html.tc-standalone .tc-ledger-shell{
  height:100%!important;
  min-height:0!important;
  overflow-y:auto!important;
  overflow-x:hidden!important;
  overscroll-behavior-y:contain;
  -webkit-overflow-scrolling:touch;
  padding-bottom:18px!important;
}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

# Cache the actual Ledger DOM node. Navigating away detaches it rather than
# destroying it; returning reattaches the same node. Rebuild only when Ledger's
# view or run state changed.
cache_js = r'''

/* --- Persistent Ledger DOM cache --- */
let tcLedgerCachedNode=null;
let tcLedgerCachedSignature='';
const tcRenderLedgerBeforeDomCache=renderLedger;
renderLedger=function(){
  const signature=ledgerView+'|'+JSON.stringify(run.state);
  if(tcLedgerCachedNode && tcLedgerCachedSignature===signature){
    app.replaceChildren(tcLedgerCachedNode);
    return;
  }
  tcRenderLedgerBeforeDomCache();
  tcLedgerCachedNode=app.querySelector('.tc-ledger-shell');
  tcLedgerCachedSignature=signature;
};
const tcRenderRunBeforeLedgerDomCache=renderRun;
renderRun=function(){
  if(uiScreen!=='ledger'){
    const mounted=app.querySelector('.tc-ledger-shell');
    if(mounted && mounted===tcLedgerCachedNode) mounted.remove();
  }
  return tcRenderRunBeforeLedgerDomCache();
};
'''

if 'Persistent Ledger DOM cache' not in s:
    # Insert before the last inline script closes so all wrapped functions exist.
    idx = s.rfind('</script>')
    if idx == -1:
        raise SystemExit('script marker missing')
    s = s[:idx] + cache_js + '\n' + s[idx:]

required = [
    'class="tc-screen tc-ledger-shell"',
    "if(panels[i])panels[i].scrollTop=0",
    "forEach(panel=>{panel.scrollTop=0;})",
    'height:clamp(180px,24vh,230px)!important',
    'Persistent Ledger DOM cache',
    'app.replaceChildren(tcLedgerCachedNode)',
    'mounted.remove()',
]
for needle in required:
    if needle not in s:
        raise SystemExit('focused fix invariant missing: ' + needle)

p.write_text(s)
