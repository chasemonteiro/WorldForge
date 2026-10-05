/* --- Shared first-come Covenant reward draw --- */
function tcSharedRewardDrawPending(state){
  const draw=state?.sharedRewardDraw;
  return Boolean(draw?.id&&Number(draw.count||0)>0&&!state?.sharedRewardReveal);
}
function tcSharedRewardDeltas(before,after){
  const keys=['favor','chaosRefreshes','riteRefreshes','appealWaivers','aviaryTickets','freeBossKills','bossVetoes','clemencies','unionDiscounts','blankAmendments','jointAppeals','erdtreeWrits','erdtreeWritsAwarded'];
  const out={};
  for(const key of keys)out[key]=Number(after?.[key]||0)-Number(before?.[key]||0);
  return out;
}
function tcGenerateSharedRewardPayload(state,count){
  const scratch=smithingCopy(state);
  const before=structuredClone(smithingData(scratch));
  const rewards=[];
  for(let i=0;i<Math.max(0,Number(count||0));i++)rewards.push(drawCovenantReward(scratch));
  return {rewards,deltas:tcSharedRewardDeltas(before,smithingData(scratch))};
}
function tcBuildClaimedSharedReward(latest,draw,rewards,deltas,drawer){
  const pendingDraw=latest?.sharedRewardDraw;
  if(!pendingDraw||pendingDraw.id!==draw.id||latest?.sharedRewardReveal)return null;
  const next=smithingCopy(latest),sm=next.smithing;
  for(const [key,delta] of Object.entries(deltas||{}))sm[key]=Number(sm[key]||0)+Number(delta||0);
  const labels=(rewards||[]).map(x=>x.label);
  const favorEarned=Math.max(0,Number(deltas?.favor||0));
  if(Array.isArray(next.history)&&next.history.length){
    next.history[0].rewards=structuredClone(labels);
    next.history[0].favorEarned=Math.max(0,Number(next.history[0].favorEarned||0))+favorEarned;
    next.history[0].rewardDrawnBy=drawer;
  }
  next.sharedRewardDraw=null;
  next.sharedRewardReveal={
    id:draw.id,
    encounterId:draw.encounterId,
    rewards:structuredClone(rewards||[]),
    boss:draw.boss||'Enemy Felled',
    drawnBy:drawer,
    revealIndex:0,
    seenBy:[]
  };
  if(!next.regionComplete&&!next.runComplete&&next.current){
    const affordable=availableBellBearings(next).filter(b=>sm.favor>=smithingContractCost(b));
    if(!sm.activeContract&&affordable.length)sm.pendingCorporateForEncounterId=next.current.id;
  }
  next.lastAction=`${drawer} drew the shared Covenant reward.`;
  next.updatedAt=new Date().toISOString();
  return next;
}
function renderSharedRewardDraw(){
  const draw=run?.state?.sharedRewardDraw;
  if(!tcSharedRewardDrawPending(run?.state))return renderRun();
  const count=Math.max(1,Number(draw.count||1));
  app.innerHTML=`<section class="tc-shared-draw-screen"><div class="tc-shared-draw-card"><div class="tc-shared-draw-glyph">✦</div><div class="tc-kicker gold">Shared Covenant Reward</div><h1>One Payout. One Draw.</h1><div class="tc-shared-draw-boss">${h(draw.boss||'Enemy Felled')}</div><div class="tc-shared-draw-count">${count} ${count===1?'reward':'rewards'} waiting</div><div class="tc-shared-draw-copy">Either Tarnished may draw this payout. The first draw is final and immediately becomes the shared result on both phones.</div><button id="tcDrawSharedReward" type="button" class="btn gold">Draw Shared Reward${count===1?'':'s'}</button></div></section>${typeof navMarkup==='function'?navMarkup('encounter'):''}`;
  if(typeof bindNav==='function')bindNav();
  document.querySelector('#tcDrawSharedReward')?.addEventListener('click',tcClaimSharedRewardDraw);
}
let tcSharedRewardDrawBusy=false;
async function tcClaimSharedRewardDraw(){
  if(tcSharedRewardDrawBusy||pending)return;
  const draw=structuredClone(run?.state?.sharedRewardDraw);
  if(!draw?.id||!tcSharedRewardDrawPending(run?.state))return renderRun();
  const btn=document.querySelector('#tcDrawSharedReward');if(btn){btn.disabled=true;btn.textContent='Drawing…';}
  const drawer=playerName();
  const payload=tcGenerateSharedRewardPayload(run.state,draw.count);
  const staged=tcBuildClaimedSharedReward(run.state,draw,payload.rewards,payload.deltas,drawer);
  if(!staged)return renderRun();
  tcSharedRewardDrawBusy=true;
  try{
    const saved=await commit(staged,{
      successToast:`${personalizePlayers(drawer,run?.state)} drew the shared Covenant reward.`,
      retryBuilder:(latest)=>tcBuildClaimedSharedReward(latest,draw,payload.rewards,payload.deltas,drawer)
    });
    if(!saved&&tcSharedRewardDrawPending(run?.state))renderSharedRewardDraw();
  }finally{tcSharedRewardDrawBusy=false;}
}
const tcRenderRunBeforeSharedRewardDraw=renderRun;
renderRun=function(){
  if(tcSharedRewardDrawPending(run?.state))return renderSharedRewardDraw();
  return tcRenderRunBeforeSharedRewardDraw();
};
/* --- End shared first-come Covenant reward draw --- */