/* --- Covenant rules: twists chosen when a Covenant begins ---
   state.rules = {kitRoll, strikes}. Set only when a Covenant is created or a
   new one begins (both forms show the same toggles); a run without state.rules
   plays exactly as before. Region travel carries unknown keys, so rules follow
   the run from region to region.
   Kit roll: every new encounter deals each player two talismans (from the Build
   Lab's list, never two of one family). "Don't have it" swaps one for free.
   Strikes: a death counter per player per fight. The third death forces an
   Appeal for that player (normal penalty) unless weapons are already locked by
   a world victory; the counter then starts again. */
const TC_RULE_INFO={
  kitRoll:['Kit roll','Each fight also deals each of you two talismans to wear.'],
  strikes:['Strikes','Count your deaths. A third death in one fight re-draws that player’s weapon, with an Appeal penalty.']
};
function tcRules(state){const r=state?.rules;return {kitRoll:Boolean(r?.kitRoll),strikes:Boolean(r?.strikes)};}
function tcTwistsMarkup(){
  return `<div class="tc-twists"><span class="label">Twists</span>${Object.entries(TC_RULE_INFO).map(([key,[name,line]])=>`<button type="button" class="tc-set-row toggle tc-twist" role="switch" aria-checked="false" data-twist="${key}"><span><strong>${h(name)}</strong><small>${h(line)}</small></span><i class="tc-switch" aria-hidden="true"></i></button>`).join('')}</div>`;
}
function tcReadTwists(root=document){
  const rules={};root.querySelectorAll('[data-twist]').forEach(b=>{rules[b.dataset.twist]=b.getAttribute('aria-checked')==='true';});
  return Object.values(rules).some(Boolean)?rules:undefined;
}
document.addEventListener('click',event=>{
  const btn=event.target.closest('[data-twist]');if(!btn)return;
  event.preventDefault();const on=btn.getAttribute('aria-checked')!=='true';
  btn.setAttribute('aria-checked',String(on));btn.querySelector('.tc-switch')?.classList.toggle('on',on);
});

// Kit drawing.
function tcTalismanPool(){const info=window.tcBuildLabInfo;return Array.isArray(info?.talismanNames)?info.talismanNames.filter(Boolean):[];}
function tcTalismanFamily(name){const info=window.tcBuildLabInfo;return info?.talismanFamilyKey?info.talismanFamilyKey(name):String(name||'').toLowerCase().replace(/\s+\+\d+$/,'');}
function tcDrawTalisman(avoidFamilies){
  const pool=tcTalismanPool().filter(n=>!avoidFamilies.has(tcTalismanFamily(n)));
  return pool.length?pick(pool):'';
}
function tcDrawKit(){
  const kit={chase:[],morgan:[],swaps:0};
  for(const slot of ['chase','morgan']){
    const fam=new Set();
    for(let i=0;i<2;i++){const t=tcDrawTalisman(fam);if(t){kit[slot].push(t);fam.add(tcTalismanFamily(t));}}
  }
  return kit.chase.length||kit.morgan.length?kit:null;
}
function tcApplyRulesToEncounter(encounter,state){
  if(!encounter)return encounter;const r=tcRules(state);
  if(r.kitRoll&&!encounter.kit){const kit=tcDrawKit();if(kit)encounter.kit=kit;}
  if(r.strikes&&!encounter.strikes)encounter.strikes={chase:0,morgan:0,forced:[]};
  return encounter;
}
const tcNewEncounterBeforeRules=newEncounter;
newEncounter=function(state){return tcApplyRulesToEncounter(tcNewEncounterBeforeRules(state),state);};
const tcInitialRunStateBeforeRules=initialRunState;
initialRunState=function(options={}){
  const state=tcInitialRunStateBeforeRules(options);
  const rules=options?.rules&&typeof options.rules==='object'?{kitRoll:Boolean(options.rules.kitRoll),strikes:Boolean(options.rules.strikes)}:null;
  if(state&&rules&&(rules.kitRoll||rules.strikes)){state.rules=rules;tcApplyRulesToEncounter(state.current,state);}
  return state;
};
// The record keeps what was worn and how often you died.
const tcCompleteEncounterBeforeRules=completeEncounter;
completeEncounter=function(state,actor){
  const next=tcCompleteEncounterBeforeRules(state,actor),c=state?.current,entry=next?.history?.[0];
  if(entry&&c){
    if(c.kit)entry.kit={chase:[...(c.kit.chase||[])],morgan:[...(c.kit.morgan||[])]};
    if(c.strikes)entry.deaths={chase:Number(c.strikes.totalChase??c.strikes.chase??0),morgan:Number(c.strikes.totalMorgan??c.strikes.morgan??0)};
  }
  return next;
};

