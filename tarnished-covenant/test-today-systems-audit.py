from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or 'missing audit invariant: '+needle)

# Guaranteed Favor is a flat +1 per completed Covenant encounter. Rite/Chaos
# still determine bonus reward draws, never additional guaranteed Favor.
require('let draws=0,guaranteedFavor=1;')
for forbidden in [
    'guaranteedFavor+=riteDraws;',
    'guaranteedFavor+=chaosDraws;',
    'guaranteedFavor=Number(guaranteedFavor)+riteDraws;',
    'guaranteedFavor=Number(guaranteedFavor)+chaosDraws;',
]:
    if forbidden in html:
        raise SystemExit('audit: per-source Favor award returned: '+forbidden)

# Live reward observation must live in the active synchronized override, never the
# retained legacy reward machine, and must survive a PWA restart.
active_start=html.rfind('renderRewardMachine=function(){')
active_end=html.find('/* --- End synchronized shared reward reveal --- */',active_start)
if active_start<0 or active_end<0: raise SystemExit('audit: synchronized reward machine missing')
active=html[active_start:active_end]
hook='tcRememberSharedRewardObserved(shared,displayIndex,me);'
if active.count(hook)!=1: raise SystemExit('audit: active reward watch hook count is not one')
if hook in html[:active_start]: raise SystemExit('audit: reward watch hook landed in legacy machine')
for needle in ['result.isConnected','index:tcSharedRewardFirstMissingIndex(shared,me),','if(reduced||data.spinning===false){finish();}','localStorage.getItem(key)','localStorage.setItem(key,JSON.stringify(seen))']:
    require(needle)
if 'sessionStorage.getItem(key)' in html or 'sessionStorage.setItem(key' in html:
    raise SystemExit('audit: reward watch still depends on sessionStorage')

# Boss access rules must cover the newly-audited route constraints and must keep
# Sanctioned Boss Kill from deadlocking required Remembrances.
for needle in [
    'function tcIsRequiredRemembranceBoss(state,name)',
    'const TC_CONSECRATED_SNOWFIELD_BOSSES=[',
    "return tcBossActuallyDefeated(state,'Commander Niall')?null:'Commander Niall';",
    'function tcMoonlightAltarAccessible(state)',
    "tcBossActuallyDefeated(state,'Royal Knight Loretta')&&tcBossActuallyDefeated(state,'Astel, Naturalborn of the Void')",
    "'count ymir mother of fingers':'Metyr, Mother of Fingers'",
    "tcIsRequiredRemembranceBoss(state,name))continue;",
    "!tcBossRandomAccessible(state,name))continue;",
]: require(needle)

# A first host-world victory freezes encounter-mutating actions until 2/2, while
# unrelated inventory actions can remain available.
for needle in [
    'function tcEncounterMutationLocked(state=run?.state)',
    'Encounter terms lock after the first host-world victory.',
    'const tcShowAppealMenuBeforeAudit=showAppealMenu;',
    'const tcResolveWeaponAppealBeforeAudit=tcResolveWeaponAppeal;',
    'const tcAuditUseCovenantBoonCore=useCovenantBoon;',
    'const tcForfeitBoonBeforeAudit=tcForfeitBoon;',
    'const tcBuildClemencyBeforeAudit=tcBuildClemency;',
    'const tcBuildJointAppealBeforeAudit=tcBuildJointAppeal;',
]: require(needle)
if 'tcUseCovenantBoonBefore' in html:
    raise SystemExit('audit: retired refresh-wrapper naming has returned')

# Veto is optional-only and stale-state safe.
for needle in [
    'if(c.target?.required||c.target?.prerequisiteFor)return false;',
    'tcIsRequiredRemembranceBoss(state,c.target?.name)',
    'function tcBossVetoReplacementLegal(state,replacement,oldBoss)',
    'const available=availableRegionalBosses(state);',
    'tcBuildBossVeto=function(latest,encounterId,oldBoss,replacement,actor)',
    'if(!tcBossVetoReplacementLegal(latest,replacement,oldBoss))return null;',
]: require(needle)

# Today's intended appeal distinction stays intact: normal Both is two penalties,
# one deliberately spent waiver covers the appeal, Joint Appeal is zero-penalty.
for needle in [
    'const tcChangeWeaponsBeforeDoubleAppealPenalty=changeWeapons;',
    "tcChangeWeaponsBeforeDoubleAppealPenalty(state,actor,'chase',false)",
    "tcChangeWeaponsBeforeDoubleAppealPenalty(next,actor,'morgan',false)",
    'Two penalties were added.',
    'function tcBuildJointAppeal(latest,encounterId,oldChase,oldMorgan,newChase,newMorgan,actor)',
    'Both weapons were reassigned with no penalty.',
]: require(needle)

# Expanded random table remains the exact agreed 100% distribution.
for needle in [
    'if(roll<0.12){sm.favor+=1;', 'if(roll<0.16){sm.favor+=2;',
    'if(roll<0.31){sm.chaosRefreshes+=1;', 'if(roll<0.46){sm.riteRefreshes+=1;',
    'if(roll<0.53){sm.appealWaivers+=1;', 'if(roll<0.59){sm.aviaryTickets+=1;',
    'if(roll<0.64){const tax=pick(TC_COVENANT_TAXES);', 'if(roll<0.74){sm.freeBossKills+=1;',
    'if(roll<0.78){sm.bossVetoes+=1;', 'if(roll<0.83){sm.clemencies+=1;',
    'if(roll<0.88){sm.unionDiscounts+=1;', 'if(roll<0.93){sm.blankAmendments+=1;',
    'if(roll<0.97){sm.jointAppeals+=1;', "sm.favor+=3;return {kind:'windfall'",
]: require(needle)

print('Tarnished Covenant today-systems audit: PASS — rewards, flat +1 Favor, appeals, co-op locks, Veto safety, and boss access all hardened.')
