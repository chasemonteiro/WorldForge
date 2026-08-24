from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

css = r'''
/* --- Screen-based Covenant UI --- */
.app-shell{max-width:760px;padding:16px 14px calc(86px + env(safe-area-inset-bottom))}
.site-header.compact{display:none}
.tc-screen{min-height:calc(100svh - 110px);animation:tcIn .22s ease-out}
@keyframes tcIn{from{opacity:.35;transform:translateY(5px)}to{opacity:1;transform:none}}
.tc-topline{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:2px 0 15px}
.tc-brand-small{font:800 8px/1 system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:var(--gold)}
.tc-sync{font:750 8px/1 system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--ash)}
.tc-title{font-size:clamp(35px,10vw,49px);line-height:.92;text-align:center;font-weight:400;margin:16px auto 7px;max-width:450px}
.tc-subtitle{text-align:center;color:var(--gold);font:800 9px/1.2 system-ui,sans-serif;letter-spacing:.17em;text-transform:uppercase;margin-bottom:22px}
.tc-rune{width:104px;height:104px;border:1px solid rgba(198,161,90,.22);border-radius:50%;margin:-1px auto -72px;opacity:.55;position:relative;pointer-events:none;box-shadow:inset 0 0 30px rgba(198,161,90,.07),0 0 36px rgba(198,161,90,.05)}
.tc-rune:before,.tc-rune:after{content:"";position:absolute;inset:18px;border:1px solid rgba(198,161,90,.28);transform:rotate(45deg)}.tc-rune:after{inset:31px;border-radius:50%;transform:none}
.tc-panel{border:1px solid rgba(198,161,90,.18);background:linear-gradient(145deg,rgba(24,21,15,.84),rgba(10,9,7,.66));box-shadow:inset 0 1px rgba(255,255,255,.015);padding:14px;margin:10px 0}
.tc-panel.soft{border-color:var(--line-soft)}
.tc-kicker{font:800 8px/1.2 system-ui,sans-serif;letter-spacing:.15em;text-transform:uppercase;color:var(--ash);margin-bottom:6px}.tc-kicker.gold{color:var(--gold)}.tc-kicker.red{color:var(--red)}.tc-kicker.violet{color:var(--violet)}
.tc-value{font-size:22px;line-height:1.08}.tc-value.big{font-size:clamp(31px,8vw,43px)}
.tc-muted{color:var(--ash);font-size:11px;line-height:1.4}.tc-italic{font-style:italic}
.tc-hub-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}.tc-hub-grid .tc-panel:first-child{grid-column:1/-1}
.tc-progress-line{height:3px;background:#242018;margin:10px 0 5px;position:relative;overflow:hidden}.tc-progress-line>span{position:absolute;inset:0 auto 0 0;background:linear-gradient(90deg,#85672f,var(--gold-bright));box-shadow:0 0 12px rgba(224,193,123,.25)}
.tc-code-row{display:flex;align-items:center;justify-content:center;gap:8px;color:var(--gold);font:800 10px/1 system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;margin:17px 0 4px}.tc-code-row button{border:0;background:transparent;color:var(--gold);font:inherit;padding:6px}
.tc-quick{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:17px}.tc-quick button{min-height:83px;border:1px solid var(--line);background:rgba(11,10,8,.75);color:var(--ink);display:grid;place-items:center;align-content:center;gap:8px;font:800 8px/1.2 system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase}.tc-icon{font-size:25px;color:var(--gold);font-family:Georgia,serif}
.tc-bottom-nav{position:fixed;z-index:30;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);height:70px;padding:5px 10px calc(5px + env(safe-area-inset-bottom));display:grid;grid-template-columns:repeat(4,1fr);background:linear-gradient(180deg,rgba(8,8,6,.88),rgba(6,6,5,.98) 28%);border-top:1px solid #2c281f;backdrop-filter:blur(12px)}
.tc-bottom-nav button{border:0;background:transparent;color:#706858;display:grid;place-items:center;align-content:center;gap:4px;font:800 7px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.07em}.tc-bottom-nav button.active{color:var(--gold-bright)}.tc-bottom-nav .nicon{font:18px/1 Georgia,serif}
.tc-brief-head{text-align:center;padding:4px 10px 13px}.tc-brief-boss{font-size:clamp(34px,10vw,48px);line-height:.98;margin:8px 0 5px}.tc-brief-region{color:var(--ash);font-size:11px}
.tc-loadouts{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line);background:rgba(14,12,9,.58)}.tc-loadout{padding:13px;min-width:0}.tc-loadout+.tc-loadout{border-left:1px solid var(--line)}.tc-loadout-name{font-size:20px;line-height:1.05;margin:6px 0 8px}.tc-mini-stat{display:grid;grid-template-columns:48px 1fr;gap:5px;margin:3px 0;font-size:9px;color:#bbb19f}.tc-mini-stat b{font:800 7px/1.3 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.06em;color:#6f6759}
.tc-feature{padding:15px 14px;margin:10px 0;border:1px solid}.tc-feature.chaos{border-color:rgba(201,102,90,.38);background:radial-gradient(circle at 10% 50%,rgba(135,43,34,.20),transparent 45%),rgba(41,15,12,.26)}.tc-feature.rite{border-color:rgba(151,128,173,.35);background:radial-gradient(circle at 10% 50%,rgba(89,62,113,.20),transparent 45%),rgba(28,20,37,.34)}.tc-feature-title{font-size:19px;margin:6px 0 5px}.tc-feature-text{font-size:11px;color:#c9c0af;line-height:1.4}.tc-feature-row{display:grid;grid-template-columns:38px 1fr;gap:10px;align-items:center}.tc-feature-glyph{font-size:27px;text-align:center}.chaos .tc-feature-glyph{color:var(--red)}.rite .tc-feature-glyph{color:var(--violet)}
.tc-seal-inline{border:0;background:transparent;color:var(--red);padding:8px 0 0;font:800 8px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.1em}.tc-actions-3{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:7px}.tc-actions-3 .btn{padding:8px 5px;font-size:8px}
.tc-penalty-summary{margin:9px 0;border-top:1px solid rgba(201,102,90,.24);padding-top:9px}.tc-penalty-summary summary{color:var(--red);cursor:pointer;font:800 8px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em}
.tc-ledger-head{display:flex;align-items:flex-end;justify-content:space-between;gap:10px;margin:8px 0 15px}.tc-ledger-count{font-size:34px;color:var(--gold-bright)}.tc-rem-grid{display:grid;grid-template-columns:1fr;gap:6px}.tc-rem{display:flex;justify-content:space-between;gap:12px;padding:10px 9px;border-bottom:1px solid var(--line-soft);font-size:11px}.tc-rem.done{color:#bfa96e}.tc-rem .stamp{font:800 8px/1 system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#5f594e}.tc-rem.done .stamp{color:var(--gold)}
.tc-region-list{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px}.tc-region-chip{padding:9px;border:1px solid var(--line-soft);font-size:10px;color:var(--ash)}.tc-region-chip.done{border-color:rgba(198,161,90,.30);color:var(--ink)}
.tc-settings-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:13px 2px;border-bottom:1px solid var(--line-soft)}.tc-settings-row .lefty{min-width:0}.tc-settings-row .name{font:800 8px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em;color:var(--ash)}.tc-settings-row .desc{font-size:12px;margin-top:4px}.tc-settings-row.danger .name,.tc-settings-row.danger .desc{color:var(--red)}
.tc-travel-hero{text-align:center;padding:10px 0 4px}.tc-conquered{font:800 9px/1 system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin-bottom:7px}.tc-travel-region{font-size:31px;line-height:1.04}.tc-travel-sigil{width:96px;height:96px;border-radius:50%;border:1px solid rgba(224,193,123,.35);margin:17px auto;background:radial-gradient(circle,rgba(224,193,123,.30),rgba(139,103,44,.08) 42%,transparent 67%);box-shadow:0 0 45px rgba(213,166,73,.12);position:relative}.tc-travel-sigil:before,.tc-travel-sigil:after{content:"";position:absolute;inset:19px;border:1px solid rgba(224,193,123,.55);transform:rotate(45deg)}.tc-travel-sigil:after{inset:32px;border-radius:50%;transform:none}
.tc-paths{display:grid;gap:9px}.tc-path{position:relative;overflow:hidden;min-height:76px;border:1px solid rgba(198,161,90,.25);background:#12110e;color:var(--ink);padding:0;text-align:left}.tc-path-art{position:absolute;inset:0;opacity:.68}.tc-path-art svg{width:100%;height:100%;display:block}.tc-path-copy{position:relative;z-index:2;padding:15px 16px;background:linear-gradient(90deg,rgba(7,7,6,.90),rgba(7,7,6,.36) 72%,transparent)}.tc-path-name{font-size:20px;line-height:1.05}.tc-path-meta{font-size:9px;color:#b9af9d;margin-top:5px;font-style:italic}
.tc-overlay{position:fixed;z-index:80;inset:0;background:rgba(3,3,3,.82);backdrop-filter:blur(7px);display:grid;align-items:end;padding:18px 12px calc(20px + env(safe-area-inset-bottom))}.tc-sheet{width:min(620px,100%);margin:auto;background:linear-gradient(180deg,#17130f,#090806);border:1px solid #4a3e2b;padding:18px;box-shadow:0 -10px 60px rgba(0,0,0,.55)}
.tc-reveal{min-height:calc(100svh - 105px);display:grid;align-content:center;text-align:center}.tc-reveal .decree{font:800 9px/1 system-ui,sans-serif;color:var(--gold);letter-spacing:.2em;text-transform:uppercase}.tc-reveal .new-boss{font-size:clamp(39px,11vw,56px);line-height:.95;margin:14px 0 22px}.tc-reveal-weapons{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 auto 13px;width:100%;max-width:600px}.tc-reveal-box{border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:11px 6px}.tc-reveal-box strong{display:block;font-weight:400;font-size:18px;margin-top:5px}
@media(max-width:420px){.tc-hub-grid{grid-template-columns:1fr}.tc-hub-grid .tc-panel:first-child{grid-column:auto}.tc-loadout{padding:11px 9px}.tc-mini-stat{grid-template-columns:42px 1fr}.tc-actions-3{gap:5px}.tc-actions-3 .btn{font-size:7px}.tc-region-list{grid-template-columns:1fr}.tc-path{min-height:70px}}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

# UI state variables.
needle = "let toastTimer = null;"
if needle not in s:
    raise SystemExit('toastTimer marker missing')
s = s.replace(needle, needle + "\nlet uiScreen = 'sanctuary';\nlet pendingRevealId = null;", 1)

helpers = r'''
function navMarkup(active) {
  return `<nav class="tc-bottom-nav">
    <button data-screen="sanctuary" class="${active==='sanctuary'?'active':''}"><span class="nicon">⌂</span><span>Sanctuary</span></button>
    <button data-screen="encounter" class="${active==='encounter'?'active':''}"><span class="nicon">✦</span><span>Encounter</span></button>
    <button data-screen="ledger" class="${active==='ledger'?'active':''}"><span class="nicon">▤</span><span>Ledger</span></button>
    <button data-screen="settings" class="${active==='settings'?'active':''}"><span class="nicon">⚙</span><span>Settings</span></button>
  </nav>`;
}
function bindNav() {
  document.querySelectorAll('[data-screen]').forEach(btn=>btn.addEventListener('click',()=>{
    uiScreen = btn.dataset.screen;
    pendingRevealId = null;
    renderRun();
  }));
}
function screenTop(title='The Tarnished Covenant') {
  return `<div class="tc-topline"><div class="tc-brand-small">${h(title)}</div><div class="tc-sync">${backend.mode==='shared'?'shared · synced':'local save'}</div></div>`;
}
function regionArtSvg(name) {
  const n = name.toLowerCase();
  let sky='#46505b', ground='#252b28', accent='#8a7952';
  if(n.includes('caelid')){sky='#6d3028';ground='#351b16';accent='#b66a45'}
  else if(n.includes('liurnia')){sky='#44606e';ground='#1e3035';accent='#7393a3'}
  else if(n.includes('weeping')){sky='#536052';ground='#28302a';accent='#819078'}
  else if(n.includes('gelmir')||n.includes('jagged')){sky='#6a3928';ground='#2c1c16';accent='#a36743'}
  else if(n.includes('mountain')||n.includes('haligtree')){sky='#7a8588';ground='#3e4445';accent='#b8b69b'}
  else if(n.includes('leyndell')||n.includes('altus')){sky='#756542';ground='#383022';accent='#c0a15c'}
  else if(n.includes('coast')){sky='#386574';ground='#21343c';accent='#72a0aa'}
  else if(n.includes('abyss')){sky='#524735';ground='#211e18';accent='#8c7955'}
  else if(n.includes('shadow')||n.includes('gravesite')){sky='#4d473d';ground='#25231e';accent='#82735d'}
  else if(n.includes('rauh')){sky='#4e6650';ground='#263529';accent='#81956e'}
  return `<svg viewBox="0 0 600 110" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="${sky}"/><stop offset="1" stop-color="#11100d"/></linearGradient></defs><rect width="600" height="110" fill="url(#g)"/><circle cx="495" cy="24" r="20" fill="${accent}" opacity=".32"/><path d="M0 83 L70 58 L125 76 L186 38 L235 74 L292 49 L346 81 L413 42 L470 69 L536 36 L600 70 V110 H0Z" fill="${ground}"/><path d="M390 75v-32h10v32m-26 0v-19h8v19m48 0v-24h8v24" stroke="${accent}" stroke-width="3" opacity=".45"/></svg>`;
}
function bindShare() { document.querySelector('#share')?.addEventListener('click',shareCovenant); }
function hubProgressPct(state){const req=Math.max(1,capstoneRequirement(state));return Math.min(100,Math.round((state.cleared/req)*100));}

