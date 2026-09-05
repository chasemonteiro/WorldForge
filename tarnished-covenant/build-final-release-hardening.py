from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# -----------------------------------------------------------------------------
# Final release hardening
#
# Challenge Rules owns reward probabilities. This late layer owns only durable
# reward inventory/presentation, complete immutable archive fields, and fixes
# for late UI wrappers that must not override the underlying gameplay handlers.
# -----------------------------------------------------------------------------

# The refresh-pairing UI used to wrap useCovenantBoon with a second busy guard.
# The real handler already owns that guard, so the wrapper set __tcBoonBusy=true
# before calling it and caused every Chaos/Rite Refresh click to return early.
duplicate_refresh_guard = """if(typeof useCovenantBoon==='function'&&!window.__tcBoonStabilized){
  window.__tcBoonStabilized=true;
  const tcUseCovenantBoonBeforePairing=useCovenantBoon;
  useCovenantBoon=async function(kind){
    if(window.__tcBoonBusy)return;
    window.__tcBoonBusy=true;
    try{return await tcUseCovenantBoonBeforePairing(kind);}
    finally{window.__tcBoonBusy=false;}
  };
}
"""
if duplicate_refresh_guard in s:
    s = s.replace(duplicate_refresh_guard, '', 1)
elif 'tcUseCovenantBoonBeforePairing' in s:
    raise SystemExit('unexpected Covenant boon wrapper shape')

core_refresh_guard = "if(window.__tcBoonBusy||!run?.state?.current)return;window.__tcBoonBusy=true;"
if core_refresh_guard not in s:
    raise SystemExit('core Covenant boon guard missing')

# Dynasty Frequent Flier is a bankable pass. One pass grants five bird trips.
old = """    appealWaivers: Number(raw.appealWaivers || 0),
    chaosRefreshes: Number(raw.chaosRefreshes || 0),
    riteRefreshes: Number(raw.riteRefreshes || 0)
  };"""
new = """    appealWaivers: Number(raw.appealWaivers || 0),
    chaosRefreshes: Number(raw.chaosRefreshes || 0),
    riteRefreshes: Number(raw.riteRefreshes || 0),
    aviaryTickets: Number(raw.aviaryTickets || 0)
  };"""
if old in s:
    s = s.replace(old, new, 1)
elif 'aviaryTickets: Number(raw.aviaryTickets || 0)' not in s:
    raise SystemExit('Frequent Flier inventory schema target missing')

# Reward reveal helper must recognize the Frequent Flier prize.
icon_pattern = r"function tcRewardIcon\(kind\)\{.*?\n\}"
icon_replacement = """function tcRewardIcon(kind){
  const icons={favor:'✦',favor2:'✦✦',chaos:'◉',rite:'✧',appeal:'⚖',aviary:'✈',tax:'☠'};
  return icons[kind]||'◇';
}"""
s, n = re.subn(icon_pattern, icon_replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('reward icon helper missing')

class_pattern = r"function tcRewardClass\(kind\)\{[^\n]*\}"
class_replacement = "function tcRewardClass(kind){return kind==='tax'?'tax':kind==='chaos'?'chaos':kind==='rite'?'rite':kind==='appeal'?'appeal':kind==='aviary'?'aviary':'favor';}"
s, n = re.subn(class_pattern, class_replacement, s, count=1)
if n != 1:
    raise SystemExit('reward class helper missing')

# Show banked Frequent Flier passes beside the other Covenant boons.
ledger_old = """    <div><strong>${sm.riteRefreshes}</strong><span>Rite Refresh${sm.riteRefreshes===1?'':'es'}</span></div>
  </div><div class=\"tc-muted\">Waivers make the next weapon appeal penalty-free. Refreshes are the only way to reroll a current Rite or unopened Chaos decree.</div></div>`;"""
ledger_new = """    <div><strong>${sm.riteRefreshes}</strong><span>Rite Refresh${sm.riteRefreshes===1?'':'es'}</span></div>
    <div><strong>${sm.aviaryTickets}</strong><span>Dynasty Frequent Flier${sm.aviaryTickets===1?'':'s'}</span></div>
  </div><div class=\"tc-muted\">Waivers make the next weapon appeal penalty-free. Refreshes reroll a Rite or unopened Chaos decree. Each Dynasty Frequent Flier grants 5 sanctioned trips to the Mohgwyn bird.</div></div>`;"""
if ledger_old in s:
    s = s.replace(ledger_old, ledger_new, 1)
elif 'Each Dynasty Frequent Flier grants 5 sanctioned trips to the Mohgwyn bird.' not in s:
    raise SystemExit('Frequent Flier ledger target missing')

# On a clean build, build-release-hardening creates the rewards field after the
# Challenge Rules layer has already run. Add the outcome fields here, when the
# final history shape definitely exists.
archive_old = """    rewards: structuredClone(encounter?.postBattleRewards || [])
  });"""
archive_new = """    rewards: structuredClone(encounter?.postBattleRewards || []),
    riteOutcome: encounter?.riteForfeited?'Forfeited':(encounter?.smithingRiteFavor?'Honored':'Failed'),
    chaosOutcome: encounter?.chaosForfeited?'Forfeited':(encounter?.chaosTriggered?(encounter?.smithingChaosFavor?'Honored':'Failed'):'Not triggered')
  });"""
if archive_old in s:
    s = s.replace(archive_old, archive_new, 1)
elif 'riteOutcome:' not in s or 'chaosOutcome:' not in s:
    raise SystemExit('Compendium outcome archive target missing')

# Four boon counters: two columns on phone, four across when room permits.
start = '/* --- Final release reward durability --- */'
end = '/* --- End final release reward durability --- */'
s = re.sub(r'\n?/\* --- Final release reward durability --- \*/.*?/\* --- End final release reward durability --- \*/\n?', '\n', s, flags=re.S)
css = """
/* --- Final release reward durability --- */
.tc-reward-result.aviary{border-color:rgba(144,161,119,.42);background:linear-gradient(90deg,transparent,rgba(89,107,68,.14),transparent)}
.tc-reward-result.aviary .tc-reward-icon,.tc-reward-result.aviary .tc-reward-name{color:#c7d1a5}
.tc-boon-grid{grid-template-columns:repeat(4,minmax(0,1fr))}
@media(max-width:430px){.tc-boon-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
/* --- End final release reward durability --- */
"""
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

for needle in [
    'aviaryTickets: Number(raw.aviaryTickets || 0)',
    "aviary:'✈'",
    "kind==='aviary'?'aviary'",
    'Each Dynasty Frequent Flier grants 5 sanctioned trips to the Mohgwyn bird.',
    "riteOutcome: encounter?.riteForfeited?'Forfeited'",
    "chaosOutcome: encounter?.chaosForfeited?'Forfeited'",
    'Final release reward durability',
    core_refresh_guard,
]:
    if needle not in s:
        raise SystemExit('final release invariant missing: ' + needle)

if 'tcUseCovenantBoonBeforePairing' in s:
    raise SystemExit('duplicate Covenant boon wrapper remains')

p.write_text(s)
