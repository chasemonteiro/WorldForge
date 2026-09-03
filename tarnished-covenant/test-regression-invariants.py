from pathlib import Path
import re

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

# New information architecture must still be the final UI layer.
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

# The tiered Smithing economy must never regress to the obsolete 3-Favor copy.
forbid("Contract commissioned. 3 Favor spent.")
require('return 4 + tier*2;')
require('pool.filter(b=>sm.favor>=smithingContractCost(b))')

# Verify the LAST navigation binder (the runtime one) does not destroy pending
# reveal state. Earlier historical implementations may remain in assembled text.
last_bind = html.rfind('bindNav=function()')
if last_bind < 0:
    raise SystemExit('hardened bindNav override missing')
bind_tail = html[last_bind:last_bind+700]
if 'pendingRevealId = null' in bind_tail or 'pendingRevealId=null' in bind_tail:
    raise SystemExit('final navigation binder still clears pending reveal state')
require("setToast('Finish the current Covenant notice first.')")

# Corporate interruption must be affordability-based and independent of the
# ephemeral decree-reveal flag so refreshing cannot bypass mandatory work.
last_elig = html.rfind('tcMandatoryContractEligible=function(state)')
if last_elig < 0:
    raise SystemExit('hardened corporate eligibility override missing')
elig_tail = html[last_elig:last_elig+450]
if 'pendingRevealId' in elig_tail:
    raise SystemExit('mandatory contract eligibility still depends on ephemeral pendingRevealId')
if 'tcAffordableBellBearings(state)' not in elig_tail:
    raise SystemExit('mandatory contract eligibility is not affordability based')

# Transition ordering: rewards and the post-battle report have priority over
# corporate paperwork; corporate paperwork has priority over normal screens.
require("if(!pendingRewardReveal?.rewards?.length&&!postBattleReport&&tcMandatoryContractEligible(state))")

# Stable historical numbering is a display transform, not mutation of history.
require("(run.state.history?.length||0)-index")

# Guard against accidental duplicate app bootstrap, a nasty failure mode for
# single-file patch pipelines.
if html.count('startApp().catch(') != 1:
    raise SystemExit(f'expected one app bootstrap, found {html.count("startApp().catch(")}')

print('Tarnished Covenant regression invariants: PASS')
