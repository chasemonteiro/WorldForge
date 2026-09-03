from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# 1) Smithing Favor becomes mandatory corporate paperwork once an affordable,
# accessible Bell Bearing contract exists. Reviewing the contract is mandatory;
# completing its in-game task is not an app lock.
# -----------------------------------------------------------------------------
marker='function renderRun() {'
if marker not in s:
    raise SystemExit('renderRun marker missing')
corp_helpers=r'''
function tcCorporateContractEligible(state){
  if(!state || state.runComplete || state.regionComplete)return null;
  const sm=smithingData(state);
  if(sm.activeContract)return null;
  const pool=availableBellBearings(state).filter(b=>sm.favor>=smithingContractCost(b));
  if(!pool.length)return null;
  return pool[0];
}
function renderCorporateNotice(){
  const state=run.state,b=tcCorporateContractEligible(state);
  if(!b)return renderRun();
  const sm=smithingData(state),cost=smithingContractCost(b);
  app.innerHTML=`<section class="tc-corporate-screen">
    <div class="tc-corp-paperclip">↳</div>
    <div class="tc-kicker red">ACTION REQUIRED · UPPER MANAGEMENT</div>
    <div class="tc-corp-subject">Corporate has forwarded a matter.</div>
    <div class="tc-corp-rule"></div>
    <p>Recent performance has attracted attention. This was avoidable.</p>
    <div class="tc-corp-forward"><span>FORWARDED TO</span><strong>THE TWIN MAIDEN HUSKS</strong></div>
    <div class="tc-corp-contract"><div class="tc-kicker ember">mandatory development opportunity</div><strong>${h(b.name)}</strong><span>${h(b.region)} · ${cost} Smithing Favor</span></div>
    <p class="tc-corp-fine">Review is mandatory before further Covenant activity. Hewg has been CC’d.</p>
    <button id="tcReviewCorporate" class="btn gold">REVIEW MANDATORY CONTRACT</button>
  </section>`;
  document.querySelector('#tcReviewCorporate')?.addEventListener('click',tcAcceptCorporateContract);
}
async function tcAcceptCorporateContract(){
  if(window.__tcCorporateBusy)return;
  const next=commissionSmithingContract(run.state);
  if(!next)return setToast('Corporate appears to have lost the paperwork.');
  window.__tcCorporateBusy=true;
  const btn=document.querySelector('#tcReviewCorporate');if(btn){btn.disabled=true;btn.textContent='Forwarding to Hewg…';}
  try{
    const ok=await commit(next,{successToast:'Contract issued. Upper management considers this resolved.'});
    if(ok!==false)setTimeout(()=>{try{renderSmithingContract();}catch(error){console.error(error);}},40);
  }finally{window.__tcCorporateBusy=false;}
}
'''
s=s.replace(marker,corp_helpers+'\n'+marker,1)

# Intercept normal run rendering only after reward/report transient screens have resolved.
needle="""function renderRun() {
  const state=run.state;
  if(pendingRewardReveal?.rewards?.length) return renderRewardMachine();
  if(postBattleReport?.encounterId===state.current?.id) return renderPostBattleReport();"""
replacement="""function renderRun() {
  const state=run.state;
  if(pendingRewardReveal?.rewards?.length) return renderRewardMachine();
  if(postBattleReport?.encounterId===state.current?.id) return renderPostBattleReport();
  if(tcCorporateContractEligible(state)) return renderCorporateNotice();"""
if needle not in s:
    raise SystemExit('renderRun corporate insertion target missing')
s=s.replace(needle,replacement,1)

# -----------------------------------------------------------------------------
# 2) Encounter UI: horizontal full-height panels instead of one long document.
# Boss + Chaos trigger remain visible in a compact sticky header; actions remain
# visible in a bottom dock. Text is not reduced.
# -----------------------------------------------------------------------------
start=s.find('function renderEncounter() {')
end=s.find('\nfunction showAppealMenu(){',start)
if start<0 or end<0:
    raise SystemExit('renderEncounter block missing')
