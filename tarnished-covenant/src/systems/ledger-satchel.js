/* --- Ledger: the Satchel (formerly Smithing) ---
   Everything the Covenant holds, as one card per possession, grouped by where
   it is spent. Cards reuse the existing action hooks (data-use-*, data-blank-to,
   data-open-past-masterwork, data-masterwork-recall), so every spend still goes
   through the original builders and their guards. Presentation only. */
const TC_SATCHEL_SIGILS={
  veto:'<path d="M14 40l6-22 12 10 12-10 6 22z"/><path d="M12 12l40 40"/>',
  flier:'<path d="M10 34c10-2 16-10 22-20 4 10 10 16 22 18-10 2-16 8-22 16-4-8-12-12-22-14z"/><circle cx="32" cy="30" r="2"/>',
  blank:'<path d="M18 10h28v44H18z"/><path d="M24 20h16M24 28h10" opacity=".35"/>',
  writ:'<path d="M32 54V30"/><path d="M32 30c-12 0-18-8-14-16 6 4 10 2 14-6 4 8 8 10 14 6 4 8-2 16-14 16z"/>'
};
function tcSatchelSigil(id){
  const paths=(typeof TC_FORGE_SIGILS!=='undefined'&&TC_FORGE_SIGILS[id])||TC_SATCHEL_SIGILS[id]||'';
  return `<svg class="tc-forge-sigil" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${paths}</g></svg>`;
}
function tcSatchelItems(state){
  const sm=smithingData(state),c=state?.current,locked=typeof tcEncounterMutationLocked==='function'&&tcEncounterMutationLocked(state);
  const penalties=Array.isArray(c?.penances)?c.penances:[];
  const vetoReady=typeof tcBossVetoEligible==='function'&&tcBossVetoEligible(state)&&tcBossVetoAffordable(state);
  const writsLeft=typeof tcErdtreeClearedIds==='function'?`${tcErdtreeClearedIds(state).length} of ${TC_ERDTREE_TARGETS.length} Avatar sites done.`:'';
  const flier=typeof tcDynastyFlierRedemptions==='function'?tcDynastyFlierRedemptions(state).at(-1):null;
  const lockedWhy='Locked after the first world victory.';
  return [
    {id:'joint',where:'here',name:'Joint Appeal',count:sm.jointAppeals,line:'Reroll both weapons, no penalty.',actions:[{attr:'data-use-joint-appeal',label:'Reroll both weapons',why:!c?'No fight in progress.':locked?lockedWhy:''}]},
    {id:'veto',where:'here',name:'Covenant Veto',count:sm.bossVetoes,line:'Send this boss back and draw another. Costs 2 Favor and a Chaos or Rite Refresh.',actions:[{attr:'data-use-boss-veto',label:'Veto this boss',why:vetoReady?'':(typeof tcBossVetoEligible==='function'&&!tcBossVetoEligible(state))?'This boss can’t be vetoed.':'Needs 2 Favor and a Refresh.'}]},
    {id:'freeboss',where:'here',name:'Sanctioned Boss Kill',count:sm.freeBossKills,line:'Mark one optional boss as killed and drop it from future draws.',actions:[{attr:'data-use-free-boss-kill',label:'Choose a boss'}]},
    {id:'clemency',where:'here',name:'Letter of Clemency',count:sm.clemencies,line:'Strike one Appeal penalty from this fight.',actions:[{attr:'data-use-clemency',label:'Strike a penalty',why:locked?lockedWhy:penalties.length?'':'No penalties to strike.'}]},
    {id:'blank',where:'here',name:'Blank Amendment',count:sm.blankAmendments,line:'Turn it into a Chaos or a Rite Refresh.',actions:[{attr:'data-blank-to="chaos"',label:'Make Chaos'},{attr:'data-blank-to="rite"',label:'Make Rite'}]},
    {id:'flier',where:'here',name:'Dynasty Frequent Flier',count:sm.aviaryTickets,line:flier?`Five bird-farming visits at Mohgwyn. Last used by ${personalizePlayers(flier.redeemedBy||'',state)}.`:'Five bird-farming visits at Mohgwyn.',actions:[{attr:'data-use-dynasty-flier',label:'Redeem 5 visits'}]},
    {id:'writ',where:'here',name:'Erdtree Writ',count:sm.erdtreeWrits,line:`Claim a Minor Erdtree Avatar’s tears after you beat it. ${writsLeft}`,actions:[{attr:'data-use-erdtree-writ',label:'Choose an Avatar'}]},
    {id:'appeal',where:'fight',name:'Appeal Waiver',count:sm.appealWaivers,line:'Make a Weapon Appeal penalty-free. Offered when you appeal.',go:{panel:1,label:'Go to Weapons'}},
    {id:'chaos',where:'fight',name:'Chaos Refresh',count:sm.chaosRefreshes,line:'Rewrite the Chaos decree before it breaks loose.',go:{panel:2,label:'Go to Chaos'}},
    {id:'rite',where:'fight',name:'Rite Refresh',count:sm.riteRefreshes,line:'Rewrite the Odd Rite.',go:{panel:3,label:'Go to Rite'}}
  ];
}
function tcSatchelCard(item){
  const buttons=item.actions?item.actions.map(a=>`<button type="button" class="tc-satchel-act" ${a.attr} ${a.why?'disabled':''}>${h(a.label)}</button>`).join(''):`<button type="button" class="tc-satchel-act go" data-satchel-go="${item.go.panel}">${h(item.go.label)}</button>`;
  const why=(item.actions||[]).map(a=>a.why).find(Boolean);
  return `<div class="tc-satchel-card ${item.where}">
    <div class="tc-satchel-top"><span class="tc-forge-seal">${tcSatchelSigil(item.id)}<b>${item.count}</b></span><div><strong>${h(item.name)}</strong><p>${h(item.line)}</p></div></div>
    ${why?`<em>${h(why)}</em>`:''}
    <div class="tc-satchel-acts ${item.actions&&item.actions.length>1?'two':''}">${buttons}</div>
  </div>`;
}
function tcSatchelTrophies(state){
  const sm=smithingData(state),records=sm.masterworkRecalls||[],me=typeof tcMasterworkSlotForIdentity==='function'?tcMasterworkSlotForIdentity():'',c=state?.current;
  const locked=typeof tcEncounterMutationLocked==='function'&&tcEncounterMutationLocked(state);
  const named=new Set(records.map(r=>r.weapon));
  const legacy=(sm.masterworks||[]).filter(n=>!named.has(n)).map(n=>({weapon:n,legacy:true}));
  const all=[...records.filter(r=>!r.used),...records.filter(r=>r.used),...legacy];
  if(!all.length)return `<p class="tc-satchel-empty">No Masterworks yet. Every claimed bearing and every Masterwork Token buys one.</p>${typeof tcQuip==='function'?tcQuip('Hewg has nothing of yours worth keeping. Yet.'):''}`;
  return `<div class="tc-trophies">${all.map(r=>{
    if(r.legacy)return `<div class="tc-trophy retired"><span class="tc-trophy-mark">⚒</span><strong>${h(r.weapon)}</strong><small>An old Masterwork, kept for the record.</small></div>`;
    const isCurrent=String(c?.[r.owner]?.name||'')===r.weapon,canUse=Boolean(!r.used&&!locked&&c&&me===r.owner&&!isCurrent);
    const status=r.used?'Recalled and retired':isCurrent?'In hand this fight':locked?'Recall locked this fight':'Recall ready';
    return `<div class="tc-trophy ${r.used?'retired':isCurrent?'current':'ready'}"><span class="tc-trophy-mark">⚒</span><strong>${h(r.weapon)}</strong><small>${h(playerLabel(r.owner,state))} · ${h(status)}</small>${canUse?`<button type="button" class="tc-satchel-act" data-masterwork-recall="${h(r.id)}" data-owner="${r.owner}">Recall it</button>`:''}</div>`;
  }).join('')}</div>`;
}
function tcSatchelMarkup(state){
  const sm=smithingData(state),items=tcSatchelItems(state);
  const held=items.filter(i=>i.count>0),empty=items.filter(i=>!i.count);
  const here=held.filter(i=>i.where==='here'),fight=held.filter(i=>i.where==='fight');
  return `<div class="tc-satchel">
    <button type="button" class="tc-satchel-purse" data-forge-open><span><b>✦</b>${sm.favor}<i>Smithing Favor</i></span><span class="tc-satchel-purse-go">${typeof tcShopOpen==="function"&&tcShopOpen(state)?"Spend at the Forge":"Visit the Forge"}</span></button>
    ${here.length?`<h4 class="tc-forge-h">Use it here</h4><div class="tc-satchel-grid">${here.map(tcSatchelCard).join('')}</div>`:''}
    ${fight.length?`<h4 class="tc-forge-h">Use it in the fight</h4><div class="tc-satchel-grid">${fight.map(tcSatchelCard).join('')}</div>`:''}
    ${empty.length?`<p class="tc-satchel-out">None held: ${empty.map(i=>h(i.name)).join(', ')}.</p>`:''}${!held.length&&typeof tcQuip==='function'?tcQuip('The satchel echoes.'):''}
    <h4 class="tc-forge-h">Masterworks</h4>
    <div class="tc-satchel-credits"><span><b>${sm.masterworkCredits}</b> ${sm.masterworkCredits===1?'credit':'credits'} to spend</span><button type="button" class="tc-satchel-act" data-open-past-masterwork ${sm.masterworkCredits>0?'':'disabled'}>Masterwork a past weapon</button></div>
    ${tcSatchelTrophies(state)}
  </div>`;
}
// The Satchel replaces the whole Smithing ledger body.
smithingLedgerMarkup=function(state){return tcSatchelMarkup(state);};
const TC_LEDGER_NAMES={remembrances:['Remembrances','Remembrances'],compendium:['Dossiers','Dossiers'],smithing:['Satchel','The Satchel']};
const tcRenderLedgerBeforeNames=renderLedger;
renderLedger=function(){
  tcRenderLedgerBeforeNames();
  try{
    app.querySelectorAll('[data-ledger-view]').forEach(btn=>{const n=TC_LEDGER_NAMES[btn.dataset.ledgerView];if(n)btn.textContent=n[0];});
    const title=app.querySelector('.tc-ledger-screen .tc-brand-small'),n=TC_LEDGER_NAMES[ledgerView];if(title&&n)title.textContent=n[1];
  }catch(error){console.warn('Ledger names skipped',error);}
};
document.addEventListener('click',event=>{
  const go=event.target.closest('[data-satchel-go]');if(!go)return;
  event.preventDefault();
  if(run?.state?.current){tcEncounterPanelId=run.state.current.id;tcEncounterPanelIndex=Number(go.dataset.satchelGo)||0;}
  uiScreen='encounter';pendingRevealId=null;renderRun();
});
/* --- End Satchel --- */
