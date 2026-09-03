from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

css = r'''
/* --- Information architecture pass: navigate between information, don't make it smaller --- */
.tc-encounter-shell{
  height:calc(100svh - 70px);
  min-height:0;
  overflow:hidden;
  display:flex;
  flex-direction:column;
  padding-bottom:0!important;
}
.tc-encounter-shell .tc-topline{flex:0 0 auto;margin-bottom:7px}
.tc-encounter-sticky{
  flex:0 0 auto;display:grid;grid-template-columns:minmax(0,1fr);gap:2px;padding:8px 10px 9px;margin:0 0 7px;
  border-top:1px solid var(--line-soft);border-bottom:1px solid var(--line-soft);background:rgba(9,8,6,.82)
}
.tc-encounter-sticky strong{font:400 clamp(19px,5.5vw,25px)/1.05 Georgia,serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tc-encounter-sticky span{color:#d9877b;font:800 9px/1.25 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.06em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tc-encounter-tabs{flex:0 0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:4px;margin-bottom:6px}
.tc-encounter-tabs button{min-height:37px;border:0;border-bottom:1px solid var(--line);background:transparent;color:var(--ash);font:850 9.5px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.055em}
.tc-encounter-tabs button.active{color:var(--gold-bright);border-bottom-color:var(--gold-bright)}
.tc-encounter-track{flex:1 1 auto;min-height:0;display:flex;width:100%;overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;scroll-behavior:smooth;scrollbar-width:none;overscroll-behavior-x:contain}
.tc-encounter-track::-webkit-scrollbar{display:none}
.tc-encounter-panel{flex:0 0 100%;min-width:100%;min-height:0;height:100%;overflow-y:auto;overscroll-behavior-y:contain;scroll-snap-align:start;padding:2px 2px 18px}
.tc-panel-heading{text-align:center;color:var(--gold);font:850 9px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.12em;margin:7px 0 9px}
.tc-encounter-actions{flex:0 0 auto;display:grid;grid-template-columns:minmax(0,1fr) minmax(112px,.34fr);gap:7px;padding:7px 0 8px;background:linear-gradient(180deg,rgba(8,8,6,.84),var(--bg) 25%);border-top:1px solid var(--line-soft)}
.tc-encounter-actions #complete{margin:0;min-height:48px}.tc-encounter-actions .tc-actions-3{display:block;margin:0}.tc-encounter-actions .tc-actions-3 .btn{height:100%;min-height:48px}.tc-encounter-actions #appealConfirm{grid-column:1/-1}
.tc-encounter-panel .tc-boss-art{min-height:145px;max-height:26svh}.tc-encounter-panel .tc-brief-head{padding-top:4px}.tc-encounter-panel .tc-loadouts{margin-bottom:8px}.tc-encounter-panel .tc-feature{margin-top:4px}.tc-encounter-panel .tc-earned-refreshes{margin-top:10px}
.tc-encounter-hint{flex:0 0 auto;text-align:center;margin:-2px 0 5px;color:#716858;font:italic 10px/1.2 Georgia,serif}
@media(max-height:720px){.tc-encounter-sticky{padding-top:6px;padding-bottom:6px}.tc-encounter-tabs button{min-height:32px}.tc-encounter-panel .tc-boss-art{min-height:110px;max-height:20svh}.tc-encounter-actions{padding-top:5px;padding-bottom:5px}}
@media(min-width:700px){.tc-encounter-shell{height:calc(100svh - 70px)}.tc-encounter-panel{padding-left:24px;padding-right:24px}}

.tc-comp-region{margin:18px 0 24px}.tc-comp-region-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;padding:0 4px 8px;border-bottom:1px solid rgba(198,161,90,.28)}
.tc-comp-region-head strong{font:400 24px/1.05 Georgia,serif;color:var(--ink)}.tc-comp-region-head span{font:850 8px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em;color:var(--gold)}
.tc-comp-region-cards{display:grid;gap:9px;margin-top:9px}.tc-comp-card{position:relative;isolation:isolate;cursor:pointer}.tc-comp-card>summary{position:relative;z-index:2;min-height:104px;padding:17px 14px!important}
.tc-comp-card>summary:before{content:"";position:absolute;z-index:-2;inset:0;background-image:var(--tc-comp-art);background-size:cover;background-position:center;opacity:.27;filter:saturate(.72) contrast(1.05)}
.tc-comp-card>summary:after{content:"";position:absolute;z-index:-1;inset:0;background:linear-gradient(90deg,rgba(7,7,5,.97) 0%,rgba(8,7,5,.85) 58%,rgba(8,7,5,.46) 100%)}
.tc-comp-card>.tc-comp-body,.tc-comp-card>.tc-comp-legacy{display:none!important}.tc-comp-card .tc-comp-boss{font-size:clamp(24px,7vw,31px)!important}.tc-comp-card .tc-comp-mark{align-self:start;margin-top:2px}
.tc-comp-sheet-overlay{position:fixed;z-index:110;inset:0;background:#080806;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom);animation:tcCompIn .22s ease-out}@keyframes tcCompIn{from{opacity:.2;transform:translateX(12px)}to{opacity:1;transform:none}}
.tc-comp-sheet{width:min(720px,100%);height:100%;margin:auto;display:flex;flex-direction:column;padding:12px 14px 18px}.tc-comp-sheet-top{flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:3px 0 10px;border-bottom:1px solid var(--line-soft)}
.tc-comp-sheet-close{border:0;background:transparent;color:var(--gold-bright);padding:8px 2px;font:850 10px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em}.tc-comp-sheet-index{font:850 8px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.11em;color:var(--ash)}
.tc-comp-sheet-scroll{flex:1 1 auto;min-height:0;overflow-y:auto;padding:18px 2px 30px;overscroll-behavior:contain}.tc-comp-sheet-region{color:var(--gold);font:850 9px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.13em}
.tc-comp-sheet h2{font:400 clamp(34px,10vw,48px)/.96 Georgia,serif;margin:8px 0 5px;text-wrap:balance}.tc-comp-sheet-flavor{font:italic 12px/1.4 Georgia,serif;color:var(--ash);margin:0 0 18px}.tc-comp-sheet .tc-comp-body,.tc-comp-sheet .tc-comp-legacy{display:block!important;border:1px solid var(--line-soft);padding:13px;background:rgba(12,11,8,.62)}

.tc-corporate-screen{min-height:calc(100svh - env(safe-area-inset-top));max-width:620px;margin:auto;padding:24px 16px calc(24px + env(safe-area-inset-bottom));display:flex;flex-direction:column;justify-content:center;text-align:center}
.tc-corporate-letter{position:relative;border:1px solid #685d45;background:linear-gradient(165deg,#181610,#0d0c09);padding:27px 20px 21px;box-shadow:0 22px 70px rgba(0,0,0,.44)}
.tc-corporate-stamp{width:70px;height:70px;margin:0 auto 15px;border:2px solid #9b5b4f;border-radius:50%;display:grid;place-items:center;color:#c87567;transform:rotate(-8deg);font:850 10px/1.05 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em}
.tc-corporate-overline{font:900 10px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.18em;color:var(--red)}.tc-corporate-screen h1{font-size:clamp(34px,10vw,49px);margin:11px auto 13px;line-height:.96}
.tc-corporate-copy{font-size:16px;line-height:1.5;color:#d5ccba;max-width:480px;margin:0 auto 18px}.tc-corporate-meta{margin:14px 0;padding:12px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);color:var(--ash);font-size:12px;line-height:1.4}.tc-corporate-screen .btn{margin-top:14px}.tc-corporate-foot{font:italic 11px/1.4 Georgia,serif;color:#7f7666;margin-top:10px}.tc-forge-notice.tc-corporate-pending{cursor:default}
'''

