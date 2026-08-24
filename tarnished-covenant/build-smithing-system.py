from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Smithing progression is deliberately layered on after the rest of the UI patches.
# It stores only JSON-safe fields inside the shared run state, so Supabase sync needs no schema change.

helpers = r'''
const TC_BELL_BEARINGS = [
  {id:'smith1',kind:'Smithing',name:'Smithing-Stone Miner’s Bell Bearing [1]',region:'Liurnia of the Lakes',custodian:'Crystalian',place:'Raya Lucaria Crystal Tunnel'},
  {id:'somber1',kind:'Somber',name:'Somberstone Miner’s Bell Bearing [1]',region:'Caelid',custodian:'Fallingstar Beast',place:'Sellia Crystal Tunnel'},
  {id:'smith2',kind:'Smithing',name:'Smithing-Stone Miner’s Bell Bearing [2]',region:'Altus Plateau + Leyndell',custodian:'Sealed Tunnel cache',place:'Sealed Tunnel'},
  {id:'somber2',kind:'Somber',name:'Somberstone Miner’s Bell Bearing [2]',region:'Altus Plateau + Leyndell',custodian:'Crystalian Duo',place:'Altus Tunnel'},
  {id:'smith3',kind:'Smithing',name:'Smithing-Stone Miner’s Bell Bearing [3]',region:'Mountaintops of the Giants',custodian:'Zamor Ruins cache',place:'Zamor Ruins'},
  {id:'somber3',kind:'Somber',name:'Somberstone Miner’s Bell Bearing [3]',region:'Mountaintops of the Giants',custodian:'The frozen road',place:'First Church of Marika'},
  {id:'smith4',kind:'Smithing',name:'Smithing-Stone Miner’s Bell Bearing [4]',region:'Crumbling Farum Azula',custodian:'Godskin Duo',place:'Dragon Temple'},
  {id:'somber4',kind:'Somber',name:'Somberstone Miner’s Bell Bearing [4]',region:'Crumbling Farum Azula',custodian:'Farum Azula cache',place:'Crumbling Farum Azula'}
];

const TC_SMITHING_TASKS = [
  'MINER’S DUE: possess at least five Cracked Crystals before approaching the custodian.',
  'RAINBOW AUDIT: place three Rainbow Stones at the entrance to the bearing’s dungeon or route.',
  'FALSE GRACE: use one Grace Mimic somewhere on the way to the bearing. It will accomplish nothing. This is important.',
  'LIGHTING CODE: use a Glowstone before entering the bearing’s dungeon or approach.',
  'SOFT LANDING CLAUSE: use Soft Cotton before entering the bearing’s dungeon or approach.',
  'TURTLE RETAINER: one Tarnished must consume a Pickled Turtle Neck before confronting the custodian.',
  'CRAB RETAINER: one Tarnished must consume Boiled Crab before confronting the custodian.',
  'FORMAL NOTICE: use any Prattling Pate at the fog gate or immediately before collecting the bearing.',
  'POST-MINING HYGIENE: use Soap after the contract is complete. The union has standards.',
  'LANTERN INSPECTION: keep a Lantern lit for the entire dungeon or approach.',
  'STRIKE NEGOTIATOR: at least one Tarnished must bring a strike-damage weapon to the custodian.',
  'POTTERY CLAUSE: land one thrown pot on the custodian before the contract can be considered complete.',
  'WARMING STONE MEETING: place a Warming Stone at the next safe point inside the dungeon or route.',
  'RUIN FRAGMENT TITHE: possess at least five Ruin Fragments when you arrive.',
  'CEREMONIAL NONSENSE: both Tarnished must gesture before the fog gate or before collecting the bearing.',
  'NO EARLY JUICE: no Crimson Flask until the custodian is below half health. If there is no custodian fight, no flask until the bearing is in sight.'
];

let ledgerView = 'remembrances';

function smithingData(state) {
  const raw = state?.smithing || {};
  return {
    favor: Number(raw.favor || 0),
    acquired: Array.isArray(raw.acquired) ? raw.acquired : [],
    activeContract: raw.activeContract || null,
    masterworks: Array.isArray(raw.masterworks) ? raw.masterworks : [],
    masterworkCredits: Number(raw.masterworkCredits || 0)
  };
}
function smithingCopy(state) {
  const next = JSON.parse(JSON.stringify(state));
  next.smithing = smithingData(next);
  return next;
}
function bellById(id){ return TC_BELL_BEARINGS.find(x=>x.id===id); }
function bellAccessible(state,b){
  try { return b.region===state.region || regionUnlocked(state,b.region) || (state.clearedRegions||[]).includes(b.region); }
  catch { return b.region===state.region; }
}
function availableBellBearings(state){
  const sm=smithingData(state);
  return TC_BELL_BEARINGS.filter(b=>!sm.acquired.includes(b.id) && (!sm.activeContract || sm.activeContract.bearingId!==b.id) && bellAccessible(state,b));
}
function smithingFavorMarkup(state){
  const sm=smithingData(state);
  return `<div class="tc-forge-favor"><span class="tc-forge-mark">✦</span><div><div class="tc-kicker ember">smithing favor</div><strong>${sm.favor}</strong></div><div class="tc-muted">earned by honoring rites and enduring Chaos</div></div>`;
}
function smithingHubMarkup(state){
  const sm=smithingData(state), contract=sm.activeContract, bearing=contract?bellById(contract.bearingId):null;
  if(contract && bearing){
    const sanctioned=contract.status==='sanctioned';
    return `<button class="tc-forge-notice ${sanctioned?'sanctioned':''}" data-smith-action="open-contract" type="button">
      <div class="tc-forge-glyph">${sanctioned?'⚒':'◈'}</div><div><div class="tc-kicker ember">${sanctioned?'custodian sanctioned':'active bell bearing contract'}</div><div class="tc-forge-title">${h(bearing.name)}</div><div class="tc-muted">${h(sanctioned?`${bearing.custodian} · permission granted`:'The Twin Maiden Husks have developed demands.')}</div></div><span class="tc-forge-arrow">›</span>
    </button>`;
  }
  const available=availableBellBearings(state);
  if(sm.favor>=3 && available.length){
    return `<button class="tc-forge-notice" data-smith-action="commission" type="button"><div class="tc-forge-glyph">◈</div><div><div class="tc-kicker ember">a contract awaits</div><div class="tc-forge-title">The Smith Calls In A Debt</div><div class="tc-muted">Spend 3 Favor to commission a Bell Bearing Contract.</div></div><span class="tc-forge-arrow">›</span></button>`;
  }
  return `<button class="tc-forge-notice quiet" data-smith-action="ledger" type="button"><div class="tc-forge-glyph">⚒</div><div><div class="tc-kicker ember">hewg’s books</div><div class="tc-forge-title">${sm.favor} Smithing Favor</div><div class="tc-muted">${sm.favor<3?'3 Favor commissions a Bell Bearing Contract.':'No accessible contract is waiting yet.'}</div></div><span class="tc-forge-arrow">›</span></button>`;
}
function smithingLedgerMarkup(state){
  const sm=smithingData(state), contract=sm.activeContract, acquired=new Set(sm.acquired);
  return `<div class="tc-smith-ledger">
    ${smithingFavorMarkup(state)}
    ${contract?(()=>{const b=bellById(contract.bearingId);return b?`<button class="tc-contract-mini" data-smith-action="open-contract"><div class="tc-kicker ember">current contract · ${contract.status==='sanctioned'?'sanctioned':'terms outstanding'}</div><strong>${h(b.name)}</strong><span>${h(b.custodian)} · ${h(b.place)}</span></button>`:''})():''}
    <div class="tc-kicker ember" style="margin-top:18px">bell bearing ledger</div>
    <div class="tc-bearing-grid">${TC_BELL_BEARINGS.map(b=>{const got=acquired.has(b.id),active=contract?.bearingId===b.id,accessible=bellAccessible(state,b);return `<div class="tc-bearing ${got?'done':active?'active':accessible?'available':'locked'}"><div><span class="tc-bearing-kind">${h(b.kind)}</span><strong>${h(b.name.replace(/^.*Bell Bearing /,'Bell Bearing '))}</strong><small>${h(b.place)}</small></div><span class="tc-bearing-stamp">${got?'claimed':active?'contract':accessible?'eligible':'later'}</span></div>`}).join('')}</div>
    <div class="tc-workbench"><div class="tc-kicker ember">Hewg’s Workbench</div><div class="tc-muted">Each claimed Bell Bearing grants one Masterwork. Masterworked weapons become part of the Covenant’s veteran arsenal.</div><div class="tc-workbench-credit">MASTERWORK CREDITS <strong>${sm.masterworkCredits}</strong></div>${sm.masterworkCredits>0&&state.current?`<div class="tc-master-actions"><button class="btn ghost" data-smith-action="masterwork" data-slot="chase">Masterwork ${h(playerLabel('chase',state))}’s ${h(state.current.chase.name)}</button><button class="btn ghost" data-smith-action="masterwork" data-slot="morgan">Masterwork ${h(playerLabel('morgan',state))}’s ${h(state.current.morgan.name)}</button></div>`:''}
      <div class="tc-master-list">${sm.masterworks.length?sm.masterworks.map(w=>`<span>⚒ ${h(w)}</span>`).join(''):'<span class="tc-muted">No veteran weapons yet.</span>'}</div>
    </div>
  </div>`;
}
function remembranceLedgerBody(state){
  const req=requiredRemembrances(state),done=req.filter(x=>hasRemembrance(state,x));
  const regionNames=Object.keys(regions).filter(r=>state.includeDlc||!r.includes('· DLC')).filter(r=>r!=='The Erdtree');
  return `<div class="tc-ledger-head"><div><div class="tc-kicker gold">remembrances claimed</div><div class="tc-muted">The final seal opens only when the ledger is complete.</div></div><div class="tc-ledger-count">${done.length}/${req.length}</div></div>
    <div class="tc-panel"><div class="tc-rem-grid">${req.map(name=>`<div class="tc-rem ${hasRemembrance(state,name)?'done':''}"><span>${h(name)}</span><span class="stamp">${hasRemembrance(state,name)?'claimed':'missing'}</span></div>`).join('')}</div></div>
    <div class="tc-kicker gold" style="margin-top:20px">world progress</div><div class="tc-region-list">${regionNames.map(r=>`<div class="tc-region-chip ${(state.clearedRegions||[]).includes(r)?'done':''}">${h(r)}${r===state.region?' · ACTIVE':(state.clearedRegions||[]).includes(r)?' · CLEARED':''}</div>`).join('')}</div>`;
}
function renderSmithingContract(){
  const state=run.state,sm=smithingData(state),ct=sm.activeContract,b=ct?bellById(ct.bearingId):null;
  if(!b) return;
  document.querySelector('#tcSmithOverlay')?.remove();
  document.body.insertAdjacentHTML('beforeend',`<div id="tcSmithOverlay" class="tc-overlay tc-forge-overlay"><div class="tc-sheet tc-contract-sheet">
    <button class="tc-sheet-x" data-smith-action="close-contract">×</button><div class="tc-contract-seal">⚒</div><div class="tc-kicker ember">THE SMITH CALLS IN A DEBT</div><h2>${h(b.name)}</h2>
    <div class="tc-contract-facts"><div><span>Custodian</span><strong>${h(b.custodian)}</strong></div><div><span>Location</span><strong>${h(b.place)}</strong></div></div>
    ${ct.status==='sanctioned'?`<div class="tc-contract-sanction"><div class="tc-kicker ember">sanction granted</div><strong>The custodian is approved for execution.</strong><p>Kill the custodian or collect the bearing, then confirm below. The bearing itself is the receipt.</p></div><button class="btn gold" data-smith-action="claim-bearing">Bearing Claimed · Close Contract</button>`:`<div class="tc-contract-demand"><div class="tc-kicker ember">price of permission</div><p>${h(ct.task)}</p></div><div class="tc-muted tc-contract-note">Honor system: when you have actually completed the demand in Elden Ring, certify it here.</div><button class="btn gold" data-smith-action="fulfill-contract">We Have Met The Union’s Demands</button>`}
  </div></div>`);
}
function commissionSmithingContract(state){
  const sm=smithingData(state),pool=availableBellBearings(state); if(sm.favor<3||!pool.length) return null;
  const next=smithingCopy(state),b=pool[Math.floor(Math.random()*pool.length)],task=TC_SMITHING_TASKS[Math.floor(Math.random()*TC_SMITHING_TASKS.length)];
  next.smithing.favor-=3; next.smithing.activeContract={bearingId:b.id,task,status:'task',commissionedAt:new Date().toISOString()}; next.lastAction=`A Bell Bearing Contract has been commissioned for ${b.name}.`; return next;
}
function fulfillSmithingContract(state){const next=smithingCopy(state);if(!next.smithing.activeContract)return null;next.smithing.activeContract.status='sanctioned';next.lastAction='The union’s demands have been met. Custodian sanctioned.';return next;}
function claimSmithingBearing(state){const next=smithingCopy(state),ct=next.smithing.activeContract;if(!ct||ct.status!=='sanctioned')return null;const b=bellById(ct.bearingId);next.smithing.acquired=Array.from(new Set([...next.smithing.acquired,ct.bearingId]));next.smithing.masterworkCredits+=1;next.smithing.activeContract=null;next.lastAction=`${b?.name||'Bell Bearing'} claimed. Hewg owes the Covenant one Masterwork.`;return next;}
function claimForgeFavor(state,type){
  if(!state.current)return null; const next=smithingCopy(state),c=next.current;
  if(type==='rite'){if(c.smithingRiteFavor)return null;c.smithingRiteFavor=true;next.smithing.favor+=1;next.lastAction='Odd Rite honored. +1 Smithing Favor.';}
  else {if(!c.chaosTriggered||c.smithingChaosFavor)return null;c.smithingChaosFavor=true;next.smithing.favor+=1;next.lastAction='Chaos endured. +1 Smithing Favor.';}
  return next;
}
function masterworkCurrent(state,slot){const next=smithingCopy(state);if(next.smithing.masterworkCredits<1||!next.current)return null;const weapon=slot==='morgan'?next.current.morgan?.name:next.current.chase?.name;if(!weapon)return null;if(!next.smithing.masterworks.includes(weapon))next.smithing.masterworks.push(weapon);next.smithing.masterworkCredits-=1;next.lastAction=`Hewg has Masterworked ${weapon}.`;return next;}
'''

