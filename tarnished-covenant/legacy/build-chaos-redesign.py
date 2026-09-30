from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Old-Souls encounter rules: one assigned weapon per player remains the hard assumption.
js=r'''
const TC_OLD_SOULS_RITES = [
 ['Old Souls','No jumping for the entire encounter. Jump attacks are therefore also gone.','True',1],
 ['Dark Souls Department','No jumping, no jump attacks, no Flask of Wondrous Physick, and no weapon skills until victory.','Grand',2],
 ['Pre-2016 Combat Design','No jumping and no weapon skills for the entire encounter.','True',1],
 ['The Floor Is Fine','Neither player may jump. If somebody does, both players must fully disengage for five seconds before attacking again.','True',1],
 ['No Aerial Budget','Jump attacks are forbidden for the entire encounter. Normal jumping for traversal is allowed.','True',1],
 ['Grounded Employment','For the first 30 seconds after engaging the boss, neither player may jump or use a jump attack.','Minor',0]
];
TC_OLD_SOULS_RITES.forEach(r=>{weirdness.push([r[0],r[1]]);TC_RITE_META.set(r[0],{tier:r[2],favor:r[3]});});
TC_EXTRA_CHAOS.push(...[
 'DARK SOULS DEPARTMENT: no jumping, no jump attacks, no Physick, and no weapon skills until victory or wipe.',
 'OLD SOULS: no jumping for the rest of this attempt.',
 'NO AERIAL BUDGET: jump attacks are forbidden for the rest of this attempt.',
 'PRE-2016 COMBAT DESIGN: no jumping and no weapon skills until victory or wipe.',
 'GROUNDED: neither player may jump for the next 30 seconds.',
 'THE FLOOR IS FINE: if either player jumps, both must disengage for five seconds before attacking again.'
].map(text=>({text,favor:1})));
'''
marker='const TC_MERCIFUL_CHAOS = new Set(['
if marker not in s: raise SystemExit('merciful Chaos marker missing')
s=s.replace(marker,js+'\n'+marker,1)

# Event naming should preserve special authored Chaos names.
old="function chaosEventName(text){\n  const t=text.toUpperCase();"
new="function chaosEventName(text){\n  const t=text.toUpperCase();\n  if(t.includes('DARK SOULS DEPARTMENT')) return 'DARK SOULS DEPARTMENT';\n  if(t.includes('OLD SOULS')) return 'OLD SOULS';\n  if(t.includes('PRE-2016')) return 'PRE-2016 COMBAT DESIGN';\n  if(t.includes('NO AERIAL')) return 'NO AERIAL BUDGET';\n  if(t.includes('GROUNDED')) return 'GROUNDED';"
if old not in s: raise SystemExit('chaosEventName marker missing')
s=s.replace(old,new,1)

