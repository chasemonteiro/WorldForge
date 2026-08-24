from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

s = s.replace(
    "APP_URL: 'https://qwnwksyiofolldliaqhf.supabase.co/functions/v1/tarnished-covenant'",
    "APP_URL: 'https://chasemonteiro.github.io/WorldForge/tarnished-covenant/'"
)

odd_rites = r'''const weirdness = [
  ['Knife Check','Hit the boss with a Kukri before victory. The hit has to connect.'],
  ['Tiny Knife Check','Hit the boss with a Throwing Dagger before victory.'],
  ['Bone Department','Hit the boss with a Bone Dart before victory.'],
  ['Crystal Mathematics','Hit the boss with a Crystal Dart before victory.'],
  ['Fire Pot Compliance','Land a Fire Pot on the boss before it dies.'],
  ['Holy Water Audit','Land a Holy Water Pot on the boss before victory.'],
  ['Oil First, Questions Later','Hit the boss with an Oil Pot at least once before victory.'],
  ['Poison Paperwork','Hit the boss with a Poisonbone Dart before victory. Poison does not have to proc.'],
  ['Volcano Pot Incident','Land a Volcano Pot on the boss before victory.'],
  ['Lightning In A Jar','Land a Lightning Pot on the boss before victory.'],
  ['Arena Survey Marker','Place one Rainbow Stone somewhere inside or immediately beside the boss arena before victory.'],
  ['Glowstone OSHA','Drop a Glowstone in the arena before the boss dies.'],
  ['Union-Mandated Break','Place a Warming Stone during the fight. At least one player must stand in its effect briefly.'],
  ['Stealth Technology','Use Mimic’s Veil before approaching the boss arena. Remain disguised for at least five seconds.'],
  ['Lantern Protocol','Both players must turn on a Lantern before the first attack and leave it on for the fight.'],
  ['Professional Cartography','Use the Telescope to inspect the boss or arena before pulling aggro.'],
  ['Personal Hygiene','Use Soap immediately before entering the boss fight.'],
  ['Hello, Management','Use Prattling Pate “Hello” before either player attacks.'],
  ['Thank You For Your Service','Use Prattling Pate “Thank You” after the boss reaches roughly half health.'],
  ['Formal Apology','Use Prattling Pate “Apologies” after the first player takes damage.'],
  ['Wonderful Assessment','Use Prattling Pate “Wonderful” after the first stance break or major punish.'],
  ['You’re Beautiful','Use Prattling Pate “You’re Beautiful” while facing the boss before the first attack.'],
  ['Performance Enhancement','One player must use Uplifting Aromatic during the fight.'],
  ['Perfume Violence','One player must use Spark Aromatic during the fight.'],
  ['Become A Fridge','One player must use Ironjar Aromatic and survive at least ten seconds in combat afterward.'],
  ['Crab Before Combat','One player must eat Boiled Crab immediately before the fight.'],
  ['Turtle Neck Technology','One player must use a Pickled Turtle Neck immediately before the fight.'],
  ['Exalted Flesh Situation','One player must use Exalted Flesh immediately before the fight.'],
  ['Starlight Budget','One player must use a Starlight Shard during the fight.'],
  ['Free Hug Debuff','One player must use Baldachin’s Blessing before the first attack.'],
  ['Pumpkin Assignment','One randomly chosen player must wear Pumpkin Helm for the entire fight.'],
  ['Cat Head Clause','One randomly chosen player must wear Imp Head (Cat) for the entire fight.'],
  ['Octopus Formalwear','One randomly chosen player must wear Octopus Head for the entire fight.'],
  ['Albinauric Representation','One randomly chosen player must wear Albinauric Mask for the entire fight.'],
  ['Mushroom Management','One randomly chosen player must wear Mushroom Crown for the entire fight.'],
  ['Bubble Executive','One randomly chosen player must wear Envoy Crown for the entire fight.'],
  ['Jar Employee Of The Month','One randomly chosen player must wear Jar for the entire fight.'],
  ['Business Casual','One randomly chosen player must wear Commoner’s Headband for the entire fight.'],
  ['Silver Tear Internship','One randomly chosen player must wear Silver Tear Mask for the entire fight.'],
  ['Bad Hat Day','One randomly chosen player must wear Black Dumpling for the entire fight.'],
  ['Polite Opening','Both players must perform Polite Bow before either damages the boss.'],
  ['Standard Opening','Both players must perform Bow before either damages the boss.'],
  ['Point Downward Review','After the first stance break, one player must perform Point Downward before attacking again.'],
  ['Academic Violence','One player must perform Erudition immediately before entering or engaging the boss.'],
  ['Chairman Of The Arena','Before the pull, both players must crouch side by side and stare at the boss for five seconds.'],
  ['Mandatory Lap','Before the first attack, both players must run one unnecessary circle around each other.'],
  ['Aggro Ceremony','The player who gets first aggro must stop and slowly walk for three seconds before attacking.'],
  ['Doorway Committee','Both players must stand in the boss doorway or fog-gate area for five seconds before entering.'],
  ['Post-Stance Meeting','After the first stance break, both players must stop attacking for three seconds and regroup.'],
  ['Victory Was Foretold','Before the pull, one player must point directly at the boss while the other crouches. Hold this tableau for three seconds.']
];'''