function renderSanctuary() {
  const state=run.state,c=state.current,done=requiredRemembrances(state).filter(x=>hasRemembrance(state,x)).length,required=requiredRemembrances(state).length;
  app.innerHTML=`<section class="tc-screen">${screenTop()}
    <div class="tc-rune"></div><h1 class="tc-title">The Tarnished<br>Covenant</h1><div class="tc-subtitle">shared challenge run</div>
    <div class="tc-hub-grid">
      <div class="tc-panel"><div class="tc-kicker">current region</div><div class="tc-value">${h(state.region)}</div><div class="tc-muted" style="margin-top:7px">${state.cleared} regional ${state.cleared===1?'boss':'bosses'} defeated</div></div>
      <div class="tc-panel"><div class="tc-kicker">current target</div><div class="tc-value">${h(c?.target?.name||'Awaiting decree')}</div></div>
      <div class="tc-panel"><div class="tc-kicker">remembrances</div><div class="tc-value">${done} <span class="tc-muted">/ ${required}</span></div></div>
      <div class="tc-panel" style="grid-column:1/-1"><div class="tc-kicker">regional progress</div><div class="tc-progress-line"><span style="width:${hubProgressPct(state)}%"></span></div><div class="tc-muted">${capstoneRequirement(state)>state.cleared?`${capstoneRequirement(state)-state.cleared} more before the capstone can appear`:'capstone eligible'}</div></div>
    </div>
    <div class="tc-code-row">CODE <strong>${h(run.joinCode||'LOCAL')}</strong><button id="share">SHARE ↗</button></div>
    <div class="tc-quick"><button data-screen="encounter"><span class="tc-icon">✦</span>Encounter</button><button data-screen="ledger"><span class="tc-icon">▤</span>Ledger</button><button data-screen="settings"><span class="tc-icon">⚙</span>Settings</button></div>
  </section>${navMarkup('sanctuary')}`;
  bindNav();bindShare();
}

