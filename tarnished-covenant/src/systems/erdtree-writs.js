/* --- Erdtree Writ system --- */
const TC_ERDTREE_WRIT_CHANCE=0.07;
const TC_ERDTREE_TARGETS=[
  {id:'weeping',region:'Weeping Peninsula',area:'Minor Erdtree · Weeping Peninsula',boss:'Erdtree Avatar',tears:['Opaline Bubbletear','Crimsonburst Crystal Tear']},
  {id:'liurnia-east',region:'Liurnia of the Lakes',area:'Minor Erdtree · East Liurnia',boss:'Erdtree Avatar',tears:['Magic-Shrouding Cracked Tear','Lightning-Shrouding Cracked Tear','Holy-Shrouding Cracked Tear']},
  {id:'liurnia-west',region:'Liurnia of the Lakes',area:'Minor Erdtree · West Liurnia',boss:'Erdtree Avatar',tears:['Cerulean Crystal Tear','Ruptured Crystal Tear']},
  {id:'caelid',region:'Caelid',area:'Minor Erdtree · Caelid',boss:'Putrid Avatar',tears:['Greenburst Crystal Tear','Flame-Shrouding Cracked Tear']},
  {id:'dragonbarrow',region:'Caelid',area:"Minor Erdtree · Greyoll's Dragonbarrow",boss:'Putrid Avatar',tears:['Opaline Hardtear','Stonebarb Cracked Tear']},
  {id:'mountaintops',region:'Mountaintops of the Giants',area:'Minor Erdtree · Mountaintops',boss:'Erdtree Avatar',tears:['Cerulean Crystal Tear','Crimson Bubbletear']},
  {id:'snowfield',region:'Mountaintops of the Giants',area:'Minor Erdtree · Consecrated Snowfield',boss:'Putrid Avatar',tears:['Ruptured Crystal Tear','Thorny Cracked Tear'],snowfield:true}
];

function tcLegacyErdtreeClearIds(state){
  const out=new Set();
  for(const entry of (Array.isArray(state?.history)?state.history:[])){
    const region=entry?.region||'',name=String(entry?.name||'').toLowerCase().replace(/[’]/g,"'").replace(/[^a-z0-9]+/g,' ').trim();
    if(region==='Weeping Peninsula'&&name==='erdtree avatar')out.add('weeping');
    if(region==='Liurnia of the Lakes'&&name.includes('erdtree avatar')&&name.includes('northeast'))out.add('liurnia-east');
    if(region==='Liurnia of the Lakes'&&name.includes('erdtree avatar')&&name.includes('southwest'))out.add('liurnia-west');
    if(region==='Caelid'&&name==='putrid avatar')out.add('caelid');
    if(region==='Mountaintops of the Giants'&&name==='erdtree avatar')out.add('mountaintops');
    if(region==='Mountaintops of the Giants'&&name==='putrid avatar')out.add('snowfield');
  }
  return [...out];
}
function tcErdtreeClearedIds(state){
  const sm=smithingData(state||{});
  return Array.from(new Set([...tcLegacyErdtreeClearIds(state),...(Array.isArray(sm.erdtreeAvatarClears)?sm.erdtreeAvatarClears:[])]));
}
function tcErdtreeWritIssueCap(state){
  return Math.max(0,TC_ERDTREE_TARGETS.length-tcLegacyErdtreeClearIds(state).length);
}
function tcErdtreeWritStockRemaining(state){
  const sm=smithingData(state||{});
  return Math.max(0,tcErdtreeWritIssueCap(state)-Number(sm.erdtreeWritsAwarded||0));
}
function tcErdtreeRegionReached(state,target){
  if(!state||!target)return false;
  return target.region===state.region||(state.clearedRegions||[]).includes(target.region)||(state.history||[]).some(x=>x?.region===target.region);
}
function tcErdtreeTargetAccessible(state,target){
  if(!tcErdtreeRegionReached(state,target))return false;
  if(target?.snowfield){
    if(typeof tcBossActuallyDefeated==='function')return tcBossActuallyDefeated(state,'Commander Niall');
    return (state.history||[]).some(x=>String(x?.name||'').toLowerCase().includes('commander niall'));
  }
  return true;
}
function tcErdtreeTargetStatus(state,target){
  if(tcErdtreeClearedIds(state).includes(target.id))return 'cleared';
  return tcErdtreeTargetAccessible(state,target)?'available':'locked';
}

