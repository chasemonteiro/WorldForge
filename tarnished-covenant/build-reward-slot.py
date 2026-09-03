from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# Covenant reward machine: visible reward feedback plus a rare comic tax result.
# -----------------------------------------------------------------------------
old="""function drawCovenantReward(state){
  const sm=state.smithing || (state.smithing=smithingData(state));
  const roll=Math.random();
  if(roll<0.40){sm.favor+=1;return {kind:'favor',label:'+1 Smithing Favor'};}
  if(roll<0.45){sm.favor+=2;return {kind:'favor',label:'+2 Smithing Favor'};}
  if(roll<0.65){sm.chaosRefreshes+=1;return {kind:'chaos',label:'Chaos Refresh'};}
  if(roll<0.85){sm.riteRefreshes+=1;return {kind:'rite',label:'Rite Refresh'};}
  sm.appealWaivers+=1;return {kind:'appeal',label:'Appeal Waiver'};
}"""
new="""const TC_COVENANT_TAXES=[
  {label:'Bone Dart Audit',detail:'Before the next encounter, spend half of your currently held runes on Bone Darts. If the merchant runs out, the bureaucracy accepts as many as you can buy.'},
  {label:'Merchant Compliance',detail:'Before the next encounter, spend 25% of your currently held runes on throwables, arrows, or bolts. The Covenant requires receipts.'},
  {label:'Inventory Tithe',detail:'Before the next encounter, buy at least 20 Rainbow Stones or Glowstones. This improves nothing.'},
  {label:'Procurement Error',detail:'Spend 5,000 runes on consumables you do not intend to use. If you have fewer than 5,000, spend what you have.'}
];
function drawCovenantReward(state){
  const sm=state.smithing || (state.smithing=smithingData(state));
  const roll=Math.random();
  if(roll<0.38){sm.favor+=1;return {kind:'favor',label:'+1 Smithing Favor',detail:'One mark of Smithing Favor is added to the Covenant treasury.'};}
  if(roll<0.43){sm.favor+=2;return {kind:'favor2',label:'+2 Smithing Favor',detail:'A rare double grant. The accountants are furious.'};}
  if(roll<0.61){sm.chaosRefreshes+=1;return {kind:'chaos',label:'Chaos Refresh',detail:'Reroll one unopened Chaos trigger on a future encounter.'};}
  if(roll<0.79){sm.riteRefreshes+=1;return {kind:'rite',label:'Rite Refresh',detail:'Reroll one Odd Rite on a future encounter.'};}
  if(roll<0.94){sm.appealWaivers+=1;return {kind:'appeal',label:'Appeal Waiver',detail:'Your next Weapon Appeal is penalty-free.'};}
  const tax=pick(TC_COVENANT_TAXES);
  return {kind:'tax',label:tax.label,detail:tax.detail};
}
function tcRewardIcon(kind){
  const icons={favor:'✦',favor2:'✦✦',chaos:'◉',rite:'✧',appeal:'⚖',tax:'☠'};
  return icons[kind]||'◇';
}
function tcRewardClass(kind){return kind==='tax'?'tax':kind==='chaos'?'chaos':kind==='rite'?'rite':kind==='appeal'?'appeal':'favor';}
"""
if old not in s: raise SystemExit('drawCovenantReward target missing')
s=s.replace(old,new,1)

# Transient reveal state is intentionally local: shared progression is saved first,
# while the device that submitted the report gets the theatrical reveal.
marker='let postBattleReport = null;'
if marker in s:
    s=s.replace(marker, marker+'\nlet pendingRewardReveal = null;',1)
else:
    # tolerate slightly different spacing/name from earlier patches
    marker='let postBattleReport=null;'
    if marker not in s: raise SystemExit('postBattleReport state marker missing')
    s=s.replace(marker, marker+'\nlet pendingRewardReveal=null;',1)

# Preserve full reward objects long enough to animate them, while still archiving labels.
s=s.replace("nc.postBattleRewards=rewards.map(x=>x.label);", "nc.postBattleRewards=rewards.map(x=>x.label);",1)
s=s.replace("nc.favorEarned=rewards.filter(x=>x.kind==='favor').reduce((sum,x)=>sum+(x.label.startsWith('+2')?2:1),0);",
            "nc.favorEarned=rewards.filter(x=>x.kind==='favor'||x.kind==='favor2').reduce((sum,x)=>sum+(x.kind==='favor2'?2:1),0);",1)

