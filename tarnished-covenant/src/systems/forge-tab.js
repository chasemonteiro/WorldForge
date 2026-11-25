/* --- Hewg's Forge: the third Site of Grace panel ---
   One scene carries the panel: a stone hearth, a coal bed and an anvil, with
   the purse resting on the hero's foot. Before every Miner's Bell Bearing is
   home the coals are banked and the panel is the Bell Bearing Hunt (a rail of
   eight bells); afterwards the fire is up and the panel is Hewg's Surplus,
   laid out as wares rather than rows. Presentation only; purchases and
   contracts go through the existing builders. The room code lives in Settings. */
const TC_FORGE_SIGILS={
  masterwork:'<path d="M14 40h36l-6 6H20z"/><path d="M18 34h28c3 0 6-2 8-5H22c-3 0-5 2-4 5z"/><path d="M30 34v6M38 34v6"/><path d="M36 10l10 6-4 6-10-6z"/><path d="M38 19L27 30"/>',
  remembrance:'<path d="M32 6v36"/><path d="M26 42h12M32 42v10"/><path d="M29 52h6"/><path d="M32 12c10 2 14 10 8 16-4 4-12 2-12-4 0-4 6-6 8-2"/>',
  appeal:'<path d="M32 10v36M22 46h20"/><path d="M14 18h36"/><path d="M14 18l-6 14h12zM50 18l-6 14h12z"/>',
  chaos:'<circle cx="32" cy="30" r="15"/><path d="M32 30c0-5 7-5 7 0 0 7-12 8-12-1 0-10 16-11 17 1"/>',
  rite:'<path d="M32 8l5 17 17 5-17 5-5 17-5-17-17-5 17-5z"/>',
  clemency:'<path d="M44 8L22 44l-2 8 6-6L48 12z"/><path d="M14 52h36"/>',
  joint:'<path d="M14 12l32 32M50 12L18 44"/><path d="M40 46l8-8M24 46l-8-8"/>',
  freeboss:'<path d="M32 6v34"/><path d="M24 40h16M32 40v12"/><path d="M18 22c4-8 24-8 28 0"/>',
  draw:'<path d="M12 20h40v26H12z"/><path d="M12 20l20 14 20-14"/><circle cx="32" cy="38" r="5"/>'
};
const TC_FORGE_LINES={
  masterwork:'One more Masterwork credit for the workbench.',
  remembrance:'Carry a felled lord’s weapon for this fight.',
  appeal:'Change a weapon with no penalty.',
  chaos:'Rewrite one Chaos decree.',
  rite:'Rewrite one Odd Rite.',
  clemency:'Erase one Appeal penalty.',
  joint:'Reroll both weapons, no penalty.',
  freeboss:'Skip one optional boss for good.',
  draw:'One random Covenant reward. It could be a tax.'
};
function tcForgeSigil(id){return `<svg class="tc-forge-sigil" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${TC_FORGE_SIGILS[id]||''}</g></svg>`;}
function tcForgeScene(lit){
  const embers=lit?Array.from({length:10},(_,i)=>`<circle class="tc-ember e${i}" cx="${142+((i*41)%108)}" cy="168" r="${1.1+(i%3)*.55}"/>`).join(''):'';
  const flame=(x,h,w,cls)=>`<path class="tc-flame ${cls}" d="M${x-w} 196C${x-w} ${196-h*.45} ${x-w*.2} ${196-h*.7} ${x} ${196-h}C${x+w*.25} ${196-h*.6} ${x+w} ${196-h*.4} ${x+w} 196z"/>`;
  return `<svg class="tc-forge-scene ${lit?'lit':'banked'}" viewBox="0 0 390 220" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
    <defs>
      <radialGradient id="tcHearth" cx="50%" cy="92%" r="78%"><stop offset="0" stop-color="${lit?'#ffd27a':'#9a4418'}"/><stop offset=".22" stop-color="${lit?'#ff7a26':'#5a2210'}"/><stop offset=".55" stop-color="${lit?'#8a2a0c':'#2c0f07'}"/><stop offset="1" stop-color="#140906"/></radialGradient>
      <radialGradient id="tcSpill" cx="50%" cy="96%" r="75%"><stop offset="0" stop-color="#ff8a3a" stop-opacity="${lit?'.45':'.12'}"/><stop offset=".6" stop-color="#ff6a1a" stop-opacity="${lit?'.10':'.03'}"/><stop offset="1" stop-color="#ff6a1a" stop-opacity="0"/></radialGradient>
      <linearGradient id="tcFlame" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#fff0b8"/><stop offset=".35" stop-color="#ffb347"/><stop offset=".8" stop-color="#e2451a" stop-opacity=".7"/><stop offset="1" stop-color="#e2451a" stop-opacity="0"/></linearGradient>
      <linearGradient id="tcStone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a221b"/><stop offset="1" stop-color="#18130f"/></linearGradient>
      <linearGradient id="tcIron" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${lit?'#ffb56a':'#a0623a'}"/><stop offset=".12" stop-color="#4a3626"/><stop offset=".5" stop-color="#1d1510"/><stop offset="1" stop-color="#0b0807"/></linearGradient>
    </defs>
    <rect width="390" height="220" fill="#0d0a08"/>
    <path d="M58 220V112c0-80 274-80 274 0v108z" fill="url(#tcStone)"/>
    <g stroke="#0d0a08" stroke-width="2.4" fill="none"><path d="M58 140h44M288 140h44M58 178h30M302 178h30M80 112v28M310 112v28M96 178v42M294 178v42"/><path d="M88 76l24 22M302 76l-24 22M138 44l10 28M252 44l-10 28M195 34v30"/></g>
    <path d="M104 220V128c0-52 182-52 182 0v92z" fill="url(#tcHearth)"/>
    <g class="tc-forge-flames" fill="url(#tcFlame)" opacity="${lit?'1':'.28'}">${lit?flame(162,58,16,'f1')+flame(196,84,20,'f2')+flame(230,62,17,'f3')+flame(180,40,10,'f4')+flame(214,46,11,'f5'):flame(196,26,18,'f2')}</g>
    <path d="M108 220c6-16 18-20 28-18s16-10 28-8 14-9 28-7 18 9 28 7 16 2 26 11 14 7 18 15z" fill="${lit?'#2a0d05':'#170804'}"/>
    <g class="tc-forge-coals" fill="${lit?'#ff9440':'#7a2e12'}"><ellipse cx="142" cy="208" rx="10" ry="4"/><ellipse cx="172" cy="203" rx="12" ry="4.5"/><ellipse cx="203" cy="205" rx="11" ry="4"/><ellipse cx="234" cy="208" rx="10" ry="4"/><ellipse cx="190" cy="214" rx="16" ry="4.5"/><ellipse cx="258" cy="214" rx="8" ry="3"/></g>
    <rect width="390" height="220" fill="url(#tcSpill)"/>
    <g class="tc-forge-embers" fill="#ffc77a">${embers}</g>
    <g fill="none" stroke="#5a4a39" stroke-width="3.2"><ellipse cx="350" cy="2" rx="5" ry="9"/><ellipse cx="350" cy="19" rx="3" ry="9"/><ellipse cx="350" cy="36" rx="5" ry="9"/><ellipse cx="350" cy="53" rx="3" ry="9"/><ellipse cx="350" cy="70" rx="5" ry="9"/><ellipse cx="350" cy="87" rx="3" ry="9"/><ellipse cx="350" cy="104" rx="5" ry="9"/></g>
    <g transform="translate(218 0)">
      <path d="M0 176h96c12 0 24-5 32-13l7 3c-6 15-19 25-36 27H78l-8 11 11 16H23l11-16-8-11H14C6 193 0 186 0 176z" fill="url(#tcIron)" stroke="${lit?'#ffa45a':'#8a5a36'}" stroke-opacity=".6" stroke-width="1.2"/>
      <g transform="translate(40 158) rotate(-12)"><rect x="0" y="-3" width="58" height="6" rx="2" fill="#4a3424"/><rect x="-12" y="-11" width="16" height="22" rx="2" fill="#2a221b" stroke="${lit?'#ffa45a':'#8a5a36'}" stroke-opacity=".55"/></g>
    </g>
    <rect y="180" width="390" height="40" fill="url(#tcFade)"/>
    <linearGradient id="tcFade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d0a08" stop-opacity="0"/><stop offset="1" stop-color="#0d0a08"/></linearGradient>
  </svg>`;
}
function tcForgeHero(state,lit){
  const sm=smithingData(state);
  return `<div class="tc-forge-hero ${lit?'lit':'banked'}">${tcForgeScene(lit)}</div>
    <div class="tc-forge-title"><div><h3>Hewg’s Forge</h3><p>${lit?'Every bearing is home. The fire is up and Hewg is selling.':'The coals stay banked until every Miner’s Bell Bearing is home.'}</p></div>
    <div class="tc-forge-purse" aria-label="${sm.favor} Smithing Favor, ${sm.masterworkCredits} Masterwork credits"><span><b>✦</b>${sm.favor}<i>Favor</i></span><span><b>⚒</b>${sm.masterworkCredits}<i>Masterworks</i></span></div></div>`;
}
function tcForgeWhy(state,item){
  const sm=smithingData(state);
  if(tcShopBusy(state))return 'Resolve the shared Covenant reward first.';
  if(item.id==='remembrance'){
    const block=tcRemembranceSwapBlocked(state);if(block)return block;
    if(!tcRemembranceWeaponChoices(state).length)return 'No remembrance weapons earned yet.';
  }
  if(sm.favor<item.cost)return `${item.cost-sm.favor} more Favor`;
  return '';
}
function tcForgeWare(state,item,size){
  const why=tcForgeWhy(state,item);
  return `<button type="button" class="tc-forge-ware ${size} ware-${item.id}" data-shop-item="${item.id}" ${why?'disabled':''}>
    ${size==='doc'?`<span class="tc-forge-seal">${tcForgeSigil(item.id)}</span>`:tcForgeSigil(item.id)}
    <strong>${h(item.label)}</strong>
    ${size==='doc'?'':`<small>${h(TC_FORGE_LINES[item.id]||item.detail)}</small>`}
    <span class="tc-forge-price"><b>${item.cost}</b> Favor</span>
    ${why&&!/more Favor$/.test(why)?`<em>${h(why)}</em>`:why?`<em class="short">${h(why)}</em>`:''}
  </button>`;
}
function tcForgeShopMarkup(state){
  const pick=ids=>ids.map(id=>tcShopItem(id)).filter(Boolean);
  const last=tcShopLog(state).slice(-3).reverse();
  return `${tcForgeHero(state,true)}
    <h4 class="tc-forge-h">Hewg’s finest</h4>
    <div class="tc-forge-finest">${pick(['masterwork','remembrance']).map(i=>tcForgeWare(state,i,'fine')).join('')}</div>
    <h4 class="tc-forge-h">Covenant documents</h4>
    <div class="tc-forge-docs">${pick(['appeal','clemency','joint','chaos','rite','freeboss']).map(i=>tcForgeWare(state,i,'doc')).join('')}</div>
    <h4 class="tc-forge-h">A sealed lot</h4>
    ${pick(['draw']).map(i=>tcForgeWare(state,i,'lot')).join('')}
    ${last.length?`<div class="tc-forge-recent"><h4 class="tc-forge-h">Lately bought</h4>${last.map(e=>`<p>${h(personalizePlayers(e.by||'',state))} bought ${h(e.detail||tcShopItem(e.item)?.label||e.item)} for ${Number(e.cost)||0} Favor.</p>`).join('')}</div>`:''}`;
}
const TC_FORGE_BELL='<svg class="tc-forge-bellshape" viewBox="0 0 48 56" aria-hidden="true"><path d="M24 4c-2 0-3 1-3 3v2C12 11 9 20 9 30v8l-4 6h38l-4-6v-8c0-10-3-19-12-21V7c0-2-1-3-3-3z"/><circle cx="24" cy="49" r="4"/></svg>';
function tcForgeBearingState(state,b){
  const sm=smithingData(state),contract=sm.activeContract;
  if(sm.acquired.includes(b.id))return {cls:'home',label:'Home'};
  if(contract?.bearingId===b.id)return {cls:'contract',label:contract.status==='sanctioned'?'Sanctioned':'Contracted'};
  if(bellAccessible(state,b))return {cls:'open',label:`${smithingContractCost(b)} Favor`};
  return {cls:'locked',label:'Not yet'};
}
function tcForgeHuntMarkup(state){
  const hub=smithingHubMarkup(state),have=tcForgeBearingCount(state);
  const bells=TC_BELL_BEARINGS.map(b=>{
    const st=tcForgeBearingState(state,b),tier=(b.name.match(/\[(\d)\]/)||[])[1]||'';
    return `<button type="button" class="tc-forge-bell ${st.cls} ${b.kind==='Somber'?'somber':'smithing'}" data-forge-bell="${h(b.id)}">${TC_FORGE_BELL}<strong>${h(b.kind)} ${h(tier)}</strong><span>${h(st.label)}</span></button>`;
  }).join('');
  return `${tcForgeHero(state,false)}
    ${hub.includes('tc-forge-notice quiet')?'':hub}
    <h4 class="tc-forge-h">Miner’s Bell Bearings · ${have} of ${TC_BELL_BEARINGS.length} home</h4>
    <div class="tc-forge-rail">${bells}</div>`;
}
function tcForgeBearingCount(state){
  const acquired=new Set(smithingData(state).acquired);
  return TC_BELL_BEARINGS.filter(b=>acquired.has(b.id)).length;
}
function tcOpenBellSheet(id){
  const state=run.state,b=TC_BELL_BEARINGS.find(x=>x.id===id);if(!b)return;
  const st=tcForgeBearingState(state,b),sm=smithingData(state);
  const text={home:'Claimed. Its Masterwork credit is already yours.',contract:'Your current contract. Open it to see the terms.',open:`Commission this contract for ${smithingContractCost(b)} Favor. You hold ${sm.favor}.`,locked:'Not available yet. Reach its region and claim the earlier bearing of this kind first.'}[st.cls];
  const action=st.cls==='contract'?'<button type="button" class="btn gold" data-smith-action="open-contract">Open contract</button>':(st.cls==='open'&&!sm.activeContract&&sm.favor>=smithingContractCost(b))?'<button type="button" class="btn gold" data-smith-action="commission">Commission contract</button>':'';
  const el=tcStrategicOverlay(b.name,`<p>${h(b.custodian)} · ${h(b.place)}</p><p>${h(text)}</p>`,action);
  el.querySelector('.tc-kicker').textContent=b.region;
  el.querySelectorAll('[data-smith-action]').forEach(btn=>btn.addEventListener('click',()=>el.remove()));
}
function tcMountForgePanel(){
  const panel=app.querySelector('.tc-sanctuary-panel[data-panel="covenant"]');
  if(!panel||panel.dataset.forge||!run?.state)return;
  panel.dataset.forge='1';panel.classList.add('tc-forge-panel');
  const open=tcShopOpen(run.state);
  const tab=app.querySelectorAll('.tc-sanctuary-tabs button')[2];if(tab)tab.textContent='Forge';
  panel.querySelector('.tc-panel-heading')?.remove();
  // The room code and the old quick links live elsewhere now (Settings, bottom bar).
  panel.querySelectorAll('.tc-quick,.tc-forge-notice,.tc-forge-favor,.tc-code-row').forEach(node=>node.remove());
  const forge=document.createElement('div');forge.className=`tc-forge ${open?'is-open':'is-hunt'}`;
  forge.innerHTML=open?tcForgeShopMarkup(run.state):tcForgeHuntMarkup(run.state);
  panel.prepend(forge);
}
const tcRenderSanctuaryBeforeForge=renderSanctuary;
renderSanctuary=function(){tcRenderSanctuaryBeforeForge();try{tcMountForgePanel();}catch(error){console.warn('Forge panel skipped',error);}};
function tcOpenForge(){uiScreen='sanctuary';tcSanctuaryPanelIndex=2;pendingRevealId=null;renderRun();}
document.addEventListener('click',event=>{
  const bell=event.target.closest('[data-forge-bell]');
  if(bell){event.preventDefault();tcOpenBellSheet(bell.dataset.forgeBell);return;}
  const el=event.target.closest('[data-forge-open]');if(!el)return;
  event.preventDefault();tcOpenForge();
});
/* --- End Hewg's Forge --- */
