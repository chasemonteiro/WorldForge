from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Final stability layer. This intentionally runs last so later feature patches cannot
# re-introduce stale UI labels or known state bugs.

# 1) Armament penalties are generated against stable internal player slots, but all
# visible scope/text must use the Covenant's chosen character names.
old = '''function penanceMarkup(c) {
  if (!c.penances?.length) return '';
  return `<section class="curse-section">
    <div class="section-kicker redtext">armament penalties</div>
    <div class="curse-head"><span class="curse-glyphs">${'☠'.repeat(Math.min(c.penances.length,6))}</span><span>${c.penances.length} active ${c.penances.length===1?'punishment':'punishments'}</span></div>
    ${c.penances.map((p,i)=>`<div class="penance-item">
      <div class="scope">${h(p.scope)} · penalty ${i+1}</div>
      <div class="penance-name">${h(p.name)}</div>
      <div class="penance-text">${h(p.text)}</div>
    </div>`).join('')}
    <div class="subtext">Penalties stack until the current target is defeated.</div>
  </section>`;
}'''
new = '''function penanceMarkup(c) {
  if (!c.penances?.length) return '';
  const state = run?.state;
  return `<section class="curse-section">
    <div class="section-kicker redtext">armament penalties</div>
    <div class="curse-head"><span class="curse-glyphs">${'☠'.repeat(Math.min(c.penances.length,6))}</span><span>${c.penances.length} active ${c.penances.length===1?'punishment':'punishments'}</span></div>
    ${c.penances.map((p,i)=>`<div class="penance-item">
      <div class="scope">${h(personalizePlayers(p.scope,state))} · penalty ${i+1}</div>
      <div class="penance-name">${h(p.name)}</div>
      <div class="penance-text">${h(personalizePlayers(p.text,state))}</div>
    </div>`).join('')}
    <div class="subtext">Penalties stack until the current target is defeated.</div>
  </section>`;
}'''
if old not in s:
    raise SystemExit('penanceMarkup stability target missing')
s = s.replace(old, new, 1)

# 2) Appeal activity text should use the selected character name, not the internal slot.
old = "  const label = which === 'both' ? 'both weapons' : `${which === 'chase' ? 'Chase' : 'Morgan'}’s weapon`;\n  next.lastAction = `${actor} changed ${label}; a penalty was added.`;"
new = "  const names = Array.isArray(next.playerNames) && next.playerNames.length >= 2 ? next.playerNames : ['Tarnished One','Tarnished Two'];\n  const label = which === 'both' ? 'both weapons' : `${which === 'chase' ? names[0] : names[1]}’s weapon`;\n  next.lastAction = `${actor} changed ${label}; a penalty was added.`;"
if old not in s:
    raise SystemExit('changeWeapons label target missing')
s = s.replace(old, new, 1)

