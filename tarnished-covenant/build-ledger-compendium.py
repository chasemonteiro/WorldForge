from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Save a rich immutable snapshot of each completed encounter so the Ledger can
# become a real run scrapbook instead of reconstructing details later.
fn_start = s.find('function completeEncounter(state, actor) {')
if fn_start < 0:
    raise SystemExit('completeEncounter function missing')
fn_end = s.find('\nfunction ', fn_start + 10)
if fn_end < 0:
    raise SystemExit('completeEncounter end missing')
chunk = s[fn_start:fn_end]
pat = r"next\.history\.unshift\(\{.*?\}\);"
replacement = r'''const encounter = next.current;
  const riteFavor = encounter?.smithingRiteFavor ? Math.max(0, Number(encounter?.weirdness?.favor ?? 1)) : 0;
  const chaosFavor = encounter?.smithingChaosFavor ? Math.max(0, Number(encounter?.chaosFavor ?? 1)) : 0;
  next.history.unshift({
    name: target.name,
    exit: target.exit,
    region: next.region,
    completedBy: actor,
    completedAt: new Date().toISOString(),
    playerNames: structuredClone(next.playerNames || {}),
    chaseWeapon: encounter?.chase?.name || '',
    morganWeapon: encounter?.morgan?.name || '',
    chaseBuild: encounter?.chase ? structuredClone(encounter.chase) : null,
    morganBuild: encounter?.morgan ? structuredClone(encounter.morgan) : null,
    oddRite: encounter?.weirdness ? structuredClone(encounter.weirdness) : null,
    chaosTrigger: encounter?.chaosTrigger || '',
    chaosTriggered: Boolean(encounter?.chaosTriggered),
    chaosConsequence: encounter?.chaosConsequence || '',
    penances: structuredClone(encounter?.penances || []),
    favorEarned: riteFavor + chaosFavor
  });'''
chunk2, n = re.subn(pat, replacement, chunk, count=1, flags=re.S)
if n != 1:
    raise SystemExit('history snapshot target missing')
s = s[:fn_start] + chunk2 + s[fn_end:]

