/* --- Site of Grace refresh: Grace and Progress panels ---
   Grace: the region painting and the grace flame share one hero, a single
   "next fight" card follows, and the Covenant memo is a pinned slip. The older
   pieces (boss overlay, buildcraft row) stay in the DOM for the code that
   decorates them, but are hidden; layout is done with grid areas so the order
   those observers insert things in no longer matters.
   Progress: a road through every region of the run, a ring of remembrance
   runes, and a few lines about the run so far. Read-only; nothing is saved. */
function tcGraceNextCard(state){
  const c=state.current;if(!c?.target)return '';
  const weapons=['chase','morgan'].map(slot=>c[slot]?.name?`<div class="tc-next-weapon"><span>${h(playerLabel(slot,state))}</span><strong>${h(c[slot].name)}</strong></div>`:'').join('');
  const rite=c.weirdness?.name?`<div class="tc-next-line rite"><span>Rite</span><p>${h(c.weirdness.name)}</p></div>`:'';
  const chaos=c.chaosTrigger?`<div class="tc-next-line chaos"><span>Chaos</span><p>${h(personalizePlayers(c.chaosTrigger,state).toLowerCase().replace(/^\w/,m=>m.toUpperCase()))}</p></div>`:'';
  const wiki=tcWikiUrl(c.target.name,'boss');
  return `<div class="tc-grace-next" role="button" tabindex="0" aria-label="Open the encounter against ${h(c.target.name)}">
    <div class="tc-next-head"><span>Next fight</span><h3>${h(c.target.name)}</h3></div>
    <div class="tc-next-weapons">${weapons}</div>
    ${chaos}${rite}
    <div class="tc-next-links">${wiki?`<a href="${wiki}" target="_blank" rel="noopener noreferrer external">Boss wiki</a>`:''}<a href="${TC_AR_CALCULATOR}" target="_blank" rel="noopener noreferrer external">AR calculator</a><b>Open encounter</b></div>
  </div>`;
}
function tcMountGraceRefresh(){
  const panel=app.querySelector('.tc-sanctuary-panel[data-panel="grace"]');
  if(!panel||!run?.state)return;
  panel.classList.add('tc-grace-refresh');
  panel.querySelector('.tc-panel-heading')?.classList.add('tc-refresh-hidden');
  let caption=panel.querySelector('.tc-grace-region');
  if(!caption){caption=document.createElement('div');caption.className='tc-grace-region';panel.appendChild(caption);}
  caption.textContent=String(run.state.region||'').replace(/ · DLC$/,'');
  panel.querySelector('.tc-grace-next')?.remove();
  const holder=document.createElement('div');holder.innerHTML=tcGraceNextCard(run.state);
  const card=holder.firstElementChild;
  if(card){
    panel.appendChild(card);
    const open=()=>{uiScreen='encounter';pendingRevealId=null;renderRun();};
    card.addEventListener('click',event=>{if(event.target.closest('a'))return;open();});
    card.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();open();}});
  }
}

