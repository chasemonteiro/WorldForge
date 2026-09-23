from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

s=re.sub(r"\n?/\* --- Weapon accessibility and Appeal deck memory --- \*/.*?/\* --- End weapon accessibility and Appeal deck memory --- \*/\n?","\n",s,flags=re.S)

# Repair the historical spreadsheet typo in generated pool data as well as the
# durable source file. The runtime migration below remains as compatibility for
# older cached pages/runs that may still carry the misspelled display name.
s=s.replace('"Malekith\'s Black Blade"','"Maliketh\'s Black Blade"')
s=s.replace('"malekith\'s black blade":','"maliketh\'s black blade":')

js=r'''
/* --- Weapon accessibility and Appeal deck memory --- */
// Weapons whose normal acquisition route requires defeating a boss remain out
// of the Covenant armory until that concrete boss kill is recorded. The gate
// model is intentionally data-driven so later regions can add acquisition rules
// without rewriting the draw engine.
const TC_WEAPON_ACQUISITION_GATES={
  "Bloodhound's Fang":[{name:'Bloodhound Knight Darriwil',region:'Limgrave + Stormveil'}],
  "Golden Halberd":[{name:'Tree Sentinel',region:'Limgrave + Stormveil'}],
  "Grafted Blade Greatsword":[{name:'Leonine Misbegotten',region:'Weeping Peninsula'}],
  "Nightrider Flail":[{name:"Night's Cavalry",region:'Weeping Peninsula'}],
  "Magma Wyrm's Scalesword":[{name:'Magma Wyrm Makar',region:'Liurnia of the Lakes'}],
  "Nightrider Glaive":[{name:"Night's Cavalry (Liurnia North)",region:'Liurnia of the Lakes'}],
  "Ornamental Straight Sword":[{name:'Grafted Scion',region:'Limgrave + Stormveil'}],
  "Dark Moon Greatsword":[{name:'Astel, Naturalborn of the Void',region:'Lake of Rot + Grand Cloister'}],

  "Gargoyle's Blackblade":[{name:'Black Blade Kindred',region:'Caelid'}],
  "Gargoyle's Black Halberd":[{name:'Black Blade Kindred',region:'Caelid'}],
  "Godslayer's Greatsword":[{name:'Godskin Apostle',region:'Caelid'}],
  "Lusat's Glintstone Staff":[{name:'Nox Swordstress & Nox Monk',region:'Caelid'}],
  "Moonveil":[{name:'Magma Wyrm',region:'Caelid'}],
  "Nox Flowing Sword":[{name:'Nox Swordstress & Nox Monk',region:'Caelid'}],
  "Regalia of Eochaid":[{name:'Frenzied Duelist',region:'Caelid'}],
  "Ruins Greatsword":[{name:'Crucible Knight and Misbegotten Warrior',region:'Caelid'}],

  "Dragon Halberd":[{name:'Dragonkin Soldier',region:'Siofra River + Nokron'}],
  "Gargoyle's Twinblade":[{name:'Valiant Gargoyle & Valiant Gargoyle (Twinblade)',region:'Siofra River + Nokron'}],
  "Gargoyle's Greatsword":[{name:'Valiant Gargoyle & Valiant Gargoyle (Twinblade)',region:'Siofra River + Nokron'}],
  "Alabaster Lord's Sword":[{name:'Alabaster Lord',region:'Lake of Rot + Grand Cloister'}],

  "Black Knife":[{name:"Black Knife Assassin (Sainted Hero's Grave)",region:'Altus Plateau + Leyndell'}],
  "Bloody Helice":[{name:'Sanguine Noble',region:'Altus Plateau + Leyndell'}],
  "Godskin Peeler":[{name:'Godskin Apostle',region:'Altus Plateau + Leyndell'}],
  "Great Club":[{name:'Stonedigger Troll',region:'Altus Plateau + Leyndell'}],
  "Marais Executioner's Sword":[{name:'Elemer of the Briar',region:'Altus Plateau + Leyndell'}],
  "Onyx Lord's Greatsword":[{name:'Onyx Lord',region:'Altus Plateau + Leyndell'}],
  "Coded Sword":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}],
  "Star Fist":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}],
  "Cane Sword":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}],
  "Black Bow":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}],
  "Gravel Stone Seal":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}],
  "Envoy's Long Horn":[{name:'Draconic Tree Sentinel',region:'Altus Plateau + Leyndell'}],
  "Erdtree Bow":[{name:'Godfrey, First Elden Lord',region:'Altus Plateau + Leyndell'}],
  "Bolt of Gransax":[{name:'Godfrey, First Elden Lord',region:'Altus Plateau + Leyndell'}],
  "Family Heads":[{name:'Necromancer Garris',region:'Altus Plateau + Leyndell'}],
  "Jar Cannon":[{name:'Demi-Human Queen Margot',region:'Mt. Gelmir'}],
  "Godskin Stitcher":[{name:'Godskin Noble',region:'Mt. Gelmir'}],
  "Inquisitor's Girandole":[{name:'Abductor Virgins (Duo)',region:'Mt. Gelmir'}],
  "Blasphemous Blade":[{name:'Rykard, Lord of Blasphemy',region:'Mt. Gelmir'}],

  "Veteran's Prosthesis":[{name:'Commander Niall',region:'Mountaintops of the Giants'}],
  "Zamor Curved Sword":[{name:'Ancient Hero of Zamor',region:'Mountaintops of the Giants'}],
  "Loretta's War Sickle":[{name:'Loretta, Knight of the Haligtree',region:'Miquella’s Haligtree'}],
  "Maliketh's Black Blade":[{name:'Maliketh, the Black Blade',region:'Crumbling Farum Azula'}],
  "Dragon King's Cragblade":[{name:'Dragonlord Placidusax',region:'Crumbling Farum Azula'}],

  "Greatsword of Solitude":[{name:'Blackgaol Knight',region:'Gravesite Plain · DLC'}],
  "Death Knight's Twin-Axes":[{name:'Death Knight',region:'Gravesite Plain · DLC'}],
  "Dryleaf Arts":[{name:'Dryleaf Dane',region:'Scadu Altus + Shadow Keep · DLC'}],
  "Rakshasa's Great Katana":[{name:'Rakshasa',region:'Scadu Altus + Shadow Keep · DLC'}],
  "Barbed Staff-Spear":[{name:'Jori, Elder Inquisitor',region:'Scadu Altus + Shadow Keep · DLC'}],
  "Maternal Staff":[
    {name:'Metyr, Mother of Fingers',region:'Scadu Altus + Shadow Keep · DLC'},
    {name:'Count Ymir, Mother of Fingers',region:'Scadu Altus + Shadow Keep · DLC'}
  ],
  "Sword of Night":[
    {name:'Metyr, Mother of Fingers',region:'Scadu Altus + Shadow Keep · DLC'},
    {name:'Count Ymir, Mother of Fingers',region:'Scadu Altus + Shadow Keep · DLC'}
  ],
  "Dancing Blade of Rannah":[{name:'Dancer of Ranah',region:'Cerulean Coast · DLC'}],
  "Star Lined Sword":[{name:'Demi-Human Queen Marigga',region:'Cerulean Coast · DLC'}],
  "Dragon-Hunter's Great Katana":[{name:'Ancient Dragon-Man',region:'Dragon’s Pit + Jagged Peak · DLC'}],
  "Flowerstone Gavel":[{name:'Bayle the Dread',region:'Dragon’s Pit + Jagged Peak · DLC'}],
  "Red Bear's Claw":[{name:'Rugalea the Great Red Bear',region:'Ancient Ruins of Rauh · DLC'}],
  "Death Knight's Longhaft Axe":[{name:'Death Knight',region:'Ancient Ruins of Rauh · DLC'}],
  "Leda's Sword":[{name:'Leda and Allies',region:'Enir-Ilim · DLC'}],
  "Dane's Footwork":[{name:'Leda and Allies',region:'Enir-Ilim · DLC'}],
  "Freyja's Greatsword":[{name:'Leda and Allies',region:'Enir-Ilim · DLC'}],
  "Obsidian Lamina":[{name:'Promised Consort Radahn',region:'Enir-Ilim · DLC'}],
  "Thiollier's Hidden Needle":[{name:'Promised Consort Radahn',region:'Enir-Ilim · DLC'}]
};

// Two spreadsheet imports had weapon rewards without their acquisition boss in
// the active boss pool. Restore those bosses so the gate can actually be earned.
const TC_ACQUISITION_BOSS_RESTORES={
  'Lake of Rot + Grand Cloister':['Alabaster Lord'],
  'Gravesite Plain · DLC':['Death Knight']
};
for(const [regionName,bosses] of Object.entries(TC_ACQUISITION_BOSS_RESTORES)){
  const pool=regions?.[regionName]?.bosses;
  if(!Array.isArray(pool))continue;
  for(const boss of bosses)if(!pool.some(name=>tcWeaponBossKey(name)===tcWeaponBossKey(boss)))pool.push(boss);
}

// The spreadsheet once shipped Maliketh's weapon as "Malekith's Black Blade".
// Canonicalize that legacy spelling so older source data cannot bypass the
// acquisition gate while the corrected regional pool propagates everywhere.
(function tcCanonicalizeMalikethWeapon(){
  for(const region of Object.values(regions||{})){
    for(const weapon of (region?.weapons||[])){
      if(tcWeaponNameKey(weapon?.name)===tcWeaponNameKey("Malekith's Black Blade"))weapon.name="Maliketh's Black Blade";
    }
  }
})();

// Greatsword is ordinary carriage loot in Caelid and was present in the app's
// original regional data before the spreadsheet pool accidentally displaced it.
(function tcRestoreCaelidGreatsword(){
  const pool=regions?.['Caelid']?.weapons;
  if(!Array.isArray(pool)||pool.some(w=>w?.name==='Greatsword'))return;
  const restored=typeof sheetWeapon==='function'?sheetWeapon('Greatsword'):W('Greatsword','Colossal Sword','Smithing Stones','Stamp (Upward Cut)');
  pool.push(restored);
})();

const TC_REGIONAL_WEAPON_RESTORES={
  'Altus Plateau + Leyndell':["Great Stars","Guardian's Swordspear"],
  'Mt. Gelmir':['Pulley Bow','Magma Blade'],
  'Mountaintops of the Giants':["Watchdog's Greatsword",'Thorned Whip',"Monk's Flameblade"],
  'Miquella’s Haligtree':["Cleanrot Knight's Sword",'Cleanrot Spear','Halo Scythe',"Envoy's Greathorn"],
  'Crumbling Farum Azula':["Beastman's Curved Sword","Beastman's Cleaver","Banished Knight's Greatsword","Banished Knight's Halberd"],
  'Scadu Altus + Shadow Keep · DLC':['Carian Thrusting Shield']
};
for(const [regionName,names] of Object.entries(TC_REGIONAL_WEAPON_RESTORES)){
  const pool=regions?.[regionName]?.weapons;
  if(!Array.isArray(pool))continue;
  for(const name of names){
    if(pool.some(w=>tcWeaponNameKey(w?.name)===tcWeaponNameKey(name)))continue;
    pool.push(typeof sheetWeapon==='function'?sheetWeapon(name):W(name,'Regional weapon','Smithing path varies','Native skill',false));
  }
}

// Leyndell proper opens after Draconic Tree Sentinel. Keep these weapons in the
// combined Altus/Leyndell deck, then let acquisition gates decide when they can draw.
(function tcRestoreLeyndellWeapons(){
  const pool=regions?.['Altus Plateau + Leyndell']?.weapons;
  if(!Array.isArray(pool))return;
  const extra=[
    W('Coded Sword','Straight Sword','Somber Smithing Stones','Unblockable Blade',false),
    W('Star Fist','Fist','Smithing Stones','Endure'),
    W('Cane Sword','Straight Sword','Smithing Stones','Square Off'),
    W('Black Bow','Bow','Somber Smithing Stones','Barrage',false),
    W('Gravel Stone Seal','Sacred Seal','Smithing Stones','No Skill',false),
    W("Envoy's Long Horn",'Great Hammer','Somber Smithing Stones','Bubble Shower',false),
    W('Erdtree Bow','Bow','Somber Smithing Stones','Mighty Shot',false),
    W('Bolt of Gransax','Spear','Somber Smithing Stones','Ancient Lightning Spear',false)
  ];
  for(const weapon of extra){const i=pool.findIndex(w=>tcWeaponNameKey(w?.name)===tcWeaponNameKey(weapon.name));if(i>=0)pool[i]=weapon;else pool.push(weapon);}
})();

function tcWeaponBossKey(name){
  if(typeof tcBossKey==='function')return tcBossKey(name);
  return String(name||'').toLowerCase().replace(/[’‘]/g,"'").replace(/[^a-z0-9]+/g,' ').trim();
}
function tcWeaponNameKey(name){
  return String(name||'')
    .replace(/\s*\(\+\d+\)\s*$/,'')
    .toLowerCase()
    .replace(/[’‘]/g,"'")
    .replace(/[‐‑‒–—-]/g,' ')
    .replace(/[^a-z0-9']+/g,' ')
    .replace(/\s+/g,' ')
    .trim();
}
const TC_WEAPON_ACQUISITION_GATE_INDEX=new Map(
  Object.entries(TC_WEAPON_ACQUISITION_GATES).map(([name,requirements])=>[tcWeaponNameKey(name),requirements])
);
function tcWeaponAcquisitionRequirements(weapon){
  const requirements=[...(TC_WEAPON_ACQUISITION_GATE_INDEX.get(tcWeaponNameKey(weapon?.name))||[])];
  const inline=String(weapon?.requires||'').trim();
  if(inline&&!requirements.some(req=>tcWeaponBossKey(req?.name)===tcWeaponBossKey(inline)))requirements.push({name:inline});
  return requirements;
}
function tcRecordedBossDefeated(state,requirement){
  const wanted=[requirement?.name,...(Array.isArray(requirement?.aliases)?requirement.aliases:[])].filter(Boolean).map(tcWeaponBossKey);
  const region=requirement?.region||'';
  if(!wanted.length)return true;
  const matches=entry=>entry&&wanted.includes(tcWeaponBossKey(entry.name))&&(!region||entry.region===region);
  if((state?.history||[]).some(matches))return true;
  if((state?.sanctionedBossKills||[]).some(matches))return true;
  if((state?.appealPenaltyBossKills||[]).some(matches))return true;
  return false;
}
function tcWeaponAcquisitionUnlocked(state,weapon){
  const gates=tcWeaponAcquisitionRequirements(weapon);
  return !gates.length||gates.every(req=>tcRecordedBossDefeated(state,req));
}
function tcLegalRegionWeapons(state,regionName,target){
  const region=regions?.[regionName];
  if(!region)return [];
  return (region.weapons||[]).filter(w=>!weaponBlockedByTarget(w,target)&&tcWeaponAcquisitionUnlocked(state,w));
}
function tcLegalAccumulatedWeaponPool(state,target){
  const regionNames=Array.from(new Set([...(state?.clearedRegions||[]),state?.region].filter(Boolean)));
  const byName=new Map();
  for(const regionName of regionNames){
    for(const weapon of tcLegalRegionWeapons(state,regionName,target))if(!byName.has(weapon.name))byName.set(weapon.name,weapon);
  }
  return [...byName.values()];
}
function tcAppealSeenWeapons(state){
  return new Set(Array.isArray(state?.current?.appealedWeaponNames)?state.current.appealedWeaponNames:[]);
}
function tcWeaponFamilyKey(name){
  const key=tcWeaponNameKey(name);
  if(key.startsWith("celebrant's "))return 'celebrant';
  return '';
}
function tcBestDiversePairFromPool(state,chasePool,morganPool){
  const all=[];
  for(const chaseWeapon of chasePool){
    for(const morganWeapon of morganPool){
      if(chaseWeapon.name===morganWeapon.name)continue;
      const cf=tcWeaponFamilyKey(chaseWeapon.name),mf=tcWeaponFamilyKey(morganWeapon.name);
      all.push({chaseWeapon,morganWeapon,sameFamily:Boolean(cf&&cf===mf),score:scoreWeaponPair(state,chaseWeapon,morganWeapon,Math.max(chasePool.length,morganPool.length))});
    }
  }
  if(!all.length)return null;
  const diverse=all.filter(x=>!x.sameFamily);
  const candidates=diverse.length?diverse:all;
  candidates.sort((a,b)=>b.score-a.score);
  return candidates[0];
}
function tcBuildWeaponPairFromCandidate(pair){
  if(!pair?.chaseWeapon||!pair?.morganWeapon)return null;
  return {chase:buildFromWeapon(pair.chaseWeapon),morgan:buildFromWeapon(pair.morganWeapon)};
}

// Make every downstream accumulated-pool caller acquisition-aware.
const tcAccumulatedWeaponPoolBeforeAccess=accumulatedWeaponPool;
accumulatedWeaponPool=function(state,target){
  const legal=tcLegalAccumulatedWeaponPool(state,target);
  return legal.length?legal:tcAccumulatedWeaponPoolBeforeAccess(state,target).filter(w=>tcWeaponAcquisitionUnlocked(state,w));
};

// New encounters burn through fresh, obtainable weapons in the present region
// first, then fall back to obtainable weapons from regions already reached.
// IMPORTANT: bestPairFromPool returns raw weapon candidates; newEncounter expects
// fully built {chase,morgan} assignments. Never leak the raw pair shape.
const tcChooseWeaponPairBeforeAccess=chooseWeaponPair;
chooseWeaponPair=function(state,target){
  const currentPool=tcLegalRegionWeapons(state,state.region,target),used=usedWeaponNames(state),unusedCurrent=currentPool.filter(w=>!used.has(w.name));
  let pair=null;
  if(unusedCurrent.length>=2)pair=tcBestDiversePairFromPool(state,unusedCurrent,unusedCurrent);
  else if(unusedCurrent.length===1){
    const fallback=tcLegalAccumulatedWeaponPool(state,target).filter(w=>w.name!==unusedCurrent[0].name&&!used.has(w.name));
    const broad=fallback.length?fallback:tcLegalAccumulatedWeaponPool(state,target).filter(w=>w.name!==unusedCurrent[0].name);
    if(broad.length)pair=Math.random()<0.5?tcBestDiversePairFromPool(state,unusedCurrent,broad):tcBestDiversePairFromPool(state,broad,unusedCurrent);
  }
  if(!pair){
    const all=tcLegalAccumulatedWeaponPool(state,target),unused=all.filter(w=>!used.has(w.name));
    const pool=unused.length>=2?unused:all;
    if(pool.length>=2)pair=tcBestDiversePairFromPool(state,pool,pool);
  }
  const built=tcBuildWeaponPairFromCandidate(pair);
  if(built)return built;

  // A legacy result is acceptable only if it already contains two complete
  // builds and both named weapons are legal under the acquisition gate model.
  const legacy=tcChooseWeaponPairBeforeAccess(state,target);
  if(legacy?.chase?.name&&legacy?.morgan?.name){
    const legalNames=new Set(tcLegalAccumulatedWeaponPool(state,target).map(w=>w.name));
    if(legalNames.has(legacy.chase.name)&&legalNames.has(legacy.morgan.name))return legacy;
  }
  throw new Error('Covenant armory could not produce two legally obtainable weapon assignments. Encounter creation was stopped before saving malformed state.');
};

// Defense in depth: a future armory patch must never be able to serialize an
// encounter that the Encounter tab cannot render.
const tcNewEncounterBeforeWeaponAccessGuard=newEncounter;
newEncounter=function(state){
  const encounter=tcNewEncounterBeforeWeaponAccessGuard(state);
  if(!encounter?.chase?.name||!encounter?.morgan?.name){
    throw new Error('Covenant refused to save an encounter without two valid weapon assignments.');
  }
  return encounter;
};

// Appeals remember every weapon rejected during the current encounter. They
// keep drawing forward through the legal deck instead of circling back to a
// weapon that was already appealed away.
const tcMakeBuildBeforeAccess=makeBuild;
makeBuild=function(regionName,target,avoidNames=[],state=null){
  if(!state)return tcMakeBuildBeforeAccess(regionName,target,avoidNames,state);
  const avoided=new Set(Array.isArray(avoidNames)?avoidNames:[avoidNames]);
  for(const name of tcAppealSeenWeapons(state))avoided.add(name);
  let pool=tcLegalRegionWeapons(state,regionName,target).filter(w=>!avoided.has(w.name));
  const currentNames=[state?.current?.chase?.name,state?.current?.morgan?.name,...tcAppealSeenWeapons(state)].filter(Boolean);
  const seenFamilies=new Set(currentNames.map(tcWeaponFamilyKey).filter(Boolean));
  const familyDiverse=pool.filter(w=>{const family=tcWeaponFamilyKey(w.name);return !family||!seenFamilies.has(family);});
  if(familyDiverse.length)pool=familyDiverse;
  const unused=pool.filter(w=>!usedWeaponNames(state).has(w.name));
  if(unused.length)pool=unused;
  else{
    const accumulated=tcLegalAccumulatedWeaponPool(state,target).filter(w=>!avoided.has(w.name));
    const accumulatedUnused=accumulated.filter(w=>!usedWeaponNames(state).has(w.name));
    pool=accumulatedUnused.length?accumulatedUnused:accumulated;
  }
  if(!pool.length){
    const legal=tcLegalAccumulatedWeaponPool(state,target).filter(w=>!new Set(Array.isArray(avoidNames)?avoidNames:[avoidNames]).has(w.name));
    if(legal.length)pool=legal;
  }
  if(!pool.length)throw new Error('No legally obtainable Covenant weapon is available for this appeal.');
  return buildFromWeapon(pick(pool));
};

const tcChangeWeaponsBeforeAccess=changeWeapons;
changeWeapons=function(state,actor,which,useWaiver=false){
  const prepared=structuredClone(state),c=prepared?.current;
  if(c){
    const seen=new Set(Array.isArray(c.appealedWeaponNames)?c.appealedWeaponNames:[]);
    if((which==='chase'||which==='both')&&c.chase?.name)seen.add(c.chase.name);
    if((which==='morgan'||which==='both')&&c.morgan?.name)seen.add(c.morgan.name);
    c.appealedWeaponNames=[...seen];
  }
  return tcChangeWeaponsBeforeAccess(prepared,actor,which,useWaiver);
};

// Joint Appeal uses the same legal draw engine and should also retire the two
// rejected assignments from the encounter's Appeal deck.
const tcBuildJointAppealBeforeWeaponAccess=tcBuildJointAppeal;
tcBuildJointAppeal=function(latest,encounterId,oldChase,oldMorgan,newChase,newMorgan,actor){
  const next=tcBuildJointAppealBeforeWeaponAccess(latest,encounterId,oldChase,oldMorgan,newChase,newMorgan,actor);
  if(next?.current){
    const seen=new Set(Array.isArray(next.current.appealedWeaponNames)?next.current.appealedWeaponNames:[]);
    if(oldChase)seen.add(oldChase);if(oldMorgan)seen.add(oldMorgan);next.current.appealedWeaponNames=[...seen];
  }
  return next;
};
/* --- End weapon accessibility and Appeal deck memory --- */
'''