helpers = r'''
function compendiumNames(entry,state){
  const current=typeof covenantNames==='function'?covenantNames(state):{chase:'Tarnished One',morgan:'Tarnished Two'};
  const saved=entry?.playerNames||{};
  return {
    chase:saved.chase||saved.player1||current.chase||'Tarnished One',
    morgan:saved.morgan||saved.player2||current.morgan||'Tarnished Two'
  };
}
function compendiumDate(value){
  if(!value)return '';
  try{return new Date(value).toLocaleDateString(undefined,{month:'short',day:'numeric'});}catch{return '';}
}
function compendiumEntryMarkup(entry,index,state){
  const names=compendiumNames(entry,state);
  const rich=Boolean(entry.chaseWeapon||entry.morganWeapon||entry.oddRite||entry.chaosTrigger);
  const chaos=entry.chaosTriggered&&entry.chaosConsequence;
  const mods=Array.isArray(entry.penances)?entry.penances:[];
  if(!rich){
    return `<details class="tc-comp-card legacy"><summary><div><div class="tc-comp-number">ENTRY ${String(index+1).padStart(2,'0')} · ${h(entry.region||'Earlier run')}</div><div class="tc-comp-boss">${h(entry.name||'Unknown foe')}</div></div><span class="tc-comp-mark">${entry.exit?'CAPSTONE':'LEGACY'}</span></summary><div class="tc-comp-legacy">This kill predates the Compendium. The Covenant remembers the corpse, but not what nonsense got you there.</div></details>`;
  }
  return `<details class="tc-comp-card ${entry.exit?'capstone':''}"><summary><div><div class="tc-comp-number">ENTRY ${String(index+1).padStart(2,'0')} · ${h(entry.region||'Unknown region')} ${compendiumDate(entry.completedAt)?'· '+h(compendiumDate(entry.completedAt)):''}</div><div class="tc-comp-boss">${h(entry.name||'Unknown foe')}</div><div class="tc-comp-pair">${h(entry.chaseWeapon||'Unknown weapon')} × ${h(entry.morganWeapon||'Unknown weapon')}</div></div><span class="tc-comp-mark">${entry.exit?'CAPSTONE':'FELLED'}</span></summary>
    <div class="tc-comp-body">
      <div class="tc-comp-weapons"><div><span>${h(names.chase)}</span><strong>${h(entry.chaseWeapon||'—')}</strong>${entry.chaseBuild?.role?`<em>${h(entry.chaseBuild.role)}</em>`:''}</div><div><span>${h(names.morgan)}</span><strong>${h(entry.morganWeapon||'—')}</strong>${entry.morganBuild?.role?`<em>${h(entry.morganBuild.role)}</em>`:''}</div></div>
      ${entry.oddRite?`<div class="tc-comp-mod rite"><span>ODD RITE</span><strong>${h(entry.oddRite.name||'Unnamed Rite')}</strong><p>${h(entry.oddRite.text||'')}</p></div>`:''}
      ${entry.chaosTriggered?`<div class="tc-comp-mod chaos"><span>CHAOS · TRIGGERED</span><strong>${h(typeof chaosEventName==='function'?chaosEventName(entry.chaosConsequence||'Chaos'): 'Chaos')}</strong><p>${h(entry.chaosConsequence||'The seal broke. Details lost to history.')}</p></div>`:`<div class="tc-comp-mod quiet"><span>CHAOS</span><strong>Seal remained intact</strong></div>`}
      ${mods.length?`<div class="tc-comp-mod penalties"><span>ARMAMENT PENALTIES · ${mods.length}</span>${mods.map(x=>`<p><b>${h(x.name||'Penalty')}</b> · ${h(x.text||'')}</p>`).join('')}</div>`:''}
      <div class="tc-comp-footer"><span>${entry.completedBy?`recorded by ${h(entry.completedBy)}`:'victory recorded'}</span><strong>${Number(entry.favorEarned||0)>0?`+${Number(entry.favorEarned)} Favor`:'No Favor'}</strong></div>
    </div>
  </details>`;
}
function compendiumLedgerMarkup(state){
  const entries=Array.isArray(state.history)?state.history:[];
  const rich=entries.filter(x=>x.chaseWeapon||x.morganWeapon||x.oddRite);
  const chaosCount=entries.filter(x=>x.chaosTriggered).length;
  const favor=entries.reduce((sum,x)=>sum+Number(x.favorEarned||0),0);
  if(!entries.length)return `<div class="tc-comp-empty"><div class="tc-comp-empty-glyph">◇</div><div class="tc-value">Nothing to remember yet.</div><div class="tc-muted">Kill something regrettable and it will be preserved here.</div></div>`;
  return `<div class="tc-comp-hero"><div><div class="tc-kicker gold">Covenant Compendium</div><div class="tc-comp-title">The run, as it actually happened.</div><div class="tc-muted">Bosses, cursed weapon pairings, Rites, Chaos, and other decisions that seemed reasonable at the time.</div></div><div class="tc-comp-total">${entries.length}</div></div>
    <div class="tc-comp-stats"><div><strong>${entries.length}</strong><span>Felled</span></div><div><strong>${rich.length}</strong><span>Full records</span></div><div><strong>${chaosCount}</strong><span>Chaos events</span></div><div><strong>${favor}</strong><span>Favor earned</span></div></div>
    <div class="tc-comp-list">${entries.map((entry,i)=>compendiumEntryMarkup(entry,i,state)).join('')}</div>`;
}
'''

marker = 'function renderLedger() {'
if marker not in s:
    raise SystemExit('renderLedger marker missing')
s = s.replace(marker, helpers + '\n' + marker, 1)

