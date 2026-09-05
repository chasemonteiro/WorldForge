from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# -----------------------------------------------------------------------------
# Region-locked Bell Bearing contracts
#
# Favor is global and can be banked across the run, but a Bell Bearing contract
# may only become eligible while the Covenant is physically in that bearing's
# region. A banked affordable contract gets one safe entry opportunity on region
# arrival; if Favor becomes sufficient later, the existing post-battle safe
# transition path will surface it then.
# -----------------------------------------------------------------------------

bell_pattern = re.compile(
    r"function bellAccessible\(state,b\)\{\s*"
    r"try \{ return b\.region===state\.region \|\| regionUnlocked\(state,b\.region\) \|\| \(state\.clearedRegions\|\|\[\]\)\.includes\(b\.region\); \}\s*"
    r"catch \{ return b\.region===state\.region; \}\s*"
    r"\}"
)
bell_new = """function bellAccessible(state,b){
  return Boolean(b&&state&&b.region===state.region);
}"""
s, n = bell_pattern.subn(bell_new, s, count=1)
if n != 1 and 'return Boolean(b&&state&&b.region===state.region);' not in s:
    raise SystemExit('Bell Bearing accessibility target missing')

old_eligible = "function tcMandatoryContractEligible(state){if(!state?.current||!pendingRevealId||state.current.id!==pendingRevealId)return false;const sm=smithingData(state);return !sm.activeContract&&sm.favor>=3&&availableBellBearings(state).length>0;}"
new_eligible = """let tcPendingRegionContractEncounterId=null;

function tcMandatoryContractEligible(state){
  if(!state?.current)return false;
  const safeTransition=pendingRevealId===state.current.id||tcPendingRegionContractEncounterId===state.current.id;
  if(!safeTransition)return false;
  const sm=smithingData(state);
  if(sm.activeContract)return false;
  return availableBellBearings(state).some(b=>sm.favor>=smithingContractCost(b));
}"""
if old_eligible in s:
    s = s.replace(old_eligible, new_eligible, 1)
elif 'function tcMandatoryContractEligible(state)' in s and 'tcPendingRegionContractEncounterId' not in s:
    raise SystemExit('Mandatory contract eligibility target changed')

travel_old = "uiScreen='sanctuary';pendingRevealId=null;commit(next);"
travel_new = "uiScreen='sanctuary';pendingRevealId=null;tcPendingRegionContractEncounterId=next.current?.id||null;commit(next);"
travel_count = s.count(travel_old)
if travel_count:
    s = s.replace(travel_old, travel_new)
elif travel_new not in s:
    raise SystemExit('Region travel contract trigger targets missing')

saved_old = "if(saved)renderSmithingContract();else renderRun();"
saved_new = "if(saved){tcPendingRegionContractEncounterId=null;renderSmithingContract();}else renderRun();"
if saved_old in s:
    s = s.replace(saved_old, saved_new, 1)
elif saved_new not in s:
    raise SystemExit('Mandatory contract completion target missing')

clear_old = "if(pendingRevealId && pendingRevealId!==nextId)pendingRevealId=null;"
clear_new = "if(pendingRevealId && pendingRevealId!==nextId)pendingRevealId=null;\n  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;"
if clear_old in s:
    s = s.replace(clear_old, clear_new, 1)
elif 'tcPendingRegionContractEncounterId!==nextId' not in s:
    raise SystemExit('Shared transient cleanup target missing')

required = [
    'return Boolean(b&&state&&b.region===state.region);',
    'let tcPendingRegionContractEncounterId=null;',
    'const safeTransition=pendingRevealId===state.current.id||tcPendingRegionContractEncounterId===state.current.id;',
    'availableBellBearings(state).some(b=>sm.favor>=smithingContractCost(b))',
    "tcPendingRegionContractEncounterId=next.current?.id||null;commit(next);",
    'tcPendingRegionContractEncounterId!==nextId',
]
for needle in required:
    if needle not in s:
        raise SystemExit('Region-locked contract invariant missing: ' + needle)

# The old unlock/cleared-region eligibility rule must no longer exist in the
# Bell Bearing accessibility helper.
match = re.search(r'function bellAccessible\(state,b\)\{(.*?)\}', s, re.S)
if not match:
    raise SystemExit('Bell accessibility helper missing after patch')
body = match.group(1)
if 'regionUnlocked' in body or 'clearedRegions' in body:
    raise SystemExit('Bell contracts are still accessible outside the current region')

p.write_text(s)
print(f'Region-locked Bell Bearing contracts applied; patched {travel_count or 2} travel paths.')
