from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# One challenge ruleset: remove the difficulty chooser and force the hard ruleset.
s=re.sub(r'''\s*<div>\s*<label class="label" for="severity">difficulty</label>\s*<select id="severity">.*?</select>\s*</div>''','',s,count=1,flags=re.S)
s=s.replace("severity: document.querySelector('#severity').value,","severity: 'cursed',",1)

# New encounters use anti-repeat pickers instead of raw replacement RNG.
s=s.replace('const weird = pick(weirdness);','const weird = tcPickRite(state);',1)
s=s.replace('chaosTrigger: pick(chaosTriggers),','chaosTrigger: tcPickChaosTrigger(state),',1)

# Carry a one-fight debt into the next generated encounter, then consume it.
s=s.replace('next.current = newEncounter(next);\n  return next;',"const tcDebt=next.pendingDebt||null;\n  next.current = newEncounter(next);\n  if(tcDebt){next.current.covenantDebt=tcDebt;next.pendingDebt=null;}\n  return next;",1)

# Override the reward table: raw Favor is rarer; refreshes stay common; taxes rise to 10%.
pat=r'''function drawCovenantReward\(state\)\{.*?\n\}'''
reward=r'''function drawCovenantReward(state){
  const sm=state.smithing || (state.smithing=smithingData(state));
  const roll=Math.random();
  if(roll<0.20){sm.favor+=1;return {kind:'favor',label:'+1 Smithing Favor',detail:'One mark of Smithing Favor. Try not to spend it all in one tunnel.'};}
  if(roll<0.23){sm.favor+=2;return {kind:'favor2',label:'+2 Smithing Favor',detail:'Two marks. Administrative error suspected.'};}
  if(roll<0.47){sm.chaosRefreshes+=1;return {kind:'chaos',label:'Chaos Refresh',detail:'Amend one Chaos decree. Repeated amendments get expensive.'};}
  if(roll<0.71){sm.riteRefreshes+=1;return {kind:'rite',label:'Rite Refresh',detail:'Amend one Odd Rite. The Covenant keeps a fee schedule.'};}
  if(roll<0.79){sm.appealWaivers+=1;return {kind:'appeal',label:'Appeal Waiver',detail:'Your next Weapon Appeal is penalty-free.'};}
  if(roll<0.90){sm.aviaryTickets+=1;return {kind:'aviary',label:'Dynasty Frequent Flier',detail:'Grants 5 sanctioned trips to the bird. The bird remains a valued member of the economy.'};}
  const tax=pick(TC_COVENANT_TAXES);
  return {kind:'tax',label:tax.label,detail:tax.detail};
}'''
s,n=re.subn(pat,reward,s,count=1,flags=re.S)
if n!=1: raise SystemExit('reward table override target missing')

