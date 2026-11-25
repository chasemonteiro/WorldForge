/* --- Ledger: Remembrances (the codex) ---
   Every remembrance the run needs, grouped by the region it waits in, in run
   order. Each card says whether it is claimed (and when), here, open or not
   reached yet, and what Hewg will forge from it (TC_REMEMBRANCE_WEAPONS).
   The road and the world map live on Site of Grace → Progress now. */
function tcRemembranceClaim(state,name){
  const key=n=>typeof tcBossKey==='function'?tcBossKey(n):String(n||'').toLowerCase();
  const hit=(state.history||[]).find(x=>key(x?.name)===key(name));
  if(!hit?.completedAt)return '';
  return new Date(hit.completedAt).toLocaleDateString(undefined,{month:'short',day:'numeric'});
}
function tcRemembranceCard(state,name){
  const st=tcRemembranceStatus(state,name),when=st.key==='done'?tcRemembranceClaim(state,name):'';
  const status={done:when?`Claimed ${when}`:'Claimed',here:'Waiting in this region',open:'Its region is open',locked:'Region not reached yet'}[st.key];
  const weapons=(typeof TC_REMEMBRANCE_WEAPONS!=='undefined'&&TC_REMEMBRANCE_WEAPONS[name])||[];
  const forge=weapons.length?`Hewg forges: ${weapons.map(w=>h(w)).join(' · ')}`:'Spells only. Hewg has nothing to forge from it.';
  return `<div class="tc-codex-card ${st.key}"><svg class="tc-codex-rune" viewBox="-14 -14 28 28" aria-hidden="true"><circle r="11"/><path d="M0-6v12M-5-2l5-4 5 4M-4 4h8"/></svg><div><strong>${h(name)}</strong><span class="tc-codex-status">${h(status)}</span><small>${forge}</small></div></div>`;
}
function tcRemembranceCodexMarkup(state){
  const req=requiredRemembrances(state),done=req.filter(name=>hasRemembrance(state,name));
  const order=Object.keys(regions);
  const byRegion=new Map();
  req.forEach(name=>{const r=REMEMBRANCE_REGION[name]||'Elsewhere';if(!byRegion.has(r))byRegion.set(r,[]);byRegion.get(r).push(name);});
  const rank=r=>(r.includes('· DLC')?1000:0)+(order.indexOf(r)<0?999:order.indexOf(r));
  const regionsInOrder=[...byRegion.keys()].sort((a,b)=>rank(a)-rank(b));
  const here=req.filter(name=>!hasRemembrance(state,name)&&REMEMBRANCE_REGION[name]===state.region);
  const ticks=req.map(name=>`<span class="${hasRemembrance(state,name)?'on':''}"></span>`).join('');
  const groups=regionsInOrder.map(region=>{
    const names=byRegion.get(region),got=names.filter(n=>hasRemembrance(state,n)).length,img=regions[region]?actualRegionImage(region):'';
    return `<section class="tc-codex-region ${region===state.region?'here':''}"><h4><span class="tc-codex-medal" style="${img?`background-image:url('${img}')`:''}"></span>${h(region.replace(/ · DLC$/,''))}<em>${got} of ${names.length}</em></h4>${names.map(n=>tcRemembranceCard(state,n)).join('')}</section>`;
  }).join('');
  return `<div class="tc-codex">
    <div class="tc-codex-head"><strong>${done.length}</strong><div><span>of ${req.length} remembrances claimed</span><p>The final seal opens when every one is claimed.</p></div></div>
    <div class="tc-rem-ticks" aria-hidden="true" style="grid-template-columns:repeat(${Math.max(1,req.length)},minmax(0,1fr))">${ticks}</div>
    ${here.length?`<p class="tc-codex-next">Waiting in ${h(state.region.replace(/ · DLC$/,''))}: ${here.map(n=>`<b>${h(n)}</b>`).join(', ')}.</p>`:''}
    ${groups}
  </div>`;
}
/* --- End Remembrances codex --- */
