from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

css=r'''
/* --- CHAOS REVEAL III: one-screen compact layout --- */
.tc-chaos-event{
  box-sizing:border-box;
  height:calc(100svh - 70px);
  min-height:0;
  padding:7px 10px 9px;
  overflow:hidden;
  display:flex;
  flex-direction:column;
}
.tc-chaos-event .tc-ember-field{position:fixed;inset:0 0 70px;z-index:-1}
.tc-chaos-head{
  flex:0 0 auto;
  grid-template-columns:1fr auto;
  padding:3px 3px 7px;
  min-height:29px;
}
.tc-chaos-head>span:first-child{display:none}
.tc-chaos-head strong{text-align:left;font-size:13px;letter-spacing:.18em}
.tc-chaos-head .favor{font-size:7px;line-height:1.15;max-width:110px}
.tc-chaos-crumb{display:none}
.tc-chaos-card{
  flex:1 1 auto;
  min-height:0;
  width:100%;
  max-width:610px;
  margin:4px auto 0;
  padding:8px 11px 10px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  overflow:hidden;
}
.tc-chaos-art-wrap{
  flex:0 0 auto;
  width:min(53vw,215px);
  height:min(47vw,190px);
  aspect-ratio:auto;
  margin:-2px auto 2px;
  border-radius:50%;
  overflow:hidden;
  background:
    radial-gradient(circle at 50% 50%,rgba(229,93,44,.33) 0 4%,transparent 5%),
    repeating-conic-gradient(from 0deg,rgba(205,145,66,.42) 0 1deg,transparent 1deg 30deg),
    radial-gradient(circle,transparent 0 29%,rgba(179,105,45,.55) 30% 31%,transparent 32% 45%,rgba(151,54,33,.5) 46% 47%,transparent 48% 61%,rgba(174,124,62,.27) 62% 63%,transparent 64%),
    radial-gradient(circle,#1a0d09 0 42%,#080605 66%,transparent 71%);
  box-shadow:inset 0 0 35px #000,0 0 32px rgba(164,47,26,.16);
  animation:chaosArtEnter .8s cubic-bezier(.16,.78,.2,1) both;
}
.tc-chaos-art-wrap:before,.tc-chaos-art-wrap:after{
  content:"";position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
  pointer-events:none
}
.tc-chaos-art-wrap:before{
  width:50%;height:50%;border:2px solid rgba(203,118,56,.65);border-radius:50%;
  box-shadow:0 0 15px rgba(226,72,37,.36),inset 0 0 18px rgba(210,64,31,.22)
}
.tc-chaos-art-wrap:after{
  width:2px;height:72%;background:linear-gradient(transparent,#e05b32 24%,#f09055 50%,#e05b32 76%,transparent);
  box-shadow:0 0 9px #d84f2e;opacity:.75
}
.tc-chaos-art{width:100%;height:100%;object-fit:cover;border-radius:50%;position:relative;z-index:1}
.tc-chaos-halo{z-index:2;inset:3%}
.tc-chaos-title{
  flex:0 0 auto;
  font-size:clamp(25px,7vw,36px);
  line-height:.94;
  margin:1px 0 5px;
}
.tc-chaos-rule{margin:0 auto 7px;width:64%}
.tc-chaos-label{font-size:7px;margin:3px 0;letter-spacing:.21em}
.tc-chaos-event-name{
  flex:0 0 auto;
  font-size:clamp(20px,5.8vw,29px);
  line-height:1.02;
  margin:4px auto 7px;
}
.tc-chaos-reading{
  flex:0 0 auto;
  margin:0 auto;
  padding:7px 10px 8px;
  width:min(100%,520px);
}
.tc-chaos-consequence{font-size:clamp(13px,3.75vw,16px);line-height:1.3}
.tc-chaos-quip{
  flex:0 0 auto;
  font-size:11px;
  line-height:1.25;
  margin:7px auto 8px;
  max-height:30px;
  overflow:hidden;
}
.tc-chaos-event .btn{
  flex:0 0 auto;
  width:min(470px,94%);
  min-height:40px;
  height:40px;
  margin:0 auto;
  font-size:10px;
}
@media(max-height:760px){
  .tc-chaos-art-wrap{width:168px;height:148px}
  .tc-chaos-title{font-size:25px}
  .tc-chaos-event-name{font-size:20px}
  .tc-chaos-consequence{font-size:13px}
  .tc-chaos-quip{display:none}
}
@media(max-height:690px){
  .tc-chaos-art-wrap{width:132px;height:116px}
  .tc-chaos-title{font-size:22px}
  .tc-chaos-rule{margin-bottom:4px}
  .tc-chaos-event-name{font-size:18px;margin-bottom:4px}
  .tc-chaos-reading{padding:5px 8px 6px}
  .tc-chaos-event .btn{height:37px;min-height:37px}
}
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

new_render=r'''function renderChaosEvent(){
  const c=run.state.current;
  const eventName=chaosEventName(c.chaosConsequence||'');
  const reward=Number(c.chaosFavor??1);
  const embers=Array.from({length:18},(_,i)=>`<i class="tc-ember" style="--x:${(i*41)%101}%;--dur:${5.5+(i%6)*.8}s;--delay:${-(i%7)*.71}s;--drift:${((i%5)-2)*11}px"></i>`).join('');
  app.innerHTML=`<section class="tc-chaos-event">
    <div class="tc-ember-field">${embers}</div>
    <div class="tc-chaos-head"><strong>Encounter</strong><span class="favor">${reward>0?`+${reward} FAVOR IF SURVIVED`:'NO FAVOR'}</span></div>
    <div class="tc-chaos-card">
      <div class="tc-chaos-art-wrap"><img class="tc-chaos-art" src="./assets/chaos-seal.webp?v=3" alt="Cracking Covenant seal" onerror="this.remove()"><div class="tc-chaos-halo"></div></div>
      <div class="tc-chaos-title">Chaos Unleashed</div><div class="tc-chaos-rule"></div>
      <div class="tc-chaos-label">Event</div><div class="tc-chaos-event-name">${h(eventName)}</div>
      <div class="tc-chaos-reading"><div class="tc-chaos-label" style="color:#a84835">Consequence</div><div class="tc-chaos-consequence">${h(personalizePlayers(c.chaosConsequence,run.state))}</div></div>
      <div class="tc-chaos-quip">“${h(eventName==='DARK SOULS DEPARTMENT'?'The Covenant has requested older, worse game design.':pick(chaosQuips))}”</div>
      <button id="ackChaos" class="btn">Endure Decree</button>
    </div>
  </section>${navMarkup('encounter')}`;
  bindNav();
  document.querySelector('#ackChaos').addEventListener('click',()=>{acknowledgedChaos.add(c.id);uiScreen='encounter';renderRun();});
}'''
pat=r'function renderChaosEvent\(\)\{.*?\n\}'
s,n=re.subn(pat,new_render,s,count=1,flags=re.S)
if n!=1: raise SystemExit('renderChaosEvent target missing')

for required in ['height:calc(100svh - 70px)','onerror="this.remove()"','Endure Decree','tc-chaos-reading']:
    if required not in s: raise SystemExit('compact Chaos invariant missing: '+required)

p.write_text(s)
