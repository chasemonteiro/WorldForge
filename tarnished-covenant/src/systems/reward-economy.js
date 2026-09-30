/* --- Expanded Covenant reward economy --- */
function tcEffectiveSmithingContractCost(state,bearing){
  const base=smithingContractCost(bearing),sm=smithingData(state);
  return Math.max(0,base-(Number(sm.unionDiscounts||0)>0?3:0));
}

// Corporate affordability and commissioning understand the voucher immediately.
tcAffordableBellBearings=function(state){
  if(!state)return [];
  const sm=smithingData(state);
  return availableBellBearings(state).filter(b=>sm.favor>=tcEffectiveSmithingContractCost(state,b));
};
commissionSmithingContract=function(state){
  const source=typeof tcNormalizeRunState==='function'?tcNormalizeRunState(state):state;
  const sm=smithingData(source),pool=availableBellBearings(source);
  const affordable=pool.filter(b=>sm.favor>=tcEffectiveSmithingContractCost(source,b));
  if(!affordable.length)return null;
  const next=smithingCopy(source),b=pick(affordable),baseCost=smithingContractCost(b),cost=tcEffectiveSmithingContractCost(source,b),task=pick(TC_SMITHING_TASKS);
  const discounted=Number(next.smithing.unionDiscounts||0)>0&&cost<baseCost;
  next.smithing.favor-=cost;
  if(discounted)next.smithing.unionDiscounts=Math.max(0,Number(next.smithing.unionDiscounts||0)-1);
  next.smithing.pendingCorporateForEncounterId=null;
  next.smithing.activeContract={bearingId:b.id,task,status:'task',cost,baseCost,discountApplied:discounted?3:0,commissionedAt:new Date().toISOString()};
  next.lastAction=`A Bell Bearing Contract has been commissioned for ${b.name} for ${cost} Favor${discounted?' after a Union Discount Voucher':''}.`;
  return next;
};
renderCorporateContractNotice=function(){
  const state=typeof tcNormalizeRunState==='function'?tcNormalizeRunState(run.state):run.state,sm=smithingData(state),affordable=tcAffordableBellBearings(state),preview=affordable[0];
  if(!preview){renderRun();return;}
  const base=smithingContractCost(preview),cost=tcEffectiveSmithingContractCost(state,preview),discounted=cost<base;
  app.innerHTML=`<section class="tc-corporate-screen"><div class="tc-corporate-letter"><div class="tc-corporate-stamp">Action<br>Required</div><div class="tc-corporate-overline">Notice From Upper Management</div><h1>Corporate Has Forwarded A Matter</h1><div class="tc-corporate-copy">Your recent performance has attracted administrative attention. A Bell Bearing Contract is now mandatory before normal encounter scheduling may resume.</div><div class="tc-corporate-meta"><strong>${sm.favor} Smithing Favor on file</strong><br>${h(preview.region)} procurement is actionable · ${cost} Favor${discounted?` after Union Discount Voucher (${base} normally)`:''}.</div><button id="tcReviewMandatoryContract" class="btn gold">Review Mandatory Contract</button><div class="tc-corporate-foot">Hewg has been CC’d. This meeting could not have been an email.</div></div></section>`;
  document.querySelector('#tcReviewMandatoryContract')?.addEventListener('click',async()=>{
    const btn=document.querySelector('#tcReviewMandatoryContract');if(btn)btn.disabled=true;
    const next=commissionSmithingContract(run.state);
    if(!next){setToast('Corporate records changed. Rechecking the file.');renderRun();return;}
    const spent=next.smithing?.activeContract?.cost,discount=next.smithing?.activeContract?.discountApplied;
    const saved=await commit(next,{successToast:`Upper Management assigned a Bell Bearing Contract${spent!=null?` · ${spent} Favor spent`:''}${discount?' · voucher applied':''}.`});
    if(saved){if(typeof tcPendingRegionContractEncounterId!=='undefined')tcPendingRegionContractEncounterId=null;renderSmithingContract();}else renderRun();
  });
};
const tcSmithingHubBeforeExpandedRewards=smithingHubMarkup;
smithingHubMarkup=function(state){
  const html=tcSmithingHubBeforeExpandedRewards(state),sm=smithingData(state),available=availableBellBearings(state);
  if(!available.length)return html;
  const cost=Math.min(...available.map(b=>tcEffectiveSmithingContractCost(state,b)));
  let out=html.replace(/Next eligible contract: \d+ Favor\./,`Next eligible contract: ${cost} Favor${sm.unionDiscounts>0?' with Union Discount Voucher':''}.`);
  out=out.replace(/Eligible contracts cost 6–12 Favor depending on Bell Bearing tier\./,`Next eligible contract costs ${cost} Favor${sm.unionDiscounts>0?' after your Union Discount Voucher':''}.`);
  out=out.replace(/· \d+ Favor minimum\./,`· ${cost} Favor minimum${sm.unionDiscounts>0?' after voucher':''}.`);
  return out;
};