// Remove the seven Physick-bearing Avatar encounters from normal random boss
// assignments. The app historically collapsed the two Caelid Putrid Avatars into
// one pool entry, so the Writ registry deliberately expands them back to seven
// real Minor Erdtree targets.
const TC_ERDTREE_POOL_REMOVALS={
  'Weeping Peninsula':['Erdtree Avatar'],
  'Liurnia of the Lakes':['Erdtree Avatar (Liurnia Northeast)','Erdtree Avatar(Liurnia Southwest)'],
  'Caelid':['Putrid Avatar'],
  'Mountaintops of the Giants':['Erdtree Avatar','Putrid Avatar']
};
for(const [regionName,names] of Object.entries(TC_ERDTREE_POOL_REMOVALS)){
  const keys=new Set(names.map(x=>String(x).toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()));
  const keep=name=>!keys.has(String(name).toLowerCase().replace(/[^a-z0-9]+/g,' ').trim());
  if(regions?.[regionName]?.bosses)regions[regionName].bosses=regions[regionName].bosses.filter(keep);
  if(typeof SHEET_BOSS_POOLS!=='undefined'&&Array.isArray(SHEET_BOSS_POOLS?.[regionName]))SHEET_BOSS_POOLS[regionName]=SHEET_BOSS_POOLS[regionName].filter(keep);
}

// While finite stock remains, Writ is a 7% top-level reward. The established
// reward table fills the remaining 93%; when the finite stock is exhausted the
// original table automatically returns to its full 100% distribution.
const tcDrawCovenantRewardBeforeErdtreeWrit=drawCovenantReward;
drawCovenantReward=function(state){
  const sm=state.smithing||(state.smithing=smithingData(state));
  if(tcErdtreeWritStockRemaining(state)>0&&Math.random()<TC_ERDTREE_WRIT_CHANCE){
    sm.erdtreeWrits=Number(sm.erdtreeWrits||0)+1;
    sm.erdtreeWritsAwarded=Number(sm.erdtreeWritsAwarded||0)+1;
    return {kind:'erdtree',label:'Erdtree Writ',detail:'Authorization to defeat one reachable, uncleared Minor Erdtree Avatar and seize its Crystal Tears. Finite issue: one Writ per remaining Avatar.'};
  }
  return tcDrawCovenantRewardBeforeErdtreeWrit(state);
};
const tcRewardIconBeforeErdtreeWrit=tcRewardIcon;
tcRewardIcon=function(kind){return kind==='erdtree'?'♧':tcRewardIconBeforeErdtreeWrit(kind);};
const tcRewardClassBeforeErdtreeWrit=tcRewardClass;
tcRewardClass=function(kind){return kind==='erdtree'?'erdtree':tcRewardClassBeforeErdtreeWrit(kind);};

