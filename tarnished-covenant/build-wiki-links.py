from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Keep this patch idempotent across rebuilds.
s=re.sub(r"\n?/\* --- Contextual Elden Ring wiki links --- \*/.*?/\* --- End contextual Elden Ring wiki links --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Contextual wiki link styles --- \*/.*?/\* --- End contextual wiki link styles --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Grace office workstation behavior --- \*/.*?/\* --- End Grace office workstation behavior --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Grace office workstation styles --- \*/.*?/\* --- End Grace office workstation styles --- \*/\n?", "\n", s, flags=re.S)

css=r'''
/* --- Contextual wiki link styles --- */
.tc-wiki-link{display:inline-flex;align-items:center;gap:4px;color:var(--gold-bright);text-decoration:none;border-bottom:1px solid rgba(224,193,123,.34);padding:5px 1px 4px;font:800 8px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.10em;white-space:nowrap;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.tc-wiki-link:active{opacity:.68}.tc-wiki-boss{margin-top:7px}.tc-wiki-weapon{margin:0 0 8px}.tc-grace-target .tc-wiki-link{margin-top:7px}.tc-comp-sheet .tc-wiki-boss{margin:1px 0 14px}.tc-comp-sheet .tc-wiki-weapon{margin:1px 0 7px}
.tc-grace-wiki-target{margin:7px 8px 0;padding:9px 10px 8px;border-top:1px solid var(--line-soft);border-bottom:1px solid var(--line-soft);text-align:center;background:linear-gradient(90deg,transparent,rgba(198,161,90,.045),transparent);flex:0 0 auto}
.tc-grace-wiki-name{font:400 clamp(18px,5.2vw,24px)/1.08 Georgia,serif;color:var(--ink);margin:4px 0 1px;text-wrap:balance}
.tc-grace-wiki-target .tc-kicker{color:var(--gold)}
.tc-grace-ar-tools{margin:7px 8px 0;padding:9px 10px;border:1px solid rgba(198,161,90,.25);background:linear-gradient(180deg,rgba(198,161,90,.06),rgba(8,8,6,.24));text-align:center;flex:0 0 auto}
.tc-grace-ar-title{font:850 8px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.13em;color:var(--gold);margin-bottom:5px}
.tc-grace-ar-weapons{display:grid;gap:2px;margin:0 0 7px;font:400 13px/1.15 Georgia,serif;color:var(--ink)}
.tc-grace-ar-weapons span{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tc-grace-ar-button{display:flex;align-items:center;justify-content:center;width:100%;min-height:36px;padding:8px 10px;border:1px solid rgba(224,193,123,.48);background:linear-gradient(180deg,rgba(198,161,90,.14),rgba(94,72,34,.08));color:var(--gold-bright);text-decoration:none;font:850 9px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.10em;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.tc-grace-ar-button:active{opacity:.72}

/* Grace is a one-screen pre-fight workstation. The old giant branding block is
   intentionally hidden after IA has used it to construct the panel. */
.tc-sanctuary-panel[data-panel="grace"]{overflow-y:hidden!important;padding-bottom:8px!important}
.tc-sanctuary-panel[data-panel="grace"]>.tc-rune,
.tc-sanctuary-panel[data-panel="grace"]>.tc-title,
.tc-sanctuary-panel[data-panel="grace"]>.tc-subtitle{display:none!important}
.tc-grace-office-memo{margin:4px 8px 8px;padding:9px 12px 10px;border-top:1px solid rgba(198,161,90,.25);border-bottom:1px solid rgba(198,161,90,.18);background:linear-gradient(90deg,transparent,rgba(198,161,90,.055),transparent);text-align:center;flex:0 0 auto}
.tc-grace-office-label{font:850 8px/1.1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.16em;color:var(--gold);margin-bottom:5px}
.tc-grace-office-copy{font:italic 12px/1.32 Georgia,serif;color:#cfc5b2;max-width:560px;margin:auto;text-wrap:balance}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-art{height:min(24svh,185px)!important;min-height:125px!important;margin:6px 0 7px!important;flex:0 1 auto}
@media(max-height:760px){
  .tc-grace-office-memo{padding:7px 10px;margin-top:2px;margin-bottom:5px}.tc-grace-office-copy{font-size:10.5px}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-art{height:18svh!important;min-height:100px!important;margin:4px 0 5px!important}
  .tc-grace-wiki-target{margin-top:4px;padding-top:6px;padding-bottom:6px}.tc-grace-ar-tools{margin-top:4px;padding-top:6px;padding-bottom:6px}
}
/* --- End contextual wiki link styles --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Contextual Elden Ring wiki links --- */
const TC_WIKI_BASE='https://eldenring.wiki.gg/wiki/';
const TC_AR_CALCULATOR='https://www.tarnished.dev/weapon-calculator';
const TC_GRACE_MEMOS=[
  'Death remains an unexcused absence unless accompanied by a Site of Grace.',
  'Finger guidance is advisory. Liability remains with the Tarnished.',
  'Management has reviewed your rune loss and elected not to comment.',
  'All demigod disputes must be resolved off company time.',
  'Flasks are classified as personal protective equipment. Refill accordingly.',
  'The Erdtree cannot currently accommodate your request for flexible scheduling.',
  'Repeated exposure to Scarlet Rot may affect eligibility for remote work.',
  'Please direct all complaints regarding gravity to the appropriate regional authority.',
  'Rune recovery remains the sole responsibility of the employee.',
  'Torrent is not approved for indoor use, regardless of operational urgency.',
  'Grace has been extended as a courtesy and should not be interpreted as job security.',
  'Any resemblance between this assignment and a reasonable workload is coincidental.'
];
function tcWikiTitle(name,kind='boss'){
  let out=String(name||'').trim().replace(/[’‘]/g,"'").replace(/[–—]/g,'-');
  if(kind==='boss')out=out.replace(/\s*\([^)]*\)\s*$/,'').trim();
  return out;
}
function tcWikiUrl(name,kind='boss'){
  const title=tcWikiTitle(name,kind);if(!title)return '';
  return TC_WIKI_BASE+encodeURIComponent(title.replace(/\s+/g,'_'));
}
function tcWikiAnchor(name,kind,label){
  const url=tcWikiUrl(name,kind);if(!url)return null;
  const a=document.createElement('a');
  a.className=`tc-wiki-link ${kind==='weapon'?'tc-wiki-weapon':'tc-wiki-boss'}`;
  a.href=url;a.target='_blank';a.rel='noopener noreferrer external';a.textContent=`${label||'WIKI'} ↗`;
  a.dataset.tcWiki='1';
  a.addEventListener('click',e=>e.stopPropagation());
  return a;
}
function tcCurrentWeaponNames(){
  const c=run?.state?.current;
  return [c?.chase?.name,c?.morgan?.name].filter(Boolean);
}
function tcBuildArTools(){
  const weapons=tcCurrentWeaponNames();
  const box=document.createElement('div');box.className='tc-grace-ar-tools';
  const names=weapons.length?weapons.map(name=>`<span>${h(name)}</span>`).join(''):'<span>Current assigned weapons</span>';
  box.innerHTML=`<div class="tc-grace-ar-title">pre-fight buildcraft</div><div class="tc-grace-ar-weapons">${names}</div><a class="tc-grace-ar-button" href="${TC_AR_CALCULATOR}" target="_blank" rel="noopener noreferrer external">Weapon AR Calculator ↗</a>`;
  box.querySelector('a')?.addEventListener('click',e=>e.stopPropagation());
  return box;
}
function tcGraceMemoForState(state){
  const seed=String(state?.current?.id||state?.current?.target?.name||state?.region||'grace');
  let hash=0;for(let i=0;i<seed.length;i++)hash=((hash<<5)-hash+seed.charCodeAt(i))|0;
  return TC_GRACE_MEMOS[Math.abs(hash)%TC_GRACE_MEMOS.length];
}
function tcDecorateGraceOffice(gracePanel){
  if(!gracePanel)return;
  const text=tcGraceMemoForState(run?.state);
  let memo=gracePanel.querySelector('.tc-grace-office-memo');
  if(!memo){
    memo=document.createElement('div');memo.className='tc-grace-office-memo';
    const art=gracePanel.querySelector('.tc-grace-art');
    if(art)art.insertAdjacentElement('beforebegin',memo);else gracePanel.appendChild(memo);
  }
  if(memo.dataset.memo!==text){
    memo.dataset.memo=text;
    memo.innerHTML=`<div class="tc-grace-office-label">Covenant Office Memorandum</div><div class="tc-grace-office-copy">${h(text)}</div>`;
  }
  gracePanel.scrollTop=0;
}
function tcDecorateGraceWiki(){
  const target=run?.state?.current?.target?.name;if(!target)return;
  const gracePanel=document.querySelector('.tc-sanctuary-panel[data-panel="grace"]');
  tcDecorateGraceOffice(gracePanel);
  if(gracePanel&&!gracePanel.querySelector('.tc-grace-wiki-target')){
    const box=document.createElement('div');box.className='tc-grace-wiki-target';
    box.innerHTML=`<div class="tc-kicker">current target</div><div class="tc-grace-wiki-name">${h(target)}</div>`;
    const a=tcWikiAnchor(target,'boss','Boss wiki');if(a)box.appendChild(a);
    const art=gracePanel.querySelector('.tc-grace-art');(art||gracePanel.lastElementChild)?.insertAdjacentElement('afterend',box);
  }
  if(gracePanel&&!gracePanel.querySelector('.tc-grace-ar-tools')){
    const targetBox=gracePanel.querySelector('.tc-grace-wiki-target');
    const tools=tcBuildArTools();
    (targetBox||gracePanel.lastElementChild)?.insertAdjacentElement('afterend',tools);
  }
  const dashboardName=document.querySelector('.tc-grace-target-name');
  if(dashboardName&&!dashboardName.parentElement.querySelector(':scope > .tc-wiki-link')){
    const a=tcWikiAnchor(target,'boss','Boss wiki');if(a)dashboardName.insertAdjacentElement('afterend',a);
  }
  const dashboardPanel=dashboardName?.closest('.tc-sanctuary-panel,.tc-screen');
  if(dashboardPanel&&!dashboardPanel.querySelector('.tc-grace-ar-tools')){
    const tools=tcBuildArTools();dashboardName.closest('.tc-grace-target')?.insertAdjacentElement('afterend',tools);
  }
  if(!gracePanel){
    const art=document.querySelector('.tc-screen .tc-grace-art');
    if(art&&!art.parentElement.querySelector('.tc-grace-wiki-target')){
      const box=document.createElement('div');box.className='tc-grace-wiki-target';
      box.innerHTML=`<div class="tc-kicker">current target</div><div class="tc-grace-wiki-name">${h(target)}</div>`;
      const a=tcWikiAnchor(target,'boss','Boss wiki');if(a)box.appendChild(a);art.insertAdjacentElement('afterend',box);
    }
    const screen=art?.closest('.tc-screen');
    if(screen&&!screen.querySelector('.tc-grace-ar-tools')){
      const targetBox=screen.querySelector('.tc-grace-wiki-target');if(targetBox)targetBox.insertAdjacentElement('afterend',tcBuildArTools());
    }
  }
}
function tcDecorateEncounterWiki(){
  const target=run?.state?.current?.target?.name;
  const head=document.querySelector('.tc-encounter-panel[data-panel="boss"] .tc-brief-head,.tc-brief-head');
  if(target&&head&&!head.querySelector('.tc-wiki-link')){
    const a=tcWikiAnchor(target,'boss','Boss wiki');if(a)head.appendChild(a);
  }
  document.querySelectorAll('.tc-encounter-panel[data-panel="weapons"] .tc-loadout,.tc-loadout').forEach(card=>{
    if(card.querySelector('.tc-wiki-link'))return;
    const name=card.querySelector('.tc-loadout-name');if(!name)return;
    const a=tcWikiAnchor(name.textContent,'weapon','Weapon wiki');if(a)name.insertAdjacentElement('afterend',a);
  });
}
function tcDecorateCompendiumWiki(){
  const sheet=document.querySelector('#tcCompendiumOverlay .tc-comp-sheet');if(!sheet)return;
  const boss=sheet.querySelector('h2');
  if(boss&&!boss.nextElementSibling?.classList?.contains('tc-wiki-link')){
    const a=tcWikiAnchor(boss.textContent,'boss','Boss wiki');if(a)boss.insertAdjacentElement('afterend',a);
  }
  sheet.querySelectorAll('.tc-comp-weapons>div').forEach(box=>{
    if(box.querySelector('.tc-wiki-link'))return;
    const name=box.querySelector('strong');if(!name)return;
    const a=tcWikiAnchor(name.textContent,'weapon','Weapon wiki');if(a)name.insertAdjacentElement('afterend',a);
  });
}
let tcWikiDecorateQueued=false;
function tcDecorateWikiLinks(){
  tcWikiDecorateQueued=false;
  try{tcDecorateGraceWiki();tcDecorateEncounterWiki();tcDecorateCompendiumWiki();}catch(error){console.warn('Wiki decoration failed',error);}
}
function tcQueueWikiDecoration(){if(tcWikiDecorateQueued)return;tcWikiDecorateQueued=true;requestAnimationFrame(tcDecorateWikiLinks);}
const tcWikiObserver=new MutationObserver(tcQueueWikiDecoration);
tcWikiObserver.observe(document.body,{childList:true,subtree:true});
document.addEventListener('click',e=>{if(e.target.closest('.tc-comp-card,.tc-bottom-nav,[data-screen]'))setTimeout(tcQueueWikiDecoration,0);});
setTimeout(tcQueueWikiDecoration,0);
/* --- End contextual Elden Ring wiki links --- */
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in ['TC_WIKI_BASE','eldenring.wiki.gg/wiki/','TC_AR_CALCULATOR','tarnished.dev/weapon-calculator','TC_GRACE_MEMOS','Covenant Office Memorandum','tcGraceMemoForState','tcDecorateGraceOffice','overflow-y:hidden!important','tcWikiUrl','tcDecorateGraceWiki','tc-grace-wiki-target','tc-grace-ar-tools','tcDecorateEncounterWiki','tcDecorateCompendiumWiki','tc-wiki-link']:
    if needle not in s: raise SystemExit('wiki/calculator/Grace invariant missing: '+needle)
p.write_text(s)
