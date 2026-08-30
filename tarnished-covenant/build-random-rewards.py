from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Preserve reward inventory through every smithingCopy().
old = """    masterworks: Array.isArray(raw.masterworks) ? raw.masterworks : [],
    masterworkCredits: Number(raw.masterworkCredits || 0)
  };"""
new = """    masterworks: Array.isArray(raw.masterworks) ? raw.masterworks : [],
    masterworkCredits: Number(raw.masterworkCredits || 0),
    appealWaivers: Number(raw.appealWaivers || 0),
    chaosRefreshes: Number(raw.chaosRefreshes || 0),
    riteRefreshes: Number(raw.riteRefreshes || 0)
  };"""
if old not in s:
    raise SystemExit('smithingData inventory target missing')
s = s.replace(old, new, 1)

helpers = r'''
function drawCovenantReward(state){
  const sm=state.smithing || (state.smithing=smithingData(state));
  const roll=Math.random();
  if(roll<0.40){sm.favor+=1;return {kind:'favor',label:'+1 Smithing Favor'};}
  if(roll<0.45){sm.favor+=2;return {kind:'favor',label:'+2 Smithing Favor'};}
  if(roll<0.65){sm.chaosRefreshes+=1;return {kind:'chaos',label:'Chaos Refresh'};}
  if(roll<0.85){sm.riteRefreshes+=1;return {kind:'rite',label:'Rite Refresh'};}
  sm.appealWaivers+=1;return {kind:'appeal',label:'Appeal Waiver'};
}
function covenantBoonMarkup(state){
  const sm=smithingData(state);
  return `<div class="tc-boon-ledger"><div class="tc-kicker ember">covenant boons</div><div class="tc-boon-grid">
    <div><strong>${sm.appealWaivers}</strong><span>Appeal Waiver${sm.appealWaivers===1?'':'s'}</span></div>
    <div><strong>${sm.chaosRefreshes}</strong><span>Chaos Refresh${sm.chaosRefreshes===1?'':'es'}</span></div>
    <div><strong>${sm.riteRefreshes}</strong><span>Rite Refresh${sm.riteRefreshes===1?'':'es'}</span></div>
  </div><div class="tc-muted">Waivers make the next weapon appeal penalty-free. Refreshes are the only way to reroll a current Rite or unopened Chaos decree.</div></div>`;
}
function tcEncounterBoons(state){
  const sm=smithingData(state),c=state.current;if(!c)return '';
  const buttons=[];
  if(sm.chaosRefreshes>0&&!c.chaosTriggered)buttons.push(`<button type="button" data-use-boon="chaos" class="btn ghost small">Chaos Refresh · ${sm.chaosRefreshes}</button>`);
  if(sm.riteRefreshes>0)buttons.push(`<button type="button" data-use-boon="rite" class="btn ghost small">Rite Refresh · ${sm.riteRefreshes}</button>`);
  return buttons.length?`<div class="tc-earned-refreshes"><div class="tc-kicker">earned refreshes</div><div class="tc-earned-refresh-grid">${buttons.join('')}</div></div>`:'';
}
async function useCovenantBoon(kind){
  if(!run?.state?.current)return;
  const sm=smithingData(run.state),key=kind==='chaos'?'chaosRefreshes':'riteRefreshes';
  if(Number(sm[key]||0)<1)return setToast('No refresh token available.');
  if(kind==='chaos'&&run.state.current.chaosTriggered)return setToast('Chaos has already broken loose. Too late to refresh it.');
  let staged=smithingCopy(run.state);staged.smithing[key]-=1;
  staged=kind==='chaos'?rerollChaos(staged,playerName()):rerollWeirdness(staged,playerName());
  await commit(staged,{successToast:`${kind==='chaos'?'Chaos':'Rite'} refreshed. Token spent.`});
}
'''
marker = 'function smithingFavorMarkup(state){'
if marker not in s:
    raise SystemExit('smithing helper marker missing')
s = s.replace(marker, helpers + '\n' + marker, 1)

# Smithing Ledger now shows the non-currency rewards too.
needle = '${smithingFavorMarkup(state)}\n    ${contract?'
if needle not in s:
    raise SystemExit('smithing ledger favor marker missing')
s = s.replace(needle, '${smithingFavorMarkup(state)}\n    ${covenantBoonMarkup(state)}\n    ${contract?', 1)

