/* --- Region bingo (a Covenant twist: rules.bingo) ---
   Every region deals a 5×5 card of side challenges (centre is free). Marks are
   on the honor system, from Site of Grace → Progress. Each completed line
   (row, column or diagonal) pays 2 Smithing Favor once. A mark that is part of
   a paid line can't be taken back. A new card is dealt on entering a region.
   state.bingo = {region, cells:[{t,d,done,by,at}], paid:[lineIndex]} */
TC_RULE_INFO.bingo=['Region bingo','Each region deals a 5×5 card of side challenges. Every line you complete pays 2 Favor.'];
const TC_BINGO_PAY=2;
const TC_BINGO_POOL=[
  ['No flasks','Beat a boss without either of you drinking a flask.'],['Riposte','Land a critical hit, riposte or backstab, on a boss.'],['Parry','Parry a boss attack.'],
  ['Spirit-free','Beat a boss without summoning Spirit Ashes.'],['First try','Beat a boss on your first attempt.'],['Last one standing','Beat a boss after one of you has died in the fight.'],
  ['Jump kill','Land the killing blow with a jump attack.'],['Skill finish','Land the killing blow with a weapon skill.'],['Ranged chip','Hit a boss with a bow, crossbow or throwing item.'],
  ['Status','Inflict a status effect on a boss: bleed, frost, poison, rot, sleep or madness.'],['Stance break','Break a boss’s stance.'],['Buffed','Use a buff before the fight: a grease, a spell or an item.'],
  ['Pot shot','Hit a boss with a thrown pot.'],['Quick work','Beat a boss in under three minutes.'],['Untouched','One of you ends a boss fight at full health.'],
  ['Mounted','Deal damage to a boss from Torrent.'],['Pleasantries','Both of you gesture at the boss before the fight.'],['Chaos endured','Endure a Chaos decree in this region.'],
  ['Rite honored','Honor an Odd Rite in this region.'],['Clean record','Beat a boss with no Appeal penalties in force.'],['Fisticuffs','Land a punch on a boss.'],
  ['Night shift','Beat a boss at night.'],['Sliver','Win with one of you under a tenth of their health.'],['Shield wall','Block a boss attack with a shield.'],
  ['Dressed alike','Both of you fight in matching armor sets.'],['Two hands','Two-hand your weapon for a whole fight.'],['Consumable','Use a consumable other than a flask on a boss.'],
  ['Skill spam','Land three weapon skills on one boss.'],['Spellwork','Hit a boss with a sorcery or incantation.'],['Explorer','Find a Site of Grace you haven’t rested at yet.']
];
const TC_BINGO_LINES=(()=>{const L=[];for(let r=0;r<5;r++)L.push([0,1,2,3,4].map(c=>r*5+c));for(let c=0;c<5;c++)L.push([0,1,2,3,4].map(r=>r*5+c));L.push([0,6,12,18,24],[4,8,12,16,20]);return L;})();
function tcBingoOn(state){return Boolean(state?.rules?.bingo);}
function tcDealBingo(region){
  const pool=[...TC_BINGO_POOL].sort(()=>Math.random()-.5).slice(0,24);
  const cells=pool.map(([t,d])=>({t,d,done:false}));
  cells.splice(12,0,{t:'Free',d:'The Covenant itself. Already sealed.',done:true,free:true});
  return {region,cells,paid:[]};
}
function tcEnsureBingo(state){
  if(!tcBingoOn(state))return;
  if(!state.bingo||state.bingo.region!==state.region)state.bingo=tcDealBingo(state.region);
}
const tcNewEncounterBeforeBingo=newEncounter;
newEncounter=function(state){const e=tcNewEncounterBeforeBingo(state);try{tcEnsureBingo(state);}catch(_){}return e;};
const tcInitialRunStateBeforeBingo=initialRunState;
initialRunState=function(options={}){
  const state=tcInitialRunStateBeforeBingo(options);
  if(state&&options?.rules?.bingo){state.rules={...(state.rules||{}),bingo:true};tcEnsureBingo(state);}
  return state;
};
function tcBingoLinesDone(cells){return TC_BINGO_LINES.map((line,i)=>line.every(k=>cells[k]?.done)?i:-1).filter(i=>i>=0);}
function tcBuildBingoMark(latest,region,index,done,actor){
  const b=latest?.bingo;if(!b||b.region!==region||!b.cells[index]||b.cells[index].free)return null;
  if(Boolean(b.cells[index].done)===Boolean(done))return null;
  if(!done&&(b.paid||[]).some(li=>TC_BINGO_LINES[li].includes(index)))return null;
  const next=structuredClone(latest),nb=next.bingo,cell=nb.cells[index];
  cell.done=Boolean(done);if(done){cell.by=actor;cell.at=new Date().toISOString();}else{delete cell.by;delete cell.at;}
  const fresh=tcBingoLinesDone(nb.cells).filter(i=>!(nb.paid||[]).includes(i));
  nb.paid=[...(nb.paid||[]),...fresh];
  if(fresh.length){next.smithing=smithingData(next);next.smithing.favor+=TC_BINGO_PAY*fresh.length;}
  next.lastAction=done?`${actor} sealed “${cell.t}” on the bingo card${fresh.length?`. Bingo! +${TC_BINGO_PAY*fresh.length} Favor.`:'.'}`:`${actor} took back “${cell.t}”.`;
  next.updatedAt=new Date().toISOString();
  return next;
}
function tcBingoMarkup(state){
  const b=state.bingo;if(!b)return '';
  const paid=new Set((b.paid||[]).flatMap(li=>TC_BINGO_LINES[li]));
  return `<h4 class="tc-forge-h">Region bingo</h4><p class="tc-bingo-help">${b.paid?.length?`${b.paid.length} ${b.paid.length===1?'line':'lines'} paid this region (+${TC_BINGO_PAY*b.paid.length} Favor).`:`Every line pays ${TC_BINGO_PAY} Favor. Tap a square to seal it.`}</p>
    <div class="tc-bingo" role="grid">${b.cells.map((c,i)=>`<button type="button" class="tc-bingo-cell ${c.done?'done':''} ${paid.has(i)?'line':''} ${c.free?'free':''}" data-bingo="${i}" aria-pressed="${Boolean(c.done)}">${h(c.t)}</button>`).join('')}</div>`;
}
function tcDecorateBingo(){
  const state=run?.state;if(!tcBingoOn(state)||!state.bingo)return;
  const box=app.querySelector('.tc-progress-new');if(!box)return;
  const html=tcBingoMarkup(state);let el=box.querySelector('.tc-bingo-box');
  if(!el){el=document.createElement('div');el.className='tc-bingo-box';const runHead=[...box.querySelectorAll('.tc-forge-h')].find(x=>x.textContent.trim()==='The run');if(runHead)runHead.before(el);else box.appendChild(el);}
  if(el.dataset.sig!==html){el.dataset.sig=html;el.innerHTML=html;}
}
document.addEventListener('click',event=>{
  const cell=event.target.closest('[data-bingo]');if(!cell)return;
  event.preventDefault();
  const state=run.state,b=state.bingo,index=Number(cell.dataset.bingo),c=b?.cells?.[index];if(!c)return;
  if(c.free)return setToast('The free square. The Covenant sealed it for you.');
  const locked=c.done&&(b.paid||[]).some(li=>TC_BINGO_LINES[li].includes(index));
  const when=c.at?new Date(c.at).toLocaleDateString(undefined,{month:'short',day:'numeric'}):'';
  const body=`<p class="tc-set-p">${h(c.d)}</p>${c.done?`<p class="tc-set-p muted">Sealed${c.by?` by ${h(personalizePlayers(c.by,state))}`:''}${when?` on ${h(when)}`:''}.${locked?' It’s part of a paid line, so it stays.':''}</p>`:''}${!c.done?'<button type="button" class="btn gold" data-bingo-set="1">We did it</button>':locked?'':'<button type="button" class="btn ghost" data-bingo-set="0">Take it back</button>'}`;
  const s=tcSettingsSheet(c.t,body);
  s.el.querySelector('[data-bingo-set]')?.addEventListener('click',async e=>{
    const done=e.currentTarget.dataset.bingoSet==='1',region=b.region,actor=playerName();
    e.currentTarget.disabled=true;s.close();
    const staged=tcBuildBingoMark(run.state,region,index,done,actor);if(!staged)return;
    await commit(staged,{retryBuilder:latest=>tcBuildBingoMark(latest,region,index,done,actor),quiet:true});
    const lines=(run.state.bingo?.paid||[]).length,before=(b.paid||[]).length;
    if(done&&lines>before)setToast(`Bingo! +${TC_BINGO_PAY*(lines-before)} Favor.`);
  });
});
if(!window.__tcBingoBound){
  window.__tcBingoBound=true;let queued=false;
  const go=()=>{queued=false;try{tcDecorateBingo();}catch(error){console.warn('Bingo skipped',error);}};
  const start=()=>new MutationObserver(()=>{if(queued||!app.querySelector('.tc-progress-new'))return;queued=true;requestAnimationFrame(go);}).observe(document.body,{childList:true,subtree:true});
  if(document.body)start();else document.addEventListener('DOMContentLoaded',start);
}
/* --- End Region bingo --- */
