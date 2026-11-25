/* --- Personality: small lines that never get in the way ---
   Three voices: the Covenant clerk (paperwork), Hewg (gruff, chained, never
   drawn) and soapstone messages built from the game's message grammar.
   Rules: one line per screen at most, small italic text, never on a button or
   in a pop-up. Lines rotate once a day and are seeded by the run, so both
   phones see the same line. Everything carries .tc-quip, which the Settings
   switch "Covenant commentary" hides (html.tc-pref-quiet). Nothing here writes
   shared state; the soapstone tally lives on each phone. */
function tcQuipsOn(){return !(typeof tcPrefs!=='undefined'&&tcPrefs.quiet);}
function tcQuipHash(text){let x=2166136261;for(const ch of String(text)){x^=ch.charCodeAt(0);x=Math.imul(x,16777619);}return x>>>0;}
function tcDayKey(){const d=new Date();return `${d.getFullYear()}-${d.getMonth()+1}-${d.getDate()}`;}
function tcDaily(list,salt=''){if(!list?.length)return '';return list[tcQuipHash(`${tcDayKey()}|${run?.id||run?.joinCode||'local'}|${salt}`)%list.length];}
function tcQuip(text,extra=''){return text?`<p class="tc-quip ${extra}">${h(text)}</p>`:'';}

// Soapstone messages: the game's templates and words, plus a few about your boss.
const TC_SOAPSTONE=[
  'Try jumping','Likely hidden path','Behold, dog!','Try finger, but hole','Fort, night','Be wary of dragon',
  'Visions of treasure…','Didn’t expect trap…','Praise the Tarnished','Time for rolling','Seek grace','Ahh, horse…',
  'Could this be a mimic?','If only I had a shield…','Still no maiden…','Why is it always poison?','First off, two-handing',
  'Offer rune','Let there be light','Weak foe ahead, therefore try attacking','Strong foe ahead','No item ahead',
  'Liar ahead','Hidden path ahead, but hole','Try rolling, and then try rolling','Behold, giant!','Ahh, rot…',
  'Didn’t expect ambush…','Praise the jump','Time for crab','Visions of victory…','If only I had a torch…',
  'Be wary of left','Seek item, but hole','Fort, night, in short, fort','Praise the Erdtree, so to speak'
];
const TC_SOAPSTONE_BOSS=['{boss} ahead','Be wary of {boss}','{boss} ahead, therefore try fleeing','Didn’t expect {boss}…','Time for {boss}','Visions of {boss}…','{boss} ahead, but hole'];
const TC_SOAP_KEY='tc-soapstone-tally-v1';
function tcSoapTally(){try{return {good:0,poor:0,rated:{},...JSON.parse(localStorage.getItem(TC_SOAP_KEY)||'{}')};}catch(_){return {good:0,poor:0,rated:{}};}}
function tcSoapstoneToday(){
  const boss=run?.state?.current?.target?.name;
  const useBoss=boss&&tcQuipHash(`${tcDayKey()}|boss`)%3===0;
  return useBoss?tcDaily(TC_SOAPSTONE_BOSS,'soapboss').replace('{boss}',boss):tcDaily(TC_SOAPSTONE,'soap');
}
function tcSoapstoneMarkup(){
  const msg=tcSoapstoneToday(),t=tcSoapTally(),mine=t.rated[`${tcDayKey()}|${msg}`];
  const total=t.good+t.poor;
  return `<div class="tc-quip tc-soapstone" data-soap="${h(msg)}"><p>${h(msg)}</p><div>${mine?`<em>You rated it ${mine==='good'?'Good':'Poor'}.${total>1?` ${total} messages appraised.`:''}</em>`:'<button type="button" data-soap-rate="good">Good</button><button type="button" data-soap-rate="poor">Poor</button>'}</div></div>`;
}
document.addEventListener('click',event=>{
  const btn=event.target.closest('[data-soap-rate]');if(!btn)return;
  const box=btn.closest('.tc-soapstone'),msg=box?.dataset.soap||'',t=tcSoapTally(),key=`${tcDayKey()}|${msg}`;
  if(t.rated[key])return;
  const kind=btn.dataset.soapRate==='poor'?'poor':'good';t[kind]+=1;t.rated[key]=kind;
  // Keep the per-day record small.
  const keys=Object.keys(t.rated);if(keys.length>60)keys.slice(0,keys.length-60).forEach(k=>delete t.rated[k]);
  try{localStorage.setItem(TC_SOAP_KEY,JSON.stringify(t));}catch(_){}
  box.outerHTML=tcSoapstoneMarkup();
});

