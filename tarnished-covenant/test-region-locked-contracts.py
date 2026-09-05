from pathlib import Path
import re

html = Path('tarnished-covenant/index.html').read_text()

def require(needle):
    if needle not in html:
        raise SystemExit('missing region-contract invariant: ' + needle)

require('return Boolean(b&&state&&b.region===state.region);')
require('let tcPendingRegionContractEncounterId=null;')
require('const safeTransition=pendingRevealId===state.current.id||tcPendingRegionContractEncounterId===state.current.id;')
require('availableBellBearings(state).some(b=>sm.favor>=smithingContractCost(b))')
require("tcPendingRegionContractEncounterId=next.current?.id||null;commit(next);")
require('tcPendingRegionContractEncounterId!==nextId')

# Both normal and safe region-travel paths should arm the one-time entry check.
if html.count("tcPendingRegionContractEncounterId=next.current?.id||null;commit(next);") < 2:
    raise SystemExit('expected both region travel paths to arm contract entry eligibility')

# Bell availability itself must not use general world-unlock or cleared-region status.
m = re.search(r'function bellAccessible\(state,b\)\{(.*?)\}', html, re.S)
if not m:
    raise SystemExit('bellAccessible helper missing')
body = m.group(1)
if 'regionUnlocked' in body or 'clearedRegions' in body:
    raise SystemExit('Bell Bearing contracts can still leak across regions')

# The automatic notice must check the actual tiered price, not the obsolete 3-Favor threshold.
m = re.search(r'function tcMandatoryContractEligible\(state\)\{(.*?)\n\}', html, re.S)
if not m:
    raise SystemExit('mandatory contract eligibility helper missing')
eligible_body = m.group(1)
if 'sm.favor>=3' in eligible_body:
    raise SystemExit('obsolete 3-Favor automatic contract threshold remains')
if 'smithingContractCost' not in eligible_body:
    raise SystemExit('automatic contract eligibility is not checking actual contract cost')

print('Tarnished Covenant region-locked contract invariants: PASS')
