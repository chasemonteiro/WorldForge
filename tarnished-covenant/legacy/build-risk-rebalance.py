from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Expand the existing pools without replacing the battle-tested originals.
extra_js = r'''
const TC_EXTRA_RITES = [
 ['Funeral Custom','Use a Grace Mimic, place a Rainbow Stone beside it, perform Dejection, then walk away without resting.','Grand',2],
 ['The Three Gifts','Before victory, use a Glowstone, a Warming Stone, and any Prattling Pate in that order.','Grand',2],
 ['Unlicensed Alchemy','During the encounter, use three differently named temporary-buff consumables as a team. Flask buffs do not count.','Grand',2],
 ['The Turtle Knows','Bring a Pickled Turtle Neck. Both players bow to the carrier, then the carrier eats it immediately before entering.','Grand',2],
 ['Pottery Degree','Land three different pot types on the boss before victory.','Grand',2],
 ['Full Performance Review','Before victory, the team must land a throwing-knife hit, jump attack, charged heavy, weapon skill, and thrown pot.','Grand',2],
 ['The Procession','Both players walk, not sprint, from the nearest safe approach to the arena entrance, then gesture before entering.','Grand',2],
 ['False Pilgrimage','Use a Grace Mimic somewhere inconvenient, mark it with two Rainbow Stones, and perform a gesture before continuing.','Grand',2],
 ['Perfumer’s Union','Use two different Aromatics during the fight. They must be differently named items.','Grand',2],
 ['Stonehenge, Unfortunately','Place five Rainbow Stones in the arena or immediately outside it before victory.','Grand',2],
 ['The Four Offices','As a team, land a light attack, charged heavy, jump attack, and weapon skill before anyone uses a second Crimson Flask.','Grand',2],
 ['Union Dinner','Each player consumes a different food item immediately before the encounter, then neither may heal for the first 15 seconds.','Grand',2],
 ['Warming Stone Hostage Negotiation','Place a Warming Stone during combat. Both players must touch its effect before either may heal again.','Grand',2],
 ['Inventory Archaeology','Use three different consumables you have not used yet during this run. Honor system.','Grand',2],
 ['The Long Introduction','Before attacking, both players gesture, use one consumable each, and circle the arena entrance once.','Grand',2],
 ['Elemental Filing Cabinet','As a team, deal three different damage types through consumables, grease, weapon skills, or attacks before victory.','Grand',2],
 ['The Archaeologist','Carry at least five Ruin Fragments into the encounter, place one Rainbow Stone, and use the Telescope before engaging.','Grand',2],
 ['Ceremonial Bankruptcy','Use one annoying-to-replace consumable you have been hoarding. You decide what counts, but it must hurt emotionally.','Grand',2],
 ['The Union Has Standards','Use Soap, a food consumable, a crafted offensive item, and a gesture between leaving Grace and defeating the boss.','Grand',2],
 ['The Liturgical Combo','In order: gesture, thrown-item hit, charged heavy, weapon skill. Any player may perform each step, but do not break the order.','Grand',2],
 ['Against Better Judgment','No Crimson Flask until both players land a charged heavy. Then use a Warming Stone before anyone takes their second flask.','Grand',2],
 ['The Full Audit','Before victory, each player uses a non-flask consumable, lands a jump attack, and lands a weapon skill. Also place a Rainbow Stone.','Grand',2],
 ['Potluck','Each player must land a different type of thrown pot before victory.','True',1],
 ['Three Point Inspection','Before victory, land one thrown knife, one pot, and one weapon skill as a team.','True',1],
 ['Stone Witness','Place a Rainbow Stone at the entrance and another inside the arena before victory.','True',1],
 ['Emergency Illumination','Use a Glowstone after the boss reaches half health.','True',1],
 ['False Grace','Use a Grace Mimic immediately before the encounter. Respect its complete uselessness.','True',1],
 ['Sacramental Snack','Each player consumes a different non-flask consumable before the first attack.','True',1],
 ['Weapon Skill Witness','Both players land their assigned weapon skill at least once before victory.','True',1],
 ['Heavy Machinery','Both players land one charged heavy before either uses their third Crimson Flask.','True',1],
 ['Jump Department','Both players land a jump attack before the boss reaches half health.','True',1],
 ['No Free Crits','On the first stance break, deliberately skip the critical attack and bow or crouch instead.','True',1],
 ['Formal Introductions','Both players gesture to the boss before either attacks. Different gestures required.','True',1],
 ['Ceremonial Stonework','Place three Rainbow Stones in a rough triangle before or during the encounter.','True',1],
 ['The Bell Does Not Toll','Use any Prattling Pate twice during the fight at two different health phases.','True',1],
 ['Tiny OSHA','Drop one Rainbow Stone and turn on both Lanterns before the pull.','Minor',0],
 ['Management Photo','Both players stand beside a Rainbow Stone and gesture before engaging.','Minor',0],
 ['Mandatory Orientation','Both players crouch for five seconds at the arena entrance.','Minor',0],
 ['Tourist Behavior','Use the Telescope and place a Rainbow Stone before engaging.','Minor',0],
 ['Clean Workplace','Use Soap and a gesture before the encounter.','Minor',0]
];
const TC_RITE_META = new Map(TC_EXTRA_RITES.map(r=>[r[0],{tier:r[2],favor:r[3]}]));
weirdness.push(...TC_EXTRA_RITES.map(r=>[r[0],r[1]]));
function riteMeta(weird){ return TC_RITE_META.get(weird?.[0]) || {tier:'True',favor:1}; }

const TC_EXTRA_CHAOS = [
 'SUCCESSION CRISIS: every time aggro changes, the new target must stop attacking for five seconds until victory.',
 'FALSE CONFIDENCE: once the boss falls below 25% health, nobody may use Crimson Flasks.',
 'DEBT COLLECTOR: if either player dies, the survivor cannot heal for the remainder of that attempt.',
 'SCARLET ACCOUNTING: after each Crimson Flask, that player must land a hit before healing again.',
 'THE COVENANT WANTS A SHOW: before victory, both players must land a charged heavy and a weapon skill.',
 'DIVORCE PROCEEDINGS: both players must remain separated for the rest of this attempt.',
 'HOSTILE WORK ENVIRONMENT: randomly choose one player. Remove all talismans until victory.',
 'LAST CALL: each player receives exactly two more Crimson Flask uses for the rest of the attempt.',
 'SILENT PARTNER: randomly choose one player. They may only attack while the other player has aggro for 30 seconds.',
 'NO SAFE OPENINGS: after every heal, that player must land a hit before healing again.',
 'MELEE ARBITRATION: nobody may deal ranged damage for the next 30 seconds.',
 'ASH OF WAR STRIKE: weapon skills are banned until somebody lands a charged heavy.',
 'ROLLING BLACKOUT: randomly choose one player. They may not roll for 15 seconds.',
 'STAMINA UNION: neither player may attack while their stamina is below half for 30 seconds.',
 'FASHION COURT: both players remove one armor piece of their choice until victory.',
 'BODYGUARD CLAUSE: the player with more health must stay closer to the boss for 20 seconds.',
 'POTION PROHIBITION: nobody may heal for 20 seconds.',
 'AGGRESSION QUOTA: each player must land three hits before their next Crimson Flask.',
 'COMPULSORY RETREAT: after each player lands one hit, both must fully disengage once before continuing.',
 'THE LONG WAY HOME: if you wipe this attempt, the current Chaos restriction remains binding for the next attempt too.',
 'NO MORE MISTAKES: the next player who takes damage loses Crimson Flask access for 30 seconds.',
 'EXECUTIVE DECISION: randomly choose one player. Only that player may use weapon skills until the attempt ends.',
 'BLOOD PRICE: the next Crimson Flask used requires that player to remove one talisman until victory.',
 'COMBO INSPECTION: nobody may hit the boss more than twice consecutively until victory.',
 'PANIC TAX: after three consecutive panic rolls, that player must stop attacking for five seconds.',
 'DEPARTMENT OF HEAVY OBJECTS: both players must land a jumping heavy before either may heal again.',
 'UNPAID INTERNSHIP: randomly choose one player. They deal no damage for 20 seconds and may only survive.',
 'MEDICAL LEAVE DENIED: the player with lower health is the only player allowed to heal until health totals reverse.',
 'SHARED LIABILITY: if either player heals, the other player cannot heal for 15 seconds.',
 'FOG OF WAR: no lock-on and no weapon skills for 30 seconds.',
 'AUDIT FROM HELL: before victory, each player must land a light attack, heavy attack, jump attack, and weapon skill.',
 'THE GREATER WILL HAS CUT FUNDING: each player gets one more Crimson Flask use. Total. Good luck.',
 'SURVIVOR BENEFITS CANCELLED: if one player dies, the survivor removes one talisman and cannot use weapon skills.',
 'BOARD MEETING: both players stop attacking for ten seconds. If anyone gets hit, restart the ten seconds.',
 'THE COVENANT IS DISPLEASED: both players remove one talisman, no weapon skills, and no lock-on for 20 seconds.',
 'MALICIOUS COMPLIANCE: both players two-hand their assigned weapon and cannot heal for 15 seconds.',
 'ABSOLUTE SHAMBLES: randomly choose one player to remove all talismans; the other loses weapon skills until wipe or victory.',
 'MUTUAL ASSURED DESTRUCTION: while both players are below half health, nobody may heal until one player lands a charged heavy.',
 'ONE BUTTON DEPARTMENT: for 30 seconds both players may use only light attacks or only heavy attacks. Choose randomly.',
 'NO COMFORT ZONE: both players must swap which side of the boss they are fighting from before attacking again.'
].map(text=>({text,favor:1}));
const TC_MERCIFUL_CHAOS = new Set([
 'ABSOLUTELY NOTHING: Chaos has reviewed the situation and decided you are already suffering enough.',
 'FREE DRINK: both players may immediately use one Crimson Flask without it counting against any existing Chaos flask restriction.',
 'MORALE BOOST: no new restriction. Both players must say something encouraging and deeply unconvincing before continuing.',
 'BOSS UNION BREAK: stop attacking for five seconds. Healing and repositioning are allowed. The boss has requested a meeting.'
]);
'''

