/* --- Covenant restyle: presentation-only markup adjustments ---------------
   Everything here changes how existing screens are labelled or arranged.
   Nothing reads from or writes to the saved run, and no handler, ID or
   data-* hook used by gameplay is removed. Styling lives in src/theme.css. */

// Bottom navigation: short labels, decorative glyphs hidden from screen readers.
const tcNavMarkupBeforeRestyle=navMarkup;
navMarkup=function(active){
  return tcNavMarkupBeforeRestyle(active)
    .replace('<nav class="tc-bottom-nav">','<nav class="tc-bottom-nav" aria-label="Main">')
    .replace('<span>Site of Grace</span>','<span>Grace</span>')
    .replace(/<span class="nicon">/g,'<span class="nicon" aria-hidden="true">');
};
// Ledger · Progress: each Remembrance shows where it is and whether that region
// is reachable yet. Read-only: uses the same helpers the travel screen uses.
function tcRemembranceStatus(state,name){
  if(hasRemembrance(state,name))return {key:'done',label:'claimed'};
  const region=REMEMBRANCE_REGION[name]||'';
  if(region&&state?.region===region)return {key:'here',label:'this region'};
  let open=false;try{open=Boolean(region&&regionUnlocked(state,region));}catch(_){open=false;}
  return open?{key:'open',label:'open'}:{key:'locked',label:'locked'};
}
remembranceLedgerBody=function(state){
  const req=requiredRemembrances(state),done=req.filter(x=>hasRemembrance(state,x));
  const regionNames=Object.keys(regions).filter(r=>state.includeDlc||!r.includes('· DLC')).filter(r=>r!=='The Erdtree');
  const ticks=req.map(name=>`<span class="${hasRemembrance(state,name)?'on':''}"></span>`).join('');
  const rows=req.map(name=>{const st=tcRemembranceStatus(state,name);return `<div class="tc-rem ${st.key==='done'?'done':''} tc-rem-${st.key}" role="listitem"><i class="tc-rem-mark" aria-hidden="true"></i><span class="tc-rem-name">${h(name)}<small>${h(REMEMBRANCE_REGION[name]||'')}</small></span><span class="stamp">${h(st.label)}</span></div>`;}).join('');
  return `<div class="tc-ledger-head"><div class="tc-ledger-count">${done.length}</div><div><div class="tc-ledger-of">of ${req.length} Remembrances</div><div class="tc-muted">The final seal opens only when the ledger is complete.</div></div></div>
    <div class="tc-rem-ticks" aria-hidden="true" style="grid-template-columns:repeat(${Math.max(1,req.length)},minmax(0,1fr))">${ticks}</div>
    <div class="tc-panel"><div class="tc-rem-grid" role="list">${rows}</div></div>
    <div class="tc-kicker gold" style="margin-top:20px">world progress</div><div class="tc-region-list">${regionNames.map(r=>`<div class="tc-region-chip ${(state.clearedRegions||[]).includes(r)?'done':''}">${h(r)}${r===state.region?' · ACTIVE':(state.clearedRegions||[]).includes(r)?' · CLEARED':''}</div>`).join('')}</div>`;
};

