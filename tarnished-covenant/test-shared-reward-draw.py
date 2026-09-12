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

# Either phone sees the same one-draw gate.
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

# Reward economy must mutate next.smithing itself, not the detached normalized
# object returned by smithingData(). This was the bug that lost earned boons.
require('const next=smithingCopy(latest),sm=next.smithing;')
forbid('const next=smithingCopy(latest),sm=smithingData(next);')
require('sm[key]=Number(sm[key]||0)+Number(delta||0);')

# The one result is shared and remembers who physically initiated the draw.
for needle in [
    'next.sharedRewardReveal={',
    'rewards:structuredClone(rewards||[])',
    'drawnBy:drawer,',
    'revealIndex:0,',
    'seenBy:[]',
    'rewardDrawnBy=drawer;',
]: require(needle)

# Reveal progression is shared. Only the drawing identity can advance to the
# next reward; the partner mirrors the new index automatically through sync.
for needle in [
    'function tcSharedRewardIndex(shared)',
    'function tcBuildSharedRewardAdvance(latest,rewardId,expectedIndex,identity)',
    'if(!shared||shared.id!==rewardId||shared.drawnBy!==identity)return null;',
    'next.sharedRewardReveal={...structuredClone(shared),revealIndex:currentIndex+1};',
    'tcHydrateSharedRewardReveal=function(state)',
    'sharedIndex,',
    'renderRewardMachine=function()',
    'const isDrawer=shared.drawnBy===me;',
    'Your screen will advance automatically.',
    'if(hasNext){void tcAdvanceSharedRewardReveal(data);return;}',
]: require(needle)

# The partner never gets a local independent next-reward advancement path. The
# final Continue remains per-phone acknowledgement so the reveal cannot vanish
# before both devices have reached the final reward.
require('void tcAcknowledgeSharedRewardReveal(data);')
require("['Chase','Morgan'].every(name=>seen.includes(name))")

# Reward economy is applied once to shared state, and stale Encounter screens are
# blocked until the shared payout is resolved.
for needle in [
    "const keys=['favor','chaosRefreshes','riteRefreshes','appealWaivers','aviaryTickets'];",
    "if(tcSharedRewardDrawPending(state)||tcSharedRewardUnresolved(state))return setToast('Finish the previous shared Covenant reward first.');",
    'if(tcSharedRewardDrawPending(run?.state))return renderSharedRewardDraw();',
]: require(needle)

# Tiny model checks for one claim and monotonic shared reveal advancement.
def claim(latest_id,draw_id,reveal=False):
    return latest_id==draw_id and not reveal
assert claim('A','A')
assert not claim(None,'A')
assert not claim('B','A')
assert not claim('A','A',True)

def advance(current,expected,total,is_drawer=True):
    return is_drawer and current==expected and current<total-1
assert advance(0,0,3)
assert not advance(1,0,3)
assert not advance(2,2,3)
assert not advance(0,0,3,False)

print('Tarnished Covenant shared reward persistence + synchronized reveal invariants: PASS')
