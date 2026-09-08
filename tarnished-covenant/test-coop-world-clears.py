from pathlib import Path

html = Path('tarnished-covenant/index.html').read_text()

def require(needle, message=None):
    if needle not in html:
        raise SystemExit(message or f'missing co-op invariant: {needle}')

def forbid(needle, message=None):
    if needle in html:
        raise SystemExit(message or f'forbidden co-op residue: {needle}')

# Victory is a two-host-world process, not a one-click encounter completion.
for needle in [
    'function tcWorldClears(encounter)',
    'function tcBothWorldsCleared(encounter)',
    "next.current.worldClears=[...clears,slot];",
    "count===2?'Both worlds cleared. File one Covenant battle report.'",
    'One Covenant encounter · two host-world victories · one reward payout.',
    'Rewards remain sealed.',
]:
    require(needle)

forbid("document.querySelector('#complete')?.addEventListener('click',()=>{\n    postBattleReport={encounterId:c.id,rite:null,chaos:null};")

# CRITICAL UI regression guard: the modern Encounter enhancer needs the raw
# #complete button to exist while renderEncounter returns. Co-op controls must
# mount only after the modern Boss / Weapons / Chaos / Rite transformation.
require('/* Co-op victory controls mount after Encounter panel enhancement. */')
forbid('  tcBindCoopWorldClearControls(state,c);')
require("const screen=app.querySelector('.tc-screen');const complete=screen?.querySelector('#complete');")
require("screen.classList.add('tc-encounter-shell');")
require('const rendered=tcRenderRunBeforeCoopWorlds();')
require('tcBindCoopWorldClearControls(run?.state,run?.state?.current);')

render_pos = html.find('const rendered=tcRenderRunBeforeCoopWorlds();')
mount_pos = html.find('tcBindCoopWorldClearControls(run?.state,run?.state?.current);', render_pos)
if render_pos < 0 or mount_pos <= render_pos:
    raise SystemExit('co-op world-clear controls do not mount after the modern Encounter render')

# The post-battle report becomes eligible only after both world slots are present.
require('if(tcBothWorldsCleared(c)){')
require("postBattleReport={encounterId:c.id,rite:null,chaos:null};")

# Reward reveal payload must be persisted in shared state so the non-initiating
# phone can hydrate the exact same reward results.
for needle in [
    'completed.sharedRewardReveal=rewards.length?',
    'rewards:structuredClone(rewards)',
    'seenBy:[]',
    'function tcHydrateSharedRewardReveal(state)',
    'pendingRewardReveal={',
    'sharedId:shared.id',
    'function tcAcknowledgeSharedRewardReveal(data)',
    "['Chase','Morgan'].every(name=>seen.includes(name))",
    'retryBuilder:(latest)=>tcBuildSharedRewardAck(latest,rewardId,me)',
    'void tcAcknowledgeSharedRewardReveal(data);',
]:
    require(needle)

forbid("pendingRewardReveal=rewards.length?{rewards:structuredClone(rewards),boss:c.target?.name||'Enemy Felled',index:0,spinning:true}:null;")

# A previous shared reveal cannot be overwritten by another victory.
require("if(tcSharedRewardUnresolved(state))return setToast('Both Tarnished must review the previous reward first.');")
require('Both Tarnished must review the previous Covenant reward before another victory can be recorded.')

# Basic model checks for the intended state machine.
def clears(values):
    return list(dict.fromkeys(x for x in values if x in ('chase','morgan')))
assert clears([]) == []
assert clears(['chase']) == ['chase']
assert len(clears(['chase','morgan'])) == 2
assert len(clears(['morgan','chase','morgan'])) == 2

# Both identities independently acknowledge the same reveal before it vanishes.
seen = []
seen = list(dict.fromkeys(seen + ['Chase']))
assert not all(x in seen for x in ('Chase','Morgan'))
seen = list(dict.fromkeys(seen + ['Morgan']))
assert all(x in seen for x in ('Chase','Morgan'))

print('Tarnished Covenant co-op + modern Encounter UI invariants: PASS')
