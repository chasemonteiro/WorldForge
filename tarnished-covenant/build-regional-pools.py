from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()
data = Path('tarnished-covenant/regional-pools.js').read_text().strip()

marker = '\nconst chaosTriggers = ['
if marker not in s:
    raise SystemExit('chaos trigger marker not found')

runtime = r'''

// Spreadsheet-backed regional pools.
const ORIGINAL_WEAPON_CATALOG = new Map();
for (const region of Object.values(regions)) {
  for (const weapon of (region.weapons || [])) {
    const key = weapon.name.replace(/ \(\+\d+\)$/,'').toLowerCase().replace(/[’]/g,"'");
    if (!ORIGINAL_WEAPON_CATALOG.has(key)) ORIGINAL_WEAPON_CATALOG.set(key, weapon);
  }
}

function sheetWeapon(name) {
  const lookup = name.replace(/ \(\+\d+\)$/,'').toLowerCase().replace(/[’]/g,"'");
  const known = ORIGINAL_WEAPON_CATALOG.get(lookup);
  if (known) return { ...known, name };
  return W(name, 'Regional weapon', 'Smithing path varies', 'Native skill', false);
}

for (const [regionName, names] of Object.entries(SHEET_WEAPON_POOLS)) {
  if (regions[regionName]) regions[regionName].weapons = names.map(sheetWeapon);
}
for (const [regionName, names] of Object.entries(SHEET_BOSS_POOLS)) {
  if (regions[regionName]) regions[regionName].bosses = [...names];
}

const WEAPON_TARGET_BLOCKS = {
  "bloodhound's fang": 'darriwil',
  'golden halberd': 'tree sentinel',
  'grafted blade greatsword': 'leonine misbegotten',
  'moonveil': 'magma wyrm',
  'ruins greatsword': 'crucible knight and misbegotten warrior',
  "godslayer's greatsword": 'godskin apostle',
  'blasphemous blade': 'rykard',
  "loretta's war sickle": 'loretta, knight of the haligtree',
  "malekith's black blade": 'maliketh',
  "dragon king's cragblade": 'placidusax',
  "dragon-hunter's great katana": 'ancient dragon-man',
  "leda's sword": 'leda and allies',
  'flowerstone gavel': 'bayle',
  'obsidian lamina': 'promised consort radahn'
};

function normalizedGameName(name = '') {
  return name.toLowerCase().replace(/[’]/g,"'");
}

function weaponBlockedByTarget(weapon, target) {
  if (weapon.requires && normalizedGameName(target.name).includes(normalizedGameName(weapon.requires))) return true;
  const block = WEAPON_TARGET_BLOCKS[normalizedGameName(weapon.name).replace(/ \(\+\d+\)$/,'')];
  return Boolean(block && normalizedGameName(target.name).includes(block));
}
'''

s = s.replace(marker, '\n' + data + runtime + '\nconst chaosTriggers = [', 1)

