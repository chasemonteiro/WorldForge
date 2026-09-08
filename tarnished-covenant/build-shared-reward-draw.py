from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# -----------------------------------------------------------------------------
# One shared reward draw, initiated by either player
#
# The post-battle report creates ONE shared pending payout. It does not roll the
# rewards itself. Both phones see the same "Draw Shared Reward" screen. The first
# phone to tap claims that payout with the normal revision/CAS save; the other
# phone receives the exact same persisted result and cannot roll again.
# -----------------------------------------------------------------------------

# Remove an older generated copy if rerunning this late build step.
s = re.sub(
    r"\n?/\* --- Shared first-come Covenant reward draw --- \*/.*?"
    r"/\* --- End shared first-come Covenant reward draw --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

# Move RNG out of finalizePostBattleReport. The report still determines the
# number of earned draws and completes the encounter, but leaves one shared draw
# request for either phone to claim.
old = """  const rewards=[];
  for(let i=0;i<draws;i++) rewards.push(drawCovenantReward(nextState));
  nc.postBattleRewards=rewards.map(x=>x.label);
  nc.favorEarned=rewards.filter(x=>x.kind==='favor'||x.kind==='favor2').reduce((sum,x)=>sum+(x.kind==='favor2'?2:1),0);
  const completed=completeEncounter(nextState,playerName());
  if(!completed.regionComplete && !completed.runComplete && completed.current){
    completed.smithing = smithingData(completed);
    const affordableCorporate = availableBellBearings(completed).filter(b=>completed.smithing.favor>=smithingContractCost(b));
    if(!completed.smithing.activeContract && affordableCorporate.length){
      completed.smithing.pendingCorporateForEncounterId = completed.current.id;
    }
  }
  postBattleReport=null;
  if(!completed.regionComplete&&!completed.runComplete&&completed.current){pendingRevealId=completed.current.id;uiScreen='encounter';}
  completed.sharedRewardReveal=rewards.length?{
    id:`${c.id}:${Date.now()}`,
    encounterId:c.id,
    rewards:structuredClone(rewards),
    boss:c.target?.name||'Enemy Felled',
    seenBy:[]
  }:null;
  pendingRewardReveal=null;
  const rewardText=rewards.length?'Covenant reward draw ready.':'Post-battle report filed.';"""

new = """  nc.postBattleRewards=[];
  nc.favorEarned=0;
  const completed=completeEncounter(nextState,playerName());
  if(!completed.regionComplete && !completed.runComplete && completed.current){
    completed.smithing = smithingData(completed);
    const affordableCorporate = availableBellBearings(completed).filter(b=>completed.smithing.favor>=smithingContractCost(b));
    if(!completed.smithing.activeContract && affordableCorporate.length){
      completed.smithing.pendingCorporateForEncounterId = completed.current.id;
    }
  }
  postBattleReport=null;
  if(!completed.regionComplete&&!completed.runComplete&&completed.current){pendingRevealId=completed.current.id;uiScreen='encounter';}
  completed.sharedRewardDraw=draws>0?{
    id:`${c.id}:${Date.now()}`,
    encounterId:c.id,
    count:draws,
    boss:c.target?.name||'Enemy Felled',
    filedBy:playerName()
  }:null;
  completed.sharedRewardReveal=null;
  pendingRewardReveal=null;
  const rewardText=draws>0?'Shared Covenant reward ready to draw.':'Post-battle report filed.';"""

if old in s:
    s = s.replace(old, new, 1)
elif 'completed.sharedRewardDraw=draws>0?' not in s:
    raise SystemExit('post-battle reward generation target missing')

# A stale Encounter screen must not allow another world-clear while the previous
# shared payout is waiting to be drawn.
old_guard = "if(tcSharedRewardUnresolved(state))return setToast('Both Tarnished must review the previous reward first.');"
new_guard = "if(tcSharedRewardDrawPending(state)||tcSharedRewardUnresolved(state))return setToast('Finish the previous shared Covenant reward first.');"
if old_guard in s:
    s = s.replace(old_guard, new_guard, 1)
elif new_guard not in s:
    raise SystemExit('world-clear reward guard target missing')

css = r'''
/* --- Shared Covenant reward draw gate --- */
.tc-shared-draw-screen{min-height:calc(100svh - env(safe-area-inset-top) - env(safe-area-inset-bottom));display:flex;align-items:center;justify-content:center;padding:18px 4px 84px}
.tc-shared-draw-card{width:min(520px,100%);text-align:center;border:1px solid rgba(198,161,90,.42);padding:26px 18px 20px;background:radial-gradient(circle at 50% 10%,rgba(198,161,90,.12),transparent 42%),linear-gradient(180deg,rgba(28,24,16,.92),rgba(8,7,5,.96));clip-path:polygon(10px 0,calc(100% - 10px) 0,100% 10px,100% calc(100% - 10px),calc(100% - 10px) 100%,10px 100%,0 calc(100% - 10px),0 10px)}
.tc-shared-draw-glyph{font-size:44px;color:var(--gold-bright);margin-bottom:7px;text-shadow:0 0 26px rgba(224,193,123,.22)}
.tc-shared-draw-card h1{font-size:clamp(31px,9vw,44px);margin:6px 0 8px}.tc-shared-draw-boss{font-style:italic;color:var(--ash);margin-bottom:18px}.tc-shared-draw-copy{font-size:14px;line-height:1.5;color:#d4cab8;margin:0 auto 18px;max-width:410px}.tc-shared-draw-count{font:850 10px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.11em;color:var(--gold);margin-bottom:13px}
/* --- End Shared Covenant reward draw gate --- */
'''
if '/* --- Shared Covenant reward draw gate --- */' not in s:
    if '</style>' not in s:
        raise SystemExit('style marker missing')
    s = s.replace('</style>', css + '\n</style>', 1)

js = r'''
/* --- Shared first-come Covenant reward draw --- */
function tcSharedRewardDrawPending(state){
  const draw=state?.sharedRewardDraw;
  return Boolean(draw?.id&&Number(draw.count||0)>0&&!state?.sharedRewardReveal);
}
function tcSharedRewardDeltas(before,after){
  const keys=['favor','chaosRefreshes','riteRefreshes','appealWaivers','aviaryTickets'];
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
  const next=smithingCopy(latest),sm=smithingData(next);
  for(const [key,delta] of Object.entries(deltas||{}))sm[key]=Number(sm[key]||0)+Number(delta||0);
  const labels=(rewards||[]).map(x=>x.label);
  const favorEarned=Math.max(0,Number(deltas?.favor||0));
  if(Array.isArray(next.history)&&next.history.length){
    next.history[0].rewards=structuredClone(labels);
    next.history[0].favorEarned=favorEarned;
    next.history[0].rewardDrawnBy=drawer;
  }
  next.sharedRewardDraw=null;
  next.sharedRewardReveal={
    id:draw.id,
    encounterId:draw.encounterId,
    rewards:structuredClone(rewards||[]),
    boss:draw.boss||'Enemy Felled',
    drawnBy:drawer,
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
      successToast:`${drawer} drew the shared Covenant reward.`,
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
'''

idx = s.rfind('</script>')
if idx < 0:
    raise SystemExit('script end marker missing')
s = s[:idx] + js + '\n' + s[idx:]

required = [
    'completed.sharedRewardDraw=draws>0?',
    "completed.sharedRewardReveal=null;",
    "const rewardText=draws>0?'Shared Covenant reward ready to draw.'",
    'function tcSharedRewardDrawPending(state)',
    'function tcGenerateSharedRewardPayload(state,count)',
    'function tcBuildClaimedSharedReward(latest,draw,rewards,deltas,drawer)',
    'if(!pendingDraw||pendingDraw.id!==draw.id||latest?.sharedRewardReveal)return null;',
    'next.sharedRewardDraw=null;',
    'drawnBy:drawer,',
    'seenBy:[]',
    'function renderSharedRewardDraw()',
    'Either Tarnished may draw this payout.',
    'function tcClaimSharedRewardDraw()',
    'retryBuilder:(latest)=>tcBuildClaimedSharedReward(latest,draw,payload.rewards,payload.deltas,drawer)',
    'if(tcSharedRewardDrawPending(run?.state))return renderSharedRewardDraw();',
    "if(tcSharedRewardDrawPending(state)||tcSharedRewardUnresolved(state))return setToast('Finish the previous shared Covenant reward first.');",
]
for needle in required:
    if needle not in s:
        raise SystemExit('shared reward draw invariant missing: ' + needle)

if 'for(let i=0;i<draws;i++) rewards.push(drawCovenantReward(nextState));' in s:
    raise SystemExit('post-battle report still rolls rewards before either player chooses to draw')

p.write_text(s)
print('One shared first-come Covenant reward draw applied.')
