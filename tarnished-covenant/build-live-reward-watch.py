from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# Live shared-reward watch tracking
#
# A partner who actually watched shared rewards live must not be sent through an
# offline replay afterward. Track only results that were visibly revealed on the
# ACTIVE synchronized reward machine. Persist the observation across PWA/browser
# restarts, and resume catch-up from the first genuinely missed reward.
# -----------------------------------------------------------------------------

s=re.sub(
    r"\n?/\* --- Live shared reward watch tracking --- \*/.*?"
    r"/\* --- End live shared reward watch tracking --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

# Clean residue from the older buggy patch, which attached to the first/legacy
# reward machine and could duplicate itself on every production rebuild.
s=s.replace('if(!catchUp&&!isDrawer)tcRememberSharedRewardObserved(shared,displayIndex);','')
s=s.replace('if(!isDrawer)tcRememberSharedRewardObserved(shared,displayIndex,me);','')
s=re.sub(
    r"\n\s*if\(!isDrawer&&result\.isConnected&&run\?\.state\?\.sharedRewardReveal\?\.id===shared\.id&&tcSharedRewardIndex\(run\.state\.sharedRewardReveal\)===displayIndex\)\{\s*"
    r"tcRememberSharedRewardObserved\(shared,displayIndex,me\);\s*\}",
    "",
    s,
)

# The catch-up decision is identity-specific because a device can change which
# internal player slot it represents between sessions.
s=s.replace(
    "return Boolean(shared?.id&&tcSharedRewardDrawerFinished(shared)&&!tcSharedRewardSeenList(shared).includes(identity));",
    "return Boolean(shared?.id&&tcSharedRewardDrawerFinished(shared)&&!tcSharedRewardSeenList(shared).includes(identity)&&!tcSharedRewardObservedAll(shared,identity));",
    1,
)
s=s.replace(
    "&&!tcSharedRewardObservedAll(shared))",
    "&&!tcSharedRewardObservedAll(shared,identity))",
    1,
)
if "&&!tcSharedRewardObservedAll(shared,identity))" not in s:
    raise SystemExit('shared reward catch-up predicate target missing')

# Patch the LAST renderRewardMachine assignment: that is the synchronized active
# implementation. Never patch the older function declaration retained above it.
active_start=s.rfind('renderRewardMachine=function(){')
active_end=s.find('/* --- End synchronized shared reward reveal --- */',active_start)
if active_start<0 or active_end<0:
    raise SystemExit('active synchronized reward machine missing')
active=s[active_start:active_end]

# Catch-up begins at the first missing result instead of replaying an already-seen
# prefix. Scope this to the catch-up object rather than depending on whitespace.
catch_start=active.find('if(catchUp){')
catch_end=active.find('    return;',catch_start)
if catch_start<0 or catch_end<0:
    raise SystemExit('catch-up hydration block missing')
catch_block=active[catch_start:catch_end]
catch_block,n=re.subn(
    r"(?m)^(\s*)index\s*:\s*(?:0|tcSharedRewardFirstMissingIndex\(shared,me\))\s*,",
    r"\1index:tcSharedRewardFirstMissingIndex(shared,me),",
    catch_block,
    count=1,
)
if n!=1:
    raise SystemExit('catch-up resume index target missing')
active=active[:catch_start]+catch_block+active[catch_end:]

# Mark an observation only when the result node is still on-screen and the shared
# authoritative index still matches. This prevents a stale spin timeout from
# claiming the partner saw a reward after the drawer already advanced.
old_finish="""    result.hidden=false;result.classList.add('revealed');data.spinning=false;
    const mayAct=catchUp||!hasNext||isDrawer;"""
new_finish="""    result.hidden=false;result.classList.add('revealed');data.spinning=false;
    if(!isDrawer&&result.isConnected&&run?.state?.sharedRewardReveal?.id===shared.id&&tcSharedRewardIndex(run.state.sharedRewardReveal)===displayIndex){
      tcRememberSharedRewardObserved(shared,displayIndex,me);
    }
    const mayAct=catchUp||!hasNext||isDrawer;"""
if old_finish not in active:
    raise SystemExit('active reward reveal finish hook target missing')
active=active.replace(old_finish,new_finish,1)

# A realtime acknowledgement from the drawer can cause a render while the partner
# is already sitting on the revealed final result. Do not spin the same result a
# second time merely because shared metadata changed.
if 'if(reduced){finish();}' in active:
    active=active.replace('if(reduced){finish();}','if(reduced||data.spinning===false){finish();}',1)
elif 'if(reduced||data.spinning===false){finish();}' not in active:
    raise SystemExit('reward no-respin target missing')

s=s[:active_start]+active+s[active_end:]

js=r'''
/* --- Live shared reward watch tracking --- */
const TC_REWARD_OBSERVED_PREFIX='tc-shared-reward-observed:';
function tcSharedRewardObservationKey(shared,identity=playerName()){
  return shared?.id&&identity?`${TC_REWARD_OBSERVED_PREFIX}${shared.id}:${identity}`:'';
}
function tcSharedRewardObservedIndices(shared,identity=playerName()){
  const key=tcSharedRewardObservationKey(shared,identity);
  if(!key)return [];
  try{
    const raw=localStorage.getItem(key);
    const parsed=raw?JSON.parse(raw):[];
    const total=Array.isArray(shared?.rewards)?shared.rewards.length:0;
    return Array.from(new Set((Array.isArray(parsed)?parsed:[]).map(Number).filter(x=>Number.isInteger(x)&&x>=0&&x<total))).sort((a,b)=>a-b);
  }catch{return [];}
}
function tcRememberSharedRewardObserved(shared,index,identity=playerName()){
  const key=tcSharedRewardObservationKey(shared,identity),value=Number(index);
  const total=Array.isArray(shared?.rewards)?shared.rewards.length:0;
  if(!key||!Number.isInteger(value)||value<0||value>=total)return;
  try{
    const seen=tcSharedRewardObservedIndices(shared,identity);
    if(!seen.includes(value))seen.push(value);
    localStorage.setItem(key,JSON.stringify(seen));
  }catch{}
}
function tcSharedRewardObservedAll(shared,identity=playerName()){
  const total=Array.isArray(shared?.rewards)?shared.rewards.length:0;
  if(total<1)return false;
  const seen=new Set(tcSharedRewardObservedIndices(shared,identity));
  for(let i=0;i<total;i++)if(!seen.has(i))return false;
  return true;
}
function tcSharedRewardFirstMissingIndex(shared,identity=playerName()){
  const total=Array.isArray(shared?.rewards)?shared.rewards.length:0;
  const seen=new Set(tcSharedRewardObservedIndices(shared,identity));
  for(let i=0;i<total;i++)if(!seen.has(i))return i;
  return Math.max(0,total-1);
}
/* --- End live shared reward watch tracking --- */
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

required=[
    "TC_REWARD_OBSERVED_PREFIX='tc-shared-reward-observed:'",
    'function tcSharedRewardObservedIndices(shared,identity=playerName())',
    'function tcRememberSharedRewardObserved(shared,index,identity=playerName())',
    'function tcSharedRewardObservedAll(shared,identity=playerName())',
    'function tcSharedRewardFirstMissingIndex(shared,identity=playerName())',
    'localStorage.getItem(key)',
    'localStorage.setItem(key,JSON.stringify(seen))',
    '&&!tcSharedRewardObservedAll(shared,identity)',
    'index:tcSharedRewardFirstMissingIndex(shared,me),',
    'result.isConnected',
    'tcRememberSharedRewardObserved(shared,displayIndex,me);',
    'if(reduced||data.spinning===false){finish();}',
]
for needle in required:
    if needle not in s: raise SystemExit('live reward watch invariant missing: '+needle)

# Exactly one observation hook, and it must be after the active synchronized
# override starts. This guards against patching the dead legacy machine again.
if s.count('tcRememberSharedRewardObserved(shared,displayIndex,me);') != 1:
    raise SystemExit('active reward observation hook is duplicated')
hook=s.find('tcRememberSharedRewardObserved(shared,displayIndex,me);')
if hook<active_start:
    raise SystemExit('reward observation hook landed in legacy reward machine')

p.write_text(s)
print('Live shared reward tracking fixed idempotently: active machine only, persistent observation, first-missed catch-up, and no stale/repeated reveal.')