function compactLoadout(label,b){return `<div class="tc-loadout"><div class="tc-kicker">${label}</div><div class="tc-loadout-name">${h(b.name)}</div><div class="tc-mini-stat"><b>skill</b><span>${h(b.native)}</span></div><div class="tc-mini-stat"><b>upgrade</b><span>${h(b.upgrade)}</span></div><div class="tc-mini-stat"><b>infusion</b><span>${h(b.affinity)}</span></div><div class="tc-mini-stat"><b>job</b><span>${h(b.role)}</span></div></div>`}
function renderEncounter() {
  const state=run.state,c=state.current;
  app.innerHTML=`<section class="tc-screen">${screenTop('Encounter Briefing')}
    <div class="tc-brief-head"><div class="tc-kicker gold">${c.target.exit?'regional capstone':'current target'}</div><div class="tc-brief-boss">${h(c.target.name)}</div><div class="tc-brief-region">${h(state.region)}</div></div>
    <div class="tc-kicker gold" style="text-align:center;margin:5px 0 7px">assigned weapons</div><div class="tc-loadouts">${compactLoadout('Chase',c.chase)}${compactLoadout('Morgan',c.morgan)}</div>
    ${c.penances?.length?`<details class="tc-penalty-summary"><summary>${c.penances.length} active armament ${c.penances.length===1?'penalty':'penalties'}</summary>${penanceMarkup(c)}</details>`:''}
    <div class="tc-feature chaos"><div class="tc-feature-row"><div class="tc-feature-glyph">◉</div><div><div class="tc-kicker red">chaos</div><div class="tc-feature-text">when this happens:</div><div class="tc-feature-title">${h(c.chaosTrigger)}</div>${c.chaosTriggered?`<div class="tc-feature-text" style="color:#df8b80">${h(c.chaosConsequence)}</div>`:`<button id="triggerChaos" class="tc-seal-inline">◉ break the seal</button>`}</div></div></div>
    <div class="tc-feature rite"><div class="tc-feature-row"><div class="tc-feature-glyph">✧</div><div><div class="tc-kicker violet">odd rite</div><div class="tc-feature-title">${h(c.weirdness.name)}</div><div class="tc-feature-text">${h(c.weirdness.text)}</div></div></div></div>
    <button id="complete" class="btn gold victory">${c.target.exit?'CAPSTONE DEFEATED · CONTINUE':'VICTORY · ROLL NEXT ENCOUNTER'}</button>
    <div class="tc-actions-3"><button id="rerollChaos" class="btn ghost">Reroll Chaos</button><button id="rerollWeird" class="btn ghost">Reroll Rite</button><button id="appealOpen" class="btn curse">Weapon Appeal</button></div>
    <div id="appealConfirm"></div>
  </section>${navMarkup('encounter')}`;
  bindNav();
  document.querySelector('#triggerChaos')?.addEventListener('click',()=>commit(triggerChaos(state,playerName())));
  document.querySelector('#rerollChaos')?.addEventListener('click',()=>commit(rerollChaos(state,playerName())));
  document.querySelector('#rerollWeird')?.addEventListener('click',()=>commit(rerollWeirdness(state,playerName())));
  document.querySelector('#appealOpen')?.addEventListener('click',showAppealMenu);
  document.querySelector('#complete')?.addEventListener('click',async()=>{
    const next=completeEncounter(state,playerName());
    if(!next.regionComplete&&!next.runComplete&&next.current){pendingRevealId=next.current.id;uiScreen='encounter';}
    await commit(next);
  });
}