// Run milestones, shown on the Covenant memo while they're fresh.
function tcRunMilestone(state){
  const history=Array.isArray(state?.history)?state.history:[];const n=history.length;
  const counts={1:'First fight on the books. The clerk opened a fresh ledger.',10:'Ten fights filed. The clerk bought a second quill.',25:'Twenty-five fights. The Covenant has started a cabinet.',50:'Fifty fights. The clerk would like a raise.',75:'Seventy-five fights. The filing cabinet is full.',100:'One hundred fights. Someone tell Miyazaki.',150:'One hundred and fifty fights. The clerk has retired; his apprentice continues.'};
  if(counts[n])return counts[n];
  const here=history.filter(x=>x?.region===state.region).length;
  if(here<=1){
    const dlcBefore=history.some(x=>String(x?.region||'').includes('· DLC')&&x.region!==state.region);
    if(String(state.region||'').includes('· DLC')&&!dlcBefore)return 'Welcome to the Realm of Shadow. The paperwork is the same here.';
    const prev=history.find(x=>x?.region&&x.region!==state.region)?.region;
    if(prev){const fights=history.filter(x=>x?.region===prev);if(fights.length>=3&&fights.every(x=>!(x?.penances||[]).length))return `Not one Appeal in ${prev.replace(/ · DLC$/,'')}. The Covenant is suspicious.`;}
  }
  return '';
}
function tcDecorateGraceQuips(){
  const panel=app.querySelector('.tc-sanctuary-panel.tc-grace-refresh');if(!panel)return;
  if(!panel.querySelector('.tc-soapstone')){const holder=document.createElement('div');holder.innerHTML=tcSoapstoneMarkup();panel.appendChild(holder.firstElementChild);}
  const memo=panel.querySelector('.tc-grace-office-memo');
  if(memo&&!memo.querySelector('.tc-milestone')){const text=tcRunMilestone(run.state);if(text)memo.insertAdjacentHTML('beforeend',tcQuip(text,'tc-milestone'));}
}
// Grace taps.
const TC_TAP_LINES={10:'The grace is flattered.',50:'The grace has noticed you.',100:'The grace would like some space.',250:'The grace has filed a complaint.',500:'The grace is considering a restraining order.',1000:'The grace has given up.'};
if(typeof tcIncrementGraceTapCounter==='function'){
  const tcIncrementGraceTapBefore=tcIncrementGraceTapCounter;
  tcIncrementGraceTapCounter=function(btn){
    tcIncrementGraceTapBefore(btn);
    try{
      const line=TC_TAP_LINES[tcReadGraceTapCount()];if(!line||!btn)return;
      btn.querySelector('.tc-tap-quip')?.remove();
      btn.insertAdjacentHTML('beforeend',`<span class="tc-quip tc-tap-quip">${h(line)}</span>`);
      const el=btn.querySelector('.tc-tap-quip');setTimeout(()=>el?.remove(),4500);
    }catch(_){}
  };
}

// Hewg, by the state of your purse.
function tcHewgLine(state){
  const sm=smithingData(state),open=typeof tcShopOpen==='function'&&tcShopOpen(state);
  let set;
  if(!sm.favor)set=['No Favor, no fire.','Empty purse. The anvil can tell.'];
  else if(open&&sm.favor>=12)set=['You’re hoarding. I can smell it.','That much Favor and you’re just standing there?'];
  else if(open)set=['Fine. The good stock’s out back.','Everything’s for sale. Except the chain.'];
  else{
    const cost=b=>typeof tcEffectiveSmithingContractCost==='function'?tcEffectiveSmithingContractCost(state,b):smithingContractCost(b);
    const affordable=typeof availableBellBearings==='function'&&availableBellBearings(state).some(b=>sm.favor>=cost(b));
    set=affordable?['You’ve Favor enough for a contract. Stop staring at me.','Bring me a bell and I’ll do the rest.']:['Bring me more Favor. The coals don’t eat promises.','Hammer’s hot. Talk fast.','Mind the anvil. It bites.'];
  }
  return `Hewg: “${tcDaily(set,'hewg')}”`;
}
function tcDecorateForgeQuip(){
  const title=app.querySelector('.tc-forge-title');if(!title||!run?.state)return;
  const line=tcHewgLine(run.state);let el=title.parentElement.querySelector('.tc-hewg');
  if(!el){title.insertAdjacentHTML('afterend',tcQuip(line,'tc-hewg'));}
  else if(el.textContent!==line)el.textContent=line;
}