marker='function triggerChaos(state, actor) {'
if marker not in s: raise SystemExit('triggerChaos marker missing')
s=s.replace(marker,extra_js+'\n'+marker,1)

# Add expanded outcomes and record whether this Chaos actually earns Favor.
old='  next.current.chaosConsequence = pick(consequences);'
new="  const rolledChaos = pick(consequences.concat(TC_EXTRA_CHAOS.map(x=>x.text)));\n  next.current.chaosConsequence = rolledChaos;\n  next.current.chaosFavor = TC_MERCIFUL_CHAOS.has(rolledChaos) ? 0 : 1;"
if old not in s: raise SystemExit('chaos pick target missing')
s=s.replace(old,new,1)

# New rites retain difficulty and reward metadata.
s=s.replace("weirdness: { name: weird[0], text: weird[1] }", "weirdness: { name: weird[0], text: weird[1], ...riteMeta(weird) }")
s=s.replace("next.current.weirdness = { name: weird[0], text: weird[1] };", "next.current.weirdness = { name: weird[0], text: weird[1], ...riteMeta(weird) };")

# Smithing contracts become increasingly painful: 6 / 8 / 10 / 12.
contract_helper=r'''function smithingContractCost(bearing){
  const tier=Math.max(1,Math.min(4,Number(String(bearing?.id||'').match(/(\d+)$/)?.[1]||1)));
  return 4 + tier*2;
}
'''
marker='function smithingHubMarkup(state){'
if marker not in s: raise SystemExit('smithing hub marker missing')
s=s.replace(marker,contract_helper+'\n'+marker,1)
s=s.replace('if(sm.favor>=3 && available.length){','if(available.length && sm.favor>=Math.min(...available.map(smithingContractCost))){',1)
s=s.replace('Spend 3 Favor to commission a Bell Bearing Contract.','Eligible contracts cost 6–12 Favor depending on Bell Bearing tier.',1)
s=s.replace("${sm.favor<3?'3 Favor commissions a Bell Bearing Contract.':'No accessible contract is waiting yet.'}", "${available.length?`Next eligible contract: ${Math.min(...available.map(smithingContractCost))} Favor.`:'No accessible contract is waiting yet.'}",1)

