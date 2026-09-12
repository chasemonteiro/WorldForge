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
  // Preserve the normal regional exploration requirement. Once the capstone
  // would otherwise become eligible, however, its physical gate is next.
  const requirement=capstoneRequirement(state);
  if(Number(state.cleared||0)<Number(requirement||0))return null;
  return tcNextUnmetPrerequisite(state,exit);
}

const tcChooseTargetBeforeCapstonePrereqPriority=chooseTarget;
chooseTarget=function(state){
  const due=tcCapstonePrerequisiteDue(state);
  if(due){
    const exit=regions?.[state.region]?.exit||'regional capstone';
    return {name:tcPoolBossName(state.region,due),exit:false,required:true,prerequisiteFor:exit};
  }
  return tcChooseTargetBeforeCapstonePrereqPriority(state);
};

const tcCapstoneChanceBeforePrereqPriority=capstoneChanceForState;
capstoneChanceForState=function(state){
  if(tcCapstonePrerequisiteDue(state))return 0;
  return tcCapstoneChanceBeforePrereqPriority(state);
};

const tcCapstoneBlockBeforePrereqPriority=capstoneBlock;
capstoneBlock=function(state){
  const due=tcCapstonePrerequisiteDue(state);
  if(!due)return tcCapstoneBlockBeforePrereqPriority(state);
  const exit=regions?.[state.region]?.exit||'the regional capstone';
  return `<div class="fate-block"><div class="progress-marks">${progressMarks(state)}</div><div class="fate-title">PREREQUISITE NEXT</div><div class="fate-copy">${h(due)} must be defeated before ${h(exit)} can be drawn.</div></div>`;
};
/* --- End capstone prerequisite priority --- */
'''

idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

required=[
    'function tcCapstonePrerequisiteDue(state)',
    'if(Number(state.cleared||0)<Number(requirement||0))return null;',
    'return tcNextUnmetPrerequisite(state,exit);',
    'const due=tcCapstonePrerequisiteDue(state);',
    'return {name:tcPoolBossName(state.region,due),exit:false,required:true,prerequisiteFor:exit};',
    'if(tcCapstonePrerequisiteDue(state))return 0;',
    'PREREQUISITE NEXT',
]
for needle in required:
    if needle not in s: raise SystemExit('capstone prerequisite priority invariant missing: '+needle)

p.write_text(s)
print('Capstone prerequisite priority applied after normal regional exploration threshold.')