function showAppealMenu(){
  const c=run.state.current;
  document.body.insertAdjacentHTML('beforeend',`<div id="tcAppealOverlay" class="tc-overlay"><div class="tc-sheet"><div class="tc-kicker red">armament appeal</div><div class="tc-value" style="margin:6px 0 4px">Refuse the decree?</div><div class="tc-muted">Changing an assigned weapon creates a severe random penalty.</div><div class="tc-panel soft" style="margin-top:14px"><div class="tc-muted">CHASE</div><div>${h(c.chase.name)}</div><div class="tc-muted" style="margin-top:8px">MORGAN</div><div>${h(c.morgan.name)}</div></div><div class="tc-actions-3"><button class="btn curse" data-overlay-appeal="chase">Chase</button><button class="btn curse" data-overlay-appeal="morgan">Morgan</button><button class="btn curse" data-overlay-appeal="both">Both</button></div><button id="closeAppeal" class="btn text-btn">Cancel</button></div></div>`);
  document.querySelector('#closeAppeal').addEventListener('click',()=>document.querySelector('#tcAppealOverlay')?.remove());
  document.querySelectorAll('[data-overlay-appeal]').forEach(btn=>btn.addEventListener('click',async()=>{const which=btn.dataset.overlayAppeal;document.querySelector('#tcAppealOverlay')?.remove();await commit(changeWeapons(run.state,playerName(),which));}));
}

