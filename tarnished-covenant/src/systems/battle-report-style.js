/* --- Battle report in the Ledger/Forge style ---
   Same saved data and builders as battle-report.js (postBattleChoice,
   tcPostBattleMasterwork, finalizePostBattleReport); only the screen changes.
   "Masterwork Both" is gone: each weapon is Masterworked on its own, after a
   confirmation that names the weapon and the credit it costs. */
function tcReportQuestion(kind,title,name,text,draws,available,answer,labels){
  if(!available)return `<div class="tc-rq muted ${kind}"><div class="tc-rq-head"><span>${title}</span><em>Not triggered</em></div><p>${h(text)}</p></div>`;
  if(draws<=0)return `<div class="tc-rq muted ${kind}"><div class="tc-rq-head"><span>${title}</span><em>No reward this time</em></div>${name?`<strong>${h(name)}</strong>`:''}<p>${h(text)}</p></div>`;
  const seal=(value,label,cls)=>`<button type="button" class="tc-rq-seal ${cls} ${answer===value?'on':''}" data-report-kind="${kind}" data-report-value="${value?'1':'0'}" aria-pressed="${answer===value}"><span class="tc-rq-disc">${value?'✓':'✕'}</span>${label}</button>`;
  return `<div class="tc-rq ${kind} ${answer===null?'open':''}"><div class="tc-rq-head"><span>${title}</span><em>${draws} reward ${draws===1?'draw':'draws'} if ${labels[0].toLowerCase()}</em></div>${name?`<strong>${h(name)}</strong>`:''}<p>${h(text)}</p><div class="tc-rq-seals">${seal(true,labels[0],'yes')}${seal(false,labels[1],'no')}</div></div>`;
}
// chaosEventName picks a random name for unmatched decrees; the report re-renders
// on every answer, so pin the pick to the decree text to keep the name steady.
function tcStableChaosName(text){
  let hash=0;for(const ch of String(text||''))hash=((hash<<5)-hash+ch.charCodeAt(0))|0;
  const real=Math.random;Math.random=()=>(Math.abs(hash)%1000)/1000;
  try{return chaosEventName(String(text||''));}finally{Math.random=real;}
}
function tcReportWeaponCards(state){
  const sm=smithingData(state),c=state.current,credits=Number(sm.masterworkCredits||0);
  const cards=['chase','morgan'].map(slot=>{
    const name=c?.[slot]?.name||'',done=sm.masterworks.includes(name);
    const why=done?'Already a Masterwork':credits<1?'No credits left':'';
    return `<div class="tc-report-weapon"><span>${h(playerLabel(slot,state))}</span><strong>${h(name||'—')}</strong><em>${h(c?.[slot]?.role||'')}</em><button type="button" class="tc-satchel-act" data-report-mw="${slot}" ${why?'disabled':''}>${done?'⚒ Masterwork':'Masterwork this'}</button>${why&&!done?`<small>${h(why)}</small>`:''}</div>`;
  }).join('');
  return `<h4 class="tc-forge-h">Worth keeping?</h4><p class="tc-report-help">A Masterwork saves the weapon for one penalty-free Recall later. ${credits} ${credits===1?'credit':'credits'} left.</p><div class="tc-report-weapons">${cards}</div>`;
}
function tcConfirmReportMasterwork(slot){
  const state=run.state,c=state.current,sm=smithingData(state),name=c?.[slot]?.name;if(!name)return;
  const el=tcStrategicOverlay(`Masterwork ${name}?`,`<p>Spend 1 of your ${sm.masterworkCredits} Masterwork credits on ${h(playerLabel(slot,state))}’s ${h(name)}. You can Recall it once later, with no Appeal penalty.</p>`,`<button type="button" class="btn gold" data-confirm-mw>Spend 1 credit</button>`);
  el.querySelector('.tc-kicker').textContent='Hewg’s Workbench';
  el.querySelector('[data-confirm-mw]').addEventListener('click',async event=>{event.currentTarget.disabled=true;el.remove();await tcPostBattleMasterwork(slot);});
}
renderPostBattleReport=function(){
  const state=run.state,c=state.current;
  if(!c){postBattleReport=null;return renderRun();}
  const draft=tcSharedBattleReportDraft(state);
  postBattleReport=draft?{...draft}:{encounterId:c.id,rite:null,chaos:null};
  const riteDraws=Number(c.weirdness?.favor??1),chaosDraws=Number(c.chaosFavor??1);
  const chaosAvailable=Boolean(c.chaosTriggered);
  const riteReady=riteDraws<=0||postBattleReport.rite!==null;
  const chaosReady=!chaosAvailable||chaosDraws<=0||postBattleReport.chaos!==null;
  const reportReady=riteReady&&chaosReady;
  const preview=tcBattleReportAwardPreview(state,postBattleReport);
  const missing=[!riteReady?'the Rite':'',!chaosReady?'the Chaos decree':''].filter(Boolean).join(' and ');
  const who=postBattleReport.updatedBy?`Last answered by ${h(personalizePlayers(postBattleReport.updatedBy,state))}.`:'Either of you can file this.';
  const art=typeof actualBossImage==='function'?actualBossImage(c.target?.name,state.region):'';
  const credits=Number(smithingData(state).masterworkCredits||0);
  const guaranteedText='+1';
  app.innerHTML=`<section class="tc-battle-report tc-report-new">
    <div class="tc-report-banner" style="${art?`--tc-report-art:url('${art}')`:''}"><span>Victory</span><h2>${h(c.target?.name||'Enemy felled')}</h2><p>${who}</p></div>
    ${tcReportQuestion('rite','Odd Rite',c.weirdness?.name||'',c.weirdness?.text||'No Rite this fight.',riteDraws,true,postBattleReport.rite,['Honored','Broken'])}
    ${tcReportQuestion('chaos','Chaos',chaosAvailable?tcStableChaosName(c.chaosConsequence||''):'',chaosAvailable?personalizePlayers(c.chaosConsequence||'',state):'The seal never broke.',chaosDraws,chaosAvailable,postBattleReport.chaos,['Endured','Broken'])}
    <div class="tc-receipt"><h4>This fight pays</h4><div><span>Smithing Favor</span><b>${guaranteedText}</b></div><div><span>Reward draws${reportReady?'':' so far'}</span><b>${preview.draws}</b></div></div>
    ${credits>0?tcReportWeaponCards(state):''}
    <div class="tc-report-file"><button id="finishBattleReport" class="btn gold" ${reportReady?'':'disabled'}>${c.target?.exit?'File report and draw rewards':'File report, draw rewards and roll the next fight'}</button><p>${reportReady?'Filing pays the Favor and opens the reward.':`Answer ${missing} first.`}</p></div>
  </section>`;
  document.querySelectorAll('[data-report-kind]').forEach(btn=>btn.addEventListener('click',()=>postBattleChoice(btn.dataset.reportKind,btn.dataset.reportValue==='1')));
  document.querySelectorAll('[data-report-mw]').forEach(btn=>btn.addEventListener('click',()=>tcConfirmReportMasterwork(btn.dataset.reportMw)));
  document.querySelector('#finishBattleReport')?.addEventListener('click',finalizePostBattleReport);
};
/* --- End battle report style --- */
