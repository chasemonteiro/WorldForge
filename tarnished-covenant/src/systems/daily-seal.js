/* --- Daily seal ---
   One small challenge a day, the same on both phones (seeded by the date and
   the run), shown on Site of Grace for every run. Sealing it is a shared write
   that records the day; a streak counts consecutive sealed days. No Favor: it
   leaves the run's economy alone. Each phone can hide it (Settings → This
   phone → Daily seal, tcPrefs.hideDaily).
   state.dailySeal = {days:{'YYYY-MM-DD':{t,by,at}}} */
const TC_DAILY_SEALS=[
  'Beat any boss without either of you drinking a flask.','Land a riposte or backstab on a boss.','Parry something. Anything.',
  'Beat a boss without Spirit Ashes.','Beat a boss on your first attempt.','Finish a boss with a weapon skill.',
  'Hit a boss with a thrown pot.','Break a boss’s stance.','Both of you gesture at the boss before the fight.',
  'Win a fight with one of you under a tenth of their health.','Fight in matching armor sets.','Two-hand your weapon for a whole fight.',
  'Find a Site of Grace you haven’t rested at.','Inflict a status effect on a boss.','Land the killing blow with a jump attack.',
  'Beat a boss in under three minutes.','Deal damage from Torrent.','Honor today’s Odd Rite, whatever it is.',
  'Use a buff before the fight starts.','Hit a boss with a sorcery or incantation.','Pick up an item you’ve never held before.'
];
function tcDayStamp(d=new Date()){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
function tcDailySealText(state,day=tcDayStamp()){
  let x=2166136261;for(const ch of `${day}|${run?.id||run?.joinCode||state?.createdBy||'local'}`){x^=ch.charCodeAt(0);x=Math.imul(x,16777619);}
  return TC_DAILY_SEALS[(x>>>0)%TC_DAILY_SEALS.length];
}
function tcDailyStreak(state,today=new Date()){
  const days=state?.dailySeal?.days||{};let n=0;const d=new Date(today);
  if(!days[tcDayStamp(d)])d.setDate(d.getDate()-1);// an unsealed today doesn't break yesterday's streak
  while(days[tcDayStamp(d)]){n++;d.setDate(d.getDate()-1);}
  return n;
}
function tcBuildDailySeal(latest,day,sealed,actor){
  if(!latest)return null;
  const next=structuredClone(latest),days={...(next.dailySeal?.days||{})};
  if(Boolean(days[day])===Boolean(sealed))return null;
  if(sealed)days[day]={t:tcDailySealText(next,day),by:actor,at:new Date().toISOString()};else delete days[day];
  // Keep a year of days.
  const keys=Object.keys(days).sort();keys.slice(0,Math.max(0,keys.length-366)).forEach(k=>delete days[k]);
  next.dailySeal={days};
  next.lastAction=sealed?`${actor} broke today’s seal.`:`${actor} unsealed today.`;
  next.updatedAt=new Date().toISOString();
  return next;
}
// A wax seal in the corner of the region painting; tapping it opens today's challenge.
function tcDailySealMarkup(state){
  const day=tcDayStamp(),done=state?.dailySeal?.days?.[day],streak=tcDailyStreak(state);
  return `<button type="button" class="tc-daily-badge ${done?'done':''}" data-daily-open aria-label="Daily seal${done?', sealed today':', not sealed yet'}${streak?`, ${streak}-day streak`:''}"><span class="tc-daily-wax">${done?'✓':'✦'}</span><span class="tc-daily-label">${done?'Sealed':'Daily seal'}</span>${streak?`<i>${streak}</i>`:''}</button>`;
}
function tcOpenDailySeal(){
  const state=run.state,day=tcDayStamp(),done=state?.dailySeal?.days?.[day],streak=tcDailyStreak(state);
  const s=tcSettingsSheet('Daily seal',`<p class="tc-set-p">${h(tcDailySealText(state,day))}</p><p class="tc-set-p muted">${done?`Sealed by ${h(personalizePlayers(done.by||'',state))}. A new one tomorrow.`:'The same challenge on both phones today. Either of you can seal it.'}${streak?` ${streak}-day streak.`:''}</p><button type="button" class="btn ${done?'ghost':'gold'}" data-daily="${done?'0':'1'}">${done?'Undo today’s seal':'We did it'}</button>`);
  s.el.querySelector('[data-daily]')?.addEventListener('click',()=>setTimeout(()=>s.close(),0));
}
document.addEventListener('click',event=>{if(event.target.closest('[data-daily-open]')){event.preventDefault();tcOpenDailySeal();}});
function tcDecorateDailySeal(){
  const panel=app.querySelector('.tc-sanctuary-panel.tc-grace-refresh');if(!panel||!run?.state)return;
  let el=panel.querySelector('.tc-daily-box');
  if(typeof tcPrefs!=='undefined'&&tcPrefs.hideDaily){el?.remove();return;}
  const html=tcDailySealMarkup(run.state);
  if(!el){el=document.createElement('div');el.className='tc-daily-box';panel.appendChild(el);}
  if(el.dataset.sig!==html){el.dataset.sig=html;el.innerHTML=html;}
}
document.addEventListener('click',async event=>{
  const btn=event.target.closest('[data-daily]');if(!btn)return;
  event.preventDefault();btn.disabled=true;
  const day=tcDayStamp(),sealed=btn.dataset.daily==='1',actor=playerName();
  const staged=tcBuildDailySeal(run.state,day,sealed,actor);if(!staged){btn.disabled=false;return;}
  await commit(staged,{retryBuilder:latest=>tcBuildDailySeal(latest,day,sealed,actor),quiet:true});
  if(sealed){const n=tcDailyStreak(run.state);setToast(n>1?`Sealed. ${n} days running.`:'Sealed for today.');}
});
if(!window.__tcDailyBound){
  window.__tcDailyBound=true;let queued=false;
  const go=()=>{queued=false;try{tcDecorateDailySeal();}catch(error){console.warn('Daily seal skipped',error);}};
  const start=()=>new MutationObserver(()=>{if(queued||!app.querySelector('.tc-grace-refresh'))return;queued=true;requestAnimationFrame(go);}).observe(document.body,{childList:true,subtree:true});
  if(document.body)start();else document.addEventListener('DOMContentLoaded',start);
}
/* --- End Daily seal --- */
