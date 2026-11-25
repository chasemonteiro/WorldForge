/* --- Encounter tabs in the Ledger/Forge style ---
   Decorates the existing Encounter panels in place: every original element,
   id and listener stays, so recording a world clear, appealing, recalling and
   rewriting still run their own code. Idempotent; re-applied after each render
   and whenever a decorator re-inserts its piece. */
const TC_SEAL_SIGIL='<svg viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M32 12v40"/><path d="M22 22l10-10 10 10"/><path d="M20 44h24"/></g></svg>';
function tcSentence(text){const s=String(text||'').trim().toLowerCase();return s.replace(/^\w/,m=>m.toUpperCase());}
function tcEncounterRecordLine(state,kind){
  const history=Array.isArray(state?.history)?state.history:[];if(!history.length)return '';
  if(kind==='chaos'){const n=history.filter(x=>x.chaosTriggered).length;return `Chaos has broken in ${n} of your ${history.length} fights.`;}
  const n=history.filter(x=>x.riteOutcome==='Honored').length;return `You’ve honored ${n} of ${history.length} Odd Rites.`;
}
function tcDecorateEncounterStyle(){
  const screen=app.querySelector('.tc-encounter-shell');const state=run?.state,c=state?.current;
  if(!screen||!c)return;
  screen.classList.add('tc-enc-style');
  // Top strip: quiet, sentence-case Chaos line.
  const strip=screen.querySelector('.tc-encounter-sticky span');
  if(strip&&!strip.dataset.tcStyled){strip.dataset.tcStyled='1';strip.textContent=c.chaosTrigger?`Chaos: ${tcSentence(personalizePlayers(c.chaosTrigger,state))}`:'No Chaos decree';}
  // Boss: art becomes the hero, the name sits on it.
  const boss=screen.querySelector('.tc-encounter-panel[data-panel="boss"]');
  if(boss)boss.classList.add('tc-enc-boss');
  // World seals.
  screen.querySelectorAll('.tc-world-clear-btn').forEach(btn=>{
    if(btn.dataset.tcSeal)return;btn.dataset.tcSeal='1';
    const slot=btn.dataset.worldClear,done=btn.classList.contains('done'),name=playerLabel(slot,state);
    btn.classList.add('tc-world-seal');
    btn.setAttribute('aria-label',done?`${name}’s world cleared`:`Record the victory in ${name}’s world`);
    btn.innerHTML=`<span class="tc-seal-disc">${TC_SEAL_SIGIL}</span><span class="tc-seal-name">${h(name)}’s world</span><small>${done?'Cleared':'Tap when defeated'}</small>`;
  });
  const note=screen.querySelector('.tc-world-clear-note');
  if(note&&!note.dataset.tcStyled){note.dataset.tcStyled='1';note.textContent='Beat the boss in both worlds. One reward pays out for the pair.';}
  // Weapons: cards, provenance marks, a holdings line under each action.
  const weapons=screen.querySelector('.tc-encounter-panel[data-panel="weapons"]');
  if(weapons){
    weapons.classList.add('tc-enc-weapons');
    const sm=smithingData(state),swaps=Array.isArray(c.remembranceSwaps)?c.remembranceSwaps:[];
    weapons.querySelectorAll('.tc-loadout').forEach((card,i)=>{
      if(card.dataset.tcStyled)return;card.dataset.tcStyled='1';
      const slot=i===0?'chase':'morgan',name=c[slot]?.name||'';
      const marks=[];
      if(sm.masterworks.includes(name))marks.push('<span class="tc-prov mw">⚒ Masterwork</span>');
      if(swaps.some(s=>s.slot===slot&&s.weapon===name))marks.push('<span class="tc-prov shop">From Hewg’s shop</span>');
      if(marks.length)card.querySelector('.tc-loadout-name')?.insertAdjacentHTML('afterend',`<div class="tc-prov-row">${marks.join('')}</div>`);
    });
    const summary=weapons.querySelector('.tc-penalty-summary>summary');
    if(summary&&!summary.dataset.tcStyled){summary.dataset.tcStyled='1';const n=c.penances?.length||0;summary.textContent=`${n} Appeal ${n===1?'penalty':'penalties'} in force`;}
    const appeal=weapons.querySelector('#appealOpen');
    if(appeal&&!weapons.querySelector('.tc-enc-hold.appeal')){appeal.insertAdjacentHTML('afterend',`<p class="tc-enc-hold appeal">${sm.appealWaivers?`You hold ${sm.appealWaivers} Appeal ${sm.appealWaivers===1?'Waiver':'Waivers'}${sm.jointAppeals?` and ${sm.jointAppeals} Joint ${sm.jointAppeals===1?'Appeal':'Appeals'}`:''}.`:'No Appeal Waivers held, so an Appeal carries a penalty.'}</p>`);}
    const recall=weapons.querySelector('[data-open-weapon-recall]');
    if(recall&&!recall.dataset.tcStyled){recall.dataset.tcStyled='1';const n=Number((recall.textContent.match(/(\d+)\s*$/)||[])[1]||0);recall.textContent='Masterwork Recall';recall.insertAdjacentHTML('afterend',`<p class="tc-enc-hold">${n?`${n} of your Masterworks ${n===1?'is':'are'} ready to recall.`:'No Masterworks ready to recall.'}</p>`);if(!n)recall.disabled=true;}
  }
  // Chaos and Rite: reserve becomes a Satchel card, plus a line from the record.
  [['chaos','Chaos Refresh','chaosRefreshes','Rewrite the Chaos decree. Costs 1 Refresh.'],['rite','Rite Refresh','riteRefreshes','Rewrite the Odd Rite. Costs 1 Refresh.']].forEach(([kind,label,key,line])=>{
    const panel=screen.querySelector(`.tc-encounter-panel[data-panel="${kind}"]`);if(!panel)return;
    panel.classList.add('tc-enc-feature');
    const reserve=panel.querySelector('.tc-panel-refresh');
    if(reserve&&!reserve.dataset.tcStyled){
      reserve.dataset.tcStyled='1';reserve.classList.add('tc-satchel-card','here');
      const count=Number(smithingData(state)[key]||0);
      const kicker=reserve.querySelector('.tc-kicker');
      const top=document.createElement('div');top.className='tc-satchel-top';
      top.innerHTML=`<span class="tc-forge-seal">${typeof tcSatchelSigil==='function'?tcSatchelSigil(kind):''}<b>${count}</b></span><div><strong>${label}</strong><p>${line}</p></div>`;
      if(kicker)kicker.replaceWith(top);else reserve.prepend(top);
      const btn=reserve.querySelector('[data-use-boon]');
      if(btn){btn.classList.add('tc-satchel-act');btn.textContent=kind==='chaos'?'Rewrite the decree':'Rewrite the Rite';}
    }
    if(!panel.querySelector('.tc-enc-record')){
      const text=tcEncounterRecordLine(state,kind);
      if(text)panel.insertAdjacentHTML('beforeend',`<p class="tc-enc-record">${h(text)}</p>`);
    }
  });
}
const tcRenderEncounterBeforeStyle=renderEncounter;
renderEncounter=function(){tcRenderEncounterBeforeStyle();try{tcDecorateEncounterStyle();}catch(error){console.warn('Encounter style skipped',error);}};
if(!window.__tcEncStyleBound){
  window.__tcEncStyleBound=true;
  let queued=false;
  const run_=()=>{queued=false;try{tcDecorateEncounterStyle();}catch(error){console.warn('Encounter style skipped',error);}};
  const start=()=>new MutationObserver(()=>{if(queued||!app.querySelector('.tc-encounter-shell'))return;queued=true;requestAnimationFrame(run_);}).observe(document.body,{childList:true,subtree:true});
  if(document.body)start();else document.addEventListener('DOMContentLoaded',start);
}
/* --- End Encounter style --- */
