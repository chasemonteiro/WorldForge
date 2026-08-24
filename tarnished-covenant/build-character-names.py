from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Replace new-run setup with character-name fields.
pattern = r"function renderNewRun\(identity\) \{.*?\n\}\n\nasync function joinSharedRun"
replacement = r'''function renderNewRun(identity) {
  app.innerHTML = `${header(true)}
    <section class="menu-section stack new-run">
      <div class="menu-title">begin new run</div>
      <div class="tc-name-grid">
        <div>
          <label class="label" for="characterOne">first Tarnished</label>
          <input id="characterOne" type="text" maxlength="24" autocomplete="off" placeholder="Character name" value="Chase">
        </div>
        <div>
          <label class="label" for="characterTwo">second Tarnished</label>
          <input id="characterTwo" type="text" maxlength="24" autocomplete="off" placeholder="Character name" value="Morgan">
        </div>
      </div>
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
    const one = document.querySelector('#characterOne').value.trim() || 'Tarnished One';
    const two = document.querySelector('#characterTwo').value.trim() || 'Tarnished Two';
    const state = initialRunState({
      region: 'Limgrave + Stormveil',
      severity: document.querySelector('#severity').value,
      includeDlc: document.querySelector('#ruleset').value === 'dlc',
      playerNames: [one, two],
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

# Persist names in run state.
s, n = re.subn(
    r"function initialRunState\(\{ region, severity, includeDlc = false, createdBy = 'Chase' \}\) \{",
    "function initialRunState({ region, severity, includeDlc = false, playerNames = ['Chase','Morgan'], createdBy = 'Chase' }) {",
    s,
    count=1
)
if n != 1:
    raise SystemExit('initialRunState signature not found')

needle = "    includeDlc,\n    createdBy,"
if needle not in s:
    raise SystemExit('initial state field marker not found')
s = s.replace(needle, "    includeDlc,\n    playerNames: Array.isArray(playerNames) && playerNames.length >= 2 ? playerNames.slice(0,2) : ['Chase','Morgan'],\n    createdBy,", 1)

# Preserve character names when moving regions.
needle = "    includeDlc: Boolean(state.includeDlc),\n    createdBy: state.createdBy || actor"
if needle not in s:
    raise SystemExit('startNextRegion marker not found')
s = s.replace(needle, "    includeDlc: Boolean(state.includeDlc),\n    playerNames: state.playerNames || ['Chase','Morgan'],\n    createdBy: state.createdBy || actor", 1)

# Shared display helpers.
marker = "function navMarkup(active) {"
if marker not in s:
    raise SystemExit('nav helper marker not found')
helpers = r'''function covenantNames(state = run?.state) {
  const names = state?.playerNames;
  return Array.isArray(names) && names.length >= 2
    ? [String(names[0] || 'Tarnished One'), String(names[1] || 'Tarnished Two')]
    : ['Chase','Morgan'];
}
function playerLabel(slot, state = run?.state) {
  const names = covenantNames(state);
  return slot === 'morgan' ? names[1] : names[0];
}
function personalizePlayers(text, state = run?.state) {
  if (!text) return text || '';
  const [one,two] = covenantNames(state);
  return String(text)
    .replace(/\bChase\b/g, one)
    .replace(/\bMorgan\b/g, two)
    .replace(/\bCHASE\b/g, one.toUpperCase())
    .replace(/\bMORGAN\b/g, two.toUpperCase());
}
'''
s = s.replace(marker, helpers + '\n' + marker, 1)

# Use custom names in loadouts and Decree reveal.
s = s.replace("${compactLoadout('Chase',c.chase)}${compactLoadout('Morgan',c.morgan)}", "${compactLoadout(playerLabel('chase',state),c.chase)}${compactLoadout(playerLabel('morgan',state),c.morgan)}")
s = s.replace("<div class=\"tc-kicker\">Chase</div><strong>${h(c.chase.name)}</strong>", "<div class=\"tc-kicker\">${h(playerLabel('chase',state))}</div><strong>${h(c.chase.name)}</strong>")
s = s.replace("<div class=\"tc-kicker\">Morgan</div><strong>${h(c.morgan.name)}</strong>", "<div class=\"tc-kicker\">${h(playerLabel('morgan',state))}</div><strong>${h(c.morgan.name)}</strong>")

# Weapon Appeal overlay labels/buttons.
s = s.replace('<div class="tc-muted">CHASE</div><div>${h(c.chase.name)}</div>', '<div class="tc-muted">${h(playerLabel(\'chase\',run.state).toUpperCase())}</div><div>${h(c.chase.name)}</div>')
s = s.replace('<div class="tc-muted" style="margin-top:8px">MORGAN</div><div>${h(c.morgan.name)}</div>', '<div class="tc-muted" style="margin-top:8px">${h(playerLabel(\'morgan\',run.state).toUpperCase())}</div><div>${h(c.morgan.name)}</div>')
s = s.replace('data-overlay-appeal="chase">Chase</button>', 'data-overlay-appeal="chase">${h(playerLabel(\'chase\',run.state))}</button>')
s = s.replace('data-overlay-appeal="morgan">Morgan</button>', 'data-overlay-appeal="morgan">${h(playerLabel(\'morgan\',run.state))}</button>')

# Personalize Chaos triggers/consequences everywhere they are displayed.
s = s.replace("${h(c.chaosTrigger)}", "${h(personalizePlayers(c.chaosTrigger,state))}")
s = s.replace("${h(c.chaosConsequence)}", "${h(personalizePlayers(c.chaosConsequence,run.state))}")

# A little styling for the two name inputs.
css = r'''
.tc-name-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.tc-name-grid input{width:100%;border:1px solid #4b402d;background:rgba(12,10,7,.82);color:var(--ink);padding:11px 10px;font:16px Georgia,serif;outline:none}
.tc-name-grid input:focus{border-color:var(--gold);box-shadow:0 0 0 1px rgba(201,163,84,.18)}
@media(max-width:430px){.tc-name-grid{grid-template-columns:1fr}}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

p.write_text(s)
