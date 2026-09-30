from pathlib import Path

p=Path('tarnished-covenant/index.html')
s=p.read_text()

css=r'''
/* --- Encounter boon pairing + illustrated remembrance ledger --- */
.tc-panel-refresh{margin:12px 0 2px;padding:11px 10px;border-top:1px solid var(--line-soft);border-bottom:1px solid var(--line-soft);background:rgba(10,9,7,.46)}
.tc-panel-refresh .tc-kicker{margin-bottom:8px}.tc-panel-refresh .btn{width:100%}
.tc-rem-hero{position:relative;isolation:isolate;overflow:hidden;min-height:132px;margin:8px 0 14px;padding:16px;display:flex;align-items:flex-end;border:1px solid rgba(198,161,90,.28);background:#0b0a08}
.tc-rem-hero:before{content:"";position:absolute;z-index:-2;inset:0;background-image:var(--tc-ledger-art);background-size:cover;background-position:center 42%;opacity:.42;filter:saturate(.76) contrast(1.05)}
.tc-rem-hero:after{content:"";position:absolute;z-index:-1;inset:0;background:linear-gradient(180deg,rgba(5,5,4,.08),rgba(5,5,4,.35) 42%,rgba(5,5,4,.96))}
.tc-rem-hero-copy{max-width:82%}.tc-rem-hero-title{font:400 clamp(25px,7vw,34px)/1 Georgia,serif;color:var(--ink);margin-top:5px}.tc-rem-hero-sub{font:italic 12px/1.35 Georgia,serif;color:#b9af9e;margin-top:5px}
.tc-rem-grid.illustrated{gap:7px}.tc-rem.illustrated{position:relative;isolation:isolate;overflow:hidden;min-height:76px;padding:12px 11px;align-items:center;border:1px solid var(--line-soft);background:#0b0a08}
.tc-rem.illustrated:before{content:"";position:absolute;z-index:-2;inset:0;background-image:var(--tc-rem-art);background-size:cover;background-position:center;opacity:.19;filter:saturate(.65) contrast(1.08)}
.tc-rem.illustrated:after{content:"";position:absolute;z-index:-1;inset:0;background:linear-gradient(90deg,rgba(7,7,5,.98) 0%,rgba(7,7,5,.83) 64%,rgba(7,7,5,.55) 100%)}
.tc-rem.illustrated.done:before{opacity:.31}.tc-rem-name{font:400 17px/1.12 Georgia,serif;color:var(--ink);max-width:78%}.tc-rem.illustrated.done .tc-rem-name{color:#dfc985}
.tc-region-list.illustrated{grid-template-columns:1fr}.tc-region-chip.illustrated{position:relative;isolation:isolate;overflow:hidden;min-height:62px;padding:11px 12px;display:flex;align-items:end;font:400 15px/1.15 Georgia,serif;color:#b9af9e;background:#0b0a08}
.tc-region-chip.illustrated:before{content:"";position:absolute;z-index:-2;inset:0;background-image:var(--tc-region-art);background-size:cover;background-position:center;opacity:.18;filter:saturate(.65)}
.tc-region-chip.illustrated:after{content:"";position:absolute;z-index:-1;inset:0;background:linear-gradient(90deg,rgba(7,7,5,.96),rgba(7,7,5,.63))}.tc-region-chip.illustrated.done{color:var(--gold-bright);border-color:rgba(198,161,90,.30)}
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
function tcStablePanelTrack(track,tabs,count,getIndex,setIndex){
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
const tcRenderEncounterBeforeBoonPairing=renderEncounter;
renderEncounter=function(){tcRenderEncounterBeforeBoonPairing();tcPairEncounterRefreshes();};

function tcLedgerArtForRegion(region){return typeof actualRegionImage==='function'?actualRegionImage(region||run?.state?.region):'';}
function tcLedgerArtForRemembrance(name,state){return tcLedgerArtForRegion(REMEMBRANCE_REGION?.[name]||state?.region);}
remembranceLedgerBody=function(state){
  const req=requiredRemembrances(state),done=req.filter(x=>hasRemembrance(state,x));
  const regionNames=Object.keys(regions).filter(r=>state.includeDlc||!r.includes('· DLC')).filter(r=>r!=='The Erdtree');
  const heroArt=tcLedgerArtForRegion(state.region);
  return `<div class="tc-rem-hero" style="--tc-ledger-art:url('${heroArt}')"><div class="tc-rem-hero-copy"><div class="tc-kicker gold">remembrance ledger</div><div class="tc-rem-hero-title">${done.length} of ${req.length} claimed</div><div class="tc-rem-hero-sub">The dead are filed by region. The final seal opens when the archive is complete.</div></div></div>
    <div class="tc-rem-grid illustrated">${req.map(name=>{const claimed=hasRemembrance(state,name),art=tcLedgerArtForRemembrance(name,state);return `<div class="tc-rem illustrated ${claimed?'done':''}" style="--tc-rem-art:url('${art}')"><span class="tc-rem-name">${h(name)}</span><span class="stamp">${claimed?'claimed':'missing'}</span></div>`}).join('')}</div>
    <div class="tc-kicker gold" style="margin-top:20px">world progress</div><div class="tc-region-list illustrated">${regionNames.map(r=>{const cleared=(state.clearedRegions||[]).includes(r);return `<div class="tc-region-chip illustrated ${cleared?'done':''}" style="--tc-region-art:url('${tcLedgerArtForRegion(r)}')">${h(r)}${r===state.region?' · ACTIVE':cleared?' · CLEARED':''}</div>`}).join('')}</div>`;
};
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in ['tcPairEncounterRefreshes','Chaos reserve','Rite reserve','tc-rem-hero','tcLedgerArtForRemembrance','tc-region-chip illustrated']:
    if needle not in s: raise SystemExit('ledger/refresh polish invariant missing: '+needle)
p.write_text(s)
