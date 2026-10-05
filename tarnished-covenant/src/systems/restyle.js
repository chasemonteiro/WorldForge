/* --- Covenant restyle: presentation-only markup adjustments ---------------
   Everything here changes how existing screens are labelled or arranged.
   Nothing reads from or writes to the saved run, and no handler, ID or
   data-* hook used by gameplay is removed. Styling lives in src/theme.css. */

// Bottom navigation: short labels, decorative glyphs hidden from screen readers.
const tcNavMarkupBeforeRestyle=navMarkup;
navMarkup=function(active){
  return tcNavMarkupBeforeRestyle(active)
    .replace('<nav class="tc-bottom-nav">','<nav class="tc-bottom-nav" aria-label="Main">')
    .replace('<span>Site of Grace</span>','<span>Grace</span>')
    .replace(/<span class="nicon">/g,'<span class="nicon" aria-hidden="true">');
};
// Ledger · Progress: each Remembrance shows where it is and whether that region
// is reachable yet. Read-only: uses the same helpers the travel screen uses.
function tcRemembranceStatus(state,name){
  if(hasRemembrance(state,name))return {key:'done',label:'claimed'};
  const region=REMEMBRANCE_REGION[name]||'';
  if(region&&state?.region===region)return {key:'here',label:'this region'};
  let open=false;try{open=Boolean(region&&regionUnlocked(state,region));}catch(_){open=false;}
  return open?{key:'open',label:'open'}:{key:'locked',label:'locked'};
}
remembranceLedgerBody=function(state){
  const req=requiredRemembrances(state),done=req.filter(x=>hasRemembrance(state,x));
  const regionNames=Object.keys(regions).filter(r=>state.includeDlc||!r.includes('· DLC')).filter(r=>r!=='The Erdtree');
  const ticks=req.map(name=>`<span class="${hasRemembrance(state,name)?'on':''}"></span>`).join('');
  const rows=req.map(name=>{const st=tcRemembranceStatus(state,name);return `<div class="tc-rem ${st.key==='done'?'done':''} tc-rem-${st.key}" role="listitem"><i class="tc-rem-mark" aria-hidden="true"></i><span class="tc-rem-name">${h(name)}<small>${h(REMEMBRANCE_REGION[name]||'')}</small></span><span class="stamp">${h(st.label)}</span></div>`;}).join('');
  return `<div class="tc-ledger-head"><div class="tc-ledger-count">${done.length}</div><div><div class="tc-ledger-of">of ${req.length} Remembrances</div><div class="tc-muted">The final seal opens only when the ledger is complete.</div></div></div>
    <div class="tc-rem-ticks" aria-hidden="true" style="grid-template-columns:repeat(${Math.max(1,req.length)},minmax(0,1fr))">${ticks}</div>
    <div class="tc-panel"><div class="tc-rem-grid" role="list">${rows}</div></div>
    <div class="tc-kicker gold" style="margin-top:20px">world progress</div><div class="tc-region-list">${regionNames.map(r=>`<div class="tc-region-chip ${(state.clearedRegions||[]).includes(r)?'done':''}">${h(r)}${r===state.region?' · ACTIVE':(state.clearedRegions||[]).includes(r)?' · CLEARED':''}</div>`).join('')}</div>`;
};

// Ledger · Smithing: boon counters become a tappable grid with a one-line
// explanation, replacing the long paragraph. Pure presentation; the counts
// and every redeem button come from the existing markup unchanged.
const TC_BOON_HELP=[
  [/^appeal waiver/i,'Optional to spend: makes one Weapon Appeal penalty-free.'],
  [/^chaos refresh/i,'Amend the current Chaos decree.'],
  [/^rite refresh/i,'Amend the current Odd Rite.'],
  [/^blank amendment/i,'Converts into either a Chaos or a Rite Refresh.'],
  [/^dynasty frequent flier/i,'Each grants 5 Mohgwyn bird-farming visits.'],
  [/^sanctioned boss kill/i,'Record one eligible optional boss in a reached region as killed.'],
  [/^covenant veto/i,'Veto an optional assignment, with the extra treasury payment shown.'],
  [/^letters? of clemency/i,'Strike one Weapon Appeal penalty from the current encounter.'],
  [/^union discount/i,'Your next Bell Bearing Contract costs 3 less Favor.'],
  [/^joint appeal/i,'Reroll both weapons without a penalty.']
];
let tcBoonHelpSelected='';
function tcBoonHelpText(label){const hit=TC_BOON_HELP.find(([re])=>re.test(label));return hit?hit[1]:'';}
function tcEnhanceBoonGrid(){
  const ledger=document.querySelector('.tc-ledger-screen .tc-boon-ledger');
  const grid=ledger?.querySelector('.tc-boon-grid');
  if(!grid||grid.dataset.tcHelp)return;
  grid.dataset.tcHelp='1';
  const cells=[...grid.children].filter(el=>el.tagName==='DIV');
  let preferred=null;
  cells.forEach(cell=>{
    const label=cell.querySelector('span')?.textContent?.trim()||'';
    const count=Number(cell.querySelector('strong')?.textContent||0);
    const btn=document.createElement('button');
    btn.type='button';btn.className='tc-boon-cell'+(count>0?' held':'');
    btn.dataset.boonHelp=label;btn.setAttribute('aria-pressed','false');
    btn.innerHTML=cell.innerHTML;
    cell.replaceWith(btn);
    if(label===tcBoonHelpSelected)preferred=btn;
    if(!preferred&&count>0)preferred=btn;
  });
  const note=document.createElement('p');note.className='tc-boon-help';note.setAttribute('aria-live','polite');
  grid.after(note);
  const longCopy=[...ledger.children].filter(el=>el.classList.contains('tc-muted')).at(-1);
  if(longCopy){
    const suffix=(longCopy.textContent.split(' · ').slice(1).join(' · ')||'').trim();
    longCopy.hidden=true;
    if(suffix){const extra=document.createElement('p');extra.className='tc-boon-extra';extra.textContent=suffix;note.after(extra);}
  }
  tcSelectBoonHelp(preferred||grid.querySelector('.tc-boon-cell'));
}
function tcSelectBoonHelp(btn){
  if(!btn)return;
  const grid=btn.closest('.tc-boon-grid'),note=grid?.nextElementSibling;
  grid?.querySelectorAll('.tc-boon-cell').forEach(b=>{const on=b===btn;b.classList.toggle('selected',on);b.setAttribute('aria-pressed',on?'true':'false');});
  tcBoonHelpSelected=btn.dataset.boonHelp||'';
  if(note?.classList.contains('tc-boon-help'))note.innerHTML=`<strong>${h(tcBoonHelpSelected)}</strong> · ${h(tcBoonHelpText(tcBoonHelpSelected))}`;
}
if(!window.__tcBoonHelpBound){
  window.__tcBoonHelpBound=true;
  document.addEventListener('click',event=>{const btn=event.target.closest?.('.tc-boon-cell');if(btn)tcSelectBoonHelp(btn);});
}
const tcRenderLedgerBeforeRestyle=renderLedger;
renderLedger=function(){
  tcRenderLedgerBeforeRestyle();
  try{tcEnhanceBoonGrid();}catch(error){console.warn('Boon grid presentation skipped',error);}
};
/* --- End Covenant restyle markup adjustments --- */