encounter=r'''function renderEncounter() {
  const state=run.state,c=state.current;
  const chaosSummary=personalizePlayers(c.chaosTrigger||'Chaos pending',state);
  app.innerHTML=`<section class="tc-encounter-shell">
    <header class="tc-encounter-sticky">
      <div><div class="tc-kicker gold">${c.target.exit?'REGIONAL CAPSTONE':'CURRENT TARGET'} · ${h(state.region)}</div><div class="tc-encounter-boss">${h(c.target.name)}</div></div>
      <div class="tc-encounter-chaosline"><span>◉</span>${h(chaosSummary)}</div>
    </header>
    <nav class="tc-panel-tabs" aria-label="Encounter sections">
      <button data-enc-panel="0" class="active">Boss</button><button data-enc-panel="1">Weapons</button><button data-enc-panel="2">Chaos</button><button data-enc-panel="3">Rite</button>
    </nav>
    <div class="tc-encounter-deck" id="tcEncounterDeck">
      <article class="tc-enc-panel" data-panel-index="0">
        <div class="tc-boss-art tc-photo tc-panel-art" style="background-image:linear-gradient(180deg,rgba(4,3,2,.08),rgba(5,4,3,.72)),url('${actualRegionImage(state.region)}')"></div>
        <div class="tc-panel-content">
          <div class="tc-kicker gold">${c.target.exit?'capstone briefing':'encounter briefing'}</div>
          <div class="tc-panel-hero">${h(c.target.name)}</div>
          ${c.covenantDebt?`<div class="tc-feature debt"><div class="tc-kicker red">COVENANT DEBT · THIS ENCOUNTER</div><div class="tc-feature-title">${h(c.covenantDebt)}</div></div>`:''}
          ${c.target.exit&&!state.capstoneDeferUsed&&state.region!=='The Erdtree'?`<div class="tc-capstone-mini"><div><div class="tc-kicker red">one-time regional deferral</div><p>One normal encounter first. Its Chaos is guaranteed late-tier. Then the capstone returns to RNG.</p></div><button id="deferCapstone" class="btn curse">DEFER ONCE · ACCEPT DEBT</button></div>`:''}
          ${c.penances?.length?`<details class="tc-penalty-summary"><summary>${c.penances.length} active armament ${c.penances.length===1?'penalty':'penalties'}</summary>${penanceMarkup(c)}</details>`:''}
        </div>
      </article>
      <article class="tc-enc-panel" data-panel-index="1">
        <div class="tc-panel-content"><div class="tc-kicker gold">assigned armaments</div><div class="tc-panel-hero small">The loadout corporate approved.</div><div class="tc-loadouts tc-loadouts-panel">${compactLoadout(playerLabel('chase',state),c.chase)}${compactLoadout(playerLabel('morgan',state),c.morgan)}</div></div>
      </article>
      <article class="tc-enc-panel" data-panel-index="2">
        <div class="tc-panel-content"><div class="tc-kicker red">chaos decree</div><div class="tc-panel-hero small">When this happens:</div><div class="tc-chaos-trigger-large">${h(chaosSummary)}</div>
        ${c.chaosTriggered?`<div class="tc-chaos-active"><div class="tc-kicker red">SEAL BROKEN</div><div class="tc-feature-title">${h(personalizePlayers(c.chaosConsequence,state))}</div></div>`:`<button id="triggerChaos" class="tc-seal-panel"><span>◉</span>BREAK THE SEAL</button>`}
        <div class="tc-panel-boons">${tcEncounterBoons(state)}</div></div>
      </article>
      <article class="tc-enc-panel" data-panel-index="3">
        <div class="tc-panel-content"><div class="tc-kicker violet">${h(c.weirdness?.tier||'True')} rite</div><div class="tc-panel-hero">${h(c.weirdness.name)}</div><div class="tc-rite-copy">${h(c.weirdness.text)}</div><div class="tc-panel-boons">${tcEncounterBoons(state)}</div></div>
      </article>
    </div>
    <div class="tc-encounter-dots"><span class="active"></span><span></span><span></span><span></span></div>
    <div class="tc-action-dock">
      <button id="appealOpen" class="btn curse small">Weapon Appeal</button>
      <button id="complete" class="btn gold">${c.target.exit?'CAPSTONE DEFEATED':'VICTORY'}</button>
    </div>
    ${navMarkup('encounter')}
  </section>`;
  bindNav();
  const deck=document.querySelector('#tcEncounterDeck'),tabs=[...document.querySelectorAll('[data-enc-panel]')],dots=[...document.querySelectorAll('.tc-encounter-dots span')];
  const setPanel=i=>{tabs.forEach((b,j)=>b.classList.toggle('active',j===i));dots.forEach((d,j)=>d.classList.toggle('active',j===i));};
  tabs.forEach(btn=>btn.addEventListener('click',()=>{const i=Number(btn.dataset.encPanel);deck?.scrollTo({left:(deck.clientWidth||1)*i,behavior:'smooth'});setPanel(i);}));
  let scrollTimer;deck?.addEventListener('scroll',()=>{clearTimeout(scrollTimer);scrollTimer=setTimeout(()=>{const i=Math.round(deck.scrollLeft/(deck.clientWidth||1));setPanel(Math.max(0,Math.min(3,i)));},60);},{passive:true});
  document.querySelector('#deferCapstone')?.addEventListener('click',tcDeferCapstone);
  document.querySelector('#triggerChaos')?.addEventListener('click',()=>commit(triggerChaos(state,playerName())));
  document.querySelector('#appealOpen')?.addEventListener('click',showAppealMenu);
  document.querySelector('#complete')?.addEventListener('click',()=>{postBattleReport={encounterId:c.id,rite:null,chaos:null};renderPostBattleReport();});
}'''
s=s[:start]+encounter+s[end:]