# Replace the ledger renderer with three complementary views. Ledger gets a
# dedicated class so it can opt out of the global screen-entry animation; that
# animation replayed on every Ledger render/tab change and read as a flicker.
pat = r"function renderLedger\(\) \{.*?\n\}\n\nfunction renderSettings\(\)"
new_renderer = r'''function renderLedger() {
  const state=run.state;
  const title=ledgerView==='smithing'?'Smithing Ledger':ledgerView==='compendium'?'Covenant Compendium':'Remembrance Ledger';
  const body=ledgerView==='smithing'?smithingLedgerMarkup(state):ledgerView==='compendium'?compendiumLedgerMarkup(state):remembranceLedgerBody(state);
  app.innerHTML=`<section class="tc-screen tc-ledger-screen">${screenTop(title)}
    <div class="tc-ledger-tabs tc-ledger-tabs-3"><button class="${ledgerView==='remembrances'?'active':''}" data-ledger-view="remembrances">Progress</button><button class="${ledgerView==='compendium'?'active':''}" data-ledger-view="compendium">Compendium</button><button class="${ledgerView==='smithing'?'active':''}" data-ledger-view="smithing">Smithing</button></div>
    ${body}
    ${navMarkup('ledger')}</section>`;
  bindNav();
}

function renderSettings()'''
s, n = re.subn(pat, new_renderer, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('ledger renderer replacement failed')

css = r'''
/* --- Ledger Compendium: the stupid things we survived --- */
.tc-ledger-screen{animation:none!important}
.tc-ledger-tabs-3{grid-template-columns:repeat(3,1fr)}
.tc-comp-hero{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:14px;align-items:end;padding:8px 3px 15px;border-bottom:1px solid rgba(198,161,90,.24)}
.tc-comp-title{font:400 clamp(24px,7vw,34px)/1.02 Georgia,serif;margin:5px 0 6px;color:var(--ink)}
.tc-comp-total{font:400 48px/.9 Georgia,serif;color:var(--gold-bright);opacity:.9}
.tc-comp-stats{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line-soft);margin:11px 0 15px;background:rgba(12,11,8,.55)}
.tc-comp-stats>div{text-align:center;padding:10px 4px;border-right:1px solid var(--line-soft)}.tc-comp-stats>div:last-child{border-right:0}
.tc-comp-stats strong{display:block;font:400 20px/1 Georgia,serif;color:var(--gold-bright)}.tc-comp-stats span{display:block;margin-top:4px;font:800 6px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em;color:var(--ash)}
.tc-comp-list{display:grid;gap:8px}.tc-comp-card{border:1px solid var(--line-soft);background:linear-gradient(145deg,rgba(22,19,14,.78),rgba(8,8,6,.72));overflow:hidden}.tc-comp-card.capstone{border-color:rgba(198,161,90,.37)}
.tc-comp-card summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:center;padding:13px 12px}.tc-comp-card summary::-webkit-details-marker{display:none}
.tc-comp-number{font:800 7px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.11em;color:var(--ash)}.tc-comp-boss{font:400 clamp(20px,6vw,27px)/1.05 Georgia,serif;margin:5px 0 3px;color:var(--ink)}.tc-comp-pair{font:italic 10px/1.25 Georgia,serif;color:#aaa18f;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tc-comp-mark{font:800 7px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em;color:var(--gold);border-left:1px solid var(--line);padding-left:10px}.tc-comp-card[open] .tc-comp-mark{color:var(--gold-bright)}
.tc-comp-body{border-top:1px solid var(--line-soft);padding:11px 12px 12px;background:rgba(5,5,4,.26)}
.tc-comp-weapons{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line-soft);margin-bottom:9px}.tc-comp-weapons>div{padding:9px;min-width:0}.tc-comp-weapons>div+div{border-left:1px solid var(--line-soft)}.tc-comp-weapons span,.tc-comp-mod>span{display:block;font:800 7px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.1em;color:var(--ash)}.tc-comp-weapons strong{display:block;font:400 15px/1.1 Georgia,serif;margin:4px 0}.tc-comp-weapons em{display:block;color:#8f8675;font-size:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tc-comp-mod{padding:9px 1px;border-top:1px solid var(--line-soft)}.tc-comp-mod strong{display:block;font:400 15px/1.2 Georgia,serif;margin:4px 0;color:var(--ink)}.tc-comp-mod p{margin:4px 0 0;font:10px/1.35 Georgia,serif;color:#bbb19f}.tc-comp-mod.rite>span{color:var(--violet)}.tc-comp-mod.chaos>span{color:var(--red)}.tc-comp-mod.quiet{opacity:.62}.tc-comp-mod.penalties>span{color:#d58b80}.tc-comp-mod.penalties b{font-weight:400;color:#d6c8b0}
.tc-comp-footer{display:flex;justify-content:space-between;gap:12px;align-items:center;border-top:1px solid var(--line-soft);padding-top:9px;margin-top:2px;font:800 7px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em;color:var(--ash)}.tc-comp-footer strong{color:var(--gold)}
.tc-comp-legacy{padding:0 12px 13px;color:var(--ash);font:italic 10px/1.4 Georgia,serif}.tc-comp-card.legacy{opacity:.77}
.tc-comp-empty{text-align:center;padding:20vh 20px 0}.tc-comp-empty-glyph{font-size:38px;color:var(--gold);margin-bottom:12px;opacity:.7}
@media(max-width:390px){.tc-comp-stats{grid-template-columns:repeat(2,1fr)}.tc-comp-stats>div:nth-child(2){border-right:0}.tc-comp-stats>div:nth-child(-n+2){border-bottom:1px solid var(--line-soft)}.tc-comp-weapons{grid-template-columns:1fr}.tc-comp-weapons>div+div{border-left:0;border-top:1px solid var(--line-soft)}}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

for needle in ['Covenant Compendium','compendiumLedgerMarkup(state)','chaseWeapon: encounter?.chase?.name','data-ledger-view="compendium"','tc-ledger-screen','animation:none!important']:
    if needle not in s:
        raise SystemExit('compendium invariant missing: '+needle)

p.write_text(s)
