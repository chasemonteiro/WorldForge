from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

required=[
    "TC_REWARD_OBSERVED_PREFIX='tc-shared-reward-observed:'",
    'function tcSharedRewardObservedIndices(shared,identity=playerName())',
    'function tcRememberSharedRewardObserved(shared,index,identity=playerName())',
    'function tcSharedRewardObservedAll(shared,identity=playerName())',
    'function tcSharedRewardFirstMissingIndex(shared,identity=playerName())',
    'localStorage.getItem(key)',
    'localStorage.setItem(key,JSON.stringify(seen))',
    '&&!tcSharedRewardObservedAll(shared,identity)',
    "catchUp?'Review Next Reward'",
    'already finished this payout. You are reviewing the same rewards now',
    'index:tcSharedRewardFirstMissingIndex(shared,me),',
    'if(reduced||data.spinning===false){finish();}',
]
for needle in required:
    if needle not in html:
        raise SystemExit('live reward watch invariant missing: '+needle)

# The hook must be in the LAST reward-machine implementation, which is the active
# synchronized override. The page intentionally retains an older legacy function.
active_start=html.rfind('renderRewardMachine=function(){')
active_end=html.find('/* --- End synchronized shared reward reveal --- */',active_start)
if active_start<0 or active_end<0:
    raise SystemExit('active synchronized reward machine missing')
active=html[active_start:active_end]
legacy=html[:active_start]
hook='tcRememberSharedRewardObserved(shared,displayIndex,me);'
if active.count(hook)!=1:
    raise SystemExit('active reward machine must contain exactly one observation hook')
if hook in legacy:
    raise SystemExit('reward observation hook incorrectly patched into legacy machine')
for needle in [
    'result.isConnected',
    'tcSharedRewardIndex(run.state.sharedRewardReveal)===displayIndex',
    'const mayAct=catchUp||!hasNext||isDrawer;',
]:
    if needle not in active:
        raise SystemExit('active reward observation safety missing: '+needle)

# Persist across standalone-app restarts; sessionStorage was insufficient for a
# player who watched live, closed the PWA, then reopened after the drawer finished.
if 'sessionStorage.getItem(key)' in html or 'sessionStorage.setItem(key' in html:
    raise SystemExit('reward observation still relies on sessionStorage')

# The catch-up replay must still exist for genuinely missed rewards.
if 'tcSharedRewardNeedsCatchup(shared,identity=playerName())' not in html:
    raise SystemExit('shared catch-up behavior missing')

print('Tarnished Covenant live reward watch invariants: PASS — active synchronized machine, persistent seen-state, no duplicate replay.')
