from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Add remembrance branch regions and the final route after the base region table.
marker = "};\n\nconst chaosTriggers = ["
if marker not in s:
    raise SystemExit('region table marker not found')
extra_regions = r'''

regions['Siofra River + Nokron'] = {
  exit: 'Regal Ancestor Spirit',
  bosses: ['Mimic Tear','Dragonkin Soldier','Valiant Gargoyles'],
  weapons: [
    W('Horn Bow','Bow','Smithing Stones','Mighty Shot'),
    W('Nox Flowing Sword','Curved Sword','Somber Smithing Stones','Flowing Form',false),
    W('Nox Flowing Hammer','Hammer','Somber Smithing Stones','Flowing Form',false)
  ]
};
regions['Lake of Rot + Grand Cloister'] = {
  exit: 'Astel, Naturalborn of the Void',
  bosses: ['Dragonkin Soldier of Nokstella','Alabaster Lord','Putrid Tree Spirit'],
  weapons: [
    W('Scorpion’s Stinger','Dagger','Somber Smithing Stones','Repeating Thrust',false),
    W('Dragonscale Blade','Katana','Somber Smithing Stones','Ice Lightning Sword',false),
    W('Alabaster Lord’s Sword','Greatsword','Somber Smithing Stones','Alabaster Lords’ Pull',false)
  ]
};
regions['Deeproot Depths'] = {
  exit: 'Lichdragon Fortissax',
  bosses: ['Fia’s Champions','Crucible Knight Siluria','Erdtree Avatar'],
  weapons: [
    W('Siluria’s Tree','Great Spear','Somber Smithing Stones','Siluria’s Woe',false),
    W('Prince of Death’s Staff','Glintstone Staff','Somber Smithing Stones','No Skill',false)
  ]
};
regions['Mohgwyn Palace'] = {
  exit: 'Mohg, Lord of Blood',
  bosses: ['Nameless White Mask','Sanguine Noble','Putrid Corpse Swarm'],
  weapons: [
    W('Varre’s Bouquet','Hammer','Somber Smithing Stones','Blood Tax',false),
    W('Mohgwyn’s Sacred Spear','Great Spear','Somber Smithing Stones','Bloodboon Ritual',false,'Mohg, Lord of Blood')
  ]
};
regions['Leyndell, Ashen Capital'] = {
  exit: 'Godfrey, First Elden Lord / Hoarah Loux',
  bosses: ['Sir Gideon Ofnir, the All-Knowing','Ulcerated Tree Spirit','Erdtree Avatar'],
  weapons: regions['Altus Plateau + Leyndell'].weapons
};
regions['The Erdtree'] = {
  exit: 'Radagon of the Golden Order / Elden Beast',
  bosses: [],
  weapons: regions['Altus Plateau + Leyndell'].weapons
};

const chaosTriggers = ['''
s = s.replace(marker, extra_regions, 1)

# Progression / remembrance model.
needle = "const MIN_REGIONAL_BOSSES = 3;\n"
if needle not in s:
    raise SystemExit('MIN_REGIONAL_BOSSES marker not found')