function renderLedger() {
  const state=run.state,req=requiredRemembrances(state),done=req.filter(x=>hasRemembrance(state,x));
  const regionNames=Object.keys(regions).filter(r=>state.includeDlc||!r.includes('· DLC')).filter(r=>r!=='The Erdtree');
  app.innerHTML=`<section class="tc-screen">${screenTop('Remembrance Ledger')}<div class="tc-ledger-head"><div><div class="tc-kicker gold">remembrances claimed</div><div class="tc-muted">The final seal opens only when the ledger is complete.</div></div><div class="tc-ledger-count">${done.length}/${req.length}</div></div>
    <div class="tc-panel"><div class="tc-rem-grid">${req.map(name=>`<div class="tc-rem ${hasRemembrance(state,name)?'done':''}"><span>${h(name)}</span><span class="stamp">${hasRemembrance(state,name)?'claimed':'missing'}</span></div>`).join('')}</div></div>
    <div class="tc-kicker gold" style="margin-top:20px">world progress</div><div class="tc-region-list">${regionNames.map(r=>`<div class="tc-region-chip ${(state.clearedRegions||[]).includes(r)?'done':''}">${h(r)}${r===state.region?' · ACTIVE':(state.clearedRegions||[]).includes(r)?' · CLEARED':''}</div>`).join('')}</div>
    <div class="tc-kicker gold" style="margin-top:22px">encounter history</div><div class="tc-panel soft">${renderHistory(state)}</div>
  </section>${navMarkup('ledger')}`;bindNav();
}

