/* --- Synchronized shared reward reveal --- */
function tcSharedRewardIndex(shared){
  const total=Array.isArray(shared?.rewards)?shared.rewards.length:0;
  return Math.max(0,Math.min(Math.max(0,total-1),Number(shared?.revealIndex||0)));
}
function tcSharedRewardSeenList(shared){
  return Array.isArray(shared?.seenBy)?shared.seenBy:[];
}
function tcSharedRewardDrawerFinished(shared){
  return Boolean(shared?.drawnBy&&tcSharedRewardSeenList(shared).includes(shared.drawnBy));
}
function tcSharedRewardNeedsCatchup(shared,identity=playerName()){
  return Boolean(shared?.id&&tcSharedRewardDrawerFinished(shared)&&!tcSharedRewardSeenList(shared).includes(identity)&&!tcSharedRewardObservedAll(shared,identity));
}
function tcSharedRewardDrawerLabel(state){
  const who=String(state?.sharedRewardReveal?.drawnBy||'');
  const slot=who.toLowerCase();
  return slot==='chase'||slot==='morgan'?playerLabel(slot,state):(who||'Your partner');
}
function tcBuildSharedRewardAdvance(latest,rewardId,expectedIndex,identity){
  const shared=latest?.sharedRewardReveal;
  if(!shared||shared.id!==rewardId||shared.drawnBy!==identity)return null;
  const rewards=Array.isArray(shared.rewards)?shared.rewards:[];
  const currentIndex=tcSharedRewardIndex(shared);
  if(currentIndex!==expectedIndex||currentIndex>=rewards.length-1)return null;
  const next=structuredClone(latest);
  next.sharedRewardReveal={...structuredClone(shared),revealIndex:currentIndex+1};
  next.updatedAt=new Date().toISOString();
  return next;
}
let tcSharedRewardAdvanceBusy=false;
async function tcAdvanceSharedRewardReveal(data){
  if(tcSharedRewardAdvanceBusy||pending)return;
  const shared=run?.state?.sharedRewardReveal;
  const rewardId=data?.sharedId||shared?.id;
  if(!shared||shared.id!==rewardId)return renderRun();
  const me=playerName(),expectedIndex=tcSharedRewardIndex(shared);
  if(shared.drawnBy!==me)return;
  const staged=tcBuildSharedRewardAdvance(run.state,rewardId,expectedIndex,me);
  if(!staged)return renderRun();
  tcSharedRewardAdvanceBusy=true;
  try{
    await commit(staged,{
      retryBuilder:(latest)=>tcBuildSharedRewardAdvance(latest,rewardId,expectedIndex,me)
    });
  }finally{tcSharedRewardAdvanceBusy=false;}
}

// During a live draw, the reveal position is authoritative shared state and the
// drawing phone controls advancement. If the drawer has already finished while
// the other phone was closed/backgrounded, that remaining phone enters a LOCAL
// catch-up replay of the already-decided rewards. Catch-up never rerolls or
// changes reward economy; it only lets the missing viewer see every result.
tcHydrateSharedRewardReveal=function(state){
  const shared=state?.sharedRewardReveal;
  // Keep the exit guard from app.js: once this phone pressed the final
  // Continue, never rebuild that reward screen while the ack is saving.
  if(shared?.id&&typeof tcRewardExitDismissedIds!=='undefined'&&tcRewardExitDismissedIds.has(shared.id)){
    pendingRewardReveal=null;
    return;
  }
  if(!tcSharedRewardUnresolved(state)){
    if(pendingRewardReveal?.sharedId)pendingRewardReveal=null;
    return;
  }
  const me=playerName();
  if(tcSharedRewardSeenBy(state,me)){
    if(pendingRewardReveal?.sharedId===shared.id)pendingRewardReveal=null;
    return;
  }
  const sharedIndex=tcSharedRewardIndex(shared);
  const catchUp=tcSharedRewardNeedsCatchup(shared,me);
  if(catchUp){
    if(!pendingRewardReveal||pendingRewardReveal.sharedId!==shared.id||!pendingRewardReveal.catchUp){
      pendingRewardReveal={
        sharedId:shared.id,
        sharedIndex,
        rewards:structuredClone(shared.rewards),
        boss:shared.boss||'Enemy Felled',
        index:tcSharedRewardFirstMissingIndex(shared,me),
        catchUp:true,
        spinning:true
      };
    }
    return;
  }
  if(!pendingRewardReveal||pendingRewardReveal.sharedId!==shared.id||pendingRewardReveal.catchUp||pendingRewardReveal.sharedIndex!==sharedIndex){
    pendingRewardReveal={
      sharedId:shared.id,
      sharedIndex,
      rewards:structuredClone(shared.rewards),
      boss:shared.boss||'Enemy Felled',
      index:sharedIndex,
      catchUp:false,
      spinning:true
    };
  }
};

