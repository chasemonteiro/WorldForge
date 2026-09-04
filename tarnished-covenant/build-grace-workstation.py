from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Idempotent: this is the single owner of the compact Grace memo/workstation layer.
s=re.sub(r"\n?/\* --- Grace office workstation styles --- \*/.*?/\* --- End Grace office workstation styles --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Grace office workstation behavior --- \*/.*?/\* --- End Grace office workstation behavior --- \*/\n?", "\n", s, flags=re.S)

css=r'''
/* --- Grace office workstation styles --- */
.tc-sanctuary-panel[data-panel="grace"]{overflow-y:hidden!important;padding-bottom:8px!important}
.tc-sanctuary-panel[data-panel="grace"]>.tc-rune,
.tc-sanctuary-panel[data-panel="grace"]>.tc-title,
.tc-sanctuary-panel[data-panel="grace"]>.tc-subtitle{display:none!important}
.tc-grace-office-memo{margin:4px 8px 9px;padding:10px 12px 11px;border-top:1px solid rgba(198,161,90,.25);border-bottom:1px solid rgba(198,161,90,.18);background:linear-gradient(90deg,transparent,rgba(198,161,90,.055),transparent);text-align:center;flex:0 0 auto}
.tc-grace-office-label{font:850 8px/1.1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.16em;color:var(--gold);margin-bottom:6px}
.tc-grace-office-copy{font:italic 13px/1.35 Georgia,serif;color:#cfc5b2;max-width:560px;margin:auto;text-wrap:balance}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-art{height:min(24svh,185px)!important;min-height:125px!important;margin:7px 0 8px!important;flex:0 1 auto}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-wiki-target{margin:7px 8px 0!important;padding:9px 9px 8px!important;flex:0 0 auto}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-wiki-name{font-size:clamp(18px,5.2vw,24px)!important;margin:4px 0 1px!important}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-tools{margin:7px 8px 0!important;padding:9px 10px 9px!important;flex:0 0 auto}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-title{margin-bottom:5px!important}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-weapons{gap:2px!important;margin-bottom:7px!important;font-size:13px!important;line-height:1.15!important}
.tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-button{min-height:36px!important;padding:8px 10px!important}
@media(max-height:760px){
  .tc-grace-office-memo{padding:8px 10px;margin-top:2px;margin-bottom:6px}
  .tc-grace-office-copy{font-size:11px}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-art{height:18svh!important;min-height:100px!important;margin:5px 0 6px!important}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-wiki-target{margin-top:5px!important;padding-top:7px!important;padding-bottom:7px!important}
  .tc-sanctuary-panel[data-panel="grace"] .tc-grace-ar-tools{margin-top:5px!important;padding-top:7px!important;padding-bottom:7px!important}
}
/* --- End Grace office workstation styles --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Grace office workstation behavior --- */
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
function tcGraceMemoForState(state){
  const seed=String(state?.current?.id||state?.current?.target?.name||state?.region||'grace');
  let hash=0;for(let i=0;i<seed.length;i++)hash=((hash<<5)-hash+seed.charCodeAt(i))|0;
  return TC_GRACE_MEMOS[Math.abs(hash)%TC_GRACE_MEMOS.length];
}
function tcDecorateGraceWorkstation(){
  const panel=document.querySelector('.tc-sanctuary-panel[data-panel="grace"]');
  if(!panel)return;
  const text=tcGraceMemoForState(run?.state);
  let memo=panel.querySelector('.tc-grace-office-memo');
  if(!memo){
    memo=document.createElement('div');memo.className='tc-grace-office-memo';
    const art=panel.querySelector('.tc-grace-art');
    (art||panel.firstElementChild)?.insertAdjacentElement(art?'beforebegin':'afterend',memo);
  }
  memo.innerHTML=`<div class="tc-grace-office-label">Covenant Office Memorandum</div><div class="tc-grace-office-copy">${h(text)}</div>`;
  panel.scrollTop=0;
}
const tcRenderSanctuaryBeforeGraceWorkstation=renderSanctuary;
renderSanctuary=function(){
  tcRenderSanctuaryBeforeGraceWorkstation();
  tcDecorateGraceWorkstation();
};
setTimeout(tcDecorateGraceWorkstation,0);
/* --- End Grace office workstation behavior --- */
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in [
  'Grace office workstation styles',
  'overflow-y:hidden!important',
  'Covenant Office Memorandum',
  'TC_GRACE_MEMOS',
  'tcGraceMemoForState',
  'tcDecorateGraceWorkstation',
  'tcRenderSanctuaryBeforeGraceWorkstation'
]:
  if needle not in s: raise SystemExit('Grace workstation invariant missing: '+needle)

p.write_text(s)
