from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Idempotent late Grace-only interaction layer.
s=re.sub(r"\n?/\* --- Idle Site of Grace ritual --- \*/.*?/\* --- End Idle Site of Grace ritual --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Idle Site of Grace behavior --- \*/.*?/\* --- End Idle Site of Grace behavior --- \*/\n?", "\n", s, flags=re.S)

css=r'''
/* --- Idle Site of Grace ritual --- */
.tc-sanctuary-panel[data-panel="grace"]{display:flex!important;flex-direction:column!important}
.tc-grace-idle{
  position:relative;flex:1 1 140px;min-height:112px;max-height:220px;margin:5px 0 0;overflow:visible;
  display:flex;align-items:center;justify-content:center;user-select:none;-webkit-user-select:none;
}
.tc-grace-idle-button{
  appearance:none;-webkit-appearance:none;position:relative;width:min(232px,64vw);height:100%;
  min-height:108px;max-height:214px;border:0;background:transparent;color:var(--gold-bright);padding:0 0 17px;
  touch-action:manipulation;-webkit-tap-highlight-color:transparent;outline-offset:2px;
}
.tc-grace-idle-button:focus-visible{outline:1px solid rgba(224,193,123,.55)}
.tc-grace-idle-glow{
  position:absolute;left:50%;top:52%;width:82%;height:62%;transform:translate(-50%,-50%);
  background:radial-gradient(ellipse,rgba(224,193,123,.16),rgba(198,161,90,.055) 43%,transparent 72%);
  filter:blur(11px);opacity:.72;pointer-events:none;animation:tcGraceArtAura 2.8s ease-in-out infinite;
}
.tc-grace-idle-art{
  position:absolute;left:50%;top:50%;width:min(218px,60vw);height:calc(100% - 10px);
  transform:translate(-50%,-51%);object-fit:contain;object-position:center bottom;pointer-events:none;
  filter:drop-shadow(0 0 8px rgba(238,207,138,.24)) drop-shadow(0 0 24px rgba(198,161,90,.12));
  will-change:contents,filter,transform;
}
.tc-grace-idle-caption{
  position:absolute;left:0;right:0;bottom:1px;text-align:center;
  font:800 6.8px/1.15 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.16em;color:#756a53;
  transition:color .2s ease,opacity .2s ease;
}
.tc-grace-idle-button:active .tc-grace-idle-caption,.tc-grace-idle-button.tc-tapped .tc-grace-idle-caption{color:#bca36b}
.tc-grace-idle-button.tc-paid .tc-grace-idle-caption{color:#8d7a50}
.tc-grace-idle-button.tc-tapped .tc-grace-idle-art{animation:tcGraceArtTap .31s ease-out}
.tc-grace-idle-spark{
  position:absolute;left:50%;top:54%;width:3px;height:3px;border-radius:50%;background:#f2d385;
  box-shadow:0 0 8px #e2b450;pointer-events:none;animation:tcGraceTapSpark .55s ease-out forwards;
}
@keyframes tcGraceArtAura{0%,100%{opacity:.48;transform:translate(-50%,-50%) scale(.94)}50%{opacity:.82;transform:translate(-50%,-50%) scale(1.06)}}
@keyframes tcGraceArtTap{0%{transform:translate(-50%,-51%) scale(1);filter:brightness(1)}35%{transform:translate(-50%,-51%) scale(1.055);filter:brightness(1.38)}100%{transform:translate(-50%,-51%) scale(1);filter:brightness(1)}}
@keyframes tcGraceTapSpark{0%{opacity:1;transform:translate(0,0) scale(1)}100%{opacity:0;transform:translate(var(--tx),var(--ty)) scale(.25)}}
@media(max-height:740px){
  .tc-grace-idle{flex-basis:100px;min-height:86px;max-height:145px;margin-top:3px}
  .tc-grace-idle-button{width:min(185px,52vw);min-height:84px;max-height:142px;padding-bottom:13px}
  .tc-grace-idle-art{width:min(174px,49vw);height:calc(100% - 7px)}
  .tc-grace-idle-caption{font-size:6.1px}
}
@media(max-height:650px){
  .tc-grace-idle{flex-basis:76px;min-height:68px;max-height:105px}
  .tc-grace-idle-button{width:150px;min-height:66px;max-height:102px;padding-bottom:10px}
  .tc-grace-idle-art{width:142px}.tc-grace-idle-caption{font-size:5.6px}
}
@media(prefers-reduced-motion:reduce){
  .tc-grace-idle-glow,.tc-grace-idle-button.tc-tapped .tc-grace-idle-art{animation:none!important}
}
/* --- End Idle Site of Grace ritual --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Idle Site of Grace behavior --- */
const TC_GRACE_FAVOR_ODDS=5000;
const TC_GRACE_TAP_COOLDOWN_MS=400;
const TC_GRACE_ART_FRAMES=[
  './assets/grace/grace-idle-1.svg',
  './assets/grace/grace-idle-2.svg',
  './assets/grace/grace-idle-3.svg',
  './assets/grace/grace-idle-4.svg'
];
const TC_GRACE_FRAME_SEQUENCE=[0,1,2,1,0,3];
const TC_GRACE_FRAME_DELAYS=[430,145,105,155,335,235];
const tcGraceFrameTimers=new WeakMap();
let tcGraceLastTapAt=0;
let tcGraceFavorBusy=false;

function tcGraceFavorPaidForCurrentEncounter(){
  const id=run?.state?.current?.id;
  return Boolean(id && run?.state?.graceIdleFavorEncounterId===id);
}
function tcGraceIdleCaption(){
  return tcGraceFavorPaidForCurrentEncounter()?'discretionary favor already issued':'touch grace';
}
function tcStartGraceArt(btn){
  const img=btn?.querySelector('.tc-grace-idle-art');if(!img)return;
  const previous=tcGraceFrameTimers.get(btn);if(previous)clearTimeout(previous);
  img.src=TC_GRACE_ART_FRAMES[0];
  if(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)return;
  TC_GRACE_ART_FRAMES.forEach(src=>{const pre=new Image();pre.src=src;});
  let step=0;
  const advance=()=>{
    if(!btn.isConnected){tcGraceFrameTimers.delete(btn);return;}
    step=(step+1)%TC_GRACE_FRAME_SEQUENCE.length;
    img.src=TC_GRACE_ART_FRAMES[TC_GRACE_FRAME_SEQUENCE[step]];
    const base=TC_GRACE_FRAME_DELAYS[step];
    const jitter=Math.round((Math.random()-.5)*54);
    const timer=setTimeout(advance,Math.max(85,base+jitter));
    tcGraceFrameTimers.set(btn,timer);
  };
  const timer=setTimeout(advance,TC_GRACE_FRAME_DELAYS[0]);
  tcGraceFrameTimers.set(btn,timer);
}
function tcGraceTapPulse(btn){
  btn.classList.remove('tc-tapped');void btn.offsetWidth;btn.classList.add('tc-tapped');
  const img=btn.querySelector('.tc-grace-idle-art');if(img)img.src=TC_GRACE_ART_FRAMES[2];
  window.setTimeout(()=>btn.classList.remove('tc-tapped'),310);
  for(let i=0;i<6;i++){
    const spark=document.createElement('i');spark.className='tc-grace-idle-spark';
    spark.style.setProperty('--tx',`${Math.round((Math.random()-.5)*88)}px`);
    spark.style.setProperty('--ty',`${-24-Math.round(Math.random()*58)}px`);
    btn.appendChild(spark);window.setTimeout(()=>spark.remove(),620);
  }
}
async function tcTryGraceFavor(btn){
  const now=Date.now();if(now-tcGraceLastTapAt<TC_GRACE_TAP_COOLDOWN_MS)return;
  tcGraceLastTapAt=now;tcGraceTapPulse(btn);
  const encounterId=run?.state?.current?.id;if(!encounterId)return;
  if(tcGraceFavorPaidForCurrentEncounter()){
    btn.classList.add('tc-paid');const cap=btn.querySelector('.tc-grace-idle-caption');if(cap)cap.textContent=tcGraceIdleCaption();return;
  }
  if(Math.floor(Math.random()*TC_GRACE_FAVOR_ODDS)!==0 || tcGraceFavorBusy)return;
  tcGraceFavorBusy=true;
  const next=smithingCopy(run.state);
  if(next.graceIdleFavorEncounterId===encounterId){tcGraceFavorBusy=false;return;}
  next.smithing.favor=Number(next.smithing.favor||0)+1;
  next.graceIdleFavorEncounterId=encounterId;
  next.lastAction='A Site of Grace produced an administrative anomaly. +1 Smithing Favor.';
  next.updatedAt=new Date().toISOString();
  try{await commit(next,{successToast:'Administrative anomaly detected. +1 Smithing Favor.'});}
  finally{tcGraceFavorBusy=false;}
}
function tcEnsureIdleGrace(){
  const panel=document.querySelector('.tc-sanctuary-panel[data-panel="grace"]');if(!panel)return;
  const tools=panel.querySelector('.tc-grace-ar-tools');if(!tools)return;
  let idle=panel.querySelector('.tc-grace-idle');
  if(!idle){
    idle=document.createElement('div');idle.className='tc-grace-idle';
    idle.innerHTML=`<button type="button" class="tc-grace-idle-button" aria-label="Touch the Site of Grace"><span class="tc-grace-idle-glow"></span><img class="tc-grace-idle-art" alt="" aria-hidden="true" draggable="false"><span class="tc-grace-idle-caption"></span></button>`;
    tools.insertAdjacentElement('afterend',idle);
    const created=idle.querySelector('.tc-grace-idle-button');
    created?.addEventListener('click',e=>tcTryGraceFavor(e.currentTarget));
    if(created)tcStartGraceArt(created);
  }else if(idle.previousElementSibling!==tools){tools.insertAdjacentElement('afterend',idle);}
  const btn=idle.querySelector('.tc-grace-idle-button');const cap=idle.querySelector('.tc-grace-idle-caption');
  if(btn)btn.classList.toggle('tc-paid',tcGraceFavorPaidForCurrentEncounter());
  if(cap)cap.textContent=tcGraceIdleCaption();
  if(btn && !tcGraceFrameTimers.has(btn) && !window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)tcStartGraceArt(btn);
}
let tcIdleGraceQueued=false;
function tcQueueIdleGrace(){if(tcIdleGraceQueued)return;tcIdleGraceQueued=true;requestAnimationFrame(()=>{tcIdleGraceQueued=false;tcEnsureIdleGrace();});}
const tcIdleGraceObserver=new MutationObserver(tcQueueIdleGrace);
tcIdleGraceObserver.observe(document.body,{childList:true,subtree:true});
document.addEventListener('click',e=>{if(e.target.closest('.tc-bottom-nav,.tc-sanctuary-tabs,[data-screen]'))setTimeout(tcQueueIdleGrace,0);});
setTimeout(tcQueueIdleGrace,0);
/* --- End Idle Site of Grace behavior --- */
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in [
  'Idle Site of Grace ritual','TC_GRACE_FAVOR_ODDS=5000','TC_GRACE_TAP_COOLDOWN_MS=400',
  'TC_GRACE_ART_FRAMES','grace-idle-4.svg','tcStartGraceArt','graceIdleFavorEncounterId',
  'Administrative anomaly detected. +1 Smithing Favor.','tcEnsureIdleGrace','tc-grace-idle-art'
]:
    if needle not in s: raise SystemExit('Idle Grace invariant missing: '+needle)

p.write_text(s)
