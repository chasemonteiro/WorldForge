/* --- Hewg's Surplus: a Favor shop that opens once every Miner's Bell Bearing is claimed ---
   Persisted additions (all optional, additive):
     smithing.shopLog            [{id,item,cost,by,at,detail}] newest last, capped
     current.remembranceSwaps    [{slot,weapon,boss,replaced,cost,by,at}]
   Every purchase is a pure builder over the latest state so a save race retries
   cleanly, and a purchase id makes a retried save impossible to double-charge. */
const TC_SHOP_LOG_LIMIT=40;
const TC_SHOP_ITEMS=[
  {id:'masterwork',label:'Masterwork Token',cost:12,glyph:'⚒',detail:'+1 Masterwork credit for Hewg’s Workbench.',grant:sm=>{sm.masterworkCredits=Number(sm.masterworkCredits||0)+1;}},
  {id:'remembrance',label:'Remembrance Weapon',cost:8,glyph:'❂',detail:'Turn a felled remembrance boss into its weapon for one Tarnished, for this fight. No Appeal penalty.'},
  {id:'appeal',label:'Appeal Waiver',cost:4,glyph:'⚖',detail:'Make one Weapon Appeal penalty-free.',grant:sm=>{sm.appealWaivers=Number(sm.appealWaivers||0)+1;}},
  {id:'chaos',label:'Chaos Refresh',cost:3,glyph:'◉',detail:'Amend one Chaos decree.',grant:sm=>{sm.chaosRefreshes=Number(sm.chaosRefreshes||0)+1;}},
  {id:'rite',label:'Rite Refresh',cost:3,glyph:'✧',detail:'Amend one Odd Rite.',grant:sm=>{sm.riteRefreshes=Number(sm.riteRefreshes||0)+1;}},
  {id:'clemency',label:'Letter of Clemency',cost:4,glyph:'♢',detail:'Erase one Weapon Appeal penalty from the current encounter.',grant:sm=>{sm.clemencies=Number(sm.clemencies||0)+1;}},
  {id:'joint',label:'Joint Appeal',cost:6,glyph:'⚔⚔',detail:'Reroll both weapons once without an Appeal penalty.',grant:sm=>{sm.jointAppeals=Number(sm.jointAppeals||0)+1;}},
  {id:'freeboss',label:'Sanctioned Boss Kill',cost:8,glyph:'⚔',detail:'Kill one optional boss and remove it from future draws.',grant:sm=>{sm.freeBossKills=Number(sm.freeBossKills||0)+1;}},
  {id:'draw',label:'Covenant Draw',cost:3,glyph:'◇',detail:'One extra random Covenant reward. Taxes included.'}
];
// Remembrance boss (as the app names them) → weapons and shields Enia trades for it.
// Spell-only remembrances (Astel, Fortissax, Dancing Lion) have none.
const TC_REMEMBRANCE_WEAPONS={
  'Godrick the Grafted':['Axe of Godrick','Grafted Dragon'],
  'Rennala, Queen of the Full Moon':['Carian Regal Scepter'],
  'Starscourge Radahn':['Starscourge Greatsword','Lion Greatbow'],
  'Regal Ancestor Spirit':['Winged Greathorn'],
  'Rykard, Lord of Blasphemy':['Blasphemous Blade'],
  'Morgott, the Omen King':['Morgott’s Cursed Sword'],
  'Fire Giant':['Giant’s Red Braid'],
  'Mohg, Lord of Blood':['Mohgwyn’s Sacred Spear'],
  'Malenia, Blade of Miquella':['Hand of Malenia'],
  'Maliketh, the Black Blade':['Maliketh’s Black Blade'],
  'Dragonlord Placidusax':['Dragon King’s Cragblade'],
  'Godfrey, First Elden Lord / Hoarah Loux':['Axe of Godfrey'],
  'Rellana, Twin Moon Knight':['Rellana’s Twin Blades'],
  'Putrescent Knight':['Putrescence Cleaver'],
  'Commander Gaius':['Sword Lance'],
  'Scadutree Avatar':['Shadow Sunflower Blossom'],
  'Metyr, Mother of Fingers':['Staff of the Great Beyond','Gazing Finger'],
  'Midra, Lord of Frenzied Flame':['Greatsword of Damnation'],
  'Messmer the Impaler':['Spear of the Impaler'],
  'Romina, Saint of the Bud':['Poleblade of the Bud'],
  'Promised Consort Radahn':['Greatsword of Radahn (Lord)','Greatsword of Radahn (Light)']
};
// Weapons the regional pools don't carry get the same generic card the pools use
// for unique weapons; only the one infusable weapon differs.
const TC_REMEMBRANCE_WEAPON_META={
  'Sword Lance':{infusable:true,upgrade:'Smithing Stones'}
};
// smithingData keeps only known fields, so the purchase log is added explicitly.
const tcSmithingDataBeforeSurplus=smithingData;
smithingData=function(state){
  const base=tcSmithingDataBeforeSurplus(state),raw=state?.smithing||{};
  return Array.isArray(raw.shopLog)?{...base,shopLog:raw.shopLog.filter(e=>e&&typeof e==='object').slice(-TC_SHOP_LOG_LIMIT)}:base;
};
const tcShopName=s=>String(s||'').replace(/[’']/g,'\'').toLowerCase();
function tcShopItem(id){return TC_SHOP_ITEMS.find(item=>item.id===id)||null;}
function tcShopOpen(state){
  const acquired=new Set(smithingData(state).acquired);
  return TC_BELL_BEARINGS.every(b=>acquired.has(b.id));
}
function tcShopBusy(state){
  return Boolean((typeof tcSharedRewardDrawPending==='function'&&tcSharedRewardDrawPending(state))||(typeof tcSharedRewardUnresolved==='function'&&tcSharedRewardUnresolved(state)));
}
function tcShopLog(state){return Array.isArray(state?.smithing?.shopLog)?state.smithing.shopLog:[];}
function tcShopCopy(latest){
  return smithingCopy(typeof tcNormalizeRunState==='function'?tcNormalizeRunState(latest):latest);
}
function tcShopRecord(next,entry){
  next.smithing.shopLog=[...tcShopLog(next),entry].slice(-TC_SHOP_LOG_LIMIT);
}
function tcRegionalWeaponByName(name){
  const key=tcShopName(name);
  for(const region of Object.values(regions||{}))for(const weapon of region.weapons||[])if(tcShopName(weapon.name)===key)return weapon;
  return null;
}
function tcRemembranceWeaponBuild(name){
  const base=tcRegionalWeaponByName(name),meta=TC_REMEMBRANCE_WEAPON_META[name]||{};
  const weapon=base?{...base}:{name,type:'Remembrance weapon',native:'Native skill',upgrade:meta.upgrade||'Smithing path varies',requires:'',infusable:Boolean(meta.infusable)};
  return buildFromWeapon(weapon);
}
function tcRemembranceWeaponChoices(state){
  const out=[];
  for(const boss of requiredRemembrances(state)){
    if(!hasRemembrance(state,boss))continue;
    for(const weapon of TC_REMEMBRANCE_WEAPONS[boss]||[])out.push({boss,weapon});
  }
  return out;
}
function tcRemembranceSwapBlocked(state){
  const c=state?.current;
  if(!c||state.runComplete||state.regionComplete)return 'There is no fight to arm right now.';
  if(typeof tcEncounterMutationLocked==='function'&&tcEncounterMutationLocked(state))return 'Weapons lock after the first world victory.';
  if((c.worldClears||[]).length)return 'Weapons lock after the first world victory.';
  if(state.current?.postBattleReport||c.battleReportDraft)return 'Finish the battle report first.';
  return '';
}
// Builds a purchase from the latest saved state. Returns null when it no longer applies.
function tcBuildShopPurchase(latest,purchaseId,itemId,actor,options={}){
  if(!latest||!purchaseId)return null;
  const item=tcShopItem(itemId);if(!item)return null;
  if(!tcShopOpen(latest)||tcShopBusy(latest))return null;
  if(tcShopLog(latest).some(entry=>entry?.id===purchaseId))return null;
  const sm=smithingData(latest);
  if(sm.favor<item.cost)return null;
  const next=tcShopCopy(latest),now=new Date().toISOString();
  next.smithing.favor=sm.favor-item.cost;
  const entry={id:purchaseId,item:item.id,cost:item.cost,by:actor,at:now};
  if(item.id==='remembrance'){
    if(tcRemembranceSwapBlocked(latest))return null;
    const slot=options.slot;if(slot!=='chase'&&slot!=='morgan')return null;
    const choice=tcRemembranceWeaponChoices(latest).find(x=>x.weapon===options.weapon);if(!choice)return null;
    const c=next.current,other=slot==='chase'?'morgan':'chase';
    if(tcShopName(c?.[other]?.name)===tcShopName(choice.weapon)||tcShopName(c?.[slot]?.name)===tcShopName(choice.weapon))return null;
    const build=tcRemembranceWeaponBuild(choice.weapon);
    if(weaponBlockedByTarget(build,c.target))return null;
    const replaced=c[slot]?.name||'';
    c[slot]=build;
    c.remembranceSwaps=[...(Array.isArray(c.remembranceSwaps)?c.remembranceSwaps:[]),{slot,weapon:choice.weapon,boss:choice.boss,replaced,cost:item.cost,by:actor,at:now}];
    entry.detail=`${playerLabel(slot,next)}: ${replaced} → ${choice.weapon}`;
    next.lastAction=`${actor} bought ${choice.weapon} from Hewg’s Surplus for ${playerLabel(slot,next)} (${item.cost} Favor). ${replaced} is set aside for this fight.`;
  }else if(item.id==='draw'){
    const reward=drawCovenantReward(next);
    entry.detail=reward.label;entry.reward={kind:reward.kind,label:reward.label,detail:reward.detail};
    next.lastAction=`${actor} bought a Covenant Draw from Hewg’s Surplus (${item.cost} Favor): ${reward.label}.`;
  }else{
    item.grant(next.smithing);
    entry.detail=item.label;
    next.lastAction=`${actor} bought ${/^[AEIOU]/.test(item.label)?'an':'a'} ${item.label} from Hewg’s Surplus for ${item.cost} Favor.`;
  }
  tcShopRecord(next,entry);
  return next;
}
function tcShopPurchaseId(){return 'shop-'+(crypto?.randomUUID?.()||Date.now().toString(36)+Math.random().toString(36).slice(2));}

function tcShopMarkup(state){
  const sm=smithingData(state);
  if(!tcShopOpen(state)){
    const have=sm.acquired.filter(id=>TC_BELL_BEARINGS.some(b=>b.id===id)).length;
    return `<div class="tc-shop locked"><div class="tc-kicker ember">Hewg’s Surplus</div><div class="tc-muted">Opens once all ${TC_BELL_BEARINGS.length} Miner’s Bell Bearings are claimed · ${have}/${TC_BELL_BEARINGS.length}.</div></div>`;
  }
  const busy=tcShopBusy(state),swapBlock=tcRemembranceSwapBlocked(state),choices=tcRemembranceWeaponChoices(state);
  const rows=TC_SHOP_ITEMS.map(item=>{
    let why='';
    if(busy)why='Resolve the shared Covenant reward first.';
    else if(sm.favor<item.cost)why=`Needs ${item.cost} Favor · you hold ${sm.favor}`;
    else if(item.id==='remembrance'&&swapBlock)why=swapBlock;
    else if(item.id==='remembrance'&&!choices.length)why='No remembrance weapons earned yet.';
    return `<button type="button" class="tc-shop-item" data-shop-item="${item.id}" ${why?'disabled':''}>
      <span class="tc-shop-glyph" aria-hidden="true">${item.glyph}</span>
      <span class="tc-shop-text"><strong>${h(item.label)}</strong><small>${h(item.detail)}</small>${why?`<em>${h(why)}</em>`:''}</span>
      <span class="tc-shop-price">${item.cost}<i>Favor</i></span>
    </button>`;
  }).join('');
  const last=tcShopLog(state).slice(-3).reverse();
  return `<div class="tc-shop"><div class="tc-shop-head"><div><div class="tc-kicker ember">Hewg’s Surplus</div><div class="tc-muted">Every bearing is home. Hewg will sell nearly anything for Favor.</div></div><div class="tc-shop-purse">✦ ${sm.favor}</div></div>
    <div class="tc-shop-list">${rows}</div>
    ${last.length?`<div class="tc-shop-log">${last.map(e=>`<div>${h(personalizePlayers(e.by||'',state))} · ${h(e.detail||tcShopItem(e.item)?.label||e.item)} · ${Number(e.cost)||0} Favor</div>`).join('')}</div>`:''}
  </div>`;
}

const tcSmithingLedgerBeforeSurplus=smithingLedgerMarkup;
smithingLedgerMarkup=function(state){
  const html=tcSmithingLedgerBeforeSurplus(state);
  // The shop sits just under the Favor total so the currency and its use read together.
  const marker='<div class="tc-kicker ember" style="margin-top:18px">bell bearing ledger</div>';
  return html.includes(marker)?html.replace(marker,tcShopMarkup(state)+marker):html+tcShopMarkup(state);
};
const tcSmithingHubBeforeSurplus=smithingHubMarkup;
smithingHubMarkup=function(state){
  const html=tcSmithingHubBeforeSurplus(state),sm=smithingData(state);
  if(!tcShopOpen(state)||sm.activeContract)return html;
  return `<button class="tc-forge-notice quiet" data-smith-action="ledger" type="button"><div class="tc-forge-glyph">⚒</div><div><div class="tc-kicker ember">hewg’s surplus is open</div><div class="tc-forge-title">${sm.favor} Smithing Favor</div><div class="tc-muted">Masterwork Tokens, remembrance weapons, Covenant documents and draws.</div></div><span class="tc-forge-arrow">›</span></button>`;
};

let tcShopBusyClick=false;
async function tcShopCommit(itemId,options={}){
  if(tcShopBusyClick)return null;
  const purchaseId=tcShopPurchaseId(),actor=playerName();
  const build=latest=>tcBuildShopPurchase(latest,purchaseId,itemId,actor,options);
  const staged=build(run.state);
  if(!staged){setToast('That purchase is no longer available.');return null;}
  tcShopBusyClick=true;
  try{
    const item=tcShopItem(itemId);
    const saved=await commit(staged,{retryBuilder:build,successToast:item.id==='draw'?'':`${item.label} bought.`});
    if(!saved)return null;
    return tcShopLog(run.state).find(e=>e.id===purchaseId)||null;
  }finally{tcShopBusyClick=false;}
}
function tcOpenShopConfirm(item){
  const sm=smithingData(run.state);
  const el=tcStrategicOverlay(item.label,`<p>${h(item.detail)}</p><p>Costs <strong>${item.cost} Favor</strong>. You hold ${sm.favor}; ${sm.favor-item.cost} after.</p>`,`<button type="button" class="btn gold" data-shop-confirm>Buy for ${item.cost} Favor</button>`);
  el.querySelector('.tc-kicker').textContent='Hewg’s Surplus';
  el.querySelector('[data-shop-confirm]').addEventListener('click',async event=>{
    event.currentTarget.disabled=true;
    const entry=await tcShopCommit(item.id);
    el.remove();
    if(entry?.reward){
      const r=entry.reward,box=tcStrategicOverlay(r.label,`<div class="tc-reward-result ${h(r.kind)}"><p>${h(r.detail)}</p></div>`);
      box.querySelector('.tc-kicker').textContent='Covenant Draw';
      box.querySelector('[data-close-strategy]').textContent='Done';
    }
  });
}
function tcOpenRemembranceShop(slot){
  const state=run.state,c=state.current,choices=tcRemembranceWeaponChoices(state);
  const chosen=slot||'';
  const players=['chase','morgan'].map(s=>`<button type="button" class="btn ${s===chosen?'gold':'ghost'}" data-shop-slot="${s}">${h(playerLabel(s,state))}<small style="display:block;opacity:.75">${h(c?.[s]?.name||'')}</small></button>`).join('');
  const list=chosen?choices.map(x=>{
    const other=chosen==='chase'?'morgan':'chase',same=tcShopName(c?.[chosen]?.name)===tcShopName(x.weapon),taken=tcShopName(c?.[other]?.name)===tcShopName(x.weapon);
    const blocked=weaponBlockedByTarget(tcRemembranceWeaponBuild(x.weapon),c.target);
    const why=same?'Already wielded':taken?`${playerLabel(other,state)} has it`:blocked?`Not against ${c.target.name}`:'';
    return `<button type="button" class="tc-strategy-item" data-shop-weapon="${h(x.weapon)}" ${why?'disabled':''}><strong>${h(x.weapon)}</strong><span>${h(x.boss)}${why?` · ${h(why)}`:''}</span></button>`;
  }).join(''):'';
  const el=tcStrategicOverlay('Remembrance Weapon',`<p>Choose who carries it. Their current weapon is set aside for this fight only; the next encounter draws normally. 8 Favor, no Appeal penalty.</p><div class="tc-strategy-actions">${players}</div>${chosen?`<div class="tc-strategy-list">${list}</div>`:''}`);
  el.querySelector('.tc-kicker').textContent='Hewg’s Surplus';
  el.querySelectorAll('[data-shop-slot]').forEach(btn=>btn.addEventListener('click',()=>tcOpenRemembranceShop(btn.dataset.shopSlot)));
  el.querySelectorAll('[data-shop-weapon]').forEach(btn=>btn.addEventListener('click',async()=>{
    el.querySelectorAll('button').forEach(b=>b.disabled=true);
    const entry=await tcShopCommit('remembrance',{slot:chosen,weapon:btn.dataset.shopWeapon});
    el.remove();
    if(entry){uiScreen='encounter';renderRun();}
  }));
}
document.addEventListener('click',event=>{
  const btn=event.target.closest('[data-shop-item]');if(!btn||btn.disabled)return;
  event.preventDefault();
  const item=tcShopItem(btn.dataset.shopItem);if(!item)return;
  if(item.id==='remembrance')tcOpenRemembranceShop(typeof tcMasterworkSlotForIdentity==='function'?tcMasterworkSlotForIdentity()||'':'');
  else tcOpenShopConfirm(item);
});
/* --- End Hewg's Surplus --- */
