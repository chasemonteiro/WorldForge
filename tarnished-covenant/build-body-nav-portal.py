from pathlib import Path

p=Path('tarnished-covenant/index.html')
s=p.read_text()

js=r'''
/* --- iOS navigation portal: fixed chrome belongs to the document viewport. --- */
const tcNavMarkupBeforePortal=navMarkup;
let tcPendingNavActive='sanctuary';
let tcDocumentNavListenerInstalled=false;

navMarkup=function(active){
  tcPendingNavActive=active||'sanctuary';
  return '';
};

function tcRemoveBodyNav(){
  document.querySelectorAll('body > .tc-bottom-nav, #app .tc-bottom-nav').forEach(node=>node.remove());
}

function tcMountBodyNav(active=tcPendingNavActive){
  tcRemoveBodyNav();
  document.body.insertAdjacentHTML('beforeend',tcNavMarkupBeforePortal(active));
}

bindNav=function(){
  tcMountBodyNav(tcPendingNavActive);
  if(tcDocumentNavListenerInstalled)return;
  tcDocumentNavListenerInstalled=true;
  document.addEventListener('click',event=>{
    const btn=event.target.closest?.('[data-screen]');
    if(!btn)return;
    if(tcTransitionIsLocked()){
      event.preventDefault();
      setToast('Finish the current Covenant notice first.');
      tcRemoveBodyNav();
      renderRun();
      return;
    }
    uiScreen=btn.dataset.screen;
    tcRemoveBodyNav();
    renderRun();
  });
};

/* Always clear the previous screen's body-level chrome first. Normal primary
   screens remount it through bindNav; blocking/full-screen transitions do not. */
const tcRenderRunBeforeBodyNavPortal=renderRun;
renderRun=function(){
  tcRemoveBodyNav();
  return tcRenderRunBeforeBodyNavPortal();
};
'''

idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in [
  'tcNavMarkupBeforePortal','tcMountBodyNav','body > .tc-bottom-nav',
  "document.addEventListener('click',event=>",'tcRenderRunBeforeBodyNavPortal'
]:
  if needle not in s: raise SystemExit('body-nav portal invariant missing: '+needle)

p.write_text(s)