selection_pattern = re.compile(r"function capstoneChance\(cleared\) \{.*?\n\}\n\nfunction initialRunState", re.S)
selection_replacement = r'''function defeatedBossNames(state, regionName = state.region) {
  return new Set((state.history || [])
    .filter(entry => entry?.region === regionName)
    .map(entry => entry.name));
}

function availableRegionalBosses(state) {
  const defeated = defeatedBossNames(state);
  return (regions[state.region].bosses || []).filter(name => !defeated.has(name));
}

function capstoneRequirement(state) {
  if (state.region === 'The Erdtree') return 0;
  const available = availableRegionalBosses(state);
  const poolAtEntry = state.cleared + available.length;
  return Math.min(MIN_REGIONAL_BOSSES, poolAtEntry);
}

function capstoneChanceForState(state) {
  const requirement = capstoneRequirement(state);
  if (state.cleared < requirement) return 0;
  return Math.min(0.10 + Math.max(0, state.cleared - requirement) * 0.09, 0.82);
}

function chooseTarget(state) {
  const region = regions[state.region];
  if (state.region === 'The Erdtree') return { name: region.exit, exit: true };

  const available = availableRegionalBosses(state);
  const revisiting = (state.clearedRegions || []).includes(state.region);
  if (revisiting && available.length) return { name: pick(available), exit: false };

  const requirement = capstoneRequirement(state);
  if (!available.length) return { name: region.exit, exit: true };
  if (state.cleared < requirement) return { name: pick(available), exit: false };
  return Math.random() < capstoneChanceForState(state)
    ? { name: region.exit, exit: true }
    : { name: pick(available), exit: false };
}

function eligibleWeapons(regionName, target) {
  const region = regions[regionName];
  const pool = (region.weapons || []).filter(w => !weaponBlockedByTarget(w, target));
  return pool.length ? pool : (region.weapons || []);
}

function buildFromWeapon(weapon) {
  return {
    ...weapon,
    affinity: weapon.infusable ? pick(affinities) : 'Fixed / unique',
    role: pick(roles)
  };
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

function usedWeaponNames(state) {
  const used = new Set();
  for (const entry of (state.history || [])) {
    if (entry.chaseWeapon) used.add(entry.chaseWeapon);
    if (entry.morganWeapon) used.add(entry.morganWeapon);
  }
  return used;
}

function accumulatedWeaponPool(state, target) {
  const regionNames = Array.from(new Set([...(state.clearedRegions || []), state.region]));
  const byName = new Map();
  for (const regionName of regionNames) {
    for (const weapon of eligibleWeapons(regionName, target)) {
      if (!byName.has(weapon.name)) byName.set(weapon.name, weapon);
    }
  }
  return [...byName.values()];
}

function scoreWeaponPair(state, chaseWeapon, morganWeapon, poolSize) {
  const chaseRecent = new Set(recentWeaponNames(state, 'chaseWeapon'));
  const morganRecent = new Set(recentWeaponNames(state, 'morganWeapon'));
  const recentPairs = new Set((state.history || [])
    .map(entry => entry?.weaponPair)
    .filter(Boolean)
    .slice(0, Math.min(10, Math.max(4, poolSize * 2))));
  let score = Math.random();
  if (!chaseRecent.has(chaseWeapon.name)) score += 5;
  if (!morganRecent.has(morganWeapon.name)) score += 5;
  if (!recentPairs.has(pairKey(chaseWeapon.name, morganWeapon.name))) score += 8;
  return score;
}

function bestPairFromPool(state, chasePool, morganPool) {
  const candidates = [];
  const poolSize = Math.max(chasePool.length, morganPool.length);
  for (const chaseWeapon of chasePool) {
    for (const morganWeapon of morganPool) {
      if (chaseWeapon.name === morganWeapon.name) continue;
      candidates.push({
        chaseWeapon,
        morganWeapon,
        score: scoreWeaponPair(state, chaseWeapon, morganWeapon, poolSize)
      });
    }
  }
  if (!candidates.length) return null;
  candidates.sort((a,b) => b.score - a.score);
  return candidates[0];
}

function chooseWeaponPair(state, target) {
  const currentPool = eligibleWeapons(state.region, target);
  const used = usedWeaponNames(state);
  const unusedCurrent = currentPool.filter(w => !used.has(w.name));
  let pair = null;

  // Burn through the current region's deck before recycling older areas.
  if (unusedCurrent.length >= 2) {
    pair = bestPairFromPool(state, unusedCurrent, unusedCurrent);
  } else if (unusedCurrent.length === 1) {
    const fallback = accumulatedWeaponPool(state, target).filter(w => w.name !== unusedCurrent[0].name);
    if (Math.random() < 0.5) pair = bestPairFromPool(state, unusedCurrent, fallback);
    else pair = bestPairFromPool(state, fallback, unusedCurrent);
  }

  if (!pair) {
    const fallback = accumulatedWeaponPool(state, target);
    pair = bestPairFromPool(state, fallback, fallback);
  }

  if (!pair) {
    const only = currentPool[0] || accumulatedWeaponPool(state, target)[0];
    return { chase: buildFromWeapon(only), morgan: buildFromWeapon(only) };
  }

  return {
    chase: buildFromWeapon(pair.chaseWeapon),
    morgan: buildFromWeapon(pair.morganWeapon)
  };
}

function makeBuild(regionName, target, avoidNames = [], state = null) {
  const avoided = new Set(Array.isArray(avoidNames) ? avoidNames : [avoidNames]);
  let pool = eligibleWeapons(regionName, target).filter(w => !avoided.has(w.name));
  if (state) {
    const unused = pool.filter(w => !usedWeaponNames(state).has(w.name));
    if (unused.length) pool = unused;
    else pool = accumulatedWeaponPool(state, target).filter(w => !avoided.has(w.name));
  }
  if (!pool.length) pool = eligibleWeapons(regionName, target);
  return buildFromWeapon(pick(pool));
}

function newEncounter(state) {
  const target = chooseTarget(state);
  const pair = chooseWeaponPair(state, target);
  const weird = pick(weirdness);
  return {
    id: crypto.randomUUID(),
    target,
    chase: pair.chase,
    morgan: pair.morgan,
    chaosTrigger: pick(chaosTriggers),
    chaosTriggered: false,
    chaosConsequence: '',
    weirdness: { name: weird[0], text: weird[1] },
    flavor: pick(encounterFlavors),
    penances: [],
    createdAt: new Date().toISOString()
  };
}

function initialRunState'''
s, n = selection_pattern.subn(selection_replacement, s, count=1)
if n != 1:
    raise SystemExit('selection block not found')

