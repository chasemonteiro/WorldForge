from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Remove obsolete fixed-cost copy left behind after Bell Bearing costs became tiered.
s = s.replace("successToast:'Contract commissioned. 3 Favor spent.'", "successToast:'Bell Bearing Contract commissioned.'")

# A missing comma in the expanded Rite pool is valid JavaScript but changes the
# expression's meaning, silently dropping a large block of Rites from rotation.
rite_gap = "['Clean Workplace','Use Soap and a gesture before the encounter.','Minor',0]\n\n ['Off The Sauce'"
if rite_gap not in s:
    raise SystemExit('expanded Rite comma repair target missing')
s = s.replace(rite_gap, "['Clean Workplace','Use Soap and a gesture before the encounter.','Minor',0],\n ['Off The Sauce'", 1)

# Restarting a Covenant should reset the run, not disconnect the phone that
# initiated the reset. Preserve the room/session and clear only transient UI.
restart_old = """    try {
      await backend.restartRun(run.id, buildFreshState(run.state));
      unsubscribe?.();
      run = null;
      clearSession();
      session = null;
      renderHome();
      setToast('Run cleared.');
"""
restart_new = """    try {
      const oldRun = run;
      const restarted = await backend.restartRun(run.id, buildFreshState(run.state));
      unsubscribe?.();
      run = {...oldRun, ...restarted, joinCode: restarted?.joinCode || oldRun?.joinCode};
      session = {runId:run.id, joinCode:run.joinCode || session?.joinCode, displayName:session?.displayName || playerName()};
      saveSession(session);
      pendingRevealId = null;
      postBattleReport = null;
      pendingRewardReveal = null;
      acknowledgedChaos.clear();
      ledgerView = 'remembrances';
      uiScreen = 'sanctuary';
      subscribe();
      renderRun();
      setToast('Covenant restarted. Same room, fresh run.');
"""
if restart_old not in s:
    raise SystemExit('restart continuity repair target missing')
s = s.replace(restart_old, restart_new, 1)

# The post-battle transition is the authoritative moment when Corporate is
# allowed to notice accumulated Favor. Persist that notice in run state so a
# refresh cannot bypass it, while avoiding mid-fight interruptions.
postbattle_anchor = "  const completed=completeEncounter(nextState,playerName());\n  postBattleReport=null;"
postbattle_replacement = """  const completed=completeEncounter(nextState,playerName());
  if(!completed.regionComplete && !completed.runComplete && completed.current){
    completed.smithing = smithingData(completed);
    const affordableCorporate = availableBellBearings(completed).filter(b=>completed.smithing.favor>=smithingContractCost(b));
    if(!completed.smithing.activeContract && affordableCorporate.length){
      completed.smithing.pendingCorporateForEncounterId = completed.current.id;
    }
  }
  postBattleReport=null;"""
if postbattle_anchor not in s:
    raise SystemExit('post-battle corporate persistence anchor missing')
s = s.replace(postbattle_anchor, postbattle_replacement, 1)

