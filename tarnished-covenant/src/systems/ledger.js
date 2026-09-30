/* --- Covenant Compendium dossier redesign --- */
function tcCompendiumRewardLabels(entry){
  const rewards=Array.isArray(entry?.rewards)?entry.rewards:[];
  return rewards.map(reward=>{
    if(typeof reward==='string')return reward;
    return reward?.label||reward?.name||reward?.kind||'Covenant reward';
  }).filter(Boolean);
}
function tcCompendiumEntryNumber(index,state){
  const total=Array.isArray(state?.history)?state.history.length:0;
  return String(Math.max(1,total-index)).padStart(2,'0');
}
function tcCompendiumDossierMarkup(entry,index,state){
  const names=compendiumNames(entry,state);
  const rich=Boolean(entry?.chaseWeapon||entry?.morganWeapon||entry?.oddRite||entry?.chaosTrigger||entry?.penances?.length||entry?.rewards?.length);
  const penalties=Array.isArray(entry?.penances)?entry.penances:[];
  const rewards=tcCompendiumRewardLabels(entry);
  const favor=Math.max(0,Number(entry?.favorEarned||0));
  const date=compendiumDate(entry?.completedAt);
  const number=tcCompendiumEntryNumber(index,state);
  const capstone=Boolean(entry?.exit);
  const chaosTriggered=Boolean(entry?.chaosTriggered);
  const status=capstone?'CAPSTONE':rich?'FELLED':'LEGACY';
  const recordedBy=entry?.completedBy?personalizePlayers(entry.completedBy,{playerNames:[names.chase,names.morgan]}):'the Covenant';
  const pairing=`<div class="tc-dossier-pair"><div class="tc-dossier-weapon"><small>${h(names.chase)}</small><strong>${h(entry?.chaseWeapon||'Unknown armament')}</strong></div><div class="tc-dossier-cross">×</div><div class="tc-dossier-weapon"><small>${h(names.morgan)}</small><strong>${h(entry?.morganWeapon||'Unknown armament')}</strong></div></div>`;
  const flags=[
    favor?`<span class="tc-dossier-flag gold">+${favor} Favor</span>`:'',
    entry?.oddRite?`<span class="tc-dossier-flag violet">Rite filed</span>`:'',
    chaosTriggered?`<span class="tc-dossier-flag red">Chaos breach</span>`:'',
    penalties.length?`<span class="tc-dossier-flag red">${penalties.length} ${penalties.length===1?'penalty':'penalties'}</span>`:'',
    rewards.length?`<span class="tc-dossier-flag gold">${rewards.length} ${rewards.length===1?'reward':'rewards'}</span>`:''
  ].filter(Boolean).join('');
  if(!rich){
    return `<details class="tc-dossier legacy"><summary><div class="tc-dossier-spine"><span class="tc-dossier-file">FILE ${number}</span><span class="tc-dossier-stamp">${status}</span></div><div class="tc-dossier-cover"><div class="tc-dossier-meta"><span class="tc-dossier-region">${h(entry?.region||'Earlier run')}</span>${date?`<span class="tc-dossier-date">${h(date)}</span>`:''}</div><div class="tc-dossier-boss">${h(entry?.name||'Unknown foe')}</div><div class="tc-dossier-flags"><span class="tc-dossier-flag">Partial archive</span></div></div><div class="tc-dossier-fold" aria-hidden="true"></div></summary><div class="tc-dossier-legacy-note">This victory predates the full Compendium record. The Covenant remembers the corpse, but the armaments, Rite, Chaos state, penalties, and treasury filing were not preserved.</div></details>`;
  }
  return `<details class="tc-dossier ${capstone?'capstone':''}"><summary><div class="tc-dossier-spine"><span class="tc-dossier-file">FILE ${number}</span><span class="tc-dossier-stamp">${status}</span></div><div class="tc-dossier-cover"><div class="tc-dossier-meta"><span class="tc-dossier-region">${h(entry?.region||'Unknown region')}</span>${date?`<span class="tc-dossier-date">${h(date)}</span>`:''}</div><div class="tc-dossier-boss">${h(entry?.name||'Unknown foe')}</div>${pairing}${flags?`<div class="tc-dossier-flags">${flags}</div>`:''}</div><div class="tc-dossier-fold" aria-hidden="true"></div></summary>
    <div class="tc-evidence">
      <div class="tc-evidence-head"><span class="tc-evidence-kicker">Filed encounter evidence</span><em>Record ${number} · ${h(entry?.region||'Unknown region')}</em></div>
      <div class="tc-armament-record">
        <div class="tc-armament-slip"><span class="tc-dossier-label">${h(names.chase)} · assigned armament</span><strong>${h(entry?.chaseWeapon||'—')}</strong>${entry?.chaseBuild?.role?`<em>${h(entry.chaseBuild.role)}</em>`:''}</div>
        <div class="tc-armament-slip"><span class="tc-dossier-label">${h(names.morgan)} · assigned armament</span><strong>${h(entry?.morganWeapon||'—')}</strong>${entry?.morganBuild?.role?`<em>${h(entry.morganBuild.role)}</em>`:''}</div>
      </div>
      ${entry?.oddRite?`<div class="tc-evidence-slip rite"><span class="tc-dossier-label">Odd Rite · honored record</span><strong>${h(entry.oddRite.name||'Unnamed Rite')}</strong><p>${h(entry.oddRite.text||'')}</p></div>`:''}
      ${chaosTriggered?`<div class="tc-evidence-slip chaos"><span class="tc-dossier-label">Chaos seal · breached</span><strong>${h(typeof chaosEventName==='function'?chaosEventName(entry?.chaosConsequence||'Chaos'):'Chaos')}</strong>${entry?.chaosTrigger?`<p class="tc-evidence-trigger">Trigger: ${h(entry.chaosTrigger)}</p>`:''}<p>${h(personalizePlayers(entry?.chaosConsequence||'The seal broke. Details lost to history.',{playerNames:[names.chase,names.morgan]}))}</p></div>`:`<div class="tc-evidence-slip quiet"><span class="tc-dossier-label">Chaos seal · intact</span><strong>No breach recorded</strong>${entry?.chaosTrigger?`<p class="tc-evidence-trigger">Trigger watched: ${h(entry.chaosTrigger)}</p>`:''}</div>`}
      ${penalties.length?`<div class="tc-evidence-slip penalties"><span class="tc-dossier-label">Armament censures · ${penalties.length}</span>${penalties.map(x=>`<p class="tc-penalty-line"><b>${h(x?.name||'Penalty')}</b> · ${h(personalizePlayers(x?.text||'',{playerNames:[names.chase,names.morgan]}))}</p>`).join('')}</div>`:''}
      ${rewards.length?`<div class="tc-evidence-slip rewards"><span class="tc-dossier-label">Treasury issue</span><div class="tc-reward-tags">${rewards.map(label=>`<span class="tc-reward-tag">${h(label)}</span>`).join('')}</div></div>`:''}
      <div class="tc-evidence-footer"><div class="tc-evidence-recorded">Recorded by ${h(recordedBy)}${date?` · ${h(date)}`:''}</div><div class="tc-evidence-favor"><span>Smithing Favor earned</span><strong>${favor?`+${favor}`:'—'}</strong></div></div>
    </div>
  </details>`;
}
compendiumEntryMarkup=function(entry,index,state){return tcCompendiumDossierMarkup(entry,index,state);};
compendiumLedgerMarkup=function(state){
  const entries=Array.isArray(state?.history)?state.history:[];
  if(!entries.length)return `<div class="tc-archive-empty"><div class="tc-archive-empty-seal">◇</div><div class="tc-value">The archive is empty.</div><div class="tc-muted">The first completed Covenant encounter will open a case file here.</div></div>`;
  const chaosCount=entries.filter(x=>x?.chaosTriggered).length;
  const favor=entries.reduce((sum,x)=>sum+Math.max(0,Number(x?.favorEarned||0)),0);
  const capstones=entries.filter(x=>x?.exit).length;
  const full=entries.filter(x=>x?.chaseWeapon||x?.morganWeapon||x?.oddRite||x?.chaosTrigger).length;
  return `<div class="tc-archive"><div class="tc-archive-cover"><div class="tc-archive-seal">✦</div><div class="tc-archive-kicker">Office of Covenant Records</div><div class="tc-archive-title">Field Dossiers</div><p class="tc-archive-copy">The run as evidence: every foe, cursed pairing, Rite, Chaos breach, censure, reward, and scrap of Favor preserved in the order it happened.</p><div class="tc-archive-facts"><span><strong>${entries.length}</strong> cases</span><i></i><span><strong>${capstones}</strong> capstones</span><i></i><span><strong>${chaosCount}</strong> chaos breaches</span><i></i><span><strong>${favor}</strong> Favor</span><i></i><span><strong>${full}</strong> full records</span></div></div><div class="tc-dossier-stack">${entries.map((entry,index)=>tcCompendiumDossierMarkup(entry,index,state)).join('')}</div></div>`;
};
/* --- End Covenant Compendium dossier redesign --- */