// Ledger · Smithing: boon counters become a tappable grid with a one-line
// explanation, replacing the long paragraph. Pure presentation; the counts
// and every redeem button come from the existing markup unchanged.
const TC_BOON_HELP=[
  [/^appeal waiver/i,'Optional to spend: makes one Weapon Appeal penalty-free.'],
  [/^chaos refresh/i,'Amend the current Chaos decree.'],
  [/^rite refresh/i,'Amend the current Odd Rite.'],
  [/^blank amendment/i,'Converts into either a Chaos or a Rite Refresh.'],
  [/^dynasty frequent flier/i,'Each grants 5 Mohgwyn bird-farming visits.'],
  [/^sanctioned boss kill/i,'Record one eligible optional boss in a reached region as killed.'],
  [/^covenant veto/i,'Veto an optional assignment, with the extra treasury payment shown.'],
  [/^letters? of clemency/i,'Strike one Weapon Appeal penalty from the current encounter.'],
  [/^union discount/i,'Your next Bell Bearing Contract costs 3 less Favor.'],
  [/^joint appeal/i,'Reroll both weapons without a penalty.']
];
let tcBoonHelpSelected='';
function tcBoonHelpText(label){const hit=TC_BOON_HELP.find(([re])=>re.test(label));return hit?hit[1]:'';}
function tcEnhanceBoonGrid(){
  const ledger=document.querySelector('.tc-ledger-screen .tc-boon-ledger');
  const grid=ledger?.querySelector('.tc-boon-grid');
  if(!grid||grid.dataset.tcHelp)return;
  grid.dataset.tcHelp='1';
  const cells=[...grid.children].filter(el=>el.tagName==='DIV');
  let preferred=null;
  cells.forEach(cell=>{
    const label=cell.querySelector('span')?.textContent?.trim()||'';
    const count=Number(cell.querySelector('strong')?.textContent||0);
    const btn=document.createElement('button');
    btn.type='button';btn.className='tc-boon-cell'+(count>0?' held':'');
    btn.dataset.boonHelp=label;btn.setAttribute('aria-pressed','false');
    btn.innerHTML=cell.innerHTML;
    cell.replaceWith(btn);
    if(label===tcBoonHelpSelected)preferred=btn;
    if(!preferred&&count>0)preferred=btn;
  });
  const note=document.createElement('p');note.className='tc-boon-help';note.setAttribute('aria-live','polite');
  grid.after(note);
  const longCopy=[...ledger.children].filter(el=>el.classList.contains('tc-muted')).at(-1);
  if(longCopy){
    const suffix=(longCopy.textContent.split(' · ').slice(1).join(' · ')||'').trim();
    longCopy.hidden=true;
    if(suffix){const extra=document.createElement('p');extra.className='tc-boon-extra';extra.textContent=suffix;note.after(extra);}
  }
  tcSelectBoonHelp(preferred||grid.querySelector('.tc-boon-cell'));
}
function tcSelectBoonHelp(btn){
  if(!btn)return;
  const grid=btn.closest('.tc-boon-grid'),note=grid?.nextElementSibling;
  grid?.querySelectorAll('.tc-boon-cell').forEach(b=>{const on=b===btn;b.classList.toggle('selected',on);b.setAttribute('aria-pressed',on?'true':'false');});
  tcBoonHelpSelected=btn.dataset.boonHelp||'';
  if(note?.classList.contains('tc-boon-help'))note.innerHTML=`<strong>${h(tcBoonHelpSelected)}</strong> · ${h(tcBoonHelpText(tcBoonHelpSelected))}`;
}
if(!window.__tcBoonHelpBound){
  window.__tcBoonHelpBound=true;
  document.addEventListener('click',event=>{const btn=event.target.closest?.('.tc-boon-cell');if(btn)tcSelectBoonHelp(btn);});
}
const tcRenderLedgerBeforeRestyle=renderLedger;
renderLedger=function(){
  tcRenderLedgerBeforeRestyle();
  try{tcEnhanceBoonGrid();}catch(error){console.warn('Boon grid presentation skipped',error);}
};
/* Swipe paging for the Grace and Encounter screens. The tracks never pan
   under the finger (CSS: touch-action:pan-y, horizontal overflow hidden, no
   native snapping). A sideways swipe turns exactly one page by pressing the
   neighbouring tab, so index, tab state and saving follow the existing path.
   The page turn itself is animated here frame by frame, because iOS Safari
   does not reliably run smooth scrollTo on a container it cannot pan. */
