from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

state_marker = "const acknowledgedChaos = new Set();"
if state_marker not in s:
    raise SystemExit('acknowledgedChaos marker missing')
s = s.replace(state_marker, state_marker + "\nlet postBattleReport = null;", 1)

pat = r'\n\s*<div class="tc-forge-claims">.*?</button></div>\n(\s*<button id="complete")'
s, n = re.subn(pat, r'\n\1', s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('live forge-claim block missing')

old = """  document.querySelector('#complete')?.addEventListener('click',async()=>{
    const next=completeEncounter(state,playerName());
    if(!next.regionComplete&&!next.runComplete&&next.current){pendingRevealId=next.current.id;uiScreen='encounter';}
    await commit(next);
  });"""
new = """  document.querySelector('#complete')?.addEventListener('click',()=>{
    postBattleReport={encounterId:c.id,rite:null,chaos:null};
    renderPostBattleReport();
  });"""
if old not in s:
    raise SystemExit('victory handler target missing')
s = s.replace(old, new, 1)

run_marker = "function renderRun() {\n  const state=run.state;"
if run_marker not in s:
    raise SystemExit('renderRun marker missing')
s = s.replace(run_marker, run_marker + "\n  if(postBattleReport?.encounterId===state.current?.id) return renderPostBattleReport();", 1)

functions = r'''
function postBattleChoice(kind,value){
  if(!postBattleReport || postBattleReport.encounterId!==run.state.current?.id) return;
  postBattleReport[kind]=Boolean(value);
  renderPostBattleReport();
}
function postBattleChoiceMarkup(kind,label,detail,reward,available=true){
  if(!available){
    return `<div class="tc-report-row muted"><div><div class="tc-kicker">${label}</div><div class="tc-report-detail">${detail}</div></div><span class="tc-report-stamp">not triggered</span></div>`;
  }
  if(reward<=0){
    return `<div class="tc-report-row muted"><div><div class="tc-kicker">${label}</div><div class="tc-report-detail">${detail}</div></div><span class="tc-report-stamp">0 favor</span></div>`;
  }
  const current=postBattleReport?.[kind];
  return `<div class="tc-report-row"><div class="tc-report-copy"><div class="tc-kicker">${label} · +${reward} Favor</div><div class="tc-report-detail">${detail}</div></div><div class="tc-report-choices">
    <button type="button" data-report-kind="${kind}" data-report-value="1" class="${current===true?'active yes':''}">Yes</button>
    <button type="button" data-report-kind="${kind}" data-report-value="0" class="${current===false?'active no':''}">No</button>
  </div></div>`;
}
function renderPostBattleReport(){
  const state=run.state,c=state.current;
  if(!c){postBattleReport=null;return renderRun();}
  if(!postBattleReport || postBattleReport.encounterId!==c.id) postBattleReport={encounterId:c.id,rite:null,chaos:null};
  const riteReward=Number(c.weirdness?.favor??1);
  const chaosReward=Number(c.chaosFavor??1);
  const riteReady=riteReward<=0 || postBattleReport.rite!==null;
  const chaosAvailable=Boolean(c.chaosTriggered);
  const chaosReady=!chaosAvailable || chaosReward<=0 || postBattleReport.chaos!==null;
  const gained=(postBattleReport.rite===true?Math.max(0,riteReward):0)+(postBattleReport.chaos===true?Math.max(0,chaosReward):0);
  app.innerHTML=`<section class="tc-battle-report">
    <div class="tc-report-kicker">Encounter Complete</div>
    <div class="tc-report-victory">VICTORY</div>
    <div class="tc-report-boss">${h(c.target?.name||'Enemy Felled')}</div>
    <div class="tc-report-rule"></div>
    ${postBattleChoiceMarkup('rite','Odd Rite',`${h(c.weirdness?.name||'No Rite')} · ${h(c.weirdness?.text||'')}`,riteReward,true)}
    ${postBattleChoiceMarkup('chaos','Chaos',chaosAvailable?`${h(chaosEventName(c.chaosConsequence||''))} · ${h(personalizePlayers(c.chaosConsequence||'',state))}`:'The Chaos seal never broke during this encounter.',chaosReward,chaosAvailable)}
    <div class="tc-report-total"><span>Smithing Favor earned</span><strong>+${gained}</strong></div>
    <button id="finishBattleReport" class="btn gold" ${riteReady&&chaosReady?'':'disabled'}>${c.target?.exit?'Record Victory · Continue':'Record Victory · Roll Next Encounter'}</button>
    <div class="tc-report-note">${riteReady&&chaosReady?'The ledger updates when you submit this report.':'Answer the eligible honor-system checks first.'}</div>
  </section>`;
  document.querySelectorAll('[data-report-kind]').forEach(btn=>btn.addEventListener('click',()=>postBattleChoice(btn.dataset.reportKind,btn.dataset.reportValue==='1')));
  document.querySelector('#finishBattleReport')?.addEventListener('click',finalizePostBattleReport);
}
async function finalizePostBattleReport(){
  const state=run.state,c=state.current;
  if(!c || !postBattleReport || postBattleReport.encounterId!==c.id) return;
  const nextState=smithingCopy(state);
  const nc=nextState.current;
  let gained=0;
  const riteReward=Number(nc.weirdness?.favor??1);
  if(postBattleReport.rite===true && riteReward>0 && !nc.smithingRiteFavor){
    nc.smithingRiteFavor=true;
    nextState.smithing.favor+=riteReward;
    gained+=riteReward;
  }
  const chaosReward=Number(nc.chaosFavor??1);
  if(postBattleReport.chaos===true && nc.chaosTriggered && chaosReward>0 && !nc.smithingChaosFavor){
    nc.smithingChaosFavor=true;
    nextState.smithing.favor+=chaosReward;
    gained+=chaosReward;
  }
  const completed=completeEncounter(nextState,playerName());
  postBattleReport=null;
  if(!completed.regionComplete&&!completed.runComplete&&completed.current){
    pendingRevealId=completed.current.id;
    uiScreen='encounter';
  }
  await commit(completed,{successToast:gained?`Post-battle report filed · +${gained} Smithing Favor`:'Post-battle report filed.'});
}
'''
marker = "function showAppealMenu(){"
if marker not in s:
    raise SystemExit('showAppealMenu marker missing')
s = s.replace(marker, functions + "\n" + marker, 1)

css = r'''
/* --- Post-battle report: Favor bookkeeping belongs after the fight --- */
.tc-battle-report{min-height:calc(100svh - 24px);max-width:620px;margin:0 auto;padding:clamp(22px,5vh,48px) 14px calc(24px + env(safe-area-inset-bottom));display:flex;flex-direction:column;justify-content:center;text-align:center}
.tc-report-kicker{font:800 8px/1 system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);margin-bottom:9px}
.tc-report-victory{font:400 clamp(34px,10vw,50px)/.9 Georgia,serif;letter-spacing:.08em;color:var(--gold-bright);text-shadow:0 0 28px rgba(224,193,123,.14)}
.tc-report-boss{font:400 clamp(22px,6.7vw,32px)/1.05 Georgia,serif;color:var(--ink);margin:10px auto 13px;text-wrap:balance}
.tc-report-rule{height:1px;width:70%;margin:0 auto 12px;background:linear-gradient(90deg,transparent,var(--line),transparent)}
.tc-report-row{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:12px;text-align:left;padding:12px 4px;border-bottom:1px solid var(--line-soft)}
.tc-report-row.muted{opacity:.66}.tc-report-copy{min-width:0}.tc-report-detail{font:11px/1.35 Georgia,serif;color:#c9c0af;margin-top:5px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.tc-report-choices{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line);min-width:116px}.tc-report-choices button{min-height:38px;padding:0 10px;border:0;background:transparent;color:var(--ash);font:800 8px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em}.tc-report-choices button+button{border-left:1px solid var(--line)}
.tc-report-choices button.active.yes{background:rgba(198,161,90,.18);color:var(--gold-bright)}.tc-report-choices button.active.no{background:rgba(201,102,90,.12);color:#d58b80}
.tc-report-stamp{font:800 8px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em;color:var(--ash)}
.tc-report-total{display:flex;align-items:center;justify-content:space-between;gap:15px;margin:15px 0 10px;padding:10px 4px;border-top:1px solid rgba(198,161,90,.22);color:var(--ash);font:800 8px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.09em}.tc-report-total strong{font:400 27px/1 Georgia,serif;color:var(--gold-bright)}
.tc-battle-report .btn{min-height:50px}.tc-report-note{font:10px/1.35 Georgia,serif;font-style:italic;color:var(--ash);margin-top:8px}
@media(max-height:700px){.tc-battle-report{padding-top:14px;padding-bottom:14px}.tc-report-row{padding:9px 3px}.tc-report-detail{-webkit-line-clamp:2}.tc-report-boss{margin:7px auto 9px}.tc-report-total{margin:10px 0 8px}}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

for needle in ['function renderPostBattleReport()','function finalizePostBattleReport()','postBattleReport={encounterId:c.id,rite:null,chaos:null}','Smithing Favor earned']:
    if needle not in s:
        raise SystemExit('post-battle invariant missing: '+needle)
if 'tc-forge-claims' in s:
    raise SystemExit('live encounter Favor controls still present')

p.write_text(s)
