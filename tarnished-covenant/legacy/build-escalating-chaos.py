from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Expanded objective triggers adapted for two-player Elden Ring co-op.
triggers = r'''const chaosTriggers = [
  'WHEN THE BOSS REACHES 75% HEALTH',
  'WHEN THE BOSS REACHES 50% HEALTH',
  'WHEN THE BOSS REACHES 25% HEALTH',
  'WHEN EITHER PLAYER USES A WEAPON SKILL / ASH OF WAR',
  'WHEN EITHER PLAYER DRINKS ANY FLASK',
  'WHEN THE TEAM LANDS A CRITICAL ATTACK',
  'WHEN THE BOSS LANDS A CRITICAL / RIPOSTE-LIKE HIT ON A PLAYER',
  'WHEN THE BOSS CHANGES PHASE OR TRANSFORMS',
  'WHEN EITHER PLAYER IS KNOCKED DOWN OR STANCE-BROKEN',
  'WHEN EITHER PLAYER SUCCESSFULLY PARRIES THE BOSS',
  'WHEN EITHER PLAYER ATTEMPTS A PARRY AND GETS HIT DURING IT',
  '30 SECONDS AFTER THE FIRST PLAYER DAMAGES THE BOSS',
  '60 SECONDS AFTER THE FIRST PLAYER DAMAGES THE BOSS',
  'WHEN EITHER PLAYER CASTS A SORCERY OR INCANTATION',
  'WHEN EITHER PLAYER TAKES FALL DAMAGE DURING THE ENCOUNTER',
  'WHEN EITHER PLAYER REACHES ZERO FP',
  'WHEN EITHER PLAYER BLOCKS A BOSS ATTACK',
  'WHEN THE BOSS GRABS EITHER PLAYER',
  'WHEN THE TEAM KILLS AN ADD OR MINION DURING THE BOSS FIGHT',
  'WHEN EITHER PLAYER FALLS BELOW 20% HEALTH',
  'WHEN EITHER PLAYER APPLIES A SELF-BUFF',
  'WHEN EITHER PLAYER TWO-HANDS THEIR ASSIGNED WEAPON',
  'WHEN THE BOSS USES A RANGED OR PROJECTILE ATTACK',
  'WHEN BLEED, FROSTBITE, POISON, ROT, SLEEP, OR MADNESS PROCS ON A PLAYER',
  'WHEN THE TEAM LANDS A BACKSTAB OR RIPOSTE',
  'WHEN EITHER PLAYER SPRINTS INTO MELEE RANGE AND ATTACKS',
  'WHEN EITHER PLAYER LANDS A JUMP ATTACK',
  'WHEN THE FIGHT REACHES THREE MINUTES',
  'WHEN EITHER PLAYER DIES',
  'AFTER THE FIRST FULL TEAM WIPE',
  'WHEN BOTH PLAYERS HAVE TAKEN DAMAGE AT LEAST ONCE',
  'WHEN BOTH PLAYERS ARE BELOW 50% HEALTH AT THE SAME TIME',
  'WHEN THE TEAM CAUSES THE FIRST BOSS STANCE BREAK',
  'WHEN ANY STATUS EFFECT PROCS ON THE BOSS',
  'WHEN BOTH PLAYERS ARE HIT BY THE SAME BOSS ATTACK OR AOE',
  'WHEN A PLAYER REACHES ZERO CRIMSON FLASKS'
];'''
s, n = re.subn(r"const chaosTriggers = \[.*?\];", triggers, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Chaos trigger pool target missing')

# These are all achievable with the Covenant's one-assigned-weapon, no-Spirit-Ash co-op rules.
chaos_js = r'''
const TC_CHAOS_EARLY = [
 'ROLLING BLACKOUT: neither player may roll for 15 seconds.',
 'WALK IT OFF: neither player may sprint for 30 seconds.',
 'FOG OF WAR: no target lock for 30 seconds.',
 'POTION PROHIBITION: nobody may heal for 20 seconds.',
 'NO CONSUMABLES YET: no consumables until the team lands five more hits.',
 'TWO-HAND NOTICE: both players must two-hand their assigned weapon for 30 seconds.',
 'GROUND FLOOR: no jump attacks for 30 seconds.',
 'NO RUNNING START: no running attacks for the rest of this attempt.',
 'MELEE ARBITRATION: no ranged damage for 20 seconds.',
 'MAGIC BLACKOUT: no sorceries or incantations for 30 seconds.',
 'ASH OF WAR STRIKE: no weapon skills for 30 seconds.',
 'HELMET INSPECTION: both players remove their helmets until victory or wipe.',
 'CHEST OPEN: randomly choose one player. They remove chest armor until victory or wipe.',
 'STAND THERE: both players stop moving for five seconds. Dodging, attacking, and healing are forbidden during the five seconds.',
 'INWARD ROLL: each player’s next three dodges must travel toward or across the boss, never directly away.',
 'LEFT DEPARTMENT: both players must dodge left for their next three dodges.',
 'RIGHT DEPARTMENT: both players must dodge right for their next three dodges.',
 'SINGLE INPUTS ONLY: for 15 seconds, each player must release the controls between attacks; no buffered attack strings.',
 'THE LONG WAIT: for 20 seconds, after either player dodges they must wait three seconds before attacking.',
 'NO FREE JUICE: the next Crimson Flask used by each player is their last Crimson Flask for 30 seconds.'
];

const TC_CHAOS_MID = [
 'SUBSTANCE OVER STYLE: no weapon skills for the rest of this attempt.',
 'NO AERIAL BUDGET: no jump attacks or charged heavy attacks for the rest of this attempt.',
 'SILENT BUILD: no sorceries or incantations for the rest of this attempt.',
 'DRY CERULEAN: no Cerulean Flasks for the rest of this attempt.',
 'SHIELD UNION STRIKE: blocking and parrying are forbidden for the rest of this attempt.',
 'TALISMAN TEETOTALER: each player removes one equipped talisman until victory or wipe.',
 'DARING DISROBEMENT: each player removes one armor piece until victory or wipe.',
 'OLD SOULS: no jumping for the rest of this attempt.',
 'NO TARGET LOCK: both players disable target lock until victory or wipe.',
 'STARVING TARNISHED: no healing of any kind for 45 seconds.',
 'FORCED AGGRESSION: each player’s next three damaging hits must be jump attacks.',
 'THE WAVER: both players must one-hand their assigned weapon for 30 seconds.',
 'MALICIOUS COMPLIANCE: both players two-hand their assigned weapon and may not heal for 20 seconds.',
 'FIVE HIT MEDICAL PLAN: each player must land five hits before their next heal.',
 'SHACKLED: for 20 seconds, dodges may only travel sideways or toward the boss.',
 'Feral Instinct: for 20 seconds, after every dodge that player must sprint toward the boss before attacking again.',
 'SPLIT FOCUS: if an add exists, both players must attack an add exclusively for 15 seconds before returning to the boss.',
 'HOLLOW OATH: each player loses access to their assigned weapon skill until victory or wipe.',
 'WEIGHT OF SIN: both players must reach Heavy Load for 30 seconds, if their inventory allows it; otherwise remove all talismans for 30 seconds.',
 'NO SECOND CHANCES: after a failed block or parry, that player may not attack for five seconds. This lasts until victory or wipe.',
 'THE COVENANT WANTS A SHOW: before anyone may heal again, each player must land a charged heavy or jump heavy.',
 'ONE BUTTON DEPARTMENT: for 30 seconds, both players use light attacks only. Weapon skills, charged attacks, and jump attacks are banned.',
 'THE OTHER ONE BUTTON DEPARTMENT: for 30 seconds, both players use heavy attacks only for weapon damage.',
 'DRAWSTRING BUREAU: if grease is used for the rest of this attempt, it must be Drawstring Grease.',
 'HYGIENIC HERO: no grease for the rest of this attempt.'
];

const TC_CHAOS_LATE = [
 'DARK SOULS DEPARTMENT: no jumping, no jump attacks, no Physick, and no weapon skills until victory or wipe.',
 'PRE-2016 COMBAT DESIGN: no jumping and no weapon skills until victory or wipe.',
 'ABSOLUTE SHAMBLES: randomly choose one player to remove all talismans; the other loses weapon skills until victory or wipe.',
 'THE GREATER WILL HAS CUT FUNDING: each player gets exactly one more Crimson Flask use for the rest of this attempt.',
 'FALSE CONFIDENCE: once the boss is below 25% health, nobody may use Crimson Flasks.',
 'DEBT COLLECTOR: if either player dies, the survivor cannot heal for the rest of that attempt.',
 'SURVIVOR BENEFITS CANCELLED: if one player dies, the survivor removes one talisman and cannot use weapon skills until wipe or victory.',
 'PANACEA PLAYTHROUGH: no intentional status buildup may be added beyond the assigned weapons’ native status until victory or wipe.',
 'NO TEARS, NO FEARS: no Physick, and each player voluntarily loses one Crimson Flask use for the rest of the attempt.',
 'THE PALE CURSE: after any status effect procs on either player, that player may not heal until they land three hits.',
 'THE HOLLOW BARGAIN: each player removes one talisman slot; in exchange, each may ignore exactly one later 30-second healing restriction this attempt.',
 'ONE LIFE: if the team wipes once more, both assigned weapons are condemned and must be rerolled before the next serious attempt.',
 'THE WHEEL: if either player has already died twice with their current assigned weapon, their next death condemns that weapon for the next encounter.',
 'BOARD MEETING: both players stop attacking for ten seconds. If either player deals damage, restart the ten-second count.',
 'AUDIT FROM HELL: before victory, each player must land a light attack, heavy attack, jump attack, and weapon skill.',
 'MUTUAL ASSURED DESTRUCTION: while both players are below half health, nobody may heal until one player lands a charged heavy.',
 'NO COMFORT ZONE: both players must cross to the opposite side of the boss before either may attack again.',
 'FULL DARK SOULS: no jumping, no target lock, and no weapon skills until victory or wipe.',
 'FLOOR IS FINE: if either player jumps, neither player may deal damage for five seconds. This lasts until victory or wipe.',
 'FINAL VOW: if the boss reaches 10% health, add OLD SOULS, no weapon skills, and no Crimson Flask use until victory or wipe.',
 'TARNISHED NO MORE: the killing blow must be a light or heavy attack from one of the two currently assigned weapons. Skills, spells, throwables, and status ticks do not count; otherwise the victory is not recorded.',
 'ASHEN SILENCE: no weapon skills, sorceries, incantations, or Physick until victory or wipe.',
 'HOSTILE WORK ENVIRONMENT: each player removes one talisman and loses sprinting for 30 seconds; weapon skills remain banned until victory or wipe.',
 'THE COVENANT IS DISPLEASED: both players remove one talisman, disable target lock, and lose weapon skills for 30 seconds.',
 'NO SECOND PHASE BENEFITS: from the next phase change onward, no Crimson Flasks until one player lands a critical attack or the attempt ends.'
];

function tcChaosProgress(state){
  const kills = Array.isArray(state?.history) ? state.history.length : Number(state?.cleared || 0);
  const target = state?.includeDlc ? 42 : 30;
  return Math.max(0, Math.min(1, kills / target));
}

function tcPickEscalatingChaos(state){
  const progress = tcChaosProgress(state);
  const severityBias = state?.severity === 'cursed' ? 0.18 : state?.severity === 'hard' ? 0.09 : 0;
  const heat = Math.max(0, Math.min(1, progress + severityBias));
  // Early: mostly tier 1. Mid: tier 2 dominates. Late: tier 3 becomes the plurality.
  const lateChance = 0.05 + heat * 0.55;
  const midChance = 0.25 + heat * 0.20;
  const roll = Math.random();
  if (roll < lateChance) return pick(TC_CHAOS_LATE);
  if (roll < lateChance + midChance) return pick(TC_CHAOS_MID);
  return pick(TC_CHAOS_EARLY);
}
'''

marker = 'function triggerChaos(state, actor) {'
if marker not in s:
    raise SystemExit('triggerChaos marker missing')
s = s.replace(marker, chaos_js + '\n' + marker, 1)

# Replace whatever prior patches used to choose the Chaos consequence.
patterns = [
    r"const rolledChaos = pick\(consequences\.concat\(TC_EXTRA_CHAOS\.map\(x=>x\.text\)\)\);",
    r"next\.current\.chaosConsequence = pick\(consequences\);"
]
replaced = False
for pat in patterns:
    s2, count = re.subn(pat, "const rolledChaos = tcPickEscalatingChaos(next);", s, count=1)
    if count:
        s = s2
        replaced = True
        break
if not replaced:
    raise SystemExit('Chaos consequence selection target missing')

# Ensure the consequence assignment exists after the new roll line.
if 'next.current.chaosConsequence = rolledChaos;' not in s:
    s = s.replace('const rolledChaos = tcPickEscalatingChaos(next);', 'const rolledChaos = tcPickEscalatingChaos(next);\n  next.current.chaosConsequence = rolledChaos;', 1)

# All escalating Chaos is harmful and earns the normal +1 Favor when endured.
if 'next.current.chaosFavor' in s:
    s = re.sub(r"next\.current\.chaosFavor = .*?;", "next.current.chaosFavor = 1;", s, count=1)
else:
    s = s.replace('next.current.chaosConsequence = rolledChaos;', 'next.current.chaosConsequence = rolledChaos;\n  next.current.chaosFavor = 1;', 1)

for needle in ['TC_CHAOS_EARLY','TC_CHAOS_MID','TC_CHAOS_LATE','tcPickEscalatingChaos','WHEN THE FIGHT REACHES THREE MINUTES','DARK SOULS DEPARTMENT']:
    if needle not in s:
        raise SystemExit('escalating Chaos invariant missing: ' + needle)

p.write_text(s)