function tcPagingTabs(track){return track?.parentElement?.querySelector('.tc-encounter-tabs,.tc-sanctuary-tabs')||null;}
function tcAnimateTrackTo(track,index){
  if(!track)return;
  const target=Math.max(0,index)*track.clientWidth,from=track.scrollLeft,dist=target-from;
  (track.__tcFlip||[]).forEach(anim=>{try{anim.cancel();}catch(_){}});track.__tcFlip=null;
  if(Math.abs(dist)<1){track.scrollLeft=target;return;}
  // Jump the scroll position at once (the app reads its page index from it),
  // then slide the pages from where they were with a transform, which the
  // graphics chip runs on its own at the display's frame rate.
  track.scrollLeft=target;track.dispatchEvent(new Event('scroll'));
  if(!Element.prototype.animate||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  track.__tcFlip=[...track.children].map(panel=>panel.animate([{transform:`translate3d(${dist}px,0,0)`},{transform:'translate3d(0,0,0)'}],{duration:320,easing:'cubic-bezier(.22,.8,.24,1)'}));
}
if(!window.__tcSwipePagingBound){
  window.__tcSwipePagingBound=true;
  let tcSwipe=null;
  const trackOf=el=>el?.closest?.('.tc-encounter-track,.tc-sanctuary-track');
  const turn=(track,dir)=>{
    const buttons=[...(tcPagingTabs(track)?.querySelectorAll('button')||[])];
    if(!buttons.length)return;
    const current=Math.round(track.scrollLeft/Math.max(1,track.clientWidth));
    const next=Math.max(0,Math.min(buttons.length-1,current+dir));
    if(next!==current)buttons[next].click();
  };
  const decide=(touch,final)=>{
    const s=tcSwipe;if(!s||s.done||!touch)return;
    if(!document.contains(s.track)){tcSwipe=null;return;}
    const dx=touch.clientX-s.x,dy=touch.clientY-s.y;
    if(!final&&Math.abs(dy)>24&&Math.abs(dy)>Math.abs(dx)){s.done=true;return;}
    if(Math.abs(dx)>=(final?40:56)&&Math.abs(dx)>Math.abs(dy)*1.25){s.done=true;turn(s.track,dx<0?1:-1);}
  };
  document.addEventListener('touchstart',event=>{
    const track=trackOf(event.target);
    if(!track||event.touches.length!==1||event.target.closest('input,select,textarea')){tcSwipe=null;return;}
    const t=event.touches[0];tcSwipe={track,x:t.clientX,y:t.clientY,done:false};
  },{passive:true,capture:true});
  document.addEventListener('touchmove',event=>decide(event.touches[0],false),{passive:true,capture:true});
  document.addEventListener('touchend',event=>{decide(event.changedTouches[0],true);tcSwipe=null;},{passive:true,capture:true});
  document.addEventListener('touchcancel',event=>{decide(event.changedTouches?.[0],true);tcSwipe=null;},{passive:true,capture:true});
  /* Every page change (tab tap or swipe) gets the frame-by-frame turn. Runs
     after the app's own tab handler, which has already set the index. */
  document.addEventListener('click',event=>{
    const btn=event.target.closest?.('.tc-encounter-tabs button,.tc-sanctuary-tabs button');if(!btn)return;
    const tabs=btn.parentElement,track=tabs?.parentElement?.querySelector('.tc-encounter-track,.tc-sanctuary-track');
    tcAnimateTrackTo(track,[...tabs.querySelectorAll('button')].indexOf(btn));
  });
  /* No native snapping now, so keep the current page aligned on resize/rotate. */
  window.addEventListener('resize',()=>{document.querySelectorAll('.tc-encounter-track,.tc-sanctuary-track').forEach(track=>{
    const buttons=[...(tcPagingTabs(track)?.querySelectorAll('button')||[])],i=buttons.findIndex(b=>b.classList.contains('active'));
    if(i>=0)track.scrollLeft=i*track.clientWidth;});},{passive:true});
}
/* Battery: animations only run where they can be seen. Grace/Encounter pages
   that are not the visible tab are paused (IntersectionObserver on the track),
   and effect layers for the pulsing buttons/seal are added here so the CSS
   can animate cheap opacity/transform layers instead of repainting. */
const tcAnimObserved=new WeakSet();
let tcAnimObserver=null;
function tcAnimVisibilityObserver(){
  if(tcAnimObserver||typeof IntersectionObserver==='undefined')return tcAnimObserver;
  tcAnimObserver=new IntersectionObserver(entries=>{
    for(const entry of entries)entry.target.classList.toggle('tc-anim-paused',!entry.isIntersecting||entry.intersectionRatio<0.02);
  },{threshold:[0,0.02,0.5]});
  return tcAnimObserver;
}
function tcAddFxLayers(button){
  if(!button||button.querySelector(':scope>.tc-fx-glow'))return;
  button.insertAdjacentHTML('afterbegin','<span class="tc-fx-glow" aria-hidden="true"></span><span class="tc-fx-sweep" aria-hidden="true"></span>');
}
function tcBatteryScan(){
  const observer=tcAnimVisibilityObserver();
  if(observer)document.querySelectorAll('.tc-encounter-panel,.tc-sanctuary-panel').forEach(panel=>{if(!tcAnimObserved.has(panel)){tcAnimObserved.add(panel);observer.observe(panel);}});
  const seal=document.querySelector('#triggerChaos.tc-seal-inline');if(seal&&!seal.disabled)tcAddFxLayers(seal);
  const endure=document.querySelector('.tc-chaos-event #ackChaos');if(endure)tcAddFxLayers(endure);
  const flame=document.querySelector('svg.tc-grace-native-svg:not([data-tc-layered])');
  if(flame&&typeof CSSRule!=='undefined')tcLayerGraceFlame(flame);
  const row=document.querySelector('.tc-feature.chaos .tc-feature-row');
  if(row&&document.querySelector('#triggerChaos')&&!row.querySelector(':scope>.tc-seal-flare'))row.insertAdjacentHTML('afterbegin','<span class="tc-seal-flare" aria-hidden="true"></span>');
}
if(!window.__tcBatteryBound){
  window.__tcBatteryBound=true;
  let queued=false;
  const schedule=()=>{if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;try{tcBatteryScan();}catch(error){console.warn('Battery scan skipped',error);}});};
  const start=()=>{const host=document.querySelector('#app');if(host)new MutationObserver(schedule).observe(host,{childList:true,subtree:true});schedule();};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
  // A rotation or a size class change redraws the flame at the new scale.
  window.addEventListener('resize',()=>{if(!tcGraceLayersStale())return;const btn=document.querySelector('.tc-grace-idle-button');if(btn&&typeof tcGraceNativeMarkup==='function'){btn.innerHTML=tcGraceNativeMarkup();if(typeof tcQueueIdleGrace==='function')tcQueueIdleGrace();schedule();}},{passive:true});
}
/* Battery: the Grace flame, layered. Each of the 24 animated pieces is moved
   into its own small <svg> layer (same viewBox, stacked exactly over the
   original), and its animation is moved onto that layer. Inside one SVG every
   frame repaints the whole drawing; separate layers are only moved and faded
   by the graphics chip. Every piece keeps its own timing, origin and path, so
   the motion is the same. Pixel units in the keyframes are SVG units, so they
   are rescaled to the drawn size. */
