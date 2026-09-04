from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Idempotent late Grace-only interaction layer.
s=re.sub(r"\n?/\* --- Idle Site of Grace ritual --- \*/.*?/\* --- End Idle Site of Grace ritual --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Idle Site of Grace behavior --- \*/.*?/\* --- End Idle Site of Grace behavior --- \*/\n?", "\n", s, flags=re.S)

css=r'''
/* --- Idle Site of Grace ritual --- */
.tc-grace-idle{
  position:relative;height:clamp(105px,17svh,155px);margin:5px 0 0;overflow:hidden;
  display:grid;place-items:center;flex:0 0 auto;user-select:none;-webkit-user-select:none;
}
.tc-grace-idle-button{
  appearance:none;-webkit-appearance:none;position:relative;width:172px;height:145px;
  border:0;background:transparent;color:var(--gold-bright);padding:0;touch-action:manipulation;
  -webkit-tap-highlight-color:transparent;outline-offset:2px;
}
.tc-grace-idle-button:focus-visible{outline:1px solid rgba(224,193,123,.55)}
.tc-grace-idle-aura{
  position:absolute;left:50%;bottom:29px;width:132px;height:72px;transform:translateX(-50%);
  background:radial-gradient(ellipse at 50% 72%,rgba(224,193,123,.24),rgba(198,161,90,.08) 42%,transparent 72%);
  filter:blur(6px);opacity:.78;animation:tcGraceAura 2.8s ease-in-out infinite;
}
.tc-grace-idle-pool{
  position:absolute;left:50%;bottom:31px;width:112px;height:18px;transform:translateX(-50%);
  border-radius:50%;border-top:1px solid rgba(238,207,138,.82);
  box-shadow:0 -2px 10px rgba(224,193,123,.30),0 0 22px rgba(198,161,90,.18);
  opacity:.9;animation:tcGracePool 2.15s ease-in-out infinite alternate;
}
.tc-grace-idle-stem{
  position:absolute;left:50%;bottom:35px;width:3px;height:66px;transform:translateX(-50%) rotate(-5deg);
  transform-origin:50% 100%;border-radius:80% 20% 70% 30%;
  background:linear-gradient(180deg,rgba(255,239,188,.96),rgba(224,193,123,.80) 42%,rgba(173,129,51,.12));
  box-shadow:0 0 8px rgba(255,221,142,.80),0 0 22px rgba(198,161,90,.42);
  animation:tcGraceStem 1.9s ease-in-out infinite alternate;
}
.tc-grace-idle-stem:before,.tc-grace-idle-stem:after{
  content:"";position:absolute;bottom:10px;width:2px;height:48px;border-radius:50%;
  background:linear-gradient(180deg,rgba(255,239,188,.9),rgba(224,193,123,.26),transparent);
  box-shadow:0 0 9px rgba(224,193,123,.55);transform-origin:50% 100%;
}
.tc-grace-idle-stem:before{left:-18px;transform:rotate(-55deg);animation:tcGraceBranchA 2.5s ease-in-out infinite alternate}
.tc-grace-idle-stem:after{right:-20px;transform:rotate(61deg);animation:tcGraceBranchB 2.15s ease-in-out infinite alternate}
.tc-grace-idle-wisp{position:absolute;left:50%;bottom:42px;width:2px;height:2px;border-radius:50%;background:#f3d992;box-shadow:0 0 7px #e4b95e;opacity:0}
.tc-grace-idle-wisp.w1{animation:tcGraceWisp 2.4s linear .15s infinite}
.tc-grace-idle-wisp.w2{animation:tcGraceWisp 2.9s linear 1.1s infinite}
.tc-grace-idle-wisp.w3{animation:tcGraceWispB 2.65s linear .7s infinite}
.tc-grace-idle-caption{
  position:absolute;left:0;right:0;bottom:5px;text-align:center;
  font:800 6.8px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.16em;color:#756a53;
  transition:color .2s ease,opacity .2s ease;
}
.tc-grace-idle-button:active .tc-grace-idle-caption,.tc-grace-idle-button.tc-tapped .tc-grace-idle-caption{color:#bca36b}
.tc-grace-idle-button.tc-tapped .tc-grace-idle-aura{animation:none;opacity:1;transform:translateX(-50%) scale(1.18)}
.tc-grace-idle-button.tc-tapped .tc-grace-idle-pool{box-shadow:0 -2px 15px rgba(246,215,145,.65),0 0 38px rgba(224,193,123,.34)}
.tc-grace-idle-button.tc-paid .tc-grace-idle-caption{color:#8d7a50}
.tc-grace-idle-spark{position:absolute;left:50%;bottom:49px;width:3px;height:3px;border-radius:50%;background:#f2d385;box-shadow:0 0 8px #e2b450;pointer-events:none;animation:tcGraceTapSpark .55s ease-out forwards}
@keyframes tcGraceAura{0%,100%{opacity:.52;transform:translateX(-50%) scale(.94)}50%{opacity:.88;transform:translateX(-50%) scale(1.06)}}
@keyframes tcGracePool{from{opacity:.62;transform:translateX(-50%) scaleX(.88)}to{opacity:1;transform:translateX(-50%) scaleX(1.06)}}
@keyframes tcGraceStem{from{transform:translateX(-50%) rotate(-7deg) scaleY(.96);opacity:.82}to{transform:translateX(-50%) rotate(-2deg) scaleY(1.04);opacity:1}}
@keyframes tcGraceBranchA{from{transform:rotate(-59deg) scaleY(.92);opacity:.5}to{transform:rotate(-49deg) scaleY(1.05);opacity:.94}}
@keyframes tcGraceBranchB{from{transform:rotate(66deg) scaleY(.88);opacity:.48}to{transform:rotate(55deg) scaleY(1.08);opacity:.92}}
@keyframes tcGraceWisp{0%{opacity:0;transform:translate(0,0) scale(.6)}15%{opacity:.8}100%{opacity:0;transform:translate(-27px,-67px) scale(1.25)}}
@keyframes tcGraceWispB{0%{opacity:0;transform:translate(2px,0) scale(.5)}18%{opacity:.75}100%{opacity:0;transform:translate(31px,-61px) scale(1.1)}}
@keyframes tcGraceTapSpark{0%{opacity:1;transform:translate(0,0) scale(1)}100%{opacity:0;transform:translate(var(--tx),var(--ty)) scale(.25)}}
@media(max-height:740px){.tc-grace-idle{height:92px}.tc-grace-idle-button{transform:scale(.78)}}
@media(max-height:650px){.tc-grace-idle{height:72px}.tc-grace-idle-button{transform:scale(.62)}}
@media(prefers-reduced-motion:reduce){.tc-grace-idle-aura,.tc-grace-idle-pool,.tc-grace-idle-stem,.tc-grace-idle-stem:before,.tc-grace-idle-stem:after,.tc-grace-idle-wisp{animation:none!important}.tc-grace-idle-wisp{display:none}}
/* --- End Idle Site of Grace ritual --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Idle Site of Grace behavior --- */
const TC_GRACE_FAVOR_ODDS=5000;
const TC_GRACE_TAP_COOLDOWN_MS=700;
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
  window.setTimeout(()=>btn.classList.remove('tc-tapped'),260);
  for(let i=0;i<5;i++){
    const spark=document.createElement('i');spark.className='tc-grace-idle-spark';
    spark.style.setProperty('--tx',`${Math.round((Math.random()-.5)*76)}px`);
    spark.style.setProperty('--ty',`${-22-Math.round(Math.random()*48)}px`);
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
    idle.innerHTML=`<button type="button" class="tc-grace-idle-button" aria-label="Touch the Site of Grace"><span class="tc-grace-idle-aura"></span><span class="tc-grace-idle-pool"></span><span class="tc-grace-idle-stem"></span><span class="tc-grace-idle-wisp w1"></span><span class="tc-grace-idle-wisp w2"></span><span class="tc-grace-idle-wisp w3"></span><span class="tc-grace-idle-caption"></span></button>`;
    tools.insertAdjacentElement('afterend',idle);
    idle.querySelector('.tc-grace-idle-button')?.addEventListener('click',e=>tcTryGraceFavor(e.currentTarget));
  }else if(idle.previousElementSibling!==tools){tools.insertAdjacentElement('afterend',idle);}
  const btn=idle.querySelector('.tc-grace-idle-button');const cap=idle.querySelector('.tc-grace-idle-caption');
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

for needle in ['Idle Site of Grace ritual','TC_GRACE_FAVOR_ODDS=5000','graceIdleFavorEncounterId','Administrative anomaly detected. +1 Smithing Favor.','tcEnsureIdleGrace','tc-grace-idle-button']:
    if needle not in s: raise SystemExit('Idle Grace invariant missing: '+needle)

p.write_text(s)
