from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# Required boss / story-gate sequences
#
# The regional encounter generator is still random for optional bosses, but an
# unavoidable progression boss in the CURRENT region always takes priority until
# it has been recorded in encounter history. This prevents the Covenant from
# rolling a capstone (or later dungeon boss) before the game can legitimately
# reach it.
#
# Only genuinely required gates are included, plus the user's explicit house rule
# that Draconic Tree Sentinel gates the Leyndell pool. Route-skippable bosses such
# as Rellana, Golden Hippopotamus, Godskin Noble (Volcano Manor), Senessax, etc.
# are deliberately NOT hard-coded as prerequisites.
# -----------------------------------------------------------------------------

# Remove a previous generated helper layer if this final patch is rerun.
s=re.sub(
    r"\n?/\* --- Required boss sequence layer --- \*/.*?"
    r"/\* --- End required boss sequence layer --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

# Remove a prior forced-target hook before reinserting it once.
s=s.replace(
    "  const requiredBoss=tcNextRequiredBoss(state);\n  if(requiredBoss)return {name:requiredBoss,exit:false,required:true};\n",
    "",
)

helpers=r'''
/* --- Required boss sequence layer --- */
const TC_REQUIRED_BOSS_SEQUENCES={
  'Limgrave + Stormveil':['Margit, The Fell Omen'],
  'Liurnia of the Lakes':['Red Wolf of Radagon'],
  'Siofra River + Nokron':['Mimic Tear'],
  'Deeproot Depths':["Fia's champions"],
  'Altus Plateau + Leyndell':['Draconic Tree Sentinel','Godfrey, First Elden Lord'],
  'Mountaintops of the Giants':['Commander Niall'],
  'Miquella’s Haligtree':['Loretta, Knight of the Haligtree'],
  'Crumbling Farum Azula':['Godskin Duo'],
  'Leyndell, Ashen Capital':['Sir Gideon Ofnir, the All-Knowing'],
  'Dragon’s Pit + Jagged Peak · DLC':['Ancient Dragon-Man'],
  'Abyssal Woods · DLC':['Jori, Elder Inquisitor'],
  'Enir-Ilim · DLC':['Leda and Allies']
};
function tcBossKey(name){
  return String(name||'').toLowerCase().replace(/[’‘]/g,"'").replace(/[^a-z0-9]+/g,' ').trim();
}
function tcHistoryHasBoss(state,name){
  const wanted=tcBossKey(name);
  return (state?.history||[]).some(entry=>tcBossKey(entry?.name)===wanted);
}
function tcRegionEverVisited(state,regionName){
  return Boolean(state&&(
    state.region===regionName ||
    (state.visitedRegions||[]).includes(regionName) ||
    (state.clearedRegions||[]).includes(regionName) ||
    (state.history||[]).some(entry=>entry?.region===regionName)
  ));
}
function tcRequiredBossSequence(state,regionName=state?.region){
  const sequence=[...(TC_REQUIRED_BOSS_SEQUENCES[regionName]||[])];
  // Redmane Castle's Misbegotten Warrior + Crucible Knight duo exists as the
  // gate before Radahn until the Festival is triggered by reaching Altus.
  if(regionName==='Caelid'&&!tcRegionEverVisited(state,'Altus Plateau + Leyndell')){
    sequence.unshift('Crucible Knight and Misbegotten Warrior');
  }
  return sequence;
}
function tcNextRequiredBoss(state){
  if(!state?.region)return null;
  return tcRequiredBossSequence(state,state.region).find(name=>!tcHistoryHasBoss(state,name))||null;
}
function tcIsRequiredBossForRegion(state,regionName,name){
  const key=tcBossKey(name);
  return tcRequiredBossSequence(state,regionName).some(required=>tcBossKey(required)===key);
}

// Jori is the gate INTO the Abyssal Woods/Midra route. The spreadsheet pool had
// him filed under Scadu Altus, so align the runtime pool with actual progression.
if(regions['Scadu Altus + Shadow Keep · DLC']){
  regions['Scadu Altus + Shadow Keep · DLC'].bosses=(regions['Scadu Altus + Shadow Keep · DLC'].bosses||[])
    .filter(name=>tcBossKey(name)!==tcBossKey('Jori, Elder Inquisitor'));
}
if(regions['Abyssal Woods · DLC']){
  regions['Abyssal Woods · DLC'].bosses=Array.from(new Set(['Jori, Elder Inquisitor',...(regions['Abyssal Woods · DLC'].bosses||[])]));
}
/* --- End required boss sequence layer --- */
'''

marker='function chooseTarget(state) {'
if marker not in s:
    raise SystemExit('chooseTarget(state) marker missing')
s=s.replace(marker,helpers+'\n'+marker,1)

# Required gates always win before optional RNG or capstone chance.
needle="function chooseTarget(state) {\n  const region = regions[state.region];\n  if (state.region === 'The Erdtree') return { name: region.exit, exit: true };\n"
replacement=needle+"\n  const requiredBoss=tcNextRequiredBoss(state);\n  if(requiredBoss)return {name:requiredBoss,exit:false,required:true};\n"
if needle not in s:
    raise SystemExit('chooseTarget insertion target missing')
s=s.replace(needle,replacement,1)

# A required gate also mathematically seals the capstone until cleared.
chance_old="function capstoneChanceForState(state) {\n  const requirement = capstoneRequirement(state);"
chance_new="function capstoneChanceForState(state) {\n  if(typeof tcNextRequiredBoss==='function'&&tcNextRequiredBoss(state))return 0;\n  const requirement = capstoneRequirement(state);"
if chance_old in s:
    s=s.replace(chance_old,chance_new,1)
elif chance_new not in s:
    raise SystemExit('capstone chance gate target missing')

# Sanctioned Boss Kill is explicitly for OPTIONAL bosses. It may never consume a
# mandatory story gate and thereby bypass the sequence system.
freeboss_old="      if(region===activeRegion&&name===activeName)continue;\n      out.push({region,name});"
freeboss_new="      if(region===activeRegion&&name===activeName)continue;\n      if(tcIsRequiredBossForRegion(state,region,name))continue;\n      out.push({region,name});"
if freeboss_old in s:
    s=s.replace(freeboss_old,freeboss_new,1)
elif 'if(tcIsRequiredBossForRegion(state,region,name))continue;' not in s:
    raise SystemExit('Sanctioned Boss Kill prerequisite exclusion target missing')

required=[
    'const TC_REQUIRED_BOSS_SEQUENCES=',
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
    "sequence.unshift('Crucible Knight and Misbegotten Warrior')",
    "!tcRegionEverVisited(state,'Altus Plateau + Leyndell')",
    'const requiredBoss=tcNextRequiredBoss(state);',
    'if(requiredBoss)return {name:requiredBoss,exit:false,required:true};',
    "if(typeof tcNextRequiredBoss==='function'&&tcNextRequiredBoss(state))return 0;",
    'if(tcIsRequiredBossForRegion(state,region,name))continue;',
]
for item in required:
    if item not in s:
        raise SystemExit('required-boss invariant missing: '+item)

p.write_text(s)
print('Required boss sequences applied before regional RNG/capstones; optional-boss boon cannot bypass them.')