function tcBuildErdtreeWritSpend(latest,targetId,actor){
  const target=TC_ERDTREE_TARGETS.find(x=>x.id===targetId),sm=smithingData(latest||{});
  if(!target||Number(sm.erdtreeWrits||0)<1)return null;
  if(tcErdtreeClearedIds(latest).includes(target.id)||!tcErdtreeTargetAccessible(latest,target))return null;
  const next=smithingCopy(latest);
  next.smithing.erdtreeWrits=Math.max(0,Number(next.smithing.erdtreeWrits||0)-1);
  next.smithing.erdtreeAvatarClears=Array.from(new Set([...(next.smithing.erdtreeAvatarClears||[]),target.id]));
  next.lastAction=`${actor} redeemed an Erdtree Writ at ${target.area}. ${target.boss} recorded felled; Crystal Tears seized.`;
  next.updatedAt=new Date().toISOString();
  return next;
}
let tcErdtreeWritBusy=false;
async function tcRedeemErdtreeWrit(targetId){
  if(tcErdtreeWritBusy)return;
  const target=TC_ERDTREE_TARGETS.find(x=>x.id===targetId);if(!target)return;
  const staged=tcBuildErdtreeWritSpend(run?.state,targetId,playerName());
  if(!staged)return setToast('That Avatar is not currently eligible for an Erdtree Writ.');
  tcErdtreeWritBusy=true;
  try{
    const saved=await commit(staged,{successToast:`Erdtree Writ redeemed · ${target.area}.`,retryBuilder:(latest)=>tcBuildErdtreeWritSpend(latest,targetId,playerName())});
    if(saved){document.querySelector('#tcStrategyOverlay')?.remove();ledgerView='smithing';uiScreen='ledger';renderRun();}
  }finally{tcErdtreeWritBusy=false;}
}
function tcOpenErdtreeWritPicker(){
  const state=run?.state,sm=smithingData(state||{}),cleared=new Set(tcErdtreeClearedIds(state));
  if(Number(sm.erdtreeWrits||0)<1)return setToast('No Erdtree Writ available.');
  const items=TC_ERDTREE_TARGETS.map(target=>{
    const status=cleared.has(target.id)?'cleared':tcErdtreeTargetAccessible(state,target)?'available':'locked';
    const label=status==='cleared'?'CLEARED':status==='available'?'SPEND WRIT':'LOCKED';
    const note=status==='locked'?(target.snowfield?'Requires Consecrated Snowfield access via Commander Niall.':`Reach ${target.region} first.`):target.tears.join(' · ');
    return `<button type="button" class="tc-erdtree-target ${status}" data-erdtree-target="${target.id}" ${status==='available'?'':'disabled'}><span><strong>${h(target.area)}</strong><span>${h(target.boss)} · ${h(note)}</span></span><em>${label}</em></button>`;
  }).join('');
  const overlay=tcStrategicOverlay('Erdtree Writ',`<p>Spend one Writ only after defeating the chosen reachable Avatar. This does not count as a Covenant encounter, regional clear, or reward payout. The Crystal Tears are the prize.</p><div class="tc-strategy-list">${items}</div><p>${tcErdtreeWritStockRemaining(state)} additional Writ${tcErdtreeWritStockRemaining(state)===1?'':'s'} can still enter circulation this run.</p>`);
  overlay.querySelectorAll('[data-erdtree-target]').forEach(btn=>btn.addEventListener('click',()=>tcRedeemErdtreeWrit(btn.dataset.erdtreeTarget)));
}

const tcCovenantBoonMarkupBeforeErdtreeWrit=covenantBoonMarkup;
covenantBoonMarkup=function(state){
  const base=tcCovenantBoonMarkupBeforeErdtreeWrit(state),sm=smithingData(state),cleared=tcErdtreeClearedIds(state).length,stock=tcErdtreeWritStockRemaining(state);
  return base+`<div class="tc-erdtree-writ-card"><div class="tc-erdtree-writ-head"><div><div class="tc-kicker ember">minor erdtree authorization</div><strong>Erdtree Writ</strong></div><div class="tc-erdtree-writ-count">${sm.erdtreeWrits}</div></div><div class="tc-muted">Spend one after defeating a reachable Minor Erdtree Avatar to claim its Physick tears. ${cleared}/${TC_ERDTREE_TARGETS.length} Avatar sites resolved · ${stock} Writ${stock===1?'':'s'} remain in the finite issue pool.</div>${sm.erdtreeWrits>0?`<button type="button" class="btn ghost small" data-use-erdtree-writ>Review Erdtree Targets</button>`:''}</div>`;
};
if(!window.__tcErdtreeWritBound){
  window.__tcErdtreeWritBound=true;
  document.addEventListener('click',e=>{if(e.target.closest('[data-use-erdtree-writ]'))tcOpenErdtreeWritPicker();});
}
/* --- End Erdtree Writ system --- */