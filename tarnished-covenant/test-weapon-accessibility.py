from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or 'missing weapon accessibility invariant: '+needle)

def forbid(needle,msg=None):
    if needle in html: raise SystemExit(msg or 'forbidden weapon accessibility behavior: '+needle)

for needle in [
    'const TC_WEAPON_ACQUISITION_GATES=',
    "\"Gargoyle's Blackblade\":[{name:'Black Blade Kindred',region:'Caelid'}]",
    "\"Gargoyle's Black Halberd\":[{name:'Black Blade Kindred',region:'Caelid'}]",
    "\"Godslayer's Greatsword\":[{name:'Godskin Apostle',region:'Caelid'}]",
    "\"Lusat's Glintstone Staff\":[{name:'Nox Swordstress & Nox Monk',region:'Caelid'}]",
    "\"Moonveil\":[{name:'Magma Wyrm',region:'Caelid'}]",
    "\"Nox Flowing Sword\":[{name:'Nox Swordstress & Nox Monk',region:'Caelid'}]",
    "\"Regalia of Eochaid\":[{name:'Frenzied Duelist',region:'Caelid'}]",
    "\"Ruins Greatsword\":[{name:'Crucible Knight and Misbegotten Warrior',region:'Caelid'}]",
]: require(needle)

# Sanctioned and Appeal-extra-boss kills are real kills for acquisition gates.
for needle in [
    'function tcRecordedBossDefeated(state,requirement)',
    '(state?.history||[]).some(matches)',
    '(state?.sanctionedBossKills||[]).some(matches)',
    '(state?.appealPenaltyBossKills||[]).some(matches)',
    'gates.every(req=>tcRecordedBossDefeated(state,req))',
]: require(needle)

# Greatsword returns to the Caelid deck and all actual draws use legal pools.
for needle in [
    "pool.some(w=>w?.name==='Greatsword')",
    "sheetWeapon('Greatsword')",
    'function tcLegalRegionWeapons(state,regionName,target)',
    '!weaponBlockedByTarget(w,target)&&tcWeaponAcquisitionUnlocked(state,w)',
    'function tcLegalAccumulatedWeaponPool(state,target)',
    'chooseWeaponPair=function(state,target)',
    'const currentPool=tcLegalRegionWeapons(state,state.region,target)',
    'const all=tcLegalAccumulatedWeaponPool(state,target)',
    'makeBuild=function(regionName,target,avoidNames=[],state=null)',
]: require(needle)

# Appeals remember rejected weapons for this encounter and legal fallback reaches
# earlier visited regions instead of reopening a locked boss-drop pool.
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

# The late layer must not deliberately fall back to the old inaccessible makeBuild
# when state exists.
forbid("if(!pool.length) pool = eligibleWeapons(regionName, target);",'legacy inaccessible appeal fallback survived late accessibility layer')

print('Tarnished Covenant weapon accessibility: PASS — Caelid boss drops unlock only after recorded kills, Greatsword is restored, and Appeals do not recycle rejected weapons.')
