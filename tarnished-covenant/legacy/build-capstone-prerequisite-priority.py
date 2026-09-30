from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Remove an older generated copy when this late build step is rerun.
s=re.sub(
    r"\n?/\* --- Capstone prerequisite priority --- \*/.*?"
    r"/\* --- End capstone prerequisite priority --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

js=r'''
/* --- Capstone prerequisite priority --- */
function tcCapstonePrerequisiteDue(state){
  if(!state?.region||state.region==='The Erdtree')return null;
  const region=regions?.[state.region];
  const exit=region?.exit;
  if(!exit)return null;
  const requirement=capstoneRequirement(state);
  if(Number(state.cleared||0)<Number(requirement||0))return null;
  return tcNextUnmetPrerequisite(state,exit);
}

// Preserve normal regional RNG. A prerequisite is substituted only when the
// ordinary chooser actually rolls the capstone while its route is still blocked.
const tcChooseTargetBeforeCapstonePrereqPriority=chooseTarget;
chooseTarget=function(state){
  const proposed=tcChooseTargetBeforeCapstonePrereqPriority(state);
  if(!proposed?.exit)return proposed;
  const due=tcCapstonePrerequisiteDue(state);
  if(!due)return proposed;
  const exit=regions?.[state.region]?.exit||proposed.name||'regional capstone';
  return {name:tcPoolBossName(state.region,due),exit:false,required:true,prerequisiteFor:exit};
};
/* --- End capstone prerequisite priority --- */
'''

idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

required=[
    'function tcCapstonePrerequisiteDue(state)',
    'const proposed=tcChooseTargetBeforeCapstonePrereqPriority(state);',
    'if(!proposed?.exit)return proposed;',
    'const due=tcCapstonePrerequisiteDue(state);',
    'return {name:tcPoolBossName(state.region,due),exit:false,required:true,prerequisiteFor:exit};',
]
for needle in required:
    if needle not in s: raise SystemExit('capstone prerequisite RNG invariant missing: '+needle)

for forbidden in [
    'if(tcCapstonePrerequisiteDue(state))return 0;',
    'PREREQUISITE NEXT',
]:
    # Only inspect this generated layer, not unrelated historical/UI text.
    start=s.rfind('/* --- Capstone prerequisite priority --- */')
    end=s.find('/* --- End capstone prerequisite priority --- */',start)
    if forbidden in s[start:end]: raise SystemExit('old forced-prerequisite behavior remains: '+forbidden)

p.write_text(s)
print('Capstone prerequisites now substitute only after a successful capstone roll.')