# -----------------------------------------------------------------------------
# 3) Post-battle becomes a short staged flow: Rite -> Chaos -> file report.
# -----------------------------------------------------------------------------
marker='function showAppealMenu(){'
if marker not in s:
    raise SystemExit('showAppealMenu marker missing')
postbattle=r'''
function renderPostBattleReport(){
  const state=run.state,c=state.current;
  if(!c){postBattleReport=null;return renderRun();}
  if(!postBattleReport||postBattleReport.encounterId!==c.id)postBattleReport={encounterId:c.id,rite:null,chaos:null};
  const riteDraws=Number(c.weirdness?.favor??1),chaosDraws=Number(c.chaosFavor??1),chaosAvailable=Boolean(c.chaosTriggered);
  let step='rite';
  if(postBattleReport.rite!==null)step=chaosAvailable&&postBattleReport.chaos===null?'chaos':'summary';
  const draws=(postBattleReport.rite===true&&!c.riteForfeited?Math.max(0,riteDraws):0)+(postBattleReport.chaos===true&&!c.chaosForfeited?Math.max(0,chaosDraws):0);
  const detail=step==='rite'?`${c.weirdness?.name||'Odd Rite'} · ${c.weirdness?.text||''}`:step==='chaos'?`${chaosEventName(c.chaosConsequence||'Chaos')} · ${personalizePlayers(c.chaosConsequence||'',state)}`:'';
  app.innerHTML=`<section class="tc-report-flow">
    <div class="tc-report-progress"><span class="done">1</span><i></i><span class="${step!=='rite'?'done':''}">2</span><i></i><span class="${step==='summary'?'done':''}">3</span></div>
    <div class="tc-report-kicker">Encounter Complete</div><div class="tc-report-victory">VICTORY</div><div class="tc-report-boss">${h(c.target?.name||'Enemy Felled')}</div>
    ${step==='rite'?`<div class="tc-report-stage"><div class="tc-kicker violet">STEP 1 · ODD RITE</div><div class="tc-report-question">Was the Rite honored?</div><div class="tc-report-stage-copy">${h(detail)}</div><div class="tc-report-bigchoices"><button data-report-kind="rite" data-report-value="1">HONORED</button><button data-report-kind="rite" data-report-value="0">FAILED</button></div></div>`:''}
    ${step==='chaos'?`<div class="tc-report-stage"><div class="tc-kicker red">STEP 2 · CHAOS</div><div class="tc-report-question">Was the decree endured?</div><div class="tc-report-stage-copy">${h(detail)}</div><div class="tc-report-bigchoices"><button data-report-kind="chaos" data-report-value="1">ENDURED</button><button data-report-kind="chaos" data-report-value="0">FAILED</button></div></div>`:''}
    ${step==='summary'?`<div class="tc-report-stage summary"><div class="tc-kicker gold">FILE REPORT</div><div class="tc-report-question">The paperwork is complete.</div><div class="tc-report-summary-grid"><div><span>RITE</span><strong>${c.riteForfeited?'FORFEITED':postBattleReport.rite?'HONORED':'FAILED'}</strong></div><div><span>CHAOS</span><strong>${c.chaosForfeited?'FORFEITED':!chaosAvailable?'NOT TRIGGERED':postBattleReport.chaos?'ENDURED':'FAILED'}</strong></div><div><span>REWARD DRAWS</span><strong>${draws}</strong></div></div><button id="finishBattleReport" class="btn gold">${c.target?.exit?'RECORD VICTORY · DRAW REWARDS':'RECORD VICTORY · DRAW REWARDS & ROLL NEXT'}</button></div>`:''}
  </section>`;
  document.querySelectorAll('[data-report-kind]').forEach(btn=>btn.addEventListener('click',()=>postBattleChoice(btn.dataset.reportKind,btn.dataset.reportValue==='1')));
  document.querySelector('#finishBattleReport')?.addEventListener('click',finalizePostBattleReport);
  if(step==='chaos'&&!chaosAvailable){postBattleReport.chaos=false;renderPostBattleReport();}
}
'''
s=s.replace(marker,postbattle+'\n'+marker,1)

