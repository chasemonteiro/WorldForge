from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or f'missing capstone-prerequisite RNG invariant: {needle}')

for needle in [
    'function tcCapstonePrerequisiteDue(state)',
    "if(!state?.region||state.region==='The Erdtree')return null;",
    'const requirement=capstoneRequirement(state);',
    'if(Number(state.cleared||0)<Number(requirement||0))return null;',
    'return tcNextUnmetPrerequisite(state,exit);',
    'const tcChooseTargetBeforeCapstonePrereqPriority=chooseTarget;',
    'const proposed=tcChooseTargetBeforeCapstonePrereqPriority(state);',
    'if(!proposed?.exit)return proposed;',
    'return {name:tcPoolBossName(state.region,due),exit:false,required:true,prerequisiteFor:exit};',
]: require(needle)

# The physical dependency graph remains intact.
for needle in [
    "'godrick the grafted':'Margit, The Fell Omen'",
    "'rennala queen of the full moon':'Red Wolf of Radagon'",
    "'morgott the omen king':'Godfrey, First Elden Lord'",
    "'godfrey first elden lord':'Draconic Tree Sentinel'",
    "'maliketh the black blade':'Godskin Duo'",
    "'godfrey first elden lord hoarah loux':'Sir Gideon Ofnir, the All-Knowing'",
]: require(needle)

start=html.find('/* --- Capstone prerequisite priority --- */')
end=html.find('/* --- End capstone prerequisite priority --- */',start)
if start<0 or end<0: raise SystemExit('capstone prerequisite layer missing')
block=html[start:end]
if 'if(tcCapstonePrerequisiteDue(state))return 0;' in block:
    raise SystemExit('capstone RNG is still being disabled by an unmet prerequisite')
if 'PREREQUISITE NEXT' in block:
    raise SystemExit('old automatic prerequisite-next UI remains')
if 'if(!proposed?.exit)return proposed;' not in block:
    raise SystemExit('prerequisite substitution is not gated on an actual capstone roll')

print('Tarnished Covenant capstone prerequisite RNG: PASS')
