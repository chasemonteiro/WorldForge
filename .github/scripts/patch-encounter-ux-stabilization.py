from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
tc = root / 'tarnished-covenant'

# -----------------------------------------------------------------------------
# Durable source: iOS standalone geometry / screen fit.
# -----------------------------------------------------------------------------
p = tc / 'build-ios-standalone-shell.py'
s = p.read_text()
if 'margin-bottom:22px!important' not in s and 'margin-bottom:88px!important' not in s:
    raise SystemExit('Encounter action margin target missing')
s = s.replace('margin-bottom:22px!important', 'margin-bottom:88px!important')
marker = '''html.tc-standalone .tc-encounter-actions{\n  margin-bottom:88px!important;\n}\n'''
extra = r'''
/* The three transient Covenant notices fit on the phone. Keep the document
   fixed and let the notice itself own the available space instead of creating
   a pointless body scroll. */
html.tc-standalone:has(.tc-chaos-event),
html.tc-standalone:has(.tc-reveal),
html.tc-standalone:has(.tc-reward-machine),
html.tc-standalone body:has(.tc-chaos-event),
html.tc-standalone body:has(.tc-reveal),
html.tc-standalone body:has(.tc-reward-machine){
  height:100%!important;
  overflow:hidden!important;
}
html.tc-standalone body:has(.tc-chaos-event) .app-shell,
html.tc-standalone body:has(.tc-reveal) .app-shell{
  height:calc(100vh - env(safe-area-inset-top))!important;
  max-height:calc(100vh - env(safe-area-inset-top))!important;
  overflow:hidden!important;
  padding:8px 14px calc(70px + env(safe-area-inset-bottom))!important;
}
html.tc-standalone body:has(.tc-reward-machine) .app-shell{
  height:calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom))!important;
  max-height:calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom))!important;
  overflow:hidden!important;
  padding:6px 14px!important;
}
html.tc-standalone .tc-chaos-event,
html.tc-standalone .tc-reveal,
html.tc-standalone .tc-reward-machine{
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  overflow:hidden!important;
}
html.tc-standalone .tc-chaos-event{padding:4px 8px!important}
html.tc-standalone .tc-reward-machine{padding:8px 14px!important;justify-content:center!important}
html.tc-standalone .tc-reveal{padding:0 2px!important}

/* The Weapons panel has ample vertical room on a phone. Give each Tarnished a
   full-width card instead of squeezing both assignments side-by-side. */
html.tc-standalone .tc-encounter-panel[data-panel="weapons"] .tc-loadouts{
  grid-template-columns:1fr!important;
}
html.tc-standalone .tc-encounter-panel[data-panel="weapons"] .tc-loadout + .tc-loadout{
  border-left:0!important;
  border-top:1px solid #54452b!important;
}
'''
if 'The three transient Covenant notices fit on the phone.' not in s:
    if marker not in s:
        raise SystemExit('iOS action CSS insertion marker missing')
    s = s.replace(marker, marker + extra, 1)
p.write_text(s)

# -----------------------------------------------------------------------------
# Durable source: refresh placement / instant restoration / tap guard.
# -----------------------------------------------------------------------------
p = tc / 'build-ledger-art-refresh-pairing.py'
s = p.read_text()
start = s.find('function tcPairEncounterRefreshes(){')
end = s.find('const tcRenderEncounterBeforeBoonPairing=renderEncounter;', start)
if start < 0 or end < 0:
    raise SystemExit('refresh pairing source block missing')