# -----------------------------------------------------------------------------
# 4) Compendium becomes a region-chapter chronicle. The list is an illustrated
# table of contents; tapping a boss opens a full-page archival record.
# -----------------------------------------------------------------------------
marker='function renderLedger() {'
if marker not in s:
    raise SystemExit('renderLedger marker missing')
compendium=r'''
function tcChronicleFlavor(entry){
  const pool=['Filed under: avoidable administrative violence.','Witnessed, documented, and unlikely to improve morale.','The Covenant considers this a successful use of company time.','Nobody asked whether this was a good idea.','Upper management has retained the incident for training purposes.'];
  let seed=0;for(const ch of String(entry?.name||''))seed=(seed+ch.charCodeAt(0))%pool.length;return pool[seed];
}
function tcChronicleRegions(state){
  const entries=Array.isArray(state.history)?state.history:[],groups=[];
  for(const entry of entries){let g=groups.find(x=>x.region===(entry.region||'Earlier Run'));if(!g){g={region:entry.region||'Earlier Run',entries:[]};groups.push(g);}g.entries.push(entry);}
  return groups;
}
function tcChronicleEntryButton(entry,index,state){
  return `<button class="tc-chronicle-entry ${entry.exit?'capstone':''}" data-comp-entry="${index}"><span class="tc-chronicle-entry-num">${String(index+1).padStart(2,'0')}</span><span><strong>${h(entry.name||'Unknown foe')}</strong><em>${h(entry.chaseWeapon||'Unknown weapon')} × ${h(entry.morganWeapon||'Unknown weapon')}</em></span><b>${entry.exit?'◆':'›'}</b></button>`;
}
function compendiumLedgerMarkup(state){
  const entries=Array.isArray(state.history)?state.history:[];
  if(!entries.length)return `<div class="tc-comp-empty"><div class="tc-comp-empty-glyph">◇</div><div class="tc-value">The pages are still clean.</div><div class="tc-muted">This condition will not survive first contact with a boss.</div></div>`;
  const groups=tcChronicleRegions(state),chaos=entries.filter(x=>x.chaosTriggered).length,forfeits=entries.filter(x=>x.riteOutcome==='Forfeited'||x.chaosOutcome==='Forfeited').length;
  return `<div class="tc-chronicle-frontispiece"><div class="tc-chronicle-sigil">✦</div><div class="tc-kicker gold">THE TARNISHED COVENANT</div><div class="tc-chronicle-title">A Chronicle of Poor Decisions</div><div class="tc-chronicle-rule"></div><div class="tc-chronicle-stats"><span><strong>${entries.length}</strong> enemies felled</span><span><strong>${chaos}</strong> Chaos events</span><span><strong>${forfeits}</strong> boons forfeited</span></div></div>
  <div class="tc-chronicle-book">${groups.map((g,gi)=>`<section class="tc-chronicle-chapter"><header><span>CHAPTER ${String(gi+1).padStart(2,'0')}</span><strong>${h(g.region)}</strong><em>${g.entries.length} ${g.entries.length===1?'record':'records'}</em></header><div>${g.entries.map(e=>tcChronicleEntryButton(e,entries.indexOf(e),state)).join('')}</div></section>`).join('')}</div>`;
}
function tcOpenChronicleEntry(index){
  const state=run.state,entry=(state.history||[])[Number(index)];if(!entry)return;
  const names=compendiumNames(entry,state),mods=Array.isArray(entry.penances)?entry.penances:[];
  document.querySelector('#tcChronicleOverlay')?.remove();
  document.body.insertAdjacentHTML('beforeend',`<div id="tcChronicleOverlay" class="tc-chronicle-overlay"><article class="tc-chronicle-page">
    <button id="tcCloseChronicle" class="tc-chronicle-close">×</button>
    <div class="tc-kicker gold">${entry.exit?'CAPSTONE RECORD':'FIELD RECORD'} · ${h(entry.region||'Unknown region')}</div>
    <div class="tc-chronicle-page-number">ENTRY ${String(Number(index)+1).padStart(2,'0')}</div><h2>${h(entry.name||'Unknown foe')}</h2><p class="tc-chronicle-flavor">${h(tcChronicleFlavor(entry))}</p>
    <div class="tc-chronicle-divider">✦</div>
    <section><div class="tc-kicker">ARMAMENTS CARRIED INTO BATTLE</div><div class="tc-chronicle-weapons"><div><span>${h(names.chase)}</span><strong>${h(entry.chaseWeapon||'—')}</strong><em>${h(entry.chaseBuild?.role||'')}</em></div><div><span>${h(names.morgan)}</span><strong>${h(entry.morganWeapon||'—')}</strong><em>${h(entry.morganBuild?.role||'')}</em></div></div></section>
    ${entry.oddRite?`<section class="tc-chronicle-record rite"><div class="tc-record-head"><span>RITE OBSERVED</span><b>${h(entry.riteOutcome||'RECORDED')}</b></div><strong>${h(entry.oddRite.name||'Unnamed Rite')}</strong><p>${h(entry.oddRite.text||'')}</p></section>`:''}
    <section class="tc-chronicle-record chaos"><div class="tc-record-head"><span>CHAOS RECORDED</span><b>${h(entry.chaosOutcome||(entry.chaosTriggered?'TRIGGERED':'NOT TRIGGERED'))}</b></div><strong>${h(entry.chaosTriggered?chaosEventName(entry.chaosConsequence||'Chaos'):'Seal remained intact')}</strong>${entry.chaosTriggered?`<p>${h(entry.chaosConsequence||'')}</p>`:''}</section>
    ${mods.length?`<section class="tc-chronicle-record"><div class="tc-record-head"><span>ARMAMENT PENALTIES</span><b>${mods.length}</b></div>${mods.map(m=>`<p><strong>${h(m.name||'Penalty')}</strong> · ${h(m.text||'')}</p>`).join('')}</section>`:''}
    ${Array.isArray(entry.rewards)&&entry.rewards.length?`<section class="tc-chronicle-record reward"><div class="tc-record-head"><span>REWARD ISSUED</span><b>FILED</b></div><p>${entry.rewards.map(h).join(' · ')}</p></section>`:''}
    <footer>${entry.completedBy?`Recorded by ${h(entry.completedBy)}`:'Victory recorded'}${entry.completedAt?` · ${h(compendiumDate(entry.completedAt))}`:''}</footer>
  </article></div>`);
  document.querySelector('#tcCloseChronicle')?.addEventListener('click',()=>document.querySelector('#tcChronicleOverlay')?.remove());
}
if(!window.__tcChronicleBound){window.__tcChronicleBound=true;document.addEventListener('click',e=>{const b=e.target.closest('[data-comp-entry]');if(b)tcOpenChronicleEntry(b.dataset.compEntry);});}
'''
s=s.replace(marker,compendium+'\n'+marker,1)