s, n = re.subn(r"const weirdness = \[.*?\];\n\nconst affinities =", odd_rites + "\n\nconst affinities =", s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Odd Rites block not found')

old = """function makeBuild(regionName, target, avoidName = '') {
  let pool = eligibleWeapons(regionName, target).filter(w => w.name !== avoidName);
  if (!pool.length) pool = eligibleWeapons(regionName, target);
  const weapon = pick(pool);
  return {
    ...weapon,
    affinity: weapon.infusable ? pick(affinities) : 'Fixed / unique',
    role: pick(roles)
  };
}

function newEncounter(state) {
  const target = chooseTarget(state.region, state.cleared);
  const chase = makeBuild(state.region, target);
  const morgan = makeBuild(state.region, target, chase.name);
  const weird = pick(weirdness);
  return {
    id: crypto.randomUUID(),
    target,
    chase,
    morgan,
    chaosTrigger: pick(chaosTriggers),
    chaosTriggered: false,
    chaosConsequence: '',
    weirdness: { name: weird[0], text: weird[1] },
    flavor: pick(encounterFlavors),
    penances: [],
    createdAt: new Date().toISOString()
  };
}
"""

new = """function buildFromWeapon(weapon) {
  return {
    ...weapon,
    affinity: weapon.infusable ? pick(affinities) : 'Fixed / unique',
    role: pick(roles)
  };
}

function makeBuild(regionName, target, avoidNames = []) {
  const avoided = new Set(Array.isArray(avoidNames) ? avoidNames : [avoidNames]);
  let pool = eligibleWeapons(regionName, target).filter(w => !avoided.has(w.name));
  if (!pool.length) pool = eligibleWeapons(regionName, target);
  return buildFromWeapon(pick(pool));
}

function recentWeaponNames(state, key, limit = 3) {
  return (state.history || [])
    .map(entry => entry?.[key])
    .filter(Boolean)
    .slice(0, limit);
}

function pairKey(a, b) {
  return [a, b].sort().join(' || ');
}

function chooseWeaponPair(state, target) {
  const pool = eligibleWeapons(state.region, target);
  if (pool.length < 2) {
    const first = buildFromWeapon(pool[0]);
    return { chase: first, morgan: buildFromWeapon(pool[0]) };
  }

  const chaseRecent = new Set(recentWeaponNames(state, 'chaseWeapon'));
  const morganRecent = new Set(recentWeaponNames(state, 'morganWeapon'));
  const recentPairs = new Set((state.history || [])
    .map(entry => entry?.weaponPair)
    .filter(Boolean)
    .slice(0, Math.min(8, pool.length * 2)));

  const candidates = [];
  for (const chaseWeapon of pool) {
    for (const morganWeapon of pool) {
      if (chaseWeapon.name === morganWeapon.name) continue;
      const key = pairKey(chaseWeapon.name, morganWeapon.name);
      let score = Math.random();
      if (!chaseRecent.has(chaseWeapon.name)) score += 5;
      if (!morganRecent.has(morganWeapon.name)) score += 5;
      if (!recentPairs.has(key)) score += 8;
      candidates.push({ chaseWeapon, morganWeapon, score });
    }
  }

  candidates.sort((a, b) => b.score - a.score);
  const best = candidates[0];
  return {
    chase: buildFromWeapon(best.chaseWeapon),
    morgan: buildFromWeapon(best.morganWeapon)
  };
}

function newEncounter(state) {
  const target = chooseTarget(state.region, state.cleared);
  const pair = chooseWeaponPair(state, target);
  const chase = pair.chase;
  const morgan = pair.morgan;
  const weird = pick(weirdness);
  return {
    id: crypto.randomUUID(),
    target,
    chase,
    morgan,
    chaosTrigger: pick(chaosTriggers),
    chaosTriggered: false,
    chaosConsequence: '',
    weirdness: { name: weird[0], text: weird[1] },
    flavor: pick(encounterFlavors),
    penances: [],
    createdAt: new Date().toISOString()
  };
}
"""

if old not in s:
    raise SystemExit('weapon assignment block not found')
s = s.replace(old, new)

old_history = """  next.history.unshift({
    name: target.name,
    exit: target.exit,
    completedBy: actor,
    completedAt: new Date().toISOString()
  });
"""
new_history = """  next.history.unshift({
    name: target.name,
    exit: target.exit,
    chaseWeapon: next.current.chase.name,
    morganWeapon: next.current.morgan.name,
    weaponPair: pairKey(next.current.chase.name, next.current.morgan.name),
    completedBy: actor,
    completedAt: new Date().toISOString()
  });
"""
if old_history not in s:
    raise SystemExit('history block not found')
s = s.replace(old_history, new_history)

s = s.replace(
    "current.chase = makeBuild(next.region, current.target, current.morgan.name);",
    "current.chase = makeBuild(next.region, current.target, [current.morgan.name, current.chase.name]);"
)
s = s.replace(
    "current.morgan = makeBuild(next.region, current.target, current.chase.name);",
    "current.morgan = makeBuild(next.region, current.target, [current.chase.name, current.morgan.name]);"
)

p.write_text(s)