replacement = r'''function tcStablePanelTrack(track,tabs,count,getIndex,setIndex){
  const setActive=i=>tabs.querySelectorAll('button').forEach((b,j)=>b.classList.toggle('active',j===i));
  const go=i=>{i=Math.max(0,Math.min(count-1,i));setIndex(i);track.scrollTo({left:i*track.clientWidth,behavior:'smooth'});setActive(i);};
  tabs.querySelectorAll('button').forEach((b,i)=>b.addEventListener('click',()=>go(i)));
  let scrollTimer=null;
  track.addEventListener('scroll',()=>{clearTimeout(scrollTimer);scrollTimer=setTimeout(()=>{const i=Math.max(0,Math.min(count-1,Math.round(track.scrollLeft/Math.max(1,track.clientWidth))));setIndex(i);setActive(i);},70);},{passive:true});
  requestAnimationFrame(()=>{const prior=track.style.scrollBehavior;track.style.scrollBehavior='auto';const i=Math.max(0,Math.min(count-1,getIndex()));track.scrollLeft=i*track.clientWidth;setActive(i);requestAnimationFrame(()=>{track.style.scrollBehavior=prior;});});
}
if(typeof tcWirePanelTrack==='function')tcWirePanelTrack=tcStablePanelTrack;

function tcPairEncounterRefreshes(){
  const screen=app.querySelector('.tc-encounter-shell');if(!screen)return;
  const chaosBtn=screen.querySelector('[data-use-boon="chaos"]');
  const riteBtn=screen.querySelector('[data-use-boon="rite"]');
  const chaosPanel=screen.querySelector('.tc-encounter-panel[data-panel="chaos"]');
  const ritePanel=screen.querySelector('.tc-encounter-panel[data-panel="rite"]');
  const place=(btn,panel,label)=>{
    if(!btn||!panel)return;
    btn.type='button';
    const oldBox=btn.closest('.tc-panel-refresh');
    if(oldBox?.parentElement===panel)return;
    const box=document.createElement('div');box.className='tc-panel-refresh';box.innerHTML=`<div class="tc-kicker">${label}</div>`;box.appendChild(btn);panel.appendChild(box);
    if(oldBox&&!oldBox.querySelector('[data-use-boon]'))oldBox.remove();
  };
  place(chaosBtn,chaosPanel,'Chaos reserve');
  place(riteBtn,ritePanel,'Rite reserve');
  screen.querySelectorAll('.tc-earned-refreshes').forEach(node=>{if(!node.querySelector('[data-use-boon]'))node.remove();});
}

if(typeof useCovenantBoon==='function'&&!window.__tcBoonStabilized){
  window.__tcBoonStabilized=true;
  const tcUseCovenantBoonBeforePairing=useCovenantBoon;
  useCovenantBoon=async function(kind){
    if(window.__tcBoonBusy)return;
    window.__tcBoonBusy=true;
    try{return await tcUseCovenantBoonBeforePairing(kind);}
    finally{window.__tcBoonBusy=false;}
  };
}
'''
s = s[:start] + replacement + s[end:]
p.write_text(s)

# -----------------------------------------------------------------------------
# Current deployed HTML: apply the same corrections directly to the historical
# baseline instead of rebuilding the entire modern pipeline around it.
# -----------------------------------------------------------------------------
p = tc / 'index.html'
s = p.read_text()
if 'margin-bottom:22px!important' not in s and 'margin-bottom:88px!important' not in s:
    raise SystemExit('generated Encounter action margin target missing')
s = s.replace('margin-bottom:22px!important', 'margin-bottom:88px!important')

css = r'''
/* --- Standalone fixed notices + Encounter phone polish --- */
html.tc-standalone:has(.tc-chaos-event),
html.tc-standalone:has(.tc-reveal),
html.tc-standalone:has(.tc-reward-machine),
html.tc-standalone body:has(.tc-chaos-event),
html.tc-standalone body:has(.tc-reveal),
html.tc-standalone body:has(.tc-reward-machine){height:100%!important;overflow:hidden!important}
html.tc-standalone body:has(.tc-chaos-event) .app-shell,
html.tc-standalone body:has(.tc-reveal) .app-shell{
  height:calc(100vh - env(safe-area-inset-top))!important;
  max-height:calc(100vh - env(safe-area-inset-top))!important;
  overflow:hidden!important;
  padding:8px 14px calc(70px + env(safe-area-inset-bottom))!important;
}
html.tc-standalone body:has(.tc-reward-machine) .app-shell{
  height:calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom))!important;
  max-height:calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom))!important;
  overflow:hidden!important;
  padding:6px 14px!important;
}
html.tc-standalone .tc-chaos-event,
html.tc-standalone .tc-reveal,
html.tc-standalone .tc-reward-machine{height:100%!important;min-height:0!important;max-height:100%!important;overflow:hidden!important}
html.tc-standalone .tc-chaos-event{padding:4px 8px!important}
html.tc-standalone .tc-reward-machine{padding:8px 14px!important;justify-content:center!important}
html.tc-standalone .tc-reveal{padding:0 2px!important}
html.tc-standalone .tc-encounter-panel[data-panel="weapons"] .tc-loadouts{grid-template-columns:1fr!important}
html.tc-standalone .tc-encounter-panel[data-panel="weapons"] .tc-loadout + .tc-loadout{border-left:0!important;border-top:1px solid #54452b!important}
'''
if 'Standalone fixed notices + Encounter phone polish' not in s:
    if '</style>' not in s:
        raise SystemExit('generated style end missing')
    s = s.replace('</style>', css + '\n</style>', 1)

