from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# Live shared-reward watch tracking
#
# A partner who actually watched every shared reward reveal live must not be sent
# through the offline catch-up replay after the drawing player acknowledges the
# payout. Record only rewards whose result was visibly revealed on this device.
# If any reward index was missed, the existing catch-up replay still runs.
# -----------------------------------------------------------------------------

s=re.sub(
    r"\n?/\* --- Live shared reward watch tracking --- \*/.*?"
    r"/\* --- End live shared reward watch tracking --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

old_catchup="return Boolean(shared?.id&&tcSharedRewardDrawerFinished(shared)&&!tcSharedRewardSeenList(shared).includes(identity));"
new_catchup="return Boolean(shared?.id&&tcSharedRewardDrawerFinished(shared)&&!tcSharedRewardSeenList(shared).includes(identity)&&!tcSharedRewardObservedAll(shared));"
if old_catchup in s:
    s=s.replace(old_catchup,new_catchup,1)
elif new_catchup not in s:
    raise SystemExit('shared reward catch-up predicate target missing')

old_finish="result.hidden=false;result.classList.add('revealed');data.spinning=false;"
new_finish="result.hidden=false;result.classList.add('revealed');data.spinning=false;if(!catchUp&&!isDrawer)tcRememberSharedRewardObserved(shared,displayIndex);"
if old_finish in s:
    s=s.replace(old_finish,new_finish,1)
elif new_finish not in s:
    raise SystemExit('reward reveal finish hook target missing')

js=r'''
/* --- Live shared reward watch tracking --- */
const TC_REWARD_OBSERVED_PREFIX='tc-shared-reward-observed:';
function tcSharedRewardObservationKey(shared){
  return shared?.id?`${TC_REWARD_OBSERVED_PREFIX}${shared.id}`:'';
}
function tcSharedRewardObservedIndices(shared){
  const key=tcSharedRewardObservationKey(shared);
  if(!key)return [];
  try{
    const raw=sessionStorage.getItem(key);
    const parsed=raw?JSON.parse(raw):[];
    return Array.from(new Set((Array.isArray(parsed)?parsed:[]).map(Number).filter(Number.isInteger))).sort((a,b)=>a-b);
  }catch{return [];}
}
function tcRememberSharedRewardObserved(shared,index){
  const key=tcSharedRewardObservationKey(shared),value=Number(index);
  if(!key||!Number.isInteger(value)||value<0)return;
  try{
    const seen=tcSharedRewardObservedIndices(shared);
    if(!seen.includes(value))seen.push(value);
    sessionStorage.setItem(key,JSON.stringify(seen));
  }catch{}
}
function tcSharedRewardObservedAll(shared){
  const total=Array.isArray(shared?.rewards)?shared.rewards.length:0;
  if(total<1)return false;
  const seen=new Set(tcSharedRewardObservedIndices(shared));
  for(let i=0;i<total;i++)if(!seen.has(i))return false;
  return true;
}
/* --- End live shared reward watch tracking --- */
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

required=[
    "TC_REWARD_OBSERVED_PREFIX='tc-shared-reward-observed:'",
    'function tcSharedRewardObservedIndices(shared)',
    'function tcRememberSharedRewardObserved(shared,index)',
    'function tcSharedRewardObservedAll(shared)',
    '&&!tcSharedRewardObservedAll(shared)',
    'if(!catchUp&&!isDrawer)tcRememberSharedRewardObserved(shared,displayIndex);',
]
for needle in required:
    if needle not in s: raise SystemExit('live reward watch invariant missing: '+needle)

p.write_text(s)
print('Live shared reward viewing now suppresses duplicate catch-up replays only when every reward was actually seen.')
