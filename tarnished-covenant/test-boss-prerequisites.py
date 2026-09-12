from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or f'missing boss prerequisite invariant: {needle}')

def forbid(needle,msg=None):
    if needle in html: raise SystemExit(msg or f'forbidden boss prerequisite behavior: {needle}')

# Core prerequisite resolver and canonical history-only boss completion.
for needle in [
    'function tcBossKey(name)',
    'function tcHistoryBossKeys(state)',
    'function tcBossActuallyDefeated(state,name)',
    'function tcNextUnmetPrerequisite(state,targetName,seen=new Set())',
    'const TC_BOSS_PREREQUISITES=',
    'const tcChooseTargetBeforeBossPrereqs=chooseTarget;',
    'chooseTarget=function(state){',
    "return {name:tcPoolBossName(state.region,prerequisite),exit:false,prerequisiteFor:proposed.name};",
]: require(needle)

# User-requested main-game chains.
for needle in [
    "'godrick the grafted':'Margit, The Fell Omen'",
    "'rennala queen of the full moon':'Red Wolf of Radagon'",
    "tcRegionEverVisited(state,'Altus Plateau + Leyndell')?null:'Crucible Knight and Misbegotten Warrior'",
    "'godfrey first elden lord':'Draconic Tree Sentinel'",
    "'morgott the omen king':'Godfrey, First Elden Lord'",
    "'maliketh the black blade':'Godskin Duo'",
    "'godfrey first elden lord hoarah loux':'Sir Gideon Ofnir, the All-Knowing'",
]: require(needle)

# Additional physical progression gates found in the audit.
for needle in [
    "'regal ancestor spirit':'Mimic Tear'",
    "'valiant gargoyles':'Mimic Tear'",
    "'lichdragon fortissax':\"Fia's champions\"",
    "'malenia blade of miquella':'Loretta, Knight of the Haligtree'",
    "'dragonlord placidusax':'Godskin Duo'",
    "'jagged peak drake':'Ancient Dragon-Man'",
    "'ancient dragon senessax':'Ancient Dragon-Man'",
    "'bayle the dread':'Ancient Dragon-Man'",
    "'promised consort radahn':'Leda and Allies'",
]: require(needle)

# Rykard retains the Volcano Manor alternative after Mountaintops is reached.
require("tcRegionEverVisited(state,'Mountaintops of the Giants')?null:'Godskin Noble'")

# Cross-region access gates send the run backward instead of spawning a boss in
# the wrong region.
for needle in [
    'const TC_REGION_ACCESS_GATES=',
    "'Deeproot Depths':[",
    "{boss:'Valiant Gargoyle & Valiant Gargoyle (Twinblade)',region:'Siofra River + Nokron'}",
    "{boss:'Mohg, the Omen',region:'Altus Plateau + Leyndell'}",
    "'Miquella’s Haligtree':[",
    "{boss:'Commander Niall',region:'Mountaintops of the Giants'}",
    "'Abyssal Woods · DLC':[",
    "{boss:'Jori, Elder Inquisitor',region:'Scadu Altus + Shadow Keep · DLC'}",
    'function tcOutstandingRouteGateForCurrentRegion(state)',
    'if(routeGate)return {name:routeGate,exit:false,prerequisiteFor:\'region access\'};',
]: require(needle)

# Random pools exclude physically inaccessible downstream bosses until their
# immediate prerequisite has actually been beaten.
require('tcAvailableRegionalBossesBeforePrereqs(state).filter(name=>tcBossRandomAccessible(state,name))')
require('return !direct||tcBossActuallyDefeated(state,direct);')

# Sanctioned Boss Kill cannot remove a required gate, and prerequisite completion
# is based on normal encounter history rather than sanctioned pool exclusions.
for needle in [
    'const TC_PROGRESSION_GATE_BOSSES=[',
    'function tcIsProgressionGateBoss(name)',
    "if(typeof tcIsProgressionGateBoss==='function'&&tcIsProgressionGateBoss(name))continue;",
]: require(needle)
start=html.find('function tcBossActuallyDefeated(state,name)')
end=html.find('function tcRegionEverVisited',start)
if start<0 or end<0: raise SystemExit('history boss completion helper missing')
completion=html[start:end]
forbid('defeatedBossNames(state)', 'Prerequisite completion must not trust sanctioned boss exclusions.') if False else None
if 'defeatedBossNames' in completion or 'sanctionedBossKills' in completion:
    raise SystemExit('Prerequisite completion incorrectly trusts sanctioned boss kills.')

# Tiny reference model for recursive/conditional ordering.
def key(name):
    import re
    k=(name or '').lower().replace('&',' and ')
    k=re.sub(r'[^a-z0-9]+',' ',k).strip()
    if k.startswith('valiant gargoyle') or k=='valiant gargoyles': return 'valiant gargoyles'
    if 'crucible knight' in k and 'misbegotten warrior' in k: return 'crucible misbegotten duo'
    return k

base={
    key('Godrick the Grafted'):'Margit, The Fell Omen',
    key('Rennala, Queen of the Full Moon'):'Red Wolf of Radagon',
    key('Godfrey, First Elden Lord'):'Draconic Tree Sentinel',
    key('Morgott, the Omen King'):'Godfrey, First Elden Lord',
    key('Maliketh, the Black Blade'):'Godskin Duo',
    key('Godfrey, First Elden Lord / Hoarah Loux'):'Sir Gideon Ofnir, the All-Knowing',
}
def direct(target,history=(),visited=()):
    k=key(target)
    if k==key('Starscourge Radahn'):
        return None if 'Altus Plateau + Leyndell' in visited else 'Crucible Knight and Misbegotten Warrior'
    return base.get(k)

def next_req(target,history=(),visited=()):
    defeated={key(x) for x in history}
    seen=set()
    def walk(t):
        k=key(t)
        if k in seen:return None
        seen.add(k)
        p=direct(t,history,visited)
        if not p or key(p) in defeated:return None
        return walk(p) or p
    return walk(target)

assert key(next_req('Godrick the Grafted'))==key('Margit, The Fell Omen')
assert next_req('Godrick the Grafted',['Margit, the Fell Omen']) is None
assert key(next_req('Morgott, the Omen King'))==key('Draconic Tree Sentinel')
assert key(next_req('Morgott, the Omen King',['Draconic Tree Sentinel']))==key('Godfrey, First Elden Lord')
assert next_req('Morgott, the Omen King',['Draconic Tree Sentinel','Godfrey, First Elden Lord']) is None
assert key(next_req('Starscourge Radahn'))==key('Crucible Knight and Misbegotten Warrior')
assert next_req('Starscourge Radahn',visited=['Altus Plateau + Leyndell']) is None
assert key(next_req('Maliketh, the Black Blade'))==key('Godskin Duo')
assert key(next_req('Godfrey, First Elden Lord / Hoarah Loux'))==key('Sir Gideon Ofnir, the All-Knowing')

print('Tarnished Covenant physical boss prerequisite graph: PASS')
