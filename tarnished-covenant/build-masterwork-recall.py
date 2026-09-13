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

const tcSmithingLedgerBeforeMasterworkRecall=smithingLedgerMarkup;
smithingLedgerMarkup=function(state){
  const html=tcSmithingLedgerBeforeMasterworkRecall(state);
  return html.replace(/<div class="tc-master-list">[\s\S]*?<\/div>/,tcMasterworkArsenalMarkup(state));
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

p.write_text(s)
print('Masterwork Recall applied: exact owner-bound build, one use, no penalty, locked after first host-world clear.')