function tcStrategicOverlay(title,body,actions=''){
  document.querySelector('#tcStrategyOverlay')?.remove();
  const el=document.createElement('div');el.id='tcStrategyOverlay';el.className='tc-strategy-overlay';
  el.innerHTML=`<div class="tc-strategy-card"><div class="tc-kicker gold">Covenant Treasury</div><h2>${h(title)}</h2>${body}${actions}<button type="button" class="btn text-btn" data-close-strategy>Cancel</button></div>`;
  document.body.appendChild(el);el.addEventListener('click',e=>{if(e.target===el||e.target.closest('[data-close-strategy]'))el.remove();});
  return el;
}
function tcPenaltyKey(p){return [p?.name||'',p?.scope||'',p?.text||''].join('␟');}
function tcBuildClemency(latest,encounterId,key,actor){
  const sm=smithingData(latest),c=latest?.current;if(!c||c.id!==encounterId||Number(sm.clemencies||0)<1)return null;
  const list=Array.isArray(c.penances)?c.penances:[],index=list.findIndex(p=>tcPenaltyKey(p)===key);if(index<0)return null;
  const next=smithingCopy(latest),removed=next.current.penances.splice(index,1)[0];next.smithing.clemencies-=1;
  next.lastAction=`${actor} filed a Letter of Clemency. ${removed?.name||'One Appeal penalty'} was struck from the encounter.`;next.updatedAt=new Date().toISOString();return next;
}
function tcOpenClemency(){
  const state=run?.state,sm=smithingData(state||{}),c=state?.current,penances=Array.isArray(c?.penances)?c.penances:[];
  if(Number(sm.clemencies||0)<1)return setToast('No Letter of Clemency available.');if(!penances.length)return setToast('There is no Appeal penalty to erase.');
  const el=tcStrategicOverlay('Letter of Clemency',`<p>Strike one existing Weapon Appeal penalty from the current encounter. This does not reroll either weapon.</p><div class="tc-strategy-list">${penances.map((p,i)=>`<button type="button" class="tc-strategy-item" data-clemency-index="${i}"><strong>${h(p.name||'Appeal Penalty')}</strong><span>${h(p.text||p.scope||'Penalty on file')}</span></button>`).join('')}</div>`);
  el.querySelectorAll('[data-clemency-index]').forEach(btn=>btn.addEventListener('click',async()=>{const p=penances[Number(btn.dataset.clemencyIndex)];if(!p)return;const actor=playerName(),key=tcPenaltyKey(p),encounterId=c.id;const build=latest=>tcBuildClemency(latest,encounterId,key,actor),staged=build(run.state);if(!staged)return setToast('That penalty is no longer on file.');btn.disabled=true;const saved=await commit(staged,{successToast:'Letter of Clemency granted. Penalty erased.',retryBuilder:build});if(saved)el.remove();}));
}