progression = r'''const MIN_REGIONAL_BOSSES = 3;

const BASE_REMEMBRANCES = [
  'Godrick the Grafted',
  'Rennala, Queen of the Full Moon',
  'Starscourge Radahn',
  'Regal Ancestor Spirit',
  'Astel, Naturalborn of the Void',
  'Rykard, Lord of Blasphemy',
  'Morgott, the Omen King',
  'Lichdragon Fortissax',
  'Fire Giant',
  'Mohg, Lord of Blood',
  'Malenia, Blade of Miquella',
  'Maliketh, the Black Blade',
  'Dragonlord Placidusax',
  'Godfrey, First Elden Lord / Hoarah Loux'
];

const DLC_REMEMBRANCES = [
  'Divine Beast Dancing Lion',
  'Rellana, Twin Moon Knight',
  'Putrescent Knight',
  'Commander Gaius',
  'Scadutree Avatar',
  'Metyr, Mother of Fingers',
  'Midra, Lord of Frenzied Flame',
  'Messmer the Impaler',
  'Romina, Saint of the Bud',
  'Promised Consort Radahn'
];

const REMEMBRANCE_REGION = {
  'Godrick the Grafted': 'Limgrave + Stormveil',
  'Rennala, Queen of the Full Moon': 'Liurnia of the Lakes',
  'Starscourge Radahn': 'Caelid',
  'Regal Ancestor Spirit': 'Siofra River + Nokron',
  'Astel, Naturalborn of the Void': 'Lake of Rot + Grand Cloister',
  'Rykard, Lord of Blasphemy': 'Mt. Gelmir',
  'Morgott, the Omen King': 'Altus Plateau + Leyndell',
  'Lichdragon Fortissax': 'Deeproot Depths',
  'Fire Giant': 'Mountaintops of the Giants',
  'Mohg, Lord of Blood': 'Mohgwyn Palace',
  'Malenia, Blade of Miquella': 'Miquella’s Haligtree',
  'Maliketh, the Black Blade': 'Crumbling Farum Azula',
  'Dragonlord Placidusax': 'Crumbling Farum Azula',
  'Godfrey, First Elden Lord / Hoarah Loux': 'Leyndell, Ashen Capital',
  'Divine Beast Dancing Lion': 'Gravesite Plain · DLC',
  'Rellana, Twin Moon Knight': 'Gravesite Plain · DLC',
  'Putrescent Knight': 'Cerulean Coast · DLC',
  'Commander Gaius': 'Scadu Altus + Shadow Keep · DLC',
  'Scadutree Avatar': 'Scadu Altus + Shadow Keep · DLC',
  'Metyr, Mother of Fingers': 'Scadu Altus + Shadow Keep · DLC',
  'Midra, Lord of Frenzied Flame': 'Abyssal Woods · DLC',
  'Messmer the Impaler': 'Scadu Altus + Shadow Keep · DLC',
  'Romina, Saint of the Bud': 'Ancient Ruins of Rauh · DLC',
  'Promised Consort Radahn': 'Enir-Ilim · DLC'
};

function collectedRemembrances(state) {
  return new Set((state.history || []).map(x => x.name));
}

function requiredRemembrances(state) {
  return state.includeDlc ? [...BASE_REMEMBRANCES, ...DLC_REMEMBRANCES] : [...BASE_REMEMBRANCES];
}

function missingRemembrances(state) {
  const collected = collectedRemembrances(state);
  return requiredRemembrances(state).filter(name => !collected.has(name));
}

function finalSealOpen(state) {
  return missingRemembrances(state).length === 0;
}

function hasRemembrance(state, name) {
  return collectedRemembrances(state).has(name);
}

function regionHasMissingRemembrance(state, regionName) {
  return missingRemembrances(state).some(name => REMEMBRANCE_REGION[name] === regionName);
}

function regionUnlocked(state, regionName) {
  const cleared = new Set(state.clearedRegions || []);
  const has = name => hasRemembrance(state, name);
  switch (regionName) {
    case 'Weeping Peninsula':
    case 'Liurnia of the Lakes':
    case 'Caelid':
      return cleared.has('Limgrave + Stormveil');
    case 'Siofra River + Nokron':
      return has('Starscourge Radahn');
    case 'Lake of Rot + Grand Cloister':
      return has('Regal Ancestor Spirit') && has('Rennala, Queen of the Full Moon');
    case 'Altus Plateau + Leyndell':
      return has('Rennala, Queen of the Full Moon');
    case 'Mt. Gelmir':
      return cleared.has('Altus Plateau + Leyndell');
    case 'Deeproot Depths':
      return has('Regal Ancestor Spirit');
    case 'Mountaintops of the Giants':
      return has('Morgott, the Omen King');
    case 'Mohgwyn Palace':
      return has('Starscourge Radahn') && cleared.has('Mountaintops of the Giants');
    case 'Miquella’s Haligtree':
      return cleared.has('Mountaintops of the Giants');
    case 'Crumbling Farum Azula':
      return has('Fire Giant');
    case 'Leyndell, Ashen Capital':
      return has('Maliketh, the Black Blade');
    case 'The Erdtree':
      return has('Godfrey, First Elden Lord / Hoarah Loux') && finalSealOpen(state);
    case 'Gravesite Plain · DLC':
      return Boolean(state.includeDlc) && has('Starscourge Radahn') && has('Mohg, Lord of Blood');
    case 'Cerulean Coast · DLC':
    case 'Dragon’s Pit + Jagged Peak · DLC':
    case 'Scadu Altus + Shadow Keep · DLC':
      return Boolean(state.includeDlc) && cleared.has('Gravesite Plain · DLC');
    case 'Abyssal Woods · DLC':
      return Boolean(state.includeDlc) && cleared.has('Scadu Altus + Shadow Keep · DLC');
    case 'Ancient Ruins of Rauh · DLC':
      return Boolean(state.includeDlc) && has('Messmer the Impaler');
    case 'Enir-Ilim · DLC':
      return Boolean(state.includeDlc) && has('Messmer the Impaler') && has('Romina, Saint of the Bud');
    default:
      return regionName === 'Limgrave + Stormveil';
  }
}

function availableNextRegions(state) {
  const cleared = new Set(state.clearedRegions || []);
  return Object.keys(regions).filter(regionName => {
    if (regionName === state.region) return false;
    if (!state.includeDlc && regionName.includes('· DLC')) return false;
    if (!regionUnlocked(state, regionName)) return false;
    if (!cleared.has(regionName)) return true;
    return regionHasMissingRemembrance(state, regionName);
  });
}

function remembranceLedgerMarkup(state) {
  const required = requiredRemembrances(state);
  const collected = collectedRemembrances(state);
  const done = required.filter(name => collected.has(name)).length;
  const missing = required.filter(name => !collected.has(name));
  return `<section class="fate-block">
    <div class="fate-title">REMEMBRANCES · ${done}/${required.length}</div>
    <div class="fate-copy">${missing.length ? `${missing.length} required before the final seal can break.` : 'all required Remembrances claimed · the final seal is open.'}</div>
  </section>`;
}
'''
s = s.replace(needle, progression, 1)

