from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# This is a late visual layer only. It deliberately leaves encounter history,
# Ledger routing, details/open-close behavior, and every recorded field intact.
# Rebuilds remove the prior layer before reapplying it so this stays idempotent.
s=re.sub(
    r"\n?/\* --- Covenant Compendium dossier redesign --- \*/.*?"
    r"/\* --- End Covenant Compendium dossier redesign --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)
s=re.sub(
    r"\n?/\* --- Covenant Compendium dossier styles --- \*/.*?"
    r"/\* --- End Covenant Compendium dossier styles --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

css=r'''
/* --- Covenant Compendium dossier styles --- */
.tc-archive{padding:2px 0 18px}
.tc-archive-cover{position:relative;overflow:hidden;margin:7px 0 16px;padding:23px 19px 18px;border-top:1px solid rgba(198,161,90,.3);border-bottom:1px solid rgba(198,161,90,.22);background:radial-gradient(circle at 86% 16%,rgba(198,161,90,.10),transparent 28%),linear-gradient(135deg,rgba(28,24,17,.78),rgba(9,9,7,.5) 62%,rgba(20,17,12,.72));box-shadow:inset 0 1px rgba(255,255,255,.025)}
.tc-archive-cover:before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.18;background:repeating-linear-gradient(0deg,transparent 0 22px,rgba(198,161,90,.07) 22px 23px)}
.tc-archive-seal{position:absolute;right:13px;top:13px;width:62px;height:62px;border:1px solid rgba(198,161,90,.38);border-radius:50%;display:grid;place-items:center;font:700 25px/1 Georgia,serif;color:rgba(224,193,123,.55);transform:rotate(9deg);box-shadow:inset 0 0 0 4px rgba(198,161,90,.025)}
.tc-archive-kicker,.tc-dossier-file,.tc-dossier-region,.tc-dossier-label,.tc-evidence-kicker,.tc-archive-facts span{font:800 7px/1.25 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.13em}
.tc-archive-kicker{color:var(--gold);position:relative;z-index:1}.tc-archive-title{position:relative;z-index:1;max-width:78%;margin:7px 0 7px;font:400 clamp(31px,9vw,43px)/.96 Georgia,serif;color:var(--ink);text-wrap:balance}.tc-archive-copy{position:relative;z-index:1;max-width:86%;margin:0;color:#aaa18e;font:italic 11px/1.45 Georgia,serif}
.tc-archive-facts{position:relative;z-index:1;display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:16px;color:var(--ash)}.tc-archive-facts span strong{font:400 14px/1 Georgia,serif;color:var(--gold-bright);letter-spacing:0;margin-right:3px}.tc-archive-facts i{width:3px;height:3px;border-radius:50%;background:rgba(198,161,90,.55)}
.tc-dossier-stack{display:grid;gap:12px}.tc-dossier{position:relative;border:1px solid rgba(74,66,48,.68);background:linear-gradient(145deg,rgba(27,23,16,.9),rgba(9,9,7,.86));box-shadow:0 10px 30px rgba(0,0,0,.16),inset 0 1px rgba(255,255,255,.018);overflow:hidden}.tc-dossier.capstone{border-color:rgba(198,161,90,.46);box-shadow:0 11px 32px rgba(0,0,0,.18),inset 3px 0 rgba(198,161,90,.28)}.tc-dossier.legacy{opacity:.78}
.tc-dossier summary{list-style:none;cursor:pointer;position:relative;display:grid;grid-template-columns:42px minmax(0,1fr) 24px;gap:11px;align-items:stretch;min-height:128px;padding:0}.tc-dossier summary::-webkit-details-marker{display:none}.tc-dossier summary:after{content:"";position:absolute;left:42px;right:24px;bottom:0;height:1px;background:linear-gradient(90deg,rgba(198,161,90,.2),rgba(57,51,38,.45),transparent)}
.tc-dossier-spine{display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:11px 7px 10px;border-right:1px solid rgba(74,66,48,.6);background:linear-gradient(180deg,rgba(198,161,90,.055),rgba(0,0,0,.12))}.tc-dossier-file{writing-mode:vertical-rl;transform:rotate(180deg);color:#887e6b}.tc-dossier-stamp{font:800 6px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em;color:var(--gold);border:1px solid rgba(198,161,90,.38);padding:5px 3px;writing-mode:vertical-rl;transform:rotate(180deg)}
.tc-dossier-cover{min-width:0;padding:13px 0 13px}.tc-dossier-meta{display:flex;gap:7px;align-items:center;flex-wrap:wrap}.tc-dossier-region{color:var(--gold)}.tc-dossier-date{font:italic 9px/1.2 Georgia,serif;color:#7f7666}.tc-dossier-boss{margin:7px 0 9px;font:400 clamp(23px,6.8vw,31px)/1.02 Georgia,serif;color:var(--ink);text-wrap:balance}.tc-dossier-pair{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:7px;align-items:center}.tc-dossier-weapon{min-width:0}.tc-dossier-weapon small{display:block;margin-bottom:2px;font:800 6px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.09em;color:#756d5e}.tc-dossier-weapon strong{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font:400 11px/1.25 Georgia,serif;color:#c9bfaa}.tc-dossier-cross{color:#665d4d;font:italic 13px/1 Georgia,serif}.tc-dossier-flags{display:flex;gap:5px;flex-wrap:wrap;margin-top:10px}.tc-dossier-flag{padding:4px 6px;border:1px solid rgba(74,66,48,.58);font:800 6px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.07em;color:#938977;background:rgba(5,5,4,.2)}.tc-dossier-flag.gold{color:var(--gold);border-color:rgba(198,161,90,.28)}.tc-dossier-flag.red{color:#cc7b70;border-color:rgba(201,102,90,.29)}.tc-dossier-flag.violet{color:#ad98c0;border-color:rgba(151,128,173,.3)}
.tc-dossier-fold{display:grid;place-items:center;color:#8b816d;font-size:14px}.tc-dossier-fold:before{content:"⌄";transition:transform .18s ease}.tc-dossier[open] .tc-dossier-fold:before{transform:rotate(180deg)}
.tc-evidence{position:relative;padding:16px 14px 14px;background:linear-gradient(180deg,rgba(8,8,6,.72),rgba(15,13,9,.92));border-top:1px solid rgba(198,161,90,.12)}.tc-evidence:before{content:"ARCHIVED";position:absolute;right:13px;top:13px;font:900 18px/1 system-ui,sans-serif;letter-spacing:.08em;color:rgba(198,161,90,.045);transform:rotate(-7deg)}
.tc-evidence-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding-bottom:9px;margin-bottom:10px;border-bottom:1px solid rgba(74,66,48,.48)}.tc-evidence-kicker{color:var(--ash)}.tc-evidence-head em{font:italic 9px/1.3 Georgia,serif;color:#776e5f}
.tc-armament-record{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px}.tc-armament-slip{position:relative;min-width:0;padding:11px 10px 10px;border:1px solid rgba(74,66,48,.6);background:linear-gradient(145deg,rgba(29,25,18,.7),rgba(15,13,10,.6))}.tc-armament-slip:before{content:"";position:absolute;left:0;top:9px;bottom:9px;width:2px;background:rgba(198,161,90,.4)}.tc-dossier-label{color:#7e7565}.tc-armament-slip strong{display:block;margin:5px 0 3px;font:400 16px/1.08 Georgia,serif;color:var(--ink);overflow-wrap:anywhere}.tc-armament-slip em{display:block;font:italic 9px/1.25 Georgia,serif;color:#8f8573}
.tc-evidence-slip{position:relative;margin-top:8px;padding:11px 10px 10px 13px;border-left:2px solid #625947;background:linear-gradient(90deg,rgba(31,27,20,.48),rgba(13,12,9,.15))}.tc-evidence-slip.rite{border-left-color:rgba(151,128,173,.72)}.tc-evidence-slip.chaos{border-left-color:rgba(201,102,90,.72)}.tc-evidence-slip.penalties{border-left-color:rgba(201,102,90,.42)}.tc-evidence-slip.rewards{border-left-color:rgba(198,161,90,.72)}.tc-evidence-slip.quiet{opacity:.68}.tc-evidence-slip .tc-dossier-label{margin-bottom:4px}.tc-evidence-slip.rite .tc-dossier-label{color:#aa94be}.tc-evidence-slip.chaos .tc-dossier-label,.tc-evidence-slip.penalties .tc-dossier-label{color:#cc7e73}.tc-evidence-slip.rewards .tc-dossier-label{color:var(--gold)}.tc-evidence-slip strong{display:block;font:400 16px/1.15 Georgia,serif;color:var(--ink)}.tc-evidence-slip p{margin:5px 0 0;font:10.5px/1.42 Georgia,serif;color:#b9af9c}.tc-evidence-trigger{color:#8e8472!important;font-style:italic!important}.tc-penalty-line+ .tc-penalty-line{margin-top:7px;padding-top:7px;border-top:1px dashed rgba(120,104,77,.22)}
.tc-reward-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:7px}.tc-reward-tag{padding:5px 7px;border:1px solid rgba(198,161,90,.26);background:rgba(198,161,90,.045);font:800 7px/1.15 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.055em;color:#c5ab74}.tc-evidence-footer{display:flex;justify-content:space-between;gap:10px;align-items:flex-end;margin-top:12px;padding-top:10px;border-top:1px solid rgba(74,66,48,.46)}.tc-evidence-recorded{font:italic 9px/1.3 Georgia,serif;color:#817766}.tc-evidence-favor{text-align:right}.tc-evidence-favor span{display:block;font:800 6px/1.1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.1em;color:#736a5b}.tc-evidence-favor strong{display:block;margin-top:2px;font:400 18px/1 Georgia,serif;color:var(--gold-bright)}
.tc-dossier-legacy-note{padding:14px 13px 15px;font:italic 10.5px/1.45 Georgia,serif;color:#9e9584;background:rgba(5,5,4,.2)}
.tc-archive-empty{text-align:center;padding:18vh 24px 0}.tc-archive-empty-seal{width:70px;height:70px;margin:0 auto 14px;border:1px solid rgba(198,161,90,.28);border-radius:50%;display:grid;place-items:center;font-size:28px;color:rgba(198,161,90,.6)}
@media(max-width:390px){.tc-archive-title{max-width:74%}.tc-archive-copy{max-width:80%}.tc-dossier summary{grid-template-columns:36px minmax(0,1fr) 20px}.tc-dossier-spine{padding-left:5px;padding-right:5px}.tc-dossier summary:after{left:36px;right:20px}.tc-armament-record{grid-template-columns:1fr}.tc-dossier-boss{font-size:22px}.tc-dossier-weapon strong{font-size:10px}}
/* --- End Covenant Compendium dossier styles --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
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
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

required=[
  'function tcCompendiumRewardLabels(entry)',
  'function tcCompendiumDossierMarkup(entry,index,state)',
  'compendiumEntryMarkup=function(entry,index,state)',
  'compendiumLedgerMarkup=function(state)',
  'Office of Covenant Records',
  'Field Dossiers',
  'tc-armament-record',
  'Odd Rite · honored record',
  'Chaos seal · breached',
  'Armament censures',
  'Treasury issue',
  'Smithing Favor earned',
]
for needle in required:
  if needle not in s: raise SystemExit('Compendium dossier invariant missing: '+needle)

p.write_text(s)
print('Compendium redesigned as a full-function Covenant dossier archive.')
