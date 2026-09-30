from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Appeal Waivers are inventory, not an automatic trigger. Choosing a weapon
# appeal should let the Covenant decide whether to spend one or accept the
# normal penalty and bank the waiver for later.
s=re.sub(
    r"\n?/\* --- Explicit Appeal Waiver choice --- \*/.*?"
    r"/\* --- End Explicit Appeal Waiver choice --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

# changeWeapons keeps all existing reroll logic, but only consumes a waiver when
# the caller explicitly asks to use one.
s=s.replace(
    'function changeWeapons(state, actor, which) {',
    'function changeWeapons(state, actor, which, useWaiver = false) {',
    1,
)
s=s.replace(
    'const waived = sm.appealWaivers > 0;',
    'const waived = Boolean(useWaiver && sm.appealWaivers > 0);',
    1,
)
if 'function changeWeapons(state, actor, which, useWaiver = false) {' not in s:
    raise SystemExit('changeWeapons signature target missing')
if 'const waived = Boolean(useWaiver && sm.appealWaivers > 0);' not in s:
    raise SystemExit('explicit waiver guard target missing')

# Keep the old assembled function only as a dead compatibility fallback. Rename
# it once, then append the real showAppealMenu override at the very end of the
# script. This is resilient to the many late build layers that reorder helpers.
if 'function tcLegacyShowAppealMenu(){' not in s:
    if 'function showAppealMenu(){' not in s:
        raise SystemExit('legacy showAppealMenu target missing')
    s=s.replace('function showAppealMenu(){','function tcLegacyShowAppealMenu(){',1)

ui=r'''
/* --- Explicit Appeal Waiver choice --- */
function tcCloseAppealOverlay(){document.querySelector('#tcAppealOverlay')?.remove();}
async function tcResolveWeaponAppeal(which,useWaiver){
  const sm=smithingData(run?.state||{});
  if(useWaiver&&Number(sm.appealWaivers||0)<1)return setToast('No Appeal Waiver remains.');
  tcCloseAppealOverlay();
  const staged=changeWeapons(run.state,playerName(),which,Boolean(useWaiver));
  await commit(staged,{
    successToast:useWaiver?'Weapon appeal granted. Appeal Waiver spent.':'Weapon appeal granted. Penalty accepted.'
  });
}
function tcShowAppealWaiverChoice(which){
  const overlay=document.querySelector('#tcAppealOverlay');
  if(!overlay)return;
  const sm=smithingData(run.state),count=Number(sm.appealWaivers||0);
  const names=covenantNames(run.state);
  const label=which==='both'?'both assigned weapons':`${which==='chase'?names[0]:names[1]}’s assigned weapon`;
  const sheet=overlay.querySelector('.tc-sheet');
  if(!sheet)return;
  sheet.innerHTML=`<div class="tc-kicker red">armament appeal</div>
    <div class="tc-value" style="margin:6px 0 4px">Appeal ${h(label)}?</div>
    <div class="tc-muted">You have <strong>${count}</strong> Appeal Waiver${count===1?'':'s'}. A waiver prevents the severe random penalty, but spending it is optional.</div>
    <div class="tc-panel soft" style="margin-top:14px"><div class="tc-kicker gold">Choose the price</div><div class="tc-muted" style="margin-top:6px">One waiver covers this entire appeal${which==='both'?', including both weapons':''}.</div></div>
    <div class="tc-stack" style="margin-top:14px;display:grid;gap:8px">
      <button id="tcSpendAppealWaiver" class="btn gold">Spend 1 Appeal Waiver · ${Math.max(0,count-1)} left</button>
      <button id="tcTakeAppealPenalty" class="btn curse">Keep Waiver · Take Penalty</button>
    </div>
    <button id="closeAppeal" class="btn text-btn">Back</button>`;
  sheet.querySelector('#tcSpendAppealWaiver')?.addEventListener('click',()=>tcResolveWeaponAppeal(which,true));
  sheet.querySelector('#tcTakeAppealPenalty')?.addEventListener('click',()=>tcResolveWeaponAppeal(which,false));
  sheet.querySelector('#closeAppeal')?.addEventListener('click',showAppealMenu);
}
function showAppealMenu(){
  tcCloseAppealOverlay();
  const state=run.state,c=state.current,sm=smithingData(state),waivers=Number(sm.appealWaivers||0);
  document.body.insertAdjacentHTML('beforeend',`<div id="tcAppealOverlay" class="tc-overlay"><div class="tc-sheet"><div class="tc-kicker red">armament appeal</div><div class="tc-value" style="margin:6px 0 4px">Refuse the decree?</div><div class="tc-muted">Changing an assigned weapon normally creates a severe random penalty.${waivers>0?` You have ${waivers} Appeal Waiver${waivers===1?'':'s'} and may choose whether to spend one after selecting the appeal.`:''}</div><div class="tc-panel soft" style="margin-top:14px"><div class="tc-muted">${h(playerLabel('chase',state).toUpperCase())}</div><div>${h(c.chase.name)}</div><div class="tc-muted" style="margin-top:8px">${h(playerLabel('morgan',state).toUpperCase())}</div><div>${h(c.morgan.name)}</div></div><div class="tc-actions-3"><button class="btn curse" data-overlay-appeal="chase">${h(playerLabel('chase',state))}</button><button class="btn curse" data-overlay-appeal="morgan">${h(playerLabel('morgan',state))}</button><button class="btn curse" data-overlay-appeal="both">Both</button></div><button id="closeAppeal" class="btn text-btn">Cancel</button></div></div>`);
  document.querySelector('#closeAppeal')?.addEventListener('click',tcCloseAppealOverlay);
  document.querySelectorAll('[data-overlay-appeal]').forEach(btn=>btn.addEventListener('click',()=>{
    const which=btn.dataset.overlayAppeal;
    if(waivers>0)tcShowAppealWaiverChoice(which);
    else void tcResolveWeaponAppeal(which,false);
  }));
}
/* --- End Explicit Appeal Waiver choice --- */
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+ui+'\n'+s[idx:]

required=[
    'function changeWeapons(state, actor, which, useWaiver = false)',
    'Boolean(useWaiver && sm.appealWaivers > 0)',
    'function tcLegacyShowAppealMenu()',
    'function tcShowAppealWaiverChoice(which)',
    'Spend 1 Appeal Waiver',
    'Keep Waiver · Take Penalty',
    'changeWeapons(run.state,playerName(),which,Boolean(useWaiver))',
    'if(waivers>0)tcShowAppealWaiverChoice(which)',
]
for needle in required:
    if needle not in s: raise SystemExit('appeal waiver choice invariant missing: '+needle)
if 'const waived = sm.appealWaivers > 0;' in s:
    raise SystemExit('automatic Appeal Waiver consumption remains in changeWeapons')

p.write_text(s)
print('Appeal Waivers now require an explicit spend-or-save choice.')