marker = 'function navMarkup(active) {'
if marker not in s:
    raise SystemExit('navMarkup marker missing')
s = s.replace(marker, helpers + '\n' + marker, 1)

# Replace the Ledger screen with a compact segmented ledger.
pattern = r"function renderLedger\(\) \{.*?\n\}\n\nfunction renderSettings"
replacement = r'''function renderLedger() {
  const state=run.state;
  app.innerHTML=`<section class="tc-screen">${screenTop(ledgerView==='smithing'?'Smithing Ledger':'Remembrance Ledger')}
    <div class="tc-ledger-tabs"><button class="${ledgerView==='remembrances'?'active':''}" data-ledger-view="remembrances">Remembrances</button><button class="${ledgerView==='smithing'?'active':''}" data-ledger-view="smithing">Smithing</button></div>
    ${ledgerView==='smithing'?smithingLedgerMarkup(state):remembranceLedgerBody(state)}
    ${navMarkup('ledger')}</section>`;
  bindNav();
}

function renderSettings'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('renderLedger block missing')

# Insert Smithing notice into Site of Grace just above the room code.
needle = '    <div class="tc-code-row">CODE <strong>${h(run.joinCode||\'LOCAL\')}</strong><button id="share">SHARE ↗</button></div>'
if needle not in s:
    raise SystemExit('Site of Grace code-row marker missing')
s = s.replace(needle, '    ${smithingHubMarkup(state)}\n' + needle, 1)

# Give Encounter a small Favor claim strip. These are deliberately honor-system buttons.
needle = '    <button id="complete" class="btn gold victory">${c.target.exit?\'CAPSTONE DEFEATED · CONTINUE\':\'VICTORY · ROLL NEXT ENCOUNTER\'}</button>'
if needle not in s:
    raise SystemExit('Encounter victory marker missing')
favor = '''    <div class="tc-forge-claims"><div class="tc-kicker ember">forge favor · honor system</div><button data-smith-action="favor-rite" ${c.smithingRiteFavor?'disabled':''}>${c.smithingRiteFavor?'✓ Rite Favor Claimed':'Odd Rite Honored · +1'}</button><button data-smith-action="favor-chaos" ${(!c.chaosTriggered||c.smithingChaosFavor)?'disabled':''}>${c.smithingChaosFavor?'✓ Chaos Favor Claimed':'Chaos Endured · +1'}</button></div>\n'''
s = s.replace(needle, favor + needle, 1)

# One delegated listener handles all forge controls across rerenders and overlays.
listener = r'''
if (!window.__tcSmithingBound) {
  window.__tcSmithingBound = true;
  document.addEventListener('click', async (event) => {
    const tab=event.target.closest('[data-ledger-view]');
    if(tab){ledgerView=tab.dataset.ledgerView;uiScreen='ledger';renderRun();return;}
    const el=event.target.closest('[data-smith-action]'); if(!el)return;
    const action=el.dataset.smithAction;
    if(action==='close-contract'){document.querySelector('#tcSmithOverlay')?.remove();return;}
    if(action==='ledger'){ledgerView='smithing';uiScreen='ledger';renderRun();return;}
    if(action==='open-contract'){renderSmithingContract();return;}
    if(action==='commission'){const next=commissionSmithingContract(run.state);if(!next)return setToast('No Bell Bearing Contract is available yet.');if(await commit(next,{successToast:'Contract commissioned. 3 Favor spent.'}))renderSmithingContract();return;}
    if(action==='fulfill-contract'){const next=fulfillSmithingContract(run.state);if(!next)return;if(await commit(next,{successToast:'Custodian sanctioned.'}))renderSmithingContract();return;}
    if(action==='claim-bearing'){const next=claimSmithingBearing(run.state);if(!next)return;if(await commit(next,{successToast:'Bell Bearing claimed. +1 Masterwork.'})){document.querySelector('#tcSmithOverlay')?.remove();ledgerView='smithing';uiScreen='ledger';renderRun();}return;}
    if(action==='favor-rite'){const next=claimForgeFavor(run.state,'rite');if(next)await commit(next,{successToast:'+1 Smithing Favor'});return;}
    if(action==='favor-chaos'){const next=claimForgeFavor(run.state,'chaos');if(next)await commit(next,{successToast:'+1 Smithing Favor'});return;}
    if(action==='masterwork'){const next=masterworkCurrent(run.state,el.dataset.slot);if(next)await commit(next,{successToast:'Hewg has done something useful.'});return;}
  });
}
'''
marker = 'async function startApp()'
if marker not in s:
    raise SystemExit('startApp marker missing')
s = s.replace(marker, listener + '\n' + marker, 1)

css = r'''
/* --- Smithing Favor / Bell Bearing Contracts --- */
:root{--ember:#d08a48;--ember-soft:#8c572d;--iron:#383630}
.tc-kicker.ember,.ember{color:var(--ember)}
.tc-ledger-tabs{display:grid;grid-template-columns:1fr 1fr;border:1px solid #453a2b;margin:4px 0 14px;background:#0b0907;clip-path:polygon(8px 0,calc(100% - 8px) 0,100% 8px,100% calc(100% - 8px),calc(100% - 8px) 100%,8px 100%,0 calc(100% - 8px),0 8px)}
.tc-ledger-tabs button{border:0;background:transparent;color:#7e7565;padding:11px 8px;font:11px Georgia,serif;letter-spacing:.08em}.tc-ledger-tabs button+button{border-left:1px solid #453a2b}.tc-ledger-tabs button.active{color:#f1d7ad;background:linear-gradient(180deg,rgba(193,116,49,.18),rgba(72,43,23,.16));box-shadow:inset 0 -2px var(--ember)}
.tc-forge-notice{width:100%;display:grid;grid-template-columns:42px 1fr 18px;align-items:center;gap:10px;text-align:left;margin:11px 0;padding:13px 12px;border:1px solid #654427;color:var(--ink);background:radial-gradient(circle at 8% 50%,rgba(184,92,35,.18),transparent 34%),linear-gradient(120deg,#1b140d,#0c0a07);clip-path:polygon(10px 0,calc(100% - 10px) 0,100% 10px,100% calc(100% - 10px),calc(100% - 10px) 100%,10px 100%,0 calc(100% - 10px),0 10px)}
.tc-forge-notice.quiet{border-color:#3e3528}.tc-forge-notice.sanctioned{border-color:#8c6238;box-shadow:inset 0 0 26px rgba(199,114,45,.07)}.tc-forge-glyph{font-size:26px;color:var(--ember);text-align:center}.tc-forge-title{font:19px/1.06 Georgia,serif;margin:4px 0}.tc-forge-arrow{color:#9b6b3d;font-size:25px}
.tc-forge-favor{display:grid;grid-template-columns:42px auto 1fr;align-items:center;gap:10px;padding:14px;border:1px solid #604324;background:linear-gradient(110deg,rgba(48,31,18,.8),rgba(11,9,7,.8));margin-bottom:11px}.tc-forge-favor strong{font:31px Georgia,serif;color:#f1c684}.tc-forge-mark{font-size:28px;color:var(--ember)}
.tc-bearing-grid{display:grid;gap:5px;margin:7px 0 18px}.tc-bearing{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px;border:1px solid #28251f;background:#0d0c0a}.tc-bearing>div{display:grid;gap:2px}.tc-bearing strong{font:14px Georgia,serif}.tc-bearing small{color:#827a6d;font-size:9px}.tc-bearing-kind{font-size:7px;letter-spacing:.12em;text-transform:uppercase;color:#8a7558}.tc-bearing-stamp{font-size:7px;letter-spacing:.09em;text-transform:uppercase;color:#625c52}.tc-bearing.available{border-color:#493822}.tc-bearing.active{border-color:var(--ember);background:rgba(73,39,18,.23)}.tc-bearing.done{border-color:#65543a;color:#cbb98d}.tc-bearing.done .tc-bearing-stamp,.tc-bearing.active .tc-bearing-stamp{color:var(--ember)}.tc-bearing.locked{opacity:.48}
.tc-contract-mini{width:100%;display:grid;text-align:left;gap:4px;padding:12px;border:1px solid #6e4928;background:#171008;color:var(--ink)}.tc-contract-mini strong{font:17px Georgia,serif}.tc-contract-mini span{font-size:9px;color:#948777}
.tc-workbench{padding:14px;border:1px solid #41392d;background:radial-gradient(circle at 95% 0,rgba(191,105,45,.10),transparent 37%),#0d0b09}.tc-workbench-credit{display:flex;justify-content:space-between;margin:12px 0 8px;padding-top:9px;border-top:1px solid #302a21;font-size:8px;letter-spacing:.1em;color:#817667}.tc-workbench-credit strong{color:var(--ember)}.tc-master-actions{display:grid;gap:6px}.tc-master-actions .btn{font-size:9px;padding:9px}.tc-master-list{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}.tc-master-list span{border:1px solid #443728;padding:6px 8px;font-size:9px;color:#c4aa83}
.tc-forge-claims{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin:10px 0;padding:10px;border:1px solid #3c3022;background:rgba(25,16,10,.5)}.tc-forge-claims .tc-kicker{grid-column:1/-1}.tc-forge-claims button{border:1px solid #604324;background:#171008;color:#caa47a;padding:9px 6px;font:8px Georgia,serif;letter-spacing:.04em}.tc-forge-claims button:disabled{opacity:.42}
.tc-forge-overlay{background:rgba(3,2,1,.90)}.tc-contract-sheet{position:relative;border-color:#76502d;background:radial-gradient(circle at 50% 0,rgba(173,89,37,.14),transparent 35%),linear-gradient(#181008,#080706)}.tc-sheet-x{position:absolute;right:9px;top:7px;border:0;background:transparent;color:#8a7b67;font-size:25px}.tc-contract-seal{width:66px;height:66px;display:grid;place-items:center;margin:0 auto 13px;border:1px solid #8b5b31;border-radius:50%;color:var(--ember);font-size:29px;box-shadow:0 0 28px rgba(202,104,41,.11)}.tc-contract-sheet h2{text-align:center;font:28px/1.02 Georgia,serif;margin:8px auto 16px;max-width:420px}.tc-contract-sheet>.tc-kicker{text-align:center}.tc-contract-facts{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid #392c20;border-bottom:1px solid #392c20;margin-bottom:13px}.tc-contract-facts div{display:grid;gap:4px;padding:10px}.tc-contract-facts div+div{border-left:1px solid #392c20}.tc-contract-facts span{font-size:7px;letter-spacing:.1em;text-transform:uppercase;color:#7f715e}.tc-contract-facts strong{font:13px Georgia,serif}.tc-contract-demand,.tc-contract-sanction{padding:13px;border:1px solid #594026;background:rgba(51,28,14,.36);margin:10px 0}.tc-contract-demand p,.tc-contract-sanction p{color:#d6c8b4;line-height:1.45;font-size:13px}.tc-contract-sanction>strong{display:block;font:20px Georgia,serif;color:#f0c27c;margin:5px 0}.tc-contract-note{text-align:center;margin:10px auto 13px;max-width:420px}
@media(max-width:430px){.tc-forge-favor{grid-template-columns:38px auto 1fr}.tc-contract-sheet h2{font-size:24px}.tc-contract-facts{grid-template-columns:1fr}.tc-contract-facts div+div{border-left:0;border-top:1px solid #392c20}}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

p.write_text(s)
