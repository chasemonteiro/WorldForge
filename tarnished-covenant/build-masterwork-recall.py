from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Idempotent late layer: remove the generated recall runtime/styles before
# rebuilding them from the current production app.
s=re.sub(r"\n?/\* --- Masterwork veteran recall --- \*/.*?/\* --- End Masterwork veteran recall --- \*/\n?","\n",s,flags=re.S)
s=re.sub(r"\n?/\* --- Masterwork veteran recall styles --- \*/.*?/\* --- End Masterwork veteran recall styles --- \*/\n?","\n",s,flags=re.S)

css=r'''
/* --- Masterwork veteran recall styles --- */
.tc-veteran-arsenal{display:grid;gap:8px;margin-top:11px}.tc-veteran-card{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;padding:11px 10px;border:1px solid var(--line-soft);background:linear-gradient(145deg,rgba(28,24,17,.7),rgba(9,9,7,.45))}.tc-veteran-card.retired{opacity:.62}.tc-veteran-card.available{border-color:rgba(198,161,90,.38)}.tc-veteran-name{font:400 16px/1.1 Georgia,serif;color:var(--ink);margin:3px 0}.tc-veteran-meta{font:800 7px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em;color:var(--ash)}.tc-veteran-status{font:800 6px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.09em;color:var(--gold);margin-top:4px}.tc-veteran-card.retired .tc-veteran-status{color:#7f7666}.tc-veteran-card.current .tc-veteran-status{color:var(--violet)}.tc-veteran-recall{width:auto;min-width:92px;min-height:38px;padding:8px 9px;font-size:7px}.tc-veteran-legacy{padding:8px 9px;border-left:1px solid var(--line-soft);font:italic 9px/1.35 Georgia,serif;color:#887f70}
@media(max-width:390px){.tc-veteran-card{grid-template-columns:1fr}.tc-veteran-recall{width:100%}}
/* --- End Masterwork veteran recall styles --- */
'''
if '</style>' not in s:raise SystemExit('masterwork recall: style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Masterwork veteran recall --- */
const tcSmithingDataBeforeMasterworkRecall=smithingData;
smithingData=function(state){
  const base=tcSmithingDataBeforeMasterworkRecall(state),raw=state?.smithing||{};
  const recalls=Array.isArray(raw.masterworkRecalls)?raw.masterworkRecalls:[];
  return {...base,masterworkRecalls:recalls.filter(x=>x&&typeof x==='object').map(x=>({
    ...x,
    id:String(x.id||''),
    weapon:String(x.weapon||x.build?.name||''),
    owner:x.owner==='morgan'?'morgan':x.owner==='chase'?'chase':'',
    build:x.build&&typeof x.build==='object'?structuredClone(x.build):null,
    used:Boolean(x.used),
    masterworkedAt:x.masterworkedAt||null,
    recalledAt:x.recalledAt||null,
    recalledEncounterId:x.recalledEncounterId||null
  })).filter(x=>x.id&&x.weapon&&x.owner&&x.build)};
};

function tcMasterworkSlotForIdentity(identity=playerName()){
  const key=String(identity||'').trim().toLowerCase();
  if(key==='chase')return 'chase';
  if(key==='morgan')return 'morgan';
  return null;
}
function tcMasterworkRecallId(){return `mw-${Date.now()}-${Math.random().toString(36).slice(2,8)}`;}

// A Masterwork now archives the exact assigned build and grants that owner one
// future penalty-free Recall. The old masterworks string list stays intact for
// backwards compatibility and duplicate prevention.
masterworkCurrent=function(state,slot){
  if(slot!=='chase'&&slot!=='morgan')return null;
  const next=smithingCopy(state);
  if(next.smithing.masterworkCredits<1||!next.current)return null;
  const build=next.current?.[slot]?structuredClone(next.current[slot]):null,weapon=build?.name;
  if(!weapon)return null;
  if(next.smithing.masterworks.includes(weapon)){
    setToast(`${weapon} is already Masterworked.`);
    return null;
  }
  next.smithing.masterworks.push(weapon);
  next.smithing.masterworkRecalls.push({
    id:tcMasterworkRecallId(),weapon,owner:slot,build,used:false,
    masterworkedAt:new Date().toISOString(),recalledAt:null,recalledEncounterId:null
  });
  next.smithing.masterworkCredits-=1;
  next.lastAction=`Hewg has Masterworked ${weapon}. One veteran Recall is now available to ${playerLabel(slot,next)}.`;
  return next;
};

function tcBuildMasterworkRecall(latest,encounterId,recordId,expectedCurrentWeapon,slot,actor){
  const c=latest?.current;
  if(!c||c.id!==encounterId||!recordId||(slot!=='chase'&&slot!=='morgan'))return null;
  if(typeof tcEncounterMutationLocked==='function'&&tcEncounterMutationLocked(latest))return null;
  const sm=smithingData(latest),record=sm.masterworkRecalls.find(x=>x.id===recordId);
  if(!record||record.used||record.owner!==slot||!record.build?.name)return null;
  if(String(c?.[slot]?.name||'')!==String(expectedCurrentWeapon||''))return null;
  if(String(c?.[slot]?.name||'')===String(record.weapon||''))return null;
  const next=smithingCopy(latest),saved=next.smithing.masterworkRecalls.find(x=>x.id===recordId);
  if(!saved||saved.used)return null;
  next.current[slot]=structuredClone(saved.build);
  saved.used=true;
  saved.recalledAt=new Date().toISOString();
  saved.recalledEncounterId=encounterId;
  next.lastAction=`${actor} recalled ${saved.weapon} from the veteran arsenal for ${playerLabel(slot,next)}. The Masterwork is now retired.`;
  next.updatedAt=new Date().toISOString();
  return next;
}

function tcMasterworkArsenalMarkup(state){
  const sm=smithingData(state),records=sm.masterworkRecalls||[],me=tcMasterworkSlotForIdentity(),locked=typeof tcEncounterMutationLocked==='function'&&tcEncounterMutationLocked(state),c=state?.current;
  const recordedNames=new Set(records.map(x=>x.weapon));
  const legacy=(sm.masterworks||[]).filter(name=>!recordedNames.has(name));
  const cards=records.map(record=>{
    const ownerLabel=playerLabel(record.owner,state),currentName=String(c?.[record.owner]?.name||''),isCurrent=currentName===record.weapon;
    const canUse=Boolean(!record.used&&!locked&&c&&me===record.owner&&!isCurrent);
    const status=record.used?'RECALLED / RETIRED':isCurrent?'CURRENTLY ASSIGNED':locked?'LOCKED AFTER 1/2 CLEAR':'RECALL AVAILABLE';
    const cls=record.used?'retired':isCurrent?'current':canUse?'available':'';
    return `<div class="tc-veteran-card ${cls}"><div><div class="tc-veteran-meta">${h(ownerLabel)} · Veteran Arsenal</div><div class="tc-veteran-name">⚒ ${h(record.weapon)}</div><div class="tc-veteran-status">${status}</div></div>${canUse?`<button type="button" class="btn ghost tc-veteran-recall" data-masterwork-recall="${h(record.id)}" data-owner="${record.owner}">Recall · 1 Use</button>`:''}</div>`;
  });
  legacy.forEach(name=>cards.push(`<div class="tc-veteran-card retired"><div><div class="tc-veteran-meta">Legacy Masterwork</div><div class="tc-veteran-name">⚒ ${h(name)}</div><div class="tc-veteran-status">VETERAN RECORD</div></div><div class="tc-veteran-legacy">This Masterwork predates Recall records.</div></div>`));
  return `<div class="tc-master-list tc-veteran-arsenal">${cards.length?cards.join(''):'<span class="tc-muted">No veteran weapons yet.</span>'}</div>`;
}



function tcWeaponRecallChoices(state,slot){
  return (smithingData(state).masterworkRecalls||[]).filter(record=>record.owner===slot&&!record.used&&record.weapon!==state.current?.[slot]?.name);
}
function tcMountWeaponRecall(weaponPanel){
  if(weaponPanel.querySelector('[data-open-weapon-recall]'))return;
  const state=run?.state,slot=tcMasterworkSlotForIdentity();if(!state?.current||!slot)return;
  const count=tcWeaponRecallChoices(state,slot).length,locked=tcEncounterMutationLocked(state);
  const button=document.createElement('button');button.type='button';button.className='btn ghost small';button.dataset.openWeaponRecall='1';
  button.textContent=`Masterwork Recall · ${count}`;
  button.style.cssText='min-height:44px;margin-top:8px;width:100%;white-space:normal';
  button.addEventListener('click',tcOpenWeaponRecall);
  (weaponPanel.querySelector('.tc-weapon-appeal-actions')||weaponPanel).appendChild(button);
  if(locked){const note=document.createElement('div');note.className='tc-muted';note.textContent='Recall locked after a world clear';button.after(note);}
}
function tcOpenWeaponRecall(){
  const state=run?.state,c=state?.current,slot=tcMasterworkSlotForIdentity();if(!c||!slot)return;
  const items=tcWeaponRecallChoices(state,slot),locked=tcEncounterMutationLocked(state),encounterId=c.id,expected=String(c[slot]?.name||'');
  const el=tcStrategicOverlay('Masterwork Recall',`<p>Replace <strong>${h(playerLabel(slot,state))}’s ${h(expected)}</strong> with one of your Masterworks. No Appeal penalty or Masterwork credit cost. Each Recall can be used once.</p>${locked?`<p>${h(tcEncounterMutationLockMessage())}</p>`:''}<div class="tc-strategy-list">${items.length?items.map((record,i)=>`<div class="tc-panel soft"><strong>${h(record.weapon)}</strong><button type="button" class="btn ghost" data-weapon-recall-choice="${i}" ${locked?'disabled':''}>Swap to this weapon · Use Recall</button></div>`).join(''):'<p>No available Masterwork Recalls for your weapon. Masterwork a weapon from the victory report or Hewg’s Workbench to add one.</p>'}</div>`);
  let busy=false;
  el.querySelectorAll('[data-weapon-recall-choice]').forEach(button=>button.addEventListener('click',async()=>{
    if(busy||pending)return;
    const record=items[Number(button.dataset.weaponRecallChoice)],actor=playerName();
    if(tcMasterworkSlotForIdentity(actor)!==slot)return;
    const build=latest=>tcBuildMasterworkRecall(latest,encounterId,record.id,expected,slot,actor),next=build(run.state);
    if(!next){el.remove();tcOpenWeaponRecall();return setToast('The encounter or Recall changed. Please check again.');}
    busy=true;button.disabled=true;
    try{const saved=await commit(next,{successToast:`${record.weapon} recalled. No Appeal penalty.`,retryBuilder:build});if(saved){el.remove();uiScreen='encounter';renderRun();}}
    finally{busy=false;if(button.isConnected)button.disabled=false;}
  }));
}

function tcPastMasterworkWeapons(state,slot){
  if(!['chase','morgan'].includes(slot))return [];
  const seen=new Set(),items=[];
  for(const entry of state.history||[]){
    const weapon=entry[slot+'Weapon'];
    if(typeof weapon!=='string'||!weapon.trim()||seen.has(weapon))continue;
    seen.add(weapon);items.push({weapon,boss:entry.name||'Completed encounter'});
  }
  return items;
}
function tcBuildPastMasterwork(latest,slot,weapon,actor){
  if(slot!==tcMasterworkSlotForIdentity(actor))return null;
  const sm=smithingData(latest);
  if(Number(sm.masterworkCredits||0)<1||sm.masterworks.includes(weapon)||!tcPastMasterworkWeapons(latest,slot).some(item=>item.weapon===weapon))return null;
  const next=smithingCopy(latest);
  next.smithing.masterworkCredits-=1;
  next.smithing.masterworks.push(weapon);
  next.smithing.masterworkRecalls.push({id:tcMasterworkRecallId(),weapon,owner:slot,build:{name:weapon},used:false,masterworkedAt:new Date().toISOString(),recalledAt:null,recalledEncounterId:null});
  next.lastAction=`${actor} Masterworked ${weapon} from a past encounter. One penalty-free Recall is available.`;
  next.updatedAt=new Date().toISOString();
  return next;
}
function tcOpenPastMasterwork(){
  const state=run?.state,slot=tcMasterworkSlotForIdentity();if(!state||!slot)return;
  const sm=smithingData(state),items=tcPastMasterworkWeapons(state,slot);
  const el=tcStrategicOverlay('Masterwork a Past Weapon',`<p>Choose a weapon you used in a completed encounter. Costs 1 Masterwork credit and grants you one future penalty-free Recall.</p><p><strong>${Number(sm.masterworkCredits||0)} credits available</strong></p><div class="tc-strategy-list">${items.length?items.map((item,i)=>`<div class="tc-panel soft"><strong>${h(item.weapon)}</strong><div class="tc-muted">Used against ${h(item.boss)}</div><button type="button" class="btn ghost" data-past-masterwork="${i}" ${sm.masterworkCredits<1||sm.masterworks.includes(item.weapon)?'disabled':''}>${sm.masterworks.includes(item.weapon)?'Already Masterworked':sm.masterworkCredits<1?'No credits available':'Masterwork · 1 credit'}</button></div>`).join(''):'<p>Your weapons will appear here after you complete an encounter.</p>'}</div>`);
  let busy=false;
  el.querySelectorAll('[data-past-masterwork]').forEach(btn=>btn.addEventListener('click',async()=>{
    if(busy||pending)return;
    const weapon=items[Number(btn.dataset.pastMasterwork)]?.weapon,actor=playerName();
    const build=latest=>tcBuildPastMasterwork(latest,slot,weapon,actor),next=build(run.state);
    if(!next){el.remove();tcOpenPastMasterwork();return setToast('Credits or weapon availability changed.');}
    busy=true;btn.disabled=true;
    try{const saved=await commit(next,{successToast:`${weapon} Masterworked.`,retryBuilder:build});if(saved){el.remove();ledgerView='smithing';uiScreen='ledger';renderRun();}}
    finally{busy=false;if(btn.isConnected)btn.disabled=false;}
  }));
}
document.addEventListener('click',event=>{if(event.target.closest('[data-open-past-masterwork]'))tcOpenPastMasterwork();});

const tcSmithingLedgerBeforeMasterworkRecall=smithingLedgerMarkup;
smithingLedgerMarkup=function(state){
  const html=tcSmithingLedgerBeforeMasterworkRecall(state);
  return html.replace(/<div class="tc-master-list">[\s\S]*?<\/div>/,tcMasterworkArsenalMarkup(state)+`<button type="button" class="btn gold" data-open-past-masterwork>Masterwork a Past Weapon · 1 credit</button>`);
};

document.addEventListener('click',async event=>{
  const btn=event.target.closest('[data-masterwork-recall]');if(!btn)return;
  event.preventDefault();
  const state=run?.state,c=state?.current,slot=btn.dataset.owner,me=tcMasterworkSlotForIdentity();
  if(!c||!slot||slot!==me)return setToast('Only the Tarnished who Masterworked this weapon may Recall it.');
  if(typeof tcEncounterMutationLocked==='function'&&tcEncounterMutationLocked(state))return setToast(tcEncounterMutationLockMessage());
  const recordId=btn.dataset.masterworkRecall,expectedCurrentWeapon=String(c?.[slot]?.name||''),encounterId=c.id,actor=playerName();
  const build=latest=>tcBuildMasterworkRecall(latest,encounterId,recordId,expectedCurrentWeapon,slot,actor),staged=build(state);
  if(!staged)return setToast('That veteran Recall is no longer available.');
  btn.disabled=true;
  const saved=await commit(staged,{successToast:'Veteran weapon recalled. This Masterwork is now retired.',retryBuilder:build});
  if(saved){ledgerView='smithing';uiScreen='ledger';renderRun();}
  else btn.disabled=false;
});
/* --- End Masterwork veteran recall --- */
'''
idx=s.rfind('</script>')
if idx<0:raise SystemExit('masterwork recall: script marker missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in [
  'masterworkRecalls:recalls.filter',
  'function tcBuildMasterworkRecall(latest,encounterId,recordId,expectedCurrentWeapon,slot,actor)',
  'One veteran Recall is now available',
  'RECALL AVAILABLE',
  'RECALLED / RETIRED',
  "retryBuilder:build",
]:
  if needle not in s:raise SystemExit('masterwork recall invariant missing: '+needle)

# Mount beside Weapon Appeal; guard keeps repeated builds idempotent.
mount="if(actions3||appealConfirm)weaponPanel.appendChild(appealBar);"
if "tcMountWeaponRecall(weaponPanel);" not in s:
    if mount not in s:raise SystemExit('weapon recall mount missing')
    s=s.replace(mount,mount+"tcMountWeaponRecall(weaponPanel);",1)

p.write_text(s)
print('Masterwork Recall applied: exact owner-bound build, one use, no penalty, locked after first host-world clear.')