# The final fight should be a guaranteed encounter once unlocked.
s = s.replace(
"function chooseTarget(regionName, cleared) {\n  const region = regions[regionName];\n  return Math.random() < capstoneChance(cleared)\n    ? { name: region.exit, exit: true }\n    : { name: pick(region.bosses), exit: false };\n}",
"function chooseTarget(regionName, cleared) {\n  const region = regions[regionName];\n  if (regionName === 'The Erdtree') return { name: region.exit, exit: true };\n  return Math.random() < capstoneChance(cleared)\n    ? { name: region.exit, exit: true }\n    : { name: pick(region.bosses), exit: false };\n}"
)

# New-run screen: progression always begins in Limgrave; DLC is an explicit ruleset toggle.
pattern = r"function renderNewRun\(identity\) \{.*?\n\}\n\nasync function joinSharedRun"
replacement = r'''function renderNewRun(identity) {
  app.innerHTML = `${header(true)}
    <section class="menu-section stack new-run">
      <div class="menu-title">begin new run</div>
      <div>
        <label class="label">starting region</label>
        <div class="status">Limgrave + Stormveil</div>
      </div>
      <div>
        <label class="label" for="ruleset">remembrance ruleset</label>
        <select id="ruleset"><option value="base" selected>Base Game · All Remembrances</option><option value="dlc">Base + Shadow of the Erdtree · All Remembrances</option></select>
      </div>
      <div>
        <label class="label" for="severity">difficulty</label>
        <select id="severity"><option value="normal">Silly</option><option value="hard" selected>Maidenless</option><option value="cursed">Miyazaki Has Noticed You</option></select>
      </div>
      <button class="btn gold" id="createRun" type="button">Begin Covenant</button>
      <button class="btn text-btn" id="back" type="button">Back</button>
    </section>`;
  document.querySelector('#back').addEventListener('click', renderHome);
  document.querySelector('#createRun').addEventListener('click', async () => {
    const state = initialRunState({
      region: 'Limgrave + Stormveil',
      severity: document.querySelector('#severity').value,
      includeDlc: document.querySelector('#ruleset').value === 'dlc',
      createdBy: identity
    });
    try {
      const created = await backend.createRun(identity, state);
      run = created;
      session = { runId: run.id, joinCode: run.joinCode, displayName: identity };
      saveSession(session);
      subscribe();
      renderRun();
    } catch (error) {
      console.error(error);
      setToast(error.message || 'Could not create Covenant.');
    }
  });
}

async function joinSharedRun'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('renderNewRun block not found')

# New persistent run fields.
pattern = r"function initialRunState\(\{ region, severity, createdBy = 'Chase' \}\) \{.*?\n\}\n\nfunction completeEncounter"
replacement = r'''function initialRunState({ region, severity, includeDlc = false, createdBy = 'Chase' }) {
  const base = {
    version: 2,
    phase: 'active',
    region,
    severity,
    includeDlc,
    createdBy,
    cleared: 0,
    clearedRegions: [],
    history: [],
    current: null,
    regionComplete: false,
    runComplete: false,
    lastAction: `${createdBy} started the Covenant.`,
    updatedAt: new Date().toISOString()
  };
  base.current = newEncounter(base);
  return base;
}