// The battle report and the Dossiers.
const TC_REPORT_LINES=['Filed in triplicate.','The lord’s estate is under review.','Victory noted. Celebration pending approval.','Another name struck from the ledger.','The Covenant acknowledges your violence.'];
function tcReportQuip(current){
  if(current?.target?.exit)return 'Capstone. The Covenant is, officially, impressed.';
  return tcDaily(TC_REPORT_LINES,`report|${current?.id||''}`);
}
function tcDossierRemark(entry){
  const pen=Array.isArray(entry?.penances)?entry.penances.length:0;
  if(entry?.exit)return 'Capstone. Framed and hung in the hall.';
  if(pen>=3)return 'The Covenant notes a pattern.';
  if(entry?.chaosTriggered&&entry?.chaosOutcome==='Honored'&&entry?.riteOutcome==='Honored')return 'Remarkably compliant.';
  if(entry?.oddRite&&entry?.riteOutcome&&entry.riteOutcome!=='Honored')return 'The Rite was… interpreted loosely.';
  if(entry?.chaosTriggered&&entry?.chaosOutcome&&entry.chaosOutcome!=='Honored')return 'Chaos won this round. The clerk has made a note.';
  if(Number(entry?.favorEarned||0)>=4)return 'A lucrative afternoon.';
  if(pen)return `${pen===1?'An Appeal was':'Appeals were'} filed. The Covenant remembers.`;
  if(!entry?.chaosTriggered)return 'Clean paperwork. Suspiciously clean.';
  return 'Nothing further to report.';
}

// Build: a dry remark, only when there is something to say.
function tcBuildRemark(screen){
  const slot=screen.querySelector('.tc-build-player-tabs .active')?.dataset.buildSlot;const b=run?.state?.builds?.[slot];if(!b)return '';
  const aff=screen.querySelector('.tc-affinity-chip.current span')?.textContent?.trim()||'';
  if(screen.querySelector('#tcWeaponResults .tc-ar-validity.bad'))return 'Requirements unmet. The Covenant admires your confidence.';
  if(aff==='Heavy'&&b.dex>b.str+5)return 'Heavy affinity on a Dexterity build. Bold.';
  if(aff==='Keen'&&b.str>b.dex+5)return 'Keen affinity on a Strength build. Interesting.';
  const info=window.tcBuildLabInfo;
  if(info){const per={};(b.talismans||[]).forEach(t=>{const s=info.STAT_TALISMANS[info.itemKey(t)];if(s)Object.entries(s).forEach(([k,v])=>{if(v)per[k]=(per[k]||0)+1;});});const hit=Object.entries(per).find(([,n])=>n>=2);if(hit)return `Two talismans for ${TC_ATTR_NAMES?.[hit[0]]||hit[0]}. Committed.`;}
  if(b.level>=80&&b.vig<30)return `Vigor ${b.vig} at level ${b.level}. Brave.`;
  if(['Occult','Blood'].includes(aff)&&b.arc>=40)return 'Arcane, all the way down.';
  const up=Number(b.weapon?.upgrade||0),max=Number((screen.querySelector('#tcUpgradeMax')?.textContent||'').replace(/\D/g,''))||0;
  if(max&&up>=max)return 'Fully upgraded. Hewg approves, quietly.';
  return '';
}
function tcDecorateBuildQuip(){
  const screen=app.querySelector('.tc-build-screen');const plate=screen?.querySelector('#tcWeaponResults .tc-ar-hero');if(!plate)return;
  const text=tcBuildRemark(screen);let el=screen.querySelector('.tc-build-quip');
  if(!text){el?.remove();return;}
  if(!el||el.previousElementSibling!==plate){el?.remove();plate.insertAdjacentHTML('afterend',tcQuip(text,'tc-build-quip'));}
  else if(el.textContent!==text)el.textContent=text;
}

// Waiting moments.
const TC_WAIT_LINES=['Consulting the Two Fingers…','Notarizing…','Filing in triplicate…','Stamping the seal…'];
function tcWaitLine(plain){return tcQuipsOn()?TC_WAIT_LINES[Math.floor(Math.random()*TC_WAIT_LINES.length)]:plain;}

function tcDecoratePersonality(){
  if(!run?.state)return;
  try{tcDecorateGraceQuips();}catch(_){}
  try{tcDecorateForgeQuip();}catch(_){}
  try{tcDecorateBuildQuip();}catch(_){}
}
if(!window.__tcPersonalityBound){
  window.__tcPersonalityBound=true;
  let queued=false;
  const go=()=>{queued=false;tcDecoratePersonality();};
  const start=()=>new MutationObserver(()=>{if(queued)return;queued=true;requestAnimationFrame(go);}).observe(document.body,{childList:true,subtree:true});
  if(document.body)start();else document.addEventListener('DOMContentLoaded',start);
}
/* --- End personality --- */
