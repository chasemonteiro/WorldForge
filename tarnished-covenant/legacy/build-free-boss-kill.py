from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# Sanctioned Boss Kill
#
# Rare shared reward. Grants one optional boss kill outside the normal Covenant
# encounter. The chosen boss is removed from future regional draws, but does NOT
# increment regional encounter progress or capstone progress.
# -----------------------------------------------------------------------------

# Remove the generated behavior layer when this final patch is rerun.
s=re.sub(
    r"\n?/\* --- Sanctioned Boss Kill reward --- \*/.*?"
    r"/\* --- End Sanctioned Boss Kill reward --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)
s=re.sub(
    r"\n?/\* --- Sanctioned Boss Kill styles --- \*/.*?"
    r"/\* --- End Sanctioned Boss Kill styles --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

# Persist the token through smithingData()/smithingCopy().
if 'freeBossKills: Number(raw.freeBossKills || 0)' not in s:
    old='    aviaryTickets: Number(raw.aviaryTickets || 0)\n  };'
    new='    aviaryTickets: Number(raw.aviaryTickets || 0),\n    freeBossKills: Number(raw.freeBossKills || 0)\n  };'
    if old not in s: raise SystemExit('smithingData aviary inventory target missing')
    s=s.replace(old,new,1)

# Reward probabilities remain challenge-first: Favor 23%, Refreshes 48%, Appeal
# 8%, Frequent Flier 6%, Sanctioned Boss Kill 5%, Covenant Tax 10%.
pat=re.compile(r"function drawCovenantReward\(state\)\{.*?\n\}",re.S)
reward=r'''function drawCovenantReward(state){
  const sm=state.smithing || (state.smithing=smithingData(state));
  const roll=Math.random();
  if(roll<0.20){sm.favor+=1;return {kind:'favor',label:'+1 Smithing Favor',detail:'One mark of Smithing Favor. Try not to spend it all in one tunnel.'};}
  if(roll<0.23){sm.favor+=2;return {kind:'favor2',label:'+2 Smithing Favor',detail:'Two marks. Administrative error suspected.'};}
  if(roll<0.47){sm.chaosRefreshes+=1;return {kind:'chaos',label:'Chaos Refresh',detail:'Amend one Chaos decree. Repeated amendments get expensive.'};}
  if(roll<0.71){sm.riteRefreshes+=1;return {kind:'rite',label:'Rite Refresh',detail:'Amend one Odd Rite. The Covenant keeps a fee schedule.'};}
  if(roll<0.79){sm.appealWaivers+=1;return {kind:'appeal',label:'Appeal Waiver',detail:'Your next Weapon Appeal is penalty-free.'};}
  if(roll<0.85){sm.aviaryTickets+=1;return {kind:'aviary',label:'Dynasty Frequent Flier',detail:'Grants 5 sanctioned trips to the bird. The bird remains a valued member of the economy.'};}
  if(roll<0.90){sm.freeBossKills+=1;return {kind:'freeboss',label:'Sanctioned Boss Kill',detail:'Kill one optional boss of your choice in the current or a previously reached region, then remove it from future Covenant encounter draws. Does not advance regional progression.'};}
  const tax=pick(TC_COVENANT_TAXES);
  return {kind:'tax',label:tax.label,detail:tax.detail};
}'''
s,n=pat.subn(reward,s,count=1)
if n!=1: raise SystemExit('drawCovenantReward target missing')

# Show a distinct reward glyph.
s=s.replace(
    "const icons={favor:'✦',favor2:'✦✦',chaos:'◉',rite:'✧',appeal:'⚖',aviary:'✈',tax:'☠'};",
    "const icons={favor:'✦',favor2:'✦✦',chaos:'◉',rite:'✧',appeal:'⚖',aviary:'✈',freeboss:'⚔',tax:'☠'};",
)
s=s.replace(
    "kind==='aviary'?'aviary':'favor';",
    "kind==='aviary'?'aviary':kind==='freeboss'?'freeboss':'favor';",
)

# The first-come shared reward system persists counters by delta. Include the
# new token so it is awarded once to shared state, just like the other boons.
s=s.replace(
    "const keys=['favor','chaosRefreshes','riteRefreshes','appealWaivers','aviaryTickets'];",
    "const keys=['favor','chaosRefreshes','riteRefreshes','appealWaivers','aviaryTickets','freeBossKills'];",
)

# A sanctioned kill removes a boss from the normal regional draw pool without
# being placed in encounter history (and therefore without increasing cleared).
defeated_pat=re.compile(
    r"function defeatedBossNames\(state, regionName = state\.region\) \{\s*"
    r"return new Set\(\(state\.history \|\| \[\]\)\s*"
    r"\.filter\(entry => entry\?\.region === regionName\)\s*"
    r"\.map\(entry => entry\.name\)\);\s*\}",
    re.S,
)
defeated_new=r'''function defeatedBossNames(state, regionName = state.region) {
  const names=new Set((state.history || [])
    .filter(entry => entry?.region === regionName)
    .map(entry => entry.name));
  for(const entry of (state.sanctionedBossKills||[])){
    if(entry?.region===regionName&&entry?.name)names.add(entry.name);
  }
  return names;
}'''
s,n=defeated_pat.subn(defeated_new,s,count=1)
if n!=1 and 'state.sanctionedBossKills||[]' not in s:
    raise SystemExit('defeatedBossNames target missing')

css=r'''
/* --- Sanctioned Boss Kill styles --- */
.tc-reward-result.freeboss{border-color:rgba(224,193,123,.55);background:radial-gradient(circle at 50% 15%,rgba(224,193,123,.14),transparent 52%)}
.tc-freeboss-btn{margin-top:10px}
.tc-freeboss-overlay{position:fixed;inset:0;z-index:1200;background:rgba(4,4,3,.88);backdrop-filter:blur(7px);display:flex;align-items:center;justify-content:center;padding:calc(env(safe-area-inset-top) + 18px) 16px calc(env(safe-area-inset-bottom) + 18px)}
.tc-freeboss-card{width:min(560px,100%);max-height:88svh;overflow:auto;padding:22px 18px;border:1px solid rgba(198,161,90,.44);background:linear-gradient(180deg,#19160f,#090806);clip-path:polygon(10px 0,calc(100% - 10px) 0,100% 10px,100% calc(100% - 10px),calc(100% - 10px) 100%,10px 100%,0 calc(100% - 10px),0 10px)}
.tc-freeboss-card h2{font-size:29px;font-weight:400;margin:6px 0 8px}.tc-freeboss-card p{color:#c8beac;font-size:13px;line-height:1.5;margin:0 0 16px}.tc-freeboss-card select{margin:6px 0 12px}.tc-freeboss-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px}.tc-freeboss-log{margin-top:11px;color:var(--ash);font-size:10px;line-height:1.45}
@media(max-width:430px){.tc-freeboss-actions{grid-template-columns:1fr}}
/* --- End Sanctioned Boss Kill styles --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Sanctioned Boss Kill reward --- */
function tcSanctionedBossKills(state){return Array.isArray(state?.sanctionedBossKills)?state.sanctionedBossKills:[];}
function tcFreeBossEligibleRegions(state){
  return Array.from(new Set([state?.region,...(state?.clearedRegions||[])]))
    .filter(region=>region&&regions?.[region]);
}
function tcEligibleFreeBossChoices(state){
  if(!state)return [];
  const activeName=state.current?.target?.name||'';
  const activeRegion=state.region;
  const out=[];
  for(const region of tcFreeBossEligibleRegions(state)){
    const defeated=defeatedBossNames(state,region);
    for(const name of (regions?.[region]?.bosses||[])){
      if(defeated.has(name))continue;
      if(region===activeRegion&&name===activeName)continue;
      out.push({region,name});
    }
  }
  return out;
}
function tcBuildSanctionedBossKill(latest,region,name,actor){
  const sm=smithingData(latest);
  if(Number(sm.freeBossKills||0)<1)return null;
  const eligible=tcEligibleFreeBossChoices(latest).some(x=>x.region===region&&x.name===name);
  if(!eligible)return null;
  const next=smithingCopy(latest);
  next.smithing.freeBossKills=Math.max(0,Number(next.smithing.freeBossKills||0)-1);
  next.sanctionedBossKills=[...tcSanctionedBossKills(next),{
    region,name,claimedBy:actor,claimedAt:new Date().toISOString()
  }];
  next.lastAction=`${actor} redeemed a Sanctioned Boss Kill for ${name} in ${region}. It was removed from future Covenant encounter draws.`;
  next.updatedAt=new Date().toISOString();
  return next;
}
function tcCloseFreeBossKillPicker(){document.querySelector('#tcFreeBossOverlay')?.remove();}
let tcFreeBossKillBusy=false;
function tcOpenFreeBossKillPicker(){
  tcCloseFreeBossKillPicker();
  const state=run?.state,sm=smithingData(state||{});
  if(Number(sm.freeBossKills||0)<1)return setToast('No Sanctioned Boss Kill available.');
  const choices=tcEligibleFreeBossChoices(state);
  if(!choices.length)return setToast('No eligible optional bosses are available in reached regions.');
  const groups=tcFreeBossEligibleRegions(state).map(region=>{
    const items=choices.map((x,i)=>({...x,i})).filter(x=>x.region===region);
    if(!items.length)return '';
    return `<optgroup label="${h(region)}">${items.map(x=>`<option value="${x.i}">${h(x.name)}</option>`).join('')}</optgroup>`;
  }).join('');
  const previous=tcSanctionedBossKills(state);
  const overlay=document.createElement('div');
  overlay.id='tcFreeBossOverlay';overlay.className='tc-freeboss-overlay';
  overlay.innerHTML=`<div class="tc-freeboss-card" role="dialog" aria-modal="true" aria-labelledby="tcFreeBossTitle">
    <div class="tc-kicker gold">Covenant Authorization</div><h2 id="tcFreeBossTitle">Sanctioned Boss Kill</h2>
    <p>Kill one optional boss outside the current Covenant assignment, then record it here. Only the current region or regions already reached are eligible. The boss leaves the future draw pool, but this does not advance regional or capstone progress.</p>
    <label class="label" for="tcFreeBossSelect">boss to sanction</label><select id="tcFreeBossSelect">${groups}</select>
    <div class="tc-freeboss-actions"><button type="button" id="tcConfirmFreeBoss" class="btn gold">Mark Killed · Spend 1</button><button type="button" id="tcCancelFreeBoss" class="btn ghost">Cancel</button></div>
    ${previous.length?`<div class="tc-freeboss-log">Already sanctioned: ${previous.slice(-4).map(x=>`${h(x.name)} · ${h(x.region)}`).join('<br>')}</div>`:''}
  </div>`;
  document.body.appendChild(overlay);
  overlay.addEventListener('click',e=>{if(e.target===overlay)tcCloseFreeBossKillPicker();});
  overlay.querySelector('#tcCancelFreeBoss')?.addEventListener('click',tcCloseFreeBossKillPicker);
  overlay.querySelector('#tcConfirmFreeBoss')?.addEventListener('click',async()=>{
    if(tcFreeBossKillBusy||pending)return;
    const idx=Number(overlay.querySelector('#tcFreeBossSelect')?.value);
    const choice=choices[idx];if(!choice)return;
    const actor=playerName();
    const staged=tcBuildSanctionedBossKill(run.state,choice.region,choice.name,actor);
    if(!staged)return setToast('That boss is no longer eligible.');
    tcFreeBossKillBusy=true;
    const btn=overlay.querySelector('#tcConfirmFreeBoss');if(btn){btn.disabled=true;btn.textContent='Recording…';}
    try{
      const saved=await commit(staged,{
        successToast:`${choice.name} removed from future Covenant draws.`,
        retryBuilder:(latest)=>tcBuildSanctionedBossKill(latest,choice.region,choice.name,actor)
      });
      if(saved)tcCloseFreeBossKillPicker();
    }finally{tcFreeBossKillBusy=false;}
  });
}

// Extend the existing boon ledger with the shared kill authorization.
covenantBoonMarkup=function(state){
  const sm=smithingData(state),sanctioned=tcSanctionedBossKills(state);
  return `<div class="tc-boon-ledger"><div class="tc-kicker ember">covenant boons</div><div class="tc-boon-grid">
    <div><strong>${sm.appealWaivers}</strong><span>Appeal Waiver${sm.appealWaivers===1?'':'s'}</span></div>
    <div><strong>${sm.chaosRefreshes}</strong><span>Chaos Refresh${sm.chaosRefreshes===1?'':'es'}</span></div>
    <div><strong>${sm.riteRefreshes}</strong><span>Rite Refresh${sm.riteRefreshes===1?'':'es'}</span></div>
    <div><strong>${sm.aviaryTickets}</strong><span>Dynasty Frequent Flier${sm.aviaryTickets===1?'':'s'}</span></div>
    <div><strong>${sm.freeBossKills}</strong><span>Sanctioned Boss Kill${sm.freeBossKills===1?'':'s'}</span></div>
  </div>${sm.freeBossKills>0?`<button type="button" class="btn ghost small tc-freeboss-btn" data-use-free-boss-kill>Redeem Sanctioned Boss Kill · ${sm.freeBossKills}</button>`:''}<div class="tc-muted">Waivers make the next weapon appeal penalty-free. Refreshes reroll a Rite or unopened Chaos decree. Frequent Fliers grant bird trips. Sanctioned Boss Kills remove an optional boss from future draws without advancing regional progress.${sanctioned.length?` · ${sanctioned.length} boss${sanctioned.length===1?' has':'es have'} been sanctioned.`:''}</div></div>`;
};
if(!window.__tcFreeBossKillBound){
  window.__tcFreeBossKillBound=true;
  document.addEventListener('click',e=>{if(e.target.closest('[data-use-free-boss-kill]'))tcOpenFreeBossKillPicker();});
}
/* --- End Sanctioned Boss Kill reward --- */
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

required=[
    'freeBossKills: Number(raw.freeBossKills || 0)',
    "kind:'freeboss',label:'Sanctioned Boss Kill'",
    "freeboss:'⚔'",
    "'aviaryTickets','freeBossKills'",
    'state.sanctionedBossKills||[]',
    'function tcEligibleFreeBossChoices(state)',
    'function tcBuildSanctionedBossKill(latest,region,name,actor)',
    'next.smithing.freeBossKills=Math.max(0,Number(next.smithing.freeBossKills||0)-1);',
    'next.sanctionedBossKills=[...tcSanctionedBossKills(next)',
    'Mark Killed · Spend 1',
    'does not advance regional or capstone progress',
]
for needle in required:
    if needle not in s: raise SystemExit('Sanctioned Boss Kill invariant missing: '+needle)

p.write_text(s)
print('Sanctioned Boss Kill reward added at 5% with backward/current-region redemption and no progress credit.')
