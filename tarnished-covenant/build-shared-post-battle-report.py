from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# Shared post-battle report
#
# The old co-op report choices lived only in the submitting phone's local
# `postBattleReport` object. That meant the partner phone rendered an untouched
# local report and misleadingly showed Guaranteed Smithing Favor as +0 while the
# other player was filing the victory. Make the report draft authoritative in
# shared run state, mirror it on both phones, and finalize from that shared draft.
# -----------------------------------------------------------------------------

s=re.sub(
    r"\n?/\* --- Shared post-battle report sync --- \*/.*?"
    r"/\* --- End shared post-battle report sync --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)
s=re.sub(
    r"\n?/\* --- Shared post-battle report styles --- \*/.*?"
    r"/\* --- End shared post-battle report styles --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

css=r'''
/* --- Shared post-battle report styles --- */
.tc-report-sync{margin:2px 0 10px;font:750 8px/1.35 system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--ash)}
.tc-report-sync strong{color:var(--gold);font-weight:850}
/* --- End shared post-battle report styles --- */
'''
if '</style>' not in s: raise SystemExit('shared report style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Shared post-battle report sync --- */
function tcSharedBattleReportDraft(state=run?.state){
  const c=state?.current;if(!c)return null;
  const d=c?.battleReportDraft;
  if(!d||d.encounterId!==c.id)return {encounterId:c.id,rite:null,chaos:null,updatedBy:null,updatedAt:null};
  return {
    encounterId:c.id,
    rite:d.rite===true?true:d.rite===false?false:null,
    chaos:d.chaos===true?true:d.chaos===false?false:null,
    updatedBy:d.updatedBy||null,
    updatedAt:d.updatedAt||null
  };
}
function tcSharedBattleReportReady(state,draft=tcSharedBattleReportDraft(state)){
  const c=state?.current;if(!c||!draft||draft.encounterId!==c.id)return false;
  const riteDraws=Number(c.weirdness?.favor??1),chaosDraws=Number(c.chaosFavor??1);
  const riteReady=riteDraws<=0||draft.rite!==null;
  const chaosAvailable=Boolean(c.chaosTriggered);
  const chaosReady=!chaosAvailable||chaosDraws<=0||draft.chaos!==null;
  return riteReady&&chaosReady;
}
function tcBattleReportAwardPreview(state,draft=tcSharedBattleReportDraft(state)){
  const c=state?.current;if(!c||!draft)return {guaranteedFavor:0,draws:0};
  const riteDraws=Number(c.weirdness?.favor??1),chaosDraws=Number(c.chaosFavor??1);
  let guaranteedFavor=0;
  if(draft.rite===true&&!c.riteForfeited&&riteDraws>0&&!c.smithingRiteFavor)guaranteedFavor=Number(guaranteedFavor)+riteDraws;
  if(draft.chaos===true&&!c.chaosForfeited&&c.chaosTriggered&&chaosDraws>0&&!c.smithingChaosFavor)guaranteedFavor=Number(guaranteedFavor)+chaosDraws;
  return {guaranteedFavor,draws:guaranteedFavor};
}
function tcBuildSharedBattleReportChoice(latest,encounterId,kind,value,actor){
  const c=latest?.current;
  if(!c||c.id!==encounterId||!['rite','chaos'].includes(kind))return null;
  if(typeof tcBothWorldsCleared==='function'&&!tcBothWorldsCleared(c))return null;
  if(latest?.sharedRewardDraw||latest?.sharedRewardReveal)return null;
  const next=structuredClone(latest),current=tcSharedBattleReportDraft(latest)||{encounterId,rite:null,chaos:null};
  next.current.battleReportDraft={
    encounterId,
    rite:current.rite,
    chaos:current.chaos,
    [kind]:Boolean(value),
    updatedBy:actor,
    updatedAt:new Date().toISOString()
  };
  next.lastAction=`${actor} updated the shared post-battle report.`;
  next.updatedAt=new Date().toISOString();
  return next;
}
let tcSharedBattleReportChoiceBusy=false;
postBattleChoice=async function(kind,value){
  if(tcSharedBattleReportChoiceBusy||pending)return;
  const state=run?.state,c=state?.current;if(!c)return;
  const encounterId=c.id,actor=playerName();
  const build=latest=>tcBuildSharedBattleReportChoice(latest,encounterId,kind,value,actor);
  const staged=build(state);if(!staged)return setToast('That battle report is no longer editable.');
  tcSharedBattleReportChoiceBusy=true;
  try{
    const saved=await commit(staged,{retryBuilder:build});
    if(saved){postBattleReport=tcSharedBattleReportDraft(run.state);renderPostBattleReport();}
  }finally{tcSharedBattleReportChoiceBusy=false;}
};

renderPostBattleReport=function(){
  const state=run.state,c=state.current;
  if(!c){postBattleReport=null;return renderRun();}
  const draft=tcSharedBattleReportDraft(state);
  postBattleReport=draft?{...draft}:{encounterId:c.id,rite:null,chaos:null};
  const riteDraws=Number(c.weirdness?.favor??1);
  const chaosDraws=Number(c.chaosFavor??1);
  const riteReady=riteDraws<=0||postBattleReport.rite!==null;
  const chaosAvailable=Boolean(c.chaosTriggered);
  const chaosReady=!chaosAvailable||chaosDraws<=0||postBattleReport.chaos!==null;
  const reportReady=riteReady&&chaosReady;
  const preview=tcBattleReportAwardPreview(state,postBattleReport);
  const guaranteedText=reportReady?`+${preview.guaranteedFavor}`:'—';
  const drawText=reportReady?String(preview.draws):'—';
  const syncLine=postBattleReport.updatedBy?`Shared report · last updated by <strong>${h(postBattleReport.updatedBy)}</strong>`:'Shared report · either Tarnished may answer';
  app.innerHTML=`<section class="tc-battle-report">
    <div class="tc-report-kicker">Encounter Complete</div>
    <div class="tc-report-victory">VICTORY</div>
    <div class="tc-report-boss">${h(c.target?.name||'Enemy Felled')}</div>
    <div class="tc-report-sync">${syncLine}</div>
    <div class="tc-report-rule"></div>
    ${postBattleChoiceMarkup('rite','Odd Rite',`${h(c.weirdness?.name||'No Rite')} · ${h(c.weirdness?.text||'')}`,riteDraws,true)}
    ${postBattleChoiceMarkup('chaos','Chaos',chaosAvailable?`${h(chaosEventName(c.chaosConsequence||''))} · ${h(personalizePlayers(c.chaosConsequence||'',state))}`:'The Chaos seal never broke during this encounter.',chaosDraws,chaosAvailable)}
    <div class="tc-report-total"><span>Guaranteed Smithing Favor</span><strong>${guaranteedText}</strong></div>
    <div class="tc-report-total"><span>Bonus Covenant reward draws</span><strong>${drawText}</strong></div>
    <button id="finishBattleReport" class="btn gold" ${reportReady?'':'disabled'}>${c.target?.exit?'Record Victory · Draw Rewards':'Record Victory · Draw Rewards & Roll Next'}</button>
    <div class="tc-report-note">${reportReady?'Honor pays Smithing Favor immediately. This exact shared total will be awarded no matter which phone files the report.':'Waiting for the shared honor-system checks. No +0 is assumed while answers are pending.'}</div>
  </section>`;
  document.querySelectorAll('[data-report-kind]').forEach(btn=>btn.addEventListener('click',()=>postBattleChoice(btn.dataset.reportKind,btn.dataset.reportValue==='1')));
  document.querySelector('#finishBattleReport')?.addEventListener('click',finalizePostBattleReport);
};

function tcBuildSharedBattleReportCompletion(latest,encounterId,actor){
  const c=latest?.current;
  if(!c||c.id!==encounterId)return null;
  if(typeof tcBothWorldsCleared==='function'&&!tcBothWorldsCleared(c))return null;
  if(latest?.sharedRewardDraw||latest?.sharedRewardReveal)return null;
  const draft=tcSharedBattleReportDraft(latest);
  if(!tcSharedBattleReportReady(latest,draft))return null;
  const nextState=smithingCopy(latest),nc=nextState.current;
  let draws=0,guaranteedFavor=0;
  const riteDraws=Number(nc.weirdness?.favor??1);
  if(draft.rite===true&&!nc.riteForfeited&&riteDraws>0&&!nc.smithingRiteFavor){
    nc.smithingRiteFavor=true;draws+=riteDraws;guaranteedFavor=Number(guaranteedFavor)+riteDraws;
  }
  const chaosDraws=Number(nc.chaosFavor??1);
  if(draft.chaos===true&&!nc.chaosForfeited&&nc.chaosTriggered&&chaosDraws>0&&!nc.smithingChaosFavor){
    nc.smithingChaosFavor=true;draws+=chaosDraws;guaranteedFavor=Number(guaranteedFavor)+chaosDraws;
  }
  delete nc.battleReportDraft;
  nextState.smithing=smithingData(nextState);
  nextState.smithing.favor+=guaranteedFavor;
  nc.postBattleRewards=[];
  nc.favorEarned=guaranteedFavor;
  const completed=completeEncounter(nextState,actor);
  if(!completed.regionComplete&&!completed.runComplete&&completed.current){
    completed.smithing=smithingData(completed);
    const affordableCorporate=availableBellBearings(completed).filter(b=>{
      const cost=typeof tcEffectiveSmithingContractCost==='function'?tcEffectiveSmithingContractCost(completed,b):smithingContractCost(b);
      return completed.smithing.favor>=cost;
    });
    if(!completed.smithing.activeContract&&affordableCorporate.length)completed.smithing.pendingCorporateForEncounterId=completed.current.id;
  }
  completed.sharedRewardDraw=draws>0?{
    id:`${encounterId}:${Date.now()}`,
    encounterId,
    count:draws,
    boss:c.target?.name||'Enemy Felled',
    filedBy:actor,
    guaranteedFavor
  }:null;
  completed.sharedRewardReveal=null;
  return {state:completed,draws,guaranteedFavor};
}

finalizePostBattleReport=async function(){
  if(window.__tcReportBusy)return;
  const state=run?.state,c=state?.current;if(!c)return;
  const encounterId=c.id,actor=playerName();
  const initial=tcBuildSharedBattleReportCompletion(state,encounterId,actor);
  if(!initial)return setToast('Finish the shared battle report before filing the victory.');
  window.__tcReportBusy=true;
  const submit=document.querySelector('#finishBattleReport');
  if(submit){submit.disabled=true;submit.textContent='Recording victory…';}
  try{
    const saved=await commit(initial.state,{
      successToast:'Post-battle report filed. Guaranteed Favor and bonus draws are shared.',
      retryBuilder:(latest)=>tcBuildSharedBattleReportCompletion(latest,encounterId,actor)?.state||null
    });
    if(saved){
      postBattleReport=null;
      pendingRewardReveal=null;
      const current=run?.state?.current;
      if(!run?.state?.regionComplete&&!run?.state?.runComplete&&current){pendingRevealId=current.id;uiScreen='encounter';}
    }
  }finally{window.__tcReportBusy=false;}
};
/* --- End shared post-battle report sync --- */
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('shared report script marker missing')
s=s[:idx]+js+'\n'+s[idx:]

required=[
    'function tcSharedBattleReportDraft(state=run?.state)',
    'battleReportDraft',
    'function tcBuildSharedBattleReportChoice(latest,encounterId,kind,value,actor)',
    'retryBuilder:build',
    'const draft=tcSharedBattleReportDraft(state);',
    "const guaranteedText=reportReady?`+${preview.guaranteedFavor}`:'—';",
    'This exact shared total will be awarded no matter which phone files the report.',
    'function tcBuildSharedBattleReportCompletion(latest,encounterId,actor)',
    'nextState.smithing.favor+=guaranteedFavor;',
    'nc.favorEarned=guaranteedFavor;',
    'guaranteedFavor\n  }:null;',
    'retryBuilder:(latest)=>tcBuildSharedBattleReportCompletion(latest,encounterId,actor)?.state||null',
]
for needle in required:
    if needle not in s: raise SystemExit('shared post-battle report invariant missing: '+needle)

if s.count('/* --- Shared post-battle report sync --- */')!=1:
    raise SystemExit('shared post-battle report layer duplicated')

p.write_text(s)
print('Shared post-battle report applied: both phones mirror choices and the same guaranteed Favor total.')
