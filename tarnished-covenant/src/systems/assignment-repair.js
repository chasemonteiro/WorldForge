/* --- Armory correction for in-progress encounters ---
   When an acquisition gate is added or corrected after an encounter was
   rolled, the current assignment can name a weapon the players cannot hold
   yet. On render, each device checks the current encounter once; if a slot is
   unobtainable it re-draws only that slot through the normal appeal-aware
   makeBuild and saves through commit() (revision-checked, retried against the
   latest state, a no-op if the other phone already fixed it). No penalty, no
   favor change, nothing else in the run is touched. */
const tcAssignmentRepairTried=new Set();
function tcUnobtainableAssignedSlots(state){
  const current=state?.current;
  if(!current||state.runComplete||state.regionComplete)return [];
  return ['chase','morgan'].filter(slot=>current[slot]?.name&&!tcWeaponAcquisitionUnlocked(state,current[slot]));
}
function tcRepairUnobtainableAssignments(state){
  const slots=tcUnobtainableAssignedSlots(state);
  if(!slots.length)return null;
  const next=structuredClone(state),current=next.current,changes=[];
  for(const slot of slots){
    const avoid=[current.chase?.name,current.morgan?.name].filter(Boolean);
    let build=null;
    try{build=makeBuild(next.region,current.target,avoid,next);}catch(error){console.warn('Armory correction found no legal weapon',error);return null;}
    if(!build?.name||!tcWeaponAcquisitionUnlocked(next,build))return null;
    changes.push(`${current[slot].name} → ${build.name}`);
    current[slot]=build;
  }
  next.lastAction=`Armory correction: ${changes.join(' · ')} (not obtainable yet).`;
  return next;
}
const tcRenderRunBeforeAssignmentRepair=renderRun;
renderRun=function(){
  tcRenderRunBeforeAssignmentRepair();
  try{
    const state=run?.state,id=state?.current?.id;
    if(!id||tcAssignmentRepairTried.has(id)||pending)return;
    if(!tcUnobtainableAssignedSlots(state).length)return;
    tcAssignmentRepairTried.add(id);
    const next=tcRepairUnobtainableAssignments(state);
    if(!next)return;
    setTimeout(()=>{commit(next,{retryBuilder:latest=>tcRepairUnobtainableAssignments(latest),successToast:next.lastAction});},0);
  }catch(error){console.warn('Armory correction skipped',error);}
};
