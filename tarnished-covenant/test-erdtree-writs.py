from pathlib import Path
import re

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or 'missing Erdtree Writ invariant: '+needle)

def forbid(needle,msg=None):
    if needle in html: raise SystemExit(msg or 'forbidden Erdtree Writ behavior: '+needle)

# Exactly seven real Physick-bearing Minor Erdtree targets are represented,
# including the two separate Caelid/Dragonbarrow Putrid Avatars that the old
# broad Caelid pool collapsed into one generic boss name.
start=html.find('const TC_ERDTREE_TARGETS=[')
end=html.find('];',start)
if start<0 or end<0: raise SystemExit('Erdtree target registry missing')
registry=html[start:end]
ids=re.findall(r"\{id:'([^']+)'",registry)
expected=['weeping','liurnia-east','liurnia-west','caelid','dragonbarrow','mountaintops','snowfield']
if ids!=expected: raise SystemExit(f'Erdtree target registry drift: {ids}')
for tear in [
    'Opaline Bubbletear','Crimsonburst Crystal Tear','Magic-Shrouding Cracked Tear',
    'Lightning-Shrouding Cracked Tear','Holy-Shrouding Cracked Tear','Greenburst Crystal Tear',
    'Flame-Shrouding Cracked Tear','Opaline Hardtear','Stonebarb Cracked Tear',
    'Crimson Bubbletear','Thorny Cracked Tear'
]: require(tear)

# The Writ is finite. Legacy Avatar victories reduce the number that can still
# enter circulation, and spending one never replenishes lifetime issuance.
for needle in [
    'const TC_ERDTREE_WRIT_CHANCE=0.07;',
    'function tcLegacyErdtreeClearIds(state)',
    'return Math.max(0,TC_ERDTREE_TARGETS.length-tcLegacyErdtreeClearIds(state).length);',
    'return Math.max(0,tcErdtreeWritIssueCap(state)-Number(sm.erdtreeWritsAwarded||0));',
    'sm.erdtreeWrits=Number(sm.erdtreeWrits||0)+1;',
    'sm.erdtreeWritsAwarded=Number(sm.erdtreeWritsAwarded||0)+1;',
    'next.smithing.erdtreeWrits=Math.max(0,Number(next.smithing.erdtreeWrits||0)-1);',
]: require(needle)

# Inventory and lifetime issuance participate in shared reward payout CAS deltas.
for needle in [
    'erdtreeWrits: Number(raw.erdtreeWrits || 0)',
    'erdtreeWritsAwarded: Number(raw.erdtreeWritsAwarded || 0)',
    'erdtreeAvatarClears: Array.isArray(raw.erdtreeAvatarClears)',
    "'jointAppeals','erdtreeWrits','erdtreeWritsAwarded'",
]: require(needle)

# The seven target encounters no longer belong to normal Covenant boss draws.
# Scadutree Avatar is deliberately unrelated and must remain available in DLC.
for needle in [
    "'Weeping Peninsula':['Erdtree Avatar']",
    "'Liurnia of the Lakes':['Erdtree Avatar (Liurnia Northeast)','Erdtree Avatar(Liurnia Southwest)']",
    "'Caelid':['Putrid Avatar']",
    "'Mountaintops of the Giants':['Erdtree Avatar','Putrid Avatar']",
    'regions[regionName].bosses=regions[regionName].bosses.filter(keep);',
    'SHEET_BOSS_POOLS[regionName]=SHEET_BOSS_POOLS[regionName].filter(keep);',
    'Scadutree Avatar',
]: require(needle)
if "'Scadu Altus + Shadow Keep · DLC':['Scadutree Avatar']" in html:
    raise SystemExit('Scadutree Avatar was incorrectly added to Writ removals')

# Consecrated Snowfield cannot be spent early; all other targets require their
# broad region to have actually been reached.
for needle in [
    'function tcErdtreeRegionReached(state,target)',
    "target.region===state.region||(state.clearedRegions||[]).includes(target.region)||(state.history||[]).some(x=>x?.region===target.region)",
    "tcBossActuallyDefeated(state,'Commander Niall')",
    "target.snowfield?'Requires Consecrated Snowfield access via Commander Niall.'",
]: require(needle)

# Redemption is one shared, race-safe state mutation and intentionally grants no
# normal Covenant encounter/region/reward progress.
for needle in [
    'function tcBuildErdtreeWritSpend(latest,targetId,actor)',
    'next.smithing.erdtreeAvatarClears=Array.from(new Set(',
    'retryBuilder:(latest)=>tcBuildErdtreeWritSpend(latest,targetId,playerName())',
    'This does not count as a Covenant encounter, regional clear, or reward payout.',
]: require(needle)
bstart=html.find('function tcBuildErdtreeWritSpend(')
bend=html.find('let tcErdtreeWritBusy=',bstart)
if bstart<0 or bend<0: raise SystemExit('Erdtree redemption builder block missing')
block=html[bstart:bend]
for bad in ['completeEncounter(','history.push(','regionProgress','postBattleRewards','sharedRewardDraw']:
    if bad in block: raise SystemExit('Erdtree Writ incorrectly grants normal progression: '+bad)

# Ledger presentation exposes current inventory, remaining finite issuance, and
# the selectable target/tear list.
for needle in [
    'minor erdtree authorization',
    'Review Erdtree Targets',
    'data-use-erdtree-writ',
    'data-erdtree-target=',
    'additional Writ',
]: require(needle)

print('Tarnished Covenant Erdtree Writ invariants: PASS — finite seven-target Physick authorization is shared, accessible, and outside normal boss progression.')
