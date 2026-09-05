from pathlib import Path
import re
import runpy

html = Path('tarnished-covenant/index.html').read_text()

def require(needle, message=None):
    if needle not in html:
        raise SystemExit(message or f'missing final release invariant: {needle}')

def forbid(needle, message=None):
    if needle in html:
        raise SystemExit(message or f'forbidden final release residue: {needle}')

# Reward probabilities remain owned by the challenge-first table.
reward_start = html.find('function drawCovenantReward(state){')
reward_end = html.find('\n}', reward_start)
if reward_start < 0 or reward_end < 0:
    raise SystemExit('drawCovenantReward missing')
reward = html[reward_start:reward_end+2]
for needle in [
    'roll<0.20', 'roll<0.23', 'roll<0.47', 'roll<0.71', 'roll<0.79', 'roll<0.90',
    "kind:'aviary'", 'Dynasty Frequent Flier'
]:
    if needle not in reward:
        raise SystemExit('challenge reward table drift: '+needle)
if html.count('function drawCovenantReward(state){') != 1:
    raise SystemExit('reward probability function has multiple owners')

# Every reward kind must survive smithingData normalization and render correctly.
for needle in [
    'aviaryTickets: Number(raw.aviaryTickets || 0)',
    "aviary:'✈'",
    "kind==='aviary'?'aviary'",
    'Each Dynasty Frequent Flier grants 5 sanctioned trips to the Mohgwyn bird.',
    'Final release reward durability'
]:
    require(needle)

# Completed encounters retain the actual reward list and honor-system outcomes.
for needle in [
    'rewards: structuredClone(encounter?.postBattleRewards || [])',
    "riteOutcome: encounter?.riteForfeited?'Forfeited'",
    "chaosOutcome: encounter?.chaosForfeited?'Forfeited'"
]:
    require(needle)

# Refresh buttons must delegate directly to the real handler. The real handler
# already owns the busy flag; any outer stability wrapper makes every click return early.
core_boon_guard = "if(window.__tcBoonBusy||!run?.state?.current)return;window.__tcBoonBusy=true;"
require(core_boon_guard)
require("const btn=event.target.closest('[data-use-boon]');")
require("if(btn)useCovenantBoon(btn.dataset.useBoon);")
forbid('tcUseCovenantBoonBefore')
forbid("if(typeof useCovenantBoon==='function'&&!window.__tcBoonStabilized)")
if html.count(core_boon_guard) != 1:
    raise SystemExit('expected exactly one Covenant boon busy guard')

# Native Grace only: 100ms accepted taps, local counter, no retired raster renderer.
for needle in [
    'const TC_GRACE_TAP_COOLDOWN_MS=100;',
    'const TC_GRACE_FAVOR_ODDS=5000;',
    'tc-grace-native-svg',
    'Grace wisp tuning',
    'Grace fidget tuning',
    'tc-grace-tap-count',
    'tcIncrementGraceTapCounter(btn)'
]:
    require(needle)
for needle in [
    'TC_GRACE_ART_FRAMES',
    'tc-grace-idle-art-frame',
    'tc-grace-idle-art-stack',
    'TC_GRACE_TAP_COOLDOWN_MS=400'
]:
    forbid(needle)

if html.count('const TC_GRACE_TAP_COOLDOWN_MS=100;') != 1:
    raise SystemExit('expected exactly one live Grace tap cadence')
if html.count('startApp().catch(') != 1:
    raise SystemExit('expected exactly one app bootstrap')

print('Tarnished Covenant final release invariants: PASS')
runpy.run_path('tarnished-covenant/test-multiplayer-invariants.py')
