from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Idempotent Grace-only ritual layer. Remove the retired image-frame renderer too.
for start,end in [
    ('Idle Site of Grace ritual','End Idle Site of Grace ritual'),
    ('Idle Site of Grace behavior','End Idle Site of Grace behavior'),
    ('Stable Grace frame renderer','End Stable Grace frame renderer'),
    ('Stable Grace frame behavior','End Stable Grace frame behavior'),
]:
    s=re.sub(r"\n?/\* --- "+re.escape(start)+r" --- \*/.*?/\* --- "+re.escape(end)+r" --- \*/\n?", "\n", s, flags=re.S)

css=r'''
/* --- Idle Site of Grace ritual --- */
.tc-sanctuary-panel[data-panel="grace"]{display:flex!important;flex-direction:column!important}
.tc-grace-idle{
  position:relative;flex:1 1 132px;min-height:108px;max-height:190px;margin:4px 0 0;
  display:flex;align-items:center;justify-content:center;overflow:hidden;user-select:none;-webkit-user-select:none;
}
.tc-grace-idle-button{
  appearance:none;-webkit-appearance:none;position:relative;width:min(236px,68vw);height:142px;
  border:0;background:transparent;color:var(--gold-bright);padding:0 0 18px;touch-action:manipulation;
  -webkit-tap-highlight-color:transparent;outline-offset:2px;
}
.tc-grace-idle-button:focus-visible{outline:1px solid rgba(224,193,123,.55)}
.tc-grace-native-glow{
  position:absolute;left:50%;top:54%;width:78%;height:67%;transform:translate(-50%,-50%);
  border-radius:50%;background:radial-gradient(ellipse,rgba(236,207,137,.20),rgba(198,161,90,.07) 40%,transparent 72%);
  filter:blur(9px);opacity:.68;pointer-events:none;animation:tcGraceNativeGlow 3.1s ease-in-out infinite;
}
.tc-grace-native-svg{
  position:absolute;left:50%;top:49%;width:210px;height:132px;transform:translate(-50%,-50%);
  overflow:visible;pointer-events:none;
}
.tc-grace-native-svg .tcg-pool{fill:none;stroke-linecap:round;transform-origin:110px 116px}
.tc-grace-native-svg .tcg-pool.outer{stroke:rgba(224,193,123,.44);stroke-width:1.15;animation:tcGracePoolOuter 3.4s ease-in-out infinite}
.tc-grace-native-svg .tcg-pool.middle{stroke:rgba(243,216,151,.72);stroke-width:1.25;animation:tcGracePoolMiddle 2.45s ease-in-out infinite}
.tc-grace-native-svg .tcg-pool.inner{stroke:rgba(255,235,181,.9);stroke-width:1.45;animation:tcGracePoolInner 1.9s ease-in-out infinite}
.tc-grace-native-svg .tcg-wisp{
  fill:none;stroke-linecap:round;stroke-linejoin:round;transform-box:fill-box;transform-origin:center bottom;
  filter:drop-shadow(0 0 3px rgba(255,226,154,.72)) drop-shadow(0 0 8px rgba(198,161,90,.28));
}
.tc-grace-native-svg .tcg-wisp.main{stroke:rgba(255,239,196,.96);stroke-width:2.8;animation:tcGraceWispMain 2.15s ease-in-out infinite alternate}
.tc-grace-native-svg .tcg-wisp.left{stroke:rgba(229,194,117,.76);stroke-width:1.6;animation:tcGraceWispLeft 2.8s ease-in-out .2s infinite alternate}
.tc-grace-native-svg .tcg-wisp.right{stroke:rgba(237,204,128,.72);stroke-width:1.45;animation:tcGraceWispRight 2.45s ease-in-out .55s infinite alternate}
.tc-grace-native-svg .tcg-wisp.crown{stroke:rgba(255,229,165,.72);stroke-width:1.25;animation:tcGraceCrown 1.8s ease-in-out infinite alternate}
.tc-grace-native-svg .tcg-core{fill:rgba(255,239,194,.92);filter:drop-shadow(0 0 5px rgba(255,218,133,.85));animation:tcGraceCore 1.65s ease-in-out infinite alternate}
.tc-grace-native-svg .tcg-mote{
  fill:#e6c477;filter:drop-shadow(0 0 3px rgba(224,193,123,.7));opacity:0;transform-box:fill-box;transform-origin:center;
}
.tc-grace-native-svg .m1{animation:tcGraceMoteA 2.8s linear .15s infinite}
.tc-grace-native-svg .m2{animation:tcGraceMoteB 3.25s linear 1.05s infinite}
.tc-grace-native-svg .m3{animation:tcGraceMoteC 2.55s linear .7s infinite}
.tc-grace-native-svg .m4{animation:tcGraceMoteA 3.5s linear 1.8s infinite}
.tc-grace-idle-caption{
  position:absolute;left:0;right:0;bottom:3px;text-align:center;
  font:800 6.7px/1.15 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.17em;color:#746a56;
  transition:color .18s ease,opacity .18s ease;
}
.tc-grace-idle-button:active .tc-grace-idle-caption,.tc-grace-idle-button.tc-tapped .tc-grace-idle-caption{color:#c6aa6d}
.tc-grace-idle-button.tc-paid .tc-grace-idle-caption{color:#8d7a50}
.tc-grace-idle-button.tc-tapped .tc-grace-native-glow{animation:none;opacity:1;transform:translate(-50%,-50%) scale(1.12)}
.tc-grace-idle-button.tc-tapped .tc-grace-native-svg{animation:tcGraceNativeTap .28s ease-out}
.tc-grace-idle-spark{
  position:absolute;left:50%;top:56%;width:3px;height:3px;border-radius:50%;background:#f2d385;
  box-shadow:0 0 8px #e2b450;pointer-events:none;animation:tcGraceTapSpark .5s ease-out forwards;
}
@keyframes tcGraceNativeGlow{0%,100%{opacity:.48;transform:translate(-50%,-50%) scale(.95)}45%{opacity:.78;transform:translate(-50%,-50%) scale(1.04)}70%{opacity:.62;transform:translate(-50%,-50%) scale(.99)}}
@keyframes tcGracePoolOuter{0%,100%{opacity:.45;transform:scaleX(.95)}50%{opacity:.82;transform:scaleX(1.035)}}
@keyframes tcGracePoolMiddle{0%,100%{opacity:.52;transform:scaleX(.93)}48%{opacity:1;transform:scaleX(1.04)}}
@keyframes tcGracePoolInner{0%,100%{opacity:.68;transform:scaleX(.96)}55%{opacity:1;transform:scaleX(1.05)}}
@keyframes tcGraceWispMain{from{opacity:.78;transform:rotate(-2deg) scaleY(.97)}to{opacity:1;transform:rotate(2.3deg) scaleY(1.035)}}
@keyframes tcGraceWispLeft{from{opacity:.42;transform:rotate(-3.5deg) scaleY(.94)}to{opacity:.82;transform:rotate(2deg) scaleY(1.04)}}
@keyframes tcGraceWispRight{from{opacity:.38;transform:rotate(3deg) scaleY(.95)}to{opacity:.78;transform:rotate(-2.5deg) scaleY(1.05)}}
@keyframes tcGraceCrown{from{opacity:.35;transform:rotate(-4deg) scale(.94)}to{opacity:.78;transform:rotate(3deg) scale(1.04)}}
@keyframes tcGraceCore{from{opacity:.7;transform:scale(.85)}to{opacity:1;transform:scale(1.15)}}
@keyframes tcGraceMoteA{0%{opacity:0;transform:translate(0,0) scale(.55)}18%{opacity:.85}100%{opacity:0;transform:translate(-14px,-52px) scale(1.05)}}
@keyframes tcGraceMoteB{0%{opacity:0;transform:translate(0,0) scale(.5)}16%{opacity:.75}100%{opacity:0;transform:translate(19px,-58px) scale(1.1)}}
@keyframes tcGraceMoteC{0%{opacity:0;transform:translate(0,0) scale(.6)}20%{opacity:.9}100%{opacity:0;transform:translate(8px,-43px) scale(.9)}}
@keyframes tcGraceNativeTap{0%{transform:translate(-50%,-50%) scale(1);filter:brightness(1)}35%{transform:translate(-50%,-50%) scale(1.045);filter:brightness(1.28)}100%{transform:translate(-50%,-50%) scale(1);filter:brightness(1)}}
@keyframes tcGraceTapSpark{0%{opacity:1;transform:translate(0,0) scale(1)}100%{opacity:0;transform:translate(var(--tx),var(--ty)) scale(.2)}}
@media(max-height:740px){
  .tc-grace-idle{flex-basis:106px;min-height:88px;max-height:148px;margin-top:2px}
  .tc-grace-idle-button{height:112px;width:min(206px,60vw);padding-bottom:14px}
  .tc-grace-native-svg{width:178px;height:112px}.tc-grace-idle-caption{font-size:6.1px}
}
@media(max-height:650px){
  .tc-grace-idle{flex-basis:82px;min-height:70px;max-height:108px}
  .tc-grace-idle-button{height:88px;width:170px;padding-bottom:10px}
  .tc-grace-native-svg{width:150px;height:94px}.tc-grace-idle-caption{font-size:5.6px}
}
@media(prefers-reduced-motion:reduce){
  .tc-grace-native-glow,.tc-grace-native-svg *{animation:none!important}
  .tc-grace-native-svg .tcg-mote{display:none}
}
/* --- End Idle Site of Grace ritual --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Idle Site of Grace behavior --- */
const TC_GRACE_FAVOR_ODDS=5000;
const TC_GRACE_TAP_COOLDOWN_MS=400;
let tcGraceLastTapAt=0;
let tcGraceFavorBusy=false;

function tcGraceFavorPaidForCurrentEncounter(){
  const id=run?.state?.current?.id;
  return Boolean(id && run?.state?.graceIdleFavorEncounterId===id);
}
function tcGraceIdleCaption(){
  return tcGraceFavorPaidForCurrentEncounter()?'discretionary favor already issued':'touch grace';
}
function tcGraceTapPulse(btn){
  btn.classList.remove('tc-tapped');void btn.offsetWidth;btn.classList.add('tc-tapped');
  window.setTimeout(()=>btn.classList.remove('tc-tapped'),280);
  for(let i=0;i<7;i++){
    const spark=document.createElement('i');spark.className='tc-grace-idle-spark';
    spark.style.setProperty('--tx',`${Math.round((Math.random()-.5)*92)}px`);
    spark.style.setProperty('--ty',`${-22-Math.round(Math.random()*58)}px`);
    btn.appendChild(spark);window.setTimeout(()=>spark.remove(),560);
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
function tcGraceNativeMarkup(){
  return `<span class="tc-grace-native-glow"></span>
  <svg class="tc-grace-native-svg" viewBox="0 0 220 150" aria-hidden="true" focusable="false">
    <ellipse class="tcg-pool outer" cx="110" cy="116" rx="58" ry="11"></ellipse>
    <ellipse class="tcg-pool middle" cx="110" cy="116" rx="45" ry="8"></ellipse>
    <ellipse class="tcg-pool inner" cx="110" cy="116" rx="30" ry="5"></ellipse>
    <path class="tcg-wisp left" d="M108 114 C94 102 91 90 98 78 C105 67 102 56 94 47"></path>
    <path class="tcg-wisp right" d="M112 114 C128 102 132 90 124 77 C118 67 122 57 132 47"></path>
    <path class="tcg-wisp main" d="M110 114 C106 98 118 88 114 75 C109 62 116 53 113 42 C110 32 115 26 112 18"></path>
    <path class="tcg-wisp crown" d="M112 38 C102 33 103 26 110 22 C117 18 117 13 113 9"></path>
    <circle class="tcg-core" cx="110" cy="115" r="3.1"></circle>
    <circle class="tcg-mote m1" cx="89" cy="96" r="1.6"></circle>
    <circle class="tcg-mote m2" cx="130" cy="91" r="1.25"></circle>
    <circle class="tcg-mote m3" cx="103" cy="82" r="1.15"></circle>
    <circle class="tcg-mote m4" cx="121" cy="104" r="1.4"></circle>
  </svg>
  <span class="tc-grace-idle-caption"></span>`;
}
function tcEnsureIdleGrace(){
  const panel=document.querySelector('.tc-sanctuary-panel[data-panel="grace"]');if(!panel)return;
  const tools=panel.querySelector('.tc-grace-ar-tools');if(!tools)return;
  let idle=panel.querySelector('.tc-grace-idle');
  if(!idle){
    idle=document.createElement('div');idle.className='tc-grace-idle';
    idle.innerHTML=`<button type="button" class="tc-grace-idle-button" aria-label="Touch the Site of Grace">${tcGraceNativeMarkup()}</button>`;
    tools.insertAdjacentElement('afterend',idle);
    idle.querySelector('.tc-grace-idle-button')?.addEventListener('click',e=>tcTryGraceFavor(e.currentTarget));
  }else if(idle.previousElementSibling!==tools){tools.insertAdjacentElement('afterend',idle);}
  const btn=idle.querySelector('.tc-grace-idle-button');const cap=idle.querySelector('.tc-grace-idle-caption');
  if(btn && !btn.querySelector('.tc-grace-native-svg')){
    btn.innerHTML=tcGraceNativeMarkup();
    btn.addEventListener('click',e=>tcTryGraceFavor(e.currentTarget));
  }
  if(btn)btn.classList.toggle('tc-paid',tcGraceFavorPaidForCurrentEncounter());
  if(cap)cap.textContent=tcGraceIdleCaption();
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
  'tc-grace-native-svg','tcGraceNativeMarkup','graceIdleFavorEncounterId',
  'Administrative anomaly detected. +1 Smithing Favor.','tcEnsureIdleGrace'
]:
    if needle not in s: raise SystemExit('Idle Grace invariant missing: '+needle)
for retired in ['TC_GRACE_ART_FRAMES','tc-grace-idle-art-frame','Stable Grace frame renderer']:
    if retired in s: raise SystemExit('Retired image Grace residue: '+retired)

p.write_text(s)
