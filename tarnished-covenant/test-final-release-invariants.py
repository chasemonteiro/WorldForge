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

# Reward probabilities remain owned by one exact expanded 100% table.
reward_start = html.find('function drawCovenantReward(state){')
reward_end = html.find('\n}', reward_start)
if reward_start < 0 or reward_end < 0:
    raise SystemExit('drawCovenantReward missing')
reward = html[reward_start:reward_end+2]
for needle in [
    'roll<0.12', 'roll<0.16', 'roll<0.31', 'roll<0.46', 'roll<0.53',
    'roll<0.59', 'roll<0.64', 'roll<0.72', 'roll<0.76', 'roll<0.82',
    'roll<0.87', 'roll<0.93', 'roll<0.97',
    "kind:'aviary'", 'Dynasty Frequent Flier',
    "kind:'veto'", 'Covenant Veto',
    "kind:'clemency'", 'Letter of Clemency',
    "kind:'discount'", 'Union Discount Voucher',
    "kind:'blank'", 'Blank Amendment',
    "kind:'joint'", 'Joint Appeal',
    "kind:'windfall'", 'Treasury Windfall',
]:
    if needle not in reward:
        raise SystemExit('challenge reward table drift: '+needle)
if html.count('function drawCovenantReward(state){') != 1:
    raise SystemExit('reward probability function has multiple owners')

# Every durable reward kind survives smithingData normalization and shared payout deltas.
for needle in [
    'aviaryTickets: Number(raw.aviaryTickets || 0)',
    'freeBossKills: Number(raw.freeBossKills || 0)',
    'bossVetoes: Number(raw.bossVetoes || 0)',
    'clemencies: Number(raw.clemencies || 0)',
    'unionDiscounts: Number(raw.unionDiscounts || 0)',
    'blankAmendments: Number(raw.blankAmendments || 0)',
    'jointAppeals: Number(raw.jointAppeals || 0)',
    "aviary:'✈'", "freeboss:'⚔'", "veto:'↺'", "joint:'⚔⚔'",
    "const keys=['favor','chaosRefreshes','riteRefreshes','appealWaivers','aviaryTickets','freeBossKills','bossVetoes','clemencies','unionDiscounts','blankAmendments','jointAppeals'];",
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
runpy.run_path('tarnished-covenant/test-region-locked-contracts.py')
runpy.run_path('tarnished-covenant/test-coop-world-clears.py')
runpy.run_path('tarnished-covenant/test-multiplayer-invariants.py')