if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

js = r'''
/* --- Late information-architecture layer. Existing renderers still create and bind the controls. --- */
let tcEncounterPanelIndex=0;
let tcEncounterPanelId=null;
function tcMakeEncounterPanel(label,nodes){const panel=document.createElement('section');panel.className='tc-encounter-panel';panel.dataset.panel=label.toLowerCase();const heading=document.createElement('div');heading.className='tc-panel-heading';heading.textContent=label;panel.appendChild(heading);nodes.filter(Boolean).forEach(node=>panel.appendChild(node));return panel;}
function tcEnhanceEncounterPanels(){
  const screen=app.querySelector('.tc-screen');const complete=screen?.querySelector('#complete');if(!screen||!complete||screen.classList.contains('tc-encounter-shell'))return;
  const c=run.state?.current;if(!c)return;if(tcEncounterPanelId!==c.id){tcEncounterPanelId=c.id;tcEncounterPanelIndex=0;}screen.classList.add('tc-encounter-shell');
  const top=screen.querySelector('.tc-topline'),brief=screen.querySelector('.tc-brief-head'),art=screen.querySelector('.tc-boss-art'),defer=screen.querySelector('.tc-capstone-defer,.tc-capstone-deferral,.tc-capstone-defer-card'),debt=screen.querySelector('.tc-feature.debt');
  const loadouts=screen.querySelector('.tc-loadouts'),weaponsHeading=loadouts?.previousElementSibling?.classList?.contains('tc-kicker')?loadouts.previousElementSibling:null,penalties=screen.querySelector('.tc-penalty-summary'),chaos=screen.querySelector('.tc-feature.chaos'),rite=screen.querySelector('.tc-feature.rite'),earned=screen.querySelector('.tc-earned-refreshes'),actions3=screen.querySelector('.tc-actions-3'),appealConfirm=screen.querySelector('#appealConfirm');
  const sticky=document.createElement('div');sticky.className='tc-encounter-sticky';sticky.innerHTML=`<strong>${h(c.target?.name||'Current Encounter')}</strong><span>CHAOS · ${h(personalizePlayers(c.chaosTrigger||'No active trigger',run.state))}</span>`;top?.after(sticky);
  const tabs=document.createElement('div');tabs.className='tc-encounter-tabs';['Boss','Weapons','Chaos','Rite'].forEach((name,i)=>{const b=document.createElement('button');b.type='button';b.textContent=name;b.dataset.tcPanel=String(i);if(i===tcEncounterPanelIndex)b.classList.add('active');tabs.appendChild(b);});sticky.after(tabs);
  const track=document.createElement('div');track.className='tc-encounter-track';const overviewNodes=[brief,art,defer,debt],weaponNodes=[weaponsHeading,loadouts,penalties],chaosNodes=[chaos],riteNodes=[rite,earned];
  const claimed=new Set([top,sticky,tabs,brief,art,defer,debt,weaponsHeading,loadouts,penalties,chaos,rite,earned,complete,actions3,appealConfirm].filter(Boolean));[...screen.children].forEach(node=>{if(!claimed.has(node)&&node!==track)riteNodes.push(node);});
  track.append(tcMakeEncounterPanel('Target',overviewNodes),tcMakeEncounterPanel('Assigned Weapons',weaponNodes),tcMakeEncounterPanel('Chaos Decree',chaosNodes),tcMakeEncounterPanel('Rite & Amendments',riteNodes));tabs.after(track);
  const hint=document.createElement('div');hint.className='tc-encounter-hint';hint.textContent='Swipe between briefing panels';track.after(hint);
  const bar=document.createElement('div');bar.className='tc-encounter-actions';bar.appendChild(complete);if(actions3)bar.appendChild(actions3);if(appealConfirm)bar.appendChild(appealConfirm);hint.after(bar);
  const go=i=>{tcEncounterPanelIndex=Math.max(0,Math.min(3,i));track.scrollTo({left:tcEncounterPanelIndex*track.clientWidth,behavior:'smooth'});tabs.querySelectorAll('button').forEach((b,j)=>b.classList.toggle('active',j===tcEncounterPanelIndex));};tabs.querySelectorAll('button').forEach((b,i)=>b.addEventListener('click',()=>go(i)));
  let scrollTimer=null;track.addEventListener('scroll',()=>{clearTimeout(scrollTimer);scrollTimer=setTimeout(()=>{const i=Math.round(track.scrollLeft/Math.max(1,track.clientWidth));tcEncounterPanelIndex=Math.max(0,Math.min(3,i));tabs.querySelectorAll('button').forEach((b,j)=>b.classList.toggle('active',j===tcEncounterPanelIndex));},70);},{passive:true});requestAnimationFrame(()=>{track.scrollLeft=tcEncounterPanelIndex*track.clientWidth;});
}
const tcRenderEncounterBeforeIA=renderEncounter;renderEncounter=function(){tcRenderEncounterBeforeIA();tcEnhanceEncounterPanels();};

function tcMandatoryContractEligible(state){if(!state?.current||!pendingRevealId||state.current.id!==pendingRevealId)return false;const sm=smithingData(state);return !sm.activeContract&&sm.favor>=3&&availableBellBearings(state).length>0;}
function renderCorporateContractNotice(){
  const state=run.state,sm=smithingData(state),available=availableBellBearings(state),preview=available[0];
  app.innerHTML=`<section class="tc-corporate-screen"><div class="tc-corporate-letter"><div class="tc-corporate-stamp">Action<br>Required</div><div class="tc-corporate-overline">Notice From Upper Management</div><h1>Corporate Has Forwarded A Matter</h1><div class="tc-corporate-copy">Your recent performance has attracted administrative attention. A Bell Bearing Contract is now mandatory before normal encounter scheduling may resume.</div><div class="tc-corporate-meta"><strong>${sm.favor} Smithing Favor on file</strong><br>${preview?`${h(preview.region)} procurement is currently actionable.`:'An eligible procurement matter has been identified.'}</div><button id="tcReviewMandatoryContract" class="btn gold">Review Mandatory Contract</button><div class="tc-corporate-foot">Hewg has been CC’d. This meeting could not have been an email.</div></div></section>`;
  document.querySelector('#tcReviewMandatoryContract')?.addEventListener('click',async()=>{const btn=document.querySelector('#tcReviewMandatoryContract');if(btn)btn.disabled=true;const next=commissionSmithingContract(run.state);if(!next){renderRun();return;}await commit(next,{successToast:'Upper Management has assigned a Bell Bearing Contract.'});renderSmithingContract();});
}
const tcRenderRunBeforeIA=renderRun;renderRun=function(){const state=run.state;if(!pendingRewardReveal?.rewards?.length&&!postBattleReport&&tcMandatoryContractEligible(state))return renderCorporateContractNotice();return tcRenderRunBeforeIA();};
const tcSmithingHubBeforeIA=smithingHubMarkup;smithingHubMarkup=function(state){const sm=smithingData(state);if(!sm.activeContract&&sm.favor>=3&&availableBellBearings(state).length){return `<div class="tc-forge-notice quiet tc-corporate-pending"><div class="tc-forge-glyph">◈</div><div><div class="tc-kicker ember">upper management review pending</div><div class="tc-forge-title">${sm.favor} Smithing Favor Has Been Noticed</div><div class="tc-muted">Corporate will forward an actionable Bell Bearing matter at the next safe transition.</div></div><span class="tc-forge-arrow">…</span></div>`;}return tcSmithingHubBeforeIA(state);};

function tcCompendiumFlavor(entry,index){const lines=['Filed under: avoidable administrative violence.','The Covenant remembers. Unfortunately.','Armaments, rites, and poor judgment preserved for audit.','A complete record of something that probably seemed sensible at the time.','Recorded for posterity and future liability.'];return lines[index%lines.length];}
function tcOpenCompendiumEntry(entry,index,card){document.querySelector('#tcCompendiumOverlay')?.remove();const source=card?.querySelector('.tc-comp-body,.tc-comp-legacy');const overlay=document.createElement('div');overlay.id='tcCompendiumOverlay';overlay.className='tc-comp-sheet-overlay';overlay.innerHTML=`<div class="tc-comp-sheet"><div class="tc-comp-sheet-top"><button class="tc-comp-sheet-close" type="button">‹ Compendium</button><span class="tc-comp-sheet-index">Entry ${String(index+1).padStart(2,'0')}</span></div><div class="tc-comp-sheet-scroll"><div class="tc-comp-sheet-region">${h(entry.region||'Unknown Region')}</div><h2>${h(entry.name||'Unknown Foe')}</h2><div class="tc-comp-sheet-flavor">${h(tcCompendiumFlavor(entry,index))}</div>${source?source.outerHTML:`<div class="tc-comp-legacy">The Covenant retains only a partial record of this encounter.</div>`}</div></div>`;document.body.appendChild(overlay);overlay.querySelector('.tc-comp-sheet-close')?.addEventListener('click',()=>overlay.remove());}
function tcEnhanceCompendium(){if(ledgerView!=='compendium')return;const list=app.querySelector('.tc-comp-list');if(!list||list.dataset.chronicle==='1')return;list.dataset.chronicle='1';const entries=Array.isArray(run.state.history)?run.state.history:[],cards=[...list.querySelectorAll('.tc-comp-card')];if(!cards.length)return;list.innerHTML='';const groups=new Map();cards.forEach((card,i)=>{const entry=entries[i]||{},region=entry.region||'Earlier Records';if(!groups.has(region))groups.set(region,[]);groups.get(region).push({card,entry,index:i});});groups.forEach((records,region)=>{const chapter=document.createElement('section');chapter.className='tc-comp-region';chapter.innerHTML=`<div class="tc-comp-region-head"><strong>${h(region)}</strong><span>${records.length} ${records.length===1?'record':'records'}</span></div><div class="tc-comp-region-cards"></div>`;const stack=chapter.querySelector('.tc-comp-region-cards');records.forEach(({card,entry,index})=>{try{card.style.setProperty('--tc-comp-art',`linear-gradient(rgba(0,0,0,.2),rgba(0,0,0,.2)), url("${actualRegionImage(entry.region||run.state.region)}")`);}catch{}card.open=false;const summary=card.querySelector('summary');summary?.addEventListener('click',e=>{e.preventDefault();card.open=false;tcOpenCompendiumEntry(entry,index,card);});stack.appendChild(card);});list.appendChild(chapter);});}
const tcRenderLedgerBeforeIA=renderLedger;renderLedger=function(){tcRenderLedgerBeforeIA();tcEnhanceCompendium();};
const tcIaExtra=document.createElement('style');tcIaExtra.textContent='.tc-battle-report{height:calc(100svh - 10px);min-height:0!important;overflow-y:auto;overscroll-behavior:contain}';document.head.appendChild(tcIaExtra);
'''

idx = s.rfind('</script>')
if idx < 0:
    raise SystemExit('script end marker missing')
s = s[:idx] + js + '\n' + s[idx:]

for needle in ['Information architecture pass','tcEnhanceEncounterPanels','renderCorporateContractNotice','tcMandatoryContractEligible','tcEnhanceCompendium','tc-comp-sheet-overlay']:
    if needle not in s:
        raise SystemExit('information architecture invariant missing: '+needle)

p.write_text(s)
