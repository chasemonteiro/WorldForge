from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or f'missing required-boss invariant: {needle}')

def forbid(needle,msg=None):
    if needle in html: raise SystemExit(msg or f'forbidden progression gate: {needle}')

# Required in-region gates. These should beat all normal RNG and capstone rolls.
for needle in [
    "'Limgrave + Stormveil':['Margit, The Fell Omen']",
    "'Liurnia of the Lakes':['Red Wolf of Radagon']",
    "'Siofra River + Nokron':['Mimic Tear']",
    "'Deeproot Depths':[\"Fia's champions\"]",
    "'Altus Plateau + Leyndell':['Draconic Tree Sentinel','Godfrey, First Elden Lord']",
    "'Mountaintops of the Giants':['Commander Niall']",
    "'Miquella’s Haligtree':['Loretta, Knight of the Haligtree']",
    "'Crumbling Farum Azula':['Godskin Duo']",
    "'Leyndell, Ashen Capital':['Sir Gideon Ofnir, the All-Knowing']",
    "'Dragon’s Pit + Jagged Peak · DLC':['Ancient Dragon-Man']",
    "'Abyssal Woods · DLC':['Jori, Elder Inquisitor']",
    "'Enir-Ilim · DLC':['Leda and Allies']",
]: require(needle)

# Redmane is conditional: the duo gates Radahn only until Altus has actually been visited.
for needle in [
    "if(regionName==='Caelid'&&!tcRegionEverVisited(state,'Altus Plateau + Leyndell'))",
    "sequence.unshift('Crucible Knight and Misbegotten Warrior')",
    'function tcRegionEverVisited(state,regionName)',
]: require(needle)

# Required target must be selected before available optional bosses/capstone RNG.
require('const requiredBoss=tcNextRequiredBoss(state);')
require('if(requiredBoss)return {name:requiredBoss,exit:false,required:true};')
choose=html.find('function chooseTarget(state) {')
forced=html.find('const requiredBoss=tcNextRequiredBoss(state);',choose)
available=html.find('const available = availableRegionalBosses(state);',choose)
if choose<0 or forced<0 or available<0 or not (choose < forced < available):
    raise SystemExit('required boss is not selected before normal regional RNG')

# Capstone is hard-sealed while a gate remains.
require("if(typeof tcNextRequiredBoss==='function'&&tcNextRequiredBoss(state))return 0;")

# Jori belongs to the Abyssal route in the runtime pool, not random Scadu Altus RNG.
require(".filter(name=>tcBossKey(name)!==tcBossKey('Jori, Elder Inquisitor'));")
require("Array.from(new Set(['Jori, Elder Inquisitor',...(regions['Abyssal Woods · DLC'].bosses||[])]))")

# Optional-kill reward cannot bypass progression bosses.
require('if(tcIsRequiredBossForRegion(state,region,name))continue;')

# Already-existing cross-region story gates should remain intact.
for needle in [
    "case 'Mountaintops of the Giants':\n      return has('Morgott, the Omen King');",
    "case 'Crumbling Farum Azula':\n      return has('Fire Giant');",
    "case 'Leyndell, Ashen Capital':\n      return has('Maliketh, the Black Blade');",
    "return Boolean(state.includeDlc) && has('Starscourge Radahn') && has('Mohg, Lord of Blood');",
    "return Boolean(state.includeDlc) && has('Messmer the Impaler') && has('Romina, Saint of the Bud');",
]: require(needle)

# Do not over-lock bosses that have legitimate bypasses / are optional routes.
sequence_start=html.find('const TC_REQUIRED_BOSS_SEQUENCES=')
sequence_end=html.find('};',sequence_start)
seq=html[sequence_start:sequence_end+2]
for optional in [
    'Godskin Noble',
    'Golden Hippopotamus',
    'Ancient Dragon Senessax',
    'Valiant Gargoyle',
    'Divine Beast Dancing Lion',
    'Rellana, Twin Moon Knight',
]:
    if optional in seq:
        raise SystemExit('optional/bypassable boss incorrectly hard-gated: '+optional)

# Tiny behavioral model for the two special cases.
def key(name):
    import re
    return re.sub(r'[^a-z0-9]+',' ',name.lower().replace('’',"'")).strip()

def next_required(region,history,altus_visited=False):
    table={
        'Limgrave + Stormveil':['Margit, The Fell Omen'],
        'Altus Plateau + Leyndell':['Draconic Tree Sentinel','Godfrey, First Elden Lord'],
        'Crumbling Farum Azula':['Godskin Duo'],
    }
    seq=list(table.get(region,[]))
    if region=='Caelid' and not altus_visited:
        seq.insert(0,'Crucible Knight and Misbegotten Warrior')
    done={key(x) for x in history}
    return next((x for x in seq if key(x) not in done),None)

assert next_required('Limgrave + Stormveil',[])=='Margit, The Fell Omen'
assert next_required('Limgrave + Stormveil',['Margit, the Fell Omen']) is None
assert next_required('Altus Plateau + Leyndell',[])=='Draconic Tree Sentinel'
assert next_required('Altus Plateau + Leyndell',['Draconic Tree Sentinel'])=='Godfrey, First Elden Lord'
assert next_required('Caelid',[],False)=='Crucible Knight and Misbegotten Warrior'
assert next_required('Caelid',[],True) is None

print('Tarnished Covenant required boss sequence invariants: PASS')
