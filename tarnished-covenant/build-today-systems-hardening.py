from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# Cross-system hardening for the co-op encounter + strategic reward economy.
# Applied after the final Encounter/appeal layers so all runtime mutations share
# the same one-encounter/two-world lock semantics and Veto validation.
# -----------------------------------------------------------------------------

s=re.sub(
    r"\n?/\* --- Today systems audit hardening --- \*/.*?"
    r"/\* --- End today systems audit hardening --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

js=r'''
/* --- Today systems audit hardening --- */
function tcEncounterMutationLocked(state=run?.state){
  const c=state?.current;if(!c)return false;
  const clears=typeof tcWorldClears==='function'?tcWorldClears(c):(Array.isArray(c.worldClears)?c.worldClears:[]);
  return clears.length>0;
}
function tcEncounterMutationLockMessage(){return 'Encounter terms lock after the first host-world victory. Finish the second world under the same decree.';}

// Normal Weapon Appeals cannot change assignments after one world has already
// been cleared. Re-check at both menu-open and final resolve time for stale UIs.
const tcShowAppealMenuBeforeAudit=showAppealMenu;
showAppealMenu=function(){
  if(tcEncounterMutationLocked())return setToast(tcEncounterMutationLockMessage());
  return tcShowAppealMenuBeforeAudit();
};
const tcResolveWeaponAppealBeforeAudit=tcResolveWeaponAppeal;
tcResolveWeaponAppeal=async function(which,useWaiver){
  if(tcEncounterMutationLocked())return setToast(tcEncounterMutationLockMessage());
  return tcResolveWeaponAppealBeforeAudit(which,useWaiver);
};

// Rite/Chaos amendment and forfeit controls mutate encounter terms too. This
// wrapper uses a distinct audit name so it cannot be confused with retired
// busy-flag stabilization code.
const tcAuditUseCovenantBoonCore=useCovenantBoon;
useCovenantBoon=async function(kind){
  if(tcEncounterMutationLocked())return setToast(tcEncounterMutationLockMessage());
  return tcAuditUseCovenantBoonCore(kind);
};
const tcForfeitBoonBeforeAudit=tcForfeitBoon;
tcForfeitBoon=async function(kind){
  if(tcEncounterMutationLocked())return setToast(tcEncounterMutationLockMessage());
  return tcForfeitBoonBeforeAudit(kind);
};
const tcEncounterBoonsBeforeAudit=tcEncounterBoons;
tcEncounterBoons=function(state){
  if(tcEncounterMutationLocked(state))return `<div class="tc-earned-refreshes"><div class="tc-kicker">encounter terms locked</div><div class="tc-muted">One host world is already cleared. Weapons, Rite, Chaos amendments, and forfeits stay fixed until the second victory.</div></div>`;
  return tcEncounterBoonsBeforeAudit(state);
};

// Treasury actions that alter the current encounter obey the same lock. Their
// builders also check latest shared state so a stale overlay cannot bypass it.
const tcBuildClemencyBeforeAudit=tcBuildClemency;
tcBuildClemency=function(latest,encounterId,key,actor){
  if(tcEncounterMutationLocked(latest))return null;
  return tcBuildClemencyBeforeAudit(latest,encounterId,key,actor);
};
const tcOpenClemencyBeforeAudit=tcOpenClemency;
tcOpenClemency=function(){
  if(tcEncounterMutationLocked())return setToast(tcEncounterMutationLockMessage());
  return tcOpenClemencyBeforeAudit();
};
const tcBuildJointAppealBeforeAudit=tcBuildJointAppeal;
tcBuildJointAppeal=function(latest,encounterId,oldChase,oldMorgan,newChase,newMorgan,actor){
  if(tcEncounterMutationLocked(latest))return null;
  return tcBuildJointAppealBeforeAudit(latest,encounterId,oldChase,oldMorgan,newChase,newMorgan,actor);
};
const tcOpenJointAppealBeforeAudit=tcOpenJointAppeal;
tcOpenJointAppeal=function(){
  if(tcEncounterMutationLocked())return setToast(tcEncounterMutationLockMessage());
  return tcOpenJointAppealBeforeAudit();
};

// A Veto is for an optional assignment only: never a forced prerequisite, a
// required Remembrance, a capstone, or a partially completed two-world encounter.
const tcBossVetoEligibleBeforeAudit=tcBossVetoEligible;
tcBossVetoEligible=function(state){
  const c=state?.current;
  if(!tcBossVetoEligibleBeforeAudit(state)||!c)return false;
  if(c.target?.required||c.target?.prerequisiteFor)return false;
  if(typeof tcIsRequiredRemembranceBoss==='function'&&tcIsRequiredRemembranceBoss(state,c.target?.name))return false;
  return true;
};
function tcBossVetoReplacementLegal(state,replacement,oldBoss){
  if(!state?.current||!replacement?.name||replacement.exit)return false;
  if(tcBossKey(replacement.name)===tcBossKey(oldBoss))return false;
  if(replacement.required||replacement.prerequisiteFor)return false;
  if(typeof tcIsProgressionGateBoss==='function'&&tcIsProgressionGateBoss(replacement.name))return false;
  if(typeof tcIsRequiredRemembranceBoss==='function'&&tcIsRequiredRemembranceBoss(state,replacement.name))return false;
  const available=availableRegionalBosses(state);
  return available.some(name=>tcBossKey(name)===tcBossKey(replacement.name));
}
tcRollVetoReplacement=function(state){
  if(!tcBossVetoEligible(state))return null;
  const current=state.current.target.name;
  const pool=availableRegionalBosses(state).filter(name=>{
    if(tcBossKey(name)===tcBossKey(current))return false;
    if(typeof tcIsProgressionGateBoss==='function'&&tcIsProgressionGateBoss(name))return false;
    if(typeof tcIsRequiredRemembranceBoss==='function'&&tcIsRequiredRemembranceBoss(state,name))return false;
    return true;
  });
  if(!pool.length)return null;
  return {name:pick(pool),exit:false};
};
const tcBuildBossVetoBeforeAudit=tcBuildBossVeto;
tcBuildBossVeto=function(latest,encounterId,oldBoss,replacement,actor){
  if(!tcBossVetoReplacementLegal(latest,replacement,oldBoss))return null;
  return tcBuildBossVetoBeforeAudit(latest,encounterId,oldBoss,replacement,actor);
};

// Make the Ledger accurately show which current-encounter actions are frozen.
const tcCovenantBoonMarkupBeforeAudit=covenantBoonMarkup;
covenantBoonMarkup=function(state){
  let html=tcCovenantBoonMarkupBeforeAudit(state);
  if(!tcEncounterMutationLocked(state))return html;
  html=html.replace(/data-use-clemency(?![^>]*disabled)/g,'data-use-clemency disabled');
  html=html.replace(/data-use-joint-appeal(?![^>]*disabled)/g,'data-use-joint-appeal disabled');
  return html;
};
/* --- End today systems audit hardening --- */
'''
idx=s.rfind('</script>')
if idx<0:raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

required=[
    'function tcEncounterMutationLocked(state=run?.state)',
    'Encounter terms lock after the first host-world victory.',
    'const tcShowAppealMenuBeforeAudit=showAppealMenu;',
    'const tcResolveWeaponAppealBeforeAudit=tcResolveWeaponAppeal;',
    'const tcAuditUseCovenantBoonCore=useCovenantBoon;',
    'const tcForfeitBoonBeforeAudit=tcForfeitBoon;',
    'const tcBuildClemencyBeforeAudit=tcBuildClemency;',
    'const tcBuildJointAppealBeforeAudit=tcBuildJointAppeal;',
    'if(c.target?.required||c.target?.prerequisiteFor)return false;',
    'tcIsRequiredRemembranceBoss(state,c.target?.name)',
    'function tcBossVetoReplacementLegal(state,replacement,oldBoss)',
    'const available=availableRegionalBosses(state);',
    'tcBuildBossVeto=function(latest,encounterId,oldBoss,replacement,actor)',
]
for needle in required:
    if needle not in s:raise SystemExit('today-systems hardening invariant missing: '+needle)

p.write_text(s)
print('Cross-system hardening applied: encounter freeze after 1/2 clears and race-safe optional-only Veto replacements.')
