from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

s=re.sub(r"\n?/\* --- Weapon accessibility and Appeal deck memory --- \*/.*?/\* --- End weapon accessibility and Appeal deck memory --- \*/\n?","\n",s,flags=re.S)

js=r'''
/* --- Weapon accessibility and Appeal deck memory --- */
// Weapons whose normal acquisition route requires defeating a boss remain out
// of the Covenant armory until that concrete boss kill is recorded. The gate
// model is intentionally data-driven so later regions can add acquisition rules
// without rewriting the draw engine.
const TC_WEAPON_ACQUISITION_GATES={
  "Gargoyle's Blackblade":[{name:'Black Blade Kindred',region:'Caelid'}],
  "Gargoyle's Black Halberd":[{name:'Black Blade Kindred',region:'Caelid'}],
  "Godslayer's Greatsword":[{name:'Godskin Apostle',region:'Caelid'}],
  "Lusat's Glintstone Staff":[{name:'Nox Swordstress & Nox Monk',region:'Caelid'}],
  "Moonveil":[{name:'Magma Wyrm',region:'Caelid'}],
  "Nox Flowing Sword":[{name:'Nox Swordstress & Nox Monk',region:'Caelid'}],
  "Regalia of Eochaid":[{name:'Frenzied Duelist',region:'Caelid'}],
  "Ruins Greatsword":[{name:'Crucible Knight and Misbegotten Warrior',region:'Caelid'}]
};

// Greatsword is ordinary carriage loot in Caelid and was present in the app's
// original regional data before the spreadsheet pool accidentally displaced it.
(function tcRestoreCaelidGreatsword(){
  const pool=regions?.['Caelid']?.weapons;
  if(!Array.isArray(pool)||pool.some(w=>w?.name==='Greatsword'))return;
  const restored=typeof sheetWeapon==='function'?sheetWeapon('Greatsword'):W('Greatsword','Colossal Sword','Smithing Stones','Stamp (Upward Cut)');
  pool.push(restored);
})();

function tcWeaponBossKey(name){
  if(typeof tcBossKey==='function')return tcBossKey(name);
  return String(name||'').toLowerCase().replace(/[’]/g,"'").replace(/[^a-z0-9]+/g,' ').trim();
}
function tcRecordedBossDefeated(state,requirement){
  const wanted=tcWeaponBossKey(requirement?.name),region=requirement?.region||'';
  if(!wanted)return true;
  const matches=entry=>entry&&tcWeaponBossKey(entry.name)===wanted&&(!region||entry.region===region);
  if((state?.history||[]).some(matches))return true;
  if((state?.sanctionedBossKills||[]).some(matches))return true;
  if((state?.appealPenaltyBossKills||[]).some(matches))return true;
  return false;
}
function tcWeaponAcquisitionUnlocked(state,weapon){
  const gates=TC_WEAPON_ACQUISITION_GATES[String(weapon?.name||'')];
  return !gates||gates.every(req=>tcRecordedBossDefeated(state,req));
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
  if(unusedCurrent.length>=2)pair=bestPairFromPool(state,unusedCurrent,unusedCurrent);
  else if(unusedCurrent.length===1){
    const fallback=tcLegalAccumulatedWeaponPool(state,target).filter(w=>w.name!==unusedCurrent[0].name&&!used.has(w.name));
    const broad=fallback.length?fallback:tcLegalAccumulatedWeaponPool(state,target).filter(w=>w.name!==unusedCurrent[0].name);
    if(broad.length)pair=Math.random()<0.5?bestPairFromPool(state,unusedCurrent,broad):bestPairFromPool(state,broad,unusedCurrent);
  }
  if(!pair){
    const all=tcLegalAccumulatedWeaponPool(state,target),unused=all.filter(w=>!used.has(w.name));
    const pool=unused.length>=2?unused:all;
    if(pool.length>=2)pair=bestPairFromPool(state,pool,pool);
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
