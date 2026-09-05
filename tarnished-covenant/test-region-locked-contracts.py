from pathlib import Path
import re

html = Path('tarnished-covenant/index.html').read_text()

def require(needle):
    if needle not in html:
        raise SystemExit('missing sequential-contract invariant: ' + needle)

# Geography: current region or an actually visited/cleared region only.
require('function bellRegionVisited(state,b)')
require("b.region===state.region||(state.clearedRegions||[]).includes(b.region)")

# Sequence: Smithing and Somber each expose only their own next unclaimed bearing.
require('function nextBellBearingForKind(state,kind)')
require("b.kind===kind&&!sm.acquired.includes(b.id)")
require('const next=nextBellBearingForKind(state,b.kind);')
require('return Boolean(next&&next.id===b.id);')

# Safe-transition triggers still work on region entry and later after Favor gains.
require('let tcPendingRegionContractEncounterId=null;')
require('const safeTransition=pendingRevealId===state.current.id||tcPendingRegionContractEncounterId===state.current.id;')
require('availableBellBearings(state).some(b=>sm.favor>=smithingContractCost(b))')
require("tcPendingRegionContractEncounterId=next.current?.id||null;commit(next);")
require('tcPendingRegionContractEncounterId!==nextId')

if html.count("tcPendingRegionContractEncounterId=next.current?.id||null;commit(next);") < 2:
    raise SystemExit('expected both region travel paths to arm contract entry eligibility')

# Never use generic world-unlock state to send the Covenant forward.
m = re.search(r'function bellRegionVisited\(state,b\)\{(.*?)\}', html, re.S)
if not m:
    raise SystemExit('bellRegionVisited helper missing')
if 'regionUnlocked' in m.group(1):
    raise SystemExit('future unlocked-but-unvisited regions can still become contract destinations')

# The automatic notice must check the real tiered price, not the obsolete 3-Favor threshold.
m = re.search(r'function tcMandatoryContractEligible\(state\)\{(.*?)\n\}', html, re.S)
if not m:
    raise SystemExit('mandatory contract eligibility helper missing')
eligible_body = m.group(1)
if 'sm.favor>=3' in eligible_body:
    raise SystemExit('obsolete 3-Favor automatic contract threshold remains')
if 'smithingContractCost' not in eligible_body:
    raise SystemExit('automatic contract eligibility is not checking actual contract cost')

# Static behavior model: verify the intended eligibility matrix using the live
# Bell Bearing ordering encoded in the app.
bells_match = re.search(r'const TC_BELL_BEARINGS = \[(.*?)\];', html, re.S)
if not bells_match:
    raise SystemExit('Bell Bearing table missing')
rows = re.findall(r"\{id:'([^']+)',kind:'([^']+)',name:'[^']+',region:'([^']+)'", bells_match.group(1))
if len(rows) < 8:
    raise SystemExit('Bell Bearing table unexpectedly incomplete')

def available(region, cleared, acquired):
    out = []
    for kind in ('Smithing', 'Somber'):
        next_row = next((r for r in rows if r[1] == kind and r[0] not in acquired), None)
        if next_row and (next_row[2] == region or next_row[2] in cleared):
            out.append(next_row[0])
    return out

# Current region works.
if 'somber1' not in available('Caelid', ['Limgrave + Stormveil'], set()):
    raise SystemExit('current-region next Somber bearing should be eligible')

# Backward works: Altus may send us back to Liurnia for Smithing [1].
backward = available('Altus Plateau + Leyndell', ['Limgrave + Stormveil', 'Liurnia of the Lakes', 'Caelid'], set())
if 'smith1' not in backward or 'somber1' not in backward:
    raise SystemExit('visited earlier-region next bearings should remain eligible')

# Forward is blocked: if Caelid was never visited, Somber [1] cannot pull us there.
no_forward = available('Liurnia of the Lakes', ['Limgrave + Stormveil'], set())
if 'somber1' in no_forward:
    raise SystemExit('unvisited future/side region bearing became eligible')

# Sequence is strict per track: Smithing [2] cannot appear before Smithing [1].
if 'smith2' in backward:
    raise SystemExit('Smithing sequence can skip Smithing [1]')
after_smith1 = available('Altus Plateau + Leyndell', ['Limgrave + Stormveil', 'Liurnia of the Lakes', 'Caelid'], {'smith1'})
if 'smith2' not in after_smith1:
    raise SystemExit('Smithing [2] should become eligible after Smithing [1] is claimed and Altus is current')

print('Tarnished Covenant sequential backward-only contract invariants: PASS')