# Add hard-mode selection, family cooldowns, escalating refresh costs, forfeits and debts.
marker='function smithingFavorMarkup(state){'
if marker not in s: raise SystemExit('smithing marker missing')
helpers=r'''
function tcTierRank(t){return t==='Grand'?3:t==='True'?2:1;}
function tcChaosTier(text){
  if((TC_CHAOS_LATE||[]).includes(text)||String(text).startsWith('NEXT ENCOUNTER DEBT:')||String(text).startsWith('DOUBLE DECREE'))return 3;
  if((TC_CHAOS_MID||[]).includes(text))return 2;
  return 1;
}
function tcFamily(text){
  const t=String(text||'').toLowerCase();
  if(/heal|flask|crimson|cerulean|physick/.test(t))return 'healing';
  if(/roll|dodge|sprint|jump|movement|stand still|walk/.test(t))return 'movement';
  if(/talisman|armor|helmet|heavy load|equip/.test(t))return 'equipment';
  if(/skill|ash of war|sorcer|incant|magic|fp/.test(t))return 'skills';
  if(/attack|heavy|light|critical|parry|block|hit/.test(t))return 'offense';
  if(/add|minion|both players|each player|opposite side|aggro/.test(t))return 'coordination';
  return 'misc';
}
function tcRecentHistory(state,n=12){return (state?.history||[]).slice(0,n);}
function tcPickChaosTrigger(state){
  const recent=tcRecentHistory(state,10).map(x=>x.chaosTrigger).filter(Boolean);
  let pool=chaosTriggers.filter(x=>!recent.includes(x));
  return pick(pool.length?pool:chaosTriggers);
}
function tcPickRite(state,minTier=2){
  const recent=tcRecentHistory(state,12);
  const names=new Set(recent.map(x=>x.oddRite?.name).filter(Boolean));
  const fams=new Set(recent.slice(0,4).map(x=>tcFamily(x.oddRite?.text||x.oddRite?.name)).filter(Boolean));
  let pool=weirdness.filter(w=>tcTierRank((typeof riteMeta==='function'?riteMeta(w):{}).tier||'True')>=minTier && !names.has(w[0]) && !fams.has(tcFamily(w[1])));
  if(!pool.length)pool=weirdness.filter(w=>tcTierRank((typeof riteMeta==='function'?riteMeta(w):{}).tier||'True')>=minTier && !names.has(w[0]));
  if(!pool.length)pool=weirdness.filter(w=>tcTierRank((typeof riteMeta==='function'?riteMeta(w):{}).tier||'True')>=minTier);
  const grand=pool.filter(w=>tcTierRank((typeof riteMeta==='function'?riteMeta(w):{}).tier||'True')===3);
  if(grand.length&&Math.random()<0.45)return pick(grand);
  return pick(pool);
}
const TC_CHAOS_DEBTS=[
 'NEXT ENCOUNTER DEBT: the first Crimson Flask use by each player is forbidden.',
 'NEXT ENCOUNTER DEBT: no Physick until the boss reaches 50% health.',
 'NEXT ENCOUNTER DEBT: one randomly chosen player begins at Heavy Load until the first stance break.',
 'NEXT ENCOUNTER DEBT: weapon skills are forbidden for the first 30 seconds.',
 'NEXT ENCOUNTER DEBT: the first failed dodge means no healing for 20 seconds.'
];
function tcPickEscalatingChaos(state,minTier=2){
  const recent=tcRecentHistory(state,12);
  const exact=new Set(recent.map(x=>x.chaosConsequence).filter(Boolean));
  const recentFamilies=new Set(recent.slice(0,4).map(x=>tcFamily(x.chaosConsequence)).filter(Boolean));
  const capstone=Boolean(state?.current?.target?.exit);
  const progress=Math.min(1,(state?.history?.length||0)/24);
  let tier=(Math.random() < (0.34 + progress*.20 + (capstone?.20:0)))?3:2;
  tier=Math.max(tier,minTier);
  let base=tier===3?[...TC_CHAOS_LATE,...TC_CHAOS_DEBTS]:[...TC_CHAOS_MID];
  let pool=base.filter(x=>!exact.has(x)&&!recentFamilies.has(tcFamily(x)));
  if(!pool.length)pool=base.filter(x=>!exact.has(x));
  if(!pool.length)pool=base;
  let first=pick(pool);
  const doubleChance=capstone?0.25:0.11+progress*.08;
  if(Math.random()<doubleChance && !String(first).startsWith('NEXT ENCOUNTER DEBT:')){
    let secondPool=[...TC_CHAOS_MID,...TC_CHAOS_LATE].filter(x=>x!==first&&tcChaosTier(x)>=Math.min(3,tier)&&tcFamily(x)!==tcFamily(first)&&!exact.has(x));
    if(secondPool.length){const second=pick(secondPool);first=`DOUBLE DECREE — ${first} SECOND DECREE — ${second}`;}
  }
  return first;
}
function rerollChaos(state,actor){
  const next=smithingCopy(state),c=next.current;if(!c)return next;
  if(!c.chaosTriggered){c.chaosTrigger=tcPickChaosTrigger(next);next.lastAction=`${actor} amended the Chaos trigger.`;return next;}
  const oldTier=tcChaosTier(c.chaosConsequence||'');
  c.chaosConsequence=tcPickEscalatingChaos(next,oldTier);
  c.chaosForfeited=false;c.smithingChaosFavor=false;
  next.lastAction=`${actor} amended an active Chaos decree. It did not get nicer.`;return next;
}
function rerollWeirdness(state,actor){
  const next=smithingCopy(state),c=next.current;if(!c)return next;
  const min=tcTierRank(c.weirdness?.tier||'True');const w=tcPickRite(next,min);const meta=riteMeta(w);
  c.weirdness={name:w[0],text:w[1],...meta};c.riteForfeited=false;c.smithingRiteFavor=false;
  next.lastAction=`${actor} amended the Rite. The replacement is no easier.`;return next;
}
function tcRefreshCost(c,kind){return Number(c?.[kind+'RefreshUses']||0)+1;}
function tcEncounterBoons(state){
  const sm=smithingData(state),c=state.current;if(!c)return '';
  const cc=tcRefreshCost(c,'chaos'),rc=tcRefreshCost(c,'rite');
  const chaosLabel=cc===1?'AMEND DECREE':cc===2?'AMEND AGAIN':'THE COVENANT IS LOSING PATIENCE';
  const riteLabel=rc===1?'AMEND RITE':rc===2?'AMEND AGAIN':'THE COVENANT IS LOSING PATIENCE';
  return `<div class="tc-earned-refreshes"><div class="tc-kicker">amendments & forfeits</div><div class="tc-earned-refresh-grid">
    <button type="button" data-use-boon="chaos" class="btn ghost small" ${sm.chaosRefreshes<cc?'disabled':''}>${chaosLabel} · ${cc} CHAOS REFRESH${cc===1?'':'ES'} (${sm.chaosRefreshes})</button>
    <button type="button" data-use-boon="rite" class="btn ghost small" ${sm.riteRefreshes<rc?'disabled':''}>${riteLabel} · ${rc} RITE REFRESH${rc===1?'':'ES'} (${sm.riteRefreshes})</button>
    <button type="button" data-forfeit-boon="chaos" class="btn text-btn small">Forfeit Chaos boon</button>
    <button type="button" data-forfeit-boon="rite" class="btn text-btn small">Forfeit Rite boon</button>
  </div></div>`;
}
async function useCovenantBoon(kind){
  if(window.__tcBoonBusy||!run?.state?.current)return;window.__tcBoonBusy=true;
  const key=kind==='chaos'?'chaosRefreshes':'riteRefreshes';const c=run.state.current;const cost=tcRefreshCost(c,kind);const sm=smithingData(run.state);
  if(Number(sm[key]||0)<cost){window.__tcBoonBusy=false;return setToast(`That amendment costs ${cost} Refreshes.`);}
  let staged=smithingCopy(run.state);staged.smithing[key]-=cost;staged.current[kind+'RefreshUses']=Number(staged.current[kind+'RefreshUses']||0)+1;
  staged=kind==='chaos'?rerollChaos(staged,playerName()):rerollWeirdness(staged,playerName());
  if(kind==='chaos')try{acknowledgedChaos.delete(staged.current.id)}catch{}
  try{await commit(staged,{successToast:`${kind==='chaos'?'Chaos':'Rite'} amended. ${cost} Refresh${cost===1?'':'es'} spent.`});}finally{window.__tcBoonBusy=false;}
}
async function tcForfeitBoon(kind){
  if(!run?.state?.current)return;const next=smithingCopy(run.state);next.current[kind==='chaos'?'chaosForfeited':'riteForfeited']=true;
  next.lastAction=`${playerName()} forfeited the ${kind==='chaos'?'Chaos':'Rite'} reward. No draw will be awarded.`;
  await commit(next,{successToast:'Potential boon forfeited. The Covenant has noted your cowardice.'});
}
'''
s=s.replace(marker,helpers+'\n'+marker,1)

