from pathlib import Path

html = Path('tarnished-covenant/index.html').read_text()

def require(needle, message=None):
    if needle not in html:
        raise SystemExit(message or f'missing regression invariant: {needle}')

def forbid(needle, message=None):
    if needle in html:
        raise SystemExit(message or f'forbidden stale behavior remains: {needle}')

# Core app surfaces / controls must survive every late patch.
for needle in [
    'function renderSanctuary()',
    'function renderEncounter()',
    'function renderPostBattleReport()',
    'function finalizePostBattleReport()',
    'function renderLedger()',
    'function renderSettings()',
    'function renderRegionComplete()',
    'function renderRunComplete()',
    'function commissionSmithingContract(state)',
    'function claimSmithingBearing(state)',
    'function triggerChaos(state, actor)',
    'id="complete"',
    'id="appealOpen"',
    'id="finishBattleReport"',
    'id="refreshApp"',
    'id="restartRun"',
    'data-ledger-view="compendium"',
    'data-ledger-view="smithing"',
]:
    require(needle)

# Information architecture must survive the hardening layer.
for needle in [
    'tc-encounter-shell',
    'tc-sanctuary-shell',
    'tcEnhanceEncounterPanels',
    'tcEnhanceSanctuaryPanels',
    'tcEnhanceCompendium',
    'tcAffordableBellBearings',
    'tcTransitionIsLocked',
]:
    require(needle)

# The tiered Smithing economy must never regress to obsolete fixed-cost behavior.
forbid("Contract commissioned. 3 Favor spent.")
require('return 4 + tier*2;')
require('pool.filter(b=>sm.favor>=smithingContractCost(b))')

# Region changes must preserve all Smithing / reward inventory rather than
# silently rebuilding an empty smithing object.
require('const tcStartNextRegionBeforeHardening=startNextRegion;')
require('next.smithing=structuredClone(state?.smithing||smithingData(state));')
require('next.smithing=smithingData(next);')

# Verify the LAST navigation binder (runtime one) does not destroy transition
# state. Historical implementations may remain earlier in assembled text.
last_bind = html.rfind('bindNav=function()')
if last_bind < 0:
    raise SystemExit('hardened bindNav override missing')
bind_tail = html[last_bind:last_bind+800]
if 'pendingRevealId = null' in bind_tail or 'pendingRevealId=null' in bind_tail:
    raise SystemExit('final navigation binder still clears pending reveal state')
require("setToast('Finish the current Covenant notice first.')")

# Corporate interruption must be persisted, affordability-based, tied to the
# next encounter, and independent of ephemeral pendingRevealId.
require('pendingCorporateForEncounterId')
require('completed.smithing.pendingCorporateForEncounterId = completed.current.id;')
last_elig = html.rfind('tcMandatoryContractEligible=function(state)')
if last_elig < 0:
    raise SystemExit('hardened corporate eligibility override missing')
elig_tail = html[last_elig:last_elig+650]
if 'pendingRevealId' in elig_tail:
    raise SystemExit('mandatory contract eligibility still depends on ephemeral pendingRevealId')
for needle in ['sm.pendingCorporateForEncounterId===state.current.id','tcAffordableBellBearings(state).length>0']:
    if needle not in elig_tail:
        raise SystemExit('mandatory contract eligibility missing safe-transition guard: '+needle)
require('next.smithing.pendingCorporateForEncounterId=null;')

# A newly accessible contract after region travel is also a safe transition.
require('next.smithing.pendingCorporateForEncounterId=next.current.id;')

# Custom character names in archived entries are arrays in current saves and
# must remain readable; also preserve compatibility with older object snapshots.
require('compendiumNames=function(entry,state)')
require('if(Array.isArray(saved))')
require("saved[0]||current[0]||'Tarnished One'")
require("saved[1]||current[1]||'Tarnished Two'")

# Rewards/report have priority over Corporate paperwork; Corporate has priority
# over normal screens.
require("if(!pendingRewardReveal?.rewards?.length&&!postBattleReport&&tcMandatoryContractEligible(state))")

# Stable historical numbering remains display-only.
require('(run.state.history?.length||0)-index')

# Fast taps must not stack appeal overlays.
require("document.querySelector('#tcAppealOverlay')?.remove();")

# Guard against accidental duplicate app bootstrap, a nasty failure mode for
# single-file patch pipelines.
if html.count('startApp().catch(') != 1:
    raise SystemExit(f'expected one app bootstrap, found {html.count("startApp().catch(")}')

print('Tarnished Covenant regression invariants: PASS')
