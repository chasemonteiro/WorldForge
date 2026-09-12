from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

required=[
    "TC_REWARD_OBSERVED_PREFIX='tc-shared-reward-observed:'",
    'function tcSharedRewardObservedIndices(shared)',
    'function tcRememberSharedRewardObserved(shared,index)',
    'function tcSharedRewardObservedAll(shared)',
    '&&!tcSharedRewardObservedAll(shared)',
    'if(!catchUp&&!isDrawer)tcRememberSharedRewardObserved(shared,displayIndex);',
    "catchUp?'Review Next Reward'",
    'already finished this payout. You are reviewing the same rewards now',
]
for needle in required:
    if needle not in html:
        raise SystemExit('live reward watch invariant missing: '+needle)

# The catch-up replay must still exist for genuinely missed rewards; the fix is
# specifically that a device which visibly observed every index does not replay.
if 'tcSharedRewardNeedsCatchup(shared,identity=playerName())' not in html:
    raise SystemExit('shared catch-up behavior missing')

print('Tarnished Covenant live reward watch/no-duplicate-replay invariants: PASS')
