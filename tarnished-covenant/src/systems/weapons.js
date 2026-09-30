/* --- Weapon accessibility and Appeal deck memory --- */
// Weapons whose normal acquisition route requires defeating a boss remain out
// of the Covenant armory until that concrete boss kill is recorded. The gate
// model is intentionally data-driven so later regions can add acquisition rules
// without rewriting the draw engine.
{{generated/acquisition-gates.js}}

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
  'Limgrave + Stormveil':['Axe of Godrick','Grafted Dragon',"Rogier's Rapier"],
  'Weeping Peninsula':['Bastard Sword','Light Crossbow','Sacrificial Axe','Misbegotten Shortbow',"Guardian's Swordspear"],
  'Liurnia of the Lakes':['Carian Regal Scepter'],
  'Caelid':['Greatsword',"Death's Poker","Cleanrot Knight's Sword",'Cleanrot Spear','Halo Scythe','Spiked Caestus','Beast-Repellent Torch','Starscourge Greatsword','Lion Greatbow','Cinquedea'],
  'Siofra River + Nokron':['Winged Greathorn'],
  'Lake of Rot + Grand Cloister':["Scorpion's Stinger",'Dragonscale Blade',"Bastard's Stars"],
  'Deeproot Depths':["Siluria's Tree","Prince of Death's Staff"],
  'Altus Plateau + Leyndell':["Great Stars","Guardian's Swordspear",'Raptor Talons',"Envoy's Horn",'Antspur Rapier','Battle Hammer',"Troll's Golden Sword",'Greatbow',"Sentry's Torch",'Golden Order Seal','Golden Epitaph','Hammer',"Gargoyle's Halberd",'Dragon Greatclaw',"Ordovis's Greatsword","Morgott's Cursed Sword"],
  'Mt. Gelmir':['Pulley Bow','Magma Blade','Fallingstar Beast Jaw','Staff of the Guilty','Gelmir Glintstone Staff','Albinauric Staff','Erdtree Seal','Magma Whip Candlestick'],
  'Mountaintops of the Giants':["Watchdog's Greatsword",'Thorned Whip',"Monk's Flameblade","Helphen's Steeple",'Death Ritual Spear','Rotten Battle Hammer','Golden Order Greatsword',"Gargoyle's Black Blades","Gargoyle's Black Axe","Giant's Red Braid",'Flowing Curved Sword','Albinauric Bow',"St. Trina's Torch"],
  'Mohgwyn Palace':["Mohgwyn's Sacred Spear",'Ripple Crescent Halberd','Curved Club','Curved Great Club'],
  'Miquella’s Haligtree':["Cleanrot Knight's Sword",'Cleanrot Spear','Halo Scythe',"Envoy's Horn","Envoy's Greathorn",'Greatbow','Partisan',"Knight's Greatsword",'Rotten Crystal Staff','Hand of Malenia'],
  'Crumbling Farum Azula':["Beastman's Curved Sword","Beastman's Cleaver","Banished Knight's Greatsword","Banished Knight's Halberd"],
  'Scadu Altus + Shadow Keep · DLC':['Carian Thrusting Shield',"Messmer Soldier's Spear"]
};
for(const [regionName,names] of Object.entries(TC_REGIONAL_WEAPON_RESTORES)){
  const pool=regions?.[regionName]?.weapons;
  if(!Array.isArray(pool))continue;
  for(const name of names){
    if(pool.some(w=>tcWeaponNameKey(w?.name)===tcWeaponNameKey(name)))continue;
    pool.push(typeof sheetWeapon==='function'?sheetWeapon(name):W(name,'Regional weapon','Smithing path varies','Native skill',false));
  }
}

const TC_RESTORED_INFUSABLE_WEAPONS=new Set([
  'Bastard Sword','Sacrificial Axe',"Guardian's Swordspear","Rogier's Rapier",
  "Cleanrot Knight's Sword",'Spiked Caestus','Raptor Talons','Antspur Rapier',
  'Battle Hammer',"Troll's Golden Sword",'Hammer',"Gargoyle's Halberd",
  'Rotten Battle Hammer','Flowing Curved Sword','Curved Club','Curved Great Club',
  'Partisan',"Knight's Greatsword"
].map(tcWeaponNameKey));
for(const region of Object.values(regions)){
  for(const weapon of (region?.weapons||[])){
    if(TC_RESTORED_INFUSABLE_WEAPONS.has(tcWeaponNameKey(weapon?.name)))weapon.infusable=true;
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
function tcAppealCooldownWeapons(state){
  return new Set(Array.isArray(state?.appealWeaponCooldown)?state.appealWeaponCooldown:[]);
}
function tcExcludeAppealCooldown(state,pool){
  const cooldown=tcAppealCooldownWeapons(state);
  if(!cooldown.size)return pool;
  const filtered=pool.filter(w=>!cooldown.has(w.name));
  return filtered.length?filtered:pool;
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
  const currentPool=tcExcludeAppealCooldown(state,tcLegalRegionWeapons(state,state.region,target)),used=usedWeaponNames(state),unusedCurrent=currentPool.filter(w=>!used.has(w.name));
  let pair=null;
  if(unusedCurrent.length>=2)pair=tcBestDiversePairFromPool(state,unusedCurrent,unusedCurrent);
  else if(unusedCurrent.length===1){
    const fallback=tcExcludeAppealCooldown(state,tcLegalAccumulatedWeaponPool(state,target)).filter(w=>w.name!==unusedCurrent[0].name&&!used.has(w.name));
    const broad=fallback.length?fallback:tcExcludeAppealCooldown(state,tcLegalAccumulatedWeaponPool(state,target)).filter(w=>w.name!==unusedCurrent[0].name);
    if(broad.length)pair=Math.random()<0.5?tcBestDiversePairFromPool(state,unusedCurrent,broad):tcBestDiversePairFromPool(state,broad,unusedCurrent);
  }
  if(!pair){
    const all=tcExcludeAppealCooldown(state,tcLegalAccumulatedWeaponPool(state,target)),unused=all.filter(w=>!used.has(w.name));
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
  for(const name of tcAppealCooldownWeapons(state))avoided.add(name);
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

const tcCompleteEncounterBeforeAppealCooldown=completeEncounter;
completeEncounter=function(state,actor){
  const prepared=structuredClone(state);
  prepared.appealWeaponCooldown=[...tcAppealSeenWeapons(state)];
  return tcCompleteEncounterBeforeAppealCooldown(prepared,actor);
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