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

for needle in [
    'tc-encounter-shell','tc-sanctuary-shell','tcEnhanceEncounterPanels',
    'tcEnhanceSanctuaryPanels','tcEnhanceCompendium','tcAffordableBellBearings',
    'tcNormalizeRunState','tcBlockingTransition','tcTransitionIsLocked',
    'tcNavDelegationInstalled'
]: require(needle)

forbid("Contract commissioned. 3 Favor spent.")
require('return 4 + tier*2;')
require('pool.filter(b=>sm.favor>=smithingContractCost(b))')

require('const tcStartNextRegionBeforeHardening=startNextRegion;')
require('const source=tcNormalizeRunState(state);')
require('next.smithing=structuredClone(source?.smithing||smithingData(source));')
require('tcNormalizeRunState(next);')

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

transition_start=html.rfind('function tcBlockingTransition(')
if transition_start < 0: raise SystemExit('central transition resolver missing')
transition_tail=html[transition_start:transition_start+900]
expected_order=["return 'reward'", "return 'post-battle'", "return 'corporate'", "return 'encounter-reveal'"]
pos=-1
for needle in expected_order:
    nxt=transition_tail.find(needle)
    if nxt < 0 or nxt <= pos: raise SystemExit('transition priority is missing or out of order: '+needle)
    pos=nxt
require("if(transition==='corporate')return renderCorporateContractNotice();")

require('compendiumNames=function(entry,state)')
require('if(Array.isArray(saved))')
require("saved[0]||current[0]||'Tarnished One'")
require("saved[1]||current[1]||'Tarnished Two'")

for needle in [
    'const restarted = await backend.restartRun',
    'run = {...oldRun, ...restarted, joinCode: restarted?.joinCode || oldRun?.joinCode};',
    'saveSession(session);', 'acknowledgedChaos.clear();',
    "uiScreen = 'sanctuary';", 'subscribe();',
    "setToast('Covenant restarted. Same room, fresh run.');"
]: require(needle)

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

require('(run.state.history?.length||0)-index')
require("document.querySelector('#tcAppealOverlay')?.remove();")

# One dynamic viewport and one owner for iPhone safe-area spacing. Geometry must
# be keyed to the explicit run class, never to a dynamically inserted nav element.
for needle in [
    'One dynamic viewport across every primary screen',
    'padding:calc(8px + env(safe-area-inset-top)) 14px 0',
    'body.tc-run-active{',
    'padding:0!important',
    'body.tc-run-active .app-shell',
    'height:100dvh!important;max-height:100dvh!important;min-height:100dvh!important',
    '.tc-sanctuary-panel{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}',
    '.tc-encounter-panel{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}'
]: require(needle)

# The viewport block itself must not wait for Safari to invalidate :has() after
# the persistent nav is mounted.
geometry_start=html.find('/* --- One dynamic viewport across every primary screen --- */')
geometry_end=html.find('</style>',geometry_start)
if geometry_start<0 or geometry_end<0: raise SystemExit('viewport geometry block missing')
geometry=html[geometry_start:geometry_end]
if 'body:has(.tc-bottom-nav)' in geometry or 'html:has(.tc-bottom-nav)' in geometry:
    raise SystemExit('viewport geometry still depends on dynamic nav :has selector')

forbid('@supports(height:100svh)')

if html.count('startApp().catch(') != 1:
    raise SystemExit(f'expected one app bootstrap, found {html.count("startApp().catch(")}')

print('Tarnished Covenant regression invariants: PASS')