idx=s.rfind('/* --- Home Screen freshness guard --- */')
if idx<0:
    idx=s.rfind('</script>')
if idx<0: raise SystemExit('weapon accessibility insertion anchor missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in [
    'const TC_WEAPON_ACQUISITION_GATES=',
    'const TC_WEAPON_ACQUISITION_GATE_INDEX=new Map(',
    'function tcWeaponAcquisitionRequirements(weapon)',
    'const TC_ACQUISITION_BOSS_RESTORES=',
    "\"Gargoyle's Black Halberd\":[{name:'Black Blade Kindred',region:'Caelid'}]",
    "\"Nox Flowing Sword\":[{name:'Nox Swordstress & Nox Monk',region:'Caelid'}]",
    "\"Moonveil\":[{name:'Magma Wyrm',region:'Caelid'}]",
    "\"Regalia of Eochaid\":[{name:'Frenzied Duelist',region:'Caelid'}]",
    "pool.some(w=>w?.name==='Greatsword')",
    'function tcRecordedBossDefeated(state,requirement)',
    'state?.sanctionedBossKills',
    'state?.appealPenaltyBossKills',
    'function tcLegalRegionWeapons(state,regionName,target)',
    'function tcLegalAccumulatedWeaponPool(state,target)',
    'function tcBuildWeaponPairFromCandidate(pair)',
    'return {chase:buildFromWeapon(pair.chaseWeapon),morgan:buildFromWeapon(pair.morganWeapon)};',
    'const tcNewEncounterBeforeWeaponAccessGuard=newEncounter;',
    'encounter?.chase?.name',
    'encounter?.morgan?.name',
    'appealedWeaponNames',
    'const tcChangeWeaponsBeforeAccess=changeWeapons;',
    'const tcBuildJointAppealBeforeWeaponAccess=tcBuildJointAppeal;'
]:
    if needle not in s: raise SystemExit('weapon accessibility invariant missing: '+needle)
p.write_text(s)
