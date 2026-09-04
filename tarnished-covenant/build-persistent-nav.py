from pathlib import Path

p=Path('tarnished-covenant/index.html')
s=p.read_text()

css=r'''
/* --- Persistent bottom navigation: viewport chrome, never screen content --- */
.tc-nav-anchor{display:none!important}
body>.tc-bottom-nav.tc-persistent-nav{position:fixed!important;z-index:130!important;left:50%!important;right:auto!important;bottom:0!important;transform:translateX(-50%)!important;width:min(760px,100%)!important;animation:none!important}
body>.tc-bottom-nav.tc-persistent-nav[hidden]{display:none!important}
/* A fixed descendant of an animated/transformed screen becomes screen-relative
   in WebKit. The persistent bar is outside .tc-screen; keep screen entry motion
   visual-only so no future fixed descendants inherit that trap either. */
.tc-screen{animation:tcScreenFade .18s ease-out!important}
@keyframes tcScreenFade{from{opacity:.45}to{opacity:1}}
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Persistent bottom navigation lifecycle --- */
let tcPersistentBottomNav=null;
let tcPersistentNavObserver=null;
let tcPersistentNavClickInstalled=false;

function tcPersistentNavHtml(active){
  return `<button data-screen="sanctuary" class="${active==='sanctuary'?'active':''}"><span class="nicon">⌂</span><span>Site of Grace</span></button>
    <button data-screen="encounter" class="${active==='encounter'?'active':''}"><span class="nicon">✦</span><span>Encounter</span></button>
    <button data-screen="ledger" class="${active==='ledger'?'active':''}"><span class="nicon">▤</span><span>Ledger</span></button>
    <button data-screen="settings" class="${active==='settings'?'active':''}"><span class="nicon">⚙</span><span>Settings</span></button>`;
}

function tcEnsurePersistentNav(){
  if(tcPersistentBottomNav?.isConnected)return tcPersistentBottomNav;
  tcPersistentBottomNav=document.createElement('nav');
  tcPersistentBottomNav.className='tc-bottom-nav tc-persistent-nav';
  tcPersistentBottomNav.hidden=true;
  document.body.appendChild(tcPersistentBottomNav);
  return tcPersistentBottomNav;
}

function tcSyncPersistentNav(){
  const anchor=app.querySelector('.tc-nav-anchor');
  const nav=tcEnsurePersistentNav();
  if(!anchor){nav.hidden=true;return;}
  const active=anchor.dataset.tcNavActive||uiScreen||'sanctuary';
  nav.innerHTML=tcPersistentNavHtml(active);
  nav.hidden=false;
}

/* Normal app screens render an invisible anchor instead of recreating the bar.
   MutationObserver hides the persistent chrome automatically on modal/transition
   screens that do not render an anchor. */
navMarkup=function(active){
  return `<span class="tc-nav-anchor" data-tc-nav-active="${h(active)}" aria-hidden="true"></span>`;
};

bindNav=function(){
  tcSyncPersistentNav();
  if(!tcPersistentNavClickInstalled){
    tcPersistentNavClickInstalled=true;
    document.addEventListener('click',event=>{
      const btn=event.target.closest?.('[data-screen]');
      if(!btn)return;
      if(tcTransitionIsLocked()){
        event.preventDefault();
        setToast('Finish the current Covenant notice first.');
        renderRun();
        return;
      }
      uiScreen=btn.dataset.screen;
      renderRun();
    });
  }
  if(!tcPersistentNavObserver){
    tcPersistentNavObserver=new MutationObserver(()=>queueMicrotask(tcSyncPersistentNav));
    tcPersistentNavObserver.observe(app,{childList:true,subtree:true});
  }
};

/* Bootstrap can restore a run before any subsequent tap. Re-sync once the first
   synchronous render settles so the nav is viewport-attached from frame one. */
queueMicrotask(()=>{if(run)tcSyncPersistentNav();});
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in ['tc-persistent-nav','tc-nav-anchor','tcPersistentNavObserver','document.body.appendChild(tcPersistentBottomNav)','navMarkup=function(active)','document.addEventListener(\'click\',event=>']:
    if needle not in s: raise SystemExit('persistent nav invariant missing: '+needle)

p.write_text(s)