old="""  const completed=completeEncounter(nextState,playerName());
  postBattleReport=null;
  if(!completed.regionComplete&&!completed.runComplete&&completed.current){pendingRevealId=completed.current.id;uiScreen='encounter';}
  const rewardText=rewards.length?`Rewards: ${rewards.map(x=>x.label).join(' · ')}`:'Post-battle report filed.';
  try{await commit(completed,{successToast:rewardText});}
  finally{window.__tcReportBusy=false;}
}"""
new="""  const completed=completeEncounter(nextState,playerName());
  postBattleReport=null;
  if(!completed.regionComplete&&!completed.runComplete&&completed.current){pendingRevealId=completed.current.id;uiScreen='encounter';}
  pendingRewardReveal=rewards.length?{rewards:structuredClone(rewards),boss:c.target?.name||'Enemy Felled',index:0,spinning:true}:null;
  const rewardText=rewards.length?'Covenant reward draw ready.':'Post-battle report filed.';
  try{
    const saved=await commit(completed,{successToast:rewardText});
    if(!saved)pendingRewardReveal=null;
  }
  finally{window.__tcReportBusy=false;}
}"""
if old not in s: raise SystemExit('finalize reward commit block missing')
s=s.replace(old,new,1)

# Reward reveal takes precedence after the successful save and before travel/new decree.
old="""function renderRun() {
  const state=run.state;
  if(postBattleReport?.encounterId===state.current?.id) return renderPostBattleReport();"""
new="""function renderRun() {
  const state=run.state;
  if(pendingRewardReveal?.rewards?.length) return renderRewardMachine();
  if(postBattleReport?.encounterId===state.current?.id) return renderPostBattleReport();"""
if old not in s: raise SystemExit('renderRun reward hook missing')
s=s.replace(old,new,1)

# Insert machine renderer before appeal menu.
marker='function showAppealMenu(){'
if marker not in s: raise SystemExit('appeal marker missing')
renderer=r'''
function renderRewardMachine(){
  const data=pendingRewardReveal;
  if(!data?.rewards?.length){pendingRewardReveal=null;return renderRun();}
  const current=data.rewards[data.index]||data.rewards[0];
  const total=data.rewards.length;
  const symbols=['✦','◉','✧','⚖','☠','◇','✦','✧','◉'];
  app.innerHTML=`<section class="tc-reward-machine">
    <div class="tc-reward-kicker">Covenant Treasury</div>
    <div class="tc-reward-title">DRAW ${data.index+1} <span>OF ${total}</span></div>
    <div class="tc-reward-boss">Victory over ${h(data.boss||'the enemy')}</div>
    <div class="tc-slot-frame" aria-live="polite">
      <div class="tc-slot-reel" data-reel="0">${symbols.map(x=>`<span>${x}</span>`).join('')}</div>
      <div class="tc-slot-reel" data-reel="1">${symbols.slice().reverse().map(x=>`<span>${x}</span>`).join('')}</div>
      <div class="tc-slot-reel" data-reel="2">${symbols.slice(3).concat(symbols.slice(0,3)).map(x=>`<span>${x}</span>`).join('')}</div>
    </div>
    <div id="tcRewardResult" class="tc-reward-result ${tcRewardClass(current.kind)}" hidden>
      <div class="tc-reward-icon">${tcRewardIcon(current.kind)}</div>
      <div class="tc-reward-type">${current.kind==='tax'?'Covenant Tax':'Reward Acquired'}</div>
      <div class="tc-reward-name">${h(current.label)}</div>
      <div class="tc-reward-detail">${h(current.detail||'The Covenant has spoken.')}</div>
    </div>
    <button id="tcRewardContinue" class="btn gold" disabled>${data.index+1<total?'Draw Next Reward':'Continue'}</button>
    <div class="tc-reward-quip">${current.kind==='tax'?'The Covenant giveth. The Covenant also has purchasing requirements.':'Honor has been converted into administratively approved loot.'}</div>
  </section>`;
  const reels=[...document.querySelectorAll('.tc-slot-reel')];
  const result=document.querySelector('#tcRewardResult');
  const btn=document.querySelector('#tcRewardContinue');
  const reduced=window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
  const finish=()=>{
    reels.forEach((reel,i)=>{reel.classList.remove('spinning');reel.innerHTML=`<span class="winner">${tcRewardIcon(current.kind)}</span>`;});
    result.hidden=false;result.classList.add('revealed');btn.disabled=false;data.spinning=false;
  };
  if(reduced){finish();}
  else{
    reels.forEach((reel,i)=>{reel.classList.add('spinning');reel.style.setProperty('--tc-spin-delay',`${i*110}ms`);});
    window.setTimeout(finish,1250);
  }
  btn.addEventListener('click',()=>{
    if(data.spinning)return;
    if(data.index+1<total){data.index+=1;data.spinning=true;renderRewardMachine();return;}
    pendingRewardReveal=null;renderRun();
  });
}
'''
s=s.replace(marker,renderer+'\n'+marker,1)