renderRewardMachine=function(){
  const data=pendingRewardReveal;
  const shared=run?.state?.sharedRewardReveal;
  if(!data?.rewards?.length||!shared||shared.id!==data.sharedId){pendingRewardReveal=null;return renderRun();}
  const me=playerName();
  const catchUp=Boolean(data.catchUp&&tcSharedRewardNeedsCatchup(shared,me));
  const sharedIndex=tcSharedRewardIndex(shared);
  if(!catchUp&&(data.index!==sharedIndex||data.sharedIndex!==sharedIndex)){
    pendingRewardReveal={...data,index:sharedIndex,sharedIndex,catchUp:false,spinning:true};
    return renderRewardMachine();
  }
  const displayIndex=catchUp?Math.max(0,Math.min(data.rewards.length-1,Number(data.index||0))):sharedIndex;
  const current=data.rewards[displayIndex]||data.rewards[0];
  const total=data.rewards.length;
  const hasNext=displayIndex+1<total;
  const isDrawer=shared.drawnBy===me;
  const drawerLabel=tcSharedRewardDrawerLabel(run.state);
  const symbols=['✦','◉','✧','⚖','☠','◇','✦','✧','◉'];
  const buttonLabel=hasNext?(catchUp?'Review Next Reward':isDrawer?'Draw Next Reward':`${drawerLabel} Is Drawing…`):'Continue';
  app.innerHTML=`<section class="tc-reward-machine">
    <div class="tc-reward-kicker">Covenant Treasury</div>
    <div class="tc-reward-title">DRAW ${displayIndex+1} <span>OF ${total}</span></div>
    <div class="tc-reward-boss">Victory over ${h(data.boss||'the enemy')}</div>
    <div class="tc-slot-frame" aria-live="polite">
      <div class="tc-slot-reel" data-reel="0">${symbols.map(x=>`<span>${x}</span>`).join('')}</div>
      <div class="tc-slot-reel" data-reel="1">${symbols.slice().reverse().map(x=>`<span>${x}</span>`).join('')}</div>
      <div class="tc-slot-reel" data-reel="2">${symbols.slice(3).concat(symbols.slice(0,3)).map(x=>`<span>${x}</span>`).join('')}</div>
    </div>
    <div id="tcRewardResult" class="tc-reward-result ${tcRewardClass(current.kind)}" hidden>
      <div class="tc-reward-icon">${tcRewardIcon(current.kind)}</div>
      <div class="tc-reward-type">${current.kind==='tax'?'Covenant Tax':'Reward Acquired'}</div>
      <div class="tc-reward-name">${h(current.label)}</div>
      <div class="tc-reward-detail">${h(current.detail||'The Covenant has spoken.')}</div>
    </div>
    <button id="tcRewardContinue" type="button" class="btn gold" disabled aria-disabled="true">${h(buttonLabel)}</button>
    ${catchUp?`<div class="tc-reward-catchup-note"><strong>${h(drawerLabel)}</strong> already finished this payout. You are reviewing the same rewards now — nothing is being drawn again.</div>`:hasNext&&!isDrawer?`<div class="tc-reward-sync-note"><strong>${h(drawerLabel)}</strong> controls this shared draw. Your screen will advance automatically.</div>`:''}
    <div class="tc-reward-quip">${current.kind==='tax'?'The Covenant giveth. The Covenant also has purchasing requirements.':'Honor has been converted into administratively approved loot.'}</div>
  </section>`;
  const reels=[...document.querySelectorAll('.tc-slot-reel')];
  const result=document.querySelector('#tcRewardResult');
  const btn=document.querySelector('#tcRewardContinue');
  const reduced=window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
  const finish=()=>{
    reels.forEach(reel=>{reel.classList.remove('spinning');reel.innerHTML=`<span class="winner">${tcRewardIcon(current.kind)}</span>`;});
    result.hidden=false;result.classList.add('revealed');data.spinning=false;
    if(!isDrawer&&result.isConnected&&run?.state?.sharedRewardReveal?.id===shared.id&&tcSharedRewardIndex(run.state.sharedRewardReveal)===displayIndex){
      tcRememberSharedRewardObserved(shared,displayIndex,me);
    }
    const mayAct=catchUp||!hasNext||isDrawer;
    btn.disabled=!mayAct;btn.setAttribute('aria-disabled',mayAct?'false':'true');btn.dataset.ready=mayAct?'1':'0';
  };
  if(reduced||data.spinning===false){finish();}
  else{
    reels.forEach((reel,i)=>{reel.classList.add('spinning');reel.style.setProperty('--tc-spin-delay',`${i*110}ms`);});
    window.setTimeout(finish,1250);
  }
  const advanceReward=(event)=>{
    if(event)event.preventDefault();
    if(btn.dataset.ready!=='1'||btn.disabled)return;
    btn.dataset.ready='0';btn.disabled=true;btn.setAttribute('aria-disabled','true');data.spinning=false;
    if(hasNext){
      if(catchUp){data.index=displayIndex+1;data.spinning=true;renderRewardMachine();return;}
      void tcAdvanceSharedRewardReveal(data);return;
    }
    void tcAcknowledgeSharedRewardReveal(data);
  };
  btn.addEventListener('click',advanceReward);
  btn.addEventListener('pointerup',event=>{if(event.pointerType==='touch')advanceReward(event);});
  btn.addEventListener('touchend',advanceReward,{passive:false});
};
/* --- End synchronized shared reward reveal --- */