function tcBuildBlankConversion(latest,kind,actor){
  const sm=smithingData(latest);if(Number(sm.blankAmendments||0)<1)return null;const next=smithingCopy(latest),key=kind==='chaos'?'chaosRefreshes':'riteRefreshes';next.smithing.blankAmendments-=1;next.smithing[key]=Number(next.smithing[key]||0)+1;next.lastAction=`${actor} converted a Blank Amendment into one ${kind==='chaos'?'Chaos':'Rite'} Refresh.`;next.updatedAt=new Date().toISOString();return next;
}
async function tcConvertBlankAmendment(kind){
  const actor=playerName(),build=latest=>tcBuildBlankConversion(latest,kind,actor),staged=build(run.state);if(!staged)return setToast('No Blank Amendment available.');await commit(staged,{successToast:`Blank Amendment converted to ${kind==='chaos'?'Chaos':'Rite'} Refresh.`,retryBuilder:build});
}

function tcBuildJointAppeal(latest,encounterId,oldChase,oldMorgan,newChase,newMorgan,actor){
  const sm=smithingData(latest),c=latest?.current;if(!c||c.id!==encounterId||Number(sm.jointAppeals||0)<1)return null;
  if(String(c.chase?.name||'')!==oldChase||String(c.morgan?.name||'')!==oldMorgan)return null;
  const next=smithingCopy(latest);next.current.chase=structuredClone(newChase);next.current.morgan=structuredClone(newMorgan);next.smithing.jointAppeals-=1;next.lastAction=`${actor} invoked a Joint Appeal. Both weapons were reassigned with no penalty.`;next.updatedAt=new Date().toISOString();return next;
}
function tcOpenJointAppeal(){
  const state=run?.state,sm=smithingData(state||{}),c=state?.current;if(Number(sm.jointAppeals||0)<1)return setToast('No Joint Appeal available.');if(!c)return;
  const el=tcStrategicOverlay('Joint Appeal',`<p>Reroll both assigned weapons once. No Appeal penalty is added, and no Appeal Waiver is consumed.</p><div class="tc-panel soft"><div class="tc-muted">Current assignments</div><div>${h(c.chase?.name||'—')} · ${h(c.morgan?.name||'—')}</div></div>`,`<div class="tc-strategy-actions"><button type="button" id="tcConfirmJoint" class="btn gold">Reroll Both · Spend 1</button><button type="button" class="btn ghost" data-close-strategy>Keep Weapons</button></div>`);
  el.querySelector('#tcConfirmJoint')?.addEventListener('click',async e=>{const actor=playerName(),encounterId=c.id,oldChase=String(c.chase?.name||''),oldMorgan=String(c.morgan?.name||'');const rolled=changeWeapons(run.state,actor,'both',false),newChase=structuredClone(rolled.current.chase),newMorgan=structuredClone(rolled.current.morgan);const build=latest=>tcBuildJointAppeal(latest,encounterId,oldChase,oldMorgan,newChase,newMorgan,actor),staged=build(run.state);if(!staged)return setToast('The current assignments changed on the other phone.');e.currentTarget.disabled=true;const saved=await commit(staged,{successToast:'Joint Appeal granted. Both weapons reassigned without penalty.',retryBuilder:build});if(saved)el.remove();});
}

