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

# Final information architecture + maintenance core.
for needle in [
    'tc-encounter-shell','tc-sanctuary-shell','tcEnhanceEncounterPanels',
    'tcEnhanceSanctuaryPanels','tcEnhanceCompendium','tcAffordableBellBearings',
    'tcNormalizeRunState','tcBlockingTransition','tcTransitionIsLocked',
    'tcNavDelegationInstalled'
]: require(needle)

# Tiered Smithing economy.
forbid("Contract commissioned. 3 Favor spent.")
require('return 4 + tier*2;')
require('pool.filter(b=>sm.favor>=smithingContractCost(b))')

# Region changes preserve Smithing / reward inventory and use the shared
# normalization boundary instead of inventing another state shape.
require('const tcStartNextRegionBeforeHardening=startNextRegion;')
require('const source=tcNormalizeRunState(state);')
require('next.smithing=structuredClone(source?.smithing||smithingData(source));')
require('tcNormalizeRunState(next);')

# Navigation is delegated once. The final binder cannot destroy transition
# state or install a fresh listener after every render.
last_bind = html.rfind('bindNav=function()')
if last_bind < 0: raise SystemExit('maintenance bindNav override missing')
bind_tail = html[last_bind:last_bind+1200]
if 'pendingRevealId = null' in bind_tail or 'pendingRevealId=null' in bind_tail:
    raise SystemExit('final navigation binder still clears pending reveal state')
for needle in [
    'if(tcNavDelegationInstalled)return;',
    "app.addEventListener('click',event=>",
    "event.target.closest?.('[data-screen]')",
    "setToast('Finish the current Covenant notice first.')"
]:
    if needle not in bind_tail: raise SystemExit('delegated navigation invariant missing: '+needle)

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

# Transition priority is centralized. Reward/report must precede Corporate,
# Corporate precedes the ordinary encounter reveal.
transition_start=html.rfind('function tcBlockingTransition(')
if transition_start < 0: raise SystemExit('central transition resolver missing')
transition_tail=html[transition_start:transition_start+900]
expected_order=[
    "return 'reward'", "return 'post-battle'", "return 'corporate'", "return 'encounter-reveal'"
]
pos=-1
for needle in expected_order:
    nxt=transition_tail.find(needle)
    if nxt < 0 or nxt <= pos: raise SystemExit('transition priority is missing or out of order: '+needle)
    pos=nxt
require("if(transition==='corporate')return renderCorporateContractNotice();")

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
entry_count=0
for line in rite_chunk.splitlines()[1:]:
    stripped=line.strip()
    if stripped.startswith("['"):
        entry_count += 1
        if not stripped.endswith('],'):
            raise SystemExit('Rite pool entry is not comma-terminated: '+stripped[:80])
if entry_count < 20:
    raise SystemExit(f'expanded Rite pool unexpectedly small: {entry_count} entries')
for expected in ["['Clean Workplace'", "['Off The Sauce'"]:
    if expected not in rite_chunk: raise SystemExit('expected expanded Rite missing: '+expected)

# Stable numbering remains a display transform; no history mutation is needed.
require('(run.state.history?.length||0)-index')
require("document.querySelector('#tcAppealOverlay')?.remove();")

# All primary surfaces share the same physical viewport. Grace and Encounter may
# no longer reserve a fake footer beneath themselves; the fixed nav overlays the
# full-height app just as it does on Ledger / Compendium.
for needle in [
    'One physical viewport across every primary screen',
    'padding:calc(8px + env(safe-area-inset-top)) 14px 0',
    'body:has(.tc-bottom-nav) .app-shell{min-height:100dvh}',
    '.tc-sanctuary-panel{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}',
    '.tc-encounter-panel{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}',
    '.tc-encounter-actions{position:relative;z-index:2;margin-bottom:calc(58px + env(safe-area-inset-bottom))'
]: require(needle)

# Single-file patch pipelines are especially vulnerable to accidental duplicate
# bootstraps. There must be exactly one application start.
if html.count('startApp().catch(') != 1:
    raise SystemExit(f'expected one app bootstrap, found {html.count("startApp().catch(")}')

print('Tarnished Covenant regression invariants: PASS')
