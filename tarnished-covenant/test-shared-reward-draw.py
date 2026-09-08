from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or f'missing shared reward invariant: {needle}')

def forbid(needle,msg=None):
    if needle in html: raise SystemExit(msg or f'forbidden shared reward behavior: {needle}')

# Filing the battle report creates a single shared pending payout; it does not
# decide the random rewards on the reporting phone.
for needle in [
    'completed.sharedRewardDraw=draws>0?',
    'count:draws,',
    "filedBy:playerName()",
    'completed.sharedRewardReveal=null;',
    "const rewardText=draws>0?'Shared Covenant reward ready to draw.'",
]: require(needle)
forbid('for(let i=0;i<draws;i++) rewards.push(drawCovenantReward(nextState));')

# Either phone sees the same draw gate.
for needle in [
    'function tcSharedRewardDrawPending(state)',
    'function renderSharedRewardDraw()',
    'Either Tarnished may draw this payout.',
    'id="tcDrawSharedReward"',
    'function tcClaimSharedRewardDraw()',
]: require(needle)

# First successful CAS consumes the pending draw. A stale second phone cannot
# build another reward result after the draw ID has disappeared or a reveal exists.
for needle in [
    'if(!pendingDraw||pendingDraw.id!==draw.id||latest?.sharedRewardReveal)return null;',
    'next.sharedRewardDraw=null;',
    'retryBuilder:(latest)=>tcBuildClaimedSharedReward(latest,draw,payload.rewards,payload.deltas,drawer)',
]: require(needle)

# The one result is shared and remembers who physically initiated the draw.
for needle in [
    'next.sharedRewardReveal={',
    'rewards:structuredClone(rewards||[])',
    'drawnBy:drawer,',
    'seenBy:[]',
    'rewardDrawnBy=drawer;',
]: require(needle)

# Reward economy is applied once to shared state, and stale Encounter screens are
# blocked until the shared payout is resolved.
for needle in [
    "const keys=['favor','chaosRefreshes','riteRefreshes','appealWaivers','aviaryTickets'];",
    'sm[key]=Number(sm[key]||0)+Number(delta||0);',
    "if(tcSharedRewardDrawPending(state)||tcSharedRewardUnresolved(state))return setToast('Finish the previous shared Covenant reward first.');",
    'if(tcSharedRewardDrawPending(run?.state))return renderSharedRewardDraw();',
]: require(needle)

# Tiny model check: one pending ID can only be consumed once.
def claim(latest_id,draw_id,reveal=False):
    return latest_id==draw_id and not reveal
assert claim('A','A')
assert not claim(None,'A')
assert not claim('B','A')
assert not claim('A','A',True)

print('Tarnished Covenant single shared reward draw invariants: PASS')
