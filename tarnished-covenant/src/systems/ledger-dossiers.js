/* --- Ledger: Dossiers (formerly Compendium) ---
   The case files, grouped into one chapter per region (newest first), each
   chapter under a strip of that region's painting. Rows are compact: date,
   boss, both weapons on one line, and a few marks. Tapping a row still opens
   the full evidence, which is lifted unchanged from the original dossier
   markup. Filter chips narrow to capstones, Chaos breaches or penalties. */
let tcDossierFilter='all';
function tcDossierEvidence(entry,index,state){
  const html=tcCompendiumDossierMarkup(entry,index,state);
  const cut=html.indexOf('</summary>');
  return cut<0?'':html.slice(cut+10).replace(/<\/details>\s*$/,'');
}
function tcDossierRow(entry,index,state){
  const names=compendiumNames(entry,state);
  const penalties=Array.isArray(entry?.penances)?entry.penances.length:0;
  const favor=Math.max(0,Number(entry?.favorEarned||0));
  const capstone=Boolean(entry?.exit),chaos=Boolean(entry?.chaosTriggered);
  const rite=entry?.riteOutcome==='Honored'?'honored':entry?.oddRite?'failed':'';
  const date=compendiumDate(entry?.completedAt);
  const weapons=[entry?.chaseWeapon,entry?.morganWeapon].filter(Boolean).map(w=>h(w)).join(' <i>&amp;</i> ');
  const marks=[
    capstone?'<span class="m cap" title="Capstone">♛</span>':'',
    chaos?'<span class="m chaos" title="Chaos broke loose">✶</span>':'',
    rite?`<span class="m rite ${rite}" title="Odd Rite ${rite}">${rite==='honored'?'◆':'◇'}</span>`:'',
    penalties?`<span class="m pen" title="${penalties} Appeal ${penalties===1?'penalty':'penalties'}">⚖${penalties}</span>`:'',
    favor?`<span class="m favor" title="Favor earned">+${favor}</span>`:''
  ].join('');
  return `<details class="tc-dossier-row ${capstone?'capstone':''}" ${capstone?'data-capstone':''} ${chaos?'data-chaos':''} ${penalties?'data-penalty':''}>
    <summary><span class="tc-dr-date">${h(date||'')}</span><span class="tc-dr-main"><strong>${h(entry?.name||'Unknown foe')}</strong><small>${weapons||'No weapons on record'}</small></span><span class="tc-dr-marks">${marks}</span></summary>
    <div class="tc-dr-evidence">${typeof tcDossierRemark==='function'?tcQuip(tcDossierRemark(entry),'tc-dossier-remark'):''}${tcDossierEvidence(entry,index,state)}</div>
  </details>`;
}
function tcDossierChapters(state){
  const entries=Array.isArray(state?.history)?state.history:[];
  const order=[],groups=new Map();
  entries.forEach((entry,index)=>{const r=entry?.region||'Earlier records';if(!groups.has(r)){groups.set(r,[]);order.push(r);}groups.get(r).push({entry,index});});
  return order.map((region,i)=>{
    const rows=groups.get(region),chaos=rows.filter(x=>x.entry?.chaosTriggered).length,cap=rows.find(x=>x.entry?.exit);
    const art=regions?.[region]?actualRegionImage(region):'';
    const summary=[`${rows.length} ${rows.length===1?'fight':'fights'}`,`${chaos} Chaos`,cap?`capstone: ${cap.entry.name}`:''].filter(Boolean).join(', ');
    return `<details class="tc-chapter" ${i===0?'open':''}><summary class="tc-chapter-head" style="${art?`--tc-chapter-art:url('${art}')`:''}"><strong>${h(region.replace(/ · DLC$/,''))}</strong><span>${h(summary)}</span></summary>
      <div class="tc-chapter-rows">${rows.map(x=>tcDossierRow(x.entry,x.index,state)).join('')}</div></details>`;
  }).join('');
}
compendiumLedgerMarkup=function(state){
  const entries=Array.isArray(state?.history)?state.history:[];
  if(!entries.length)return `<div class="tc-archive-empty"><div class="tc-archive-empty-seal">◇</div><div class="tc-value">No case files yet.</div><div class="tc-muted">Your first recorded victory opens one here.</div>${typeof tcQuip==='function'?tcQuip('The clerk sharpens a quill.'):''}</div>`;
  const chaos=entries.filter(x=>x?.chaosTriggered).length,caps=entries.filter(x=>x?.exit).length,pen=entries.filter(x=>x?.penances?.length).length;
  const favor=entries.reduce((sum,x)=>sum+Math.max(0,Number(x?.favorEarned||0)),0);
  const chip=(id,label,n)=>`<button type="button" class="tc-dossier-chip ${tcDossierFilter===id?'on':''}" data-dossier-filter="${id}">${label}${n!=null?` <b>${n}</b>`:''}</button>`;
  return `<div class="tc-dossiers" data-filter="${tcDossierFilter}">
    <div class="tc-dossier-tally"><span><b>${entries.length}</b>fights</span><span><b>${caps}</b>capstones</span><span><b>${chaos}</b>Chaos</span><span><b>${favor}</b>Favor</span></div>
    <div class="tc-dossier-chips">${chip('all','All')}${chip('capstone','Capstones',caps)}${chip('chaos','Chaos',chaos)}${chip('penalty','Penalties',pen)}</div>
    <p class="tc-dossier-legend"><span class="m cap">♛</span> capstone <span class="m chaos">✶</span> Chaos broke <span class="m rite honored">◆</span> Rite honored <span class="m pen">⚖</span> penalties</p>
    ${tcDossierChapters(state)}
  </div>`;
};
function tcApplyDossierFilter(root){
  if(!root)return;
  root.dataset.filter=tcDossierFilter;
  root.querySelectorAll('.tc-dossier-chip').forEach(c=>c.classList.toggle('on',c.dataset.dossierFilter===tcDossierFilter));
  root.querySelectorAll('.tc-chapter').forEach((chapter,i)=>{
    const rows=[...chapter.querySelectorAll('.tc-dossier-row')];
    const hits=tcDossierFilter==='all'?rows.length:rows.filter(r=>r.hasAttribute('data-'+tcDossierFilter)).length;
    chapter.hidden=!hits;
    if(tcDossierFilter!=='all')chapter.open=true;else chapter.open=i===0;
  });
}
document.addEventListener('click',event=>{
  const chip=event.target.closest('[data-dossier-filter]');if(!chip)return;
  event.preventDefault();tcDossierFilter=chip.dataset.dossierFilter;tcApplyDossierFilter(chip.closest('.tc-dossiers'));
});
const tcRenderLedgerBeforeDossiers=renderLedger;
renderLedger=function(){tcRenderLedgerBeforeDossiers();try{tcApplyDossierFilter(app.querySelector('.tc-dossiers'));}catch(error){console.warn('Dossier filter skipped',error);}};
/* --- End Dossiers --- */
