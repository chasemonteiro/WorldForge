from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or f'missing capstone-prerequisite invariant: {needle}')

for needle in [
    'function tcCapstonePrerequisiteDue(state)',
    "if(!state?.region||state.region==='The Erdtree')return null;",
    'const requirement=capstoneRequirement(state);',
    'if(Number(state.cleared||0)<Number(requirement||0))return null;',
    'return tcNextUnmetPrerequisite(state,exit);',
    'const tcChooseTargetBeforeCapstonePrereqPriority=chooseTarget;',
    'return {name:tcPoolBossName(state.region,due),exit:false,required:true,prerequisiteFor:exit};',
    'const tcCapstoneChanceBeforePrereqPriority=capstoneChanceForState;',
    'if(tcCapstonePrerequisiteDue(state))return 0;',
    'PREREQUISITE NEXT',
]: require(needle)

# The graph itself must still carry the concrete chains that this priority layer
# promotes once the normal regional encounter-count threshold is met.
for needle in [
    "'godrick the grafted':'Margit, The Fell Omen'",
    "'rennala queen of the full moon':'Red Wolf of Radagon'",
    "'morgott the omen king':'Godfrey, First Elden Lord'",
    "'godfrey first elden lord':'Draconic Tree Sentinel'",
    "'maliketh the black blade':'Godskin Duo'",
    "'godfrey first elden lord hoarah loux':'Sir Gideon Ofnir, the All-Knowing'",
]: require(needle)

# This is deliberately NOT a rigid "first fight in every region" system: normal
# exploration still happens until the existing capstone requirement is met.
start=html.find('function tcCapstonePrerequisiteDue(state)')
end=html.find('const tcChooseTargetBeforeCapstonePrereqPriority',start)
if start<0 or end<0: raise SystemExit('capstone prerequisite helper block missing')
block=html[start:end]
if 'capstoneRequirement(state)' not in block or 'state.cleared' not in block:
    raise SystemExit('capstone prerequisite priority bypasses normal regional exploration threshold')

print('Tarnished Covenant capstone prerequisite priority: PASS')
