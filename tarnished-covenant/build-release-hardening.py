from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# -----------------------------------------------------------------------------
# 1) Runtime bug: earned Refresh tokens referenced reroll helpers that no longer
# existed after the UI rewrites. Restore explicit, state-safe implementations.
# -----------------------------------------------------------------------------
if 'function rerollChaos(state, actor)' not in s:
    marker = 'async function useCovenantBoon(kind){'
    if marker not in s:
        raise SystemExit('boon-use marker missing')
    helpers = r'''
function tcPickDifferent(pool,current,keyFn=x=>x){
  const choices=(pool||[]).filter(x=>keyFn(x)!==current);
  return pick(choices.length?choices:pool);
}
function rerollChaos(state, actor){
  const next=smithingCopy(state);
  if(!next.current || next.current.chaosTriggered)return next;
  const old=next.current.chaosTrigger;
  next.current.chaosTrigger=tcPickDifferent(chaosTriggers,old,x=>x);
  next.lastAction=`${actor} spent a Chaos Refresh. The trigger changed.`;
  next.updatedAt=new Date().toISOString();
  return next;
}
function rerollWeirdness(state, actor){
  const next=smithingCopy(state);
  if(!next.current)return next;
  const old=next.current.weirdness?.name||'';
  const weird=tcPickDifferent(weirdness,old,x=>x?.[0]);
  if(!weird)return next;
  const meta=typeof riteMeta==='function'?riteMeta(weird):{tier:'True',favor:1};
  next.current.weirdness={name:weird[0],text:weird[1],...meta};
  next.current.smithingRiteFavor=false;
  next.lastAction=`${actor} spent a Rite Refresh. A new Rite was drawn.`;
  next.updatedAt=new Date().toISOString();
  return next;
}
'''
    s = s.replace(marker, helpers + '\n' + marker, 1)

# Protect boon buttons against fast double taps / duplicate network writes.
old = """async function useCovenantBoon(kind){
  if(!run?.state?.current)return;
  const sm=smithingData(run.state),key=kind==='chaos'?'chaosRefreshes':'riteRefreshes';"""
new = """async function useCovenantBoon(kind){
  if(window.__tcBoonBusy || !run?.state?.current)return;
  window.__tcBoonBusy=true;
  const clicked=document.querySelector(`[data-use-boon=\"${kind}\"]`);
  if(clicked)clicked.disabled=true;
  const sm=smithingData(run.state),key=kind==='chaos'?'chaosRefreshes':'riteRefreshes';"""
if old not in s:
    raise SystemExit('useCovenantBoon start target missing')
s = s.replace(old,new,1)
old_end = """  staged=kind==='chaos'?rerollChaos(staged,playerName()):rerollWeirdness(staged,playerName());
  await commit(staged,{successToast:`${kind==='chaos'?'Chaos':'Rite'} refreshed. Token spent.`});
}"""
new_end = """  staged=kind==='chaos'?rerollChaos(staged,playerName()):rerollWeirdness(staged,playerName());
  try{await commit(staged,{successToast:`${kind==='chaos'?'Chaos':'Rite'} refreshed. Token spent.`});}
  finally{window.__tcBoonBusy=false;}
}"""
if old_end not in s:
    raise SystemExit('useCovenantBoon end target missing')
s=s.replace(old_end,new_end,1)
# Early-return paths above the try must release the guard.
s=s.replace("if(Number(sm[key]||0)<1)return setToast('No refresh token available.');",
            "if(Number(sm[key]||0)<1){window.__tcBoonBusy=false;return setToast('No refresh token available.');}",1)
s=s.replace("if(kind==='chaos'&&run.state.current.chaosTriggered)return setToast('Chaos has already broken loose. Too late to refresh it.');",
            "if(kind==='chaos'&&run.state.current.chaosTriggered){window.__tcBoonBusy=false;return setToast('Chaos has already broken loose. Too late to refresh it.');}",1)

