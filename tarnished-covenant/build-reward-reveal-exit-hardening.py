from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

s=re.sub(r"\n?/\* --- Shared reward reveal exit hardening --- \*/.*?/\* --- End shared reward reveal exit hardening --- \*/\n?","\n",s,flags=re.S)

js=r'''
/* --- Shared reward reveal exit hardening --- */
// A final reward acknowledgement is a shared CAS action, but leaving the local
// reward screen must never depend on which phone wins that acknowledgement race.
const tcRewardExitDismissedIds=new Set();

const tcHydrateSharedRewardRevealBeforeExitHardening=tcHydrateSharedRewardReveal;
tcHydrateSharedRewardReveal=function(state){
  const id=state?.sharedRewardReveal?.id;
  if(id&&tcRewardExitDismissedIds.has(id)){
    pendingRewardReveal=null;
    return;
  }
  return tcHydrateSharedRewardRevealBeforeExitHardening(state);
};

async function tcRewardExitAuthoritativeSync(){
  if(backend?.mode!=='shared'||!run?.id)return false;
  try{
    const latest=await backend.getRun(run.id);
    if(!latest?.state)return false;
    return tcApplyAuthoritativeRun(latest,{source:'reward-exit-hardening'});
  }catch(error){
    console.warn('Reward-exit authoritative sync failed',error);
    return false;
  }
}

const tcAcknowledgeSharedRewardRevealBeforeExitHardening=tcAcknowledgeSharedRewardReveal;
tcAcknowledgeSharedRewardReveal=async function(data){
  const rewardId=data?.sharedId||run?.state?.sharedRewardReveal?.id||null;
  if(rewardId)tcRewardExitDismissedIds.add(rewardId);
  pendingRewardReveal=null;
  renderRun();
  try{
    await tcAcknowledgeSharedRewardRevealBeforeExitHardening(data);
  }finally{
    await tcRewardExitAuthoritativeSync();
    const remaining=run?.state?.sharedRewardReveal;
    const seen=Array.isArray(remaining?.seenBy)?remaining.seenBy:[];
    if(!remaining||remaining.id!==rewardId||seen.includes(playerName())){
      if(rewardId)tcRewardExitDismissedIds.delete(rewardId);
    }
    pendingRewardReveal=null;
    renderRun();
  }
};

// iOS can receive a realtime render while the slot-machine timeout still owns a
// detached button. The new button then stays disabled forever. A final-frame
// watchdog always targets the CURRENT DOM button, never the detached one.
function tcArmFinalRewardExitWatchdog(){
  const data=pendingRewardReveal;
  const btn=document.querySelector('#tcRewardContinue');
  if(!btn||!data?.rewards?.length)return;
  const finalIndex=data.rewards.length-1;
  if(Number(data.index)!==finalIndex)return;
  const rewardId=data.sharedId;
  window.setTimeout(()=>{
    const liveData=pendingRewardReveal;
    const liveBtn=document.querySelector('#tcRewardContinue');
    if(!liveBtn||!liveData?.rewards?.length||liveData.sharedId!==rewardId)return;
    if(Number(liveData.index)!==liveData.rewards.length-1)return;
    const result=document.querySelector('#tcRewardResult');
    if(result&&!result.hidden){
      liveBtn.disabled=false;
      liveBtn.setAttribute('aria-disabled','false');
      liveBtn.dataset.ready='1';
    }
  },1650);
}

const tcRenderRewardMachineBeforeExitHardening=renderRewardMachine;
renderRewardMachine=function(){
  const out=tcRenderRewardMachineBeforeExitHardening();
  tcArmFinalRewardExitWatchdog();
  return out;
};

async function tcRetryDismissedRewardAck(){
  const shared=run?.state?.sharedRewardReveal;
  if(!shared?.id||!tcRewardExitDismissedIds.has(shared.id)||pending||tcSharedRewardAckBusy)return;
  const me=playerName();
  const staged=tcBuildSharedRewardAck(run.state,shared.id,me);
  if(staged){
    await commit(staged,{retryBuilder:(latest)=>tcBuildSharedRewardAck(latest,shared.id,me)});
  }
  await tcRewardExitAuthoritativeSync();
  const remaining=run?.state?.sharedRewardReveal;
  if(!remaining||remaining.id!==shared.id||(remaining.seenBy||[]).includes(me))tcRewardExitDismissedIds.delete(shared.id);
}
window.addEventListener('online',()=>setTimeout(tcRetryDismissedRewardAck,250));
document.addEventListener('visibilitychange',()=>{if(!document.hidden)setTimeout(tcRetryDismissedRewardAck,250);});
/* --- End shared reward reveal exit hardening --- */
'''

idx=s.rfind('/* --- Home Screen freshness guard --- */')
if idx<0: idx=s.rfind('</script>')
if idx<0: raise SystemExit('reward reveal exit insertion anchor missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in [
  'const tcRewardExitDismissedIds=new Set();',
  'const tcHydrateSharedRewardRevealBeforeExitHardening=tcHydrateSharedRewardReveal;',
  'async function tcRewardExitAuthoritativeSync()',
  'const tcAcknowledgeSharedRewardRevealBeforeExitHardening=tcAcknowledgeSharedRewardReveal;',
  'pendingRewardReveal=null;\n  renderRun();',
  'function tcArmFinalRewardExitWatchdog()',
  "document.querySelector('#tcRewardContinue')",
  "liveBtn.dataset.ready='1';",
  'const tcRenderRewardMachineBeforeExitHardening=renderRewardMachine;',
  'async function tcRetryDismissedRewardAck()'
]:
    if needle not in s: raise SystemExit('reward exit hardening invariant missing: '+needle)
p.write_text(s)