/* Progress */
function tcRunRegions(state){
  const names=Object.keys(regions).filter(r=>state.includeDlc||!r.includes('· DLC'));
  return names;
}
function tcRegionRemembrances(state,region){
  const req=requiredRemembrances(state).filter(name=>REMEMBRANCE_REGION[name]===region);
  return {total:req.length,done:req.filter(name=>hasRemembrance(state,name)).length};
}
function tcRunFacts(state){
  const history=Array.isArray(state.history)?state.history:[];
  const fights=history.length;
  const chaos=history.filter(x=>x.chaosTriggered).length;
  const rites=history.filter(x=>x.riteOutcome==='Honored').length;
  const masterworks=smithingData(state).masterworks.length;
  const times=history.map(x=>Date.parse(x.completedAt)).filter(Number.isFinite);
  const start=times.length?Math.min(...times):Date.parse(state.current?.createdAt)||Date.now();
  const days=Math.max(1,Math.round((Date.now()-start)/86400000));
  const plural=(n,one,many)=>`${n} ${n===1?one:many}`;
  return [
    `<strong>${fights}</strong> ${fights===1?'fight':'fights'} won over <strong>${days}</strong> ${days===1?'day':'days'}.`,
    `Chaos was unleashed in <strong>${chaos}</strong> of them.`,
    `<strong>${rites}</strong> Odd ${rites===1?'Rite':'Rites'} honored.`,
    `${plural(masterworks,'weapon','weapons')} made Masterworks.`.replace(/^(\d+)/,'<strong>$1</strong>')
  ];
}
function tcJourneyMarkup(state){
  const cleared=new Set(state.clearedRegions||[]),names=tcRunRegions(state);
  return names.map(region=>{
    const here=region===state.region,done=cleared.has(region);
    const status=here?'here':done?'done':'ahead';
    const rem=tcRegionRemembrances(state,region),short=region.replace(/ · DLC$/,'');
    let detail='';
    if(here){
      const need=capstoneRequirement(state)-state.cleared,exit=regions[region]?.exit;
      detail=`<div class="tc-road-detail"><p>${state.cleared} ${state.cleared===1?'boss':'bosses'} felled here.</p><p>${need>0?`${need} more ${need===1?'fight':'fights'} before ${h(exit||'the capstone')} can be drawn.`:`${h(exit||'The capstone')} can now be drawn.`}</p>${rem.total?`<p>${rem.done} of ${rem.total} ${rem.total===1?'remembrance':'remembrances'} claimed here.</p>`:''}</div>`;
    }
    const dlc=region.includes('· DLC')?'<i>DLC</i>':'';
    return `<li class="tc-road-stop ${status}"><span class="tc-road-medal" style="background-image:url('${actualRegionImage(region)}')"></span><div class="tc-road-text"><strong>${h(short)}${dlc}</strong>${!here&&rem.total?`<small>${rem.done}/${rem.total} remembrances</small>`:''}${detail}</div></li>`;
  }).join('');
}
function tcRuneRingMarkup(state){
  const req=requiredRemembrances(state),n=req.length,done=req.filter(name=>hasRemembrance(state,name)).length;
  const R=96,cx=120,cy=120;
  const runes=req.map((name,i)=>{
    const a=-Math.PI/2+i*2*Math.PI/n,x=cx+R*Math.cos(a),y=cy+R*Math.sin(a),got=hasRemembrance(state,name),dlc=(REMEMBRANCE_REGION[name]||'').includes('· DLC');
    return `<g class="tc-rune-mark ${got?'got':''} ${dlc?'dlc':''}" data-rune="${h(name)}" data-i="${i}" transform="translate(${x.toFixed(1)} ${y.toFixed(1)})" role="button" tabindex="-1" aria-label="${h(name)}${got?', claimed':', not yet'}"><circle r="11"/><path d="M0-6v12M-5-2l5-4 5 4M-4 4h8"/></g>`;
  }).join('');
  return `<div class="tc-rune-ring"><svg viewBox="0 0 240 240" data-no-swipe tabindex="0" role="slider" aria-label="Remembrances. Drag or use the arrow keys to turn the ring." aria-valuemin="1" aria-valuemax="${n}" aria-valuenow="1"><path class="tc-ring-notch" d="M114 2h12l-6 9z"/><circle class="tc-ring-line" cx="${cx}" cy="${cy}" r="${R}"/><circle class="tc-ring-inner" cx="${cx}" cy="${cy}" r="${R-30}"/><g class="tc-ring-rot">${runes}</g><text x="${cx}" y="${cy+4}" class="tc-ring-count">${done}</text><text x="${cx}" y="${cy+30}" class="tc-ring-of">of ${n} remembrances</text></svg></div>`;
}
// The ring turns under a finger and snaps to the nearest rune; the rune under
// the notch at the top is described in the caption below. Tapping a rune turns
// it to the top; tapping the one already there opens its sheet.
function tcRuneCaption(state,name){
  const got=hasRemembrance(state,name),region=String(REMEMBRANCE_REGION[name]||'').replace(/ · DLC$/,'');
  const history=Array.isArray(state.history)?state.history:[];
  const key=n=>typeof tcBossKey==='function'?tcBossKey(n):String(n||'').toLowerCase();
  const idx=history.findIndex(x=>key(x?.name)===key(name)),win=idx>=0?history[idx]:null;
  const lines=[];
  if(got&&win){
    const when=win.completedAt?new Date(win.completedAt).toLocaleDateString(undefined,{weekday:'long',month:'long',day:'numeric'}):'';
    lines.push(`Claimed${when?` ${when}`:''}${win.region?` in ${String(win.region).replace(/ · DLC$/,'')}`:''}. Fight ${history.length-idx} of ${history.length}.`);
    const w=[win.chaseWeapon,win.morganWeapon].filter(Boolean);
    if(w.length)lines.push(`Felled with ${w.join(' and ')}${win.chaosTriggered?', Chaos and all':''}.`);
  }else if(got)lines.push('Claimed.');
  else lines.push(region===String(state.region||'').replace(/ · DLC$/,'')?`Waiting in this region.`:`Not claimed yet. It waits in ${region||'a later region'}.`);
  const forge=(typeof TC_REMEMBRANCE_WEAPONS!=='undefined'&&TC_REMEMBRANCE_WEAPONS[name])||[];
  if(forge.length)lines.push(`Hewg forges: ${forge.join(', ')}.`);
  return `<strong>${h(name)}</strong>${lines.map(l=>`<p>${h(l)}</p>`).join('')}`;
}
function tcBindRuneRing(svg,state){
  if(!svg)return;
  const marks=[...svg.querySelectorAll('.tc-rune-mark')],n=marks.length;if(!n)return;
  const step=360/n,cx=120,cy=120,R=96,rot=svg.querySelector('.tc-ring-rot');
  const caption=svg.closest('.tc-progress-new')?.querySelector('.tc-rune-caption');
  const still=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
  let angle=0,focus=-1,anim=0;
  const base=marks.map((m,i)=>{const a=-Math.PI/2+i*2*Math.PI/n;return [cx+R*Math.cos(a),cy+R*Math.sin(a)];});
  const draw=()=>{
    rot.setAttribute('transform',`rotate(${angle.toFixed(2)} ${cx} ${cy})`);
    marks.forEach((m,i)=>m.setAttribute('transform',`translate(${base[i][0].toFixed(1)} ${base[i][1].toFixed(1)}) rotate(${(-angle).toFixed(2)})`));
  };
  const nearest=()=>((Math.round(-angle/step)%n)+n)%n;
  const setFocus=i=>{
    if(i===focus)return;focus=i;
    marks.forEach((m,j)=>m.classList.toggle('focus',j===i));
    svg.setAttribute('aria-valuenow',String(i+1));svg.setAttribute('aria-valuetext',marks[i].dataset.rune);
    if(caption)caption.innerHTML=tcRuneCaption(state,marks[i].dataset.rune);
  };
  const turnTo=i=>{
    cancelAnimationFrame(anim);
    // Shortest way round to bring rune i to the top.
    let target=-i*step;while(target-angle>180)target-=360;while(target-angle<-180)target+=360;
    if(still()){angle=target;draw();setFocus(i);return;}
    const from=angle,t0=performance.now(),dur=280;
    const tick=now=>{const k=Math.min(1,(now-t0)/dur),e=1-Math.pow(1-k,3);angle=from+(target-from)*e;draw();if(k<1)anim=requestAnimationFrame(tick);else setFocus(i);};
    anim=requestAnimationFrame(tick);
  };
  const pointAngle=ev=>{const r=svg.getBoundingClientRect();return Math.atan2(ev.clientY-(r.top+r.height/2),ev.clientX-(r.left+r.width/2))*180/Math.PI;};
  let drag=null;
  svg.addEventListener('pointerdown',ev=>{cancelAnimationFrame(anim);drag={id:ev.pointerId,last:pointAngle(ev),x:ev.clientX,y:ev.clientY,moved:false,rune:ev.target.closest('[data-rune]')};try{svg.setPointerCapture(ev.pointerId);}catch(_){}});
  svg.addEventListener('pointermove',ev=>{
    if(!drag||ev.pointerId!==drag.id)return;
    if(!drag.moved&&Math.hypot(ev.clientX-drag.x,ev.clientY-drag.y)<6)return;
    drag.moved=true;const a=pointAngle(ev);let d=a-drag.last;if(d>180)d-=360;if(d<-180)d+=360;drag.last=a;angle+=d;draw();setFocus(nearest());
  });
  const end=ev=>{
    if(!drag||ev.pointerId!==drag.id)return;const d=drag;drag=null;
    if(d.moved){turnTo(nearest());return;}
    if(d.rune){const i=Number(d.rune.dataset.i);if(i===focus)tcOpenRuneSheet(d.rune.dataset.rune);else turnTo(i);}
  };
  svg.addEventListener('pointerup',end);svg.addEventListener('pointercancel',ev=>{if(drag&&ev.pointerId===drag.id){drag=null;turnTo(nearest());}});
  svg.addEventListener('keydown',ev=>{
    if(ev.key==='ArrowRight'||ev.key==='ArrowDown'){ev.preventDefault();turnTo(((focus<0?0:focus)+1)%n);}
    else if(ev.key==='ArrowLeft'||ev.key==='ArrowUp'){ev.preventDefault();turnTo(((focus<0?0:focus)-1+n)%n);}
    else if((ev.key==='Enter'||ev.key===' ')&&focus>=0){ev.preventDefault();tcOpenRuneSheet(marks[focus].dataset.rune);}
  });
  draw();
}
function tcOpenRuneSheet(name){
  const state=run.state,got=hasRemembrance(state,name),region=REMEMBRANCE_REGION[name]||'';
  const win=(state.history||[]).find(x=>typeof tcBossKey==='function'?tcBossKey(x.name)===tcBossKey(name):x.name===name);
  const when=win?.completedAt?new Date(win.completedAt).toLocaleDateString(undefined,{month:'short',day:'numeric'}):'';
  const body=got?`<p>Claimed${win?.region?` in ${h(win.region.replace(/ · DLC$/,''))}`:''}${when?` on ${h(when)}`:''}.</p>`:`<p>Not claimed yet. It waits in ${h(region.replace(/ · DLC$/,'')||'a later region')}.</p>`;
  const el=tcStrategicOverlay(name,body);el.querySelector('.tc-kicker').textContent='Remembrance';const close=el.querySelector('[data-close-strategy]');if(close)close.textContent='Done';
}
function tcMountProgressRefresh(){
  const panel=app.querySelector('.tc-sanctuary-panel[data-panel="progress"]');
  if(!panel||panel.dataset.refreshed||!run?.state)return;
  panel.dataset.refreshed='1';panel.classList.add('tc-progress-refresh');
  panel.querySelector('.tc-panel-heading')?.classList.add('tc-refresh-hidden');
  const state=run.state;
  const box=document.createElement('div');box.className='tc-progress-new';
  box.innerHTML=`<h4 class="tc-forge-h">The road so far</h4><ol class="tc-road">${tcJourneyMarkup(state)}</ol>
    <h4 class="tc-forge-h">The run</h4><div class="tc-run-row">${tcRuneRingMarkup(state)}<div class="tc-run-facts">${tcRunFacts(state).map(line=>`<p>${line}</p>`).join('')}</div></div><div class="tc-rune-caption" aria-live="polite"><p class="tc-rune-hint">Turn the ring to read each remembrance.</p></div>`;
  panel.appendChild(box);
  // Start with the stop before this one fully in view at the top, so no medal is cut.
  requestAnimationFrame(()=>{const road=box.querySelector('.tc-road'),here=road?.querySelector('.tc-road-stop.here');if(!road||!here)return;const prev=here.previousElementSibling||here;road.scrollTop=Math.max(0,prev.offsetTop-parseFloat(getComputedStyle(road).paddingTop||0));});
  try{tcBindRuneRing(box.querySelector('.tc-rune-ring svg'),state);}catch(error){console.warn('Rune ring skipped',error);}
}
const tcRenderSanctuaryBeforeRefresh=renderSanctuary;
renderSanctuary=function(){
  tcRenderSanctuaryBeforeRefresh();
  try{tcMountGraceRefresh();}catch(error){console.warn('Grace refresh skipped',error);}
  try{tcMountProgressRefresh();}catch(error){console.warn('Progress refresh skipped',error);}
};
document.addEventListener('click',event=>{
  const rune=event.target.closest('[data-rune]');if(!rune||rune.closest('.tc-rune-ring'))return;
  event.preventDefault();tcOpenRuneSheet(rune.dataset.rune);
});
/* --- End Site of Grace refresh --- */