# Favor is no longer guaranteed by every challenge.
s = s.replace('earned by honoring rites and enduring Chaos', 'one possible reward from honoring rites and enduring Chaos', 1)

# Remove unlimited/free fishing buttons and their direct handlers anywhere they survived.
s = re.sub(r'\s*<button[^>]*id="rerollChaos"[^>]*>.*?</button>', '', s, flags=re.S)
s = re.sub(r'\s*<button[^>]*id="rerollWeird"[^>]*>.*?</button>', '', s, flags=re.S)
s = re.sub(r"\s*document\.querySelector\('#rerollChaos'\)[^;]*;", '', s)
s = re.sub(r"\s*document\.querySelector\('#rerollWeird'\)[^;]*;", '', s)

# Put earned refreshes immediately before the Victory control on the active Encounter screen.
complete_marker = '<button id="complete"'
if complete_marker not in s:
    raise SystemExit('encounter complete button marker missing')
s = s.replace(complete_marker, '${tcEncounterBoons(state)}\n      <button id="complete"', 1)

# Appeal Waivers automatically make the next weapon appeal free.
old = """  current.penances.push(makePenance(current.target.name));
  const names = Array.isArray(next.playerNames) && next.playerNames.length >= 2 ? next.playerNames : ['Tarnished One','Tarnished Two'];"""
new = """  const sm = smithingData(next);
  const waived = sm.appealWaivers > 0;
  if (waived) { next.smithing = sm; next.smithing.appealWaivers -= 1; }
  else current.penances.push(makePenance(current.target.name));
  const names = Array.isArray(next.playerNames) && next.playerNames.length >= 2 ? next.playerNames : ['Tarnished One','Tarnished Two'];"""
if old not in s:
    raise SystemExit('weapon appeal penalty target missing')
s = s.replace(old, new, 1)
s = s.replace("next.lastAction = `${actor} changed ${label}; a penalty was added.`;", "next.lastAction = waived ? `${actor} changed ${label}; an Appeal Waiver covered the penalty.` : `${actor} changed ${label}; a penalty was added.`;", 1)

# Replace the post-battle report with random reward draws instead of deterministic Favor.
start = s.find('function renderPostBattleReport(){')
end = s.find('\nfunction showAppealMenu(){', start)
if start < 0 or end < 0:
    raise SystemExit('post-battle function block missing')
replacement = r'''function renderPostBattleReport(){
  const state=run.state,c=state.current;
  if(!c){postBattleReport=null;return renderRun();}
  if(!postBattleReport || postBattleReport.encounterId!==c.id) postBattleReport={encounterId:c.id,rite:null,chaos:null};
  const riteDraws=Number(c.weirdness?.favor??1);
  const chaosDraws=Number(c.chaosFavor??1);
  const riteReady=riteDraws<=0 || postBattleReport.rite!==null;
  const chaosAvailable=Boolean(c.chaosTriggered);
  const chaosReady=!chaosAvailable || chaosDraws<=0 || postBattleReport.chaos!==null;
  const draws=(postBattleReport.rite===true?Math.max(0,riteDraws):0)+(postBattleReport.chaos===true?Math.max(0,chaosDraws):0);
  app.innerHTML=`<section class="tc-battle-report">
    <div class="tc-report-kicker">Encounter Complete</div>
    <div class="tc-report-victory">VICTORY</div>
    <div class="tc-report-boss">${h(c.target?.name||'Enemy Felled')}</div>
    <div class="tc-report-rule"></div>
    ${postBattleChoiceMarkup('rite','Odd Rite',`${h(c.weirdness?.name||'No Rite')} · ${h(c.weirdness?.text||'')}`,riteDraws,true)}
    ${postBattleChoiceMarkup('chaos','Chaos',chaosAvailable?`${h(chaosEventName(c.chaosConsequence||''))} · ${h(personalizePlayers(c.chaosConsequence||'',state))}`:'The Chaos seal never broke during this encounter.',chaosDraws,chaosAvailable)}
    <div class="tc-report-total"><span>Covenant reward draws</span><strong>${draws}</strong></div>
    <button id="finishBattleReport" class="btn gold" ${riteReady&&chaosReady?'':'disabled'}>${c.target?.exit?'Record Victory · Draw Rewards':'Record Victory · Draw Rewards & Roll Next'}</button>
    <div class="tc-report-note">${riteReady&&chaosReady?'Each earned draw can become Smithing Favor, a Refresh, or a rare Appeal Waiver.':'Answer the eligible honor-system checks first.'}</div>
  </section>`;
  document.querySelectorAll('[data-report-kind]').forEach(btn=>btn.addEventListener('click',()=>postBattleChoice(btn.dataset.reportKind,btn.dataset.reportValue==='1')));
  document.querySelector('#finishBattleReport')?.addEventListener('click',finalizePostBattleReport);
}
async function finalizePostBattleReport(){
  const state=run.state,c=state.current;
  if(!c || !postBattleReport || postBattleReport.encounterId!==c.id) return;
  const nextState=smithingCopy(state);
  const nc=nextState.current;
  let draws=0;
  const riteDraws=Number(nc.weirdness?.favor??1);
  if(postBattleReport.rite===true && riteDraws>0 && !nc.smithingRiteFavor){
    nc.smithingRiteFavor=true;draws+=riteDraws;
  }
  const chaosDraws=Number(nc.chaosFavor??1);
  if(postBattleReport.chaos===true && nc.chaosTriggered && chaosDraws>0 && !nc.smithingChaosFavor){
    nc.smithingChaosFavor=true;draws+=chaosDraws;
  }
  const rewards=[];
  for(let i=0;i<draws;i++) rewards.push(drawCovenantReward(nextState));
  nc.postBattleRewards=rewards.map(x=>x.label);
  nc.favorEarned=rewards.filter(x=>x.kind==='favor').reduce((sum,x)=>sum+(x.label.startsWith('+2')?2:1),0);
  const completed=completeEncounter(nextState,playerName());
  postBattleReport=null;
  if(!completed.regionComplete&&!completed.runComplete&&completed.current){pendingRevealId=completed.current.id;uiScreen='encounter';}
  const rewardText=rewards.length?`Rewards: ${rewards.map(x=>x.label).join(' · ')}`:'Post-battle report filed.';
  await commit(completed,{successToast:rewardText});
}
'''
s = s[:start] + replacement + s[end:]