// Builders (pure; used with commit's retryBuilder).
function tcBuildKitSwap(latest,encounterId,slot,index,actor){
  if(!latest?.current||latest.current.id!==encounterId||!latest.current.kit)return null;
  const next=structuredClone(latest),kit=next.current.kit,list=kit[slot];if(!Array.isArray(list)||!list[index])return null;
  const fam=new Set([...kit.chase,...kit.morgan].map(tcTalismanFamily));
  const swapped=list[index],fresh=tcDrawTalisman(fam);if(!fresh)return null;
  list[index]=fresh;kit.swaps=Number(kit.swaps||0)+1;
  next.lastAction=`${actor} didn’t have ${swapped}; the kit dealt ${fresh} instead.`;
  next.updatedAt=new Date().toISOString();
  return next;
}
function tcBuildStrike(latest,encounterId,slot,delta,actor){
  if(!latest?.current||latest.current.id!==encounterId||!latest.current.strikes)return null;
  const next=structuredClone(latest),c=next.current,s=c.strikes,names=covenantNames(next),who=slot==='chase'?names[0]:names[1];
  const totalKey=slot==='chase'?'totalChase':'totalMorgan';
  const count=Math.max(0,Number(s[slot]||0)+delta);
  s[totalKey]=Math.max(0,Number(s[totalKey]??s[slot]??0)+delta);
  if(count<3){s[slot]=count;next.lastAction=delta>0?`${who} died (${count} of 3).`:`${actor} took back one of ${who}’s deaths.`;next.updatedAt=new Date().toISOString();return next;}
  // Third strike.
  s[slot]=0;
  const locked=typeof tcEncounterMutationLocked==='function'&&tcEncounterMutationLocked(next);
  if(locked){next.lastAction=`${who}’s third death. Weapons are locked after a world victory, so the strike is only recorded.`;next.updatedAt=new Date().toISOString();return next;}
  const old=c[slot]?.name||'';
  const appealed=changeWeapons(next,actor,slot,false);
  appealed.current.strikes={...s,forced:[...(s.forced||[]),{slot,weapon:old,at:new Date().toISOString()}]};
  appealed.lastAction=`${who}’s third death. The Covenant took ${old} and dealt ${appealed.current[slot]?.name||'a new weapon'}, with an Appeal penalty.`;
  return appealed;
}
async function tcCommitStrike(slot,delta){
  const c=run?.state?.current;if(!c)return;
  const encounterId=c.id,actor=playerName();
  const staged=tcBuildStrike(run.state,encounterId,slot,delta,actor);if(!staged)return;
  await commit(staged,{retryBuilder:latest=>tcBuildStrike(latest,encounterId,slot,delta,actor),quiet:true});
}
function tcConfirmThirdStrike(slot){
  const state=run.state,c=state.current,who=playerLabel(slot,state),locked=typeof tcEncounterMutationLocked==='function'&&tcEncounterMutationLocked(state);
  const body=locked?`<p class="tc-set-p">Weapons are locked after a world victory, so this third death is only recorded and the count starts again.</p>`:`<p class="tc-set-p">That’s ${h(who)}’s third death this fight. The Covenant takes ${h(c[slot]?.name||'the weapon')} and deals a new one, with an Appeal penalty. The count then starts again.</p>`;
  const s=tcSettingsSheet('Third strike',`${body}<button type="button" class="btn curse" data-strike-confirm>${locked?'Record it':'Take the strike'}</button><button type="button" class="btn ghost" data-pick-close>It was a misclick</button>`);
  s.el.querySelector('[data-strike-confirm]').addEventListener('click',async e=>{e.currentTarget.disabled=true;s.close();await tcCommitStrike(slot,1);});
}

