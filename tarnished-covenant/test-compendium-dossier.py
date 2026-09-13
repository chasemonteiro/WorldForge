from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html:
        raise SystemExit(msg or 'missing Compendium dossier invariant: '+needle)

# Late override exists exactly once and keeps native details/summary behavior.
for needle in [
    '/* --- Covenant Compendium dossier redesign --- */',
    '/* --- Covenant Compendium dossier styles --- */',
    'function tcCompendiumRewardLabels(entry)',
    'function tcCompendiumDossierMarkup(entry,index,state)',
    'compendiumEntryMarkup=function(entry,index,state)',
    'compendiumLedgerMarkup=function(state)',
    '<details class="tc-dossier',
    '<summary>',
    'Office of Covenant Records',
    'Field Dossiers',
]: require(needle)

if html.count('/* --- Covenant Compendium dossier redesign --- */') != 1:
    raise SystemExit('Compendium dossier JS layer duplicated')
if html.count('/* --- Covenant Compendium dossier styles --- */') != 1:
    raise SystemExit('Compendium dossier CSS layer duplicated')

# No historical functionality/data is dropped: all fields that mattered in the
# previous Compendium remain represented in the dossier detail view.
for needle in [
    'entry?.name',
    'entry?.region',
    'entry?.completedAt',
    'entry?.completedBy',
    'entry?.exit',
    'entry?.chaseWeapon',
    'entry?.morganWeapon',
    'entry?.chaseBuild?.role',
    'entry?.morganBuild?.role',
    'entry?.oddRite',
    'entry?.chaosTrigger',
    'entry?.chaosTriggered',
    'entry?.chaosConsequence',
    'entry?.penances',
    'entry?.rewards',
    'entry?.favorEarned',
]: require(needle)

# Explicit visual sections guard against the page drifting back into a data grid.
for needle in [
    'tc-archive-cover',
    'tc-dossier-spine',
    'tc-dossier-cover',
    'tc-armament-record',
    'tc-evidence-slip rite',
    'tc-evidence-slip chaos',
    'tc-evidence-slip penalties',
    'tc-evidence-slip rewards',
    'tc-evidence-footer',
    'Smithing Favor earned',
    'Partial archive',
]: require(needle)

# Defensive reward rendering supports both old string snapshots and newer reward
# objects without losing historical data.
for needle in [
    "if(typeof reward==='string')return reward;",
    "reward?.label||reward?.name||reward?.kind||'Covenant reward'",
]: require(needle)

print('Tarnished Covenant Compendium dossier invariants: PASS — full historical functionality retained in archive-style UI.')