function renderSettings() {
 const state=run.state;
 app.innerHTML=`<section class="tc-screen">${screenTop('Covenant Settings')}<div class="tc-rune" style="margin:5px auto 5px"></div>
  <div class="tc-panel"><div class="tc-kicker gold">share code</div><div class="tc-value big" style="text-align:center;letter-spacing:.14em;margin:9px">${h(run.joinCode||'LOCAL')}</div><button id="share" class="btn ghost">Share Covenant</button></div>
  <div class="tc-kicker gold" style="margin-top:20px">run options</div>
  <div class="tc-settings-row"><div class="lefty"><div class="name">difficulty</div><div class="desc">${state.severity==='normal'?'Silly':state.severity==='hard'?'Maidenless':'Miyazaki Has Noticed You'}</div></div><span>›</span></div>
  <div class="tc-settings-row"><div class="lefty"><div class="name">ruleset</div><div class="desc">${state.includeDlc?'Base + Shadow of the Erdtree · All Remembrances':'Base Game · All Remembrances'}</div></div><span class="tc-muted">locked</span></div>
  <div class="tc-kicker gold" style="margin-top:22px">run management</div>
  <button id="restartRun" class="tc-settings-row danger" style="width:100%;border-left:0;border-right:0;border-top:0;background:transparent;text-align:left"><div class="lefty"><div class="name">restart covenant</div><div class="desc">Erase progress and return to the beginning.</div></div><span>↻</span></button>
  <button id="leave" class="tc-settings-row" style="width:100%;border-left:0;border-right:0;border-top:0;background:transparent;color:var(--ink);text-align:left"><div class="lefty"><div class="name">leave run</div><div class="desc">Return to the opening screen.</div></div><span>›</span></button><div id="restartConfirm"></div>
 </section>${navMarkup('settings')}`;
 bindNav();bindShare();document.querySelector('#restartRun').addEventListener('click',showRestart);document.querySelector('#leave').addEventListener('click',()=>{unsubscribe?.();run=null;clearSession();session=null;renderHome();});
}