css=r'''
/* --- CHAOS REVEAL II: generated seal art + true motion --- */
.tc-chaos-event{position:relative;isolation:isolate;min-height:calc(100svh - 70px);padding:10px 14px 28px;overflow:hidden;background:radial-gradient(circle at 50% 28%,rgba(116,24,15,.17),transparent 38%),linear-gradient(180deg,#080706,#030303 70%,#070504);color:#e9dfcd;animation:chaosCurtain .65s ease-out both}
.tc-chaos-event:before{content:"";position:absolute;z-index:-2;inset:0;background-image:radial-gradient(circle at 50% 28%,rgba(204,61,32,.10),transparent 26%),repeating-radial-gradient(circle at 50% 28%,transparent 0 42px,rgba(172,119,55,.035) 43px 44px);animation:chaosRuneTurn 34s linear infinite}
.tc-chaos-event:after{content:"";position:absolute;z-index:-1;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.58),transparent 20%,transparent 80%,rgba(0,0,0,.58)),linear-gradient(180deg,transparent 55%,rgba(0,0,0,.52));pointer-events:none}
.tc-chaos-head{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;border-bottom:1px solid rgba(195,151,75,.2);padding:6px 4px 10px;font-family:Georgia,serif;color:#bfa36d;letter-spacing:.14em;text-transform:uppercase;font-size:10px}.tc-chaos-head strong{text-align:center;font-size:19px;font-weight:400;color:#e4d3af;letter-spacing:.18em}.tc-chaos-head .favor{text-align:right;font-size:8px;color:#c6a764}
.tc-chaos-crumb{font:9px/1.2 Georgia,serif;letter-spacing:.14em;text-transform:uppercase;color:#8e8069;padding:11px 5px 7px}.tc-chaos-crumb b{color:#b64a38;font-weight:400}
.tc-chaos-card{position:relative;margin:4px auto 0;max-width:610px;border:1px solid rgba(185,145,72,.34);padding:10px 14px 20px;background:linear-gradient(180deg,rgba(13,11,9,.5),rgba(5,5,5,.82));box-shadow:inset 0 0 38px rgba(0,0,0,.55),0 16px 50px rgba(0,0,0,.35)}
.tc-chaos-card:before,.tc-chaos-card:after{content:"";position:absolute;width:35px;height:35px;border-color:#8a6a37;opacity:.55}.tc-chaos-card:before{left:6px;top:6px;border-left:1px solid;border-top:1px solid}.tc-chaos-card:after{right:6px;bottom:6px;border-right:1px solid;border-bottom:1px solid}
.tc-chaos-art-wrap{position:relative;width:min(82vw,360px);aspect-ratio:1;margin:1px auto -9px;animation:chaosArtEnter 1.15s cubic-bezier(.16,.78,.2,1) both}.tc-chaos-art{width:100%;height:100%;display:block;object-fit:cover;border-radius:50%;mix-blend-mode:screen;filter:saturate(.82) contrast(1.05);mask-image:radial-gradient(circle,#000 55%,rgba(0,0,0,.8) 68%,transparent 73%)}
.tc-chaos-halo{position:absolute;inset:7%;border:1px solid rgba(203,77,43,.28);border-radius:50%;box-shadow:0 0 35px rgba(178,48,28,.2);animation:chaosHalo 8s linear infinite}.tc-chaos-halo:before{content:"";position:absolute;inset:10%;border:1px dashed rgba(207,160,73,.25);border-radius:50%;animation:chaosHalo 13s linear infinite reverse}
.tc-ember-field{position:absolute;inset:0;overflow:hidden;pointer-events:none}.tc-ember{position:absolute;bottom:-10%;width:2px;height:8px;border-radius:50%;background:#d35a2a;box-shadow:0 0 7px #db5725;opacity:0;animation:chaosEmber var(--dur) var(--delay) linear infinite;left:var(--x)}
.tc-chaos-title{font-family:Georgia,serif;font-size:clamp(30px,8.3vw,50px);font-weight:400;letter-spacing:.035em;text-align:center;text-transform:uppercase;color:#c8ac75;text-shadow:0 2px 18px #000;margin:0 0 13px;animation:chaosRevealText .7s .58s both}.tc-chaos-rule{height:1px;background:linear-gradient(90deg,transparent,#7a542d 20%,#ad4c2f 50%,#7a542d 80%,transparent);margin:0 auto 15px;width:80%}
.tc-chaos-label{text-align:center;color:#9d7745;font:8px/1.2 system-ui,sans-serif;letter-spacing:.24em;text-transform:uppercase;margin:7px 0}.tc-chaos-event-name{text-align:center;font:400 clamp(24px,7vw,38px)/1 Georgia,serif;letter-spacing:.055em;text-transform:uppercase;color:#eee7db;margin:8px auto 14px;max-width:540px;text-wrap:balance;animation:chaosRevealText .65s .78s both}
.tc-chaos-reading{position:relative;max-width:520px;margin:0 auto;padding:13px 15px 12px;border-top:1px solid rgba(164,120,62,.25);border-bottom:1px solid rgba(164,120,62,.18);background:linear-gradient(90deg,transparent,rgba(9,8,7,.8) 12%,rgba(9,8,7,.86) 88%,transparent);animation:chaosRevealText .65s .94s both}.tc-chaos-consequence{text-align:center;color:#ded3c0;font:400 16px/1.48 Georgia,serif;text-shadow:0 2px 9px #000}.tc-chaos-quip{text-align:center;color:#8f8799;font:italic 13px/1.4 Georgia,serif;margin:13px auto 15px;max-width:430px;animation:chaosRevealText .65s 1.08s both}
.tc-chaos-event .btn{display:block;width:min(520px,94%);margin:0 auto;min-height:53px;border:1px solid #8e5e31;color:#dfc28b;background:linear-gradient(180deg,rgba(104,27,18,.86),rgba(45,10,8,.96));font-family:Georgia,serif;font-size:12px;letter-spacing:.16em;text-transform:uppercase;clip-path:polygon(13px 0,calc(100% - 13px) 0,100% 13px,100% calc(100% - 13px),calc(100% - 13px) 100%,13px 100%,0 calc(100% - 13px),0 13px);box-shadow:inset 0 0 22px rgba(213,68,33,.11),0 6px 22px rgba(0,0,0,.3);animation:chaosRevealText .65s 1.2s both}
@keyframes chaosCurtain{from{opacity:0;background:#000}to{opacity:1}}@keyframes chaosRuneTurn{to{transform:rotate(360deg)}}@keyframes chaosHalo{to{transform:rotate(360deg)}}@keyframes chaosArtEnter{0%{opacity:0;transform:scale(.72);filter:blur(8px)}55%{opacity:1;transform:scale(1.035);filter:none}100%{transform:scale(1)}}@keyframes chaosRevealText{from{opacity:0;transform:translateY(11px);filter:blur(2px)}to{opacity:1;transform:none;filter:none}}@keyframes chaosEmber{0%{opacity:0;transform:translate3d(0,0,0) scale(.6)}12%{opacity:.7}100%{opacity:0;transform:translate3d(var(--drift),-105vh,0) scale(1.3)}}
@media(max-width:430px){.tc-chaos-event{padding-left:9px;padding-right:9px}.tc-chaos-card{padding-left:9px;padding-right:9px}.tc-chaos-art-wrap{width:min(84vw,330px)}.tc-chaos-consequence{font-size:15px}.tc-chaos-head strong{font-size:16px}}
@media(prefers-reduced-motion:reduce){.tc-chaos-event,.tc-chaos-art-wrap,.tc-chaos-title,.tc-chaos-event-name,.tc-chaos-reading,.tc-chaos-quip,.tc-chaos-event .btn,.tc-chaos-halo,.tc-chaos-halo:before,.tc-ember{animation:none!important}.tc-ember{display:none}}
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

new_render=r'''function renderChaosEvent(){
  const c=run.state.current;
  const eventName=chaosEventName(c.chaosConsequence||'');
  const reward=Number(c.chaosFavor??1);
  const embers=Array.from({length:28},(_,i)=>`<i class="tc-ember" style="--x:${(i*37)%101}%;--dur:${5+(i%7)*.7}s;--delay:${-(i%9)*.63}s;--drift:${((i%5)-2)*13}px"></i>`).join('');
  app.innerHTML=`<section class="tc-chaos-event">
    <div class="tc-ember-field">${embers}</div>
    <div class="tc-chaos-head"><span>✦</span><strong>Encounter</strong><span class="favor">${reward>0?`+${reward} Favor if survived`:'No Favor'}</span></div>
    <div class="tc-chaos-crumb">Site of Grace &nbsp;›&nbsp; <b>Encounter</b></div>
    <div class="tc-chaos-card">
      <div class="tc-chaos-art-wrap"><img class="tc-chaos-art" src="./assets/chaos-seal.webp" alt="Cracking Covenant seal"><div class="tc-chaos-halo"></div></div>
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

for required in ['TC_OLD_SOULS_RITES','chaos-seal.webp','Endure Decree','DARK SOULS DEPARTMENT','tc-ember-field']:
    if required not in s: raise SystemExit('Chaos redesign invariant missing: '+required)
p.write_text(s)