js = r'''
/* --- Cross-system regression hardening --- */

/* smithingData is the normalization boundary for all Covenant inventory. Keep
   the persisted corporate-work marker whenever the object is cloned. */
const tcSmithingDataBeforeHardening=smithingData;
smithingData=function(state){
  const base=tcSmithingDataBeforeHardening(state);
  const raw=state?.smithing||{};
  return {...base,pendingCorporateForEncounterId:raw.pendingCorporateForEncounterId||null};
};

function tcAffordableBellBearings(state){
  if(!state)return [];
  const sm=smithingData(state);
  return availableBellBearings(state).filter(b=>sm.favor>=smithingContractCost(b));
}

/* Region travel used to rebuild a fresh state and silently discard all Smithing
   Favor, Bell Bearings, Masterworks, and reward inventory. Preserve it. A newly
   accessible affordable contract may become pending here because travel is a
   safe transition before the region's first encounter. */
const tcStartNextRegionBeforeHardening=startNextRegion;
startNextRegion=function(state,actor,region,severity=state.severity){
  const next=tcStartNextRegionBeforeHardening(state,actor,region,severity);
  next.smithing=structuredClone(state?.smithing||smithingData(state));
  next.smithing=smithingData(next);
  const affordable=tcAffordableBellBearings(next);
  if(next.current&&!next.smithing.activeContract&&affordable.length){
    next.smithing.pendingCorporateForEncounterId=next.current.id;
  }else{
    next.smithing.pendingCorporateForEncounterId=null;
  }
  return next;
};

/* Commissioning always consumes the persisted notice. This prevents a second
   corporate interruption from resurfacing after the same contract is closed. */
const tcCommissionBeforeHardening=commissionSmithingContract;
commissionSmithingContract=function(state){
  const next=tcCommissionBeforeHardening(state);
  if(next?.smithing)next.smithing.pendingCorporateForEncounterId=null;
  return next;
};

/* Mandatory Corporate work is both affordability-based and explicitly tied to
   the next encounter created at a safe transition. */
tcMandatoryContractEligible=function(state){
  if(!state?.current)return false;
  const sm=smithingData(state);
  return !sm.activeContract && sm.pendingCorporateForEncounterId===state.current.id && tcAffordableBellBearings(state).length>0;
};

renderCorporateContractNotice=function(){
  const state=run.state,sm=smithingData(state),affordable=tcAffordableBellBearings(state),preview=affordable[0];
  if(!preview){renderRun();return;}
  const cost=smithingContractCost(preview);
  app.innerHTML=`<section class="tc-corporate-screen"><div class="tc-corporate-letter"><div class="tc-corporate-stamp">Action<br>Required</div><div class="tc-corporate-overline">Notice From Upper Management</div><h1>Corporate Has Forwarded A Matter</h1><div class="tc-corporate-copy">Your recent performance has attracted administrative attention. A Bell Bearing Contract is now mandatory before normal encounter scheduling may resume.</div><div class="tc-corporate-meta"><strong>${sm.favor} Smithing Favor on file</strong><br>${h(preview.region)} procurement is actionable · contracts currently start at ${cost} Favor.</div><button id="tcReviewMandatoryContract" class="btn gold">Review Mandatory Contract</button><div class="tc-corporate-foot">Hewg has been CC’d. This meeting could not have been an email.</div></div></section>`;
  document.querySelector('#tcReviewMandatoryContract')?.addEventListener('click',async()=>{
    const btn=document.querySelector('#tcReviewMandatoryContract');if(btn)btn.disabled=true;
    const next=commissionSmithingContract(run.state);
    if(!next){setToast('Corporate records changed. Rechecking the file.');renderRun();return;}
    const spent=next.smithing?.activeContract?.cost;
    const saved=await commit(next,{successToast:`Upper Management assigned a Bell Bearing Contract${spent?` · ${spent} Favor spent`:''}.`});
    if(saved)renderSmithingContract();else renderRun();
  });
};

/* The Sanctuary only calls something "pending" when the persisted notice is
   actually queued. Merely having enough Favor during a fight is not enough. */
smithingHubMarkup=function(state){
  const sm=smithingData(state);
  const affordable=tcAffordableBellBearings(state);
  if(!sm.activeContract&&sm.pendingCorporateForEncounterId===state?.current?.id&&affordable.length){
    const nextCost=Math.min(...affordable.map(smithingContractCost));
    return `<div class="tc-forge-notice quiet tc-corporate-pending"><div class="tc-forge-glyph">◈</div><div><div class="tc-kicker ember">upper management review pending</div><div class="tc-forge-title">${sm.favor} Smithing Favor Has Been Noticed</div><div class="tc-muted">Corporate has an actionable Bell Bearing matter on file · ${nextCost} Favor minimum.</div></div><span class="tc-forge-arrow">…</span></div>`;
  }
  return tcSmithingHubBeforeIA(state);
};

/* Compendium snapshots store playerNames as an array. Read old object-shaped
   snapshots too for compatibility, but never throw away custom Tarnished names. */
compendiumNames=function(entry,state){
  const current=typeof covenantNames==='function'?covenantNames(state):['Tarnished One','Tarnished Two'];
  const saved=entry?.playerNames;
  if(Array.isArray(saved))return {chase:saved[0]||current[0]||'Tarnished One',morgan:saved[1]||current[1]||'Tarnished Two'};
  return {
    chase:saved?.chase||saved?.player1||current[0]||'Tarnished One',
    morgan:saved?.morgan||saved?.player2||current[1]||'Tarnished Two'
  };
};

/* A reveal/report is a state transition, not just a screen. Bottom navigation
   must not erase it or let a player skip mandatory paperwork. */
function tcTransitionIsLocked(){
  const state=run?.state;
  if(pendingRewardReveal?.rewards?.length)return true;
  if(postBattleReport)return true;
  if(tcMandatoryContractEligible(state))return true;
  if(pendingRevealId && state?.current?.id===pendingRevealId)return true;
  return false;
}

bindNav=function(){
  document.querySelectorAll('[data-screen]').forEach(btn=>btn.addEventListener('click',()=>{
    if(tcTransitionIsLocked()){
      setToast('Finish the current Covenant notice first.');
      renderRun();
      return;
    }
    uiScreen=btn.dataset.screen;
    renderRun();
  }));
};

/* Avoid stacking duplicate modal sheets under fast taps. */
const tcShowAppealMenuBeforeHardening=showAppealMenu;
showAppealMenu=function(){
  document.querySelector('#tcAppealOverlay')?.remove();
  tcShowAppealMenuBeforeHardening();
};

/* Keep stale overlays from surviving a shared-state update or successful save,
   then enforce persisted Corporate work before normal screens. */
const tcRenderRunBeforeHardening=renderRun;
renderRun=function(){
  document.querySelector('#tcAppealOverlay')?.remove();
  const state=run?.state;
  if(!pendingRewardReveal?.rewards?.length&&!postBattleReport&&tcMandatoryContractEligible(state))return renderCorporateContractNotice();
  return tcRenderRunBeforeHardening();
};
'''

idx = s.rfind('</script>')
if idx < 0:
    raise SystemExit('script end marker missing')
s = s[:idx] + js + '\n' + s[idx:]

for needle in [
    'pendingCorporateForEncounterId',
    'tcAffordableBellBearings',
    'tcStartNextRegionBeforeHardening',
    'structuredClone(state?.smithing||smithingData(state))',
    'tcTransitionIsLocked',
    'Finish the current Covenant notice first.',
    'Corporate records changed. Rechecking the file.',
    'tcShowAppealMenuBeforeHardening',
    'Array.isArray(saved)',
    'Same room, fresh run.'
]:
    if needle not in s:
        raise SystemExit('regression hardening invariant missing: '+needle)

p.write_text(s)