function tcBossVetoEligible(state){
  const c=state?.current;if(!c?.target?.name||c.target.exit)return false;
  if(typeof tcIsProgressionGateBoss==='function'&&tcIsProgressionGateBoss(c.target.name))return false;
  if(Array.isArray(c.worldClears)&&c.worldClears.length)return false;
  return true;
}
function tcBossVetoAffordable(state){const sm=smithingData(state||{});return Number(sm.bossVetoes||0)>0&&Number(sm.favor||0)>=2&&(Number(sm.chaosRefreshes||0)>=1||Number(sm.riteRefreshes||0)>=1);}
function tcRollVetoReplacement(state){
  if(!tcBossVetoEligible(state))return null;const current=state.current.target.name,temp=structuredClone(state);temp.sanctionedBossKills=[...(temp.sanctionedBossKills||[]),{region:state.region,name:current,temporary:true}];
  for(let i=0;i<60;i++){const target=chooseTarget(temp);if(!target?.name||target.name===current||target.exit)continue;if(typeof tcIsProgressionGateBoss==='function'&&tcIsProgressionGateBoss(target.name))continue;return structuredClone(target);}return null;
}
function tcBuildBossVeto(latest,encounterId,oldBoss,replacement,actor,refreshKind){
  const refreshKey=refreshKind==='chaos'?'chaosRefreshes':refreshKind==='rite'?'riteRefreshes':null;if(!refreshKey||Number(smithingData(latest||{})[refreshKey]||0)<1)return null;
  if(!tcBossVetoEligible(latest)||!tcBossVetoAffordable(latest))return null;const c=latest.current;if(c.id!==encounterId||c.target.name!==oldBoss)return null;
  const next=smithingCopy(latest);next.smithing.bossVetoes-=1;next.smithing.favor-=2;next.smithing[refreshKey]-=1;next.current.target=structuredClone(replacement);next.current.worldClears=[];next.lastAction=`${actor} invoked a Covenant Veto. ${oldBoss} was reassigned to ${replacement.name}.`;next.updatedAt=new Date().toISOString();return next;
}
function tcOpenBossVeto(){
  const state=run?.state,sm=smithingData(state||{}),c=state?.current;if(Number(sm.bossVetoes||0)<1)return setToast('No Covenant Veto available.');
  if(!tcBossVetoEligible(state))return setToast('Required bosses, capstones, and partially cleared encounters cannot be vetoed.');
  const ready=tcBossVetoAffordable(state),el=tcStrategicOverlay('Covenant Veto',`<p>Reject <strong>${h(c.target.name)}</strong> and draw a different non-required boss from this region. Your current weapons, Rite, Chaos decree, and existing penalties stay in force.</p><div class="tc-panel soft"><div class="tc-kicker gold">Invocation cost</div><div class="tc-boon-recipe">1 Covenant Veto · 2 Smithing Favor · 1 Chaos OR Rite Refresh</div><div class="tc-muted" style="margin-top:8px">On file: ${sm.favor} Favor · ${sm.chaosRefreshes} Chaos · ${sm.riteRefreshes} Rite</div><label for="tcVetoRefresh">Refresh to spend</label><select id="tcVetoRefresh">${Number(sm.chaosRefreshes||0)>0?'<option value="chaos">Chaos Refresh</option>':''}${Number(sm.riteRefreshes||0)>0?'<option value="rite">Rite Refresh</option>':''}</select></div>`,`<div class="tc-strategy-actions"><button type="button" id="tcConfirmVeto" class="btn gold" ${ready?'':'disabled'}>Reject Boss · Pay Cost</button><button type="button" class="btn ghost" data-close-strategy>Keep Boss</button></div>`);
  el.querySelector('#tcConfirmVeto')?.addEventListener('click',async e=>{const replacement=tcRollVetoReplacement(run.state);if(!replacement)return setToast('No legal alternate boss is currently available.');const refreshKind=el.querySelector('#tcVetoRefresh').value,actor=playerName(),encounterId=c.id,oldBoss=c.target.name,build=latest=>tcBuildBossVeto(latest,encounterId,oldBoss,replacement,actor,refreshKind),staged=build(run.state);if(!staged)return setToast('The Veto cost or encounter changed on the other phone.');e.currentTarget.disabled=true;const saved=await commit(staged,{successToast:`Covenant Veto accepted · new target: ${replacement.name}.`,retryBuilder:build});if(saved)el.remove();});
}

