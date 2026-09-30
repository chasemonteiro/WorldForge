from pathlib import Path
import re
p=Path('tarnished-covenant/index.html')
s=p.read_text()
s=re.sub(r"\n?/\* --- Appeal extra boss recording --- \*/.*?/\* --- End appeal extra boss recording --- \*/\n?","\n",s,flags=re.S)
s=re.sub(r"\n?/\* --- Appeal extra boss styles --- \*/.*?/\* --- End appeal extra boss styles --- \*/\n?","\n",s,flags=re.S)
css=r'''/* --- Appeal extra boss styles --- */
.tc-penalty-boss-record{margin-top:9px;padding:10px;border:1px solid rgba(198,161,90,.28);background:rgba(198,161,90,.05)}
.tc-penalty-boss-record strong{display:block;font-size:12px;color:var(--gold-bright);font-weight:400}.tc-penalty-boss-record span{display:block;margin-top:4px;color:var(--ash);font-size:10px;line-height:1.4}.tc-penalty-boss-record .btn{margin-top:8px}
/* --- End appeal extra boss styles --- */'''
s=s.replace('</style>',css+'\n</style>',1)
js=r'''/* --- Appeal extra boss recording --- */
function tcAppealPenaltyBossKills(state){return Array.isArray(state?.appealPenaltyBossKills)?state.appealPenaltyBossKills:[];}
function tcPenanceNeedsBossRecord(p){const t=`${p?.name||''} ${p?.text||''}`.toLowerCase();return t.includes('boss')&&(t.includes('kill')||t.includes('defeat')||t.includes('slay'));}
function tcPenanceBossRecord(state,p){return p?.bossRecord||tcAppealPenaltyBossKills(state).find(x=>x?.penanceId&&x.penanceId===p?.id)||null;}
const tcDefeatedBossNamesBeforeAppealRecord=defeatedBossNames;
defeatedBossNames=function(state,regionName=state.region){const out=tcDefeatedBossNamesBeforeAppealRecord(state,regionName);for(const x of tcAppealPenaltyBossKills(state)){if(x?.region===regionName&&x?.name)out.add(x.name);}return out;};
const tcLegacyErdtreeClearIdsBeforeAppealRecord=tcLegacyErdtreeClearIds;
tcLegacyErdtreeClearIds=function(state){const out=new Set(tcLegacyErdtreeClearIdsBeforeAppealRecord(state));for(const x of tcAppealPenaltyBossKills(state)){if(x?.erdtreeTargetId)out.add(x.erdtreeTargetId);}return [...out];};
function tcAppealBossChoices(state){
  const normal=(typeof tcEligibleFreeBossChoices==='function'?tcEligibleFreeBossChoices(state):[]).map(x=>({...x,type:'boss'}));
  const sm=smithingData(state||{}),avatars=[];
  if(Number(sm.erdtreeWrits||0)>0&&typeof TC_ERDTREE_TARGETS!=='undefined')for(const t of TC_ERDTREE_TARGETS){if(!tcErdtreeClearedIds(state).includes(t.id)&&tcErdtreeTargetAccessible(state,t))avatars.push({region:t.region,name:t.area,type:'erdtree',erdtreeTargetId:t.id,boss:t.boss});}
  return [...normal,...avatars];
}
function tcBuildAppealBossRecord(latest,encounterId,penanceId,choice,actor){
  const c=latest?.current;if(!c||c.id!==encounterId)return null;const i=(c.penances||[]).findIndex(p=>p.id===penanceId);if(i<0)return null;const p=c.penances[i];if(!tcPenanceNeedsBossRecord(p)||tcPenanceBossRecord(latest,p))return null;
  let next;
  if(choice.type==='erdtree'){
    next=tcBuildErdtreeWritSpend(latest,choice.erdtreeTargetId,actor);if(!next)return null;
  }else{
    if(!tcAppealBossChoices(latest).some(x=>x.type==='boss'&&x.region===choice.region&&x.name===choice.name))return null;
    next=smithingCopy(latest);
  }
  const record={penanceId,region:choice.region,name:choice.name,recordedBy:actor,recordedAt:new Date().toISOString(),source:'weapon-appeal',erdtreeTargetId:choice.erdtreeTargetId||null};
  const j=(next.current.penances||[]).findIndex(x=>x.id===penanceId);if(j<0)return null;next.current.penances[j].bossRecord=record;next.appealPenaltyBossKills=[...tcAppealPenaltyBossKills(next),record];next.lastAction=`${actor} recorded ${choice.name} in ${choice.region} for a Weapon Appeal extra-boss penalty.`;next.updatedAt=new Date().toISOString();return next;
}
function tcOpenAppealBossPicker(penanceId){
  const state=run?.state,c=state?.current,p=(c?.penances||[]).find(x=>x.id===penanceId);if(!p||!tcPenanceNeedsBossRecord(p))return;
  if(tcPenanceBossRecord(state,p))return setToast('That Appeal penalty already has a boss on file.');
  const choices=tcAppealBossChoices(state);if(!choices.length)return setToast('No eligible extra bosses are currently available.');
  const opts=choices.map((x,i)=>`<option value="${i}">${h(x.name)} · ${h(x.region)}${x.type==='erdtree'?' · spends 1 Erdtree Writ':''}</option>`).join('');
  const el=tcStrategicOverlay('Record Extra Boss Kill',`<p>Choose the boss actually killed to satisfy this Weapon Appeal penalty. Recording it removes that boss from future Covenant draws. Minor Erdtree Avatars require and consume an Erdtree Writ.</p><label class="label">boss killed</label><select id="tcAppealBossSelect">${opts}</select>`,`<div class="tc-strategy-actions"><button type="button" class="btn gold" id="tcConfirmAppealBoss">Record Boss</button></div>`);
  el.querySelector('#tcConfirmAppealBoss')?.addEventListener('click',async e=>{const choice=choices[Number(el.querySelector('#tcAppealBossSelect')?.value)];if(!choice)return;const actor=playerName(),encounterId=c.id,build=latest=>tcBuildAppealBossRecord(latest,encounterId,penanceId,choice,actor),staged=build(run.state);if(!staged)return setToast('That boss or penalty is no longer eligible.');e.currentTarget.disabled=true;const saved=await commit(staged,{successToast:`${choice.name} recorded for the Appeal penalty.`,retryBuilder:build});if(saved)el.remove();});
}
penanceMarkup=function(c){if(!c.penances?.length)return '';const state=run?.state;return `<section class="curse-section"><div class="section-kicker redtext">armament penalties</div><div class="curse-head"><span class="curse-glyphs">${'☠'.repeat(Math.min(c.penances.length,6))}</span><span>${c.penances.length} active ${c.penances.length===1?'punishment':'punishments'}</span></div>${c.penances.map((p,i)=>{const needs=tcPenanceNeedsBossRecord(p),rec=tcPenanceBossRecord(state,p);return `<div class="penance-item"><div class="scope">${h(personalizePlayers(p.scope,state))} · penalty ${i+1}</div><div class="penance-name">${h(p.name)}</div><div class="penance-text">${h(personalizePlayers(p.text,state))}</div>${needs?`<div class="tc-penalty-boss-record">${rec?`<strong>Extra boss recorded</strong><span>${h(rec.name)} · ${h(rec.region)}</span>`:`<strong>Extra boss still unrecorded</strong><span>Once you kill the required extra boss, put the specific kill on file.</span><button type="button" class="btn ghost small" data-record-appeal-boss="${h(p.id)}">Record Extra Boss Kill</button>`}</div>`:''}</div>`}).join('')}<div class="subtext">Penalties stack until the current target is defeated.</div></section>`;};
if(!window.__tcAppealBossRecordBound){window.__tcAppealBossRecordBound=true;document.addEventListener('click',e=>{const b=e.target.closest('[data-record-appeal-boss]');if(b)tcOpenAppealBossPicker(b.dataset.recordAppealBoss);});}
/* --- End appeal extra boss recording --- */'''
idx=s.rfind('</script>')
if idx<0:raise SystemExit('script marker missing')
s=s[:idx]+js+s[idx:]
for n in ['function tcPenanceNeedsBossRecord(p)','function tcBuildAppealBossRecord(latest,encounterId,penanceId,choice,actor)','Record Extra Boss Kill','appealPenaltyBossKills','Minor Erdtree Avatars require and consume an Erdtree Writ.']:
    if n not in s:raise SystemExit('appeal boss record invariant missing: '+n)
p.write_text(s)
print('Weapon Appeal extra-boss penalties now record a concrete shared boss kill and remove it from future draws.')
