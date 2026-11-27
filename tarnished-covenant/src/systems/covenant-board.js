/* --- Bounty board (a Covenant twist: rules.board) ---
   Instead of one assigned boss, the board posts three bounties and you pick
   your fight. Posts come from the ordinary target chooser for this region (so
   capstone timing and prerequisites still apply) plus bosses left alive in
   regions you have already passed through. A bounty pays Smithing Favor when
   the fight is filed: 1, +1 if a remembrance or capstone is on the line, +1 for
   every fight it has waited. Unpicked bounties expire after three fights.
   state.board = {posts:[{id,name,exit,required,prerequisiteFor,region,postedAt}]}
   current.bountyPending = true until a pick; current.bounty = the taken post.
   Weapons are dealt again for the picked target so acquisition gates hold. */
const TC_BOUNTY_LIFE=3;
TC_RULE_INFO.board=['Bounty board','Pick each fight from three posted bounties, including bosses left behind in earlier regions. Bounties pay Favor, grow while they wait, and expire.'];
function tcBoardOn(state){return Boolean(state?.rules?.board);}
function tcBountyAge(state,post){return Math.max(0,(state?.history?.length||0)-Number(post?.postedAt||0));}
function tcBountyValue(state,post){
  const big=Boolean(post?.exit||(typeof REMEMBRANCE_REGION!=='undefined'&&REMEMBRANCE_REGION[post?.name]));
  return 1+(big?1:0)+Math.min(TC_BOUNTY_LIFE-1,tcBountyAge(state,post));
}
function tcKilledAnywhere(state){
  const names=new Set((state?.history||[]).map(x=>x?.name).filter(Boolean));
  for(const k of (state?.sanctionedBossKills||[]))if(k?.name)names.add(k.name);
  return names;
}
function tcBacktrackBosses(state){
  const visited=[...new Set((state?.history||[]).map(x=>x?.region).filter(r=>r&&r!==state.region&&regions?.[r]))];
  const killed=tcKilledAnywhere(state),out=[];
  for(const region of visited)for(const name of (regions[region].bosses||[]))if(!killed.has(name))out.push({name,exit:false,region});
  return out;
}
function tcRefreshBoard(state){
  const killed=tcKilledAnywhere(state);
  const board=state.board&&Array.isArray(state.board.posts)?state.board:{posts:[]};
  // Drop the felled, the expired, and anything no longer reachable from here.
  board.posts=board.posts.filter(p=>p?.name&&!killed.has(p.name)&&tcBountyAge(state,p)<TC_BOUNTY_LIFE&&(p.region===state.region?true:Boolean(regions?.[p.region])));
  const taken=new Set(board.posts.map(p=>p.name));
  const candidates=[];
  for(let i=0;i<40&&candidates.length<6;i++){
    let t=null;try{t=chooseTarget(state);}catch(_){t=null;}
    if(t?.name&&!taken.has(t.name)&&!killed.has(t.name)&&!candidates.some(c=>c.name===t.name))candidates.push({...t,region:state.region});
    // A forced fight (a prerequisite or the last capstone) is always posted.
    if(t&&(t.required||t.prerequisiteFor))break;
  }
  const forced=candidates.find(c=>c.required||c.prerequisiteFor||(c.exit&&!availableRegionalBosses(state).length));
  const back=tcBacktrackBosses(state).filter(b=>!taken.has(b.name)&&!candidates.some(c=>c.name===b.name));
  const mix=[...(forced?[forced]:[]),...candidates.filter(c=>c!==forced),...back.sort(()=>Math.random()-.5).slice(0,2)];
  // Mostly this region: at most one old bounty at a time, unless this region is bare.
  for(const c of mix){
    if(board.posts.length>=3)break;
    const oldPosted=board.posts.filter(p=>p.region!==state.region).length;
    if(c.region!==state.region&&oldPosted>=1&&candidates.length)continue;
    if(board.posts.some(p=>p.name===c.name))continue;
    board.posts.push({id:crypto.randomUUID(),name:c.name,exit:Boolean(c.exit),required:Boolean(c.required),prerequisiteFor:c.prerequisiteFor||'',region:c.region,postedAt:state.history?.length||0});
  }
  state.board=board;return board;
}
const tcNewEncounterBeforeBoard=newEncounter;
newEncounter=function(state){
  const encounter=tcNewEncounterBeforeBoard(state);
  if(encounter&&tcBoardOn(state)){
    try{tcRefreshBoard(state);encounter.bountyPending=true;}catch(error){console.warn('Bounty board skipped',error);}
  }
  return encounter;
};
// The initial state rolls its first encounter before rules exist; post the board then.
const tcInitialRunStateBeforeBoard=initialRunState;
initialRunState=function(options={}){
  const state=tcInitialRunStateBeforeBoard(options);
  if(state&&options?.rules?.board){state.rules={...(state.rules||{}),board:true};tcRefreshBoard(state);if(state.current)state.current.bountyPending=true;}
  return state;
};
function tcBuildBountyPick(latest,encounterId,postId,actor){
  const c=latest?.current;if(!c||c.id!==encounterId||!c.bountyPending)return null;
  const post=(latest.board?.posts||[]).find(p=>p.id===postId);if(!post)return null;
  const next=structuredClone(latest),cur=next.current;
  const target={name:post.name,exit:Boolean(post.exit)};
  if(post.required)target.required=true;if(post.prerequisiteFor)target.prerequisiteFor=post.prerequisiteFor;
  cur.target=target;
  const pair=chooseWeaponPair(next,target);cur.chase=pair.chase;cur.morgan=pair.morgan;
  cur.bounty={id:post.id,name:post.name,region:post.region,value:tcBountyValue(next,post)};
  cur.bountyPending=false;
  next.board.posts=next.board.posts.filter(p=>p.id!==post.id);
  next.lastAction=`${actor} took the bounty on ${post.name} (+${cur.bounty.value} Favor).`;
  next.updatedAt=new Date().toISOString();
  return next;
}
// Paying out, and recording an old region's boss under its own region.
const tcCompleteEncounterBeforeBoard=completeEncounter;
completeEncounter=function(state,actor){
  const next=tcCompleteEncounterBeforeBoard(state,actor),bounty=state?.current?.bounty,entry=next?.history?.[0];
  if(bounty&&entry&&entry.name===bounty.name){
    const value=Math.max(0,Number(bounty.value||0));
    if(value){next.smithing=smithingData(next);next.smithing.favor+=value;entry.bountyFavor=value;}
    if(bounty.region&&bounty.region!==entry.region){entry.region=bounty.region;entry.backtrack=true;}
  }
  return next;
};
// While a pick is pending the old pool correction must not touch the target,
// and a bounty from another region is never "outside the pool".
if(typeof tcTargetOutsidePool==='function'){
  const tcTargetOutsidePoolBeforeBoard=tcTargetOutsidePool;
  tcTargetOutsidePool=function(state){if(state?.current?.bounty||state?.current?.bountyPending)return false;return tcTargetOutsidePoolBeforeBoard(state);};
}