js = r'''
/* --- Encounter interaction stabilization --- */
function tcStablePanelTrack(track,tabs,count,getIndex,setIndex){
  const setActive=i=>tabs.querySelectorAll('button').forEach((b,j)=>b.classList.toggle('active',j===i));
  const go=i=>{i=Math.max(0,Math.min(count-1,i));setIndex(i);track.scrollTo({left:i*track.clientWidth,behavior:'smooth'});setActive(i);};
  tabs.querySelectorAll('button').forEach((b,i)=>b.addEventListener('click',()=>go(i)));
  let scrollTimer=null;
  track.addEventListener('scroll',()=>{clearTimeout(scrollTimer);scrollTimer=setTimeout(()=>{const i=Math.max(0,Math.min(count-1,Math.round(track.scrollLeft/Math.max(1,track.clientWidth))));setIndex(i);setActive(i);},70);},{passive:true});
  requestAnimationFrame(()=>{const prior=track.style.scrollBehavior;track.style.scrollBehavior='auto';const i=Math.max(0,Math.min(count-1,getIndex()));track.scrollLeft=i*track.clientWidth;setActive(i);requestAnimationFrame(()=>{track.style.scrollBehavior=prior;});});
}
if(typeof tcWirePanelTrack==='function')tcWirePanelTrack=tcStablePanelTrack;

function tcRepairEncounterRefreshes(){
  const screen=app.querySelector('.tc-encounter-shell');if(!screen)return;
  const chaosBtn=screen.querySelector('[data-use-boon="chaos"]');
  const riteBtn=screen.querySelector('[data-use-boon="rite"]');
  const chaosPanel=screen.querySelector('.tc-encounter-panel[data-panel="chaos"]');
  const ritePanel=screen.querySelector('.tc-encounter-panel[data-panel="rite"]');
  const place=(btn,panel,label)=>{
    if(!btn||!panel)return;
    btn.type='button';
    const oldBox=btn.closest('.tc-panel-refresh');
    if(oldBox?.parentElement===panel)return;
    const box=document.createElement('div');box.className='tc-panel-refresh';box.innerHTML=`<div class="tc-kicker">${label}</div>`;box.appendChild(btn);panel.appendChild(box);
    if(oldBox&&!oldBox.querySelector('[data-use-boon]'))oldBox.remove();
  };
  place(chaosBtn,chaosPanel,'Chaos reserve');
  place(riteBtn,ritePanel,'Rite reserve');
  screen.querySelectorAll('.tc-earned-refreshes').forEach(node=>{if(!node.querySelector('[data-use-boon]'))node.remove();});
}
const tcRenderEncounterBeforeInteractionStabilization=renderEncounter;
renderEncounter=function(){tcRenderEncounterBeforeInteractionStabilization();tcRepairEncounterRefreshes();};

if(typeof useCovenantBoon==='function'&&!window.__tcBoonStabilized){
  window.__tcBoonStabilized=true;
  const tcUseCovenantBoonBeforeInteractionStabilization=useCovenantBoon;
  useCovenantBoon=async function(kind){if(window.__tcBoonBusy)return;window.__tcBoonBusy=true;try{return await tcUseCovenantBoonBeforeInteractionStabilization(kind);}finally{window.__tcBoonBusy=false;}};
}
'''
if 'Encounter interaction stabilization' not in s:
    idx = s.rfind('</script>')
    if idx < 0:
        raise SystemExit('generated script end missing')
    s = s[:idx] + js + '\n' + s[idx:]
p.write_text(s)

# Focused invariants.
checks = {
    'index.html': [
        'margin-bottom:88px!important',
        'Standalone fixed notices + Encounter phone polish',
        'tc-encounter-panel[data-panel="weapons"] .tc-loadouts',
        'function tcStablePanelTrack',
        'function tcRepairEncounterRefreshes',
        '__tcBoonBusy',
    ],
    'build-ios-standalone-shell.py': [
        'margin-bottom:88px!important',
        'The three transient Covenant notices fit on the phone.',
    ],
    'build-ledger-art-refresh-pairing.py': [
        'function tcStablePanelTrack',
        '__tcBoonBusy',
        "place(chaosBtn,chaosPanel,'Chaos reserve')",
    ],
}
for name, needles in checks.items():
    text=(tc/name).read_text()
    for needle in needles:
        if needle not in text:
            raise SystemExit(f'{name} invariant missing: {needle}')