function completeEncounter'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('initialRunState block not found')

# Mark regions globally cleared and finish the run after Elden Beast.
s = s.replace(
"  if (target.exit) {\n    next.regionComplete = true;\n    next.current = null;\n    return next;\n  }",
"  if (target.exit) {\n    next.clearedRegions = Array.from(new Set([...(next.clearedRegions || []), next.region]));\n    next.regionComplete = true;\n    next.current = null;\n    if (target.name === 'Radagon of the Golden Order / Elden Beast') next.runComplete = true;\n    return next;\n  }"
)

# Preserve global progression when entering the next region.
pattern = r"function startNextRegion\(state, actor, region, severity = state\.severity\) \{.*?\n\}"
replacement = r'''function startNextRegion(state, actor, region, severity = state.severity) {
  const next = initialRunState({
    region,
    severity,
    includeDlc: Boolean(state.includeDlc),
    createdBy: state.createdBy || actor
  });
  next.history = [...(state.history || [])];
  next.clearedRegions = [...(state.clearedRegions || [])];
  next.lastAction = `${actor} entered ${region}.`;
  return next;
}'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('startNextRegion block not found')

# Show ledger during active play.
s = s.replace("    ${capstoneBlock(state)}\n", "    ${capstoneBlock(state)}\n    ${remembranceLedgerMarkup(state)}\n", 1)

# Special final region capstone copy.
s = s.replace(
"function capstoneBlock(state) {\n  const fate = Math.round(capstoneChance(state.cleared) * 100);",
"function capstoneBlock(state) {\n  if (state.region === 'The Erdtree') return `<div class=\"fate-block\"><div class=\"fate-title\">FINAL AUDIENCE</div><div class=\"fate-copy\">all required Remembrances have been claimed.</div></div>`;\n  const fate = Math.round(capstoneChance(state.cleared) * 100);"
)

# Run-complete screen takes precedence over ordinary region completion.
s = s.replace(
"  if (state.regionComplete) return renderRegionComplete();",
"  if (state.runComplete) return renderRunComplete();\n  if (state.regionComplete) return renderRegionComplete();",
1
)

# Replace the region-complete screen with gated paths and missing-remembrance guidance.
pattern = r"function renderRegionComplete\(\) \{.*?\n\}\n\nasync function shareCovenant"
replacement = r'''function renderRegionComplete() {
  const state = run.state;
  setRegionTheme(state.region);
  const choices = availableNextRegions(state);
  const options = choices.map(r => `<option value="${h(r)}">${h(r)}${(state.clearedRegions || []).includes(r) ? ' · RETURN' : ''}</option>`).join('');
  const missing = missingRemembrances(state);
  const seal = finalSealOpen(state);
  app.innerHTML = `${header(true)}
    <section class="escape-screen">
      <div class="tag">REGIONAL BOSS DEFEATED</div>
      <div class="escape-title">Region Complete</div>
      <div class="escape-copy">${state.region} cleared. Outstanding armament penalties are forgiven.</div>
    </section>
    ${remembranceLedgerMarkup(state)}
    <div class="ornament"><span>✦</span></div>
    <section class="menu-section stack">
      <div class="eyebrow left">paths now open</div>
      ${choices.length ? `<div><label class="label" for="nextRegion">next region</label><select id="nextRegion">${options}</select></div><button id="continue" class="btn gold" type="button">Travel to Selected Region</button>` : `<div class="status">No new route is currently open.</div>`}
      ${!seal ? `<div class="status warn">Final seal closed · missing: ${h(missing.slice(0,5).join(', '))}${missing.length > 5 ? ` +${missing.length-5} more` : ''}</div>` : `<div class="status">Final seal open.</div>`}
      <button id="share" class="btn ghost" type="button">Share Covenant</button>
      <button id="restartRun" class="btn curse" type="button">Restart Covenant</button>
      <div id="restartConfirm"></div>
      <button id="leave" class="btn text-btn" type="button">leave run</button>
    </section>
    <section class="history"><div class="section-kicker">encounter history</div>${renderHistory(state)}</section>`;
  document.querySelector('#continue')?.addEventListener('click',()=>{
    const next = startNextRegion(state,playerName(),document.querySelector('#nextRegion').value,state.severity);
    commit(next);
  });
  document.querySelector('#share').addEventListener('click',shareCovenant);
  document.querySelector('#restartRun').addEventListener('click',showRestart);
  document.querySelector('#leave').addEventListener('click',()=>{unsubscribe?.();run=null;clearSession();session=null;renderHome();});
}