// Encounter: the kit and the death count under each weapon card.
function tcKitMarkup(state,slot){
  const c=state.current,kit=c?.kit?.[slot],r=tcRules(state);let out='';
  if(r.kitRoll&&Array.isArray(kit)&&kit.length){
    out+=`<div class="tc-kit"><span class="tc-kit-label">Talismans</span>${kit.map((t,i)=>`<div class="tc-kit-item"><span class="tc-kit-disc">${typeof tcBuildSigil==='function'?tcBuildSigil('talisman'):''}</span><strong>${h(t)}</strong><button type="button" class="tc-kit-swap" data-kit-swap="${slot}" data-kit-index="${i}">Don’t have it</button></div>`).join('')}</div>`;
  }
  if(r.strikes&&c?.strikes){
    const n=Number(c.strikes[slot]||0),forced=(c.strikes.forced||[]).filter(f=>f.slot===slot).length;
    out+=`<div class="tc-strikes"><span class="tc-kit-label">Deaths</span><span class="tc-strike-pips" aria-label="${n} of 3">${[0,1,2].map(i=>`<i class="${i<n?'on':''}"></i>`).join('')}</span><button type="button" class="tc-strike-add" data-strike="${slot}">I died</button>${n?`<button type="button" class="tc-kit-swap" data-strike-undo="${slot}">Undo</button>`:''}${forced?`<small>${forced} ${forced===1?'strike':'strikes'} taken this fight</small>`:''}</div>`;
  }
  return out;
}
function tcDecorateEncounterRules(){
  const state=run?.state,c=state?.current;if(!c||!(c.kit||c.strikes))return;
  const weapons=app.querySelector('.tc-encounter-panel[data-panel="weapons"]');if(!weapons)return;
  const cards=weapons.querySelectorAll('.tc-loadout');if(!cards.length)return;
  // One full-width panel under both weapon cards, a section per player.
  const anchor=cards[cards.length-1].parentElement===cards[0].parentElement&&cards[0].parentElement!==weapons?cards[0].parentElement:cards[cards.length-1];
  const html=['chase','morgan'].map(slot=>{const inner=tcKitMarkup(state,slot);return inner?`<section class="tc-kit-player"><h5>${h(playerLabel(slot,state))}</h5>${inner}</section>`:'';}).join('');
  let box=weapons.querySelector('.tc-kit-box');
  if(!box){box=document.createElement('div');box.className='tc-kit-box';anchor.after(box);}
  if(box.dataset.sig!==html){box.dataset.sig=html;box.innerHTML=html;}
}
document.addEventListener('click',event=>{
  const swap=event.target.closest('[data-kit-swap]');
  if(swap){
    event.preventDefault();const c=run?.state?.current;if(!c)return;
    const slot=swap.dataset.kitSwap,index=Number(swap.dataset.kitIndex),encounterId=c.id,actor=playerName();
    swap.disabled=true;
    const staged=tcBuildKitSwap(run.state,encounterId,slot,index,actor);if(!staged)return;
    void commit(staged,{retryBuilder:latest=>tcBuildKitSwap(latest,encounterId,slot,index,actor),quiet:true});
    return;
  }
  const add=event.target.closest('[data-strike]');
  if(add){event.preventDefault();const slot=add.dataset.strike,n=Number(run?.state?.current?.strikes?.[slot]||0);if(n>=2)tcConfirmThirdStrike(slot);else void tcCommitStrike(slot,1);return;}
  const undo=event.target.closest('[data-strike-undo]');
  if(undo){event.preventDefault();void tcCommitStrike(undo.dataset.strikeUndo,-1);}
});
if(!window.__tcRulesBound){
  window.__tcRulesBound=true;let queued=false;
  const go=()=>{queued=false;try{tcDecorateEncounterRules();}catch(error){console.warn('Rules decoration skipped',error);}};
  const start=()=>new MutationObserver(()=>{if(queued||!app.querySelector('.tc-encounter-shell'))return;queued=true;requestAnimationFrame(go);}).observe(document.body,{childList:true,subtree:true});
  if(document.body)start();else document.addEventListener('DOMContentLoaded',start);
}
/* --- End Covenant rules --- */
