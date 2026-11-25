/* --- Hewg's Forge: the third Site of Grace panel ---
   Before every Miner's Bell Bearing is home it is the Bell Bearing Hunt hub
   (contract call-to-action, bearings at a glance). Afterwards it becomes
   Hewg's Surplus. The room code stays at the foot of the panel; the old quick
   links (duplicates of the bottom bar) are dropped. Presentation only. */
const TC_FORGE_ANVIL=`<svg class="tc-forge-anvil" viewBox="0 0 160 120" aria-hidden="true">
  <defs><radialGradient id="tcForgeGlow" cx="50%" cy="62%" r="55%"><stop offset="0" stop-color="#ff9a3c" stop-opacity=".55"/><stop offset=".55" stop-color="#b4461a" stop-opacity=".18"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
  <linearGradient id="tcForgeIron" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6b5a45"/><stop offset=".45" stop-color="#3a3026"/><stop offset="1" stop-color="#1c1712"/></linearGradient></defs>
  <ellipse class="tc-forge-heat" cx="80" cy="74" rx="78" ry="46" fill="url(#tcForgeGlow)"/>
  <path d="M30 52h86c8 0 16-4 22-10l4 2c-4 12-14 20-26 22H98l-6 12 10 14H58l10-14-6-12H40c-6 0-10-5-10-10z" fill="url(#tcForgeIron)" stroke="#c8a85b" stroke-opacity=".55" stroke-width="1.2"/>
  <path d="M50 102h60v6H50z" fill="#2a221a" stroke="#c8a85b" stroke-opacity=".4"/>
  <g class="tc-forge-hammer"><path d="M86 20l26-14 6 10-26 14z" fill="#4a3d30" stroke="#c8a85b" stroke-opacity=".6"/><path d="M98 22l-24 30" stroke="#8a6a3e" stroke-width="4" stroke-linecap="round"/></g>
  <g class="tc-forge-sparks" fill="#ffb25a"><circle cx="76" cy="48" r="1.6"/><circle cx="84" cy="46" r="1.2"/><circle cx="70" cy="45" r="1"/><circle cx="90" cy="49" r="1.3"/><circle cx="80" cy="43" r="1"/></g>
</svg>`;
function tcForgeBearingCount(state){
  const acquired=new Set(smithingData(state).acquired);
  return TC_BELL_BEARINGS.filter(b=>acquired.has(b.id)).length;
}
function tcForgePurse(state){
  const sm=smithingData(state);
  return `<div class="tc-forge-purse"><div><span>Smithing Favor</span><strong>✦ ${sm.favor}</strong></div><div><span>Masterwork Credits</span><strong>⚒ ${sm.masterworkCredits}</strong></div></div>`;
}
function tcForgeHuntMarkup(state){
  const sm=smithingData(state),acquired=new Set(sm.acquired),contract=sm.activeContract,have=tcForgeBearingCount(state);
  const rows=TC_BELL_BEARINGS.map(b=>{
    const got=acquired.has(b.id),active=contract?.bearingId===b.id,open=!got&&!active&&bellAccessible(state,b);
    const status=got?'Home':active?(contract.status==='sanctioned'?'Sanctioned':'Contract'):open?`${smithingContractCost(b)} Favor`:'Locked';
    const cls=got?'done':active?'active':open?'available':'locked';
    return `<div class="tc-forge-bearing ${cls}"><span class="tc-forge-bell" aria-hidden="true">${got?'◆':active?'◈':'◇'}</span><div><strong>${h(b.name.replace(/ Miner’s Bell Bearing/,''))}</strong><small>${h(b.custodian)} · ${h(b.place)}</small></div><em>${h(status)}</em></div>`;
  }).join('');
  return `<div class="tc-forge-hero hunt"><img src="assets/bosses/bell-bearing-hunter.webp" alt="" loading="lazy" decoding="async"><div class="tc-forge-hero-copy"><div class="tc-kicker ember">The Bell Bearing Hunt</div><h3>${have} of ${TC_BELL_BEARINGS.length} Bearings Home</h3><p>Bring every Miner’s Bell Bearing home and Hewg opens his surplus stock.</p><div class="tc-forge-progress"><span style="width:${Math.round(have/TC_BELL_BEARINGS.length*100)}%"></span></div></div></div>
    ${tcForgePurse(state)}
    ${(()=>{const hub=smithingHubMarkup(state);return hub.includes('tc-forge-notice quiet')?'':hub;})()}
    <div class="tc-kicker ember tc-forge-section">Bearings</div>
    <div class="tc-forge-bearings">${rows}</div>`;
}
function tcForgeShopMarkup(state){
  return `<div class="tc-forge-hero shop">${TC_FORGE_ANVIL}<div class="tc-forge-hero-copy"><div class="tc-kicker ember">Hewg’s Surplus</div><h3>Every Bearing Is Home</h3><p>“Favor, is it? Fine. I’ve a few things lying about.”</p></div></div>
    ${tcForgePurse(state)}
    ${tcShopMarkup(state,{bare:true})}`;
}
function tcMountForgePanel(){
  const panel=app.querySelector('.tc-sanctuary-panel[data-panel="covenant"]');
  if(!panel||panel.dataset.forge||!run?.state)return;
  panel.dataset.forge='1';panel.classList.add('tc-forge-panel');
  const open=tcShopOpen(run.state);
  const tab=app.querySelectorAll('.tc-sanctuary-tabs button')[2];if(tab)tab.textContent='Forge';
  const heading=panel.querySelector('.tc-panel-heading');if(heading)heading.textContent='Hewg’s Forge';
  panel.querySelectorAll('.tc-quick,.tc-forge-notice,.tc-forge-favor').forEach(node=>node.remove());
  const forge=document.createElement('div');forge.className='tc-forge';
  forge.innerHTML=open?tcForgeShopMarkup(run.state):tcForgeHuntMarkup(run.state);
  if(heading)heading.after(forge);else panel.prepend(forge);
  const code=panel.querySelector('.tc-code-row');if(code){code.classList.add('tc-forge-code');panel.appendChild(code);}
}
const tcRenderSanctuaryBeforeForge=renderSanctuary;
renderSanctuary=function(){tcRenderSanctuaryBeforeForge();try{tcMountForgePanel();}catch(error){console.warn('Forge panel skipped',error);}};
function tcOpenForge(){uiScreen='sanctuary';tcSanctuaryPanelIndex=2;pendingRevealId=null;renderRun();}
document.addEventListener('click',event=>{
  const el=event.target.closest('[data-forge-open]');if(!el)return;
  event.preventDefault();tcOpenForge();
});
/* --- End Hewg's Forge --- */