# -----------------------------------------------------------------------------
# Styles for all three systems.
# -----------------------------------------------------------------------------
css=r'''
/* --- mandatory corporate smithing notice --- */
.tc-corporate-screen{min-height:calc(100dvh - 42px);max-width:620px;margin:auto;display:flex;flex-direction:column;justify-content:center;padding:24px 10px 90px;position:relative}.tc-corp-paperclip{position:absolute;right:14px;top:18px;font-size:34px;color:#655b49;transform:rotate(24deg)}.tc-corp-subject{font:400 clamp(34px,10vw,52px)/.98 Georgia,serif;margin:10px 0 14px}.tc-corp-rule{height:1px;background:linear-gradient(90deg,var(--red),transparent);margin-bottom:15px}.tc-corporate-screen>p{font-size:16px;line-height:1.5;color:#c9c0af}.tc-corp-forward{margin:14px 0;border:1px solid var(--line);padding:12px;background:rgba(16,14,10,.64)}.tc-corp-forward span,.tc-corp-contract span{display:block;font:800 8px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.12em;color:var(--ash)}.tc-corp-forward strong{display:block;margin-top:5px;font-size:18px;font-weight:400}.tc-corp-contract{padding:16px 0;border-top:1px solid rgba(198,161,90,.24);border-bottom:1px solid rgba(198,161,90,.24)}.tc-corp-contract>strong{display:block;font-size:25px;font-weight:400;margin:6px 0}.tc-corp-fine{font-style:italic;color:var(--ash)!important;font-size:13px!important}.tc-corporate-screen .btn{margin-top:14px;min-height:58px}

/* --- swipe-first encounter --- */
.tc-encounter-shell{height:100dvh;max-height:100dvh;overflow:hidden;display:grid;grid-template-rows:auto auto minmax(0,1fr) auto auto auto;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom)}.tc-encounter-sticky{padding:10px 14px 8px;background:rgba(8,8,6,.96);border-bottom:1px solid var(--line);z-index:5}.tc-encounter-boss{font-size:clamp(25px,7vw,34px);line-height:1.02;margin-top:3px}.tc-encounter-chaosline{margin-top:7px;padding-top:7px;border-top:1px solid var(--line-soft);font:800 10px/1.3 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.04em;color:#c9b8a4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.tc-encounter-chaosline span{color:var(--red);margin-right:7px}.tc-panel-tabs{display:grid;grid-template-columns:repeat(4,1fr);background:#0b0a08;border-bottom:1px solid var(--line)}.tc-panel-tabs button{border:0;background:transparent;color:var(--ash);min-height:38px;font:800 8px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em}.tc-panel-tabs button.active{color:var(--gold-bright);border-bottom:2px solid var(--gold)}.tc-encounter-deck{display:flex;overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;scrollbar-width:none;-webkit-overflow-scrolling:touch}.tc-encounter-deck::-webkit-scrollbar{display:none}.tc-enc-panel{flex:0 0 100%;width:100%;height:100%;scroll-snap-align:start;overflow-y:auto;overscroll-behavior:contain;padding:0 14px 16px}.tc-panel-art{height:clamp(120px,24vh,210px);margin:0 -14px 13px}.tc-panel-content{max-width:720px;margin:auto;padding-top:14px}.tc-panel-hero{font:400 clamp(30px,9vw,46px)/1 Georgia,serif;margin:7px 0 16px}.tc-panel-hero.small{font-size:clamp(25px,7vw,34px)}.tc-loadouts-panel{grid-template-columns:1fr 1fr;border:1px solid var(--line-soft)}.tc-chaos-trigger-large{font-size:clamp(24px,7vw,36px);line-height:1.12;margin:18px 0;color:#e4d9c5}.tc-chaos-active{padding:16px;border:1px solid rgba(201,102,90,.42);background:rgba(95,28,22,.12)}.tc-seal-panel{width:100%;min-height:110px;border:1px solid rgba(201,102,90,.5);background:radial-gradient(circle,rgba(105,29,23,.18),transparent 70%);color:var(--red);font:800 11px/1.2 system-ui,sans-serif;letter-spacing:.12em}.tc-seal-panel span{display:block;font:38px/1 Georgia,serif;margin-bottom:8px}.tc-rite-copy{font-size:18px;line-height:1.52;color:#d5cbbb}.tc-panel-boons{margin-top:17px}.tc-capstone-mini{padding:12px 0;border-top:1px solid rgba(201,102,90,.3);border-bottom:1px solid rgba(201,102,90,.25)}.tc-capstone-mini p{font-size:14px;line-height:1.42;color:#c8beac}.tc-encounter-dots{display:flex;justify-content:center;gap:6px;padding:6px 0;background:#080806}.tc-encounter-dots span{width:5px;height:5px;border-radius:50%;background:#4b4437}.tc-encounter-dots span.active{background:var(--gold-bright);box-shadow:0 0 8px rgba(224,193,123,.4)}.tc-action-dock{display:grid;grid-template-columns:.42fr 1fr;gap:7px;padding:7px 12px;background:rgba(8,8,6,.98);border-top:1px solid var(--line)}.tc-action-dock .btn{min-height:48px}.tc-encounter-shell .tc-bottom-nav{position:relative;bottom:auto;left:auto;right:auto}

/* --- staged battle report --- */
.tc-report-flow{min-height:100dvh;max-width:660px;margin:auto;padding:calc(env(safe-area-inset-top) + 16px) 16px calc(env(safe-area-inset-bottom) + 26px);display:flex;flex-direction:column;justify-content:center;text-align:center}.tc-report-progress{display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:17px}.tc-report-progress span{width:25px;height:25px;border:1px solid var(--line);border-radius:50%;display:grid;place-items:center;font:800 9px/1 system-ui,sans-serif;color:var(--ash)}.tc-report-progress span.done{color:#17120a;background:var(--gold);border-color:var(--gold)}.tc-report-progress i{width:36px;height:1px;background:var(--line)}.tc-report-stage{margin-top:18px;text-align:left;padding:17px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:rgba(15,13,10,.5)}.tc-report-question{font-size:28px;line-height:1.04;margin:7px 0}.tc-report-stage-copy{font-size:15px;line-height:1.45;color:#c8beac}.tc-report-bigchoices{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:17px}.tc-report-bigchoices button{min-height:58px;border:1px solid var(--line);background:#12100c;color:var(--ink);font:800 10px/1 system-ui,sans-serif;letter-spacing:.08em}.tc-report-bigchoices button:first-child{border-color:rgba(198,161,90,.55);color:var(--gold-bright)}.tc-report-summary-grid{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--line);margin:15px 0}.tc-report-summary-grid>div{padding:12px 5px;border-right:1px solid var(--line)}.tc-report-summary-grid>div:last-child{border-right:0}.tc-report-summary-grid span{display:block;font:800 7px/1.2 system-ui,sans-serif;color:var(--ash);letter-spacing:.08em}.tc-report-summary-grid strong{display:block;margin-top:5px;font-size:14px;font-weight:400;color:var(--gold-bright)}

/* --- chronicle compendium --- */
.tc-chronicle-frontispiece{text-align:center;padding:24px 12px 28px;margin:4px 0 18px;border-top:1px solid rgba(198,161,90,.22);border-bottom:1px solid rgba(198,161,90,.22);background:radial-gradient(ellipse,rgba(198,161,90,.07),transparent 66%)}.tc-chronicle-sigil{font-size:34px;color:var(--gold);margin-bottom:8px}.tc-chronicle-title{font:400 clamp(31px,9vw,44px)/1 Georgia,serif;margin:7px auto;max-width:520px}.tc-chronicle-rule{width:90px;height:1px;background:var(--gold);margin:15px auto;opacity:.55}.tc-chronicle-stats{display:flex;justify-content:center;flex-wrap:wrap;gap:8px 18px;color:var(--ash);font-size:12px;font-style:italic}.tc-chronicle-stats strong{color:var(--gold-bright);font-size:18px;font-weight:400;margin-right:3px}.tc-chronicle-book{display:grid;gap:18px}.tc-chronicle-chapter{border-left:1px solid rgba(198,161,90,.26);padding-left:11px}.tc-chronicle-chapter>header{padding:0 2px 9px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:auto 1fr auto;align-items:baseline;gap:9px}.tc-chronicle-chapter>header span{font:800 7px/1 system-ui,sans-serif;letter-spacing:.12em;color:var(--gold)}.tc-chronicle-chapter>header strong{font-size:22px;font-weight:400}.tc-chronicle-chapter>header em{font-size:10px;color:var(--ash)}.tc-chronicle-entry{width:100%;display:grid;grid-template-columns:34px 1fr 20px;align-items:center;gap:8px;text-align:left;border:0;border-bottom:1px solid var(--line-soft);background:transparent;color:var(--ink);padding:12px 3px}.tc-chronicle-entry.capstone{background:linear-gradient(90deg,rgba(198,161,90,.07),transparent)}.tc-chronicle-entry-num{font:800 8px/1 system-ui,sans-serif;color:#6e6452}.tc-chronicle-entry strong{display:block;font-size:18px;font-weight:400;line-height:1.1}.tc-chronicle-entry em{display:block;margin-top:4px;font-size:10px;color:var(--ash);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.tc-chronicle-entry>b{color:var(--gold);font-size:14px}.tc-chronicle-overlay{position:fixed;inset:0;z-index:100;background:#080806;overflow:auto;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom)}.tc-chronicle-page{max-width:690px;min-height:100dvh;margin:auto;padding:28px 18px 48px;position:relative;background:linear-gradient(90deg,transparent,rgba(198,161,90,.025),transparent)}.tc-chronicle-close{position:fixed;right:17px;top:calc(env(safe-area-inset-top) + 12px);z-index:4;width:42px;height:42px;border:1px solid var(--line);border-radius:50%;background:#0c0b08;color:var(--ink);font-size:25px}.tc-chronicle-page-number{font:800 9px/1 system-ui,sans-serif;letter-spacing:.15em;color:var(--ash);margin-top:15px}.tc-chronicle-page h2{font:400 clamp(38px,11vw,56px)/.96 Georgia,serif;margin:8px 45px 8px 0}.tc-chronicle-flavor{font-size:14px;font-style:italic;color:var(--ash)}.tc-chronicle-divider{text-align:center;color:var(--gold);margin:22px 0}.tc-chronicle-page section{margin:15px 0}.tc-chronicle-weapons{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-top:8px}.tc-chronicle-weapons>div{padding:13px 10px}.tc-chronicle-weapons>div+div{border-left:1px solid var(--line)}.tc-chronicle-weapons span{display:block;font:800 8px/1 system-ui,sans-serif;color:var(--ash)}.tc-chronicle-weapons strong{display:block;font-size:20px;font-weight:400;margin:5px 0}.tc-chronicle-weapons em{font-size:11px;color:#938a79}.tc-chronicle-record{padding:13px 0;border-top:1px solid var(--line-soft)}.tc-record-head{display:flex;justify-content:space-between;gap:10px}.tc-record-head span,.tc-record-head b{font:800 8px/1.2 system-ui,sans-serif;letter-spacing:.09em}.tc-record-head span{color:var(--ash)}.tc-record-head b{color:var(--gold)}.tc-chronicle-record>strong{display:block;font-size:20px;font-weight:400;margin:7px 0}.tc-chronicle-record p{font-size:14px;line-height:1.5;color:#c7bdab}.tc-chronicle-record.rite .tc-record-head span{color:var(--violet)}.tc-chronicle-record.chaos .tc-record-head span{color:var(--red)}.tc-chronicle-record.reward .tc-record-head span{color:var(--gold)}.tc-chronicle-page footer{margin-top:28px;padding-top:12px;border-top:1px solid var(--line);font-size:11px;color:var(--ash);font-style:italic}
@media(max-width:430px){.tc-loadouts-panel,.tc-chronicle-weapons{grid-template-columns:1fr}.tc-loadouts-panel .tc-loadout+.tc-loadout,.tc-chronicle-weapons>div+div{border-left:0;border-top:1px solid var(--line)}.tc-report-summary-grid{grid-template-columns:1fr}.tc-report-summary-grid>div{border-right:0;border-bottom:1px solid var(--line)}.tc-report-summary-grid>div:last-child{border-bottom:0}.tc-chronicle-chapter>header{grid-template-columns:1fr auto}.tc-chronicle-chapter>header span{grid-column:1/-1}.tc-action-dock{grid-template-columns:.48fr 1fr}}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

for invariant in ['ACTION REQUIRED · UPPER MANAGEMENT','tcCorporateContractEligible','tc-encounter-deck','data-enc-panel="3"','A Chronicle of Poor Decisions','tcOpenChronicleEntry','REVIEW MANDATORY CONTRACT']:
    if invariant not in s:
        raise SystemExit('interface overhaul invariant missing: '+invariant)

p.write_text(s)