function renderDecreeReveal(){
 const state=run.state,c=state.current;
 app.innerHTML=`<section class="tc-screen tc-reveal">${screenTop('New Decree')}<div class="decree">new decree</div><div class="new-boss">${h(c.target.name)}</div><div class="tc-reveal-weapons"><div class="tc-reveal-box"><div class="tc-kicker">Chase</div><strong>${h(c.chase.name)}</strong></div><div class="tc-reveal-box"><div class="tc-kicker">Morgan</div><strong>${h(c.morgan.name)}</strong></div></div><div class="tc-feature chaos" style="text-align:left"><div class="tc-kicker red">chaos</div><div class="tc-feature-text">${h(c.chaosTrigger)}</div></div><div class="tc-feature rite" style="text-align:left"><div class="tc-kicker violet">odd rite</div><div class="tc-feature-title">${h(c.weirdness.name)}</div><div class="tc-feature-text">${h(c.weirdness.text)}</div></div><button id="acceptDecree" class="btn gold">Accept the Decree</button></section>${navMarkup('encounter')}`;
 bindNav();document.querySelector('#acceptDecree').addEventListener('click',()=>{pendingRevealId=null;uiScreen='encounter';renderRun();});
}
'''

# Insert helpers just before renderRun.
marker = '\nfunction renderRun() {'
if marker not in s:
    raise SystemExit('renderRun marker missing')
s = s.replace(marker, '\n' + helpers + '\nfunction renderRun() {', 1)

# Replace renderRun body only.
pattern = r"function renderRun\(\) \{.*?\n\}\n\nfunction showRestart"
replacement = r'''function renderRun() {
  const state=run.state;
  setRegionTheme(state.region);
  if(state.runComplete) return renderRunComplete();
  if(state.regionComplete) return renderRegionComplete();
  if(pendingRevealId && state.current?.id===pendingRevealId) return renderDecreeReveal();
  if(uiScreen==='encounter') return renderEncounter();
  if(uiScreen==='ledger') return renderLedger();
  if(uiScreen==='settings') return renderSettings();
  return renderSanctuary();
}

function showRestart'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('renderRun replacement failed')

# Replace region complete screen with visual travel cards.
pattern = r"function renderRegionComplete\(\) \{.*?\n\}\n\nfunction renderRunComplete"
replacement = r'''function renderRegionComplete() {
  const state=run.state;setRegionTheme(state.region);
  const choices=availableNextRegions(state),missing=missingRemembrances(state),seal=finalSealOpen(state);
  app.innerHTML=`<section class="tc-screen">${screenTop('Region Complete')}<div class="tc-travel-hero"><div class="tc-conquered">region conquered</div><div class="tc-travel-region">${h(state.region)}</div><div class="tc-travel-sigil"></div></div><div class="tc-kicker gold" style="text-align:center;margin-bottom:10px">paths now open</div><div class="tc-paths">${choices.length?choices.map(r=>`<button class="tc-path" data-travel="${h(r)}"><span class="tc-path-art">${regionArtSvg(r)}</span><span class="tc-path-copy"><span class="tc-path-name">${h(r)}</span><span class="tc-path-meta">${(state.clearedRegions||[]).includes(r)?'Return · unfinished remembrance remains':'Travel here next'}</span></span></button>`).join(''):`<div class="tc-panel"><div class="tc-muted">No new path is currently open.</div></div>`}</div><div class="tc-panel" style="margin-top:17px"><div class="tc-kicker gold">remembrance ledger</div><div class="tc-value">${requiredRemembrances(state).length-missing.length} / ${requiredRemembrances(state).length}</div><div class="tc-muted" style="margin-top:6px">${seal?'The final seal is open.':'The final seal remains closed. Claim every required Remembrance.'}</div></div><button id="share" class="btn ghost">Share Covenant</button></section>${navMarkup('sanctuary')}`;
  bindNav();bindShare();document.querySelectorAll('[data-travel]').forEach(btn=>btn.addEventListener('click',()=>{const next=startNextRegion(state,playerName(),btn.dataset.travel,state.severity);uiScreen='sanctuary';pendingRevealId=null;commit(next);}));
}

function renderRunComplete'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('region complete replacement failed')

p.write_text(s)
