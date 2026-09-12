from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# Physical boss prerequisites / access gates
#
# The Covenant's random encounter system must respect bosses that physically gate
# later bosses/areas. Optional fights remain random, but an inaccessible target is
# never rolled early. When a capstone is selected with an unmet prerequisite, the
# next unmet prerequisite is substituted first. Route-dependent exceptions are
# modeled explicitly (Radahn festival / Rykard Volcano Manor route).
# -----------------------------------------------------------------------------

s=re.sub(
    r"\n?/\* --- Boss prerequisite dependency graph --- \*/.*?"
    r"/\* --- End boss prerequisite dependency graph --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

# Sanctioned Boss Kill is for optional off-assignment loot only. Progression gates
# must still be fought as Covenant encounters and cannot be removed from the pool.
freeboss_old="""      if(region===activeRegion&&name===activeName)continue;
      out.push({region,name});"""
freeboss_new="""      if(region===activeRegion&&name===activeName)continue;
      if(typeof tcIsProgressionGateBoss==='function'&&tcIsProgressionGateBoss(name))continue;
      out.push({region,name});"""
if freeboss_old in s:
    s=s.replace(freeboss_old,freeboss_new,1)
elif "tcIsProgressionGateBoss(name))continue;" not in s:
    raise SystemExit('Sanctioned Boss Kill eligibility target missing')

js=r'''
/* --- Boss prerequisite dependency graph --- */
function tcBossKey(name){
  let key=String(name||'').normalize('NFKD').replace(/[’‘]/g,"'").toLowerCase();
  key=key.replace(/&/g,' and ').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
  // Historical/alternate labels used by earlier Covenant builds.
  if(/^valiant gargoyle/.test(key)||key==='valiant gargoyles')return 'valiant gargoyles';
  if(key.includes('crucible knight')&&key.includes('misbegotten warrior'))return 'crucible misbegotten duo';
  return key;
}
function tcHistoryBossKeys(state){return new Set((state?.history||[]).map(x=>tcBossKey(x?.name)).filter(Boolean));}
function tcBossActuallyDefeated(state,name){return tcHistoryBossKeys(state).has(tcBossKey(name));}
function tcRegionEverVisited(state,region){
  return Boolean(region&&state&&(
    state.region===region ||
    (state.clearedRegions||[]).includes(region) ||
    (state.history||[]).some(x=>x?.region===region)
  ));
}
function tcPoolBossName(regionName,wanted){
  const wantedKey=tcBossKey(wanted);
  const region=regions?.[regionName];
  const names=[...(region?.bosses||[]),region?.exit].filter(Boolean);
  return names.find(name=>tcBossKey(name)===wantedKey)||wanted;
}

// Direct physical ordering. These are deliberately boss-to-boss requirements,
// not generic difficulty ordering. Recursion turns Morgott -> Golden Godfrey ->
// Draconic Tree Sentinel into the correct next encounter automatically.
const TC_BOSS_PREREQUISITES={
  'godrick the grafted':'Margit, The Fell Omen',
  'rennala queen of the full moon':'Red Wolf of Radagon',
  'regal ancestor spirit':'Mimic Tear',
  'valiant gargoyles':'Mimic Tear',
  'godfrey first elden lord':'Draconic Tree Sentinel',
  'mohg the omen':'Draconic Tree Sentinel',
  'esgar priest of blood':'Draconic Tree Sentinel',
  'fell twins':'Morgott, the Omen King',
  'morgott the omen king':'Godfrey, First Elden Lord',
  'lichdragon fortissax':"Fia's champions",
  'malenia blade of miquella':'Loretta, Knight of the Haligtree',
  'dragonlord placidusax':'Godskin Duo',
  'maliketh the black blade':'Godskin Duo',
  'godfrey first elden lord hoarah loux':'Sir Gideon Ofnir, the All-Knowing',
  'jagged peak drake':'Ancient Dragon-Man',
  'ancient dragon senessax':'Ancient Dragon-Man',
  'bayle the dread':'Ancient Dragon-Man',
  'promised consort radahn':'Leda and Allies'
};
function tcDirectBossPrerequisite(state,targetName){
  const key=tcBossKey(targetName);
  // Redmane Castle's duo is only necessary before the festival has been activated
  // by reaching Altus. This is the Covenant's chosen model for the route split.
  if(key==='starscourge radahn'){
    return tcRegionEverVisited(state,'Altus Plateau + Leyndell')?null:'Crucible Knight and Misbegotten Warrior';
  }
  // Rykard can be reached through the Temple of Eiglay after Godskin Noble, or
  // via Tanith after the Mountaintops contract route becomes possible.
  if(key==='rykard lord of blasphemy'){
    return tcRegionEverVisited(state,'Mountaintops of the Giants')?null:'Godskin Noble';
  }
  return TC_BOSS_PREREQUISITES[key]||null;
}
function tcNextUnmetPrerequisite(state,targetName,seen=new Set()){
  const targetKey=tcBossKey(targetName);
  if(seen.has(targetKey))return null;
  seen.add(targetKey);
  const direct=tcDirectBossPrerequisite(state,targetName);
  if(!direct||tcBossActuallyDefeated(state,direct))return null;
  const nested=tcNextUnmetPrerequisite(state,direct,seen);
  return nested||tcPoolBossName(state?.region,direct);
}
function tcBossRandomAccessible(state,name){
  const direct=tcDirectBossPrerequisite(state,name);
  return !direct||tcBossActuallyDefeated(state,direct);
}

// Access gates whose prerequisite boss lives in an earlier/source region. These
// are kept separate from boss prerequisites so the app can send players backward
// to the correct region rather than pretending the boss lives in the destination.
const TC_REGION_ACCESS_GATES={
  'Deeproot Depths':[
    {boss:'Valiant Gargoyle & Valiant Gargoyle (Twinblade)',region:'Siofra River + Nokron'},
    {boss:'Mohg, the Omen',region:'Altus Plateau + Leyndell'}
  ],
  'Miquella’s Haligtree':[
    {boss:'Commander Niall',region:'Mountaintops of the Giants'}
  ],
  'Abyssal Woods · DLC':[
    {boss:'Jori, Elder Inquisitor',region:'Scadu Altus + Shadow Keep · DLC'}
  ]
};
function tcRegionDestinationPreviouslyVisited(state,region){
  return Boolean((state?.clearedRegions||[]).includes(region)||(state?.history||[]).some(x=>x?.region===region));
}
function tcRegionAccessGateSatisfied(state,region){
  const gates=TC_REGION_ACCESS_GATES[region];
  if(!gates?.length)return true;
  // Do not strand an old save already past a newly-added access gate.
  if(tcRegionDestinationPreviouslyVisited(state,region))return true;
  return gates.some(g=>tcBossActuallyDefeated(state,g.boss));
}
function tcMissingRegionGateCandidates(state,region){
  const gates=TC_REGION_ACCESS_GATES[region]||[];
  if(tcRegionAccessGateSatisfied(state,region))return [];
  return gates.filter(g=>!tcBossActuallyDefeated(state,g.boss));
}

const tcAvailableRegionalBossesBeforePrereqs=availableRegionalBosses;
availableRegionalBosses=function(state){
  return tcAvailableRegionalBossesBeforePrereqs(state).filter(name=>tcBossRandomAccessible(state,name));
};

const tcRegionUnlockedBeforeBossPrereqs=regionUnlocked;
regionUnlocked=function(state,regionName){
  return tcRegionUnlockedBeforeBossPrereqs(state,regionName)&&tcRegionAccessGateSatisfied(state,regionName);
};

const tcAvailableNextRegionsBeforeBossPrereqs=availableNextRegions;
availableNextRegions=function(state){
  const out=[...tcAvailableNextRegionsBeforeBossPrereqs(state)];
  for(const [destination] of Object.entries(TC_REGION_ACCESS_GATES)){
    if(!state?.includeDlc&&destination.includes('· DLC'))continue;
    if(tcRegionDestinationPreviouslyVisited(state,destination))continue;
    if(!tcRegionUnlockedBeforeBossPrereqs(state,destination))continue;
    if(tcRegionAccessGateSatisfied(state,destination))continue;
    for(const gate of tcMissingRegionGateCandidates(state,destination)){
      if(!state?.includeDlc&&gate.region.includes('· DLC'))continue;
      if(!out.includes(gate.region))out.push(gate.region);
    }
  }
  return out;
};

function tcOutstandingRouteGateForCurrentRegion(state){
  if(!state?.region)return null;
  for(const [destination] of Object.entries(TC_REGION_ACCESS_GATES)){
    if(!state.includeDlc&&destination.includes('· DLC'))continue;
    if(tcRegionDestinationPreviouslyVisited(state,destination))continue;
    if(!tcRegionUnlockedBeforeBossPrereqs(state,destination))continue;
    if(tcRegionAccessGateSatisfied(state,destination))continue;
    const gate=tcMissingRegionGateCandidates(state,destination).find(g=>g.region===state.region);
    if(!gate)continue;
    const nested=tcNextUnmetPrerequisite(state,gate.boss);
    return tcPoolBossName(state.region,nested||gate.boss);
  }
  return null;
}

const tcChooseTargetBeforeBossPrereqs=chooseTarget;
chooseTarget=function(state){
  // A deliberate return trip for an access gate always resolves that gate first.
  const routeGate=tcOutstandingRouteGateForCurrentRegion(state);
  if(routeGate)return {name:routeGate,exit:false,prerequisiteFor:'region access'};

  const proposed=tcChooseTargetBeforeBossPrereqs(state);
  if(!proposed?.name)return proposed;
  const prerequisite=tcNextUnmetPrerequisite(state,proposed.name);
  if(prerequisite){
    return {name:tcPoolBossName(state.region,prerequisite),exit:false,prerequisiteFor:proposed.name};
  }
  return proposed;
};

const TC_PROGRESSION_GATE_BOSSES=[
  'Margit, The Fell Omen','Red Wolf of Radagon','Crucible Knight and Misbegotten Warrior',
  'Mimic Tear','Valiant Gargoyle & Valiant Gargoyle (Twinblade)','Godskin Noble',
  'Draconic Tree Sentinel','Godfrey, First Elden Lord',"Fia's champions",'Commander Niall',
  'Loretta, Knight of the Haligtree','Godskin Duo','Sir Gideon Ofnir, the All-Knowing',
  'Ancient Dragon-Man','Jori, Elder Inquisitor','Leda and Allies'
];
function tcIsProgressionGateBoss(name){
  const key=tcBossKey(name);
  return TC_PROGRESSION_GATE_BOSSES.some(x=>tcBossKey(x)===key);
}
/* --- End boss prerequisite dependency graph --- */
'''

idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

required=[
    'const TC_BOSS_PREREQUISITES=',
    "'godrick the grafted':'Margit, The Fell Omen'",
    "'rennala queen of the full moon':'Red Wolf of Radagon'",
    "key==='starscourge radahn'",
    "tcRegionEverVisited(state,'Altus Plateau + Leyndell')?null:'Crucible Knight and Misbegotten Warrior'",
    "key==='rykard lord of blasphemy'",
    "'morgott the omen king':'Godfrey, First Elden Lord'",
    "'godfrey first elden lord':'Draconic Tree Sentinel'",
    "'maliketh the black blade':'Godskin Duo'",
    "'godfrey first elden lord hoarah loux':'Sir Gideon Ofnir, the All-Knowing'",
    "'malenia blade of miquella':'Loretta, Knight of the Haligtree'",
    "'lichdragon fortissax':\"Fia's champions\"",
    "'bayle the dread':'Ancient Dragon-Man'",
    "'promised consort radahn':'Leda and Allies'",
    "'Miquella’s Haligtree':[",
    "{boss:'Commander Niall',region:'Mountaintops of the Giants'}",
    "'Abyssal Woods · DLC':[",
    "{boss:'Jori, Elder Inquisitor',region:'Scadu Altus + Shadow Keep · DLC'}",
    'function tcNextUnmetPrerequisite(state,targetName,seen=new Set())',
    'function tcOutstandingRouteGateForCurrentRegion(state)',
    'function tcIsProgressionGateBoss(name)',
    "tcIsProgressionGateBoss(name))continue;",
]
for needle in required:
    if needle not in s: raise SystemExit('boss prerequisite invariant missing: '+needle)

p.write_text(s)
print('Boss prerequisite dependency graph applied with conditional routes and backward access gates.')