# Active Chaos can create a debt for the next encounter.
old="""  next.current.chaosConsequence = rolledChaos;
  next.current.chaosFavor = 1;"""
new="""  next.current.chaosConsequence = rolledChaos;
  next.current.chaosFavor = 1;
  if(String(rolledChaos).startsWith('NEXT ENCOUNTER DEBT:')) next.pendingDebt=String(rolledChaos).replace('NEXT ENCOUNTER DEBT:','').trim();"""
if old not in s: raise SystemExit('trigger Chaos assignment missing')
s=s.replace(old,new,1)

# Show inherited debt in the encounter briefing.
needle='${c.penances?.length?`<details class="tc-penalty-summary">'
if needle in s:
    s=s.replace(needle,'${c.covenantDebt?`<div class="tc-feature debt"><div class="tc-kicker red">COVENANT DEBT · THIS ENCOUNTER</div><div class="tc-feature-title">${h(c.covenantDebt)}</div></div>`:\'\'}\n    '+needle,1)

# Forfeited challenges never create reward draws; archive the distinction.
s=s.replace("if(postBattleReport.rite===true && riteDraws>0 && !nc.smithingRiteFavor){","if(postBattleReport.rite===true && !nc.riteForfeited && riteDraws>0 && !nc.smithingRiteFavor){",1)
s=s.replace("if(postBattleReport.chaos===true && nc.chaosTriggered && chaosDraws>0 && !nc.smithingChaosFavor){","if(postBattleReport.chaos===true && !nc.chaosForfeited && nc.chaosTriggered && chaosDraws>0 && !nc.smithingChaosFavor){",1)
s=s.replace("rewards: structuredClone(encounter?.postBattleRewards || [])","rewards: structuredClone(encounter?.postBattleRewards || []),\n    riteOutcome: encounter?.riteForfeited?'Forfeited':(encounter?.smithingRiteFavor?'Honored':'Failed'),\n    chaosOutcome: encounter?.chaosForfeited?'Forfeited':(encounter?.chaosTriggered?(encounter?.smithingChaosFavor?'Honored':'Failed'):'Not triggered')",1)

# Delegated forfeit controls.
listener=r'''
if(!window.__tcForfeitBound){window.__tcForfeitBound=true;document.addEventListener('click',e=>{const b=e.target.closest('[data-forfeit-boon]');if(b)tcForfeitBoon(b.dataset.forfeitBoon);});}
'''
pos=s.rfind('</script>')
if pos<0: raise SystemExit('script end missing')
s=s[:pos]+listener+'\n'+s[pos:]

css=r'''
/* --- challenge-first ruleset --- */
.tc-feature.debt{margin:10px 0;border-color:rgba(201,102,90,.5);background:rgba(90,24,20,.13)}
.tc-earned-refresh-grid{grid-template-columns:1fr 1fr}.tc-earned-refresh-grid .text-btn{min-height:38px;color:#a99f8d}
@media(max-width:430px){.tc-earned-refresh-grid{grid-template-columns:1fr}}
'''
s=s.replace('</style>',css+'\n</style>',1)

for x in ['tcPickRite(state)','tcPickChaosTrigger(state)','TC_CHAOS_DEBTS','tcRefreshCost','data-forfeit-boon','DOUBLE DECREE','severity: \'cursed\'']:
    if x not in s: raise SystemExit('challenge ruleset invariant missing: '+x)

p.write_text(s)
