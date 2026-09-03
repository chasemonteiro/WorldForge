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
    'function renderSanctuary()', 'function renderEncounter()',
    'function renderPostBattleReport()', 'function finalizePostBattleReport()',
    'function renderLedger()', 'function renderSettings()',
    'function renderRegionComplete()', 'function renderRunComplete()',
    'function commissionSmithingContract(state)', 'function claimSmithingBearing(state)',
    'function triggerChaos(state, actor)', 'id="complete"', 'id="appealOpen"',
    'id="finishBattleReport"', 'id="refreshApp"', 'id="restartRun"',
    'data-ledger-view="compendium"', 'data-ledger-view="smithing"',
]: require(needle)

for needle in ['tc-encounter-shell','tc-sanctuary-shell','tcEnhanceEncounterPanels','tcEnhanceSanctuaryPanels','tcEnhanceCompendium','tcAffordableBellBearings','tcTransitionIsLocked']:
    require(needle)

# Tiered Smithing economy.
forbid("Contract commissioned. 3 Favor spent.")
require('return 4 + tier*2;')
require('pool.filter(b=>sm.favor>=smithingContractCost(b))')

# Region changes preserve Smithing / reward inventory.
require('const tcStartNextRegionBeforeHardening=startNextRegion;')
require('next.smithing=structuredClone(state?.smithing||smithingData(state));')
require('next.smithing=smithingData(next);')

# Final navigation binder cannot destroy transition state.
last_bind = html.rfind('bindNav=function()')
if last_bind < 0: raise SystemExit('hardened bindNav override missing')
bind_tail = html[last_bind:last_bind+800]
if 'pendingRevealId = null' in bind_tail or 'pendingRevealId=null' in bind_tail:
    raise SystemExit('final navigation binder still clears pending reveal state')
require("setToast('Finish the current Covenant notice first.')")

# Corporate interruption is persisted, affordable, safe-transition-bound.
require('pendingCorporateForEncounterId')
require('completed.smithing.pendingCorporateForEncounterId = completed.current.id;')
last_elig = html.rfind('tcMandatoryContractEligible=function(state)')
if last_elig < 0: raise SystemExit('hardened corporate eligibility override missing')
elig_tail = html[last_elig:last_elig+650]
if 'pendingRevealId' in elig_tail: raise SystemExit('mandatory contract eligibility still depends on ephemeral pendingRevealId')
for needle in ['sm.pendingCorporateForEncounterId===state.current.id','tcAffordableBellBearings(state).length>0']:
    if needle not in elig_tail: raise SystemExit('mandatory contract eligibility missing safe-transition guard: '+needle)
require('next.smithing.pendingCorporateForEncounterId=null;')
require('next.smithing.pendingCorporateForEncounterId=next.current.id;')

# Custom names in archived entries.
require('compendiumNames=function(entry,state)')
require('if(Array.isArray(saved))')
require("saved[0]||current[0]||'Tarnished One'")
require("saved[1]||current[1]||'Tarnished Two'")

# Restart must keep this phone in the same room while clearing transient UI.
for needle in [
    'const restarted = await backend.restartRun',
    'run = {...oldRun, ...restarted, joinCode: restarted?.joinCode || oldRun?.joinCode};',
    'saveSession(session);', 'acknowledgedChaos.clear();',
    "uiScreen = 'sanctuary';", 'subscribe();',
    "setToast('Covenant restarted. Same room, fresh run.');"
]: require(needle)

# Semantic validation for the expanded Rite array. Every array-entry line must
# be comma-terminated; JavaScript syntax alone does not catch missing commas here.
start = html.find('const TC_EXTRA_RITES = [')
end = html.find('];', start)
if start < 0 or end < 0: raise SystemExit('TC_EXTRA_RITES block missing')
rite_chunk = html[start:end]
for line in rite_chunk.splitlines()[1:]:
    stripped=line.strip()
    if stripped.startswith("['") and not stripped.endswith('],'):
        raise SystemExit('Rite pool entry is not comma-terminated: '+stripped[:80])
for expected in ["['Clean Workplace'", "['Off The Sauce'", "['The Wall'"]:
    if expected not in rite_chunk: raise SystemExit('expected expanded Rite missing: '+expected)

# Rewards/report precede Corporate; stable numbering remains display-only.
require("if(!pendingRewardReveal?.rewards?.length&&!postBattleReport&&tcMandatoryContractEligible(state))")
require('(run.state.history?.length||0)-index')
require("document.querySelector('#tcAppealOverlay')?.remove();")

if html.count('startApp().catch(') != 1:
    raise SystemExit(f'expected one app bootstrap, found {html.count("startApp().catch(")}')

print('Tarnished Covenant regression invariants: PASS')
