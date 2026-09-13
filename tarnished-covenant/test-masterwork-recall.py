from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or 'missing Masterwork Recall invariant: '+needle)

for needle in [
    'const tcSmithingDataBeforeMasterworkRecall=smithingData;',
    'masterworkRecalls:recalls.filter',
    'build:x.build&&typeof x.build===\'object\'?structuredClone(x.build):null',
    'masterworkedAt:new Date().toISOString()',
    'used:false',
    'function tcBuildMasterworkRecall(latest,encounterId,recordId,expectedCurrentWeapon,slot,actor)',
    "if(typeof tcEncounterMutationLocked==='function'&&tcEncounterMutationLocked(latest))return null;",
    'if(!record||record.used||record.owner!==slot||!record.build?.name)return null;',
    "if(String(c?.[slot]?.name||'')!==String(expectedCurrentWeapon||''))return null;",
    'next.current[slot]=structuredClone(saved.build);',
    'saved.used=true;',
    'saved.recalledEncounterId=encounterId;',
    'RECALL AVAILABLE',
    'RECALLED / RETIRED',
    'Only the Tarnished who Masterworked this weapon may Recall it.',
    'retryBuilder:build',
]: require(needle)

# Masterworking must preserve the exact current build and bind the Recall to the
# same internal player slot rather than storing only a weapon name.
master_start=html.find('masterworkCurrent=function(state,slot){')
master_end=html.find('\nfunction tcBuildMasterworkRecall',master_start)
if master_start<0 or master_end<0: raise SystemExit('Masterwork override missing')
master=html[master_start:master_end]
for needle in ['structuredClone(next.current[slot])','owner:slot,build,used:false','next.smithing.masterworkCredits-=1']:
    if needle not in master: raise SystemExit('Masterwork snapshot invariant missing: '+needle)

# Recall is intentionally not a Weapon Appeal: it may not create penalties,
# consume an Appeal Waiver, or change the other Tarnished's assignment.
recall_start=html.find('function tcBuildMasterworkRecall(')
recall_end=html.find('\nfunction tcMasterworkArsenalMarkup',recall_start)
if recall_start<0 or recall_end<0: raise SystemExit('Recall builder block missing')
recall=html[recall_start:recall_end]
for forbidden in ['penances.push','appealWaivers','makePenance','current.chase=','current.morgan=']:
    if forbidden in recall: raise SystemExit('Recall builder has forbidden Appeal/other-player mutation: '+forbidden)

# The generated layer must be singular after repeated production builds.
if html.count('/* --- Masterwork veteran recall --- */')!=1:
    raise SystemExit('Masterwork Recall runtime duplicated')
if html.count('/* --- Masterwork veteran recall styles --- */')!=1:
    raise SystemExit('Masterwork Recall styles duplicated')

print('Masterwork Recall: PASS — one owner-bound exact-build Recall, stale-safe, penalty-free, and locked after 1/2 clears.')
