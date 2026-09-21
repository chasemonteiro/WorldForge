from pathlib import Path
import re

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or 'missing weapon accessibility invariant: '+needle)

def forbid(needle,msg=None):
    if needle in html: raise SystemExit(msg or 'forbidden weapon accessibility behavior: '+needle)

# The acquisition table must be universal, not a Caelid-only patch.
gate_match=re.search(r"const TC_WEAPON_ACQUISITION_GATES=\{([\s\S]*?)\n\};",html)
if not gate_match:
    raise SystemExit('universal weapon gate table missing')
gate_block=gate_match.group(1)
gate_count=len(re.findall(r'^\s{2}"[^"]+":\[',gate_block,re.M))
if gate_count < 45:
    raise SystemExit(f'universal weapon gate table unexpectedly small: {gate_count} entries')

# Representative gates from the opening hours through endgame and DLC.
for needle in [
    "\"Bloodhound's Fang\":[{name:'Bloodhound Knight Darriwil',region:'Limgrave + Stormveil'}]",
    "\"Golden Halberd\":[{name:'Tree Sentinel',region:'Limgrave + Stormveil'}]",
    "\"Grafted Blade Greatsword\":[{name:'Leonine Misbegotten',region:'Weeping Peninsula'}]",
    "\"Magma Wyrm's Scalesword\":[{name:'Magma Wyrm Makar',region:'Liurnia of the Lakes'}]",
    "\"Dark Moon Greatsword\":[{name:'Astel, Naturalborn of the Void',region:'Lake of Rot + Grand Cloister'}]",
    "\"Moonveil\":[{name:'Magma Wyrm',region:'Caelid'}]",
    "\"Dragon Halberd\":[{name:'Dragonkin Soldier',region:'Siofra River + Nokron'}]",
    "\"Gargoyle's Twinblade\":[{name:'Valiant Gargoyle & Valiant Gargoyle (Twinblade)',region:'Siofra River + Nokron'}]",
    "\"Bloody Helice\":[{name:'Sanguine Noble',region:'Altus Plateau + Leyndell'}]",
    "\"Marais Executioner's Sword\":[{name:'Elemer of the Briar',region:'Altus Plateau + Leyndell'}]",
    "\"Blasphemous Blade\":[{name:'Rykard, Lord of Blasphemy',region:'Mt. Gelmir'}]",
    "\"Veteran's Prosthesis\":[{name:'Commander Niall',region:'Mountaintops of the Giants'}]",
    "\"Loretta's War Sickle\":[{name:'Loretta, Knight of the Haligtree',region:'Miquella’s Haligtree'}]",
    "\"Dragon King's Cragblade\":[{name:'Dragonlord Placidusax',region:'Crumbling Farum Azula'}]",
    "\"Greatsword of Solitude\":[{name:'Blackgaol Knight',region:'Gravesite Plain · DLC'}]",
    "\"Death Knight's Twin-Axes\":[{name:'Death Knight',region:'Gravesite Plain · DLC'}]",
    "\"Dryleaf Arts\":[{name:'Dryleaf Dane',region:'Scadu Altus + Shadow Keep · DLC'}]",
    "\"Rakshasa's Great Katana\":[{name:'Rakshasa',region:'Scadu Altus + Shadow Keep · DLC'}]",
    "\"Star Lined Sword\":[{name:'Demi-Human Queen Marigga',region:'Cerulean Coast · DLC'}]",
    "\"Dragon-Hunter's Great Katana\":[{name:'Ancient Dragon-Man',region:'Dragon’s Pit + Jagged Peak · DLC'}]",
    "\"Death Knight's Longhaft Axe\":[{name:'Death Knight',region:'Ancient Ruins of Rauh · DLC'}]",
    "\"Leda's Sword\":[{name:'Leda and Allies',region:'Enir-Ilim · DLC'}]",
    "\"Obsidian Lamina\":[{name:'Promised Consort Radahn',region:'Enir-Ilim · DLC'}]",
]: require(needle)

# Multi-stage quest rewards are not legal until every modeled boss requirement is met.
for needle in [
    '"Maternal Staff":[',
    "{name:'Metyr, Mother of Fingers',region:'Scadu Altus + Shadow Keep · DLC'}",
    "{name:'Count Ymir, Mother of Fingers',region:'Scadu Altus + Shadow Keep · DLC'}",
    '"Sword of Night":[',
]: require(needle)

