from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Idempotent late composition layer. It does not own Grace data or navigation;
# it only rearranges the existing memo/wiki/buildcraft decorators into a
# one-screen dashboard hierarchy.
s=re.sub(r"\n?/\* --- Grace home-screen composition --- \*/.*?/\* --- End Grace home-screen composition --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Grace home-screen behavior --- \*/.*?/\* --- End Grace home-screen behavior --- \*/\n?", "\n", s, flags=re.S)

css=r'''
/* --- Grace home-screen composition --- */
.tc-sanctuary-panel[data-panel="grace"]>.tc-panel-heading{display:none!important}

/* Treat the memo as a status strip, not another content card. */
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-office-memo{
  display:grid;grid-template-columns:auto minmax(0,1fr);align-items:center;gap:11px;
  margin:3px 0 7px;padding:8px 11px;text-align:left;
  border-top:1px solid rgba(198,161,90,.24);border-bottom:1px solid rgba(198,161,90,.18);
  background:linear-gradient(90deg,rgba(198,161,90,.07),rgba(198,161,90,.025) 58%,transparent);
}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-office-label{margin:0;white-space:nowrap;font-size:7.5px;line-height:1.15}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-office-copy{margin:0;max-width:none;font-size:11.5px;line-height:1.25;text-align:left}

/* The Grace image is the hero. Current target lives inside it rather than
   consuming a second full-width section below. */
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-art{
  position:relative!important;height:min(30svh,225px)!important;min-height:165px!important;
  margin:6px 0 8px!important;flex:0 1 auto;
}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-art:after{z-index:1;pointer-events:none}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-art>.tc-grace-wiki-target{
  position:absolute;z-index:2;left:0;right:0;bottom:0;margin:0!important;
  padding:42px 14px 12px;text-align:left;border:0!important;
  background:linear-gradient(180deg,transparent,rgba(5,5,4,.56) 34%,rgba(5,5,4,.93));
}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-art>.tc-grace-wiki-target .tc-kicker{font-size:7.5px}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-art>.tc-grace-wiki-target .tc-grace-wiki-name{
  margin:4px 0 2px;font-size:clamp(23px,6.4vw,31px);line-height:1.02;color:#f0e5cf;
  text-shadow:0 2px 12px #000,0 1px 2px #000;max-width:88%;
}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-art>.tc-grace-wiki-target .tc-wiki-link{margin-top:3px;padding-top:4px;padding-bottom:3px}

/* Assigned armaments + calculator read as one home-screen utility row. */
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-tools{
  display:grid;grid-template-columns:minmax(0,1fr) minmax(142px,.82fr);grid-template-rows:auto auto;
  column-gap:12px;row-gap:3px;align-items:center;margin:0!important;padding:9px 11px!important;text-align:left;
  border:1px solid rgba(198,161,90,.24);background:linear-gradient(90deg,rgba(198,161,90,.055),rgba(8,8,6,.18));
}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-title{grid-column:1;grid-row:1;margin:0;font-size:7.5px}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-weapons{grid-column:1;grid-row:2;margin:0;gap:1px;font-size:12.5px;line-height:1.15;min-width:0}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-button{
  grid-column:2;grid-row:1 / span 2;min-height:50px;padding:8px 9px;text-align:center;font-size:8.5px;line-height:1.25;
}

@media(max-width:380px){
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-office-memo{gap:8px;padding-left:8px;padding-right:8px}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-office-label{font-size:6.7px}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-office-copy{font-size:10.5px}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-tools{grid-template-columns:minmax(0,1fr) 132px;column-gap:8px;padding:8px!important}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-weapons{font-size:11.5px}
}
@media(max-height:740px){
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-office-memo{margin-top:1px;margin-bottom:5px;padding-top:6px;padding-bottom:6px}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-office-copy{font-size:10px}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-art{height:24svh!important;min-height:140px!important;margin-top:4px!important;margin-bottom:6px!important}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-art>.tc-grace-wiki-target{padding-top:34px;padding-bottom:9px}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-art>.tc-grace-wiki-target .tc-grace-wiki-name{font-size:21px}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-tools{padding-top:7px!important;padding-bottom:7px!important}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-button{min-height:44px}
}
/* --- End Grace home-screen composition --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Grace home-screen behavior --- */
function tcComposeGraceHomeScreen(){
  const panel=document.querySelector('.tc-sanctuary-panel[data-panel="grace"]');
  if(!panel)return;
  const art=panel.querySelector('.tc-grace-art');
  const target=panel.querySelector('.tc-grace-wiki-target');
  const tools=panel.querySelector('.tc-grace-ar-tools');
  if(art&&target&&target.parentElement!==art)art.appendChild(target);
  if(art&&tools&&tools.previousElementSibling!==art)art.insertAdjacentElement('afterend',tools);
  panel.scrollTop=0;
}
let tcGraceHomeQueued=false;
function tcQueueGraceHomeScreen(){
  if(tcGraceHomeQueued)return;tcGraceHomeQueued=true;
  requestAnimationFrame(()=>{tcGraceHomeQueued=false;tcComposeGraceHomeScreen();});
}
const tcGraceHomeObserver=new MutationObserver(tcQueueGraceHomeScreen);
tcGraceHomeObserver.observe(document.body,{childList:true,subtree:true});
document.addEventListener('click',e=>{if(e.target.closest('.tc-bottom-nav,[data-screen],.tc-sanctuary-tabs'))setTimeout(tcQueueGraceHomeScreen,0);});
setTimeout(tcQueueGraceHomeScreen,0);
/* --- End Grace home-screen behavior --- */
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in ['Grace home-screen composition','tcComposeGraceHomeScreen','tcGraceHomeObserver','tc-grace-art>.tc-grace-wiki-target','grid-template-columns:minmax(0,1fr) minmax(142px,.82fr)']:
    if needle not in s: raise SystemExit('Grace home-screen invariant missing: '+needle)

p.write_text(s)