# -----------------------------------------------------------------------------
# 2) Reward history bug: Compendium still calculated the pre-randomization
# deterministic Favor value. Store the actual reward result and full reward list.
# -----------------------------------------------------------------------------
s = s.replace(
    "favorEarned: riteFavor + chaosFavor\n  });",
    "favorEarned: Math.max(0, Number(encounter?.favorEarned ?? 0)),\n    rewards: structuredClone(encounter?.postBattleRewards || [])\n  });",
    1
)
if 'rewards: structuredClone(encounter?.postBattleRewards || [])' not in s:
    raise SystemExit('could not patch Compendium reward snapshot')

# Show the actual randomized rewards in old-fight reminiscence cards.
needle = """      ${mods.length?`<div class=\"tc-comp-mod penalties\"><span>ARMAMENT PENALTIES · ${mods.length}</span>${mods.map(x=>`<p><b>${h(x.name||'Penalty')}</b> · ${h(x.text||'')}</p>`).join('')}</div>`:''}
      <div class=\"tc-comp-footer\"><span>${entry.completedBy?`recorded by ${h(entry.completedBy)}`:'victory recorded'}</span><strong>${Number(entry.favorEarned||0)>0?`+${Number(entry.favorEarned)} Favor`:'No Favor'}</strong></div>"""
replacement = """      ${mods.length?`<div class=\"tc-comp-mod penalties\"><span>ARMAMENT PENALTIES · ${mods.length}</span>${mods.map(x=>`<p><b>${h(x.name||'Penalty')}</b> · ${h(x.text||'')}</p>`).join('')}</div>`:''}
      ${Array.isArray(entry.rewards)&&entry.rewards.length?`<div class=\"tc-comp-mod rewards\"><span>COVENANT REWARDS</span><p>${entry.rewards.map(h).join(' · ')}</p></div>`:''}
      <div class=\"tc-comp-footer\"><span>${entry.completedBy?`recorded by ${h(entry.completedBy)}`:'victory recorded'}</span><strong>${Number(entry.favorEarned||0)>0?`+${Number(entry.favorEarned)} Favor`:(Array.isArray(entry.rewards)&&entry.rewards.length?'Boons earned':'No reward')}</strong></div>"""
if needle in s:
    s=s.replace(needle,replacement,1)
else:
    raise SystemExit('Compendium footer marker missing')

# -----------------------------------------------------------------------------
# 3) Prevent accidental duplicate post-battle submissions on mobile.
# -----------------------------------------------------------------------------
old = """async function finalizePostBattleReport(){
  const state=run.state,c=state.current;
  if(!c || !postBattleReport || postBattleReport.encounterId!==c.id) return;"""
new = """async function finalizePostBattleReport(){
  if(window.__tcReportBusy)return;
  const state=run.state,c=state.current;
  if(!c || !postBattleReport || postBattleReport.encounterId!==c.id) return;
  window.__tcReportBusy=true;
  const submit=document.querySelector('#finishBattleReport');
  if(submit){submit.disabled=true;submit.textContent='Recording victory…';}"""
if old not in s:
    raise SystemExit('finalize report start missing')
s=s.replace(old,new,1)
old = """  await commit(completed,{successToast:rewardText});
}"""
new = """  try{await commit(completed,{successToast:rewardText});}
  finally{window.__tcReportBusy=false;}
}"""
if old not in s:
    raise SystemExit('finalize report commit target missing')
s=s.replace(old,new,1)

# -----------------------------------------------------------------------------
# 4) Appeal Waiver usability. The old confirmation always threatened a severe
# penalty even when the next appeal was already paid for.
# -----------------------------------------------------------------------------
old = '<div class="tc-muted">Changing an assigned weapon creates a severe random penalty.</div>'
new = '<div class="tc-muted">${smithingData(run.state).appealWaivers>0?`Appeal Waiver available · this appeal is penalty-free and will consume 1 waiver.`:`Changing an assigned weapon creates a severe random penalty.`}</div>'
if old in s:
    s=s.replace(old,new,1)