# 3) Keep the legacy appeal confirmation safe too. It is not the main overlay anymore,
# but older/alternate render paths can still call it.
pattern = r"function showAppeal\(which\) \{.*?\n\}"
replacement = r'''function showAppeal(which) {
  const names = covenantNames(run?.state);
  const labels = { chase: `${names[0]}’s weapon`, morgan: `${names[1]}’s weapon`, both: 'both weapons' };
  const box = document.querySelector('#appealConfirm');
  if (!box) return showAppealMenu();
  box.innerHTML = `<div class="confirm">
    <div class="section-kicker redtext">armament appeal</div>
    <h3>Change ${h(labels[which] || 'assigned weapon')}?</h3>
    <div class="rtext">You get a new region-legal weapon, then ${h(names[0])}, ${h(names[1])}, or both receive a severe random penalty. You do not see the penalty first.</div>
    <div class="confirm-actions"><button id="accept" class="btn curse" type="button">Accept Penalty & Reroll</button><button id="cancel" class="btn ghost" type="button">Keep Current Weapon</button></div>
  </div>`;
  document.querySelector('#cancel')?.addEventListener('click',()=>{box.innerHTML='';});
  document.querySelector('#accept')?.addEventListener('click',()=>commit(changeWeapons(run.state,playerName(),which)));
}'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('showAppeal stability target missing')

# 4) Restart is a clean run in the same ruleset: preserve character names and DLC choice.
# Also remove the stale claim that a specifically named person's phone returns home.
s = s.replace("'Morgan’s phone resets too. The room code stays the same.'", "'The shared run resets for both players. The room code stays the same.'")
old = '''      const fresh = initialRunState({
        region,
        severity,
        createdBy: latestState?.createdBy || state.createdBy || playerName()
      });'''
new = '''      const fresh = initialRunState({
        region,
        severity,
        includeDlc: Boolean(latestState?.includeDlc ?? state.includeDlc),
        playerNames: latestState?.playerNames || state.playerNames || ['Tarnished One','Tarnished Two'],
        createdBy: latestState?.createdBy || state.createdBy || playerName()
      });'''
if old not in s:
    raise SystemExit('restart state preservation target missing')
s = s.replace(old, new, 1)
s = s.replace("fresh.lastAction = `${playerName()} restarted the Covenant. started a fresh run.`;", "fresh.lastAction = `${playerName()} restarted the Covenant.`;")

# 5) Hewg should never consume a credit for a weapon already in the veteran arsenal.
pattern = r"function masterworkCurrent\(state,slot\)\{.*?\n\}"
replacement = r'''function masterworkCurrent(state,slot){
  const next=smithingCopy(state);
  if(next.smithing.masterworkCredits<1||!next.current)return null;
  const weapon=slot==='morgan'?next.current.morgan?.name:next.current.chase?.name;
  if(!weapon)return null;
  if(next.smithing.masterworks.includes(weapon)){
    setToast(`${weapon} is already Masterworked.`);
    return null;
  }
  next.smithing.masterworks.push(weapon);
  next.smithing.masterworkCredits-=1;
  next.lastAction=`Hewg has Masterworked ${weapon}.`;
  return next;
}'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('masterworkCurrent stability target missing')

# 6) Never grant a bearing/Masterwork for an invalid contract definition.
pattern = r"function claimSmithingBearing\(state\)\{.*?\n\}"
replacement = r'''function claimSmithingBearing(state){
  const next=smithingCopy(state),ct=next.smithing.activeContract;
  if(!ct||ct.status!=='sanctioned')return null;
  const b=bellById(ct.bearingId);
  if(!b){
    setToast('This contract is no longer valid. No reward was spent or granted.');
    return null;
  }
  next.smithing.acquired=Array.from(new Set([...next.smithing.acquired,ct.bearingId]));
  next.smithing.masterworkCredits+=1;
  next.smithing.activeContract=null;
  next.lastAction=`${b.name} claimed. Hewg owes the Covenant one Masterwork.`;
  return next;
}'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('claimSmithingBearing stability target missing')

# 7) Make stale internal actor names harmless wherever lastAction is shown in legacy UI.
# Stable slot names remain in persisted history/backend membership by design.
s = s.replace("${h(state.lastAction || '')}", "${h(personalizePlayers(state.lastAction || '', state))}")

# Build-time regression checks for bugs found during the audit.
forbidden = {
    "legacy appeal label map": "const labels = { chase: 'Chase’s weapon', morgan: 'Morgan’s weapon'",
    "hard-coded appeal mutation label": "? 'Chase' : 'Morgan'}’s weapon",
    "hard-coded restart phone": "Morgan’s phone resets too",
    "unpersonalized penalty scope": "<div class=\"scope\">${h(p.scope)}",
    "unpersonalized penalty text": "<div class=\"penance-text\">${h(p.text)}",
}
for label, needle in forbidden.items():
    if needle in s:
        raise SystemExit(f'Regression detected: {label}')

# Important structural invariants. Fail the build instead of publishing a half-patched app.
required = [
    'function personalizePlayers(',
    'function renderChaosEvent(',
    'function renderSmithingContract(',
    'function masterworkCurrent(',
    'function renderLedger()',
    'function renderEncounter()',
    'function renderRun()',
    'playerNames:',
    'data-smith-action="commission"',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'App invariant missing: {needle}')

p.write_text(s)
