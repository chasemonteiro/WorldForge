from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Remove an obsolete fixed-cost message left behind after Bell Bearing contract
# costs became tiered. This route is mostly superseded by the corporate notice,
# but keeping it truthful prevents confusing fallback UI.
s = s.replace("successToast:'Contract commissioned. 3 Favor spent.'", "successToast:'Bell Bearing Contract commissioned.'")

js = r'''
/* --- Cross-system regression hardening --- */
function tcAffordableBellBearings(state){
  if(!state)return [];
  const sm=smithingData(state);
  return availableBellBearings(state).filter(b=>sm.favor>=smithingContractCost(b));
}

/* Mandatory corporate work must survive refresh/navigation and must never fire
   unless a contract can actually be paid for. */
tcMandatoryContractEligible=function(state){
  if(!state?.current)return false;
  const sm=smithingData(state);
  return !sm.activeContract && tcAffordableBellBearings(state).length>0;
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
    const saved=await commit(next,{successToast:`Upper Management assigned a Bell Bearing Contract · ${next.smithing?.activeContract?.cost||'Favor'} spent.`});
    if(saved)renderSmithingContract();else renderRun();
  });
};

smithingHubMarkup=function(state){
  const sm=smithingData(state);
  const affordable=tcAffordableBellBearings(state);
  if(!sm.activeContract&&affordable.length){
    const nextCost=Math.min(...affordable.map(smithingContractCost));
    return `<div class="tc-forge-notice quiet tc-corporate-pending"><div class="tc-forge-glyph">◈</div><div><div class="tc-kicker ember">upper management review pending</div><div class="tc-forge-title">${sm.favor} Smithing Favor Has Been Noticed</div><div class="tc-muted">Corporate has an actionable Bell Bearing matter on file · ${nextCost} Favor minimum.</div></div><span class="tc-forge-arrow">…</span></div>`;
  }
  return tcSmithingHubBeforeIA(state);
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

/* Keep stale overlays from surviving a screen transition caused by shared-state
   updates or a successful save. */
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
    'tcAffordableBellBearings',
    'tcTransitionIsLocked',
    'Finish the current Covenant notice first.',
    'Corporate records changed. Rechecking the file.',
    'tcShowAppealMenuBeforeHardening'
]:
    if needle not in s:
        raise SystemExit('regression hardening invariant missing: '+needle)

p.write_text(s)
