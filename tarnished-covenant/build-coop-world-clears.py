from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# -----------------------------------------------------------------------------
# Co-op encounter completion + shared reward reveal
#
# Elden Ring co-op requires a boss to be defeated once in each host world. The
# Covenant treats those two in-game kills as ONE encounter: record both world
# clears, then file one post-battle report, roll one reward payout, and show the
# same payout independently on both phones.
# -----------------------------------------------------------------------------

# Remove an older copy if this late build step is re-run on an assembled page.
s = re.sub(
    r"\n?/\* --- Co-op dual-world clears \+ shared reward reveal --- \*/.*?"
    r"/\* --- End co-op dual-world clears \+ shared reward reveal --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

# The old victory button immediately opened a local post-battle report after a
# single kill. Replace that binding with the shared two-world clear controls.
old_complete = """  document.querySelector('#complete')?.addEventListener('click',()=>{
    postBattleReport={encounterId:c.id,rite:null,chaos:null};
    renderPostBattleReport();
  });"""
new_complete = """  tcBindCoopWorldClearControls(state,c);"""
if old_complete in s:
    s = s.replace(old_complete, new_complete, 1)
elif 'tcBindCoopWorldClearControls(state,c);' not in s:
    raise SystemExit('single-world victory binding target missing')

# Reward results were previously placed only in the initiating phone's local
# pendingRewardReveal variable. Persist the reveal payload in shared run state.
old_reward = "pendingRewardReveal=rewards.length?{rewards:structuredClone(rewards),boss:c.target?.name||'Enemy Felled',index:0,spinning:true}:null;"
new_reward = """completed.sharedRewardReveal=rewards.length?{
    id:`${c.id}:${Date.now()}`,
    encounterId:c.id,
    rewards:structuredClone(rewards),
    boss:c.target?.name||'Enemy Felled',
    seenBy:[]
  }:null;
  pendingRewardReveal=null;"""
if old_reward in s:
    s = s.replace(old_reward, new_reward, 1)
elif 'completed.sharedRewardReveal=rewards.length?' not in s:
    raise SystemExit('local reward reveal assignment target missing')

# Finishing the slot/reward machine now acknowledges the shared reveal for this
# device identity instead of merely clearing a local variable.
old_finish = """    if(data.index+1<total){data.index+=1;data.spinning=true;renderRewardMachine();return;}
    pendingRewardReveal=null;renderRun();"""
new_finish = """    if(data.index+1<total){data.index+=1;data.spinning=true;renderRewardMachine();return;}
    void tcAcknowledgeSharedRewardReveal(data);"""
if old_finish in s:
    s = s.replace(old_finish, new_finish, 1)
elif 'void tcAcknowledgeSharedRewardReveal(data);' not in s:
    raise SystemExit('reward-machine completion target missing')

css = r'''
/* --- Co-op dual-world clears --- */
.tc-world-clear-card{margin:14px 0 4px;padding:14px;border:1px solid var(--line);background:linear-gradient(180deg,rgba(30,27,20,.78),rgba(13,12,9,.72));clip-path:polygon(8px 0,calc(100% - 8px) 0,100% 8px,100% calc(100% - 8px),calc(100% - 8px) 100%,8px 100%,0 calc(100% - 8px),0 8px)}
.tc-world-clear-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:11px}.tc-world-clear-head strong{display:block;font-size:18px;font-weight:400;line-height:1.15}.tc-world-clear-count{font:850 11px/1 system-ui,sans-serif;color:var(--gold);white-space:nowrap;padding-top:3px}.tc-world-clear-note{font-size:11px;line-height:1.4;color:var(--ash);margin-top:4px}.tc-world-clear-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.tc-world-clear-btn{min-height:54px}.tc-world-clear-btn.done{border-color:rgba(198,161,90,.48);color:var(--gold-bright);background:rgba(126,93,40,.12)}.tc-world-clear-btn.done:before{content:'✓ ';}.tc-world-clear-wait{margin-top:9px;text-align:center;font:750 9px/1.4 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.07em;color:var(--ash)}
@media(max-width:430px){.tc-world-clear-grid{grid-template-columns:1fr}.tc-world-clear-head{align-items:center}}
/* --- End co-op dual-world clears --- */
'''
if '/* --- Co-op dual-world clears --- */' not in s:
    if '</style>' not in s:
        raise SystemExit('style marker missing')
    s = s.replace('</style>', css + '\n</style>', 1)

js = r'''
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
  if(tcSharedRewardUnresolved(state))return setToast('Both Tarnished must review the previous reward first.');
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
  if(['Chase','Morgan'].every(name=>seen.includes(name)))next.sharedRewardReveal=null;
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
  return tcRenderRunBeforeCoopWorlds();
};
/* --- End co-op dual-world clears + shared reward reveal --- */
'''
idx = s.rfind('</script>')
if idx < 0:
    raise SystemExit('script end marker missing')
s = s[:idx] + js + s[idx:]

required = [
    'tcBindCoopWorldClearControls(state,c);',
    'function tcWorldClears(encounter)',
    'function tcBothWorldsCleared(encounter)',
    "next.current.worldClears=[...clears,slot];",
    "Rewards remain sealed.",
    'completed.sharedRewardReveal=rewards.length?',
    'seenBy:[]',
    'function tcHydrateSharedRewardReveal(state)',
    'function tcAcknowledgeSharedRewardReveal(data)',
    "['Chase','Morgan'].every(name=>seen.includes(name))",
    'void tcAcknowledgeSharedRewardReveal(data);',
    'Both Tarnished must review the previous Covenant reward',
]
for needle in required:
    if needle not in s:
        raise SystemExit('co-op invariant missing: ' + needle)

if old_complete in s:
    raise SystemExit('single-kill victory handler remains')
if old_reward in s:
    raise SystemExit('local-only reward reveal assignment remains')

p.write_text(s)
print('Co-op dual-world clears and shared reward reveal applied.')
