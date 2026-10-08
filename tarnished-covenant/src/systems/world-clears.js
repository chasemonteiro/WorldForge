/* --- Co-op dual-world clears + shared reward reveal --- */
function tcWorldClears(encounter){
  const source=Array.isArray(encounter?.worldClears)?encounter.worldClears:[];
  return Array.from(new Set(source.filter(x=>x==='chase'||x==='morgan')));
}
function tcBothWorldsCleared(encounter){return tcWorldClears(encounter).length===2;}
function tcSharedRewardSeenBy(state,identity=playerName()){
  const seen=Array.isArray(state?.sharedRewardReveal?.seenBy)?state.sharedRewardReveal.seenBy:[];
  return seen.includes(identity);
}
function tcSharedRewardUnresolved(state){
  const reward=state?.sharedRewardReveal;
  return Boolean(reward?.id&&Array.isArray(reward.rewards)&&reward.rewards.length);
}
function tcBindCoopWorldClearControls(state,c){
  const original=document.querySelector('#complete');
  if(!original||!c)return;
  const clears=tcWorldClears(c),unresolved=tcSharedRewardUnresolved(state);
  const card=document.createElement('div');
  card.className='tc-world-clear-card';
  const buttons=['chase','morgan'].map(slot=>{
    const done=clears.includes(slot),label=playerLabel(slot,state);
    return `<button type="button" class="btn tc-world-clear-btn ${done?'done':''}" data-world-clear="${slot}" ${done||unresolved?'disabled':''}>${done?`${h(label)}’s World Cleared`:`Defeated in ${h(label)}’s World`}</button>`;
  }).join('');
  card.innerHTML=`<div class="tc-world-clear-head"><div><strong>Clear Both Worlds</strong><div class="tc-world-clear-note">One Covenant encounter · two host-world victories · one reward payout.</div></div><span class="tc-world-clear-count">${clears.length} / 2</span></div><div class="tc-world-clear-grid">${buttons}</div>${unresolved?'<div class="tc-world-clear-wait">Both Tarnished must review the previous Covenant reward before another victory can be recorded.</div>':clears.length===1?'<div class="tc-world-clear-wait">One world remains. Rewards wait until both clears are recorded.</div>':''}`;
  original.replaceWith(card);
  card.querySelectorAll('[data-world-clear]').forEach(btn=>btn.addEventListener('click',()=>tcRecordWorldClear(btn.dataset.worldClear)));
}
let tcWorldClearBusy=false;
async function tcRecordWorldClear(slot){
  if(tcWorldClearBusy||pending)return;
  const state=run?.state,c=state?.current;
  if(!c||!['chase','morgan'].includes(slot))return;
  if(tcSharedRewardDrawPending(state)||tcSharedRewardUnresolved(state))return setToast('Finish the previous shared Covenant reward first.');
  const clears=tcWorldClears(c);
  if(clears.includes(slot))return;
  tcWorldClearBusy=true;
  const next=structuredClone(state);
  next.current.worldClears=[...clears,slot];
  const count=next.current.worldClears.length;
  next.lastAction=`${playerLabel(slot,next)}’s world cleared against ${c.target?.name||'the target'} · ${count}/2.`;
  next.updatedAt=new Date().toISOString();
  try{
    await commit(next,{successToast:count===2?'Both worlds cleared. File one Covenant battle report.':'World clear recorded · 1 of 2. Rewards remain sealed.'});
  }finally{tcWorldClearBusy=false;}
}
function tcHydrateSharedRewardReveal(state){
  const shared=state?.sharedRewardReveal;
  if(!tcSharedRewardUnresolved(state)){
    if(pendingRewardReveal?.sharedId)pendingRewardReveal=null;
    return;
  }
  const me=playerName();
  if(tcSharedRewardSeenBy(state,me)){
    if(pendingRewardReveal?.sharedId===shared.id)pendingRewardReveal=null;
    return;
  }
  if(!pendingRewardReveal||pendingRewardReveal.sharedId!==shared.id){
    pendingRewardReveal={
      sharedId:shared.id,
      rewards:structuredClone(shared.rewards),
      boss:shared.boss||'Enemy Felled',
      index:0,
      spinning:true
    };
  }
}
function tcBuildSharedRewardAck(latest,rewardId,identity){
  const shared=latest?.sharedRewardReveal;
  if(!shared||shared.id!==rewardId)return null;
  const seen=Array.from(new Set([...(Array.isArray(shared.seenBy)?shared.seenBy:[]),identity]));
  if((shared.seenBy||[]).includes(identity))return null;
  const next=structuredClone(latest);
  // Two different phones have seen it. Identities other than Chase/Morgan (an
  // old 'Tarnished' join) must not leave the reveal, and the world clears it
  // gates, stuck forever.
  if(['Chase','Morgan'].every(name=>seen.includes(name))||seen.length>=2)next.sharedRewardReveal=null;
  else next.sharedRewardReveal={...structuredClone(shared),seenBy:seen};
  next.updatedAt=new Date().toISOString();
  return next;
}
let tcSharedRewardAckBusy=false;
async function tcAcknowledgeSharedRewardReveal(data){
  if(tcSharedRewardAckBusy)return;
  const rewardId=data?.sharedId||run?.state?.sharedRewardReveal?.id;
  if(!rewardId){pendingRewardReveal=null;return renderRun();}
  const me=playerName();
  const staged=tcBuildSharedRewardAck(run.state,rewardId,me);
  pendingRewardReveal=null;
  if(!staged)return renderRun();
  tcSharedRewardAckBusy=true;
  try{
    await commit(staged,{
      successToast:'Covenant reward acknowledged.',
      retryBuilder:(latest)=>tcBuildSharedRewardAck(latest,rewardId,me)
    });
  }finally{tcSharedRewardAckBusy=false;}
}

const tcRenderRunBeforeCoopWorlds=renderRun;
renderRun=function(){
  const state=run?.state;
  if(state)tcHydrateSharedRewardReveal(state);
  const c=state?.current;
  if(c&&!state?.regionComplete&&!state?.runComplete){
    if(tcBothWorldsCleared(c)){
      if(!postBattleReport||postBattleReport.encounterId!==c.id)postBattleReport={encounterId:c.id,rite:null,chaos:null};
    }else if(postBattleReport?.encounterId===c.id){
      postBattleReport=null;
    }
  }
  const rendered=tcRenderRunBeforeCoopWorlds();
  /* The modern Encounter enhancer has now finished and #complete has been moved
     into its final action area. Replace it only now, never before enhancement. */
  if(!postBattleReport&&!pendingRewardReveal)tcBindCoopWorldClearControls(run?.state,run?.state?.current);
  return rendered;
};
/* --- End co-op dual-world clears + shared reward reveal --- */