function renderRunComplete() {
  const state = run.state;
  setRegionTheme('Leyndell');
  const total = requiredRemembrances(state).length + 1;
  app.innerHTML = `${header(true)}
    <section class="escape-screen">
      <div class="tag">COVENANT COMPLETE</div>
      <div class="escape-title">All Remembrances Claimed</div>
      <div class="escape-copy">Radagon and the Elden Beast are defeated. ${total}/${total} required remembrance encounters complete.</div>
    </section>
    <div class="ornament"><span>✦</span></div>
    <section class="menu-section stack">
      <button id="share" class="btn ghost" type="button">Share Covenant</button>
      <button id="restartRun" class="btn curse" type="button">Restart Covenant</button>
      <div id="restartConfirm"></div>
    </section>
    <section class="history"><div class="section-kicker">encounter history</div>${renderHistory(state)}</section>`;
  document.querySelector('#share').addEventListener('click',shareCovenant);
  document.querySelector('#restartRun').addEventListener('click',showRestart);
}

async function shareCovenant'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('renderRegionComplete block not found')

# Include Scadutree Avatar in the DLC region where it can be rolled and credited.
s = s.replace(
"bosses: ['Golden Hippopotamus','Commander Gaius','Ralva the Great Red Bear','Ghostflame Dragon','Furnace Golem','Metyr, Mother of Fingers']",
"bosses: ['Golden Hippopotamus','Commander Gaius','Scadutree Avatar','Ralva the Great Red Bear','Ghostflame Dragon','Furnace Golem','Metyr, Mother of Fingers']"
)

p.write_text(s)