pattern=r"function commissionSmithingContract\(state\)\{.*?\n\}"
replacement=r'''function commissionSmithingContract(state){
  const sm=smithingData(state),pool=availableBellBearings(state);
  const affordable=pool.filter(b=>sm.favor>=smithingContractCost(b));
  if(!affordable.length)return null;
  const next=smithingCopy(state),b=pick(affordable),cost=smithingContractCost(b),task=pick(TC_SMITHING_TASKS);
  next.smithing.favor-=cost;
  next.smithing.activeContract={bearingId:b.id,task,status:'task',cost,commissionedAt:new Date().toISOString()};
  next.lastAction=`A Bell Bearing Contract has been commissioned for ${b.name} for ${cost} Favor.`;
  return next;
}'''
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('commission function target missing')

pattern=r"function claimForgeFavor\(state,type\)\{.*?\n\}"
replacement=r'''function claimForgeFavor(state,type){
  if(!state.current)return null;
  const next=smithingCopy(state),c=next.current;
  if(type==='rite'){
    if(c.smithingRiteFavor)return null;
    const reward=Number(c.weirdness?.favor??1);
    if(reward<=0){setToast('Minor Rite completed. The Covenant is amused, but no Favor was earned.');return null;}
    c.smithingRiteFavor=true;next.smithing.favor+=reward;next.lastAction=`${c.weirdness?.tier||'True'} Rite honored. +${reward} Smithing Favor.`;
  } else {
    if(!c.chaosTriggered||c.smithingChaosFavor)return null;
    const reward=Number(c.chaosFavor??1);
    if(reward<=0){setToast('Chaos was merciful. No Smithing Favor was earned.');return null;}
    c.smithingChaosFavor=true;next.smithing.favor+=reward;next.lastAction=`Chaos endured. +${reward} Smithing Favor.`;
  }
  return next;
}'''
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('favor function target missing')