# Update post-battle wording from deterministic currency to draw count.
s = s.replace("<div class=\"tc-kicker\">${label} · +${reward} Favor</div>", "<div class=\"tc-kicker\">${label} · ${reward} reward ${reward===1?'draw':'draws'}</div>")
s = s.replace("<span class=\"tc-report-stamp\">0 favor</span>", "<span class=\"tc-report-stamp\">no reward</span>")

# Global delegated listener for earned refreshes.
listener = r'''
if(!window.__tcBoonBound){
  window.__tcBoonBound=true;
  document.addEventListener('click',event=>{
    const btn=event.target.closest('[data-use-boon]');
    if(btn)useCovenantBoon(btn.dataset.useBoon);
  });
}
'''
script_end = s.rfind('</script>')
if script_end < 0:
    raise SystemExit('script end missing')
s = s[:script_end] + listener + '\n' + s[script_end:]

css = r'''
/* --- Random Covenant rewards / boon inventory --- */
.tc-boon-ledger{margin:10px 0 18px;padding:13px;border:1px solid rgba(198,161,90,.18);background:rgba(14,12,9,.48)}
.tc-boon-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin:9px 0 8px}.tc-boon-grid>div{min-width:0;padding:10px 6px;border:1px solid var(--line-soft);text-align:center}.tc-boon-grid strong{display:block;font:400 25px/1 Georgia,serif;color:var(--gold-bright)}.tc-boon-grid span{display:block;margin-top:5px;font:800 7px/1.25 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.06em;color:var(--ash)}
.tc-earned-refreshes{margin:10px 0 8px;padding-top:9px;border-top:1px solid var(--line-soft)}.tc-earned-refresh-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin-top:7px}.tc-earned-refresh-grid .btn:only-child{grid-column:1/-1}
@media(max-width:380px){.tc-boon-grid{gap:4px}.tc-boon-grid>div{padding:8px 3px}.tc-boon-grid span{font-size:6.5px}}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

for invariant in ['drawCovenantReward','appealWaivers','chaosRefreshes','riteRefreshes','Covenant reward draws','data-use-boon']:
    if invariant not in s:
        raise SystemExit('reward economy invariant missing: '+invariant)
if 'id="rerollChaos"' in s or 'id="rerollWeird"' in s:
    raise SystemExit('free encounter reroll button survived')

p.write_text(s)
