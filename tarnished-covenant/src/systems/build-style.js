/* --- Build screen in the Ledger/Forge style ---
   build-lab.js keeps every field, id, listener and the autosave. This layer only
   rearranges and redraws what it renders, and is re-applied whenever the Build
   Lab redraws a piece (MutationObserver), so it must stay idempotent.
   - Weapon: a framed plate for the AR, wrapped affinities, scaling bars, and
     gear effects as small cards.
   - Stats: Level in a seal with the level check under it; gear bonuses shown
     on the attribute they change.
   - Gear: a talisman pouch and a Physick flask. Each socket opens a slide-up,
     searchable list; picking sets the original <select> and fires its change
     event, so the Build Lab's own save and checks run as before.
   - The save bar is gone: a small status mark sits under the player tabs and a
     Save button appears only if a save fails. */
const TC_BUILD_SIGILS={
  talisman:'<circle cx="32" cy="38" r="14"/><path d="M32 24V10M26 14h12"/><circle cx="32" cy="38" r="6" opacity=".5"/>',
  physick:'<path d="M26 8h12M28 8v12L16 44a8 8 0 0 0 7 12h18a8 8 0 0 0 7-12L36 20V8"/><path d="M20 40h24" opacity=".5"/>',
  scadu:'<path d="M32 56V28"/><path d="M32 28c-10 0-16-6-16-14 8 0 12 4 16 10 4-6 8-10 16-10 0 8-6 14-16 14z"/><path d="M24 56h16"/>',
  gear:'<path d="M32 8l6 6h8v8l6 6-6 6v8h-8l-6 6-6-6h-8v-8l-6-6 6-6v-8h8z"/><circle cx="32" cy="28" r="7"/>',
  warn:'<path d="M32 10l24 42H8z"/><path d="M32 26v12M32 44v1"/>'
};
function tcBuildSigil(id){return `<svg class="tc-forge-sigil" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">${TC_BUILD_SIGILS[id]||''}</g></svg>`;}
const TC_ATTR_NAMES={str:'Strength',dex:'Dexterity',int:'Intelligence',fai:'Faith',arc:'Arcane'};
function tcBuildItemEffect(name,kind){
  const info=window.tcBuildLabInfo;if(!name||!info)return '';
  const key=info.itemKey(name);
  const stats=(kind==='physick'?info.STAT_PHYSICK:info.STAT_TALISMANS)[key];
  if(stats)return Object.entries(stats).filter(([,v])=>v).map(([k,v])=>`+${v} ${TC_ATTR_NAMES[k]||k.toUpperCase()}`).join(', ');
  const note=(kind==='physick'?info.PHYSICK_NOTES:info.CONDITIONAL_TALISMANS)[key];
  if(!note)return '';
  return note.replace(/^Physick active:\s*/i,'').split(';')[0].replace(/\.$/,'').replace(/^\w/,m=>m.toUpperCase());
}
function tcBuildStatusMark(screen){
  const row=screen.querySelector('.tc-build-save-row'),tabs=screen.querySelector('.tc-build-player-tabs');if(!row||!tabs)return;
  if(row.previousElementSibling!==tabs)tabs.after(row);
  const text=row.querySelector('.tc-build-save-state')?.textContent||'';
  row.classList.toggle('failed',/not saved|interrupted/i.test(text));
  row.classList.toggle('busy',/saving|waiting|unsaved/i.test(text)&&!/not saved/i.test(text));
}
function tcDecorateWeaponResults(screen){
  const host=screen.querySelector('#tcWeaponResults');if(!host)return;
  host.querySelectorAll('.tc-req-row:not(.head):not([data-tc-bar])').forEach(row=>{
    row.dataset.tcBar='1';
    const label=row.querySelector('span')?.textContent||'',[need,yours,grade]=[...row.querySelectorAll('b')].map(b=>b.textContent.trim());
    const n=Number(need)||0,y=Number(yours)||0,unmet=row.classList.contains('unmet');
    const pct=Math.max(4,Math.min(100,y/99*100)),mark=n?Math.min(100,n/99*100):null;
    row.innerHTML=`<span class="tc-grade ${grade==='—'?'none':''}">${grade==='—'?'·':grade}</span><span class="tc-req-name">${label}</span><span class="tc-req-bar"><i style="width:${pct}%"></i>${mark!=null?`<em style="left:${mark}%"></em>`:''}</span><span class="tc-req-nums">${y}${n?`<small>needs ${n}</small>`:''}</span>`;
  });
  // The "strongest affinity" slip disappears once you're already on the
  // affinity its button would switch to (or on the strongest outright).
  const tip=host.querySelector('.tc-affinity-tip');
  if(tip){
    const pick=tip.querySelector('[data-affinity-pick]')?.dataset.affinityPick,current=host.querySelector('.tc-affinity-chip.current')?.dataset.affinityPick;
    tip.hidden=tip.classList.contains('best')||Boolean(pick&&current&&pick===current);
  }
  const head=host.querySelector('.tc-req-row.head');if(head)head.remove();
  const reqTitle=host.querySelector('.tc-req-table>span');if(reqTitle&&!reqTitle.dataset.tcStyled){reqTitle.dataset.tcStyled='1';reqTitle.textContent='What it scales with';}
  host.querySelectorAll('.tc-weapon-note:not([data-tc-card])').forEach(note=>{
    note.dataset.tcCard='1';
    let text=note.textContent.trim(),kind='talisman';
    const gear=text.match(/^Effective combat stats include active talisman and Physick bonuses:\s*(.*)\.$/);
    if(gear){kind='gear';text=`Your gear adds ${gear[1]} to these numbers.`;}
    else if(/^Scadutree Blessing/.test(text))kind='scadu';
    else if(/^Physick active:/i.test(text)){kind='physick';text=text.replace(/^Physick active:\s*/i,'').replace(/^\w/,m=>m.toUpperCase());}
    else if(note.classList.contains('warn'))kind='warn';
    else if(/staffs and seals/.test(text))kind='gear';
    note.classList.add('tc-effect-card',kind);
    note.innerHTML=`<span class="tc-effect-seal">${tcBuildSigil(kind)}</span><p>${h(text)}</p>`;
  });
}
function tcDecorateStats(screen){
  const pane=screen.querySelector('[data-build-pane="stats"]');if(!pane)return;
  const grid=pane.querySelector('.tc-build-stats'),level=pane.querySelector('#tcBuild-level')?.closest('.tc-build-field');
  let seal=pane.querySelector('.tc-level-seal');
  if(!seal&&level){
    seal=document.createElement('div');seal.className='tc-level-seal';
    pane.querySelector('.tc-build-section-head')?.after(seal);
    seal.appendChild(level);
    const status=pane.querySelector('#tcBuildStatus');if(status)seal.after(status);
  }
  const small=pane.querySelector('.tc-build-origin small');
  if(small&&!small.dataset.tcStyled){small.dataset.tcStyled='1';small.textContent='Sets the starting stats and their minimums. Your Level is never changed for you.';}
  // Gear bonus on the attribute it changes.
  const boosts={};
  pane.querySelectorAll('.tc-effective-stats span.boosted').forEach(span=>{const key=(span.firstChild?.textContent||'').trim().toLowerCase(),value=span.querySelector('b')?.textContent;if(key&&value)boosts[key]=value;});
  Object.keys(TC_ATTR_NAMES).forEach(key=>{
    const field=grid?.querySelector(`#tcBuild-${key}`)?.closest('.tc-build-field');if(!field)return;
    let tag=field.querySelector('.tc-stat-gear');
    if(boosts[key]){if(!tag){tag=document.createElement('span');tag.className='tc-stat-gear';field.appendChild(tag);}tag.textContent=`${boosts[key]} with gear`;}
    else tag?.remove();
  });
}
function tcSocketMarkup(kind,index,value){
  const effect=tcBuildItemEffect(value,kind);
  return `<button type="button" class="tc-socket ${value?'filled':'empty'}" data-socket-kind="${kind}" data-socket-index="${index}">
    <span class="tc-socket-disc">${value?tcBuildSigil(kind):'<b>+</b>'}</span>
    <span class="tc-socket-text"><strong>${value?h(value):kind==='physick'?'Empty tear slot':'Empty slot'}</strong>${effect?`<small>${h(effect)}</small>`:''}</span>
  </button>`;
}
function tcDecorateGear(screen){
  const panes=[...screen.querySelectorAll('[data-build-pane="gear"]')];if(!panes.length)return;
  const [talPane,physPane]=panes;
  const draw=(pane,kind,attr,cls)=>{
    if(!pane)return;
    const selects=[...pane.querySelectorAll(`select[${attr}]`)];if(!selects.length)return;
    const wrap=pane.querySelector('.tc-build-talismans');if(wrap)wrap.classList.add('tc-select-store');
    let box=pane.querySelector('.'+cls);
    if(!box){box=document.createElement('div');box.className=cls;(wrap||pane).before(box);}
    const sig=selects.map(s=>s.value).join('|');if(box.dataset.sig===sig)return;box.dataset.sig=sig;
    box.innerHTML=(kind==='physick'?`<svg class="tc-flask" viewBox="0 0 120 150" aria-hidden="true"><path d="M48 8h24M52 8v28L20 92a34 34 0 0 0 30 50h20a34 34 0 0 0 30-50L68 36V8"/><path d="M26 98c22-8 46 8 68 0" opacity=".5"/></svg>`:'')+`<div class="tc-socket-grid">${selects.map((s,i)=>tcSocketMarkup(kind,i,s.value)).join('')}</div>`;
  };
  draw(talPane,'talisman','data-talisman','tc-pouch');
  draw(physPane,'physick','data-physick','tc-physick-flask');
  const helper=physPane?.querySelector('.tc-build-helper');
  if(helper&&!helper.dataset.tcStyled){helper.dataset.tcStyled='1';helper.textContent='Knot tears add +10 to their stat in every number above. Crimson, Cerulean and Ruptured Crystal Tears may fill both slots if you own two.';}
  [talPane,physPane].forEach(p=>{const span=p?.querySelector('.tc-build-section-head span');if(span&&!span.dataset.tcStyled){span.dataset.tcStyled='1';span.textContent=p===talPane?'Tap a socket to change it':'Assumes the Physick is active';}});
}
function tcOpenSocketSheet(kind,index){
  const attr=kind==='physick'?'data-physick':'data-talisman';
  const select=()=>document.querySelector(`.tc-build-screen select[${attr}="${index}"]`);
  const s=select();if(!s)return;
  document.querySelector('.tc-pick-sheet-wrap')?.remove();
  const wrap=document.createElement('div');wrap.className='tc-pick-sheet-wrap';
  const options=[...s.options].filter(o=>o.value);
  const title=kind==='physick'?`Crystal Tear ${index+1}`:`Talisman slot ${index+1}`;
  wrap.innerHTML=`<div class="tc-pick-sheet" role="dialog" aria-modal="true" aria-label="${h(title)}">
    <div class="tc-pick-head"><strong>${h(title)}</strong><button type="button" class="tc-pick-close" data-pick-close aria-label="Close">✕</button></div>
    <input type="search" class="tc-pick-search" placeholder="Search ${kind==='physick'?'tears':'talismans'}" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="search">
    <div class="tc-pick-list">
      <button type="button" class="tc-pick-item empty ${s.value?'':'on'}" data-pick-value=""><strong>Leave it empty</strong></button>
      ${options.map(o=>{const effect=tcBuildItemEffect(o.value,kind);return `<button type="button" class="tc-pick-item ${o.value===s.value?'on':''}" data-pick-value="${h(o.value)}" ${o.disabled?'disabled':''}><strong>${h(o.value)}</strong>${o.disabled?'<small>Already worn</small>':effect?`<small>${h(effect)}</small>`:''}</button>`;}).join('')}
    </div></div>`;
  document.body.appendChild(wrap);
  requestAnimationFrame(()=>wrap.classList.add('open'));
  const close=()=>{wrap.classList.remove('open');setTimeout(()=>wrap.remove(),260);};
  wrap.addEventListener('click',event=>{
    if(event.target===wrap||event.target.closest('[data-pick-close]'))return close();
    const item=event.target.closest('[data-pick-value]');if(!item||item.disabled)return;
    const target=select();
    if(target&&target.value!==item.dataset.pickValue){
      if(item.dataset.pickValue&&![...target.options].some(o=>o.value===item.dataset.pickValue))return close();
      target.value=item.dataset.pickValue;target.dispatchEvent(new Event('change',{bubbles:true}));
    }
    close();
    const screen=document.querySelector('.tc-build-screen');if(screen)tcDecorateGear(screen);
  });
  const search=wrap.querySelector('.tc-pick-search');
  search.addEventListener('input',()=>{const q=search.value.trim().toLowerCase();wrap.querySelectorAll('.tc-pick-item:not(.empty)').forEach(b=>{b.hidden=Boolean(q)&&!b.dataset.pickValue.toLowerCase().includes(q);});});
  wrap.querySelector('.tc-pick-item.on')?.scrollIntoView({block:'center'});
}
function tcDecorateBuildStyle(){
  const screen=app.querySelector('.tc-build-screen');if(!screen)return;
  screen.classList.add('tc-build-new');
  tcBuildStatusMark(screen);
  tcDecorateWeaponResults(screen);
  tcDecorateStats(screen);
  tcDecorateGear(screen);
}
document.addEventListener('click',event=>{
  const socket=event.target.closest('[data-socket-kind]');if(!socket)return;
  event.preventDefault();tcOpenSocketSheet(socket.dataset.socketKind,Number(socket.dataset.socketIndex)||0);
});
if(!window.__tcBuildStyleBound){
  window.__tcBuildStyleBound=true;
  let queued=false;
  const run_=()=>{queued=false;try{tcDecorateBuildStyle();}catch(error){console.warn('Build style skipped',error);}};
  const start=()=>new MutationObserver(()=>{if(queued||!app.querySelector('.tc-build-screen'))return;queued=true;requestAnimationFrame(run_);}).observe(document.body,{childList:true,subtree:true,characterData:true});
  if(document.body)start();else document.addEventListener('DOMContentLoaded',start);
}
/* --- End Build style --- */
