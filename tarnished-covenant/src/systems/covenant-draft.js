/* --- Hostile draft (a Covenant twist: rules.draft) ---
   Each fight, each of you chooses your partner's weapon from three. Options are
   ordinary legal draws (makeBuild, so gates, decks and a dealt character's
   classes still apply). The weapons dealt with the encounter stay underneath
   until both picks are in; then both are revealed together.
   current.draft = {for:{chase:[builds],morgan:[builds]}, picks:{chase:i|null, morgan:i|null}}
   current.draftPending = true until both picks are in. With the bounty board
   the draft is drawn after the bounty is taken. */
TC_RULE_INFO.draft=['Hostile draft','Each fight, you choose your partner’s weapon from three. Both are revealed together.'];
function tcDraftOn(state){return Boolean(state?.rules?.draft);}
function tcOtherSlot(slot){return slot==='chase'?'morgan':'chase';}
function tcDraftOptions(state,target,slot,avoid){
  const out=[],names=new Set(avoid.filter(Boolean));
  const fits=b=>typeof tcBuildFits==='function'?tcBuildFits(state,slot,b):true;
  for(let pass=0;pass<2&&out.length<3;pass++){
    for(let i=0;i<24&&out.length<3;i++){
      let b=null;try{b=makeBuild(state.region,target,[...names],state);}catch(_){b=null;}
      if(!b?.name||names.has(b.name))continue;
      if(pass===0&&!fits(b))continue;
      names.add(b.name);out.push(b);
    }
  }
  return out;
}
function tcMakeDraft(state,encounter){
  if(!encounter?.target)return null;
  const forChase=tcDraftOptions(state,encounter.target,'chase',[]);
  const forMorgan=tcDraftOptions(state,encounter.target,'morgan',forChase.map(b=>b.name));
  if(forChase.length<2||forMorgan.length<2)return null;
  return {for:{chase:forChase,morgan:forMorgan},picks:{chase:null,morgan:null}};
}
function tcAttachDraft(state,encounter){
  if(!tcDraftOn(state)||!encounter||encounter.bountyPending)return encounter;
  const draft=tcMakeDraft(state,encounter);
  if(draft){encounter.draft=draft;encounter.draftPending=true;}
  return encounter;
}
const tcNewEncounterBeforeDraft=newEncounter;
newEncounter=function(state){return tcAttachDraft(state,tcNewEncounterBeforeDraft(state));};
const tcInitialRunStateBeforeDraft=initialRunState;
initialRunState=function(options={}){
  const state=tcInitialRunStateBeforeDraft(options);
  if(state&&options?.rules?.draft){state.rules={...(state.rules||{}),draft:true};tcAttachDraft(state,state.current);}
  return state;
};
if(typeof tcBuildBountyPick==='function'){
  const tcBuildBountyPickBeforeDraft=tcBuildBountyPick;
  tcBuildBountyPick=function(latest,encounterId,postId,actor){
    const next=tcBuildBountyPickBeforeDraft(latest,encounterId,postId,actor);
    if(next?.current&&tcDraftOn(next))tcAttachDraft(next,next.current);
    return next;
  };
}
function tcBuildDraftPick(latest,encounterId,forSlot,index,actor){
  const c=latest?.current;if(!c||c.id!==encounterId||!c.draftPending||!c.draft)return null;
  if(c.draft.picks[forSlot]!==null&&c.draft.picks[forSlot]!==undefined)return null;
  const option=c.draft.for[forSlot]?.[index];if(!option)return null;
  const next=structuredClone(latest),d=next.current.draft;
  d.picks[forSlot]=index;
  const names=covenantNames(next),chooser=forSlot==='chase'?names[1]:names[0];
  if(d.picks.chase!==null&&d.picks.morgan!==null){
    next.current.chase=structuredClone(d.for.chase[d.picks.chase]);
    next.current.morgan=structuredClone(d.for.morgan[d.picks.morgan]);
    next.current.draftPending=false;
    next.lastAction=`The draft is in: ${names[0]} wields ${next.current.chase.name}, ${names[1]} wields ${next.current.morgan.name}.`;
  }else next.lastAction=`${chooser} has chosen. Waiting on the other pick.`;
  next.updatedAt=new Date().toISOString();
  return next;
}
// Screen: shown over the Encounter (after any bounty) until both picks are in.
function tcDraftTasks(state){
  const me=backend?.mode==='shared'&&typeof tcMasterworkSlotForIdentity==='function'?tcMasterworkSlotForIdentity():null;
  // Each phone picks for its partner; one phone playing alone (local mode) does both.
  return me?[tcOtherSlot(me)]:['chase','morgan'];
}
function tcDraftMarkup(state){
  const c=state.current,d=c.draft,tasks=tcDraftTasks(state);
  const section=forSlot=>{
    const chosen=d.picks[forSlot];
    const who=playerLabel(forSlot,state);
    if(chosen!==null&&chosen!==undefined)return `<div class="tc-draft-done"><strong>You chose for ${h(who)}.</strong><p>Revealed when both picks are in.</p></div>`;
    return `<h4 class="tc-forge-h">Choose ${h(who)}’s weapon</h4><div class="tc-draft-options">${d.for[forSlot].map((b,i)=>`<button type="button" class="tc-draft-option" data-draft-for="${forSlot}" data-draft-index="${i}"><strong>${h(b.name)}</strong><small>${h(typeof tcWeaponClass==='function'?tcWeaponClass(b.name):'')}${b.affinity&&b.affinity!=='Fixed / unique'?` · ${h(b.affinity)}`:''}</small></button>`).join('')}</div>`;
  };
  const waiting=['chase','morgan'].filter(s=>!tasks.includes(s)).map(s=>{const done=d.picks[s]!==null&&d.picks[s]!==undefined;return `<p class="tc-draft-wait">${done?`${h(playerLabel(tcOtherSlot(s),state))} has chosen your weapon.`:`${h(playerLabel(tcOtherSlot(s),state))} is choosing your weapon…`}</p>`;}).join('');
  return `<section class="tc-board tc-draft"><p class="tc-board-kicker">Hostile draft</p><h2>${h(c.target?.name||'The next fight')}</h2><p class="tc-board-help">Pick the weapon your partner will carry into this fight. Choose wisely, or don’t.</p>${tasks.map(section).join('')}${waiting}${typeof tcQuip==='function'?tcQuip('The clerk reminds you that friendship is not covered by the Covenant.'):''}</section>`;
}
function tcDecorateDraft(){
  const state=run?.state,c=state?.current,shell=app.querySelector('.tc-encounter-shell');if(!shell)return;
  const pending=Boolean(c?.draftPending&&c?.draft&&!c?.bountyPending&&tcDraftOn(state));
  let box=shell.querySelector('.tc-draft');
  if(!pending){box?.remove();if(!c?.bountyPending)shell.classList.remove('tc-board-open');return;}
  shell.classList.add('tc-board-open');
  const html=tcDraftMarkup(state);
  if(!box){const w=document.createElement('div');w.innerHTML=html;box=w.firstElementChild;box.dataset.sig=html;shell.prepend(box);}
  else if(box.dataset.sig!==html){box.outerHTML=html;shell.querySelector('.tc-draft').dataset.sig=html;}
}
document.addEventListener('click',event=>{
  const opt=event.target.closest('[data-draft-for]');if(!opt)return;
  event.preventDefault();
  const state=run.state,forSlot=opt.dataset.draftFor,index=Number(opt.dataset.draftIndex),b=state.current?.draft?.for?.[forSlot]?.[index];if(!b)return;
  const s=tcSettingsSheet(`Give ${playerLabel(forSlot,state)} the ${b.name}?`,`<p class="tc-set-p">Once chosen it can’t be changed. ${h(playerLabel(forSlot,state))} sees it when both picks are in.</p><button type="button" class="btn gold" data-draft-confirm>Hand it over</button>`);
  s.el.querySelector('[data-draft-confirm]').addEventListener('click',async e=>{
    e.currentTarget.disabled=true;s.close();
    const encounterId=state.current.id,actor=playerName();
    const staged=tcBuildDraftPick(run.state,encounterId,forSlot,index,actor);if(!staged)return setToast('That pick was already made.');
    await commit(staged,{retryBuilder:latest=>tcBuildDraftPick(latest,encounterId,forSlot,index,actor),quiet:true});
  });
});
if(typeof tcGraceNextCard==='function'){
  const tcGraceNextCardBeforeDraft=tcGraceNextCard;
  tcGraceNextCard=function(state){
    const c=state?.current;
    if(!(c?.draftPending&&c?.draft&&!c?.bountyPending&&tcDraftOn(state)))return tcGraceNextCardBeforeDraft(state);
    return `<div class="tc-grace-next tc-grace-board" role="button" tabindex="0" aria-label="Open the draft"><div class="tc-next-head"><span>Hostile draft</span><h3>${h(c.target?.name||'Next fight')}</h3></div><div class="tc-board-names"><p>Each of you chooses the other’s weapon.</p></div><div class="tc-next-links"><b>Open the draft</b></div></div>`;
  };
}
if(!window.__tcDraftBound){
  window.__tcDraftBound=true;let queued=false;
  const go=()=>{queued=false;try{tcDecorateDraft();}catch(error){console.warn('Draft skipped',error);}};
  const start=()=>new MutationObserver(()=>{if(queued||!app.querySelector('.tc-encounter-shell'))return;queued=true;requestAnimationFrame(go);}).observe(document.body,{childList:true,subtree:true});
  if(document.body)start();else document.addEventListener('DOMContentLoaded',start);
}
/* --- End Hostile draft --- */
