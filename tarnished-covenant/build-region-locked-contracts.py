from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# -----------------------------------------------------------------------------
# Sequential, visited-region Bell Bearing contracts
#
# Favor is global and bankable. Smithing and Somber each advance in their own
# strict Bell Bearing sequence. Only the next unclaimed bearing in each track may
# become a contract, and its region must be the current region or one the run has
# already cleared/visited. This allows Corporate to send the Covenant backward
# for skipped procurement, but never forward into an unvisited region.
# -----------------------------------------------------------------------------

helpers_pattern = re.compile(
    r"function bellById\(id\)\{\s*return TC_BELL_BEARINGS\.find\(x=>x\.id===id\);\s*\}\s*"
    r"function bellAccessible\(state,b\)\{.*?\}\s*"
    r"function availableBellBearings\(state\)\{.*?\n\}",
    re.S,
)
helpers_new = """function bellById(id){ return TC_BELL_BEARINGS.find(x=>x.id===id); }
function bellRegionVisited(state,b){
  return Boolean(b&&state&&(b.region===state.region||(state.clearedRegions||[]).includes(b.region)));
}
function nextBellBearingForKind(state,kind){
  const sm=smithingData(state);
  return TC_BELL_BEARINGS.find(b=>b.kind===kind&&!sm.acquired.includes(b.id))||null;
}
function bellAccessible(state,b){
  if(!b||!bellRegionVisited(state,b))return false;
  const next=nextBellBearingForKind(state,b.kind);
  return Boolean(next&&next.id===b.id);
}
function availableBellBearings(state){
  const sm=smithingData(state);
  return TC_BELL_BEARINGS.filter(b=>!sm.acquired.includes(b.id) && (!sm.activeContract || sm.activeContract.bearingId!==b.id) && bellAccessible(state,b));
}"""
s, n = helpers_pattern.subn(helpers_new, s, count=1)
if n != 1:
    # Support rerunning over a previously patched build.
    rerun_pattern = re.compile(
        r"function bellById\(id\)\{.*?\nfunction availableBellBearings\(state\)\{.*?\n\}",
        re.S,
    )
    s, n = rerun_pattern.subn(helpers_new, s, count=1)
if n != 1 and 'function nextBellBearingForKind(state,kind)' not in s:
    raise SystemExit('Bell Bearing helper block target missing')

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
    'function bellRegionVisited(state,b)',
    "b.region===state.region||(state.clearedRegions||[]).includes(b.region)",
    'function nextBellBearingForKind(state,kind)',
    "b.kind===kind&&!sm.acquired.includes(b.id)",
    'const next=nextBellBearingForKind(state,b.kind);',
    'return Boolean(next&&next.id===b.id);',
    'let tcPendingRegionContractEncounterId=null;',
    'const safeTransition=pendingRevealId===state.current.id||tcPendingRegionContractEncounterId===state.current.id;',
    'availableBellBearings(state).some(b=>sm.favor>=smithingContractCost(b))',
    "tcPendingRegionContractEncounterId=next.current?.id||null;commit(next);",
    'tcPendingRegionContractEncounterId!==nextId',
]
for needle in required:
    if needle not in s:
        raise SystemExit('Sequential contract invariant missing: ' + needle)

# General unlock status must never grant procurement access. Only current or
# actually visited/cleared regions are geographically eligible.
visited_match = re.search(r'function bellRegionVisited\(state,b\)\{(.*?)\}', s, re.S)
if not visited_match:
    raise SystemExit('Bell visited-region helper missing after patch')
visited_body = visited_match.group(1)
if 'regionUnlocked' in visited_body:
    raise SystemExit('Bell contracts can still send players into unvisited unlocked regions')

p.write_text(s)
print(f'Sequential visited-region Bell Bearing contracts applied; patched {travel_count or 2} travel paths.')