# Spreadsheet imports had removed two acquisition bosses that their weapon pools need.
for needle in [
    'const TC_ACQUISITION_BOSS_RESTORES={',
    "'Lake of Rot + Grand Cloister':['Alabaster Lord']",
    "'Gravesite Plain · DLC':['Death Knight']",
]: require(needle)

# Gate lookup is normalized and also honors any hand-authored weapon.requires metadata.
for needle in [
    'function tcWeaponNameKey(name)',
    ".replace(/\\s*\\(\\+\\d+\\)\\s*$/,'')",
    "replace(/[’‘]/g,\"'\")",
    "replace(/[‐‑‒–—-]/g,' ')",
    'const TC_WEAPON_ACQUISITION_GATE_INDEX=new Map(',
    'function tcWeaponAcquisitionRequirements(weapon)',
    "const inline=String(weapon?.requires||'').trim();",
    'const gates=tcWeaponAcquisitionRequirements(weapon);',
    'gates.every(req=>tcRecordedBossDefeated(state,req))',
]: require(needle)

# Normal victories, Sanctioned Boss Kills, and recorded Weapon Appeal extra-boss kills
# are all legitimate ways to satisfy an acquisition boss gate.
for needle in [
    'function tcRecordedBossDefeated(state,requirement)',
    '(state?.history||[]).some(matches)',
    '(state?.sanctionedBossKills||[]).some(matches)',
    '(state?.appealPenaltyBossKills||[]).some(matches)',
]: require(needle)

# Ordinary accessible Caelid loot stays in the pool.
for needle in [
    "pool.some(w=>w?.name==='Greatsword')",
    "sheetWeapon('Greatsword')",
]: require(needle)

# Every assignment path must pass through acquisition-aware legal pools.
for needle in [
    'function tcLegalRegionWeapons(state,regionName,target)',
    '!weaponBlockedByTarget(w,target)&&tcWeaponAcquisitionUnlocked(state,w)',
    'function tcLegalAccumulatedWeaponPool(state,target)',
    'chooseWeaponPair=function(state,target)',
    'const currentPool=tcLegalRegionWeapons(state,state.region,target)',
    'const all=tcLegalAccumulatedWeaponPool(state,target)',
    'makeBuild=function(regionName,target,avoidNames=[],state=null)',
]: require(needle)

# bestPairFromPool returns raw candidates. The accessibility layer must convert
# them back into the complete {chase,morgan} build shape expected by newEncounter.
for needle in [
    'function tcBuildWeaponPairFromCandidate(pair)',
    'if(!pair?.chaseWeapon||!pair?.morganWeapon)return null;',
    'return {chase:buildFromWeapon(pair.chaseWeapon),morgan:buildFromWeapon(pair.morganWeapon)};',
    'const built=tcBuildWeaponPairFromCandidate(pair);',
    'if(built)return built;',
    'const tcNewEncounterBeforeWeaponAccessGuard=newEncounter;',
    'if(!encounter?.chase?.name||!encounter?.morgan?.name)',
    'Covenant refused to save an encounter without two valid weapon assignments.',
]: require(needle)
forbid('  return pair;','raw bestPairFromPool candidate may not be returned from chooseWeaponPair')

# Appeals keep moving forward through the legal deck instead of immediately
# recycling the weapon that was just rejected.
for needle in [
    'function tcAppealSeenWeapons(state)',
    'state?.current?.appealedWeaponNames',
    'const tcChangeWeaponsBeforeAccess=changeWeapons;',
    "if((which==='chase'||which==='both')&&c.chase?.name)seen.add(c.chase.name);",
    "if((which==='morgan'||which==='both')&&c.morgan?.name)seen.add(c.morgan.name);",
    'c.appealedWeaponNames=[...seen];',
    'const accumulated=tcLegalAccumulatedWeaponPool(state,target).filter(w=>!avoided.has(w.name));',
    'const tcBuildJointAppealBeforeWeaponAccess=tcBuildJointAppeal;',
]: require(needle)

forbid("if(!pool.length) pool = eligibleWeapons(regionName, target);",'legacy inaccessible appeal fallback survived late accessibility layer')

print(f'Tarnished Covenant weapon accessibility: PASS — {gate_count} boss-gated weapons are enforced across the full run, all unlock paths are recognized, fallback pools stay legal, and Appeals do not recycle rejected weapons.')