// The board itself: a screen over the Encounter until a bounty is taken.
function tcBoardMarkup(state){
  const posts=state.board?.posts||[];
  const card=p=>{
    const age=tcBountyAge(state,p),value=tcBountyValue(state,p),left=TC_BOUNTY_LIFE-age;
    const art=typeof actualBossImage==='function'?actualBossImage(p.name,p.region):'';
    const tags=[p.exit?'Capstone':'',(typeof REMEMBRANCE_REGION!=='undefined'&&REMEMBRANCE_REGION[p.name])?'Remembrance':'',p.region!==state.region?`Back in ${String(p.region).replace(/ · DLC$/,'')}`:'',p.required||p.prerequisiteFor?'Required':''].filter(Boolean);
    return `<button type="button" class="tc-bounty ${p.exit?'capstone':''}" data-bounty="${h(p.id)}" style="${art?`--tc-bounty-art:url('${art}')`:''}">
      <span class="tc-bounty-pay">+${value}<small>Favor</small></span>
      <strong>${h(p.name)}</strong>
      ${tags.length?`<span class="tc-bounty-tags">${tags.map(t=>`<i>${h(t)}</i>`).join('')}</span>`:''}
      <small class="tc-bounty-age">${age?`Posted ${age} ${age===1?'fight':'fights'} ago. `:'New. '}${left<=1?'Expires after this fight.':`Expires in ${left} fights.`}</small>
    </button>`;
  };
  return `<section class="tc-board"><p class="tc-board-kicker">Bounty board</p><h2>Choose your fight</h2><p class="tc-board-help">Bounties pay Favor when the fight is filed. They grow while they wait, then come down.</p><div class="tc-board-posts">${posts.map(card).join('')||'<p class="tc-set-p">No bounties posted. Check back after a sync.</p>'}</div>${typeof tcQuip==='function'&&typeof tcDaily==='function'?tcQuip(tcDaily(['The clerk accepts no responsibility for the bounties.','Payment on proof of felling. The clerk will want details.','Unclaimed bounties are returned to the hunters’ guild. There is no hunters’ guild.'],'board')):''}</section>`;
}
function tcDecorateBoard(){
  const state=run?.state,c=state?.current,shell=app.querySelector('.tc-encounter-shell');if(!shell)return;
  const pending=Boolean(c?.bountyPending&&tcBoardOn(state));
  shell.classList.toggle('tc-board-open',pending||Boolean(c?.draftPending&&c?.draft&&state?.rules?.draft));
  let board=shell.querySelector('.tc-board:not(.tc-draft)');
  if(!pending){board?.remove();return;}
  const html=tcBoardMarkup(state);
  if(!board){const wrap=document.createElement('div');wrap.innerHTML=html;board=wrap.firstElementChild;board.dataset.sig=html;shell.prepend(board);}
  else if(board.dataset.sig!==html){board.outerHTML=html;shell.querySelector('.tc-board:not(.tc-draft)').dataset.sig=html;}
}
function tcConfirmBounty(postId){
  const state=run.state,post=(state.board?.posts||[]).find(p=>p.id===postId);if(!post)return;
  const value=tcBountyValue(state,post);
  const s=tcSettingsSheet(`Take the bounty on ${post.name}?`,`<p class="tc-set-p">It pays +${value} Smithing Favor when the fight is filed. Your weapons are dealt for this fight once you take it.${post.region!==state.region?` This one is back in ${h(String(post.region).replace(/ · DLC$/,''))}.`:''}</p><button type="button" class="btn gold" data-take-bounty>Take the bounty</button>`);
  s.el.querySelector('[data-take-bounty]').addEventListener('click',async e=>{
    e.currentTarget.disabled=true;s.close();
    const encounterId=state.current.id,actor=playerName();
    const staged=tcBuildBountyPick(run.state,encounterId,postId,actor);if(!staged)return setToast('That bounty is gone. The board changed.');
    await commit(staged,{retryBuilder:latest=>tcBuildBountyPick(latest,encounterId,postId,actor),successToast:`Bounty taken: ${post.name}.`});
  });
}
document.addEventListener('click',event=>{
  const b=event.target.closest('[data-bounty]');if(!b)return;
  event.preventDefault();tcConfirmBounty(b.dataset.bounty);
});
// Grace's next-fight card points at the board while a pick is pending.
if(typeof tcGraceNextCard==='function'){
  const tcGraceNextCardBeforeBoard=tcGraceNextCard;
  tcGraceNextCard=function(state){
    if(!(state?.current?.bountyPending&&tcBoardOn(state)))return tcGraceNextCardBeforeBoard(state);
    const posts=state.board?.posts||[];
    return `<div class="tc-grace-next tc-grace-board" role="button" tabindex="0" aria-label="Open the bounty board"><div class="tc-next-head"><span>Bounty board</span><h3>${posts.length} ${posts.length===1?'bounty':'bounties'} posted</h3></div><div class="tc-board-names">${posts.map(p=>`<p><b>+${tcBountyValue(state,p)}</b> ${h(p.name)}</p>`).join('')}</div><div class="tc-next-links"><b>Choose your fight</b></div></div>`;
  };
}
if(!window.__tcBoardBound){
  window.__tcBoardBound=true;let queued=false;
  const go=()=>{queued=false;try{tcDecorateBoard();}catch(error){console.warn('Bounty board skipped',error);}};
  const start=()=>new MutationObserver(()=>{if(queued||!app.querySelector('.tc-encounter-shell'))return;queued=true;requestAnimationFrame(go);}).observe(document.body,{childList:true,subtree:true});
  if(document.body)start();else document.addEventListener('DOMContentLoaded',start);
}
/* --- End bounty board --- */