// The expanded treasury stays in the Ledger rather than crowding every Encounter panel.
covenantBoonMarkup=function(state){
  const sm=smithingData(state),c=state?.current,penalties=Array.isArray(c?.penances)?c.penances:[],sanctioned=typeof tcSanctionedBossKills==='function'?tcSanctionedBossKills(state):[];
  const vetoReady=tcBossVetoEligible(state)&&tcBossVetoAffordable(state);
  return `<div class="tc-boon-ledger"><div class="tc-kicker ember">covenant boons</div><div class="tc-boon-grid tc-boon-grid-expanded">
    <div><strong>${sm.appealWaivers}</strong><span>Appeal Waiver${sm.appealWaivers===1?'':'s'}</span></div><div><strong>${sm.chaosRefreshes}</strong><span>Chaos Refresh${sm.chaosRefreshes===1?'':'es'}</span></div>
    <div><strong>${sm.riteRefreshes}</strong><span>Rite Refresh${sm.riteRefreshes===1?'':'es'}</span></div><div><strong>${sm.blankAmendments}</strong><span>Blank Amendment${sm.blankAmendments===1?'':'s'}</span></div>
    <div><strong>${sm.aviaryTickets}</strong><span>Dynasty Frequent Flier${sm.aviaryTickets===1?'':'s'}</span></div><div><strong>${sm.freeBossKills}</strong><span>Sanctioned Boss Kill${sm.freeBossKills===1?'':'s'}</span></div>
    <div><strong>${sm.bossVetoes}</strong><span>Covenant Veto${sm.bossVetoes===1?'':'es'}</span></div><div><strong>${sm.clemencies}</strong><span>Letter${sm.clemencies===1?'':'s'} of Clemency</span></div>
    <div><strong>${sm.unionDiscounts}</strong><span>Union Discount${sm.unionDiscounts===1?'':'s'}</span></div><div><strong>${sm.jointAppeals}</strong><span>Joint Appeal${sm.jointAppeals===1?'':'s'}</span></div>
  </div><div class="tc-boon-actions">
    ${sm.freeBossKills>0?`<button type="button" class="btn ghost small" data-use-free-boss-kill>Redeem Sanctioned Boss Kill · ${sm.freeBossKills}</button>`:''}
    ${sm.bossVetoes>0?`<button type="button" class="btn ghost small" data-use-boss-veto ${vetoReady?'':'disabled'}>Invoke Covenant Veto · ${sm.bossVetoes}</button>`:''}
    ${sm.clemencies>0?`<button type="button" class="btn ghost small" data-use-clemency ${penalties.length?'':'disabled'}>File Letter of Clemency · ${sm.clemencies}</button>`:''}
    ${sm.jointAppeals>0&&c?`<button type="button" class="btn ghost small" data-use-joint-appeal>Use Joint Appeal · ${sm.jointAppeals}</button>`:''}
    ${sm.blankAmendments>0?`<div class="tc-boon-actions two"><button type="button" class="btn ghost small" data-blank-to="chaos">Blank → Chaos · ${sm.blankAmendments}</button><button type="button" class="btn ghost small" data-blank-to="rite">Blank → Rite · ${sm.blankAmendments}</button></div>`:''}
  </div><div class="tc-muted">Appeal Waivers are optional to spend. Blank Amendments convert into either Refresh. Union Discounts automatically reduce the next Bell Bearing Contract by 3 Favor. Joint Appeals reroll both weapons without a penalty. Covenant Vetoes require the additional treasury payment shown above.${sanctioned.length?` · ${sanctioned.length} boss${sanctioned.length===1?' has':'es have'} been sanctioned.`:''}</div></div>`;
};

if(!window.__tcExpandedRewardBound){window.__tcExpandedRewardBound=true;document.addEventListener('click',e=>{if(e.target.closest('[data-use-boss-veto]'))tcOpenBossVeto();else if(e.target.closest('[data-use-clemency]'))tcOpenClemency();else if(e.target.closest('[data-use-joint-appeal]'))tcOpenJointAppeal();else{const blank=e.target.closest('[data-blank-to]');if(blank)void tcConvertBlankAmendment(blank.dataset.blankTo);}});}
/* --- End Expanded Covenant reward economy --- */