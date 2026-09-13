from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Remove the generated layer before reapplying it so repeated production builds
# stay idempotent.
s=re.sub(r"\n?/\* --- Shared Bell Bearing contract presentation --- \*/.*?/\* --- End shared Bell Bearing contract presentation --- \*/\n?","\n",s,flags=re.S)

js=r'''
/* --- Shared Bell Bearing contract presentation --- */
const TC_SHARED_CONTRACT_SEEN_PREFIX='tc-shared-contract-seen-v1';
function tcSharedContractPresentationKey(state=run?.state){
  const ct=smithingData(state||{}).activeContract;
  if(!ct)return '';
  return [ct.bearingId||'unknown',ct.commissionedAt||'legacy',ct.status||'task'].join('|');
}
function tcSharedContractSeenStorageKey(state=run?.state,identity=playerName()){
  const contractKey=tcSharedContractPresentationKey(state);
  if(!contractKey)return '';
  let runKey='local';
  try{runKey=run?.id||loadSession()?.runId||'local';}catch(_){runKey=run?.id||'local';}
  return `${TC_SHARED_CONTRACT_SEEN_PREFIX}:${runKey}:${identity}:${contractKey}`;
}
function tcSharedContractWasSurfaced(state=run?.state,identity=playerName()){
  const key=tcSharedContractSeenStorageKey(state,identity);if(!key)return false;
  try{return localStorage.getItem(key)==='1';}catch(_){return false;}
}
function tcRememberSharedContractSurfaced(state=run?.state,identity=playerName()){
  const key=tcSharedContractSeenStorageKey(state,identity);if(!key)return;
  try{localStorage.setItem(key,'1');}catch(_){}
}
function tcMaybeSurfaceSharedContract(state=run?.state){
  if(!state||postBattleReport||pendingRewardReveal?.rewards?.length)return;
  const ct=smithingData(state).activeContract;
  if(!ct||!bellById(ct.bearingId)||tcSharedContractWasSurfaced(state))return;
  const expected={bearingId:ct.bearingId,commissionedAt:ct.commissionedAt||'',status:ct.status||'task'};
  tcRememberSharedContractSurfaced(state);
  requestAnimationFrame(()=>{
    const live=smithingData(run?.state||{}).activeContract;
    if(!live)return;
    if(live.bearingId!==expected.bearingId)return;
    if((live.commissionedAt||'')!==expected.commissionedAt)return;
    if((live.status||'task')!==expected.status)return;
    renderSmithingContract();
  });
}
const tcRenderRunBeforeSharedContractSync=renderRun;
renderRun=function(){
  const rendered=tcRenderRunBeforeSharedContractSync();
  tcMaybeSurfaceSharedContract(run?.state);
  return rendered;
};
/* --- End shared Bell Bearing contract presentation --- */
'''
idx=s.rfind('</script>')
if idx<0:raise SystemExit('script end marker missing')
s=s[:idx]+js+s[idx:]

for needle in [
    "const TC_SHARED_CONTRACT_SEEN_PREFIX='tc-shared-contract-seen-v1';",
    'function tcSharedContractPresentationKey(state=run?.state)',
    'function tcMaybeSurfaceSharedContract(state=run?.state)',
    'tcRememberSharedContractSurfaced(state);',
    'renderSmithingContract();',
    'const tcRenderRunBeforeSharedContractSync=renderRun;',
    'tcMaybeSurfaceSharedContract(run?.state);',
]:
    if needle not in s:raise SystemExit('shared contract presentation invariant missing: '+needle)

p.write_text(s)
print('Shared Bell Bearing contracts now surface once on every participating device and again when status changes.')