const TC_GRACE_ANIMATED='.tcg-pool,.tcg-flame-body,.tcg-root,.tcg-wisp,.tcg-core,.tcg-mote';
let tcGraceKeyframeSheet=null;const tcGraceKeyframesMade=new Set();
function tcFindKeyframes(name){
  let found=null;
  for(const sheet of document.styleSheets){let rules;try{rules=sheet.cssRules;}catch(_){continue;}
    for(const rule of rules)if(rule.type===CSSRule.KEYFRAMES_RULE&&rule.name===name)found=rule;}
  return found;
}
function tcScaledKeyframesName(name,scale){
  const key=`${name}__L${Math.round(scale*1000)}`;
  if(tcGraceKeyframesMade.has(key))return key;
  const source=tcFindKeyframes(name);if(!source)return null;
  if(!tcGraceKeyframeSheet){tcGraceKeyframeSheet=document.createElement('style');tcGraceKeyframeSheet.id='tc-grace-layer-keyframes';document.head.appendChild(tcGraceKeyframeSheet);}
  const body=[...source.cssRules].map(frame=>frame.cssText.replace(/(-?\d*\.?\d+)px/g,(_,n)=>`${(Number(n)*scale).toFixed(3)}px`)).join('');
  tcGraceKeyframeSheet.textContent+=`@keyframes ${key}{${body}}`;
  tcGraceKeyframesMade.add(key);return key;
}
let tcGraceLayerCache=null;
function tcLayerGraceFlame(svg){
  if(!svg||svg.dataset.tcLayered||!(svg instanceof SVGSVGElement))return;
  const vb=svg.viewBox.baseVal;if(!vb||!vb.width)return;
  const rect=svg.getBoundingClientRect();if(!rect.width||!rect.height)return;
  // Same drawn size as last time: reuse the finished layers instead of
  // measuring all 24 pieces again (that measuring is what made Grace slow to open).
  const cacheKey=`${Math.round(rect.width*10)}x${Math.round(rect.height*10)}`;
  if(tcGraceLayerCache?.key===cacheKey){const tpl=document.createElement('template');tpl.innerHTML=tcGraceLayerCache.html;svg.replaceWith(tpl.content.firstElementChild);return;}
  const scale=Math.min(rect.width/vb.width,rect.height/vb.height),offX=(rect.width-vb.width*scale)/2,offY=(rect.height-vb.height*scale)/2;
  const wrapper=document.createElement('div');
  wrapper.className=svg.getAttribute('class')+' tcg-layered';wrapper.setAttribute('aria-hidden','true');wrapper.dataset.tcLayered='1';
  const base=svg.cloneNode(false);base.removeAttribute('class');base.setAttribute('class','tcg-layer tcg-base');
  const pieces=[...svg.querySelectorAll(TC_GRACE_ANIMATED)];
  const plans=pieces.map(el=>{
    const cs=getComputedStyle(el),names=cs.animationName.split(',').map(x=>x.trim());
    let ux,uy;const [ox,oy]=cs.transformOrigin.split(' ').map(parseFloat);
    if(cs.transformBox==='fill-box'){const b=el.getBBox();ux=b.x+ox;uy=b.y+oy;}else{ux=vb.x+ox;uy=vb.y+oy;}
    const prev=el.style.animation;el.style.animation='none';const baseOpacity=getComputedStyle(el).opacity;el.style.animation=prev;
    return {el,baseOpacity,anim:{names,duration:cs.animationDuration,delay:cs.animationDelay,timing:cs.animationTimingFunction,count:cs.animationIterationCount,direction:cs.animationDirection,fill:cs.animationFillMode},ux,uy};
  });
  // Static parts (defs, anything not animated) stay in a base layer.
  for(const child of [...svg.childNodes]){if(child.nodeType===1&&child.matches(TC_GRACE_ANIMATED))continue;base.appendChild(child.cloneNode(true));}
  wrapper.appendChild(base);
  for(const plan of plans){
    // Each layer is cropped to its own piece (plus room for the glow), so the
    // graphics memory is a few small tiles rather than 24 full-size ones.
    const m=14,b=plan.el.getBBox(),vx=b.x-m,vy=b.y-m,vw=b.width+2*m,vh=b.height+2*m;
    const layer=svg.cloneNode(false);layer.removeAttribute('class');layer.setAttribute('class','tcg-layer');
    layer.setAttribute('viewBox',`${vx} ${vy} ${vw} ${vh}`);layer.setAttribute('preserveAspectRatio','none');
    const piece=plan.el.cloneNode(true);layer.appendChild(piece);
    const names=plan.anim.names.map(n=>n==='none'?'none':(tcScaledKeyframesName(n,scale)||n));
    const left=offX+(vx-vb.x)*scale,top=offY+(vy-vb.y)*scale,ox=((plan.ux-vx)*scale).toFixed(3),oy=((plan.uy-vy)*scale).toFixed(3);
    layer.style.cssText=`left:${left.toFixed(3)}px;top:${top.toFixed(3)}px;width:${(vw*scale).toFixed(3)}px;height:${(vh*scale).toFixed(3)}px;opacity:${plan.baseOpacity};transform-origin:${ox}px ${oy}px;animation-name:${names.join(',')};animation-duration:${plan.anim.duration};animation-delay:${plan.anim.delay};animation-timing-function:${plan.anim.timing};animation-iteration-count:${plan.anim.count};animation-direction:${plan.anim.direction};animation-fill-mode:${plan.anim.fill};`;
    wrapper.appendChild(layer);
  }
  wrapper.dataset.tcScale=String(scale);
  tcGraceLayerCache={key:cacheKey,html:wrapper.outerHTML};
  svg.replaceWith(wrapper);
}
function tcGraceLayersStale(){
  const wrapper=document.querySelector('.tc-grace-native-svg.tcg-layered');if(!wrapper)return false;
  const layer=wrapper.querySelector('.tcg-layer');const vb=layer?.viewBox?.baseVal;const r=wrapper.getBoundingClientRect();
  if(!vb||!r.width)return false;
  return Math.abs(Math.min(r.width/vb.width,r.height/vb.height)-Number(wrapper.dataset.tcScale||0))>0.01;
}
/* Smoothness: when a bottom-bar tab is pressed, the next screen glides in
   (opacity + a small rise, compositor-only) and the gold marker slides from
   the old tab to the new one. Classes are set from a MutationObserver, which
   runs before the browser paints the new screen, so there is no flash. */
