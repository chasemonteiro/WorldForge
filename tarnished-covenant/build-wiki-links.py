from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Keep this patch idempotent across rebuilds.
s=re.sub(r"\n?/\* --- Contextual Elden Ring wiki links --- \*/.*?/\* --- End contextual Elden Ring wiki links --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Contextual wiki link styles --- \*/.*?/\* --- End contextual wiki link styles --- \*/\n?", "\n", s, flags=re.S)

css=r'''
/* --- Contextual wiki link styles --- */
.tc-wiki-link{display:inline-flex;align-items:center;gap:4px;color:var(--gold-bright);text-decoration:none;border-bottom:1px solid rgba(224,193,123,.34);padding:5px 1px 4px;font:800 8px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.10em;white-space:nowrap;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.tc-wiki-link:active{opacity:.68}.tc-wiki-boss{margin-top:7px}.tc-wiki-weapon{margin:0 0 8px}.tc-grace-target .tc-wiki-link{margin-top:7px}.tc-comp-sheet .tc-wiki-boss{margin:1px 0 14px}.tc-comp-sheet .tc-wiki-weapon{margin:1px 0 7px}
.tc-grace-wiki-target{margin:14px 8px 0;padding:13px 10px 12px;border-top:1px solid var(--line-soft);border-bottom:1px solid var(--line-soft);text-align:center;background:linear-gradient(90deg,transparent,rgba(198,161,90,.045),transparent)}
.tc-grace-wiki-name{font:400 clamp(21px,6vw,28px)/1.08 Georgia,serif;color:var(--ink);margin:6px 0 2px;text-wrap:balance}
.tc-grace-wiki-target .tc-kicker{color:var(--gold)}
.tc-grace-ar-tools{margin:12px 8px 0;padding:13px 12px 12px;border:1px solid rgba(198,161,90,.25);background:linear-gradient(180deg,rgba(198,161,90,.06),rgba(8,8,6,.24));text-align:center}
.tc-grace-ar-title{font:850 8px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.13em;color:var(--gold);margin-bottom:8px}
.tc-grace-ar-weapons{display:grid;gap:5px;margin:0 0 10px;font:400 15px/1.25 Georgia,serif;color:var(--ink)}
.tc-grace-ar-weapons span{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tc-grace-ar-button{display:flex;align-items:center;justify-content:center;width:100%;min-height:42px;padding:10px 12px;border:1px solid rgba(224,193,123,.48);background:linear-gradient(180deg,rgba(198,161,90,.14),rgba(94,72,34,.08));color:var(--gold-bright);text-decoration:none;font:850 9px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.10em;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.tc-grace-ar-button:active{opacity:.72}
/* --- End contextual wiki link styles --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Contextual Elden Ring wiki links --- */
const TC_WIKI_BASE='https://eldenring.wiki.gg/wiki/';
const TC_AR_CALCULATOR='https://www.tarnished.dev/weapon-calculator';
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
function tcDecorateGraceWiki(){
  const target=run?.state?.current?.target?.name;if(!target)return;
  const gracePanel=document.querySelector('.tc-sanctuary-panel[data-panel="grace"]');
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

for needle in ['TC_WIKI_BASE','eldenring.wiki.gg/wiki/','TC_AR_CALCULATOR','tarnished.dev/weapon-calculator','tcWikiUrl','tcDecorateGraceWiki','tc-grace-wiki-target','tc-grace-ar-tools','tcDecorateEncounterWiki','tcDecorateCompendiumWiki','tc-wiki-link']:
    if needle not in s: raise SystemExit('wiki/calculator invariant missing: '+needle)
p.write_text(s)
