from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# One-time regional capstone defer.
# A defer forces exactly one normal encounter, then ordinary capstone RNG resumes.
# The detour's Chaos is guaranteed to pull from the late tier or worse.
# -----------------------------------------------------------------------------

# Force chooseTarget() to honor the one-encounter normal detour flag.
needle="""function chooseTarget(state) {
  const region = regions[state.region];
  if (state.region === 'The Erdtree') return { name: region.exit, exit: true };
"""
replacement="""function chooseTarget(state) {
  const region = regions[state.region];
  if (state.region === 'The Erdtree') return { name: region.exit, exit: true };
  if(state.capstoneDetourPending){
    const normalPool=availableRegionalBosses(state);
    const fallback=(region.bosses||[]).filter(name=>name!==region.exit);
    const name=pick(normalPool.length?normalPool:fallback);
    if(name)return {name,exit:false};
  }
"""
if needle not in s:
    raise SystemExit('chooseTarget capstone-defer hook missing')
s=s.replace(needle,replacement,1)

# Add shared-state helper before the Encounter renderer.
marker='function renderEncounter() {'
if marker not in s:
    raise SystemExit('renderEncounter marker missing')
helper=r'''
async function tcDeferCapstone(){
  if(window.__tcCapstoneDeferBusy||!run?.state?.current?.target?.exit)return;
  const state=run.state;
  if(state.region==='The Erdtree')return setToast('There is nowhere left to procrastinate.');
  if(state.capstoneDeferUsed)return setToast('The Covenant already granted this region one delay.');
  window.__tcCapstoneDeferBusy=true;
  const btn=document.querySelector('#deferCapstone');if(btn)btn.disabled=true;
  try{
    const next=smithingCopy(state);
    const deferredName=next.current.target.name;
    next.capstoneDeferUsed=true;
    next.capstoneDeferredName=deferredName;
    next.capstoneDetourPending=true;
    next.current=newEncounter(next);
    next.capstoneDetourPending=false;
    next.current.deferredCapstoneDetour=true;
    next.current.deferredCapstoneName=deferredName;
    next.current.covenantDebt='DEFERRED JUDGMENT: you asked for one more fight. Chaos on this detour is guaranteed late-tier.';
    next.lastAction=`${playerName()} deferred ${deferredName}. One debt encounter has been issued.`;
    next.updatedAt=new Date().toISOString();
    pendingRevealId=next.current.id;
    uiScreen='encounter';
    await commit(next,{successToast:'Capstone deferred once. The Covenant has provided worse paperwork.'});
  }finally{window.__tcCapstoneDeferBusy=false;}
}
function tcCapstoneDeferMarkup(state,c){
  if(!c?.target?.exit||state.region==='The Erdtree'||state.capstoneDeferUsed)return '';
  return `<div class="tc-capstone-defer">
    <div><div class="tc-kicker red">one-time regional deferral</div><div class="tc-capstone-defer-copy">Not ready to cash this check? Take exactly one normal encounter first. The capstone then returns to RNG. The detour's Chaos is guaranteed late-tier.</div></div>
    <button id="deferCapstone" type="button" class="btn curse">DEFER ONCE · ACCEPT DEBT ENCOUNTER</button>
  </div>`;
}
'''
s=s.replace(marker,helper+'\n'+marker,1)

# Put the option immediately after the encounter heading/art so it is impossible to miss.
needle="""    <div class=\"tc-kicker gold\" style=\"text-align:center;margin:5px 0 7px\">assigned weapons</div>"""
replacement="""    ${tcCapstoneDeferMarkup(state,c)}
    <div class=\"tc-kicker gold\" style=\"text-align:center;margin:5px 0 7px\">assigned weapons</div>"""
if needle not in s:
    raise SystemExit('encounter defer markup insertion target missing')
s=s.replace(needle,replacement,1)

# Bind the defer control in the active encounter screen.
needle="""  bindNav();
  document.querySelector('#triggerChaos')?.addEventListener('click',()=>commit(triggerChaos(state,playerName())));"""
replacement="""  bindNav();
  document.querySelector('#deferCapstone')?.addEventListener('click',tcDeferCapstone);
  document.querySelector('#triggerChaos')?.addEventListener('click',()=>commit(triggerChaos(state,playerName())));"""
if needle not in s:
    raise SystemExit('encounter bind target missing')
s=s.replace(needle,replacement,1)

# Debt encounters cannot roll below late tier when their Chaos seal breaks.
s=s.replace("const rolledChaos = tcPickEscalatingChaos(next);",
            "const rolledChaos = tcPickEscalatingChaos(next,next.current?.deferredCapstoneDetour?3:2);",1)

# Reset defer bookkeeping when entering a different region, while preserving all
# other global state carried by the region persistence patch.
needle="""  next.lastAction = `${actor} entered ${region}.`;
  return next;
}"""
replacement="""  next.capstoneDeferUsed=false;
  next.capstoneDeferredName=null;
  next.capstoneDetourPending=false;
  next.lastAction = `${actor} entered ${region}.`;
  return next;
}"""
if needle not in s:
    raise SystemExit('startNextRegion reset target missing')
s=s.replace(needle,replacement,1)

css=r'''
/* --- one-time capstone defer --- */
.tc-capstone-defer{margin:10px 0 15px;padding:14px;border-top:1px solid rgba(201,102,90,.36);border-bottom:1px solid rgba(201,102,90,.28);background:linear-gradient(90deg,transparent,rgba(92,24,20,.15),transparent)}
.tc-capstone-defer-copy{font-size:14px;line-height:1.45;color:#c8beac;margin:6px 0 11px}.tc-capstone-defer .btn{min-height:52px}
'''
if '</style>' not in s: raise SystemExit('style end missing')
s=s.replace('</style>',css+'\n</style>',1)

for invariant in ['capstoneDetourPending','capstoneDeferUsed','DEFER ONCE · ACCEPT DEBT ENCOUNTER','deferredCapstoneDetour?3:2','function tcDeferCapstone()']:
    if invariant not in s: raise SystemExit('capstone defer invariant missing: '+invariant)

p.write_text(s)
