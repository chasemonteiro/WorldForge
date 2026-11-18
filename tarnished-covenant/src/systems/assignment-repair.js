/* --- Armory correction for in-progress encounters ---
   When an acquisition gate is added or corrected after an encounter was
   rolled, the current assignment can name a weapon the players cannot hold
   yet. On render, each device checks the current encounter once; if a slot is
   unobtainable it re-draws only that slot through the normal appeal-aware
   makeBuild and saves through commit() (revision-checked, retried against the
   latest state, a no-op if the other phone already fixed it). No penalty, no
   favor change, nothing else in the run is touched. */
const tcAssignmentRepairTried=new Set();
function tcAssignmentRepairBlocked(state){
  // Terms are fixed once a world is cleared, and reward/report screens must
  // not be re-rendered or have their buttons blocked by a background save.
  if(typeof tcEncounterMutationLocked==='function'&&tcEncounterMutationLocked(state))return true;
  if(typeof postBattleReport!=='undefined'&&postBattleReport)return true;
  if(typeof tcSharedRewardDrawPending==='function'&&tcSharedRewardDrawPending(state))return true;
  if(typeof tcSharedRewardUnresolved==='function'&&tcSharedRewardUnresolved(state))return true;
  return false;
}
function tcUnobtainableAssignedSlots(state){
  const current=state?.current;
  if(!current||state.runComplete||state.regionComplete||tcAssignmentRepairBlocked(state))return [];
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
/* Boss-pool correction: when a boss is moved out of a region's pool after the
   current encounter rolled it, the unstarted encounter gets a fresh legal boss
   from the region (never the capstone). Weapons, Rite and Chaos stay unless a
   weapon is barred by the new boss, in which case only that slot re-draws.
   Required/prerequisite targets and capstones are never touched. */
function tcTargetOutsidePool(state){
  const current=state?.current,target=current?.target;
  if(!current||!target?.name||target.exit||target.required||state.runComplete||state.regionComplete||tcAssignmentRepairBlocked(state))return false;
  if((current.worldClears||[]).length)return false;
  const pool=regions?.[state.region]?.bosses;
  return Array.isArray(pool)&&pool.length>0&&!pool.includes(target.name);
}
function tcRepairOutOfPoolTarget(state){
  if(!tcTargetOutsidePool(state))return null;
  const next=structuredClone(state),current=next.current,old=current.target.name;
  let target=null;
  for(let i=0;i<60;i++){const t=chooseTarget(next);if(t?.name&&!t.exit&&t.name!==old&&(t.required||regions[next.region].bosses.includes(t.name))){target=structuredClone(t);break;}}
  if(!target)return null;
  current.target=target;current.worldClears=[];
  const changes=[`${old} → ${target.name}`];
  for(const slot of ['chase','morgan']){
    const build=current[slot];
    if(!build?.name||typeof weaponBlockedByTarget!=='function'||!weaponBlockedByTarget(build,target))continue;
    const avoid=[current.chase?.name,current.morgan?.name].filter(Boolean);
    let replacement=null;try{replacement=makeBuild(next.region,target,avoid,next);}catch(error){return null;}
    if(!replacement?.name)return null;
    changes.push(`${build.name} → ${replacement.name}`);current[slot]=replacement;
  }
  next.lastAction=`Boss correction: ${changes.join(' · ')} (${old} is no longer drawn in ${next.region}).`;
  return next;
}
const tcBossPoolRepairTried=new Set();
const tcRenderRunBeforeBossPoolRepair=renderRun;
renderRun=function(){
  tcRenderRunBeforeBossPoolRepair();
  try{
    const id=run?.state?.current?.id;
    if(!id||tcBossPoolRepairTried.has(id)||!tcTargetOutsidePool(run.state))return;
    setTimeout(async()=>{
      if(pending||tcBossPoolRepairTried.has(id)||run?.state?.current?.id!==id)return;
      const next=tcRepairOutOfPoolTarget(run.state);
      if(!next)return;
      tcBossPoolRepairTried.add(id);
      let toast=next.lastAction;
      const saved=await commit(next,{quiet:true,retryBuilder:latest=>{const rebuilt=tcRepairOutOfPoolTarget(latest);if(rebuilt)toast=rebuilt.lastAction;return rebuilt;}});
      if(saved&&toast)setToast(toast);
      if(!saved)tcBossPoolRepairTried.delete(id);
    },90);
  }catch(error){console.warn('Boss correction skipped',error);}
};
const tcRenderRunBeforeAssignmentRepair=renderRun;
renderRun=function(){
  tcRenderRunBeforeAssignmentRepair();
  try{
    const id=run?.state?.current?.id;
    if(!id||tcAssignmentRepairTried.has(id)||!tcUnobtainableAssignedSlots(run.state).length)return;
    setTimeout(async()=>{
      // Rebuild from whatever is current at save time, never from a snapshot
      // taken during render; wait out any other save instead of colliding.
      if(pending||tcAssignmentRepairTried.has(id)||run?.state?.current?.id!==id)return;
      const next=tcRepairUnobtainableAssignments(run.state);
      if(!next)return;
      tcAssignmentRepairTried.add(id);
      let toast=next.lastAction;
      const saved=await commit(next,{quiet:true,retryBuilder:latest=>{const rebuilt=tcRepairUnobtainableAssignments(latest);if(rebuilt)toast=rebuilt.lastAction;return rebuilt;}});
      if(saved&&toast)setToast(toast);
      if(!saved)tcAssignmentRepairTried.delete(id);
    },60);
  }catch(error){console.warn('Armory correction skipped',error);}
};