else:
    raise SystemExit('appeal explanation marker missing')

# -----------------------------------------------------------------------------
# 5) Mobile usability/accessibility polish: reliable 44px targets, focus states,
# wrapping, overscroll behavior, short-screen reports, and disabled feedback.
# -----------------------------------------------------------------------------
css = r'''
/* --- Release hardening / mobile usability --- */
html{-webkit-text-size-adjust:100%;text-size-adjust:100%;overscroll-behavior-y:none}
button,[role="button"],summary{touch-action:manipulation;-webkit-tap-highlight-color:rgba(224,193,123,.10)}
button:focus-visible,summary:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--gold-bright);outline-offset:2px}
button:disabled{pointer-events:none;filter:saturate(.55)}
.tc-bottom-nav button{min-height:44px}
.tc-ledger-tabs button{min-height:44px;padding:8px 4px}
.tc-settings-row{min-height:58px}
.tc-comp-card summary{min-height:60px}
.tc-value,.tc-feature-title,.tc-brief-boss,.tc-report-boss,.tc-comp-boss,.tc-path-name,.tc-forge-title{overflow-wrap:anywhere}
.tc-loadout-name,.tc-comp-weapons strong{overflow-wrap:anywhere}
.tc-earned-refresh-grid .btn{min-height:44px}
.tc-report-choices button{min-width:48px;min-height:44px}
.tc-sheet{max-height:calc(100dvh - 24px);overflow:auto;-webkit-overflow-scrolling:touch}
.tc-battle-report{min-height:calc(100dvh - 24px)}
@supports not (height:100dvh){.tc-battle-report{min-height:calc(100vh - 24px)}}
@media(max-width:360px){.tc-ledger-tabs button{font-size:7px;letter-spacing:.04em}.tc-bottom-nav button{letter-spacing:.03em}.tc-boon-grid{grid-template-columns:1fr}.tc-report-row{grid-template-columns:1fr}.tc-report-choices{width:100%}}
@media(max-height:640px){.tc-battle-report{justify-content:flex-start;padding-top:10px}.tc-report-victory{font-size:30px}.tc-report-boss{font-size:21px}.tc-report-row{padding:7px 3px}.tc-report-detail{-webkit-line-clamp:1}.tc-report-total{margin:7px 0 6px}.tc-report-note{display:none}}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

# -----------------------------------------------------------------------------
# 6) Static release regression checks. These catch runtime-reference regressions
# that `node --check` cannot, plus high-value UI invariants from prior fixes.
# -----------------------------------------------------------------------------
required = [
  'function rerollChaos(state, actor)',
  'function rerollWeirdness(state, actor)',
  'function drawCovenantReward(state)',
  'rewards: structuredClone(encounter?.postBattleRewards || [])',
  'id="refreshApp"',
  "const SESSION_COOKIE = 'tarnished_covenant_session_v1'",
  'data-ledger-view="compendium"',
  'Covenant reward draws',
  'data-use-boon="chaos"',
  'data-use-boon="rite"',
  'window.__tcReportBusy',
  'window.__tcBoonBusy',
]
for item in required:
    if item not in s:
        raise SystemExit('release invariant missing: '+item)

for forbidden in [
  'id="rerollChaos"',
  'id="rerollWeird"',
  'Smithing Favor earned</span>',
]:
    if forbidden in s:
        raise SystemExit('obsolete/free-control invariant violated: '+forbidden)

# Catch duplicate IDs for the important global controls. Dynamic overlays are not
# included here because those are intentionally created/destroyed at runtime.
for control_id in ['refreshApp','restartRun','finishBattleReport']:
    count=s.count(f'id="{control_id}"')
    if count>1:
        raise SystemExit(f'duplicate control id {control_id}: {count}')

p.write_text(s)