let tcScreenEnter=null;
document.addEventListener('click',event=>{
  const btn=event.target.closest?.('.tc-bottom-nav [data-screen]');if(!btn||btn.classList.contains('active'))return;
  const nav=btn.closest('.tc-bottom-nav'),buttons=[...nav.querySelectorAll('button')],old=nav.querySelector('button.active');
  // Measure now, while the old screen is laid out, so the new screen never
  // has to be measured before its first paint.
  const r=nav.getBoundingClientRect();
  tcScreenEnter={at:performance.now(),navLeft:r.left,navWidth:r.width,count:buttons.length,fromIndex:old?buttons.indexOf(old):-1,screen:btn.dataset.screen};
},true);
function tcApplyScreenEnter(){
  if(!tcScreenEnter||performance.now()-tcScreenEnter.at>1500){tcScreenEnter=null;return;}
  const host=document.querySelector('#app'),nav=host?.querySelector('.tc-bottom-nav'),active=nav?.querySelector('button.active');
  if(!host||!active)return;
  const info=tcScreenEnter;tcScreenEnter=null;
  if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  // The new screen's elements are fresh, so adding the class starts their
  // glide without forcing a layout.
  host.classList.add('tc-screen-enter');
  clearTimeout(host.__tcEnterTimer);host.__tcEnterTimer=setTimeout(()=>host.classList.remove('tc-screen-enter'),400);
  const buttons=[...nav.querySelectorAll('button')],toIndex=buttons.indexOf(active);
  if(info.fromIndex>=0&&toIndex>=0&&buttons.length===info.count){const step=info.navWidth/info.count;nav.style.setProperty('--tc-nav-from',`${Math.round((info.fromIndex-toIndex)*step)}px`);nav.classList.add('tc-nav-slide');}
}
if(!window.__tcScreenEnterBound){
  window.__tcScreenEnterBound=true;
  const watch=()=>{const host=document.querySelector('#app');if(host)new MutationObserver(()=>{if(tcScreenEnter)tcApplyScreenEnter();}).observe(host,{childList:true});};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',watch);else watch();
}
/* --- End Covenant restyle markup adjustments --- */
