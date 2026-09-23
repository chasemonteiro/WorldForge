from pathlib import Path
import re
import subprocess
import textwrap

html=Path('tarnished-covenant/index.html').read_text()
regional_source=Path('tarnished-covenant/regional-pools.js').read_text()

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
if gate_count < 53:
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
    "\"Coded Sword\":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}]",
    "\"Star Fist\":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}]",
    "\"Cane Sword\":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}]",
    "\"Black Bow\":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}]",
    "\"Gravel Stone Seal\":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}]",
    "\"Envoy's Long Horn\":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}]",
    "\"Erdtree Bow\":[{name:'Godfrey, First Elden Lord',region:'Altus Plateau + Leyndell'}]",
    "\"Bolt of Gransax\":[{name:'Godfrey, First Elden Lord',region:'Altus Plateau + Leyndell'}]",
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
    "\"Red Bear's Claw\":[{name:'Rugalea the Great Red Bear',region:'Ancient Ruins of Rauh · DLC'}]",
    "\"Death Knight's Longhaft Axe\":[{name:'Death Knight',region:'Ancient Ruins of Rauh · DLC'}]",
    "\"Leda's Sword\":[{name:'Leda and Allies',region:'Enir-Ilim · DLC'}]",
    "\"Obsidian Lamina\":[{name:'Promised Consort Radahn',region:'Enir-Ilim · DLC'}]",
]: require(needle)

# Canonical source spelling and the runtime migration both keep Maliketh's
# weapon inside the gate table, including rebuilds from older cached data.
for needle in [
    'function tcCanonicalizeMalikethWeapon()',
    'weapon.name="Maliketh\'s Black Blade";',
]: require(needle)
if "Malekith's Black Blade" in regional_source:
    raise SystemExit('regional weapon source still contains the gate-bypassing Malekith misspelling')
if "Maliketh's Black Blade" not in regional_source:
    raise SystemExit('canonical Maliketh weapon is missing from the regional source pool')

# Cross-check the generated acquisition table against the spreadsheet-backed
# armory. Every gated weapon must exist in a pool, and every region-specific
# requirement must be a boss, capstone, or explicit restored acquisition boss.
node_audit=textwrap.dedent(r'''
const fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('tarnished-covenant/index.html','utf8');
const data=fs.readFileSync('tarnished-covenant/regional-pools.js','utf8');
const gateMatch=html.match(/const TC_WEAPON_ACQUISITION_GATES=(\{[\s\S]*?\n\});\n\n\/\/ Two spreadsheet/);
const restoreMatch=html.match(/const TC_ACQUISITION_BOSS_RESTORES=(\{[\s\S]*?\n\});/);
if(!gateMatch||!restoreMatch)throw new Error('weapon gate or restore table missing');
const ctx={};vm.createContext(ctx);
vm.runInContext(data+';this.weaponPools=SHEET_WEAPON_POOLS;this.bossPools=SHEET_BOSS_POOLS;',ctx);
vm.runInContext('this.gates='+gateMatch[1]+';this.restores='+restoreMatch[1],ctx);
function weaponKey(name){return String(name||'').replace(/\s*\(\+\d+\)\s*$/,'').toLowerCase().replace(/[’‘]/g,"'").replace(/[‐‑‒–—-]/g,' ').replace(/[^a-z0-9']+/g,' ').replace(/\s+/g,' ').trim();}
function bossKey(name){let key=String(name||'').normalize('NFKD').replace(/[’‘]/g,"'").toLowerCase().replace(/&/g,' and ').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');if(/^valiant gargoyle/.test(key)||key==='valiant gargoyles')return 'valiant gargoyles';if(key.includes('crucible knight')&&key.includes('misbegotten warrior'))return 'crucible misbegotten duo';return key;}
const exits={};
for(const match of html.matchAll(/\n\s*'([^']+)'\s*:\s*\{\s*\n\s*exit:\s*'([^']+)'/g))exits[match[1]]=match[2];
for(const match of html.matchAll(/regions\['([^']+)'\]\s*=\s*\{\s*\n\s*exit:\s*'([^']+)'/g))exits[match[1]]=match[2];
const poolWeapons=new Set(Object.values(ctx.weaponPools).flat().map(weaponKey));
const errors=[];
for(const [weapon,requirements] of Object.entries(ctx.gates)){
  if(!poolWeapons.has(weaponKey(weapon)))errors.push(`gated weapon missing from source pools: ${weapon}`);
  for(const requirement of requirements){
    if(!requirement.region)continue;
    const available=[...(ctx.bossPools[requirement.region]||[]),...(ctx.restores[requirement.region]||[]),exits[requirement.region]].filter(Boolean).map(bossKey);
    const accepted=[requirement.name,...(requirement.aliases||[])].map(bossKey);
    if(!accepted.some(name=>available.includes(name)))errors.push(`unsatisfiable acquisition gate: ${weapon} <- ${requirement.name} @ ${requirement.region}`);
  }
}
if(errors.length)throw new Error(errors.join('\n'));
''')
audit=subprocess.run(['node','-e',node_audit],text=True,capture_output=True)
if audit.returncode:
    raise SystemExit('weapon acquisition data audit failed:\n'+(audit.stderr or audit.stdout))

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

# Leyndell proper expands the combined regional armory after DTS; two sanctuary-area
# rewards wait for Golden Godfrey.
for needle in [
    'function tcRestoreLeyndellWeapons()',
    "W('Coded Sword','Straight Sword','Somber Smithing Stones','Unblockable Blade',false)",
    "W('Star Fist','Fist','Smithing Stones','Endure')",
    "W('Cane Sword','Straight Sword','Smithing Stones','Square Off')",
    "W('Black Bow','Bow','Somber Smithing Stones','Barrage',false)",
    "W('Gravel Stone Seal','Sacred Seal','Smithing Stones','No Skill',false)",
    "W(\"Envoy's Long Horn\",'Great Hammer','Somber Smithing Stones','Bubble Shower',false)",
    "W('Erdtree Bow','Bow','Somber Smithing Stones','Mighty Shot',false)",
    "W('Bolt of Gransax','Spear','Somber Smithing Stones','Ancient Lightning Spear',false)",
    "const i=pool.findIndex(w=>tcWeaponNameKey(w?.name)===tcWeaponNameKey(weapon.name));if(i>=0)pool[i]=weapon;else pool.push(weapon);",
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
