from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Remove any previous generated copy before reapplying.
s=re.sub(
    r"\n?/\* --- Synchronized shared reward reveal --- \*/.*?"
    r"/\* --- End synchronized shared reward reveal --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

# Repair the reward-economy persistence bug in already assembled builds. The old
# code mutated smithingData(next), which is a detached normalized object rather
# than next.smithing itself, so reward counters could be written to history but
# never actually persist in shared state.
s=s.replace(
    'const next=smithingCopy(latest),sm=smithingData(next);',
    'const next=smithingCopy(latest),sm=next.smithing;',
)

# Every newly claimed shared payout starts its reveal sequence at reward zero.
old_reveal='''    boss:draw.boss||'Enemy Felled',
    drawnBy:drawer,
    seenBy:[]'''
new_reveal='''    boss:draw.boss||'Enemy Felled',
    drawnBy:drawer,
    revealIndex:0,
    seenBy:[]'''
if old_reveal in s:
    s=s.replace(old_reveal,new_reveal,1)
elif 'revealIndex:0,' not in s:
    raise SystemExit('shared reward reveal creation target missing')

css=r'''
/* --- Synchronized shared reward reveal --- */
.tc-reward-sync-note{margin:10px auto 0;max-width:440px;text-align:center;color:var(--ash);font:800 9px/1.45 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.07em}
.tc-reward-sync-note strong{color:var(--gold-bright)}
.tc-reward-catchup-note{margin:10px auto 0;max-width:460px;text-align:center;color:#c9b98f;font:800 9px/1.5 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.07em}
/* --- End synchronized shared reward reveal --- */
'''
if '/* --- Synchronized shared reward reveal --- */' not in s:
    if '</style>' not in s: raise SystemExit('style end missing')
    s=s.replace('</style>',css+'\n</style>',1)

js=r'''
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
  return Boolean(shared?.id&&tcSharedRewardDrawerFinished(shared)&&!tcSharedRewardSeenList(shared).includes(identity));
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
        index:0,
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
    const mayAct=catchUp||!hasNext||isDrawer;
    btn.disabled=!mayAct;btn.setAttribute('aria-disabled',mayAct?'false':'true');btn.dataset.ready=mayAct?'1':'0';
  };
  if(reduced){finish();}
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
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end missing')
s=s[:idx]+js+'\n'+s[idx:]

required=[
    'const next=smithingCopy(latest),sm=next.smithing;',
    'revealIndex:0,',
    'function tcSharedRewardIndex(shared)',
    'function tcSharedRewardDrawerFinished(shared)',
    'function tcSharedRewardNeedsCatchup(shared,identity=playerName())',
    'function tcBuildSharedRewardAdvance(latest,rewardId,expectedIndex,identity)',
    'next.sharedRewardReveal={...structuredClone(shared),revealIndex:currentIndex+1};',
    'tcHydrateSharedRewardReveal=function(state)',
    'catchUp:true,',
    'renderRewardMachine=function()',
    "catchUp?'Review Next Reward'",
    'already finished this payout. You are reviewing the same rewards now',
    'if(catchUp){data.index=displayIndex+1;data.spinning=true;renderRewardMachine();return;}',
    'void tcAdvanceSharedRewardReveal(data);return;',
    'void tcAcknowledgeSharedRewardReveal(data);',
]
for needle in required:
    if needle not in s: raise SystemExit('shared reveal sync invariant missing: '+needle)

p.write_text(s)
print('Shared reward reveal synchronized with offline catch-up replay.')