css=r'''
/* --- Covenant reward slot machine --- */
.tc-reward-machine{min-height:calc(100dvh - 82px);display:flex;flex-direction:column;justify-content:center;max-width:620px;margin:auto;padding:20px 16px 98px;text-align:center}
.tc-reward-kicker{font:850 11px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.18em;color:var(--gold);margin-bottom:8px}.tc-reward-title{font:400 clamp(30px,9vw,46px)/1 Georgia,serif;color:var(--ink);letter-spacing:.04em}.tc-reward-title span{font-size:.42em;color:var(--ash);letter-spacing:.12em}.tc-reward-boss{margin:8px auto 18px;color:var(--ash);font-size:15px;font-style:italic}
.tc-slot-frame{position:relative;display:grid;grid-template-columns:repeat(3,1fr);gap:8px;max-width:430px;width:100%;margin:0 auto 17px;padding:10px;border:1px solid rgba(198,161,90,.42);background:linear-gradient(180deg,rgba(35,29,18,.78),rgba(8,7,5,.92));box-shadow:inset 0 0 0 1px rgba(224,193,123,.08)}
.tc-slot-frame:before,.tc-slot-frame:after{content:"";position:absolute;left:7%;right:7%;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);opacity:.55}.tc-slot-frame:before{top:-5px}.tc-slot-frame:after{bottom:-5px}
.tc-slot-reel{height:96px;overflow:hidden;border:1px solid var(--line);background:radial-gradient(circle at 50% 35%,rgba(198,161,90,.12),rgba(5,5,4,.94));display:flex;flex-direction:column;align-items:center;font:400 48px/96px Georgia,serif;color:var(--gold-bright);position:relative}.tc-slot-reel span{height:96px;min-height:96px;display:grid;place-items:center;width:100%}.tc-slot-reel.spinning{animation:tcReelShake .16s linear infinite;animation-delay:var(--tc-spin-delay)}.tc-slot-reel.spinning span{animation:tcSymbols .48s linear infinite}.tc-slot-reel .winner{font-size:49px;text-shadow:0 0 24px rgba(224,193,123,.24)}
@keyframes tcSymbols{from{transform:translateY(0)}to{transform:translateY(-288px)}}@keyframes tcReelShake{0%,100%{filter:brightness(.88)}50%{filter:brightness(1.25)}}
.tc-reward-result{margin:4px auto 15px;padding:16px 15px 17px;width:100%;border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:linear-gradient(90deg,transparent,rgba(198,161,90,.07),transparent)}.tc-reward-result.revealed{animation:tcRewardIn .32s ease-out both}@keyframes tcRewardIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}.tc-reward-result.tax{border-color:rgba(201,102,90,.42);background:linear-gradient(90deg,transparent,rgba(110,28,22,.16),transparent)}
.tc-reward-icon{font:400 42px/1 Georgia,serif;color:var(--gold-bright);margin-bottom:6px}.tc-reward-result.tax .tc-reward-icon,.tc-reward-result.tax .tc-reward-name{color:#e17e71}.tc-reward-type{font:850 9px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.16em;color:var(--ash)}.tc-reward-name{font:400 27px/1.08 Georgia,serif;color:var(--gold-bright);margin:7px 0}.tc-reward-detail{font-size:15px;line-height:1.45;color:#d4cab8;max-width:500px;margin:auto}.tc-reward-machine .btn{max-width:430px;margin:0 auto}.tc-reward-quip{font-size:12px;line-height:1.4;color:var(--ash);font-style:italic;margin:10px auto 0;max-width:470px}
@media(max-width:380px){.tc-slot-reel{height:82px;font-size:41px;line-height:82px}.tc-slot-reel span{height:82px;min-height:82px}.tc-slot-reel .winner{font-size:43px}.tc-reward-detail{font-size:14px}}@media(prefers-reduced-motion:reduce){.tc-slot-reel,.tc-slot-reel span,.tc-reward-result{animation:none!important}}
'''
if '</style>' not in s: raise SystemExit('style end missing')
s=s.replace('</style>',css+'\n</style>',1)

for invariant in ['TC_COVENANT_TAXES','function renderRewardMachine()','pendingRewardReveal','Bone Dart Audit','Covenant Treasury']:
    if invariant not in s: raise SystemExit('slot invariant missing: '+invariant)

p.write_text(s)
