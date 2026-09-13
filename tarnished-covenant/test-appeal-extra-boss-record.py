from pathlib import Path
html=Path('tarnished-covenant/index.html').read_text()

def req(x):
    if x not in html: raise SystemExit('missing appeal extra-boss invariant: '+x)
for x in [
    'function tcAppealPenaltyBossKills(state)',
    'function tcPenanceNeedsBossRecord(p)',
    'function tcBuildAppealBossRecord(latest,encounterId,penanceId,choice,actor)',
    'next.current.penances[j].bossRecord=record;',
    'next.appealPenaltyBossKills=[...tcAppealPenaltyBossKills(next),record];',
    'Record Extra Boss Kill',
    'data-record-appeal-boss=',
    'Minor Erdtree Avatars require and consume an Erdtree Writ.',
    "next=tcBuildErdtreeWritSpend(latest,choice.erdtreeTargetId,actor)",
    'tcDefeatedBossNamesBeforeAppealRecord',
    'tcLegacyErdtreeClearIdsBeforeAppealRecord',
]: req(x)
# The record is bookkeeping only: ordinary extra-boss kills must not consume a
# Sanctioned Boss Kill or grant normal encounter/capstone/reward progress.
start=html.find('function tcBuildAppealBossRecord(')
end=html.find('function tcOpenAppealBossPicker(',start)
block=html[start:end]
for bad in ['freeBossKills-=','completeEncounter(','history.push(','sharedRewardDraw','regionProgress']:
    if bad in block: raise SystemExit('appeal extra-boss record incorrectly mutates progression: '+bad)
print('Weapon Appeal extra-boss recording invariants: PASS')