# Make the stakes visible before players decide whether the Rite is worth doing.
s=s.replace('<div class="tc-kicker violet">odd rite</div><div class="tc-feature-title">${h(c.weirdness.name)}</div>', '<div class="tc-kicker violet">${h(c.weirdness?.tier||\'True\')} rite · ${Number(c.weirdness?.favor??1)>0?`+${Number(c.weirdness?.favor??1)} Favor`:\'no Favor\'}</div><div class="tc-feature-title">${h(c.weirdness.name)}</div>',1)
s=s.replace("${c.smithingRiteFavor?'✓ Rite Favor Claimed':'Odd Rite Honored · +1'}", "${c.smithingRiteFavor?'✓ Rite Favor Claimed':Number(c.weirdness?.favor??1)>0?`Rite Honored · +${Number(c.weirdness?.favor??1)}`:'Minor Rite · No Favor'}",1)
s=s.replace("${c.smithingChaosFavor?'✓ Chaos Favor Claimed':'Chaos Endured · +1'}", "${c.smithingChaosFavor?'✓ Chaos Favor Claimed':Number(c.chaosFavor??1)>0?'Chaos Endured · +1':'Merciful Chaos · No Favor'}",1)

# Regression invariants.
for needle in ['TC_EXTRA_RITES','TC_EXTRA_CHAOS','smithingContractCost','chaosFavor','Grand Rite honored']:
    if needle not in s: raise SystemExit('risk rebalance invariant missing: '+needle)

p.write_text(s)
