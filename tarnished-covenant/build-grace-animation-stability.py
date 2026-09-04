from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

s=re.sub(r"\n?/\* --- Stable Grace frame renderer --- \*/.*?/\* --- End Stable Grace frame renderer --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Stable Grace frame behavior --- \*/.*?/\* --- End Stable Grace frame behavior --- \*/\n?", "\n", s, flags=re.S)

css=r'''
/* --- Stable Grace frame renderer --- */
.tc-grace-idle-art-stack{position:absolute;inset:0;pointer-events:none}
.tc-grace-idle-art-frame{
  position:absolute;left:50%;top:50%;width:min(218px,60vw);height:calc(100% - 10px);
  object-fit:contain;object-position:center bottom;opacity:0;
  transform:translate(-50%,-51%);transition:opacity 72ms linear;
  filter:drop-shadow(0 0 8px rgba(238,207,138,.24)) drop-shadow(0 0 24px rgba(198,161,90,.12));
  will-change:opacity,transform,filter;
}
.tc-grace-idle-art-frame.tc-active{opacity:1}
.tc-grace-idle-art-frame[data-grace-frame="1"]{transform:translate(-50%,-51%) scale(.97)}
.tc-grace-idle-art-frame[data-grace-frame="2"]{transform:translate(-50%,-51%) scale(.95)}
.tc-grace-idle-art-frame[data-grace-frame="3"]{transform:translate(-50%,-50%) scaleX(.96) scaleY(1.08)}
.tc-grace-idle-button.tc-tapped .tc-grace-idle-art-frame.tc-active{filter:brightness(1.22) drop-shadow(0 0 12px rgba(238,207,138,.34)) drop-shadow(0 0 30px rgba(198,161,90,.18))}
@media(max-height:740px){.tc-grace-idle-art-frame{width:min(174px,49vw);height:calc(100% - 7px)}}
@media(max-height:650px){.tc-grace-idle-art-frame{width:142px}}
@media(prefers-reduced-motion:reduce){.tc-grace-idle-art-frame{transition:none!important}}
/* --- End Stable Grace frame renderer --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Stable Grace frame behavior --- */
const tcGraceStableTimers=new WeakMap();
function tcGraceStableShow(btn,index){
  const frames=btn?.querySelectorAll('.tc-grace-idle-art-frame');
  if(!frames?.length)return;
  frames.forEach((frame,i)=>frame.classList.toggle('tc-active',i===index));
  btn.dataset.graceFrame=String(index);
}
function tcStartGraceArt(btn){
  const previous=tcGraceStableTimers.get(btn);if(previous)clearTimeout(previous);
  tcGraceStableShow(btn,0);
  if(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)return;
  let step=0;
  const advance=()=>{
    if(!btn.isConnected){tcGraceStableTimers.delete(btn);return;}
    step=(step+1)%TC_GRACE_FRAME_SEQUENCE.length;
    tcGraceStableShow(btn,TC_GRACE_FRAME_SEQUENCE[step]);
    const base=TC_GRACE_FRAME_DELAYS[step];
    const jitter=Math.round((Math.random()-.5)*42);
    const timer=setTimeout(advance,Math.max(95,base+jitter));
    tcGraceStableTimers.set(btn,timer);
  };
  const timer=setTimeout(advance,TC_GRACE_FRAME_DELAYS[0]);
  tcGraceStableTimers.set(btn,timer);
}
function tcGraceTapPulse(btn){
  btn.classList.remove('tc-tapped');void btn.offsetWidth;btn.classList.add('tc-tapped');
  tcGraceStableShow(btn,2);
  window.setTimeout(()=>btn.classList.remove('tc-tapped'),240);
  for(let i=0;i<6;i++){
    const spark=document.createElement('i');spark.className='tc-grace-idle-spark';
    spark.style.setProperty('--tx',`${Math.round((Math.random()-.5)*88)}px`);
    spark.style.setProperty('--ty',`${-24-Math.round(Math.random()*58)}px`);
    btn.appendChild(spark);window.setTimeout(()=>spark.remove(),620);
  }
}
function tcEnsureIdleGrace(){
  const panel=document.querySelector('.tc-sanctuary-panel[data-panel="grace"]');if(!panel)return;
  const tools=panel.querySelector('.tc-grace-ar-tools');if(!tools)return;
  let idle=panel.querySelector('.tc-grace-idle');
  if(!idle){idle=document.createElement('div');idle.className='tc-grace-idle';tools.insertAdjacentElement('afterend',idle);}
  else if(idle.previousElementSibling!==tools){tools.insertAdjacentElement('afterend',idle);}
  let btn=idle.querySelector('.tc-grace-idle-button');
  if(!btn){btn=document.createElement('button');btn.type='button';btn.className='tc-grace-idle-button';btn.setAttribute('aria-label','Touch the Site of Grace');idle.replaceChildren(btn);}
  let stack=btn.querySelector('.tc-grace-idle-art-stack');
  if(!stack){
    btn.innerHTML=`<span class="tc-grace-idle-glow"></span><span class="tc-grace-idle-art-stack">${TC_GRACE_ART_FRAMES.map((src,i)=>`<img class="tc-grace-idle-art-frame${i===0?' tc-active':''}" data-grace-frame="${i}" src="${src}" alt="" aria-hidden="true" draggable="false" decoding="async">`).join('')}</span><span class="tc-grace-idle-caption"></span>`;
    btn.addEventListener('click',e=>tcTryGraceFavor(e.currentTarget));
    btn.querySelectorAll('.tc-grace-idle-art-frame').forEach(img=>{if(img.decode)img.decode().catch(()=>{});});
    tcStartGraceArt(btn);
  }
  const cap=btn.querySelector('.tc-grace-idle-caption');
  btn.classList.toggle('tc-paid',tcGraceFavorPaidForCurrentEncounter());
  if(cap)cap.textContent=tcGraceIdleCaption();
  if(!tcGraceStableTimers.has(btn) && !window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)tcStartGraceArt(btn);
}
setTimeout(tcQueueIdleGrace,0);
/* --- End Stable Grace frame behavior --- */
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in ['Stable Grace frame renderer','tcGraceStableShow','tc-grace-idle-art-frame','TC_GRACE_TAP_COOLDOWN_MS=400']:
    if needle not in s: raise SystemExit('Stable Grace invariant missing: '+needle)

p.write_text(s)
