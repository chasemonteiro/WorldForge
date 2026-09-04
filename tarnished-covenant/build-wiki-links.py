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
.tc-wiki-link:active{opacity:.68}.tc-wiki-boss{margin-top:7px}.tc-wiki-weapon{margin:0 0 8px}.tc-grace-wiki-row{text-align:center;margin:-2px 0 9px}.tc-grace-target .tc-wiki-link{margin-top:7px}.tc-comp-sheet .tc-wiki-boss{margin:1px 0 14px}.tc-comp-sheet .tc-wiki-weapon{margin:1px 0 7px}
/* --- End contextual wiki link styles --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Contextual Elden Ring wiki links --- */
const TC_WIKI_BASE='https://eldenring.wiki.fextralife.com/';
function tcWikiTitle(name,kind='boss'){
  let out=String(name||'').trim().replace(/[’‘]/g,"'").replace(/[–—]/g,'-');
  if(kind==='boss')out=out.replace(/\s*\([^)]*\)\s*$/,'').trim();
  return out;
}
function tcWikiUrl(name,kind='boss'){
  const title=tcWikiTitle(name,kind);
  if(!title)return '';
  return TC_WIKI_BASE+encodeURIComponent(title).replace(/%20/g,'+');
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
function tcDecorateGraceWiki(){
  const target=run?.state?.current?.target?.name;if(!target)return;
  const dashboardName=document.querySelector('.tc-sanctuary-panel[data-panel="grace"] .tc-grace-target-name,.tc-grace-target-name');
  if(dashboardName&&!dashboardName.parentElement.querySelector(':scope > .tc-wiki-link')){
    const a=tcWikiAnchor(target,'boss','Boss wiki');if(a)dashboardName.insertAdjacentElement('afterend',a);
  }
  const oldGrid=document.querySelector('.tc-sanctuary-panel[data-panel="grace"] .tc-hub-grid,.tc-screen .tc-hub-grid');
  if(oldGrid&&!oldGrid.parentElement.querySelector(':scope > .tc-grace-wiki-row')){
    const row=document.createElement('div');row.className='tc-grace-wiki-row';
    const a=tcWikiAnchor(target,'boss','Current target wiki');if(a){row.appendChild(a);oldGrid.insertAdjacentElement('afterend',row);}
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

for needle in ['TC_WIKI_BASE','tcWikiUrl','tcDecorateGraceWiki','tcDecorateEncounterWiki','tcDecorateCompendiumWiki','tc-wiki-link']:
    if needle not in s: raise SystemExit('wiki link invariant missing: '+needle)
p.write_text(s)