complete_pattern = re.compile(r"function completeEncounter\(state, actor\) \{.*?\n\}\n\nfunction rerollChaos", re.S)
complete_replacement = r'''function completeEncounter(state, actor) {
  const next = structuredClone(state);
  const target = next.current.target;
  next.history.unshift({
    name: target.name,
    region: next.region,
    exit: target.exit,
    chaseWeapon: next.current.chase.name,
    morganWeapon: next.current.morgan.name,
    weaponPair: pairKey(next.current.chase.name, next.current.morgan.name),
    completedBy: actor,
    completedAt: new Date().toISOString()
  });
  next.cleared += 1;
  next.lastAction = `${actor} says ${target.name} is defeated.`;
  next.updatedAt = new Date().toISOString();

  if (target.exit) {
    next.clearedRegions = Array.from(new Set([...(next.clearedRegions || []), next.region]));
    next.regionComplete = true;
    next.current = null;
    if (target.name === 'Radagon of the Golden Order / Elden Beast') next.runComplete = true;
    return next;
  }

  // If this is a return trip, leave automatically once its outstanding Remembrances are done.
  if ((next.clearedRegions || []).includes(next.region) && !regionHasMissingRemembrance(next, next.region)) {
    next.regionComplete = true;
    next.current = null;
    return next;
  }

  next.current = newEncounter(next);
  return next;
}

function rerollChaos'''
s, n = complete_pattern.subn(complete_replacement, s, count=1)
if n != 1:
    raise SystemExit('completeEncounter block not found')

# Appeals follow the same regional-first deck rule.
s = s.replace("current.chase = makeBuild(next.region, current.target, [current.morgan.name, current.chase.name]);",
              "current.chase = makeBuild(next.region, current.target, [current.morgan.name, current.chase.name], next);")
s = s.replace("current.morgan = makeBuild(next.region, current.target, [current.chase.name, current.morgan.name]);",
              "current.morgan = makeBuild(next.region, current.target, [current.chase.name, current.morgan.name], next);")
s = s.replace("current.chase = makeBuild(next.region, current.target);",
              "current.chase = makeBuild(next.region, current.target, [], next);")
s = s.replace("current.morgan = makeBuild(next.region, current.target, [current.chase.name, current.morgan.name]);",
              "current.morgan = makeBuild(next.region, current.target, [current.chase.name, current.morgan.name], next);")

progress_pattern = re.compile(r"function progressMarks\(cleared\) \{.*?\n\}\n\nfunction capstoneBlock\(state\) \{.*?\n\}", re.S)
progress_replacement = r'''function progressMarks(state) {
  const required = capstoneRequirement(state);
  const count = Math.max(4, Math.min(10, Math.max(required + 4, state.cleared + 3)));
  return Array.from({length:count},(_,i)=>`<span class="mark ${i < state.cleared ? 'done' : ''} ${i < required ? 'required' : ''}">${i < state.cleared ? '◆' : '◇'}</span>`).join('');
}

function capstoneBlock(state) {
  if (state.region === 'The Erdtree') return `<div class="fate-block"><div class="fate-title">FINAL AUDIENCE</div><div class="fate-copy">all required Remembrances have been claimed.</div></div>`;
  const required = capstoneRequirement(state);
  const fate = Math.round(capstoneChanceForState(state) * 100);
  const locked = state.cleared < required;
  const needed = Math.max(0, required - state.cleared);
  return `<div class="fate-block">
    <div class="progress-marks">${progressMarks(state)}</div>
    <div class="fate-title">${locked ? 'CAPSTONE SEALED' : (availableRegionalBosses(state).length ? `CAPSTONE CHANCE · ${fate}%` : 'CAPSTONE NEXT')}</div>
    <div class="fate-copy">${locked ? `${needed} more regional ${needed === 1 ? 'boss' : 'bosses'} required · capstone remains locked` : (availableRegionalBosses(state).length ? 'the regional capstone is now eligible to roll.' : 'all preliminary bosses in this area are cleared.')}</div>
  </div>`;
}'''
s, n = progress_pattern.subn(progress_replacement, s, count=1)
if n != 1:
    raise SystemExit('capstone display block not found')

p.write_text(s)
